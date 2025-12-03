"""Security scanner adapters for unified vulnerability scanning.

This module provides adapters for integrating various security scanning tools
(Semgrep, CodeQL, Trivy, etc.) into a common interface. Each adapter:

1. Implements the ScannerAdapter interface
2. Translates tool-specific configuration to tool commands
3. Parses tool output to Unified Finding Format (UFFormat)
4. Handles tool discovery and installation

See ADR-005 for architectural design decisions.
"""

from specify_cli.security.adapters.base import ScannerAdapter
from specify_cli.security.adapters.discovery import ToolDiscovery

__all__ = ["ScannerAdapter", "ToolDiscovery"]
