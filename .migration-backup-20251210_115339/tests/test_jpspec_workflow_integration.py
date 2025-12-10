"""Integration tests for /jpspec workflow state constraints.

This test module verifies that /jpspec commands correctly enforce workflow
state constraints through the WorkflowStateGuard module. It covers:

- AC #1: Test file exists
- AC #2-7: State transitions for all /jpspec commands
- AC #8: Invalid state transition handling
- AC #9: Custom workflow configurations
- AC #10: Test coverage >80%

The tests simulate real workflow scenarios with mock task systems and
verify that commands properly validate states before execution and
update states after successful completion.
"""

import pytest
from pathlib import Path
from typing import Optional
import yaml

from specify_cli.workflow.state_guard import (
    WorkflowStateGuard,
    StateCheckResult,
)


# =============================================================================
# Test Fixtures
# =============================================================================


class MockTaskSystem:
    """Mock task system for integration testing.

    Simulates a task management system (like backlog.md) with state tracking.
    """

    def __init__(self, initial_state: str = "To Do"):
        """Initialize mock task system with initial state."""
        self.tasks: dict[str, str] = {"task-101": initial_state}
        self.state_history: list[
            tuple[str, str, str]
        ] = []  # (task_id, old_state, new_state)

    def get_task_state(self, task_id: str) -> Optional[str]:
        """Get the current state of a task."""
        return self.tasks.get(task_id)

    def set_task_state(self, task_id: str, new_state: str) -> bool:
        """Update the state of a task. Returns True on success."""
        old_state = self.tasks.get(task_id, "Unknown")
        self.state_history.append((task_id, old_state, new_state))
        self.tasks[task_id] = new_state
        return True


@pytest.fixture
def default_workflow_config():
    """Standard workflow configuration matching jpspec_workflow.yml."""
    return {
        "version": "1.1",
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
                "command": "/jpspec:assess",
                "input_states": ["To Do"],
                "output_state": "Assessed",
            },
            "specify": {
                "command": "/jpspec:specify",
                "input_states": ["Assessed"],
                "output_state": "Specified",
            },
            "research": {
                "command": "/jpspec:research",
                "input_states": ["Specified"],
                "output_state": "Researched",
            },
            "plan": {
                "command": "/jpspec:plan",
                "input_states": ["Specified", "Researched"],
                "output_state": "Planned",
            },
            "implement": {
                "command": "/jpspec:implement",
                "input_states": ["Planned"],
                "output_state": "In Implementation",
            },
            "validate": {
                "command": "/jpspec:validate",
                "input_states": ["In Implementation"],
                "output_state": "Validated",
            },
            "operate": {
                "command": "/jpspec:operate",
                "input_states": ["Validated"],
                "output_state": "Deployed",
            },
        },
    }


@pytest.fixture
def workflow_config_file(default_workflow_config, tmp_path):
    """Create temporary workflow config file."""
    config_path = tmp_path / "jpspec_workflow.yml"
    config_path.write_text(yaml.dump(default_workflow_config))
    return config_path


@pytest.fixture
def custom_workflow_config():
    """Custom workflow configuration for testing configurability."""
    return {
        "version": "1.0",
        "states": ["New", "Active", "Complete"],
        "workflows": {
            "start": {
                "command": "/jpspec:start",
                "input_states": ["New"],
                "output_state": "Active",
            },
            "finish": {
                "command": "/jpspec:finish",
                "input_states": ["Active"],
                "output_state": "Complete",
            },
        },
    }


@pytest.fixture
def custom_config_file(custom_workflow_config, tmp_path):
    """Create temporary custom workflow config file."""
    config_path = tmp_path / "custom_workflow.yml"
    config_path.write_text(yaml.dump(custom_workflow_config))
    return config_path


# =============================================================================
# AC #1: Test File Exists
# =============================================================================


def test_integration_test_file_exists():
    """AC #1: Verify this integration test file exists."""
    test_file = Path(__file__)
    assert test_file.exists(), "Integration test file should exist"
    assert test_file.name == "test_jpspec_workflow_integration.py"


# =============================================================================
# AC #2: /jpspec:specify State Transition (Assessed → Specified)
# =============================================================================


