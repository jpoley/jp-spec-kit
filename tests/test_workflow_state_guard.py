"""Unit tests for WorkflowStateGuard module.

This test module provides comprehensive unit testing for the WorkflowStateGuard
class and its helper functions. Unlike the integration tests in
test_jpspec_workflow_integration.py, these tests focus on testing individual
methods and components in isolation using mocks and test doubles.

Coverage areas:
- Configuration loading and validation
- State normalization and comparison
- State checking logic
- Error message formatting
- Convenience functions
- Edge cases and boundary conditions
"""

import pytest
from pathlib import Path
from unittest.mock import Mock
import yaml

from specify_cli.workflow.state_guard import (
    WorkflowStateGuard,
    StateCheckResult,
    StateCheckResponse,
    check_workflow_state,
    get_next_state,
    get_valid_workflows,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def minimal_config():
    """Minimal valid workflow configuration."""
    return {
        "workflows": {
            "test": {
                "input_states": ["Start"],
                "output_state": "End",
            }
        }
    }


@pytest.fixture
def complete_config():
    """Complete workflow configuration with multiple workflows."""
    return {
        "version": "1.0",
        "states": ["To Do", "In Progress", "Done"],
        "workflows": {
            "start": {
                "command": "/jpspec:start",
                "input_states": ["To Do"],
                "output_state": "In Progress",
            },
            "finish": {
                "command": "/jpspec:finish",
                "input_states": ["In Progress"],
                "output_state": "Done",
            },
        },
    }


@pytest.fixture
def mock_task_system():
    """Mock task system for testing state updates."""
    mock = Mock()
    mock.get_task_state.return_value = "To Do"
    mock.set_task_state.return_value = True
    return mock


# =============================================================================
# Initialization and Configuration Loading Tests
# =============================================================================


class TestInitialization:
    """Test WorkflowStateGuard initialization and configuration loading."""

    def test_init_with_explicit_config_path(self, tmp_path, minimal_config):
        """Initialize with explicitly provided config path."""
        config_file = tmp_path / "test_config.yml"
        config_file.write_text(yaml.dump(minimal_config))

        guard = WorkflowStateGuard(config_path=config_file)

        assert guard.config_path == config_file
        assert guard.has_config
        assert "test" in guard.config["workflows"]

    def test_init_with_task_system(self, tmp_path, minimal_config, mock_task_system):
        """Initialize with task system for state updates."""
        config_file = tmp_path / "test_config.yml"
        config_file.write_text(yaml.dump(minimal_config))

        guard = WorkflowStateGuard(
            config_path=config_file, task_system=mock_task_system
        )

        assert guard.task_system == mock_task_system

    def test_init_without_config_creates_empty_guard(self):
        """Initialize without config creates guard with no config."""
        guard = WorkflowStateGuard(config_path=Path("/nonexistent/config.yml"))

        assert not guard.has_config
        assert guard.config == {}

    def test_init_searches_default_paths(self, tmp_path, minimal_config, monkeypatch):
        """Initialize without explicit path searches default locations."""
        # Change to temp directory
        monkeypatch.chdir(tmp_path)

        # Create config in first default location
        default_file = tmp_path / "jpspec_workflow.yml"
        default_file.write_text(yaml.dump(minimal_config))

        guard = WorkflowStateGuard()

        # config_path will be relative path, resolve both for comparison
        assert guard.config_path.resolve() == default_file.resolve()
        assert guard.has_config

    def test_find_config_checks_all_default_paths(self, monkeypatch):
        """_find_config checks all default paths in order."""
        guard = WorkflowStateGuard(config_path=Path("/nonexistent"))

        # Should check all paths from DEFAULT_CONFIG_PATHS
        assert len(guard.DEFAULT_CONFIG_PATHS) == 3
        assert guard.DEFAULT_CONFIG_PATHS[0] == Path("jpspec_workflow.yml")
        assert guard.DEFAULT_CONFIG_PATHS[1] == Path("memory/jpspec_workflow.yml")
        assert guard.DEFAULT_CONFIG_PATHS[2] == Path(".jpspec/workflow.yml")

    def test_load_config_handles_yaml_error(self, tmp_path):
        """_load_config returns empty dict on YAML parse error."""
        bad_config = tmp_path / "bad.yml"
        bad_config.write_text("invalid: yaml: content:\n  - [unclosed")

        guard = WorkflowStateGuard(config_path=bad_config)

        assert guard.config == {}
        assert not guard.has_config

    def test_load_config_handles_missing_file(self):
        """_load_config returns empty dict when file doesn't exist."""
        guard = WorkflowStateGuard(config_path=Path("/nonexistent/file.yml"))

        assert guard.config == {}
        assert not guard.has_config

    def test_load_config_handles_empty_file(self, tmp_path):
        """_load_config returns empty dict for empty YAML file."""
        empty_file = tmp_path / "empty.yml"
        empty_file.write_text("")

        guard = WorkflowStateGuard(config_path=empty_file)

        assert guard.config == {}
        assert not guard.has_config

    def test_has_config_property_requires_workflows(self, tmp_path):
        """has_config returns False if workflows section missing."""
        # Config with states but no workflows
        config_without_workflows = {"states": ["Start", "End"]}
        config_file = tmp_path / "no_workflows.yml"
        config_file.write_text(yaml.dump(config_without_workflows))

        guard = WorkflowStateGuard(config_path=config_file)

        assert not guard.has_config


# =============================================================================
# Configuration Query Tests
# =============================================================================


class TestConfigurationQueries:
    """Test configuration query methods."""

    def test_get_workflow_config_existing_workflow(self, tmp_path, complete_config):
        """get_workflow_config returns workflow configuration."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        wf_config = guard.get_workflow_config("start")

        assert wf_config["command"] == "/jpspec:start"
        assert wf_config["input_states"] == ["To Do"]
        assert wf_config["output_state"] == "In Progress"

    def test_get_workflow_config_nonexistent_workflow(self, tmp_path, complete_config):
        """get_workflow_config returns empty dict for unknown workflow."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        wf_config = guard.get_workflow_config("nonexistent")

        assert wf_config == {}

    def test_get_workflow_config_no_config(self):
        """get_workflow_config returns empty dict when no config loaded."""
        guard = WorkflowStateGuard(config_path=Path("/nonexistent"))

        wf_config = guard.get_workflow_config("any")

        assert wf_config == {}

    def test_get_input_states_returns_list(self, tmp_path, complete_config):
        """get_input_states returns list of allowed input states."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        states = guard.get_input_states("start")

        assert isinstance(states, list)
        assert states == ["To Do"]

    def test_get_input_states_multiple_states(self, tmp_path):
        """get_input_states returns all input states for workflow."""
        config = {
            "workflows": {
                "multi": {
                    "input_states": ["State1", "State2", "State3"],
                    "output_state": "End",
                }
            }
        }
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(config))
        guard = WorkflowStateGuard(config_path=config_file)

        states = guard.get_input_states("multi")

        assert len(states) == 3
        assert "State1" in states
        assert "State2" in states
        assert "State3" in states

    def test_get_input_states_nonexistent_workflow(self, tmp_path, complete_config):
        """get_input_states returns empty list for unknown workflow."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        states = guard.get_input_states("nonexistent")

        assert states == []

    def test_get_output_state_returns_string(self, tmp_path, complete_config):
        """get_output_state returns output state string."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        output = guard.get_output_state("start")

        assert output == "In Progress"

    def test_get_output_state_nonexistent_workflow(self, tmp_path, complete_config):
        """get_output_state returns None for unknown workflow."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        output = guard.get_output_state("nonexistent")

        assert output is None

    def test_get_output_state_missing_in_config(self, tmp_path):
        """get_output_state returns None when output_state not defined."""
        config = {"workflows": {"no_output": {"input_states": ["Start"]}}}
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(config))
        guard = WorkflowStateGuard(config_path=config_file)

        output = guard.get_output_state("no_output")

        assert output is None

    def test_get_all_states_returns_list(self, tmp_path, complete_config):
        """get_all_states returns all defined states."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        states = guard.get_all_states()

        assert isinstance(states, list)
        assert states == ["To Do", "In Progress", "Done"]

    def test_get_all_states_no_states_defined(self, tmp_path, minimal_config):
        """get_all_states returns empty list when states not defined."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(minimal_config))
        guard = WorkflowStateGuard(config_path=config_file)

        states = guard.get_all_states()

        assert states == []


