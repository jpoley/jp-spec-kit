"""Tool dependency manager for security scanners.

This module provides the main ToolManager class for installing,
managing, and monitoring security scanning tools.

Features:
- Auto-installation with version pinning
- License compliance checking (CodeQL)
- Dependency size monitoring (alert at 500MB)
- Offline mode for air-gapped environments
- Cross-platform support

Security Features:
- HTTPS-only downloads (no HTTP allowed)
- Path traversal protection via Path.relative_to()
- TOCTOU mitigation via temp directory extraction
- Symlink attack detection
- Maximum download size enforcement
- Version format validation with anchored regex
- Pip installs allow dependencies to ensure tool functionality
- Command injection prevention via path validation
"""

import logging
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import time
import uuid
import zipfile
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

try:
    from filelock import FileLock as ExternalFileLock

    HAS_FILELOCK = True
except ImportError:
    HAS_FILELOCK = False
    # On Unix without filelock, fall back to fcntl
    if sys.platform != "win32":
        import fcntl

from flowspec_cli.security.tools.models import (
    DEFAULT_TOOL_CONFIGS,
    CacheInfo,
    InstallMethod,
    InstallResult,
    ToolConfig,
    ToolInfo,
    ToolStatus,
)

logger = logging.getLogger(__name__)

# VERSION_PATTERN: Regex for validating semantic version strings (anchored for exact match)
#
# Pattern explanation:
# - ^v?              : Optional 'v' prefix at start (e.g., "v1.0.0" or "1.0.0")
# - (\d+\.\d+        : Major.minor (required, e.g., "1.0")
# - (?:\.\d+)?       : Optional patch version (e.g., ".0" in "1.0.0")
# - (?:-[\w.]+)?     : Optional pre-release/metadata (e.g., "-beta1", "-rc.1")
# - )$               : Anchor to end (no extra content allowed)
#
# Accepted formats:
#   - "1.0", "1.0.0", "v1.0.0"
#   - "1.0.0-beta1", "v2.15.0-rc.1"
#
# Rejected formats:
#   - "1.2.3.4" (too many segments)
#   - "abc", "version" (non-numeric)
#   - "semgrep 1.0.0" (contains spaces, not just version)
VERSION_PATTERN = re.compile(r"^v?(\d+\.\d+(?:\.\d+)?(?:-[\w.]+)?)$")

# VERSION_SEARCH_PATTERN: Regex for extracting version from tool output (not anchored)
# Used for parsing version strings from --version output, which may contain other text
VERSION_SEARCH_PATTERN = re.compile(r"v?(\d+\.\d+(?:\.\d+)?(?:-[\w.]+)?)")

# Constants for timeouts and limits (Issue #9: Extract magic numbers)
PIP_INSTALL_TIMEOUT_SECONDS = 300  # 5 minutes for pip install
VERSION_CHECK_TIMEOUT_SECONDS = 5  # 5 seconds for --version check
DOWNLOAD_CHUNK_SIZE = 8192  # 8KB chunks for streaming downloads
MAX_ERROR_MESSAGE_LENGTH = 200  # Truncate error messages for logs

# Characters that could enable command injection
DANGEROUS_PATH_CHARS = frozenset(";|&$`\n\r<>")


