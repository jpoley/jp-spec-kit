"""Tool dependency management for security scanners.

This module provides:
- ToolManager: Main class for installing and managing security tools
- Data models: ToolConfig, ToolInfo, InstallResult, CacheInfo
- Enums: ToolStatus, InstallMethod

Example:
    >>> from specify_cli.security.tools import ToolManager
    >>> manager = ToolManager()
    >>> result = manager.install("semgrep")
    >>> if result.success:
    ...     print(f"Installed at: {result.tool_info.path}")

Security Features:
    - HTTPS-only downloads (HTTP rejected)
    - Path traversal protection via Path.relative_to()
    - Symlink attack detection
    - Maximum download size enforcement
    - Pip installs use --no-deps to prevent dependency confusion
"""

from specify_cli.security.tools.manager import ToolManager
from specify_cli.security.tools.models import (
    CacheInfo,
    InstallMethod,
    InstallResult,
    ToolConfig,
    ToolInfo,
    ToolStatus,
)

__all__ = [
    "ToolManager",
    "ToolConfig",
    "ToolInfo",
    "InstallResult",
    "CacheInfo",
    "ToolStatus",
    "InstallMethod",
]