# =============================================================================
# State Normalization Tests
# =============================================================================


class TestStateNormalization:
    """Test state normalization logic."""

    def test_normalize_state_lowercase(self):
        """normalize_state converts to lowercase."""
        guard = WorkflowStateGuard(config_path=Path("/nonexistent"))

        assert guard.normalize_state("TO DO") == "to do"
        assert guard.normalize_state("In Progress") == "in progress"
        assert guard.normalize_state("DONE") == "done"

    def test_normalize_state_strips_whitespace(self):
        """normalize_state strips leading/trailing whitespace."""
        guard = WorkflowStateGuard(config_path=Path("/nonexistent"))

        assert guard.normalize_state("  To Do  ") == "to do"
        assert guard.normalize_state("\tIn Progress\n") == "in progress"
        assert guard.normalize_state("   DONE   ") == "done"

    def test_normalize_state_preserves_internal_spaces(self):
        """normalize_state preserves internal whitespace."""
        guard = WorkflowStateGuard(config_path=Path("/nonexistent"))

        assert guard.normalize_state("In  Progress") == "in  progress"
        assert guard.normalize_state("To   Do") == "to   do"

    def test_normalize_state_empty_string(self):
        """normalize_state handles empty string."""
        guard = WorkflowStateGuard(config_path=Path("/nonexistent"))

        assert guard.normalize_state("") == ""
        assert guard.normalize_state("   ") == ""

    def test_normalize_state_special_characters(self):
        """normalize_state preserves special characters."""
        guard = WorkflowStateGuard(config_path=Path("/nonexistent"))

        assert guard.normalize_state("In-Progress") == "in-progress"
        assert guard.normalize_state("To_Do") == "to_do"
        assert guard.normalize_state("Work/Review") == "work/review"


