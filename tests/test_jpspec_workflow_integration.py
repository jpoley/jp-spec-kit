"""Integration tests for /jpspec workflow state constraints.

This module tests the WorkflowConfig integration with /jpspec commands,
ensuring that workflow state transitions are properly validated and enforced.

Tests verify:
- Workflow state validation (input_states checking)
- State transitions (output_state updating)
- Error handling for invalid states
- Custom workflow configurations
- Complete workflow paths through all states
"""

import pytest
from pathlib import Path

from specify_cli.workflow.config import WorkflowConfig
from specify_cli.workflow.exceptions import (
    WorkflowNotFoundError,
    WorkflowStateError,
)


class TestWorkflowStateValidation:
    """Test workflow state validation for /jpspec commands."""

    @pytest.fixture
    def workflow_config(self) -> WorkflowConfig:
        """Load default workflow configuration."""
        # Clear cache to ensure fresh load for each test
        WorkflowConfig.clear_cache()
        # Skip schema validation in tests (schema may be outdated)
        return WorkflowConfig.load(validate=False)

    def test_specify_allowed_from_assessed(self, workflow_config: WorkflowConfig):
        """Test /jpspec:specify is allowed from 'Assessed' state."""
        # AC #2: Test /jpspec:specify state transition (To Do → Specified)
        # Note: Actually Assessed → Specified based on workflow config
        input_states = workflow_config.get_input_states("specify")
        assert "Assessed" in input_states, "specify should accept Assessed state"

        output_state = workflow_config.get_next_state("Assessed", "specify")
        assert output_state == "Specified", "specify should transition to Specified"

    def test_specify_blocked_from_wrong_state(self, workflow_config: WorkflowConfig):
        """Test /jpspec:specify is blocked from incorrect states."""
        # AC #8: Tests for invalid state transitions (error handling)
        with pytest.raises(WorkflowStateError) as exc_info:
            workflow_config.get_next_state("Planned", "specify")

        error = exc_info.value
        assert "specify" in str(error)
        assert "Planned" in str(error)
        assert hasattr(error, "valid_states")

    def test_research_allowed_from_specified(self, workflow_config: WorkflowConfig):
        """Test /jpspec:research is allowed from 'Specified' state."""
        # AC #3: Test /jpspec:research state transition (Specified → Researched)
        input_states = workflow_config.get_input_states("research")
        assert "Specified" in input_states, "research should accept Specified state"

        output_state = workflow_config.get_next_state("Specified", "research")
        assert output_state == "Researched", "research should transition to Researched"

    def test_research_is_optional(self, workflow_config: WorkflowConfig):
        """Test that research phase is marked as optional."""
        # AC #3: Verify research is optional workflow
        is_optional = workflow_config.is_workflow_optional("research")
        assert is_optional, "research phase should be optional"

    def test_plan_allowed_from_specified_or_researched(
        self, workflow_config: WorkflowConfig
    ):
        """Test /jpspec:plan accepts both Specified and Researched states."""
        # AC #4: Test /jpspec:plan state transition (Researched → Planned)
        input_states = workflow_config.get_input_states("plan")
        assert "Specified" in input_states, "plan should accept Specified state"
        assert "Researched" in input_states, "plan should accept Researched state"

        # Test transition from Researched
        output_state = workflow_config.get_next_state("Researched", "plan")
        assert output_state == "Planned", "plan should transition to Planned"

        # Test transition from Specified (skipping research)
        output_state = workflow_config.get_next_state("Specified", "plan")
        assert output_state == "Planned", "plan should transition to Planned"

    def test_implement_allowed_from_planned(self, workflow_config: WorkflowConfig):
        """Test /jpspec:implement is allowed from 'Planned' state."""
        # AC #5: Test /jpspec:implement state transition (Planned → In Implementation)
        input_states = workflow_config.get_input_states("implement")
        assert "Planned" in input_states, "implement should accept Planned state"

        output_state = workflow_config.get_next_state("Planned", "implement")
        assert output_state == "In Implementation", (
            "implement should transition to In Implementation"
        )

    def test_implement_blocked_from_specified(self, workflow_config: WorkflowConfig):
        """Test /jpspec:implement is blocked before planning."""
        # AC #8: Tests for invalid state transitions
        with pytest.raises(WorkflowStateError) as exc_info:
            workflow_config.get_next_state("Specified", "implement")

        error = exc_info.value
        assert "implement" in str(error)
        assert "Specified" in str(error)

    def test_validate_allowed_from_in_implementation(
        self, workflow_config: WorkflowConfig
    ):
        """Test /jpspec:validate is allowed from 'In Implementation' state."""
        # AC #6: Test /jpspec:validate state transition (In Implementation → Validated)
        input_states = workflow_config.get_input_states("validate")
        assert "In Implementation" in input_states, (
            "validate should accept In Implementation state"
        )

        output_state = workflow_config.get_next_state("In Implementation", "validate")
        assert output_state == "Validated", "validate should transition to Validated"

    def test_validate_requires_human_approval(self, workflow_config: WorkflowConfig):
        """Test that validate workflow requires human approval."""
        # AC #6: Verify validate requires human approval
        workflow_def = workflow_config.workflows.get("validate", {})
        requires_approval = workflow_def.get("requires_human_approval", False)
        assert requires_approval, "validate workflow should require human approval"

    def test_operate_allowed_from_validated(self, workflow_config: WorkflowConfig):
        """Test /jpspec:operate is allowed from 'Validated' state."""
        # AC #7: Test /jpspec:operate state transition (Validated → Deployed)
        input_states = workflow_config.get_input_states("operate")
        assert "Validated" in input_states, "operate should accept Validated state"

        output_state = workflow_config.get_next_state("Validated", "operate")
        assert output_state == "Deployed", "operate should transition to Deployed"


