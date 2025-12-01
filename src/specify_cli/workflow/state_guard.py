"""Workflow state guard for /jpspec command validation.

Validates that tasks are in allowed states before command execution
and updates state after successful completion.
"""

from enum import Enum
from pathlib import Path
from typing import Optional

import yaml


class StateCheckResult(Enum):
    """Result of state validation check."""

    ALLOWED = "allowed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    NO_CONFIG = "no_config"


class WorkflowStateGuard:
    """Guards /jpspec commands by validating workflow state transitions."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize with optional config path."""
        self.config_path = config_path or Path("jpspec_workflow.yml")
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load workflow configuration from YAML file."""
        if not self.config_path.exists():
            return {}
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f) or {}
        except (yaml.YAMLError, OSError):
            return {}

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

    def check_state(
        self, workflow_name: str, current_state: str, skip_check: bool = False
    ) -> tuple[StateCheckResult, str]:
        """Check if current state allows workflow execution.

        Args:
            workflow_name: Name of the workflow (e.g., 'specify', 'plan')
            current_state: Current task state
            skip_check: If True, skip validation (power user override)

        Returns:
            Tuple of (result, message)
        """
        if skip_check:
            return StateCheckResult.SKIPPED, "State check skipped (--skip-state-check)"

        if not self.config:
            return StateCheckResult.NO_CONFIG, "No workflow config found, proceeding"

        input_states = self.get_input_states(workflow_name)
        if not input_states:
            return (
                StateCheckResult.NO_CONFIG,
                f"No input states defined for '{workflow_name}'",
            )

        # Normalize state comparison (case-insensitive)
        current_normalized = current_state.lower().strip()
        allowed_normalized = [s.lower().strip() for s in input_states]

        if current_normalized in allowed_normalized:
            return (
                StateCheckResult.ALLOWED,
                f"State '{current_state}' is valid for {workflow_name}",
            )

        # Build helpful error message
        valid_workflows = self.get_valid_workflows_for_state(current_state)
        suggestions = (
            f"Valid workflows for '{current_state}': {', '.join(valid_workflows)}"
            if valid_workflows
            else f"No workflows available for state '{current_state}'"
        )

        msg = (
            f"Cannot run /jpspec:{workflow_name}\n\n"
            f'Current state: "{current_state}"\n'
            f"Required states: {input_states}\n\n"
            f"Suggestions:\n"
            f"  - {suggestions}\n"
            f"  - Use --skip-state-check to bypass (not recommended)"
        )
        return StateCheckResult.BLOCKED, msg

    def get_valid_workflows_for_state(self, current_state: str) -> list[str]:
        """Get all workflows that can run from the current state."""
        valid = []
        current_normalized = current_state.lower().strip()
        for wf_name, wf_config in self.config.get("workflows", {}).items():
            input_states = wf_config.get("input_states", [])
            if current_normalized in [s.lower().strip() for s in input_states]:
                valid.append(f"/jpspec:{wf_name}")
        return valid


def check_workflow_state(
    workflow: str,
    current_state: str,
    skip: bool = False,
    config_path: Optional[str] = None,
) -> tuple[bool, str]:
    """CLI helper to check workflow state.

    Returns:
        Tuple of (can_proceed, message)
    """
    path = Path(config_path) if config_path else None
    guard = WorkflowStateGuard(path)
    result, msg = guard.check_state(workflow, current_state, skip)
    can_proceed = result in (
        StateCheckResult.ALLOWED,
        StateCheckResult.SKIPPED,
        StateCheckResult.NO_CONFIG,
    )
    return can_proceed, msg


def get_next_state(workflow: str, config_path: Optional[str] = None) -> Optional[str]:
    """Get the output state for a workflow."""
    path = Path(config_path) if config_path else None
    guard = WorkflowStateGuard(path)
    return guard.get_output_state(workflow)
