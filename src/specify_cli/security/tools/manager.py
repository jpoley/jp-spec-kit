"""Tool dependency manager for security scanners.

This module provides the main ToolManager class for installing,
managing, and monitoring security scanning tools.

Features:
- Auto-installation with version pinning
- License compliance checking (CodeQL)
- Dependency size monitoring (alert at 500MB)
- Offline mode for air-gapped environments
- Cross-platform support
"""

import logging
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

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


class ToolManager:
    """Manager for security scanning tool dependencies.

    This class handles:
    - Tool discovery and installation
    - Version pinning and updates
    - License compliance checking
    - Cache size monitoring
    - Offline mode operation

    Example:
        >>> manager = ToolManager()
        >>> result = manager.install("semgrep")
        >>> if result.success:
        ...     print(f"Installed at: {result.tool_info.path}")
    """

    # Cache size warning threshold in MB
    CACHE_WARNING_THRESHOLD_MB = 500

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

        Raises:
            ValueError: If tool_name is not in configurations.
        """
        if tool_name not in self.tool_configs:
            return InstallResult(
                success=False,
                error_message=f"Unknown tool: {tool_name}. Available: {list(self.tool_configs.keys())}",
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
                timeout=300,  # 5 minute timeout
                check=True,
            )

            # Find the installed tool
            tool_path = self._find_tool(config.name)
            if not tool_path:
                return InstallResult(
                    success=False,
                    error_message=f"Installed {package} but could not find {config.name} executable",
                )

            tool_info = self.get_tool_info(config.name)
            return InstallResult(success=True, tool_info=tool_info)

        except subprocess.CalledProcessError as e:
            return InstallResult(
                success=False,
                error_message=f"pip install failed: {e.stderr}",
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

        url = config.binary_urls[platform_key].format(version=config.version)
        dest_dir = self.cache_dir / config.name / config.version

        try:
            # Download and extract
            logger.info(f"Downloading {config.name} from {url}")
            dest_dir.mkdir(parents=True, exist_ok=True)

            # Use curl or wget for download
            download_path = dest_dir / "download.zip"
            self._download_file(url, download_path)

            # Extract
            shutil.unpack_archive(download_path, dest_dir)
            download_path.unlink()

            # Find executable
            tool_path = self._find_in_directory(dest_dir, config.name)
            if not tool_path:
                return InstallResult(
                    success=False,
                    error_message=f"Downloaded but could not find {config.name} executable",
                )

            # Make executable
            tool_path.chmod(tool_path.stat().st_mode | 0o755)

            tool_info = ToolInfo(
                name=config.name,
                version=config.version or "unknown",
                path=tool_path,
                status=ToolStatus.INSTALLED,
                install_method=InstallMethod.BINARY,
                size_mb=self._get_size_mb(dest_dir),
            )

            return InstallResult(success=True, tool_info=tool_info)

        except Exception as e:
            logger.error(f"Binary install failed: {e}")
            return InstallResult(
                success=False,
                error_message=f"Binary install failed: {e}",
            )

    def _download_file(self, url: str, dest: Path) -> None:
        """Download a file from URL.

        Args:
            url: URL to download.
            dest: Destination path.

        Raises:
            RuntimeError: If download fails.
        """
        import urllib.request

        try:
            urllib.request.urlretrieve(url, dest)
        except Exception as e:
            raise RuntimeError(f"Download failed: {e}") from e

    def get_cache_info(self) -> CacheInfo:
        """Get information about the tool cache.

        Returns:
            CacheInfo with size and tool details.
        """
        total_size = 0.0
        tools = []

        for item in self.cache_dir.iterdir():
            if item.is_dir():
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

        # Compare with configured version
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

        # Find most recent version
        versions = sorted(tool_dir.iterdir(), reverse=True)
        for version_dir in versions:
            if version_dir.is_dir():
                executable = self._find_in_directory(version_dir, tool_name)
                if executable:
                    return executable

        return None

    def _find_in_directory(self, directory: Path, tool_name: str) -> Path | None:
        """Find executable in directory tree.

        Args:
            directory: Directory to search.
            tool_name: Name of the tool.

        Returns:
            Path to executable or None.
        """
        for path in directory.rglob(tool_name):
            if path.is_file() and os.access(path, os.X_OK):
                return path
        for path in directory.rglob(f"{tool_name}.exe"):
            if path.is_file():
                return path
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
            # Parse version from output
            output = result.stdout.strip()
            if output:
                # Common patterns: "1.0.0", "tool version 1.0.0", "v1.0.0"
                parts = output.split()
                for part in parts:
                    if part[0].isdigit() or (part.startswith("v") and len(part) > 1):
                        return part.lstrip("v")
            return "unknown"
        except Exception:
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

        if self.cache_dir and str(self.cache_dir) in path_str:
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
        for item in path.rglob("*"):
            if item.is_file():
                total += item.stat().st_size

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