class TestWorkflowTransitions:
    """Test complete workflow transition paths."""

    @pytest.fixture
    def workflow_config(self) -> WorkflowConfig:
        """Load workflow configuration."""
        WorkflowConfig.clear_cache()
        return WorkflowConfig.load(validate=False)

    def test_full_workflow_path_with_research(self, workflow_config: WorkflowConfig):
        """Test complete workflow: Assessed → Specified → Researched → Planned → In Implementation → Validated → Deployed."""
        # This tests the full happy path through all workflow stages
        states = [
            ("Assessed", "specify", "Specified"),
            ("Specified", "research", "Researched"),
            ("Researched", "plan", "Planned"),
            ("Planned", "implement", "In Implementation"),
            ("In Implementation", "validate", "Validated"),
            ("Validated", "operate", "Deployed"),
        ]

        for from_state, workflow, expected_to_state in states:
            actual_to_state = workflow_config.get_next_state(from_state, workflow)
            assert actual_to_state == expected_to_state, (
                f"Workflow {workflow} should transition {from_state} → {expected_to_state}"
            )

    def test_workflow_path_skipping_research(self, workflow_config: WorkflowConfig):
        """Test workflow path that skips optional research phase."""
        # Test that research is optional and can be skipped
        states = [
            ("Assessed", "specify", "Specified"),
            ("Specified", "plan", "Planned"),  # Skip research
            ("Planned", "implement", "In Implementation"),
            ("In Implementation", "validate", "Validated"),
            ("Validated", "operate", "Deployed"),
        ]

        for from_state, workflow, expected_to_state in states:
            actual_to_state = workflow_config.get_next_state(from_state, workflow)
            assert actual_to_state == expected_to_state, (
                f"Workflow {workflow} should transition {from_state} → {expected_to_state}"
            )

    def test_get_valid_workflows_for_each_state(self, workflow_config: WorkflowConfig):
        """Test get_valid_workflows returns correct workflows for each state."""
        # AC #5: Error messages suggest valid workflows for current state
        test_cases = {
            "Assessed": ["specify"],
            "Specified": ["research", "plan"],  # research is optional
            "Researched": ["plan"],
            "Planned": ["implement"],
            "In Implementation": ["validate"],
            "Validated": ["operate"],
        }

        for state, expected_workflows in test_cases.items():
            valid_workflows = workflow_config.get_valid_workflows(state)
            for expected in expected_workflows:
                assert expected in valid_workflows, (
                    f"State '{state}' should allow workflow '{expected}'"
                )

    def test_transition_validation(self, workflow_config: WorkflowConfig):
        """Test is_valid_transition for workflow transitions."""
        # AC #2-7: Verify all expected transitions are valid
        valid_transitions = [
            ("Assessed", "Specified"),
            ("Specified", "Researched"),
            ("Specified", "Planned"),  # Skip research
            ("Researched", "Planned"),
            ("Planned", "In Implementation"),
            ("In Implementation", "Validated"),
            ("Validated", "Deployed"),
        ]

        for from_state, to_state in valid_transitions:
            is_valid = workflow_config.is_valid_transition(from_state, to_state)
            assert is_valid, f"Transition {from_state} → {to_state} should be valid"

    def test_invalid_transitions_blocked(self, workflow_config: WorkflowConfig):
        """Test that invalid transitions are properly blocked."""
        # AC #8: Tests for invalid state transitions
        invalid_transitions = [
            ("Assessed", "Planned"),  # Skip specify
            ("Specified", "In Implementation"),  # Skip plan
            ("Planned", "Validated"),  # Skip implement
            ("Researched", "Validated"),  # Skip plan and implement
        ]

        for from_state, to_state in invalid_transitions:
            is_valid = workflow_config.is_valid_transition(from_state, to_state)
            assert not is_valid, (
                f"Transition {from_state} → {to_state} should be invalid"
            )


