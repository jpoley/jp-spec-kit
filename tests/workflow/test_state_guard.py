"""Tests for workflow state guard."""

import tempfile
from pathlib import Path

import pytest
import yaml

from specify_cli.workflow.state_guard import (
    StateCheckResult,
    WorkflowStateGuard,
    check_workflow_state,
    get_next_state,
)


@pytest.fixture
def sample_config():
    """Sample workflow configuration."""
    return {
        "workflows": {
            "assess": {"input_states": ["To Do"], "output_state": "Assessed"},
            "specify": {"input_states": ["Assessed"], "output_state": "Specified"},
            "research": {"input_states": ["Specified"], "output_state": "Researched"},
            "plan": {"input_states": ["Specified", "Researched"], "output_state": "Planned"},
            "implement": {"input_states": ["Planned"], "output_state": "In Implementation"},
            "validate": {"input_states": ["In Implementation"], "output_state": "Validated"},
            "operate": {"input_states": ["Validated"], "output_state": "Deployed"},
        }
    }


@pytest.fixture
def config_file(sample_config):
    """Create temporary config file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        yaml.dump(sample_config, f)
        return Path(f.name)


class TestWorkflowStateGuard:
    """Tests for WorkflowStateGuard class."""

    def test_load_config(self, config_file):
        """Test loading workflow configuration."""
        guard = WorkflowStateGuard(config_file)
        assert "workflows" in guard.config
        assert "specify" in guard.config["workflows"]

    def test_missing_config(self):
        """Test handling of missing config file."""
        guard = WorkflowStateGuard(Path("/nonexistent/config.yml"))
        assert guard.config == {}

    def test_get_input_states(self, config_file):
        """Test getting input states for workflow."""
        guard = WorkflowStateGuard(config_file)
        states = guard.get_input_states("plan")
        assert "Specified" in states
        assert "Researched" in states

    def test_get_output_state(self, config_file):
        """Test getting output state for workflow."""
        guard = WorkflowStateGuard(config_file)
        assert guard.get_output_state("implement") == "In Implementation"

    def test_check_state_allowed(self, config_file):
        """Test state check when state is allowed."""
        guard = WorkflowStateGuard(config_file)
        result, msg = guard.check_state("implement", "Planned")
        assert result == StateCheckResult.ALLOWED

    def test_check_state_blocked(self, config_file):
        """Test state check when state is blocked."""
        guard = WorkflowStateGuard(config_file)
        result, msg = guard.check_state("implement", "Specified")
        assert result == StateCheckResult.BLOCKED
        assert "Cannot run" in msg
        assert "Planned" in msg

    def test_check_state_skip(self, config_file):
        """Test state check with skip flag."""
        guard = WorkflowStateGuard(config_file)
        result, msg = guard.check_state("implement", "Wrong State", skip_check=True)
        assert result == StateCheckResult.SKIPPED

    def test_check_state_no_config(self):
        """Test state check with no config."""
        guard = WorkflowStateGuard(Path("/nonexistent.yml"))
        result, msg = guard.check_state("implement", "Any State")
        assert result == StateCheckResult.NO_CONFIG

    def test_case_insensitive_state_check(self, config_file):
        """Test that state checks are case-insensitive."""
        guard = WorkflowStateGuard(config_file)
        result, _ = guard.check_state("implement", "planned")
        assert result == StateCheckResult.ALLOWED
        result, _ = guard.check_state("implement", "PLANNED")
        assert result == StateCheckResult.ALLOWED

    def test_get_valid_workflows_for_state(self, config_file):
        """Test getting valid workflows for a state."""
        guard = WorkflowStateGuard(config_file)
        workflows = guard.get_valid_workflows_for_state("Specified")
        assert "/jpspec:research" in workflows
        assert "/jpspec:plan" in workflows

    def test_multiple_input_states(self, config_file):
        """Test workflow with multiple valid input states."""
        guard = WorkflowStateGuard(config_file)
        result1, _ = guard.check_state("plan", "Specified")
        result2, _ = guard.check_state("plan", "Researched")
        assert result1 == StateCheckResult.ALLOWED
        assert result2 == StateCheckResult.ALLOWED


class TestCLIHelpers:
    """Tests for CLI helper functions."""

    def test_check_workflow_state_allowed(self, config_file):
        """Test CLI helper returns True for allowed state."""
        can_proceed, msg = check_workflow_state("implement", "Planned", config_path=str(config_file))
        assert can_proceed is True

    def test_check_workflow_state_blocked(self, config_file):
        """Test CLI helper returns False for blocked state."""
        can_proceed, msg = check_workflow_state("implement", "To Do", config_path=str(config_file))
        assert can_proceed is False
        assert "Cannot run" in msg

    def test_get_next_state(self, config_file):
        """Test getting next state via CLI helper."""
        next_state = get_next_state("validate", config_path=str(config_file))
        assert next_state == "Validated"

    def test_get_next_state_no_config(self):
        """Test getting next state with no config."""
        next_state = get_next_state("validate", config_path="/nonexistent.yml")
        assert next_state is None


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_state_string(self, config_file):
        """Test handling of empty state string."""
        guard = WorkflowStateGuard(config_file)
        result, _ = guard.check_state("implement", "")
        assert result == StateCheckResult.BLOCKED

    def test_whitespace_state_string(self, config_file):
        """Test handling of whitespace in state string."""
        guard = WorkflowStateGuard(config_file)
        result, _ = guard.check_state("implement", "  Planned  ")
        assert result == StateCheckResult.ALLOWED

    def test_unknown_workflow(self, config_file):
        """Test handling of unknown workflow name."""
        guard = WorkflowStateGuard(config_file)
        result, msg = guard.check_state("nonexistent", "Any State")
        assert result == StateCheckResult.NO_CONFIG