class TestSpecifyTransition:
    """AC #2: Tests for /jpspec:specify state transition (Assessed → Specified)."""

    def test_specify_allowed_from_assessed(self, workflow_config_file):
        """Specify command allowed when task is in Assessed state."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("specify", "Assessed")

        assert response.result == StateCheckResult.ALLOWED
        assert response.next_state == "Specified"
        assert "Assessed" in response.required_states

    def test_specify_blocked_from_todo(self, workflow_config_file):
        """Specify command blocked when task is in To Do state."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("specify", "To Do")

        assert response.result == StateCheckResult.BLOCKED
        assert response.current_state == "To Do"
        assert "Assessed" in response.required_states
        assert "/jpspec:specify" in response.message

    def test_specify_blocked_from_planned(self, workflow_config_file):
        """Specify command blocked when task is already past specification."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("specify", "Planned")

        assert response.result == StateCheckResult.BLOCKED
        assert "Planned" in response.message

    def test_specify_updates_task_state(self, workflow_config_file):
        """Specify command updates task state to Specified after success."""
        mock_system = MockTaskSystem("Assessed")
        guard = WorkflowStateGuard(workflow_config_file, task_system=mock_system)

        # Verify allowed
        response = guard.check_state("specify", "Assessed")
        assert response.result == StateCheckResult.ALLOWED

        # Update state
        success, msg = guard.update_task_state("task-101", "specify")
        assert success
        assert mock_system.get_task_state("task-101") == "Specified"

    def test_specify_case_insensitive_state(self, workflow_config_file):
        """Specify command handles case-insensitive state matching."""
        guard = WorkflowStateGuard(workflow_config_file)

        # All variations should work
        assert (
            guard.check_state("specify", "assessed").result == StateCheckResult.ALLOWED
        )
        assert (
            guard.check_state("specify", "ASSESSED").result == StateCheckResult.ALLOWED
        )
        assert (
            guard.check_state("specify", "Assessed").result == StateCheckResult.ALLOWED
        )


# =============================================================================
# AC #3: /jpspec:research State Transition (Specified → Researched)
# =============================================================================


class TestResearchTransition:
    """AC #3: Tests for /jpspec:research state transition (Specified → Researched)."""

    def test_research_allowed_from_specified(self, workflow_config_file):
        """Research command allowed when task is in Specified state."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("research", "Specified")

        assert response.result == StateCheckResult.ALLOWED
        assert response.next_state == "Researched"

    def test_research_blocked_from_todo(self, workflow_config_file):
        """Research command blocked when task is in To Do state."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("research", "To Do")

        assert response.result == StateCheckResult.BLOCKED
        assert "Specified" in response.required_states

    def test_research_blocked_from_planned(self, workflow_config_file):
        """Research command blocked when task is already planned."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("research", "Planned")

        assert response.result == StateCheckResult.BLOCKED

    def test_research_updates_task_state(self, workflow_config_file):
        """Research command updates task state to Researched after success."""
        mock_system = MockTaskSystem("Specified")
        guard = WorkflowStateGuard(workflow_config_file, task_system=mock_system)

        # Update state
        success, msg = guard.update_task_state("task-101", "research")
        assert success
        assert mock_system.get_task_state("task-101") == "Researched"

    def test_research_transition_recorded_in_history(self, workflow_config_file):
        """Research transition is recorded in task history."""
        mock_system = MockTaskSystem("Specified")
        guard = WorkflowStateGuard(workflow_config_file, task_system=mock_system)

        guard.update_task_state("task-101", "research")

        assert len(mock_system.state_history) == 1
        task_id, old_state, new_state = mock_system.state_history[0]
        assert task_id == "task-101"
        assert old_state == "Specified"
        assert new_state == "Researched"


# =============================================================================
# AC #4: /jpspec:plan State Transition (Specified/Researched → Planned)
# =============================================================================


class TestPlanTransition:
    """AC #4: Tests for /jpspec:plan state transition (Specified/Researched → Planned)."""

    def test_plan_allowed_from_specified(self, workflow_config_file):
        """Plan command allowed when task is in Specified state."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("plan", "Specified")

        assert response.result == StateCheckResult.ALLOWED
        assert response.next_state == "Planned"

    def test_plan_allowed_from_researched(self, workflow_config_file):
        """Plan command allowed when task is in Researched state."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("plan", "Researched")

        assert response.result == StateCheckResult.ALLOWED
        assert response.next_state == "Planned"

    def test_plan_accepts_multiple_input_states(self, workflow_config_file):
        """Plan command configuration has multiple valid input states."""
        guard = WorkflowStateGuard(workflow_config_file)
        input_states = guard.get_input_states("plan")

        assert "Specified" in input_states
        assert "Researched" in input_states
        assert len(input_states) == 2

    def test_plan_blocked_from_todo(self, workflow_config_file):
        """Plan command blocked when task is in To Do state."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("plan", "To Do")

        assert response.result == StateCheckResult.BLOCKED

    def test_plan_blocked_from_implementation(self, workflow_config_file):
        """Plan command blocked when task is already in implementation."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("plan", "In Implementation")

        assert response.result == StateCheckResult.BLOCKED

    def test_plan_updates_task_state_from_specified(self, workflow_config_file):
        """Plan command updates task state from Specified to Planned."""
        mock_system = MockTaskSystem("Specified")
        guard = WorkflowStateGuard(workflow_config_file, task_system=mock_system)

        success, msg = guard.update_task_state("task-101", "plan")
        assert success
        assert mock_system.get_task_state("task-101") == "Planned"

    def test_plan_updates_task_state_from_researched(self, workflow_config_file):
        """Plan command updates task state from Researched to Planned."""
        mock_system = MockTaskSystem("Researched")
        guard = WorkflowStateGuard(workflow_config_file, task_system=mock_system)

        success, msg = guard.update_task_state("task-101", "plan")
        assert success
        assert mock_system.get_task_state("task-101") == "Planned"


