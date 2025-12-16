"""Workflow configuration exceptions.

This module defines a hierarchy of exceptions for workflow configuration
errors, providing clear and actionable error messages for users.
"""

from typing import Any


class WorkflowConfigError(Exception):
    """Base exception for workflow configuration errors.

    All workflow-related exceptions inherit from this class, allowing
    callers to catch all workflow errors with a single except clause.

    Attributes:
        message: Human-readable error description.
        details: Additional context for debugging.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """Initialize a WorkflowConfigError.

        Args:
            message: Human-readable error description.
            details: Additional context for debugging.
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation with details if available."""
        if self.details:
            detail_str = ", ".join(f"{k}={v!r}" for k, v in self.details.items())
            return f"{self.message} ({detail_str})"
        return self.message


class WorkflowConfigNotFoundError(WorkflowConfigError):
    """Raised when workflow config file is not found.

    This error occurs when attempting to load a workflow configuration
    file that does not exist at the specified path.

    Example:
        >>> raise WorkflowConfigNotFoundError("/path/to/config.yml")
        WorkflowConfigNotFoundError: Workflow config not found: /path/to/config.yml
    """

    def __init__(self, path: str, searched_paths: list[str] | None = None):
        """Initialize with the missing config path.

        Args:
            path: The path that was attempted.
            searched_paths: List of all paths that were searched.
        """
        details = {"path": path}
        if searched_paths:
            details["searched_paths"] = searched_paths

        message = f"Workflow config not found: {path}"
        if searched_paths:
            message += f"\nSearched paths: {', '.join(searched_paths)}"

        super().__init__(message, details)
        self.path = path
        self.searched_paths = searched_paths or []


class WorkflowConfigValidationError(WorkflowConfigError):
    """Raised when workflow config fails schema validation.

    This error occurs when the configuration file exists but contains
    invalid structure, types, or values according to the JSON schema.

    Attributes:
        errors: List of specific validation error messages.

    Example:
        >>> raise WorkflowConfigValidationError(
        ...     "Config validation failed",
        ...     errors=["'version' is a required property"]
        ... )
    """

    def __init__(self, message: str, errors: list[str] | None = None):
        """Initialize with validation error details.

        Args:
            message: Summary of the validation failure.
            errors: List of specific validation errors.
        """
        self.errors = errors or []

        details = {}
        if errors:
            details["error_count"] = len(errors)
            details["first_error"] = errors[0] if errors else None

        super().__init__(message, details)

    def __str__(self) -> str:
        """Return string representation with all validation errors."""
        if self.errors:
            error_list = "\n  - ".join(self.errors)
            return f"{self.message}:\n  - {error_list}"
        return self.message


class WorkflowStateError(WorkflowConfigError):
    """Raised when an invalid state is referenced.

    This error occurs when trying to use a state name that is not
    defined in the workflow configuration.

    Example:
        >>> raise WorkflowStateError("InvalidState", ["To Do", "Specified"])
        WorkflowStateError: Invalid state: 'InvalidState'
    """

    def __init__(self, state: str, valid_states: list[str] | None = None):
        """Initialize with the invalid state and valid alternatives.

        Args:
            state: The invalid state name that was referenced.
            valid_states: List of valid state names for guidance.
        """
        details = {"state": state}
        if valid_states:
            details["valid_states"] = valid_states

        message = f"Invalid state: '{state}'"
        if valid_states:
            message += f"\nValid states: {', '.join(valid_states)}"

        super().__init__(message, details)
        self.state = state
        self.valid_states = valid_states or []


class WorkflowNotFoundError(WorkflowConfigError):
    """Raised when a workflow is not found.

    This error occurs when trying to access a workflow phase that is
    not defined in the configuration.

    Example:
        >>> raise WorkflowNotFoundError("nonexistent", ["specify", "plan"])
        WorkflowNotFoundError: Workflow not found: 'nonexistent'
    """

    def __init__(self, workflow: str, valid_workflows: list[str] | None = None):
        """Initialize with the missing workflow and valid alternatives.

        Args:
            workflow: The workflow name that was not found.
            valid_workflows: List of valid workflow names for guidance.
        """
        details = {"workflow": workflow}
        if valid_workflows:
            details["valid_workflows"] = valid_workflows

        message = f"Workflow not found: '{workflow}'"
        if valid_workflows:
            message += f"\nValid workflows: {', '.join(valid_workflows)}"

        super().__init__(message, details)
        self.workflow = workflow
        self.valid_workflows = valid_workflows or []
