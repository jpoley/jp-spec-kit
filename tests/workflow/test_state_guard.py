"""Comprehensive tests for workflow state guard.

Tests cover all 8 acceptance criteria for task-096:
- AC #1: WorkflowConfig loading
- AC #2: State validation before execution
- AC #3: Clear error messages
- AC #4: State update after execution
- AC #5: Workflow suggestions for current state
- AC #6: Support for multiple task systems
- AC #7: No breaking changes (backward compatibility)
- AC #8: All 6 commands implement checks
"""

import tempfile
from pathlib import Path
from typing import Optional

import pytest
import yaml

from specify_cli.workflow.state_guard import (
    StateCheckResult,
    TaskSystem,
    WorkflowStateGuard,
    check_workflow_state,
    get_next_state,
    get_valid_workflows,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def sample_config():
    """Sample workflow configuration matching jpspec_workflow.yml structure."""
    return {
        "version": "1.0",
        "states": [
            "To Do",
            "Assessed",
            "Specified",
            "Researched",
            "Planned",
            "In Implementation",
            "Validated",
            "Deployed",
            "Done",
        ],
        "workflows": {
            "assess": {
                "input_states": ["To Do"],
                "output_state": "Assessed",
                "command": "/jpspec:assess",
            },
            "specify": {
                "input_states": ["Assessed"],
                "output_state": "Specified",
                "command": "/jpspec:specify",
            },
            "research": {
                "input_states": ["Specified"],
                "output_state": "Researched",
                "command": "/jpspec:research",
            },
            "plan": {
                "input_states": ["Specified", "Researched"],
                "output_state": "Planned",
                "command": "/jpspec:plan",
            },
            "implement": {
                "input_states": ["Planned"],
                "output_state": "In Implementation",
                "command": "/jpspec:implement",
            },
            "validate": {
                "input_states": ["In Implementation"],
                "output_state": "Validated",
                "command": "/jpspec:validate",
            },
            "operate": {
                "input_states": ["Validated"],
                "output_state": "Deployed",
                "command": "/jpspec:operate",
            },
        },
    }


@pytest.fixture
def config_file(sample_config):
    """Create temporary config file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(sample_config, f)
        return Path(f.name)


@pytest.fixture
def config_dir(sample_config):
    """Create temp directory with config file for default path testing."""
    import tempfile as tf

    tmpdir = Path(tf.mkdtemp())
    config_path = tmpdir / "jpspec_workflow.yml"
    with open(config_path, "w") as f:
        yaml.dump(sample_config, f)
    return tmpdir


class MockTaskSystem:
    """Mock task system for testing AC #6."""

    def __init__(self):
        self.tasks: dict[str, str] = {}
        self.calls: list[tuple[str, str, str]] = []

    def get_task_state(self, task_id: str) -> Optional[str]:
        return self.tasks.get(task_id)

    def set_task_state(self, task_id: str, new_state: str) -> bool:
        self.calls.append(("set_state", task_id, new_state))
        self.tasks[task_id] = new_state
        return True


# =============================================================================
# AC #1: WorkflowConfig Loading Tests
# =============================================================================


class TestConfigLoading:
    """Tests for AC #1: All /jpspec command implementations load WorkflowConfig."""

    def test_load_config_from_explicit_path(self, config_file):
        """Guard loads config from explicit path."""
        guard = WorkflowStateGuard(config_file)
        assert guard.has_config
        assert "workflows" in guard.config

    def test_load_config_from_default_path(self, config_dir, monkeypatch):
        """Guard finds config in default locations."""
        monkeypatch.chdir(config_dir)
        guard = WorkflowStateGuard()
        assert guard.has_config

    def test_handles_missing_config_gracefully(self):
        """Guard handles missing config without error."""
        guard = WorkflowStateGuard(Path("/nonexistent/config.yml"))
        assert not guard.has_config
        assert guard.config == {}

    def test_handles_empty_config_file(self):
        """Guard handles empty config file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("")
        guard = WorkflowStateGuard(Path(f.name))
        assert not guard.has_config

    def test_handles_invalid_yaml(self):
        """Guard handles invalid YAML gracefully."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("invalid: yaml: [\n")
        guard = WorkflowStateGuard(Path(f.name))
        assert guard.config == {}

    def test_searches_multiple_default_paths(self, sample_config):
        """Guard searches multiple default paths."""
        # Check the DEFAULT_CONFIG_PATHS are defined
        assert len(WorkflowStateGuard.DEFAULT_CONFIG_PATHS) >= 1
        assert Path("jpspec_workflow.yml") in WorkflowStateGuard.DEFAULT_CONFIG_PATHS


# =============================================================================
# AC #2: State Validation Before Execution Tests
# =============================================================================


class TestStateValidation:
    """Tests for AC #2: Each command validates task is in allowed input_state."""

    def test_allows_valid_state(self, config_file):
        """Guard allows execution when state is valid."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "Planned")
        assert response.result == StateCheckResult.ALLOWED

    def test_blocks_invalid_state(self, config_file):
        """Guard blocks execution when state is invalid."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "To Do")
        assert response.result == StateCheckResult.BLOCKED

    def test_case_insensitive_state_check(self, config_file):
        """State checks are case-insensitive."""
        guard = WorkflowStateGuard(config_file)

        result1 = guard.check_state("implement", "planned")
        result2 = guard.check_state("implement", "PLANNED")
        result3 = guard.check_state("implement", "Planned")

        assert result1.result == StateCheckResult.ALLOWED
        assert result2.result == StateCheckResult.ALLOWED
        assert result3.result == StateCheckResult.ALLOWED

    def test_handles_whitespace_in_state(self, config_file):
        """Guard handles whitespace in state strings."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "  Planned  ")
        assert response.result == StateCheckResult.ALLOWED

    def test_skip_check_flag_bypasses_validation(self, config_file):
        """--skip-state-check bypasses validation."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "Wrong State", skip_check=True)
        assert response.result == StateCheckResult.SKIPPED

    def test_multiple_input_states_allowed(self, config_file):
        """Workflows with multiple input states accept any of them."""
        guard = WorkflowStateGuard(config_file)

        # plan accepts both Specified and Researched
        result1 = guard.check_state("plan", "Specified")
        result2 = guard.check_state("plan", "Researched")

        assert result1.result == StateCheckResult.ALLOWED
        assert result2.result == StateCheckResult.ALLOWED

    def test_no_config_allows_execution(self):
        """Missing config allows execution with NO_CONFIG result."""
        guard = WorkflowStateGuard(Path("/nonexistent.yml"))
        response = guard.check_state("implement", "Any State")
        assert response.result == StateCheckResult.NO_CONFIG

    def test_unknown_workflow_returns_no_config(self, config_file):
        """Unknown workflow name returns NO_CONFIG."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("nonexistent_workflow", "Any State")
        assert response.result == StateCheckResult.NO_CONFIG


# =============================================================================
# AC #3: Clear Error Messages Tests
# =============================================================================


class TestErrorMessages:
    """Tests for AC #3: Commands provide clear error messages."""

    def test_blocked_message_includes_command_name(self, config_file):
        """Error message includes the command that was blocked."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "To Do")
        assert "/jpspec:implement" in response.message

    def test_blocked_message_shows_current_state(self, config_file):
        """Error message shows the current task state."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "To Do")
        assert "To Do" in response.message

    def test_blocked_message_shows_required_states(self, config_file):
        """Error message shows required states."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "To Do")
        assert "Planned" in response.message

    def test_blocked_message_suggests_bypass_option(self, config_file):
        """Error message suggests --skip-state-check option."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "To Do")
        assert "--skip-state-check" in response.message

    def test_response_includes_structured_data(self, config_file):
        """Response includes structured data for programmatic use."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "To Do")

        assert response.current_state == "To Do"
        assert "Planned" in response.required_states
        assert response.suggested_workflows is not None


# =============================================================================
# AC #4: State Update After Execution Tests
# =============================================================================


class TestStateUpdate:
    """Tests for AC #4: Commands update task state after successful execution."""

    def test_gets_output_state_for_workflow(self, config_file):
        """Guard provides output state for workflow."""
        guard = WorkflowStateGuard(config_file)
        assert guard.get_output_state("implement") == "In Implementation"
        assert guard.get_output_state("validate") == "Validated"

    def test_response_includes_next_state(self, config_file):
        """Successful check includes next state in response."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "Planned")
        assert response.next_state == "In Implementation"

    def test_update_task_state_with_task_system(self, config_file):
        """Guard can update task state through task system."""
        mock_system = MockTaskSystem()
        guard = WorkflowStateGuard(config_file, task_system=mock_system)

        success, msg = guard.update_task_state("task-123", "implement")

        assert success
        assert mock_system.tasks["task-123"] == "In Implementation"
        assert ("set_state", "task-123", "In Implementation") in mock_system.calls

    def test_update_fails_without_task_system(self, config_file):
        """State update fails gracefully without task system."""
        guard = WorkflowStateGuard(config_file)
        success, msg = guard.update_task_state("task-123", "implement")

        assert not success
        assert "No task system" in msg


# =============================================================================
# AC #5: Workflow Suggestions Tests
# =============================================================================


class TestWorkflowSuggestions:
    """Tests for AC #5: Error messages suggest valid workflows."""

    def test_suggests_valid_workflows_for_state(self, config_file):
        """Guard suggests valid workflows for current state."""
        guard = WorkflowStateGuard(config_file)
        workflows = guard.get_valid_workflows_for_state("Specified")

        assert "/jpspec:research" in workflows
        assert "/jpspec:plan" in workflows

    def test_blocked_response_includes_suggestions(self, config_file):
        """Blocked response includes workflow suggestions."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "Specified")

        assert response.suggested_workflows is not None
        assert len(response.suggested_workflows) > 0
        # For Specified state, research and plan are valid
        assert "/jpspec:research" in response.suggested_workflows

    def test_message_includes_suggestions(self, config_file):
        """Error message includes suggestions text."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "Specified")

        assert "Suggestions" in response.message
        assert "Valid workflows" in response.message

    def test_no_suggestions_when_no_valid_workflows(self, config_file):
        """Handles case when no workflows are valid."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "Done")

        # Done state has no valid next workflows in sample config
        assert "No workflows available" in response.message


# =============================================================================
# AC #6: Multiple Task Systems Support Tests
# =============================================================================


class TestTaskSystemIntegration:
    """Tests for AC #6: Works with backlog.md and future task systems."""

    def test_task_system_protocol_compliance(self):
        """TaskSystem protocol defines required methods."""
        # Verify protocol has required methods
        assert hasattr(TaskSystem, "get_task_state")
        assert hasattr(TaskSystem, "set_task_state")

    def test_works_with_mock_task_system(self, config_file):
        """Guard integrates with custom task system."""
        mock_system = MockTaskSystem()
        mock_system.tasks["task-001"] = "Planned"

        guard = WorkflowStateGuard(config_file, task_system=mock_system)

        # Verify guard has the task system configured
        assert guard.task_system is mock_system
        # Verify can get state through the mock
        state = mock_system.get_task_state("task-001")
        assert state == "Planned"

    def test_guard_operates_without_task_system(self, config_file):
        """Guard operates correctly without task system configured."""
        guard = WorkflowStateGuard(config_file)
        assert guard.task_system is None

        # Should still perform state checks
        response = guard.check_state("implement", "Planned")
        assert response.result == StateCheckResult.ALLOWED

    def test_guard_accepts_custom_task_system(self, config_file):
        """Guard accepts custom task system at init."""
        mock_system = MockTaskSystem()
        guard = WorkflowStateGuard(config_file, task_system=mock_system)
        assert guard.task_system is mock_system


# =============================================================================
# AC #7: Backward Compatibility Tests
# =============================================================================


class TestBackwardCompatibility:
    """Tests for AC #7: No breaking changes to existing interfaces."""

    def test_cli_helper_returns_tuple(self, config_file):
        """CLI helper maintains (bool, str) return signature."""
        can_proceed, msg = check_workflow_state(
            "implement", "Planned", config_path=str(config_file)
        )
        assert isinstance(can_proceed, bool)
        assert isinstance(msg, str)

    def test_cli_helper_true_for_allowed(self, config_file):
        """CLI helper returns True for allowed state."""
        can_proceed, _ = check_workflow_state(
            "implement", "Planned", config_path=str(config_file)
        )
        assert can_proceed is True

    def test_cli_helper_false_for_blocked(self, config_file):
        """CLI helper returns False for blocked state."""
        can_proceed, _ = check_workflow_state(
            "implement", "To Do", config_path=str(config_file)
        )
        assert can_proceed is False

    def test_cli_helper_true_for_no_config(self):
        """CLI helper returns True when no config (permissive default)."""
        can_proceed, _ = check_workflow_state(
            "implement", "Any State", config_path="/nonexistent.yml"
        )
        assert can_proceed is True

    def test_cli_helper_true_for_skip(self, config_file):
        """CLI helper returns True when skip flag is set."""
        can_proceed, _ = check_workflow_state(
            "implement", "Wrong State", skip=True, config_path=str(config_file)
        )
        assert can_proceed is True

    def test_get_next_state_helper(self, config_file):
        """get_next_state helper works correctly."""
        next_state = get_next_state("implement", config_path=str(config_file))
        assert next_state == "In Implementation"

    def test_get_next_state_returns_none_for_missing(self):
        """get_next_state returns None for missing config."""
        next_state = get_next_state("implement", config_path="/nonexistent.yml")
        assert next_state is None

    def test_get_valid_workflows_helper(self, config_file):
        """get_valid_workflows helper works correctly."""
        workflows = get_valid_workflows("Specified", config_path=str(config_file))
        assert "/jpspec:research" in workflows
        assert "/jpspec:plan" in workflows


# =============================================================================
# AC #8: All Commands Implement Checks Tests
# =============================================================================


class TestAllCommandsCovered:
    """Tests for AC #8: All 6 commands implement checks."""

    JPSPEC_COMMANDS = [
        "assess",
        "specify",
        "research",
        "plan",
        "implement",
        "validate",
        "operate",
    ]

    def test_all_commands_defined_in_config(self, sample_config):
        """All jpspec commands are defined in workflow config."""
        workflows = sample_config["workflows"]
        for cmd in self.JPSPEC_COMMANDS:
            assert cmd in workflows, f"Command '{cmd}' not in workflow config"

    def test_all_commands_have_input_states(self, config_file):
        """All commands have input_states defined."""
        guard = WorkflowStateGuard(config_file)
        for cmd in self.JPSPEC_COMMANDS:
            states = guard.get_input_states(cmd)
            assert len(states) > 0, f"Command '{cmd}' has no input_states"

    def test_all_commands_have_output_state(self, config_file):
        """All commands have output_state defined."""
        guard = WorkflowStateGuard(config_file)
        for cmd in self.JPSPEC_COMMANDS:
            state = guard.get_output_state(cmd)
            assert state is not None, f"Command '{cmd}' has no output_state"

    def test_all_commands_can_be_validated(self, config_file):
        """All commands can be validated through state guard."""
        guard = WorkflowStateGuard(config_file)
        for cmd in self.JPSPEC_COMMANDS:
            input_states = guard.get_input_states(cmd)
            valid_state = input_states[0] if input_states else "Unknown"

            response = guard.check_state(cmd, valid_state)
            assert response.result in (
                StateCheckResult.ALLOWED,
                StateCheckResult.NO_CONFIG,
            ), f"Command '{cmd}' validation failed"


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_state_string(self, config_file):
        """Handles empty state string."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "")
        assert response.result == StateCheckResult.BLOCKED

    def test_none_state_handling(self, config_file):
        """Handles None-like state values gracefully."""
        guard = WorkflowStateGuard(config_file)
        # Empty string is valid input, should be blocked
        response = guard.check_state("implement", "   ")
        assert response.result == StateCheckResult.BLOCKED

    def test_special_characters_in_state(self, config_file):
        """Handles special characters in state names."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "State<with>special&chars")
        assert response.result == StateCheckResult.BLOCKED

    def test_very_long_state_name(self, config_file):
        """Handles very long state names."""
        guard = WorkflowStateGuard(config_file)
        long_state = "A" * 1000
        response = guard.check_state("implement", long_state)
        assert response.result == StateCheckResult.BLOCKED

    def test_unicode_state_names(self, config_file):
        """Handles unicode characters in state names."""
        guard = WorkflowStateGuard(config_file)
        response = guard.check_state("implement", "Estado en Progreso")
        assert response.result == StateCheckResult.BLOCKED


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for state guard with real workflow scenarios."""

    def test_complete_workflow_progression(self, config_file):
        """Test state guard through complete workflow progression."""
        mock_system = MockTaskSystem()
        mock_system.tasks["task-001"] = "To Do"
        guard = WorkflowStateGuard(config_file, task_system=mock_system)

        # Start with assess
        response = guard.check_state("assess", mock_system.tasks["task-001"])
        assert response.result == StateCheckResult.ALLOWED
        mock_system.tasks["task-001"] = response.next_state

        # Proceed to specify
        response = guard.check_state("specify", mock_system.tasks["task-001"])
        assert response.result == StateCheckResult.ALLOWED
        assert mock_system.tasks["task-001"] == "Assessed"

    def test_workflow_branching_with_optional_research(self, config_file):
        """Test branching workflow (plan accepts Specified or Researched)."""
        guard = WorkflowStateGuard(config_file)

        # Direct path: Specified -> plan
        response = guard.check_state("plan", "Specified")
        assert response.result == StateCheckResult.ALLOWED

        # Research path: Specified -> research -> plan
        response = guard.check_state("research", "Specified")
        assert response.result == StateCheckResult.ALLOWED
        response = guard.check_state("plan", "Researched")
        assert response.result == StateCheckResult.ALLOWED