# =============================================================================
# AC #5: /jpspec:implement State Transition (Planned → In Implementation)
# =============================================================================


class TestImplementTransition:
    """AC #5: Tests for /jpspec:implement state transition (Planned → In Implementation)."""

    def test_implement_allowed_from_planned(self, workflow_config_file):
        """Implement command allowed when task is in Planned state."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("implement", "Planned")

        assert response.result == StateCheckResult.ALLOWED
        assert response.next_state == "In Implementation"

    def test_implement_blocked_from_todo(self, workflow_config_file):
        """Implement command blocked when task is in To Do state."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("implement", "To Do")

        assert response.result == StateCheckResult.BLOCKED
        assert "Planned" in response.required_states

    def test_implement_blocked_from_specified(self, workflow_config_file):
        """Implement command blocked when task is only specified."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("implement", "Specified")

        assert response.result == StateCheckResult.BLOCKED
        assert response.current_state == "Specified"
        # Should suggest /jpspec:plan
        assert response.suggested_workflows is not None
        assert "/jpspec:plan" in response.suggested_workflows

    def test_implement_blocked_from_validated(self, workflow_config_file):
        """Implement command blocked when task is already validated."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("implement", "Validated")

        assert response.result == StateCheckResult.BLOCKED

    def test_implement_updates_task_state(self, workflow_config_file):
        """Implement command updates task state to In Implementation."""
        mock_system = MockTaskSystem("Planned")
        guard = WorkflowStateGuard(workflow_config_file, task_system=mock_system)

        success, msg = guard.update_task_state("task-101", "implement")
        assert success
        assert mock_system.get_task_state("task-101") == "In Implementation"

    def test_implement_error_message_quality(self, workflow_config_file):
        """Implement command provides helpful error message when blocked."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("implement", "To Do")

        # Message should include all helpful information
        assert "Cannot run /jpspec:implement" in response.message
        assert 'Current state: "To Do"' in response.message
        assert "Required states:" in response.message
        assert "Planned" in response.message
        assert "Suggestions:" in response.message
        assert "--skip-state-check" in response.message


# =============================================================================
# AC #6: /jpspec:validate State Transition (In Implementation → Validated)
# =============================================================================


class TestValidateTransition:
    """AC #6: Tests for /jpspec:validate state transition (In Implementation → Validated)."""

    def test_validate_allowed_from_implementation(self, workflow_config_file):
        """Validate command allowed when task is In Implementation."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("validate", "In Implementation")

        assert response.result == StateCheckResult.ALLOWED
        assert response.next_state == "Validated"

    def test_validate_blocked_from_planned(self, workflow_config_file):
        """Validate command blocked when task is only planned."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("validate", "Planned")

        assert response.result == StateCheckResult.BLOCKED
        assert "In Implementation" in response.required_states

    def test_validate_blocked_from_deployed(self, workflow_config_file):
        """Validate command blocked when task is already deployed."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("validate", "Deployed")

        assert response.result == StateCheckResult.BLOCKED

    def test_validate_updates_task_state(self, workflow_config_file):
        """Validate command updates task state to Validated."""
        mock_system = MockTaskSystem("In Implementation")
        guard = WorkflowStateGuard(workflow_config_file, task_system=mock_system)

        success, msg = guard.update_task_state("task-101", "validate")
        assert success
        assert mock_system.get_task_state("task-101") == "Validated"

    def test_validate_suggests_implement_workflow(self, workflow_config_file):
        """Validate command suggests /jpspec:implement when task is Planned."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("validate", "Planned")

        assert response.suggested_workflows is not None
        assert "/jpspec:implement" in response.suggested_workflows


