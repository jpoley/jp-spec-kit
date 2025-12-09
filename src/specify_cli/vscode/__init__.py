"""VS Code integration module for Specflow.

This module provides utilities for integrating Specflow with VS Code Copilot,
including:
- Settings generation for agent pinning
- Role-based agent prioritization
- Command namespace configuration
"""

from .settings_generator import VSCodeSettingsGenerator

__all__ = ["VSCodeSettingsGenerator"]
