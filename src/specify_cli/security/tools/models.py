"""Data models for tool dependency management.

This module defines the data structures used for managing security
scanning tool dependencies, including configuration, status, and
installation results.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ToolStatus(Enum):
    """Status of a security scanning tool."""

    NOT_INSTALLED = "not_installed"
    INSTALLED = "installed"
    UPDATE_AVAILABLE = "update_available"
    LICENSE_REQUIRED = "license_required"
    OFFLINE_ONLY = "offline_only"


class InstallMethod(Enum):
    """Method used to install a tool."""

    PIP = "pip"
    BINARY = "binary"
    DOCKER = "docker"
    SYSTEM = "system"  # Already installed via system package manager


@dataclass
class ToolConfig:
    """Configuration for a security scanning tool.

    Attributes:
        name: Tool identifier (e.g., "semgrep", "codeql").
        version: Pinned version (e.g., "1.45.0") or None for latest.
        install_method: How to install the tool.
        license_check: Whether tool requires license acceptance.
        license_url: URL to license terms if license_check is True.
        binary_urls: Platform-specific binary download URLs.
        pip_package: Package name for pip installation.
        size_estimate_mb: Estimated size in MB for download monitoring.
    """

    name: str
    version: str | None = None
    install_method: InstallMethod = InstallMethod.PIP
    license_check: bool = False
    license_url: str | None = None
    binary_urls: dict[str, str] = field(default_factory=dict)
    pip_package: str | None = None
    size_estimate_mb: int = 50


@dataclass
class ToolInfo:
    """Information about an installed tool.

    Attributes:
        name: Tool identifier.
        version: Installed version string.
        path: Path to executable.
        status: Current tool status.
        install_method: How the tool was installed.
        size_mb: Size of installation in MB.
    """

    name: str
    version: str
    path: Path
    status: ToolStatus
    install_method: InstallMethod
    size_mb: float = 0.0


@dataclass
class InstallResult:
    """Result of a tool installation attempt.

    Attributes:
        success: Whether installation succeeded.
        tool_info: Tool information if successful.
        error_message: Error message if failed.
        license_required: Whether user needs to accept license.
    """

    success: bool
    tool_info: ToolInfo | None = None
    error_message: str | None = None
    license_required: bool = False


@dataclass
class CacheInfo:
    """Information about the tool cache.

    Attributes:
        cache_dir: Path to cache directory.
        total_size_mb: Total size of cached tools in MB.
        tool_count: Number of cached tools.
        tools: List of cached tool information.
        size_warning: True if cache exceeds warning threshold.
        warning_threshold_mb: Size threshold that triggers warning.
    """

    cache_dir: Path
    total_size_mb: float
    tool_count: int
    tools: list[ToolInfo]
    size_warning: bool = False
    warning_threshold_mb: int = 500


# Default tool configurations
DEFAULT_TOOL_CONFIGS: dict[str, ToolConfig] = {
    "semgrep": ToolConfig(
        name="semgrep",
        version="1.45.0",  # Pinned for reproducibility
        install_method=InstallMethod.PIP,
        pip_package="semgrep",
        size_estimate_mb=100,
    ),
    "codeql": ToolConfig(
        name="codeql",
        version="2.15.0",
        install_method=InstallMethod.BINARY,
        license_check=True,
        license_url="https://github.com/github/codeql-cli-binaries/blob/main/LICENSE.md",
        binary_urls={
            "linux": "https://github.com/github/codeql-cli-binaries/releases/download/v{version}/codeql-linux64.zip",
            "darwin": "https://github.com/github/codeql-cli-binaries/releases/download/v{version}/codeql-osx64.zip",
            "win32": "https://github.com/github/codeql-cli-binaries/releases/download/v{version}/codeql-win64.zip",
        },
        size_estimate_mb=400,
    ),
    "bandit": ToolConfig(
        name="bandit",
        version="1.7.7",
        install_method=InstallMethod.PIP,
        pip_package="bandit",
        size_estimate_mb=10,
    ),
}