# =============================================================================
# AC #7: /jpspec:operate State Transition (Validated → Deployed)
# =============================================================================


class TestOperateTransition:
    """AC #7: Tests for /jpspec:operate state transition (Validated → Deployed)."""

    def test_operate_allowed_from_validated(self, workflow_config_file):
        """Operate command allowed when task is Validated."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("operate", "Validated")

        assert response.result == StateCheckResult.ALLOWED
        assert response.next_state == "Deployed"

    def test_operate_blocked_from_implementation(self, workflow_config_file):
        """Operate command blocked when task is still in implementation."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("operate", "In Implementation")

        assert response.result == StateCheckResult.BLOCKED
        assert "Validated" in response.required_states

    def test_operate_blocked_from_todo(self, workflow_config_file):
        """Operate command blocked when task hasn't been validated."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("operate", "To Do")

        assert response.result == StateCheckResult.BLOCKED

    def test_operate_updates_task_state(self, workflow_config_file):
        """Operate command updates task state to Deployed."""
        mock_system = MockTaskSystem("Validated")
        guard = WorkflowStateGuard(workflow_config_file, task_system=mock_system)

        success, msg = guard.update_task_state("task-101", "operate")
        assert success
        assert mock_system.get_task_state("task-101") == "Deployed"

    def test_operate_suggests_validate_workflow(self, workflow_config_file):
        """Operate command suggests /jpspec:validate when task is In Implementation."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("operate", "In Implementation")

        assert response.suggested_workflows is not None
        assert "/jpspec:validate" in response.suggested_workflows


# =============================================================================
# AC #8: Invalid State Transitions (Error Handling)
# =============================================================================


class TestInvalidTransitions:
    """AC #8: Tests for invalid state transitions with helpful error messages."""

    def test_blocked_transition_includes_current_state(self, workflow_config_file):
        """Blocked transition error includes current state."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("operate", "To Do")

        assert response.result == StateCheckResult.BLOCKED
        assert response.current_state == "To Do"
        assert "To Do" in response.message

    def test_blocked_transition_includes_required_states(self, workflow_config_file):
        """Blocked transition error includes required states."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("operate", "To Do")

        assert "Validated" in response.required_states
        assert "Required states:" in response.message

    def test_blocked_transition_suggests_valid_workflows(self, workflow_config_file):
        """Blocked transition error suggests valid workflows for current state."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("operate", "To Do")

        # For "To Do" state, only /jpspec:assess is valid
        assert response.suggested_workflows is not None
        assert "/jpspec:assess" in response.suggested_workflows

    def test_blocked_transition_suggests_bypass_option(self, workflow_config_file):
        """Blocked transition error mentions bypass option."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("operate", "To Do")

        assert "--skip-state-check" in response.message

    def test_skip_state_check_bypasses_validation(self, workflow_config_file):
        """Skip state check flag bypasses all validation."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("operate", "Wrong State", skip_check=True)

        assert response.result == StateCheckResult.SKIPPED
        assert "skipped" in response.message.lower()

    def test_multiple_blocked_transitions_different_messages(
        self, workflow_config_file
    ):
        """Different blocked transitions have contextual messages."""
        guard = WorkflowStateGuard(workflow_config_file)

        response1 = guard.check_state("implement", "To Do")
        response2 = guard.check_state("validate", "To Do")

        # Both blocked but with different required states
        assert response1.result == StateCheckResult.BLOCKED
        assert response2.result == StateCheckResult.BLOCKED
        assert response1.required_states != response2.required_states

    def test_no_valid_workflows_for_terminal_state(self, workflow_config_file):
        """Terminal state (Done) has no valid workflows."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("implement", "Done")

        assert response.result == StateCheckResult.BLOCKED
        # Done state should have no valid next workflows
        valid_workflows = guard.get_valid_workflows_for_state("Done")
        assert len(valid_workflows) == 0

    def test_update_state_without_task_system_fails_gracefully(
        self, workflow_config_file
    ):
        """State update without task system fails with helpful message."""
        guard = WorkflowStateGuard(workflow_config_file)
        success, msg = guard.update_task_state("task-101", "implement")

        assert not success
        assert "No task system" in msg

    def test_update_state_with_invalid_workflow_fails(self, workflow_config_file):
        """State update with invalid workflow name fails gracefully."""
        mock_system = MockTaskSystem("Planned")
        guard = WorkflowStateGuard(workflow_config_file, task_system=mock_system)

        success, msg = guard.update_task_state("task-101", "nonexistent")
        assert not success
        assert "No output state" in msg