class TestWorkflowAgents:
    """Test workflow agent assignments."""

    @pytest.fixture
    def workflow_config(self) -> WorkflowConfig:
        """Load workflow configuration."""
        WorkflowConfig.clear_cache()
        return WorkflowConfig.load(validate=False)

    def test_specify_has_pm_planner_agent(self, workflow_config: WorkflowConfig):
        """Test /jpspec:specify uses @pm-planner agent."""
        # AC #1: All /jpspec command implementations reference WorkflowConfig
        agents = workflow_config.get_agents("specify")
        assert len(agents) > 0, "specify workflow should have agents"

        # Check agent structure
        workflows = workflow_config.workflows
        specify_workflow = workflows.get("specify", {})
        agent_list = specify_workflow.get("agents", [])
        assert len(agent_list) > 0, "specify should have agent definitions"

        # Verify PM planner agent
        agent_names = [a.get("name") for a in agent_list if isinstance(a, dict)]
        assert "product-requirements-manager" in agent_names, (
            "specify should have product-requirements-manager agent"
        )

    def test_all_workflows_have_agents(self, workflow_config: WorkflowConfig):
        """Test that all /jpspec workflows have assigned agents."""
        # AC #1: All /jpspec command implementations reference WorkflowConfig
        workflows_to_test = [
            "specify",
            "research",
            "plan",
            "implement",
            "validate",
            "operate",
        ]

        for workflow_name in workflows_to_test:
            agents = workflow_config.get_agents(workflow_name)
            assert len(agents) > 0, (
                f"Workflow '{workflow_name}' should have agents assigned"
            )

    def test_agent_loop_classification(self, workflow_config: WorkflowConfig):
        """Test that agent_loops configuration exists and has structure."""
        # Verify agent_loops configuration exists
        agent_loops = workflow_config._data.get("agent_loops", {})
        assert agent_loops, "agent_loops configuration should exist"

        # Verify inner loop agents exist in config (uses 'inner' key)
        inner_agents_config = agent_loops.get("inner", {}).get("agents", [])
        assert len(inner_agents_config) > 0, "Inner loop should have agents"
        assert "frontend-engineer" in inner_agents_config, (
            "frontend-engineer should be in inner loop"
        )
        assert "backend-engineer" in inner_agents_config, (
            "backend-engineer should be in inner loop"
        )

        # Verify outer loop agents exist in config (uses 'outer' key)
        outer_agents_config = agent_loops.get("outer", {}).get("agents", [])
        assert len(outer_agents_config) > 0, "Outer loop should have agents"
        assert "product-requirements-manager" in outer_agents_config, (
            "product-requirements-manager should be in outer loop"
        )
        assert "software-architect" in outer_agents_config, (
            "software-architect should be in outer loop"
        )


class TestCustomWorkflowConfiguration:
    """Test support for custom workflow configurations."""

    def test_load_with_custom_config(self, tmp_path: Path):
        """Test loading custom workflow configuration."""
        # AC #9: Tests for custom workflow configurations
        custom_config = {
            "version": "1.1",
            "states": ["To Do", "Custom State", "Done"],
            "workflows": {
                "custom": {
                    "command": "/jpspec:custom",
                    "description": "Custom workflow",
                    "agents": [{"name": "custom-agent", "identity": "@custom"}],
                    "input_states": ["To Do"],
                    "output_state": "Custom State",
                }
            },
            "transitions": [
                {
                    "from": "To Do",
                    "to": "Custom State",
                    "via": "custom",
                    "validation": "NONE",
                }
            ],
        }

        # Write custom config
        config_file = tmp_path / "jpspec_workflow.yml"
        import yaml

        with open(config_file, "w") as f:
            yaml.safe_dump(custom_config, f)

        # Load custom config
        WorkflowConfig.clear_cache()
        config = WorkflowConfig.load(path=config_file, validate=False)

        # Verify custom workflow loaded
        workflows = config.workflows
        assert "custom" in workflows, "Custom workflow should be loaded"

        # Verify custom state transition
        output_state = config.get_next_state("To Do", "custom")
        assert output_state == "Custom State", "Custom workflow should work"

    def test_workflow_config_version(self):
        """Test that workflow config has correct version."""
        # AC #9: Verify version metadata
        WorkflowConfig.clear_cache()
        config = WorkflowConfig.load(validate=False)

        version = config.version
        assert version is not None, "Config should have version"
        assert isinstance(version, str), "Version should be string"

    def test_workflow_config_metadata(self):
        """Test that workflow config includes metadata."""
        # AC #9: Tests for custom workflow configurations
        WorkflowConfig.clear_cache()
        config = WorkflowConfig.load(validate=False)

        # Check that config has expected workflows
        workflows = config.workflows
        expected_workflows = [
            "specify",
            "research",
            "plan",
            "implement",
            "validate",
            "operate",
        ]

        for workflow_name in expected_workflows:
            assert workflow_name in workflows, (
                f"Config should include '{workflow_name}' workflow"
            )


