"""Workflow configuration and validation module.

This module provides workflow configuration loading, validation, and
transition schema definitions for JPSpec workflows.

Key components:
- WorkflowConfig: Load and query workflow configuration from YAML
- WorkflowValidator: Semantic validation of workflow configuration
- TransitionSchema: Define input/output artifacts and validation modes
- ValidationMode: Transition gate types (NONE, KEYWORD, PULL_REQUEST)
"""

from specify_cli.workflow.config import WorkflowConfig
from specify_cli.workflow.exceptions import (
    WorkflowConfigError,
    WorkflowConfigNotFoundError,
    WorkflowConfigValidationError,
    WorkflowNotFoundError,
    WorkflowStateError,
)
from specify_cli.workflow.transition import (
    WORKFLOW_TRANSITIONS,
    Artifact,
    KeywordValidation,
    TransitionSchema,
    ValidationMode,
    format_validation_mode,
    get_transition_by_name,
    get_transitions_from_state,
    parse_validation_mode,
    validate_transition_schema,
)
from specify_cli.workflow.validator import (
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    WorkflowValidator,
    validate_workflow,
)

__all__ = [
    # Configuration
    "WorkflowConfig",
    # Exceptions
    "WorkflowConfigError",
    "WorkflowConfigNotFoundError",
    "WorkflowConfigValidationError",
    "WorkflowNotFoundError",
    "WorkflowStateError",
    # Transition Schema
    "Artifact",
    "KeywordValidation",
    "TransitionSchema",
    "ValidationMode",
    "WORKFLOW_TRANSITIONS",
    "format_validation_mode",
    "get_transition_by_name",
    "get_transitions_from_state",
    "parse_validation_mode",
    "validate_transition_schema",
    # Validation
    "ValidationSeverity",
    "ValidationIssue",
    "ValidationResult",
    "WorkflowValidator",
    "validate_workflow",
]