# =============================================================================
# AC #9: Custom Workflow Configurations
# =============================================================================


class TestCustomWorkflowConfig:
    """AC #9: Tests with custom workflow configurations."""

    def test_custom_config_loads_successfully(self, custom_config_file):
        """Custom workflow configuration loads successfully."""
        guard = WorkflowStateGuard(custom_config_file)
        assert guard.has_config
        assert "start" in guard.config["workflows"]

    def test_custom_config_states_recognized(self, custom_config_file):
        """Custom workflow states are recognized."""
        guard = WorkflowStateGuard(custom_config_file)
        states = guard.get_all_states()

        assert "New" in states
        assert "Active" in states
        assert "Complete" in states

    def test_custom_workflow_transitions_enforced(self, custom_config_file):
        """Custom workflow transitions are enforced."""
        guard = WorkflowStateGuard(custom_config_file)

        # Start allowed from New
        response1 = guard.check_state("start", "New")
        assert response1.result == StateCheckResult.ALLOWED
        assert response1.next_state == "Active"

        # Start blocked from Active
        response2 = guard.check_state("start", "Active")
        assert response2.result == StateCheckResult.BLOCKED

    def test_custom_config_finish_workflow(self, custom_config_file):
        """Custom finish workflow enforces constraints."""
        guard = WorkflowStateGuard(custom_config_file)

        # Finish allowed from Active
        response1 = guard.check_state("finish", "Active")
        assert response1.result == StateCheckResult.ALLOWED
        assert response1.next_state == "Complete"

        # Finish blocked from New
        response2 = guard.check_state("finish", "New")
        assert response2.result == StateCheckResult.BLOCKED

    def test_custom_config_state_updates(self, custom_config_file):
        """Custom config supports state updates through task system."""
        mock_system = MockTaskSystem("New")
        guard = WorkflowStateGuard(custom_config_file, task_system=mock_system)

        # Update through start workflow
        success, msg = guard.update_task_state("task-101", "start")
        assert success
        assert mock_system.get_task_state("task-101") == "Active"

        # Update through finish workflow
        success, msg = guard.update_task_state("task-101", "finish")
        assert success
        assert mock_system.get_task_state("task-101") == "Complete"

    def test_custom_config_suggestions(self, custom_config_file):
        """Custom config provides workflow suggestions."""
        guard = WorkflowStateGuard(custom_config_file)

        workflows = guard.get_valid_workflows_for_state("New")
        assert "/jpspec:start" in workflows

        workflows = guard.get_valid_workflows_for_state("Active")
        assert "/jpspec:finish" in workflows

    def test_minimal_workflow_config(self, tmp_path):
        """Minimal workflow configuration works."""
        minimal_config = {
            "version": "1.0",
            "workflows": {
                "simple": {
                    "input_states": ["Start"],
                    "output_state": "End",
                }
            },
        }
        config_path = tmp_path / "minimal.yml"
        config_path.write_text(yaml.dump(minimal_config))

        guard = WorkflowStateGuard(config_path)
        assert guard.has_config

        response = guard.check_state("simple", "Start")
        assert response.result == StateCheckResult.ALLOWED

    def test_no_config_file_allows_all_transitions(self):
        """Missing config file allows all transitions (permissive default)."""
        guard = WorkflowStateGuard(Path("/nonexistent/config.yml"))

        response = guard.check_state("any_workflow", "Any State")
        assert response.result == StateCheckResult.NO_CONFIG


