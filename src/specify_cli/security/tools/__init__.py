"""Tool dependency management for security scanners.

This module provides tools for managing security scanning dependencies
like Semgrep, CodeQL, and Bandit.

Features:
- Auto-installation with version pinning
- License compliance checking (CodeQL)
- Dependency size monitoring (alert at 500MB)
- Offline mode for air-gapped environments
- Cross-platform support (Linux, macOS, Windows)
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
    "CacheInfo",
    "InstallMethod",
    "InstallResult",
    "ToolConfig",
    "ToolInfo",
    "ToolManager",
    "ToolStatus",
]
