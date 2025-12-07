"""Push Rules - Git workflow enforcement configuration.

This module provides configuration loading, validation, and querying for
push-rules.md files that define mandatory pre-push validation checks.

Example:
    >>> from specify_cli.push_rules import load_push_rules
    >>> config = load_push_rules(Path("push-rules.md"))
    >>> print(config.rebase_policy.enforcement)
    'strict'
"""

from .models import (
    JanitorSettings,
    PushRulesConfig,
    RebaseEnforcement,
    RebasePolicy,
    ValidationCommand,
)
from .parser import (
    PushRulesError,
    PushRulesNotFoundError,
    PushRulesParseError,
    PushRulesValidationError,
    load_push_rules,
    validate_push_rules,
)
from .scaffold import (
    get_scaffold_summary,
    get_template_content,
    scaffold_push_rules,
)

__all__ = [
    # Models
    "PushRulesConfig",
    "RebasePolicy",
    "RebaseEnforcement",
    "ValidationCommand",
    "JanitorSettings",
    # Parser functions
    "load_push_rules",
    "validate_push_rules",
    # Exceptions
    "PushRulesError",
    "PushRulesNotFoundError",
    "PushRulesParseError",
    "PushRulesValidationError",
    # Scaffold functions
    "scaffold_push_rules",
    "get_scaffold_summary",
    "get_template_content",
]