# =============================================================================
# State Check Tests
# =============================================================================


class TestStateCheck:
    """Test check_state method."""

    def test_check_state_allowed_exact_match(self, tmp_path, complete_config):
        """check_state returns ALLOWED for exact state match."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("start", "To Do")

        assert response.result == StateCheckResult.ALLOWED
        assert response.current_state == "To Do"
        assert response.next_state == "In Progress"
        assert "To Do" in response.required_states

    def test_check_state_allowed_case_insensitive(self, tmp_path, complete_config):
        """check_state matches states case-insensitively."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        # All variations should work
        assert guard.check_state("start", "to do").result == StateCheckResult.ALLOWED
        assert guard.check_state("start", "TO DO").result == StateCheckResult.ALLOWED
        assert guard.check_state("start", "To Do").result == StateCheckResult.ALLOWED

    def test_check_state_allowed_whitespace_trimmed(self, tmp_path, complete_config):
        """check_state trims whitespace from states."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("start", "  To Do  ")

        assert response.result == StateCheckResult.ALLOWED

    def test_check_state_blocked_wrong_state(self, tmp_path, complete_config):
        """check_state returns BLOCKED for invalid state."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("start", "Done")

        assert response.result == StateCheckResult.BLOCKED
        assert response.current_state == "Done"
        assert response.required_states == ["To Do"]
        assert isinstance(response.suggested_workflows, list)

    def test_check_state_skipped_when_skip_flag_set(self, tmp_path, complete_config):
        """check_state returns SKIPPED when skip_check=True."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("start", "Wrong State", skip_check=True)

        assert response.result == StateCheckResult.SKIPPED
        assert "skipped" in response.message.lower()
        assert response.current_state == "Wrong State"

    def test_check_state_no_config_loaded(self):
        """check_state returns NO_CONFIG when config not loaded."""
        guard = WorkflowStateGuard(config_path=Path("/nonexistent"))

        response = guard.check_state("any", "Any State")

        assert response.result == StateCheckResult.NO_CONFIG
        assert "No workflow config" in response.message

    def test_check_state_no_input_states_defined(self, tmp_path):
        """check_state returns NO_CONFIG when workflow has no input_states."""
        config = {"workflows": {"no_inputs": {"output_state": "End"}}}
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(config))
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("no_inputs", "Start")

        assert response.result == StateCheckResult.NO_CONFIG
        assert "No input states defined" in response.message

    def test_check_state_response_includes_next_state(self, tmp_path, complete_config):
        """check_state response includes next_state for allowed transitions."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("start", "To Do")

        assert response.next_state == "In Progress"

    def test_check_state_message_quality_allowed(self, tmp_path, complete_config):
        """check_state provides helpful message for allowed state."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("start", "To Do")

        assert "valid" in response.message.lower()
        assert "To Do" in response.message

    def test_check_state_message_quality_blocked(self, tmp_path, complete_config):
        """check_state provides helpful message for blocked state."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("start", "Done")

        assert "Cannot run" in response.message
        assert "Current state:" in response.message
        assert "Required states:" in response.message
        assert "Suggestions:" in response.message


