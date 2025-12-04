"""Data models for tool dependency management.

This module contains dataclasses and enums for representing
tool configurations, installation status, and cache information.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ToolStatus(Enum):
    """Status of a security tool installation."""

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
    SYSTEM = "system"


@dataclass
class ToolConfig:
    """Configuration for a security scanning tool.

    Attributes:
        name: Tool name (e.g., "semgrep").
        version: Pinned version string.
        install_method: How to install the tool.
        license_check: Whether license acceptance is required.
        license_url: URL to license terms.
        binary_urls: Platform-specific download URLs.
        pip_package: PyPI package name if different from tool name.
        size_estimate_mb: Estimated download size in MB.
    """

    name: str
    version: str | None = None
    install_method: InstallMethod = InstallMethod.PIP
    license_check: bool = False
    license_url: str | None = None
    binary_urls: dict[str, str] = field(default_factory=dict)
    pip_package: str | None = None
    size_estimate_mb: int = 0


@dataclass
class ToolInfo:
    """Information about an installed tool.

    Attributes:
        name: Tool name.
        version: Installed version string.
        path: Path to executable.
        status: Current installation status.
        install_method: How the tool was installed.
        size_mb: Actual size in MB.
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
        error_message: Error description if failed.
        license_required: Whether license acceptance is needed.
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
        total_size_mb: Total size of cached tools.
        tool_count: Number of cached tools.
        tools: List of cached tool info.
        size_warning: True if over threshold.
        warning_threshold_mb: Size threshold for warning.
    """

    cache_dir: Path
    total_size_mb: float
    tool_count: int
    tools: list[ToolInfo]
    size_warning: bool = False
    warning_threshold_mb: int = 500


# Default configurations for supported tools
DEFAULT_TOOL_CONFIGS: dict[str, ToolConfig] = {
    "semgrep": ToolConfig(
        name="semgrep",
        version="1.45.0",
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
