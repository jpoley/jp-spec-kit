"""Workflow configuration and validation module.

This module provides workflow configuration loading, validation, and
transition schema definitions for JPSpec workflows.

Key components:
- WorkflowConfig: Load and query workflow configuration from YAML
- WorkflowValidator: Semantic validation of workflow configuration
- TransitionSchema: Define input/output artifacts and validation modes
- ValidationMode: Transition gate types (NONE, KEYWORD, PULL_REQUEST)
- PRDValidator: Validate PRD artifacts for transition gates
- ADRValidator: Validate ADR artifacts for transition gates
- TransitionValidator: Validate transitions based on validation mode
"""

from specify_cli.workflow.adr_validator import (
    ADRValidationResult,
    ADRValidator,
    validate_adr_for_transition,
)
from specify_cli.workflow.config import WorkflowConfig
from specify_cli.workflow.exceptions import (
    WorkflowConfigError,
    WorkflowConfigNotFoundError,
    WorkflowConfigValidationError,
    WorkflowNotFoundError,
    WorkflowStateError,
)
from specify_cli.workflow.prd_validator import (
    PRDValidationResult,
    PRDValidator,
    validate_prd_for_transition,
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
from specify_cli.workflow.validation_engine import (
    TransitionValidationResult,
    TransitionValidator,
)
from specify_cli.workflow.state_guard import (
    StateCheckResponse,
    StateCheckResult,
    TaskSystem,
    WorkflowStateGuard,
    check_workflow_state,
    get_next_state,
    get_valid_workflows,
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
    # PRD Validation
    "PRDValidator",
    "PRDValidationResult",
    "validate_prd_for_transition",
    # ADR Validation
    "ADRValidator",
    "ADRValidationResult",
    "validate_adr_for_transition",
    # Transition Validation Engine
    "TransitionValidator",
    "TransitionValidationResult",
    # Workflow Validation
    "ValidationSeverity",
    "ValidationIssue",
    "ValidationResult",
    "WorkflowValidator",
    "validate_workflow",
    # State Guard
    "StateCheckResult",
    "StateCheckResponse",
    "TaskSystem",
    "WorkflowStateGuard",
    "check_workflow_state",
    "get_next_state",
    "get_valid_workflows",
]