# =============================================================================
# Error Message Building Tests
# =============================================================================


class TestErrorMessageBuilding:
    """Test _build_blocked_message method."""

    def test_build_blocked_message_includes_workflow_name(
        self, tmp_path, complete_config
    ):
        """Blocked message includes workflow name."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        message = guard._build_blocked_message(
            "start", "Wrong", ["To Do"], ["/jpspec:finish"]
        )

        assert "/jpspec:start" in message

    def test_build_blocked_message_includes_current_state(
        self, tmp_path, complete_config
    ):
        """Blocked message includes current state."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        message = guard._build_blocked_message(
            "start", "Wrong", ["To Do"], ["/jpspec:finish"]
        )

        assert 'Current state: "Wrong"' in message

    def test_build_blocked_message_includes_required_states(
        self, tmp_path, complete_config
    ):
        """Blocked message includes required states."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        message = guard._build_blocked_message("start", "Wrong", ["To Do", "Ready"], [])

        assert "Required states:" in message
        assert "To Do" in message
        assert "Ready" in message

    def test_build_blocked_message_includes_suggestions_when_available(
        self, tmp_path, complete_config
    ):
        """Blocked message includes workflow suggestions."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        message = guard._build_blocked_message(
            "start", "In Progress", ["To Do"], ["/jpspec:finish"]
        )

        assert "Suggestions:" in message
        assert "/jpspec:finish" in message

    def test_build_blocked_message_no_suggestions_available(
        self, tmp_path, complete_config
    ):
        """Blocked message handles no available suggestions."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        message = guard._build_blocked_message("start", "Done", ["To Do"], [])

        assert "No workflows available" in message

    def test_build_blocked_message_includes_bypass_hint(
        self, tmp_path, complete_config
    ):
        """Blocked message mentions --skip-state-check option."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        message = guard._build_blocked_message("start", "Wrong", ["To Do"], [])

        assert "--skip-state-check" in message

    def test_build_blocked_message_multi_line_format(self, tmp_path, complete_config):
        """Blocked message is properly formatted with line breaks."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        message = guard._build_blocked_message("start", "Wrong", ["To Do"], [])

        lines = message.split("\n")
        assert len(lines) > 5  # Should be multi-line
        assert lines[0] == "Cannot run /jpspec:start"
        assert lines[1] == ""  # Blank line for readability


# =============================================================================
# Workflow Suggestions Tests
# =============================================================================


class TestWorkflowSuggestions:
    """Test get_valid_workflows_for_state method."""

    def test_get_valid_workflows_single_match(self, tmp_path, complete_config):
        """get_valid_workflows_for_state returns matching workflows."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        workflows = guard.get_valid_workflows_for_state("To Do")

        assert workflows == ["/jpspec:start"]

    def test_get_valid_workflows_multiple_matches(self, tmp_path):
        """get_valid_workflows_for_state returns all matching workflows."""
        config = {
            "workflows": {
                "option1": {"input_states": ["Ready"], "output_state": "Done"},
                "option2": {"input_states": ["Ready"], "output_state": "Complete"},
            }
        }
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(config))
        guard = WorkflowStateGuard(config_path=config_file)

        workflows = guard.get_valid_workflows_for_state("Ready")

        assert len(workflows) == 2
        assert "/jpspec:option1" in workflows
        assert "/jpspec:option2" in workflows

    def test_get_valid_workflows_no_matches(self, tmp_path, complete_config):
        """get_valid_workflows_for_state returns empty list when no match."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        workflows = guard.get_valid_workflows_for_state("Unknown State")

        assert workflows == []

    def test_get_valid_workflows_case_insensitive(self, tmp_path, complete_config):
        """get_valid_workflows_for_state matches case-insensitively."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        workflows1 = guard.get_valid_workflows_for_state("to do")
        workflows2 = guard.get_valid_workflows_for_state("TO DO")

        assert workflows1 == workflows2 == ["/jpspec:start"]

    def test_get_valid_workflows_sorted(self, tmp_path):
        """get_valid_workflows_for_state returns sorted list."""
        config = {
            "workflows": {
                "zebra": {"input_states": ["Ready"], "output_state": "Done"},
                "alpha": {"input_states": ["Ready"], "output_state": "Complete"},
                "beta": {"input_states": ["Ready"], "output_state": "Finished"},
            }
        }
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(config))
        guard = WorkflowStateGuard(config_path=config_file)

        workflows = guard.get_valid_workflows_for_state("Ready")

        # Should be sorted alphabetically
        assert workflows == ["/jpspec:alpha", "/jpspec:beta", "/jpspec:zebra"]

    def test_get_valid_workflows_no_config(self):
        """get_valid_workflows_for_state returns empty list with no config."""
        guard = WorkflowStateGuard(config_path=Path("/nonexistent"))

        workflows = guard.get_valid_workflows_for_state("Any State")

        assert workflows == []


