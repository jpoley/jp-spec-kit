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
- Path traversal protection in archive extraction
- Symlink attack detection
- Version format validation
"""

import logging
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import zipfile
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from specify_cli.security.tools.models import (
    DEFAULT_TOOL_CONFIGS,
    CacheInfo,
    InstallMethod,
    InstallResult,
    ToolConfig,
    ToolInfo,
    ToolStatus,
)

logger = logging.getLogger(__name__)

# Anchored regex for exact version validation (rejects "1.2.3.4.5")
VERSION_PATTERN = re.compile(r"^v?(\d+\.\d+(?:\.\d+)?(?:-[\w.]+)?)$")

# Unanchored regex for extracting version from tool output
VERSION_SEARCH_PATTERN = re.compile(r"v?(\d+\.\d+(?:\.\d+)?(?:-[\w.]+)?)")


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
        - Archives validated for path traversal attacks
        - Symlinks in archives are rejected
        - Version strings are validated before use

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

        # Check offline mode
        if self.offline_mode:
            cached = self._find_in_cache(tool_name)
            if cached:
                return InstallResult(
                    success=True,
                    tool_info=ToolInfo(
                        name=tool_name,
                        version="cached",
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
                timeout=300,
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
            error_msg = str(e.stderr).split("\n")[0][:200] if e.stderr else str(e)
            return InstallResult(
                success=False,
                error_message=f"pip install failed: {error_msg}",
            )
        except subprocess.TimeoutExpired:
            return InstallResult(
                success=False,
                error_message="Installation timed out after 5 minutes",
            )

    def _install_binary(self, config: ToolConfig) -> InstallResult:
        """Install tool by downloading binary.

        Args:
            config: Tool configuration.

        Returns:
            InstallResult with status.
        """
        platform_key = self._get_platform_key()
        if platform_key not in config.binary_urls:
            return InstallResult(
                success=False,
                error_message=f"No binary available for platform: {platform_key}",
            )

        # Validate version format before URL construction
        if config.version and not self._is_valid_version(config.version):
            return InstallResult(
                success=False,
                error_message=f"Invalid version format: {config.version}",
            )

        url = config.binary_urls[platform_key].format(version=config.version or "")
        dest_dir = self.cache_dir / config.name / (config.version or "latest")

        try:
            logger.info(f"Downloading {config.name} from {url}")
            dest_dir.mkdir(parents=True, exist_ok=True)

            download_path = dest_dir / "download.zip"
            self._download_file(url, download_path)

            # Count files before extraction
            files_before = set(dest_dir.rglob("*"))

            # Extract with security validation
            self._safe_extract_archive(download_path, dest_dir)

            # Validate extraction produced files
            files_after = set(dest_dir.rglob("*"))
            new_files = files_after - files_before - {download_path}
            if not new_files:
                return InstallResult(
                    success=False,
                    error_message="Archive extraction produced no files",
                )

            download_path.unlink()

            tool_path = self._find_in_directory(dest_dir, config.name)
            if not tool_path:
                return InstallResult(
                    success=False,
                    error_message=f"Could not find {config.name} executable",
                )

            # Set executable permission (owner only for security)
            if tool_path.is_file():
                tool_path.chmod(stat.S_IRWXU)  # 0o700 - owner only
            else:
                return InstallResult(
                    success=False,
                    error_message=f"Found path is not a valid file: {tool_path}",
                )

            tool_info = ToolInfo(
                name=config.name,
                version=config.version or "unknown",
                path=tool_path,
                status=ToolStatus.INSTALLED,
                install_method=InstallMethod.BINARY,
                size_mb=self._get_size_mb(dest_dir),
            )

            return InstallResult(success=True, tool_info=tool_info)

        except (OSError, RuntimeError, zipfile.BadZipFile) as e:
            logger.error(f"Binary install failed: {type(e).__name__}: {e}")
            return InstallResult(
                success=False,
                error_message="Binary installation failed",
            )

    def _download_file(self, url: str, dest: Path) -> None:
        """Download a file from URL with timeout.

        Security:
            - Only HTTPS URLs are allowed for downloading binaries
            - SSL/TLS certificates are validated by default

        Args:
            url: URL to download (must be HTTPS).
            dest: Destination path.

        Raises:
            ValueError: If URL is not HTTPS.
            RuntimeError: If download fails or times out.
        """
        if not url.startswith("https://"):
            raise ValueError(f"Only HTTPS URLs are allowed for security, got: {url}")

        try:
            with urlopen(url, timeout=self.DOWNLOAD_TIMEOUT_SECONDS) as response:
                with open(dest, "wb") as f:
                    chunk_size = 8192
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
        except URLError as e:
            raise RuntimeError(f"Download failed: {e}") from e
        except TimeoutError as e:
            raise RuntimeError(
                f"Download timed out after {self.DOWNLOAD_TIMEOUT_SECONDS}s"
            ) from e

    def _safe_extract_archive(self, archive_path: Path, dest_dir: Path) -> None:
        """Safely extract archive with security protections.

        Security:
            - Validates all paths are within destination directory
            - Rejects absolute paths in archive
            - Prevents directory traversal attacks (../)
            - Rejects symlinks that could escape destination

        Args:
            archive_path: Path to archive file.
            dest_dir: Destination directory.

        Raises:
            RuntimeError: If archive contains suspicious paths or symlinks.
        """
        dest_dir_resolved = dest_dir.resolve()

        if str(archive_path).endswith(".zip"):
            with zipfile.ZipFile(archive_path, "r") as zf:
                for member in zf.namelist():
                    # Check for absolute paths
                    if Path(member).is_absolute():
                        raise RuntimeError(f"Archive contains absolute path: {member}")

                    # Check for path traversal using path components
                    # This correctly allows files like "README..md"
                    if ".." in Path(member).parts:
                        raise RuntimeError(f"Archive contains path traversal: {member}")

                    # Verify resolved path is within dest_dir
                    member_path = (dest_dir / member).resolve()
                    if not str(member_path).startswith(str(dest_dir_resolved)):
                        raise RuntimeError(
                            f"Archive member escapes destination: {member}"
                        )

                    # Check for symlinks (zipfile stores them as external_attr)
                    info = zf.getinfo(member)
                    if self._is_zip_symlink(info):
                        raise RuntimeError(
                            f"Archive contains symlink (not allowed): {member}"
                        )

                zf.extractall(dest_dir)
        else:
            # For other archive types, use shutil with post-validation
            shutil.unpack_archive(archive_path, dest_dir)

            # Post-extraction validation
            for item in dest_dir.rglob("*"):
                # Check for symlinks
                if item.is_symlink():
                    item.unlink()
                    raise RuntimeError(f"Extracted symlink removed: {item}")

                item_resolved = item.resolve()
                if not str(item_resolved).startswith(str(dest_dir_resolved)):
                    if item.is_file():
                        item.unlink()
                    raise RuntimeError(f"Extracted file escaped destination: {item}")

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
                        tools.append(
                            ToolInfo(
                                name=item.name,
                                version="cached",
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
            return None

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
            pass

        return None

    def _get_tool_version(self, tool_name: str, tool_path: Path) -> str:
        """Get version of installed tool.

        Args:
            tool_name: Name of the tool.
            tool_path: Path to executable.

        Returns:
            Version string or "unknown".
        """
        try:
            result = subprocess.run(
                [str(tool_path), "--version"],
                capture_output=True,
                text=True,
                timeout=5,
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

        if str(self.cache_dir) in path_str:
            return InstallMethod.BINARY
        elif "site-packages" in path_str or ".venv" in path_str or "venv" in path_str:
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
                        continue
        except (OSError, PermissionError):
            pass

        return total / (1024 * 1024)

    def _get_platform_key(self) -> str:
        """Get platform key for binary downloads.

        Returns:
            Platform identifier (linux, darwin, win32).
        """
        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "darwin":
            return "darwin"
        elif system == "windows":
            return "win32"
        return system