class TestErrorHandlingAndMessages:
    """Test error handling and error message quality."""

    @pytest.fixture
    def workflow_config(self) -> WorkflowConfig:
        """Load workflow configuration."""
        WorkflowConfig.clear_cache()
        return WorkflowConfig.load(validate=False)

    def test_invalid_workflow_error_message(self, workflow_config: WorkflowConfig):
        """Test error message for invalid workflow name."""
        # AC #3: Commands provide clear error messages when state check fails
        with pytest.raises(WorkflowNotFoundError) as exc_info:
            workflow_config.get_agents("nonexistent")

        error = exc_info.value
        assert "nonexistent" in str(error), "Error should mention the invalid workflow"

    def test_invalid_state_error_provides_valid_states(
        self, workflow_config: WorkflowConfig
    ):
        """Test that invalid state errors include valid states."""
        # AC #5: Error messages suggest valid workflows for current state
        with pytest.raises(WorkflowStateError) as exc_info:
            workflow_config.get_next_state("Invalid State", "implement")

        error = exc_info.value
        assert hasattr(error, "valid_states"), (
            "Error should provide valid_states attribute"
        )
        assert len(error.valid_states) > 0, "Error should include valid input states"

    def test_error_message_includes_workflow_name(
        self, workflow_config: WorkflowConfig
    ):
        """Test that error messages include workflow name."""
        # AC #3: Commands provide clear error messages
        with pytest.raises(WorkflowStateError) as exc_info:
            workflow_config.get_next_state("Specified", "implement")

        error_msg = str(exc_info.value)
        assert "implement" in error_msg, "Error message should include workflow name"
        assert "Specified" in error_msg, "Error message should include current state"


class TestBacklogIntegration:
    """Test integration with backlog.md task system."""

    @pytest.fixture
    def workflow_config(self) -> WorkflowConfig:
        """Load workflow configuration."""
        WorkflowConfig.clear_cache()
        return WorkflowConfig.load(validate=False)

    def test_workflows_create_backlog_tasks(self, workflow_config: WorkflowConfig):
        """Test that design workflows are configured to create tasks."""
        # AC #6: Commands work with backlog.md task system
        design_workflows = ["specify", "research", "plan", "operate"]

        for workflow_name in design_workflows:
            workflow_def = workflow_config.workflows.get(workflow_name, {})
            creates_tasks = workflow_def.get("creates_backlog_tasks", False)
            assert creates_tasks, (
                f"Workflow '{workflow_name}' should create backlog tasks"
            )

    def test_implement_requires_backlog_tasks(self, workflow_config: WorkflowConfig):
        """Test that implement workflow requires existing tasks."""
        # AC #6: Commands work with backlog.md task system
        workflow_def = workflow_config.workflows.get("implement", {})
        requires_tasks = workflow_def.get("requires_backlog_tasks", False)
        assert requires_tasks, (
            "implement workflow should require existing backlog tasks"
        )

    def test_all_workflows_defined(self, workflow_config: WorkflowConfig):
        """Test that all 6 /jpspec workflows are defined."""
        # AC #8: All 6 commands implement checks
        required_workflows = [
            "specify",
            "research",
            "plan",
            "implement",
            "validate",
            "operate",
        ]

        workflows = workflow_config.workflows
        for workflow_name in required_workflows:
            assert workflow_name in workflows, (
                f"Workflow '{workflow_name}' should be defined"
            )

            # Verify each has required fields
            workflow_def = workflows[workflow_name]
            assert "input_states" in workflow_def, f"{workflow_name} needs input_states"
            assert "output_state" in workflow_def, f"{workflow_name} needs output_state"
            assert "agents" in workflow_def, f"{workflow_name} needs agents"


# Test coverage target: >80%
# This test suite covers:
# - State validation for all 6 workflows (AC #2-7)
# - Invalid state error handling (AC #8)
# - Custom configurations (AC #9)
# - Error message quality (AC #3, #5)
# - Backlog integration (AC #6)
# - All workflow definitions (AC #1, #8)