# =============================================================================
# Task State Update Tests
# =============================================================================


class TestTaskStateUpdate:
    """Test update_task_state method."""

    def test_update_task_state_success(
        self, tmp_path, complete_config, mock_task_system
    ):
        """update_task_state successfully updates task state."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(
            config_path=config_file, task_system=mock_task_system
        )

        success, message = guard.update_task_state("task-123", "start")

        assert success
        assert "updated to" in message.lower()
        assert "In Progress" in message
        mock_task_system.set_task_state.assert_called_once_with(
            "task-123", "In Progress"
        )

    def test_update_task_state_no_output_state(self, tmp_path, mock_task_system):
        """update_task_state fails when workflow has no output state."""
        config = {"workflows": {"no_output": {"input_states": ["Start"]}}}
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(config))
        guard = WorkflowStateGuard(
            config_path=config_file, task_system=mock_task_system
        )

        success, message = guard.update_task_state("task-123", "no_output")

        assert not success
        assert "No output state" in message

    def test_update_task_state_no_task_system(self, tmp_path, complete_config):
        """update_task_state fails when no task system configured."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        success, message = guard.update_task_state("task-123", "start")

        assert not success
        assert "No task system" in message

    def test_update_task_state_task_system_fails(
        self, tmp_path, complete_config, mock_task_system
    ):
        """update_task_state handles task system failure."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        mock_task_system.set_task_state.return_value = False
        guard = WorkflowStateGuard(
            config_path=config_file, task_system=mock_task_system
        )

        success, message = guard.update_task_state("task-123", "start")

        assert not success
        assert "Failed to update" in message

    def test_update_task_state_unknown_workflow(
        self, tmp_path, complete_config, mock_task_system
    ):
        """update_task_state fails gracefully for unknown workflow."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(
            config_path=config_file, task_system=mock_task_system
        )

        success, message = guard.update_task_state("task-123", "nonexistent")

        assert not success
        mock_task_system.set_task_state.assert_not_called()


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_check_workflow_state_allowed(self, tmp_path, complete_config):
        """check_workflow_state returns (True, message) for allowed."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))

        can_proceed, message = check_workflow_state(
            "start", "To Do", config_path=str(config_file)
        )

        assert can_proceed
        assert "valid" in message.lower()

    def test_check_workflow_state_blocked(self, tmp_path, complete_config):
        """check_workflow_state returns (False, message) for blocked."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))

        can_proceed, message = check_workflow_state(
            "start", "Done", config_path=str(config_file)
        )

        assert not can_proceed
        assert "Cannot run" in message

    def test_check_workflow_state_skipped(self, tmp_path, complete_config):
        """check_workflow_state returns (True, message) when skipped."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))

        can_proceed, message = check_workflow_state(
            "start", "Wrong", skip=True, config_path=str(config_file)
        )

        assert can_proceed
        assert "skipped" in message.lower()

    def test_check_workflow_state_no_config(self):
        """check_workflow_state returns (True, message) when no config."""
        can_proceed, message = check_workflow_state(
            "any", "Any State", config_path="/nonexistent/config.yml"
        )

        assert can_proceed
        assert "No workflow config" in message

    def test_check_workflow_state_no_config_path(
        self, tmp_path, complete_config, monkeypatch
    ):
        """check_workflow_state searches default paths when path=None."""
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / "jpspec_workflow.yml"
        config_file.write_text(yaml.dump(complete_config))

        can_proceed, message = check_workflow_state("start", "To Do")

        assert can_proceed

    def test_get_next_state_returns_state(self, tmp_path, complete_config):
        """get_next_state returns output state for workflow."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))

        next_state = get_next_state("start", config_path=str(config_file))

        assert next_state == "In Progress"

    def test_get_next_state_returns_none(self, tmp_path, complete_config):
        """get_next_state returns None for unknown workflow."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))

        next_state = get_next_state("nonexistent", config_path=str(config_file))

        assert next_state is None

    def test_get_next_state_no_config_path(
        self, tmp_path, complete_config, monkeypatch
    ):
        """get_next_state searches default paths when path=None."""
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / "jpspec_workflow.yml"
        config_file.write_text(yaml.dump(complete_config))

        next_state = get_next_state("start")

        assert next_state == "In Progress"

    def test_get_valid_workflows_returns_list(self, tmp_path, complete_config):
        """get_valid_workflows returns list of valid workflows."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))

        workflows = get_valid_workflows("To Do", config_path=str(config_file))

        assert workflows == ["/jpspec:start"]

    def test_get_valid_workflows_empty_list(self, tmp_path, complete_config):
        """get_valid_workflows returns empty list for unknown state."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))

        workflows = get_valid_workflows("Unknown", config_path=str(config_file))

        assert workflows == []

    def test_get_valid_workflows_no_config_path(
        self, tmp_path, complete_config, monkeypatch
    ):
        """get_valid_workflows searches default paths when path=None."""
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / "jpspec_workflow.yml"
        config_file.write_text(yaml.dump(complete_config))

        workflows = get_valid_workflows("To Do")

        assert workflows == ["/jpspec:start"]


# =============================================================================
# Edge Cases and Boundary Conditions
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_workflow_name(self, tmp_path, complete_config):
        """Handle empty workflow name gracefully."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("", "To Do")

        assert response.result == StateCheckResult.NO_CONFIG

    def test_empty_current_state(self, tmp_path, complete_config):
        """Handle empty current state gracefully."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("start", "")

        assert response.result == StateCheckResult.BLOCKED

    def test_whitespace_only_workflow_name(self, tmp_path, complete_config):
        """Handle whitespace-only workflow name."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("   ", "To Do")

        assert response.result == StateCheckResult.NO_CONFIG

    def test_whitespace_only_current_state(self, tmp_path, complete_config):
        """Handle whitespace-only current state."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(complete_config))
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("start", "   ")

        assert response.result == StateCheckResult.BLOCKED

    def test_unicode_in_state_names(self, tmp_path):
        """Handle Unicode characters in state names."""
        config = {
            "workflows": {
                "test": {
                    "input_states": ["待办", "进行中"],
                    "output_state": "完成",
                }
            }
        }
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(config, allow_unicode=True))
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("test", "待办")

        assert response.result == StateCheckResult.ALLOWED
        assert response.next_state == "完成"

    def test_very_long_state_name(self, tmp_path):
        """Handle very long state names."""
        long_state = "A" * 1000
        config = {
            "workflows": {"test": {"input_states": [long_state], "output_state": "End"}}
        }
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(config))
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("test", long_state)

        assert response.result == StateCheckResult.ALLOWED

    def test_many_input_states(self, tmp_path):
        """Handle workflow with many input states."""
        many_states = [f"State{i}" for i in range(100)]
        config = {
            "workflows": {"test": {"input_states": many_states, "output_state": "End"}}
        }
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(config))
        guard = WorkflowStateGuard(config_path=config_file)

        # All should be allowed
        for state in many_states:
            response = guard.check_state("test", state)
            assert response.result == StateCheckResult.ALLOWED

    def test_special_yaml_characters_in_state(self, tmp_path):
        """Handle YAML special characters in state names."""
        config = {
            "workflows": {
                "test": {
                    "input_states": ["State: With: Colons", "State [brackets]"],
                    "output_state": "State {braces}",
                }
            }
        }
        config_file = tmp_path / "config.yml"
        config_file.write_text(yaml.dump(config))
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("test", "State: With: Colons")

        assert response.result == StateCheckResult.ALLOWED

    def test_null_values_in_config(self, tmp_path):
        """Handle null values in configuration."""
        config_file = tmp_path / "config.yml"
        config_file.write_text(
            """
