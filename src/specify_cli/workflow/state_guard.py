"""Workflow state guard for /jpspec command validation.

Validates that tasks are in allowed states before command execution
and updates state after successful completion.

This module is designed to work with both backlog.md CLI and future
task management systems through a pluggable interface.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Protocol

import yaml


class StateCheckResult(Enum):
    """Result of state validation check."""

    ALLOWED = "allowed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    NO_CONFIG = "no_config"
    NO_TASK = "no_task"


@dataclass
class StateCheckResponse:
    """Response from state validation check."""

    result: StateCheckResult
    message: str
    current_state: Optional[str] = None
    required_states: Optional[list[str]] = None
    suggested_workflows: Optional[list[str]] = None
    next_state: Optional[str] = None


class TaskSystem(Protocol):
    """Protocol for task management system integration."""

    def get_task_state(self, task_id: str) -> Optional[str]:
        """Get the current state of a task."""
        ...

    def set_task_state(self, task_id: str, new_state: str) -> bool:
        """Update the state of a task. Returns True on success."""
        ...


class WorkflowStateGuard:
    """Guards /jpspec commands by validating workflow state transitions.

    This guard enforces workflow constraints to ensure commands are only
    executed when tasks are in appropriate states. It provides:
    - State validation before command execution
    - Helpful error messages with suggestions
    - Integration with configurable task systems
    """

    DEFAULT_CONFIG_PATHS = [
        Path("jpspec_workflow.yml"),
        Path("memory/jpspec_workflow.yml"),
        Path(".jpspec/workflow.yml"),
    ]

    def __init__(
        self,
        config_path: Optional[Path] = None,
        task_system: Optional[TaskSystem] = None,
    ):
        """Initialize the state guard.

        Args:
            config_path: Path to workflow config. If None, searches default locations.
            task_system: Task management system for state updates. Optional.
        """
        self.config_path = config_path or self._find_config()
        self.config = self._load_config()
        self.task_system = task_system

    def _find_config(self) -> Optional[Path]:
        """Find workflow config in default locations."""
        for path in self.DEFAULT_CONFIG_PATHS:
            if path.exists():
                return path
        return None

    def _load_config(self) -> dict:
        """Load workflow configuration from YAML file."""
        if self.config_path is None or not self.config_path.exists():
            return {}
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f) or {}
        except (yaml.YAMLError, OSError):
            return {}

    @property
    def has_config(self) -> bool:
        """Check if a valid configuration is loaded."""
        return bool(self.config and self.config.get("workflows"))

    def get_workflow_config(self, workflow_name: str) -> dict:
        """Get configuration for a specific workflow."""
        workflows = self.config.get("workflows", {})
        return workflows.get(workflow_name, {})

    def get_input_states(self, workflow_name: str) -> list[str]:
        """Get allowed input states for a workflow."""
        wf = self.get_workflow_config(workflow_name)
        return wf.get("input_states", [])

    def get_output_state(self, workflow_name: str) -> Optional[str]:
        """Get output state after successful workflow execution."""
        wf = self.get_workflow_config(workflow_name)
        return wf.get("output_state")

    def get_all_states(self) -> list[str]:
        """Get all defined states from configuration."""
        return self.config.get("states", [])

    def normalize_state(self, state: str) -> str:
        """Normalize state string for comparison."""
        return state.lower().strip()

    def check_state(
        self,
        workflow_name: str,
        current_state: str,
        skip_check: bool = False,
    ) -> StateCheckResponse:
        """Check if current state allows workflow execution.

        Args:
            workflow_name: Name of the workflow (e.g., 'specify', 'plan')
            current_state: Current task state
            skip_check: If True, skip validation (power user override)

        Returns:
            StateCheckResponse with result details
        """
        if skip_check:
            return StateCheckResponse(
                result=StateCheckResult.SKIPPED,
                message="State check skipped (--skip-state-check)",
                current_state=current_state,
            )

        if not self.has_config:
            return StateCheckResponse(
                result=StateCheckResult.NO_CONFIG,
                message="No workflow config found - proceeding without state validation",
                current_state=current_state,
            )

        input_states = self.get_input_states(workflow_name)
        if not input_states:
            return StateCheckResponse(
                result=StateCheckResult.NO_CONFIG,
                message=f"No input states defined for '{workflow_name}' - proceeding",
                current_state=current_state,
            )

        # Normalize state comparison (case-insensitive, trimmed)
        current_normalized = self.normalize_state(current_state)
        allowed_normalized = [self.normalize_state(s) for s in input_states]

        if current_normalized in allowed_normalized:
            next_state = self.get_output_state(workflow_name)
            return StateCheckResponse(
                result=StateCheckResult.ALLOWED,
                message=f"State '{current_state}' is valid for /jpspec:{workflow_name}",
                current_state=current_state,
                required_states=input_states,
                next_state=next_state,
            )

        # Build helpful error message with suggestions
        valid_workflows = self.get_valid_workflows_for_state(current_state)

        return StateCheckResponse(
            result=StateCheckResult.BLOCKED,
            message=self._build_blocked_message(
                workflow_name, current_state, input_states, valid_workflows
            ),
            current_state=current_state,
            required_states=input_states,
            suggested_workflows=valid_workflows,
        )

    def _build_blocked_message(
        self,
        workflow_name: str,
        current_state: str,
        required_states: list[str],
        valid_workflows: list[str],
    ) -> str:
        """Build a helpful error message when state check fails."""
        lines = [
            f"Cannot run /jpspec:{workflow_name}",
            "",
            f'  Current state: "{current_state}"',
            f"  Required states: {', '.join(required_states)}",
            "",
        ]

        if valid_workflows:
            lines.extend(
                [
                    "Suggestions:",
                    f"  - Valid workflows for '{current_state}': {', '.join(valid_workflows)}",
                ]
            )
        else:
            lines.extend(
                [
                    "Suggestions:",
                    f"  - No workflows available for state '{current_state}'",
                ]
            )

        lines.extend(
            [
                "  - Check if the task needs a status update first",
                "  - Use --skip-state-check to bypass (not recommended)",
            ]
        )

        return "\n".join(lines)

    def get_valid_workflows_for_state(self, current_state: str) -> list[str]:
        """Get all workflows that can run from the current state."""
        valid = []
        current_normalized = self.normalize_state(current_state)
        for wf_name, wf_config in self.config.get("workflows", {}).items():
            input_states = wf_config.get("input_states", [])
            if current_normalized in [self.normalize_state(s) for s in input_states]:
                valid.append(f"/jpspec:{wf_name}")
        return sorted(valid)

    def update_task_state(self, task_id: str, workflow_name: str) -> tuple[bool, str]:
        """Update task state after successful workflow execution.

        Args:
            task_id: ID of the task to update
            workflow_name: Name of completed workflow

        Returns:
            Tuple of (success, message)
        """
        next_state = self.get_output_state(workflow_name)
        if not next_state:
            return False, f"No output state defined for '{workflow_name}'"

        if not self.task_system:
            return False, "No task system configured for state updates"

        success = self.task_system.set_task_state(task_id, next_state)
        if success:
            return True, f"Task {task_id} state updated to '{next_state}'"
        return False, f"Failed to update task {task_id} state"


# Convenience functions for CLI usage


def check_workflow_state(
    workflow: str,
    current_state: str,
    skip: bool = False,
    config_path: Optional[str] = None,
) -> tuple[bool, str]:
    """CLI helper to check workflow state.

    Args:
        workflow: Workflow name (e.g., 'specify', 'plan')
        current_state: Current task state
        skip: Skip state validation
        config_path: Optional path to config file

    Returns:
        Tuple of (can_proceed, message)
    """
    path = Path(config_path) if config_path else None
    guard = WorkflowStateGuard(path)
    response = guard.check_state(workflow, current_state, skip)
    can_proceed = response.result in (
        StateCheckResult.ALLOWED,
        StateCheckResult.SKIPPED,
        StateCheckResult.NO_CONFIG,
    )
    return can_proceed, response.message


def get_next_state(
    workflow: str,
    config_path: Optional[str] = None,
) -> Optional[str]:
    """Get the output state for a workflow.

    Args:
        workflow: Workflow name
        config_path: Optional path to config file

    Returns:
        The output state or None
    """
    path = Path(config_path) if config_path else None
    guard = WorkflowStateGuard(path)
    return guard.get_output_state(workflow)


def get_valid_workflows(
    current_state: str,
    config_path: Optional[str] = None,
) -> list[str]:
    """Get valid workflows for a given state.

    Args:
        current_state: Current task state
        config_path: Optional path to config file

    Returns:
        List of valid workflow command names
    """
    path = Path(config_path) if config_path else None
    guard = WorkflowStateGuard(path)
    return guard.get_valid_workflows_for_state(current_state)
