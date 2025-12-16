"""VS Code integration module for flowspec.

This module provides utilities for integrating flowspec with VS Code Copilot,
including:
- Settings generation for agent pinning
- Role-based agent prioritization
- Command namespace configuration
"""

from .settings_generator import VSCodeSettingsGenerator

__all__ = ["VSCodeSettingsGenerator"]