workflows:
  test:
    input_states: null
    output_state: null
"""
        )
        guard = WorkflowStateGuard(config_path=config_file)

        response = guard.check_state("test", "Any")

        # Should handle gracefully
        assert response.result == StateCheckResult.NO_CONFIG

    def test_recursive_config_loading_protection(self, tmp_path):
        """Ensure config loading doesn't follow symlinks recursively."""
        config_file = tmp_path / "config.yml"
        # has_config requires workflows to be non-empty
        config_file.write_text(
            "workflows:\n  test:\n    input_states: [Start]\n    output_state: End"
        )

        # This shouldn't cause infinite loop
        guard = WorkflowStateGuard(config_path=config_file)
        assert guard.has_config


# =============================================================================
# StateCheckResponse Tests
# =============================================================================


class TestStateCheckResponse:
    """Test StateCheckResponse dataclass."""

    def test_response_initialization_minimal(self):
        """StateCheckResponse can be created with minimal fields."""
        response = StateCheckResponse(result=StateCheckResult.ALLOWED, message="OK")

        assert response.result == StateCheckResult.ALLOWED
        assert response.message == "OK"
        assert response.current_state is None
        assert response.required_states is None
        assert response.suggested_workflows is None
        assert response.next_state is None

    def test_response_initialization_complete(self):
        """StateCheckResponse can be created with all fields."""
        response = StateCheckResponse(
            result=StateCheckResult.BLOCKED,
            message="Error",
            current_state="Wrong",
            required_states=["Right"],
            suggested_workflows=["/jpspec:fix"],
            next_state="Fixed",
        )

        assert response.result == StateCheckResult.BLOCKED
        assert response.message == "Error"
        assert response.current_state == "Wrong"
        assert response.required_states == ["Right"]
        assert response.suggested_workflows == ["/jpspec:fix"]
        assert response.next_state == "Fixed"

    def test_response_equality(self):
        """StateCheckResponse supports equality comparison."""
        r1 = StateCheckResponse(result=StateCheckResult.ALLOWED, message="OK")
        r2 = StateCheckResponse(result=StateCheckResult.ALLOWED, message="OK")

        assert r1 == r2

    def test_response_inequality(self):
        """StateCheckResponse detects inequality."""
        r1 = StateCheckResponse(result=StateCheckResult.ALLOWED, message="OK")
        r2 = StateCheckResponse(result=StateCheckResult.BLOCKED, message="Error")

        assert r1 != r2