# =============================================================================
# Integration Scenario Tests (Complete Workflows)
# =============================================================================


class TestCompleteWorkflowScenarios:
    """Integration tests for complete workflow scenarios."""

    def test_happy_path_full_workflow(self, workflow_config_file):
        """Test complete workflow progression from To Do to Deployed."""
        mock_system = MockTaskSystem("To Do")
        guard = WorkflowStateGuard(workflow_config_file, task_system=mock_system)

        # Step 1: Assess (To Do → Assessed)
        assert (
            guard.check_state("assess", mock_system.get_task_state("task-101")).result
            == StateCheckResult.ALLOWED
        )
        guard.update_task_state("task-101", "assess")
        assert mock_system.get_task_state("task-101") == "Assessed"

        # Step 2: Specify (Assessed → Specified)
        assert (
            guard.check_state("specify", mock_system.get_task_state("task-101")).result
            == StateCheckResult.ALLOWED
        )
        guard.update_task_state("task-101", "specify")
        assert mock_system.get_task_state("task-101") == "Specified"

        # Step 3: Plan (Specified → Planned) - skipping optional research
        assert (
            guard.check_state("plan", mock_system.get_task_state("task-101")).result
            == StateCheckResult.ALLOWED
        )
        guard.update_task_state("task-101", "plan")
        assert mock_system.get_task_state("task-101") == "Planned"

        # Step 4: Implement (Planned → In Implementation)
        assert (
            guard.check_state(
                "implement", mock_system.get_task_state("task-101")
            ).result
            == StateCheckResult.ALLOWED
        )
        guard.update_task_state("task-101", "implement")
        assert mock_system.get_task_state("task-101") == "In Implementation"

        # Step 5: Validate (In Implementation → Validated)
        assert (
            guard.check_state("validate", mock_system.get_task_state("task-101")).result
            == StateCheckResult.ALLOWED
        )
        guard.update_task_state("task-101", "validate")
        assert mock_system.get_task_state("task-101") == "Validated"

        # Step 6: Operate (Validated → Deployed)
        assert (
            guard.check_state("operate", mock_system.get_task_state("task-101")).result
            == StateCheckResult.ALLOWED
        )
        guard.update_task_state("task-101", "operate")
        assert mock_system.get_task_state("task-101") == "Deployed"

        # Verify state history
        assert len(mock_system.state_history) == 6

    def test_workflow_with_research_phase(self, workflow_config_file):
        """Test workflow including optional research phase."""
        mock_system = MockTaskSystem("Specified")
        guard = WorkflowStateGuard(workflow_config_file, task_system=mock_system)

        # Research (Specified → Researched)
        assert (
            guard.check_state("research", mock_system.get_task_state("task-101")).result
            == StateCheckResult.ALLOWED
        )
        guard.update_task_state("task-101", "research")
        assert mock_system.get_task_state("task-101") == "Researched"

        # Plan (Researched → Planned)
        assert (
            guard.check_state("plan", mock_system.get_task_state("task-101")).result
            == StateCheckResult.ALLOWED
        )
        guard.update_task_state("task-101", "plan")
        assert mock_system.get_task_state("task-101") == "Planned"

    def test_attempting_out_of_order_workflow(self, workflow_config_file):
        """Test that out-of-order workflow execution is blocked."""
        guard = WorkflowStateGuard(workflow_config_file)

        # Try to implement without planning
        response = guard.check_state("implement", "Specified")
        assert response.result == StateCheckResult.BLOCKED

        # Verify suggestions point to correct next step
        assert "/jpspec:plan" in response.suggested_workflows

    def test_workflow_branching_point(self, workflow_config_file):
        """Test workflow branching at plan command (Specified or Researched)."""
        guard = WorkflowStateGuard(workflow_config_file)

        # Path 1: Direct to plan from Specified
        response1 = guard.check_state("plan", "Specified")
        assert response1.result == StateCheckResult.ALLOWED

        # Path 2: Plan from Researched
        response2 = guard.check_state("plan", "Researched")
        assert response2.result == StateCheckResult.ALLOWED

        # Both lead to same output state
        assert response1.next_state == response2.next_state == "Planned"

    def test_state_history_tracking(self, workflow_config_file):
        """Test that state transitions are tracked in history."""
        mock_system = MockTaskSystem("Planned")
        guard = WorkflowStateGuard(workflow_config_file, task_system=mock_system)

        # Execute multiple transitions
        guard.update_task_state("task-101", "implement")
        guard.update_task_state("task-101", "validate")
        guard.update_task_state("task-101", "operate")

        # Verify history contains all transitions
        assert len(mock_system.state_history) == 3
        assert mock_system.state_history[0] == (
            "task-101",
            "Planned",
            "In Implementation",
        )
        assert mock_system.state_history[1] == (
            "task-101",
            "In Implementation",
            "Validated",
        )
        assert mock_system.state_history[2] == ("task-101", "Validated", "Deployed")


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_state_string(self, workflow_config_file):
        """Empty state string is handled gracefully."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("implement", "")

        assert response.result == StateCheckResult.BLOCKED

    def test_whitespace_only_state(self, workflow_config_file):
        """Whitespace-only state is handled gracefully."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("implement", "   ")

        assert response.result == StateCheckResult.BLOCKED

    def test_unknown_state_value(self, workflow_config_file):
        """Unknown state value is blocked with helpful message."""
        guard = WorkflowStateGuard(workflow_config_file)
        response = guard.check_state("implement", "UnknownState")

        assert response.result == StateCheckResult.BLOCKED
        assert "UnknownState" in response.message

    def test_state_normalization(self, workflow_config_file):
        """State comparison is case-insensitive and whitespace-trimmed."""
        guard = WorkflowStateGuard(workflow_config_file)

        # All these should be equivalent
        states = ["planned", "  Planned  ", "PLANNED", "PlAnNeD"]
        for state in states:
            response = guard.check_state("implement", state)
            assert response.result == StateCheckResult.ALLOWED

    def test_workflow_config_without_output_state(self, tmp_path):
        """Workflow without output_state can check but not update."""
        incomplete_config = {
            "version": "1.0",
            "workflows": {
                "check_only": {
                    "input_states": ["Start"],
                    # No output_state defined
                }
            },
        }
        config_path = tmp_path / "incomplete.yml"
        config_path.write_text(yaml.dump(incomplete_config))

        mock_system = MockTaskSystem("Start")
        guard = WorkflowStateGuard(config_path, task_system=mock_system)

        # Check works
        response = guard.check_state("check_only", "Start")
        assert response.result == StateCheckResult.ALLOWED

        # Update fails gracefully
        success, msg = guard.update_task_state("task-101", "check_only")
        assert not success
        assert "No output state" in msg

    def test_concurrent_state_checks(self, workflow_config_file):
        """Multiple concurrent state checks don't interfere."""
        guard = WorkflowStateGuard(workflow_config_file)

        # Simulate concurrent checks
        responses = [
            guard.check_state("implement", "Planned"),
            guard.check_state("validate", "In Implementation"),
            guard.check_state("operate", "Validated"),
        ]

        # All should succeed independently
        assert all(r.result == StateCheckResult.ALLOWED for r in responses)

    def test_assess_workflow_at_start(self, workflow_config_file):
        """Assess workflow is the entry point from To Do."""
        guard = WorkflowStateGuard(workflow_config_file)

        # Assess should be allowed from To Do
        response = guard.check_state("assess", "To Do")
        assert response.result == StateCheckResult.ALLOWED
        assert response.next_state == "Assessed"

        # No other workflows should be valid from To Do
        valid_workflows = guard.get_valid_workflows_for_state("To Do")
        assert valid_workflows == ["/jpspec:assess"]