class ToolManager:
    """Manager for security scanning tool dependencies.

    This class handles:
    - Tool discovery and installation
    - Version pinning and updates
    - License compliance checking
    - Cache size monitoring
    - Offline mode operation

    Security:
        - Downloads require HTTPS (HTTP is rejected)
        - Archives validated for path traversal via Path.relative_to()
        - Symlinks in archives are rejected
        - Version strings are validated before use
        - Maximum download size enforced
        - Temp directory extraction prevents TOCTOU
        - Paths validated before subprocess execution

    Example:
        >>> manager = ToolManager()
        >>> result = manager.install("semgrep")
        >>> if result.success:
        ...     print(f"Installed at: {result.tool_info.path}")
    """

    # Cache size warning threshold in MB
    CACHE_WARNING_THRESHOLD_MB = 500

    # Download timeout in seconds
    DOWNLOAD_TIMEOUT_SECONDS = 300

    # Maximum search depth for finding executables
    MAX_SEARCH_DEPTH = 5

    # Maximum number of files allowed in an archive (zip bomb protection)
    MAX_ARCHIVE_FILES = 10000

    # Maximum file size for executables in MB (sanity check)
    MAX_EXECUTABLE_SIZE_MB = 1000

    def __init__(
        self,
        cache_dir: Path | None = None,
        offline_mode: bool = False,
        tool_configs: dict[str, ToolConfig] | None = None,
    ):
        """Initialize tool manager.

        Args:
            cache_dir: Directory to cache tools (default: ~/.specify/tools).
            offline_mode: If True, only use cached tools, no network access.
            tool_configs: Custom tool configurations (default: built-in configs).
        """
        self.cache_dir = cache_dir or Path.home() / ".specify" / "tools"
        self.offline_mode = offline_mode
        self.tool_configs = tool_configs or DEFAULT_TOOL_CONFIGS.copy()
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_tool_info(self, tool_name: str) -> ToolInfo | None:
        """Get information about an installed tool.

        Args:
            tool_name: Name of the tool (e.g., "semgrep").

        Returns:
            ToolInfo if found, None otherwise.
        """
        tool_path = self._find_tool(tool_name)
        if not tool_path:
            return None

        version = self._get_tool_version(tool_name, tool_path)
        status = self._determine_status(tool_name, version)
        install_method = self._detect_install_method(tool_path)
        size_mb = self._get_size_mb(tool_path)

        return ToolInfo(
            name=tool_name,
            version=version,
            path=tool_path,
            status=status,
            install_method=install_method,
            size_mb=size_mb,
        )

    def is_available(self, tool_name: str) -> bool:
        """Check if tool is available for use.

        Args:
            tool_name: Name of the tool.

        Returns:
            True if tool is installed and ready.
        """
        return self._find_tool(tool_name) is not None

    def install(
        self,
        tool_name: str,
        accept_license: bool = False,
        force: bool = False,
    ) -> InstallResult:
        """Install a security scanning tool.

        Args:
            tool_name: Name of the tool to install.
            accept_license: If True, auto-accept license (for CodeQL etc).
            force: If True, reinstall even if already installed.

        Returns:
            InstallResult with success status and tool info or error.
        """
        if tool_name not in self.tool_configs:
            return InstallResult(
                success=False,
                error_message=f"Unknown tool: {tool_name}",
            )

        config = self.tool_configs[tool_name]

        # Check if already installed (unless force)
        if not force:
            existing = self.get_tool_info(tool_name)
            if existing and existing.status == ToolStatus.INSTALLED:
                return InstallResult(success=True, tool_info=existing)

        # Check offline mode (Issue #13: Get actual version for cached tools)
        if self.offline_mode:
            cached = self._find_in_cache(tool_name)
            if cached:
                actual_version = self._get_tool_version(tool_name, cached)
                return InstallResult(
                    success=True,
                    tool_info=ToolInfo(
                        name=tool_name,
                        version=actual_version,
                        path=cached,
                        status=ToolStatus.OFFLINE_ONLY,
                        install_method=InstallMethod.BINARY,
                    ),
                )
            return InstallResult(
                success=False,
                error_message=f"Offline mode: {tool_name} not found in cache",
            )

        # Check license requirement
        if config.license_check and not accept_license:
            return InstallResult(
                success=False,
                license_required=True,
                error_message=f"License acceptance required. Review: {config.license_url}",
            )

        # Install based on method
        if config.install_method == InstallMethod.PIP:
            return self._install_pip(config)
        elif config.install_method == InstallMethod.BINARY:
            return self._install_binary(config)
        else:
            return InstallResult(
                success=False,
                error_message=f"Unsupported install method: {config.install_method}",
            )

    def _install_pip(self, config: ToolConfig) -> InstallResult:
        """Install tool using pip.

        Args:
            config: Tool configuration.

        Returns:
            InstallResult with status.
        """
        package = config.pip_package or config.name
        version_spec = f"=={config.version}" if config.version else ""

        try:
            # Note: For maximum supply chain security, use requirements.txt with
            # --require-hashes. The --no-deps flag breaks tool functionality.
            cmd = [
                sys.executable,
                "-m",
                "pip",
                "install",
                f"{package}{version_spec}",
            ]
            logger.info(f"Installing {package}{version_spec}")

            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=PIP_INSTALL_TIMEOUT_SECONDS,
                check=True,
            )

            tool_path = self._find_tool(config.name)
            if not tool_path:
                return InstallResult(
                    success=False,
                    error_message=f"Installed but could not find {config.name} executable",
                )

            tool_info = self.get_tool_info(config.name)
            return InstallResult(success=True, tool_info=tool_info)

        except subprocess.CalledProcessError as e:
            # Issue #9: Use constant for error message truncation
            error_msg = (
                str(e.stderr).split("\n")[0][:MAX_ERROR_MESSAGE_LENGTH]
                if e.stderr
                else str(e)
            )
            return InstallResult(
                success=False,
                error_message=f"pip install failed: {error_msg}",
            )
        except subprocess.TimeoutExpired:
            return InstallResult(
                success=False,
                error_message=f"Installation timed out after {PIP_INSTALL_TIMEOUT_SECONDS // 60} minutes",
            )

    def _acquire_install_lock(self, tool_name: str, version: str, timeout: int = 60):
        """Acquire file-based lock for concurrent installation protection.

        Args:
            tool_name: Name of the tool.
            version: Version being installed.
            timeout: Maximum seconds to wait for lock.

        Returns:
            Context manager that holds the lock file handle.

        Raises:
            RuntimeError: If lock cannot be acquired within timeout.
        """
        lock_file = self.cache_dir / f".{tool_name}_{version}.lock"
        lock_file.parent.mkdir(parents=True, exist_ok=True)

        # Use external filelock library if available (cross-platform)
        if HAS_FILELOCK:
            return ExternalFileLock(str(lock_file), timeout=timeout)

        # Fallback implementation for Unix systems without filelock
        if sys.platform != "win32":

            class FcntlFileLock:
                def __init__(self, path: Path, timeout: int):
                    self.path = path
                    self.timeout = timeout
                    self.file_handle = None

                def __enter__(self):
                    self.file_handle = open(self.path, "w", encoding="utf-8")
                    start_time = time.time()
                    try:
                        while True:
                            try:
                                # Non-blocking exclusive lock
                                fcntl.flock(
                                    self.file_handle.fileno(),
                                    fcntl.LOCK_EX | fcntl.LOCK_NB,
                                )
                                return self
                            except OSError:
                                # Lock held by another process
                                if time.time() - start_time >= self.timeout:
                                    raise RuntimeError(
                                        f"Could not acquire install lock for {self.path.name} within {self.timeout}s"
                                    )
                                time.sleep(0.1)
                    except Exception:
                        # Clean up file handle on any error during lock acquisition
                        if self.file_handle:
                            self.file_handle.close()
                        raise

                def __exit__(self, exc_type, exc_val, exc_tb):
                    # Release lock and close file
                    # The lock is automatically released when file is closed
                    if self.file_handle:
                        try:
                            fcntl.flock(self.file_handle.fileno(), fcntl.LOCK_UN)
                        except Exception:
                            pass  # Ignore errors during unlock
                        finally:
                            self.file_handle.close()
                    # Clean up lock file
                    try:
                        if self.path.exists():
                            self.path.unlink()
                    except Exception:
                        pass  # Ignore cleanup errors
                    return False

            return FcntlFileLock(lock_file, timeout)

        # Windows without filelock library
        raise RuntimeError(
            "File locking requires 'filelock' package on Windows. "
            "Install with: pip install filelock"
        )

    def _install_binary(self, config: ToolConfig) -> InstallResult:
        """Install tool by downloading binary.

        Args:
            config: Tool configuration.

        Returns:
            InstallResult with status.
        """
        # Issue #11: Raise error for unsupported platforms
        try:
            platform_key = self._get_platform_key()
        except RuntimeError as e:
            return InstallResult(success=False, error_message=str(e))

        if platform_key not in config.binary_urls:
            return InstallResult(
                success=False,
                error_message=f"No binary available for platform: {platform_key}",
            )

        # Issue #14: Require version for binary install
        if not config.version:
            return InstallResult(
                success=False,
                error_message=f"Binary install requires version specification for {config.name}",
            )

        # Validate version format before URL construction
        if not self._is_valid_version(config.version):
            return InstallResult(
                success=False,
                error_message=f"Invalid version format: {config.version}",
            )

        # Validate and construct URL
        url_template = config.binary_urls[platform_key]
        is_valid, error_msg = self._validate_url_template(url_template, config.version)
        if not is_valid:
            return InstallResult(
                success=False,
                error_message=f"Invalid URL template: {error_msg}",
            )

        # Defensive: wrap format() even though validation passed
        try:
            url = url_template.format(version=config.version)
        except KeyError as e:
            return InstallResult(
                success=False,
                error_message=f"URL template formatting failed: {str(e)}",
            )

        dest_dir = self.cache_dir / config.name / config.version

        # Acquire file-based lock for concurrent installation protection
        try:
            with self._acquire_install_lock(config.name, config.version):
                return self._install_binary_locked(config, url, dest_dir)
        except RuntimeError as e:
            return InstallResult(
                success=False,
                error_message=f"Lock acquisition failed: {e}",
            )

    def _install_binary_locked(
        self, config: ToolConfig, url: str, dest_dir: Path
    ) -> InstallResult:
        """Install binary with lock already acquired.

        Args:
            config: Tool configuration.
            url: Download URL.
            dest_dir: Destination directory.

        Returns:
            InstallResult with status.
        """
        download_path = None
        try:
            logger.info(f"Downloading {config.name} from {url}")
            dest_dir.mkdir(parents=True, exist_ok=True)

            # Use URL-based filename for download
            download_filename = self._get_filename_from_url(url)
            download_path = dest_dir / download_filename

            # Issue #3: Calculate max download size
            max_download_mb = (
                config.size_estimate_mb * 2 if config.size_estimate_mb else 1000
            )
            self._download_file(url, download_path, max_size_mb=max_download_mb)

            # Count files before extraction for validation
            files_before = set(dest_dir.rglob("*"))

            # Issue #6: Set restrictive umask before extraction
            old_umask = os.umask(0o077)
            try:
                # Extract with security validation
                self._safe_extract_archive(download_path, dest_dir)
            finally:
                os.umask(old_umask)

            # Validate archive produced files
            files_after = set(dest_dir.rglob("*"))
            new_files = files_after - files_before - {download_path}
            if not new_files:
                return InstallResult(
                    success=False,
                    error_message="Archive extraction produced no files",
                )

            tool_path = self._find_in_directory(dest_dir, config.name)
            if not tool_path:
                # Issue #21: Cleanup on extraction failure
                shutil.rmtree(dest_dir)
                return InstallResult(
                    success=False,
                    error_message=f"Could not find {config.name} executable in archive",
                )

            # Set executable permission (owner only for security)
            if not tool_path.is_file():
                shutil.rmtree(dest_dir)
                return InstallResult(
                    success=False,
                    error_message=f"Found path is not a valid file: {tool_path}",
                )

            # Check file size for sanity
            file_size_mb = tool_path.stat().st_size / (1024 * 1024)
            if file_size_mb > self.MAX_EXECUTABLE_SIZE_MB:
                shutil.rmtree(dest_dir)
                return InstallResult(
                    success=False,
                    error_message=f"Executable too large ({file_size_mb:.1f}MB > {self.MAX_EXECUTABLE_SIZE_MB}MB)",
                )

            tool_path.chmod(stat.S_IRWXU)  # 0o700 - owner only

            tool_info = ToolInfo(
                name=config.name,
                version=config.version,
                path=tool_path,
                status=ToolStatus.INSTALLED,
                install_method=InstallMethod.BINARY,
                size_mb=self._get_size_mb(dest_dir),
            )

            return InstallResult(success=True, tool_info=tool_info)

        except (ValueError, RuntimeError, zipfile.BadZipFile) as e:
            # Security exceptions (path traversal, zip bombs, etc.)
            error_details = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Security error during binary install: {error_details}")
            # Clean up partial installation on any failure
            if dest_dir.exists():
                try:
                    shutil.rmtree(dest_dir)
                except (OSError, PermissionError) as cleanup_err:
                    logger.warning(f"Failed to clean up {dest_dir}: {cleanup_err}")
            return InstallResult(
                success=False,
                error_message=f"Security error: {e}",
            )
        except (OSError, PermissionError) as e:
            # Filesystem errors (permissions, disk full, etc.)
            error_details = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Filesystem error during binary install: {error_details}")
            # Clean up partial installation on any failure
            if dest_dir.exists():
                try:
                    shutil.rmtree(dest_dir)
                except (OSError, PermissionError) as cleanup_err:
                    logger.warning(f"Failed to clean up {dest_dir}: {cleanup_err}")
            return InstallResult(
                success=False,
                error_message=f"Filesystem error: {e}",
            )
        finally:
            # Issue #5: Always clean up download file in finally block
            if download_path and download_path.exists():
                try:
                    download_path.unlink()
                except (OSError, PermissionError) as e:
                    logger.warning(
                        f"Could not remove download file {download_path}: {e}"
                    )

    def _download_file(
        self, url: str, dest: Path, max_size_mb: int | None = None
    ) -> None:
        """Download a file from URL with timeout and size limit.

        Security:
            - Only HTTPS URLs are allowed for downloading binaries
            - SSL/TLS certificates are validated by default
            - Maximum download size enforced to prevent disk exhaustion

        Args:
            url: URL to download (must be HTTPS).
            dest: Destination path.
            max_size_mb: Maximum file size in MB (default: None = unlimited).

        Raises:
            ValueError: If URL is not HTTPS.
            RuntimeError: If download fails, times out, or exceeds size limit.
        """
        if not url.startswith("https://"):
            raise ValueError(f"Only HTTPS URLs are allowed for security, got: {url}")

        # Issue #3: Calculate max bytes for size enforcement
        max_bytes = (max_size_mb * 1024 * 1024) if max_size_mb else None
        total_downloaded = 0

        try:
            # Issue #15: Open file first to fail fast on file errors
            with open(dest, "wb") as f:
                with urlopen(url, timeout=self.DOWNLOAD_TIMEOUT_SECONDS) as response:
                    while True:
                        chunk = response.read(DOWNLOAD_CHUNK_SIZE)
                        if not chunk:
                            break

                        total_downloaded += len(chunk)
                        if max_bytes and total_downloaded > max_bytes:
                            raise RuntimeError(
                                f"Download exceeded maximum size: {max_size_mb}MB"
                            )

                        f.write(chunk)
        except (URLError, RuntimeError) as e:
            # Clean up partial download on any failure
            try:
                dest.unlink()
            except (OSError, FileNotFoundError):
                pass  # File may not exist or already deleted

            if isinstance(e, URLError):
                raise RuntimeError(f"Download failed: {e}") from e
            else:
                raise  # Re-raise RuntimeError (size exceeded)
        # Issue #18: Removed dead TimeoutError handler - URLError catches timeouts

    def _safe_extract_archive(self, archive_path: Path, dest_dir: Path) -> None:
        """Safely extract archive with security protections.

        Security:
            - Validates all paths using Path.relative_to() (not string prefix)
            - Rejects absolute paths in archive
            - Prevents directory traversal attacks (../)
            - Detects and rejects symlinks before resolution (TOCTOU protection)
            - Limits number of files to prevent zip bomb DoS
            - Uses temp directory for non-ZIP to prevent TOCTOU

        Args:
            archive_path: Path to archive file.
            dest_dir: Destination directory.

        Raises:
            RuntimeError: If archive contains suspicious paths or symlinks.
        """
        # Issue #3: Check both suffix and name for compound extensions
        suffix_lower = archive_path.suffix.lower()
        name_lower = archive_path.name.lower()

        if suffix_lower == ".zip":
            self._extract_zip_safely(archive_path, dest_dir)
        elif suffix_lower in [".tar", ".tgz"] or name_lower.endswith(
            (".tar.gz", ".tar.bz2", ".tar.xz")
        ):
            self._extract_tar_safely(archive_path, dest_dir)
        else:
            # For other archive types, use generic extraction with validation
            self._extract_non_zip_safely(archive_path, dest_dir)

    def _extract_zip_safely(self, archive_path: Path, dest_dir: Path) -> None:
        """Extract ZIP archive with security validation.

        Args:
            archive_path: Path to ZIP file.
            dest_dir: Destination directory.

        Raises:
            RuntimeError: If archive contains malicious content.
        """
        with zipfile.ZipFile(archive_path, "r") as zf:
            # Check file count to prevent zip bomb DoS
            member_count = len(zf.namelist())
            if member_count > self.MAX_ARCHIVE_FILES:
                raise RuntimeError(
                    f"Archive contains too many files ({member_count} > {self.MAX_ARCHIVE_FILES})"
                )

            # Pre-extraction validation
            for member in zf.namelist():
                # Check for absolute paths
                if Path(member).is_absolute():
                    raise RuntimeError(f"Archive contains absolute path: {member}")

                # Use Path.parts for path traversal check (not substring)
                if ".." in Path(member).parts:
                    raise RuntimeError(f"Archive contains path traversal: {member}")

                # Validate without resolve() to prevent TOCTOU with symlinks
                member_path = dest_dir / member
                # Check if path would escape using relative_to
                try:
                    member_path.relative_to(dest_dir)
                except ValueError:
                    raise RuntimeError(f"Archive member escapes destination: {member}")

                # Check for symlinks using _is_zip_symlink() method
                info = zf.getinfo(member)
                if self._is_zip_symlink(info):
                    raise RuntimeError(
                        f"Archive contains symlink (not allowed): {member}"
                    )

            # Track files before extraction to detect NEW files only
            files_before = set(dest_dir.rglob("*"))

            # All paths validated, safe to extract
            zf.extractall(dest_dir)

            # Issue #1/#2: Post-extraction check - only check NEW files for symlinks
            files_after = set(dest_dir.rglob("*"))
            new_files = files_after - files_before
            symlinks = [p for p in new_files if p.is_symlink()]
            if symlinks:
                for symlink_path in symlinks:
                    logger.warning(f"Removing symlink: {symlink_path}")
                    symlink_path.unlink()
                raise RuntimeError(
                    f"Zip archive contains {len(symlinks)} symlink(s): {', '.join(s.name for s in symlinks)}"
                )

    def _extract_tar_safely(self, archive_path: Path, dest_dir: Path) -> None:
        """Extract tar archive with security validation.

        Args:
            archive_path: Path to tar archive.
            dest_dir: Destination directory.

        Raises:
            RuntimeError: If archive contains malicious content.
        """
        try:
            with tarfile.open(archive_path, "r:*") as tf:
                # Pre-extraction validation
                member_count = 0
                for member in tf.getmembers():
                    member_count += 1
                    # Check file count limit during pre-extraction
                    if member_count > self.MAX_ARCHIVE_FILES:
                        raise RuntimeError(
                            f"Archive contains {member_count} files (>{self.MAX_ARCHIVE_FILES})"
                        )

                    # Check for absolute paths
                    if Path(member.name).is_absolute():
                        raise RuntimeError(
                            f"Archive contains absolute path: {member.name}"
                        )

                    # Check for path traversal
                    if ".." in Path(member.name).parts:
                        raise RuntimeError(
                            f"Archive contains path traversal: {member.name}"
                        )

                    # Detect symlinks BEFORE any path resolution (TOCTOU protection)
                    # Reject ALL symlinks for consistency with ZIP handling
                    if member.issym() or member.islnk():
                        raise RuntimeError(
                            f"Archive contains symlink (not allowed): {member.name}"
                        )

                    # Validate member path WITHOUT resolve() to avoid following symlinks
                    member_path = dest_dir / member.name
                    try:
                        # Use relative_to on non-resolved path
                        member_path.relative_to(dest_dir)
                    except ValueError:
                        raise RuntimeError(
                            f"Archive member escapes destination: {member.name}"
                        )

                # Track files before extraction to detect NEW files only
                files_before = set(dest_dir.rglob("*"))

                # All validated, extract
                tf.extractall(dest_dir)

                # Issue #4/#6: Post-extraction symlink check for defense in depth
                files_after = set(dest_dir.rglob("*"))
                new_files = files_after - files_before
                symlinks = [p for p in new_files if p.is_symlink()]
                if symlinks:
                    for symlink_path in symlinks:
                        logger.warning(f"Removing symlink: {symlink_path}")
                        symlink_path.unlink()
                    raise RuntimeError(
                        f"Tar archive contains {len(symlinks)} symlink(s): {', '.join(s.name for s in symlinks)}"
                    )
        except tarfile.TarError as e:
            # Issue #5/#8: Cleanup on tar extraction failure
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            raise RuntimeError(f"Failed to extract tar archive: {e}") from e
        except RuntimeError:
            # Issue #5/#8: Cleanup on validation failure
            if dest_dir.exists():
                shutil.rmtree(dest_dir)
            raise

    def _extract_non_zip_safely(self, archive_path: Path, dest_dir: Path) -> None:
        """Extract non-ZIP/non-tar archive with TOCTOU mitigation.

        Uses a temporary directory for extraction and validation
        before moving to the final destination.

        Args:
            archive_path: Path to archive file.
            dest_dir: Destination directory.

        Raises:
            RuntimeError: If archive contains malicious content.
        """
        # Issue #2: Extract to temp directory first to prevent TOCTOU
        temp_extract = dest_dir.parent / f".tmp_extract_{uuid.uuid4().hex}"

        try:
            temp_extract.mkdir(parents=True, exist_ok=True)

            # Extract to temp location
            shutil.unpack_archive(archive_path, temp_extract)

            # Post-extraction validation
            file_count = 0
            for item in temp_extract.rglob("*"):
                file_count += 1
                # File count limit check
                if file_count > self.MAX_ARCHIVE_FILES:
                    shutil.rmtree(temp_extract)
                    raise RuntimeError(
                        f"Archive contains {file_count} files (>{self.MAX_ARCHIVE_FILES})"
                    )

                # Check for symlinks BEFORE calling resolve() to prevent TOCTOU
                if item.is_symlink():
                    logger.warning(f"Removing symlink: {item}")
                    shutil.rmtree(temp_extract)
                    raise RuntimeError(
                        f"Archive contains symlink (not allowed): {item.name}"
                    )

                # Validate path without resolve() first
                try:
                    item.relative_to(temp_extract)
                except ValueError:
                    # Path escapes destination - remove it
                    shutil.rmtree(temp_extract)
                    raise RuntimeError(f"Extracted file escaped destination: {item}")

            # Validation passed - move contents to final destination
            for item in temp_extract.iterdir():
                dest_item = dest_dir / item.name
                if dest_item.exists():
                    if dest_item.is_dir():
                        shutil.rmtree(dest_item)
                    else:
                        dest_item.unlink()
                shutil.move(str(item), str(dest_dir / item.name))

        finally:
            # Always clean up temp directory
            if temp_extract.exists():
                shutil.rmtree(temp_extract)

    def _is_zip_symlink(self, zip_info: zipfile.ZipInfo) -> bool:
        """Check if a ZIP member is a symlink.

        Args:
            zip_info: ZIP file member info.

        Returns:
            True if the member is a symbolic link.
        """
        # Unix symlinks have the symlink bit set in external_attr
        # external_attr stores Unix mode in upper 16 bits
        unix_mode = zip_info.external_attr >> 16
        return stat.S_ISLNK(unix_mode) if unix_mode else False

    def _is_valid_version(self, version: str) -> bool:
        """Validate version string format.

        Args:
            version: Version string to validate.

        Returns:
            True if version format is valid (e.g., "1.0.0", "v2.15.0").
        """
        return bool(VERSION_PATTERN.match(version))

    def _validate_url_template(
        self, url_template: str, version: str
    ) -> tuple[bool, str]:
        """Validate URL template and substitution.

        Security:
            - Validates URL template contains only {version} placeholder
            - Checks for malformed URLs after substitution
            - Prevents double slashes (https://example.com//file)
            - Validates placeholder exists or version is empty

        Args:
            url_template: URL template with {version} placeholder.
            version: Version string to substitute.

        Returns:
            Tuple of (is_valid, error_message). error_message is empty if valid.
        """
        # Check for only allowed placeholder
        allowed_placeholders = ["{version}"]
        placeholders = re.findall(r"\{[^}]+\}", url_template)
        for placeholder in placeholders:
            if placeholder not in allowed_placeholders:
                return (
                    False,
                    f"Invalid URL template placeholder: {placeholder}. Only {{version}} is allowed.",
                )

        # Handle empty version
        if not version:
            if "{version}" in url_template:
                return (False, "URL template requires {version} but version is empty.")
            # No placeholder needed if version is empty
            final_url = url_template
        else:
            # Issue #3/#10: Substitute version with error handling using str(e)
            try:
                final_url = url_template.format(version=version)
            except KeyError as e:
                return (
                    False,
                    f"URL template contains unsupported placeholder: {str(e)}",
                )

        # Issue #2: Check for malformed URLs (double slashes except in protocol)
        # Split on :// to separate protocol from path
        parts = final_url.split("://", 1)
        if len(parts) == 2:
            protocol, rest = parts
            # Check for double slashes in the path/query part
            if "//" in rest:
                return (
                    False,
                    f"Malformed URL: {final_url}",
                )
        elif "//" in final_url:
            # Issue #2: Handle URLs without protocol (e.g., relative URLs)
            return (False, f"Malformed URL: {final_url}")

        # Basic URL validation
        try:
            parsed = urlparse(final_url)
            if not parsed.scheme or not parsed.netloc:
                return (False, f"Invalid URL after substitution: {final_url}")
        except Exception as e:
            return (False, f"URL parsing failed: {e}")

        return (True, "")

    def _get_filename_from_url(self, url: str) -> str:
        """Extract filename with extension from URL.

        Args:
            url: URL to extract filename from.

        Returns:
            Filename with extension, or "download.bin" if cannot determine.
        """
        try:
            parsed = urlparse(url)
            path = parsed.path
            if path:
                filename = Path(path).name
                if filename and "." in filename:
                    return filename
        except Exception as e:
            # Issue #9: Add logging to empty except clause
            logger.debug(f"Failed to extract filename from URL '{url}': {e}")
        # Default fallback
        return "download.bin"

    def get_cache_info(self) -> CacheInfo:
        """Get information about the tool cache.

        Returns:
            CacheInfo with size and tool details.
        """
        total_size = 0.0
        tools = []

        try:
            if not self.cache_dir.exists():
                return CacheInfo(
                    cache_dir=self.cache_dir,
                    total_size_mb=0.0,
                    tool_count=0,
                    tools=[],
                )

            for item in self.cache_dir.iterdir():
                if item.is_dir():
                    try:
                        size_mb = self._get_size_mb(item)
                        total_size += size_mb
                        # Get actual version for cached tools
                        version = "cached"
                        exe_path = self._find_in_directory(item, item.name)
                        if exe_path:
                            version = self._get_tool_version(item.name, exe_path)
                        tools.append(
                            ToolInfo(
                                name=item.name,
                                version=version,
                                path=item,
                                status=ToolStatus.INSTALLED,
                                install_method=InstallMethod.BINARY,
                                size_mb=size_mb,
                            )
                        )
                    except (OSError, PermissionError) as e:
                        logger.warning(f"Could not read cache entry {item}: {e}")
                        continue
        except (OSError, PermissionError) as e:
            logger.error(f"Could not read cache directory: {e}")
            return CacheInfo(
                cache_dir=self.cache_dir,
                total_size_mb=0.0,
                tool_count=0,
                tools=[],
            )

        return CacheInfo(
            cache_dir=self.cache_dir,
            total_size_mb=total_size,
            tool_count=len(tools),
            tools=tools,
            size_warning=total_size > self.CACHE_WARNING_THRESHOLD_MB,
            warning_threshold_mb=self.CACHE_WARNING_THRESHOLD_MB,
        )

    def check_for_updates(self, tool_name: str) -> tuple[bool, str | None]:
        """Check if a tool has updates available.

        Args:
            tool_name: Name of the tool.

        Returns:
            Tuple of (update_available, latest_version).
        """
        if tool_name not in self.tool_configs:
            return (False, None)

        config = self.tool_configs[tool_name]
        current = self.get_tool_info(tool_name)

        if not current:
            return (False, None)

        if config.version and current.version != config.version:
            return (True, config.version)

        return (False, None)

    def update_tool(self, tool_name: str) -> InstallResult:
        """Update a tool to the configured version.

        Args:
            tool_name: Name of the tool.

        Returns:
            InstallResult with status.
        """
        return self.install(tool_name, accept_license=True, force=True)

    def _find_tool(self, tool_name: str) -> Path | None:
        """Find tool in search paths.

        Args:
            tool_name: Name of the tool.

        Returns:
            Path to executable or None.
        """
        # 1. System PATH
        system_path = shutil.which(tool_name)
        if system_path:
            return Path(system_path)

        # 2. Current venv
        venv_path = self._find_in_venv(tool_name)
        if venv_path:
            return venv_path

        # 3. Cache directory
        cached = self._find_in_cache(tool_name)
        if cached:
            return cached

        return None

    def _find_in_venv(self, tool_name: str) -> Path | None:
        """Find tool in virtual environment.

        Args:
            tool_name: Name of the tool.

        Returns:
            Path if found, None otherwise.
        """
        venv_dirs = [
            Path.cwd() / ".venv",
            Path.cwd() / "venv",
            Path(sys.prefix),
        ]

        for venv_dir in venv_dirs:
            if not venv_dir.exists():
                continue
            for bin_dir in ["bin", "Scripts"]:
                tool_path = venv_dir / bin_dir / tool_name
                if tool_path.exists():
                    return tool_path
        return None

    def _find_in_cache(self, tool_name: str) -> Path | None:
        """Find tool in cache directory.

        Args:
            tool_name: Name of the tool.

        Returns:
            Path if found, None otherwise.
        """
        tool_dir = self.cache_dir / tool_name
        if not tool_dir.exists():
            return None

        try:
            versions = sorted(
                tool_dir.iterdir(),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            for version_dir in versions:
                if version_dir.is_dir():
                    executable = self._find_in_directory(version_dir, tool_name)
                    if executable:
                        return executable
        except (OSError, PermissionError):
            # Issue #19: Comment explaining why we ignore errors
            # Ignore permission errors during cache search - continue with other methods
            pass

        return None

    def _find_in_directory(
        self, directory: Path, tool_name: str, max_depth: int | None = None
    ) -> Path | None:
        """Find executable in directory tree with depth limit.

        Args:
            directory: Directory to search.
            tool_name: Name of the tool.
            max_depth: Maximum search depth (default: MAX_SEARCH_DEPTH).

        Returns:
            Path to executable or None.
        """
        if max_depth is None:
            max_depth = self.MAX_SEARCH_DEPTH

        return self._find_executable_recursive(directory, tool_name, 0, max_depth)

    def _find_executable_recursive(
        self, directory: Path, tool_name: str, current_depth: int, max_depth: int
    ) -> Path | None:
        """Recursively find executable with depth limit.

        Args:
            directory: Current directory to search.
            tool_name: Name of the tool.
            current_depth: Current recursion depth.
            max_depth: Maximum allowed depth.

        Returns:
            Path to executable or None.
        """
        if current_depth > max_depth:
            return None

        try:
            for item in directory.iterdir():
                if item.name == tool_name and item.is_file():
                    if os.access(item, os.X_OK):
                        return item
                if item.name == f"{tool_name}.exe" and item.is_file():
                    return item
                if item.is_dir() and current_depth < max_depth:
                    result = self._find_executable_recursive(
                        item, tool_name, current_depth + 1, max_depth
                    )
                    if result:
                        return result
        except (OSError, PermissionError):
            # Issue #19: Comment explaining why we ignore errors
            # Ignore permission errors during recursive search - continue checking other directories
            pass

        return None

    def _get_tool_version(self, tool_name: str, tool_path: Path) -> str:
        """Get version of installed tool.

        Security:
            - Validates tool_path doesn't contain shell metacharacters
            - Uses resolved absolute path to prevent TOCTOU
            - Limited timeout prevents hang

        Args:
            tool_name: Name of the tool.
            tool_path: Path to executable.

        Returns:
            Version string or "unknown".
        """
        try:
            # Issue #8: Validate path before subprocess execution
            resolved_path = tool_path.resolve()
            path_str = str(resolved_path)

            # Check for shell metacharacters that could enable command injection
            if any(char in path_str for char in DANGEROUS_PATH_CHARS):
                logger.warning(f"Tool path contains dangerous characters: {path_str}")
                return "unknown"

            result = subprocess.run(
                [path_str, "--version"],
                capture_output=True,
                text=True,
                timeout=VERSION_CHECK_TIMEOUT_SECONDS,
            )
            output = result.stdout.strip() or result.stderr.strip()
            if output:
                match = VERSION_SEARCH_PATTERN.search(output)
                if match:
                    return match.group(1)
            return "unknown"
        except Exception as e:
            logger.debug(f"Failed to get version for {tool_name}: {e}")
            return "unknown"

    def _determine_status(self, tool_name: str, version: str) -> ToolStatus:
        """Determine tool status based on version.

        Args:
            tool_name: Name of the tool.
            version: Installed version.

        Returns:
            ToolStatus enum value.
        """
        if tool_name not in self.tool_configs:
            return ToolStatus.INSTALLED

        config = self.tool_configs[tool_name]
        if config.version and version != config.version:
            return ToolStatus.UPDATE_AVAILABLE

        return ToolStatus.INSTALLED

    def _detect_install_method(self, tool_path: Path) -> InstallMethod:
        """Detect how tool was installed.

        Args:
            tool_path: Path to executable.

        Returns:
            InstallMethod enum value.
        """
        path_str = str(tool_path)
        # Issue #16: Use path parts instead of substring to avoid false positives
        parts = tool_path.parts

        if str(self.cache_dir) in path_str:
            return InstallMethod.BINARY
        elif "site-packages" in parts or ".venv" in parts or "venv" in parts:
            return InstallMethod.PIP
        else:
            return InstallMethod.SYSTEM

    def _get_size_mb(self, path: Path) -> float:
        """Get size of file or directory in MB.

        Args:
            path: Path to measure.

        Returns:
            Size in megabytes.
        """
        if path.is_file():
            return path.stat().st_size / (1024 * 1024)

        total = 0
        try:
            for dirpath, _, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        # Issue #19: Comment explaining why we ignore errors
                        # Ignore errors reading individual files - continue calculating total
                        continue
        except (OSError, PermissionError):
            # Issue #19: Comment explaining why we ignore errors
            # Ignore errors walking directory - return partial total
            pass

        return total / (1024 * 1024)

    def _get_platform_key(self) -> str:
        """Get platform key for binary downloads.

        Returns:
            Platform identifier (linux, darwin, win32).

        Raises:
            RuntimeError: If platform is not supported.
        """
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "darwin":
            return "darwin"
        elif system == "windows":
            return "win32"
        else:
            # Issue #11: Raise error for unsupported platforms instead of broken fallback
            raise RuntimeError(
                f"Unsupported platform: {system}. "
                f"Supported platforms: linux, darwin, win32"
            )
