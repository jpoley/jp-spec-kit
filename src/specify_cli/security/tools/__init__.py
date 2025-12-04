"""Tool dependency management for security scanners.

This module provides installation, version management, and caching
for security scanning tools like Semgrep and CodeQL.

Features:
- Auto-installation with version pinning
- License compliance checking (CodeQL)
- Dependency size monitoring
- Offline mode for air-gapped environments
- Cross-platform support (Linux, macOS, Windows)
"""

from specify_cli.security.tools.manager import ToolManager
from specify_cli.security.tools.models import (
    CacheInfo,
    InstallResult,
    ToolConfig,
    ToolInfo,
    ToolStatus,
)

__all__ = [
    "ToolManager",
    "ToolConfig",
    "ToolInfo",
    "ToolStatus",
    "InstallResult",
    "CacheInfo",
]
