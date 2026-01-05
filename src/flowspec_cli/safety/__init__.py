"""Safety configuration for Claude Code hooks.

This module handles configuration for GitHub PR safety guards and other
safety-related settings that prevent Claude from performing destructive operations.
"""

from .github_pr import (
    GITHUB_PR_SAFETY_DEFAULTS,
    configure_github_pr_safety,
    get_github_pr_safety_config,
    has_github_pr_safety_config,
    prompt_github_pr_safety,
    resolve_pr_safety_settings,
)

__all__ = [
    "GITHUB_PR_SAFETY_DEFAULTS",
    "configure_github_pr_safety",
    "get_github_pr_safety_config",
    "has_github_pr_safety_config",
    "prompt_github_pr_safety",
    "resolve_pr_safety_settings",
]