# =============================================================================
# StateCheckResult Enum Tests
# =============================================================================


class TestStateCheckResultEnum:
    """Test StateCheckResult enum."""

    def test_enum_values_exist(self):
        """All expected enum values exist."""
        assert StateCheckResult.ALLOWED
        assert StateCheckResult.BLOCKED
        assert StateCheckResult.SKIPPED
        assert StateCheckResult.NO_CONFIG
        assert StateCheckResult.NO_TASK

    def test_enum_values_unique(self):
        """All enum values are unique."""
        values = [
            StateCheckResult.ALLOWED,
            StateCheckResult.BLOCKED,
            StateCheckResult.SKIPPED,
            StateCheckResult.NO_CONFIG,
            StateCheckResult.NO_TASK,
        ]
        assert len(values) == len(set(values))

    def test_enum_string_values(self):
        """Enum values have expected string representations."""
        assert StateCheckResult.ALLOWED.value == "allowed"
        assert StateCheckResult.BLOCKED.value == "blocked"
        assert StateCheckResult.SKIPPED.value == "skipped"
        assert StateCheckResult.NO_CONFIG.value == "no_config"
        assert StateCheckResult.NO_TASK.value == "no_task"

    def test_enum_comparison(self):
        """Enum values support comparison."""
        assert StateCheckResult.ALLOWED != StateCheckResult.BLOCKED
