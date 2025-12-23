"""Tests for validating flowspec_workflow.yml configuration.

This module validates that the workflow configuration file:
1. Has valid YAML syntax and loads without errors
2. Contains all required sections (states, workflows, transitions, agent_loops)
3. All states are reachable via transitions
4. No cycles exist in the transition graph (forms a valid DAG)
5. Agent names are consistent across workflows and agent_loops
6. All workflows have valid input/output states
7. Metadata counts are accurate

Task: 118 - Create default flowspec_workflow.yml configuration
"""

from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import pytest
import yaml


@pytest.fixture
def workflow_config_path() -> Path:
    """Return path to the workflow configuration file."""
    return Path(__file__).parent.parent / "flowspec_workflow.yml"


@pytest.fixture
def workflow_config(workflow_config_path: Path) -> dict[str, Any]:
    """Load and return the workflow configuration."""
    if not workflow_config_path.exists():
        pytest.skip(f"Workflow config not found at {workflow_config_path}")
    with open(workflow_config_path) as f:
        return yaml.safe_load(f)


class TestWorkflowConfigStructure:
    """Test the basic structure of the workflow configuration."""

    def test_config_loads_without_errors(self, workflow_config_path: Path) -> None:
        """Verify the YAML file loads without syntax errors."""
        assert workflow_config_path.exists(), (
            f"Config file not found: {workflow_config_path}"
        )
        with open(workflow_config_path) as f:
            config = yaml.safe_load(f)
        assert config is not None, "Config file is empty"

    def test_has_version(self, workflow_config: dict[str, Any]) -> None:
        """Verify config has a version field."""
        assert "version" in workflow_config, "Missing 'version' field"
        assert workflow_config["version"] in ("1.0", "1.1", "2.0"), (
            "Expected version 1.0, 1.1, or 2.0"
        )

    def test_has_required_sections(self, workflow_config: dict[str, Any]) -> None:
        """Verify config has all required top-level sections."""
        required_sections = ["states", "workflows", "transitions", "agent_loops"]
        for section in required_sections:
            assert section in workflow_config, f"Missing required section: {section}"

    def test_has_metadata(self, workflow_config: dict[str, Any]) -> None:
        """Verify config has metadata section."""
        assert "metadata" in workflow_config, "Missing 'metadata' section"


class TestStates:
    """Test the states configuration."""

    def test_has_all_required_states(self, workflow_config: dict[str, Any]) -> None:
        """Verify all 9 required states are defined (including Assessed)."""
        expected_states = [
            "To Do",
            "Assessed",
            "Specified",
            "Researched",
            "Planned",
            "In Implementation",
            "Validated",
            "Deployed",
            "Done",
        ]
        states = workflow_config["states"]
        assert len(states) == 9, f"Expected 9 states, got {len(states)}"
        for state in expected_states:
            assert state in states, f"Missing state: {state}"

    def test_states_are_unique(self, workflow_config: dict[str, Any]) -> None:
        """Verify no duplicate states."""
        states = workflow_config["states"]
        assert len(states) == len(set(states)), "Duplicate states found"

    def test_initial_state_is_first(self, workflow_config: dict[str, Any]) -> None:
        """Verify 'To Do' is the first state (initial state convention)."""
        states = workflow_config["states"]
        assert states[0] == "To Do", "First state should be 'To Do'"

    def test_terminal_state_is_last(self, workflow_config: dict[str, Any]) -> None:
        """Verify 'Done' is the last state (terminal state convention)."""
        states = workflow_config["states"]
        assert states[-1] == "Done", "Last state should be 'Done'"


class TestWorkflows:
    """Test the workflows configuration."""

    def test_has_all_seven_workflows(self, workflow_config: dict[str, Any]) -> None:
        """Verify all 7 /flowspec workflows are defined (including assess)."""
        expected_workflows = [
            "assess",
            "specify",
            "research",
            "plan",
            "implement",
            "validate",
            "operate",
        ]
        workflows = workflow_config["workflows"]
        assert len(workflows) >= 7, (
            f"Expected at least 7 workflows, got {len(workflows)}"
        )
        for workflow in expected_workflows:
            assert workflow in workflows, f"Missing workflow: {workflow}"

    def test_workflow_has_required_fields(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify each workflow has required fields."""
        required_fields = [
            "command",
            "description",
            "agents",
            "input_states",
            "output_state",
        ]
        workflows = workflow_config["workflows"]
        for name, workflow in workflows.items():
            for field in required_fields:
                assert field in workflow, f"Workflow '{name}' missing field: {field}"

    def test_workflow_commands_match_flowspec(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify workflow commands follow /flow:{name} pattern."""
        workflows = workflow_config["workflows"]
        for name, workflow in workflows.items():
            expected_command = f"/flow:{name}"
            assert workflow["command"] == expected_command, (
                f"Workflow '{name}' has incorrect command: {workflow['command']}"
            )

    def test_workflow_input_states_are_valid(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify all input_states reference valid states."""
        valid_states = set(workflow_config["states"])
        workflows = workflow_config["workflows"]
        for name, workflow in workflows.items():
            for input_state in workflow["input_states"]:
                assert input_state in valid_states, (
                    f"Workflow '{name}' has invalid input_state: {input_state}"
                )

    def test_workflow_output_states_are_valid(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify all output_states reference valid states."""
        valid_states = set(workflow_config["states"])
        workflows = workflow_config["workflows"]
        for name, workflow in workflows.items():
            assert workflow["output_state"] in valid_states, (
                f"Workflow '{name}' has invalid output_state: {workflow['output_state']}"
            )

    def test_each_workflow_has_agents(self, workflow_config: dict[str, Any]) -> None:
        """Verify each workflow has at least one agent."""
        workflows = workflow_config["workflows"]
        for name, workflow in workflows.items():
            assert len(workflow["agents"]) > 0, f"Workflow '{name}' has no agents"


class TestAgentAssignments:
    """Test agent assignments match expected values from command files."""

    def test_specify_has_pm_planner(self, workflow_config: dict[str, Any]) -> None:
        """Verify specify workflow uses PM Planner agent."""
        agents = workflow_config["workflows"]["specify"]["agents"]
        agent_names = [a["name"] for a in agents]
        assert "product-requirements-manager" in agent_names

    def test_research_has_correct_agents(self, workflow_config: dict[str, Any]) -> None:
        """Verify research workflow uses researcher and business-validator."""
        agents = workflow_config["workflows"]["research"]["agents"]
        agent_names = [a["name"] for a in agents]
        assert "researcher" in agent_names
        assert "business-validator" in agent_names

    def test_plan_has_correct_agents(self, workflow_config: dict[str, Any]) -> None:
        """Verify plan workflow uses software-architect and platform-engineer."""
        agents = workflow_config["workflows"]["plan"]["agents"]
        agent_names = [a["name"] for a in agents]
        assert "software-architect" in agent_names
        assert "platform-engineer" in agent_names

    def test_implement_has_correct_agents(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify implement workflow uses frontend and backend engineers."""
        agents = workflow_config["workflows"]["implement"]["agents"]
        agent_names = [a["name"] for a in agents]
        assert "frontend-engineer" in agent_names
        assert "backend-engineer" in agent_names

    def test_validate_has_correct_agents(self, workflow_config: dict[str, Any]) -> None:
        """Verify validate workflow uses QA, security, tech-writer, release-manager."""
        agents = workflow_config["workflows"]["validate"]["agents"]
        agent_names = [a["name"] for a in agents]
        assert "quality-guardian" in agent_names
        assert "secure-by-design-engineer" in agent_names
        assert "tech-writer" in agent_names
        assert "release-manager" in agent_names

    def test_operate_has_sre_agent(self, workflow_config: dict[str, Any]) -> None:
        """Verify operate workflow uses SRE agent."""
        agents = workflow_config["workflows"]["operate"]["agents"]
        agent_names = [a["name"] for a in agents]
        assert "sre-agent" in agent_names


class TestTransitions:
    """Test state transition configuration."""

    def test_transitions_have_required_fields(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify each transition has from, to, and via fields."""
        transitions = workflow_config["transitions"]
        for i, transition in enumerate(transitions):
            assert "from" in transition, f"Transition {i} missing 'from' field"
            assert "to" in transition, f"Transition {i} missing 'to' field"
            assert "via" in transition, f"Transition {i} missing 'via' field"

    def test_transition_states_are_valid(self, workflow_config: dict[str, Any]) -> None:
        """Verify all transitions reference valid states."""
        valid_states = set(workflow_config["states"])
        transitions = workflow_config["transitions"]
        for i, transition in enumerate(transitions):
            assert transition["from"] in valid_states, (
                f"Transition {i} has invalid 'from' state: {transition['from']}"
            )
            assert transition["to"] in valid_states, (
                f"Transition {i} has invalid 'to' state: {transition['to']}"
            )

    def test_primary_workflow_path_exists(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify the primary forward path through all states exists."""
        transitions = workflow_config["transitions"]

        # Build adjacency list from transitions
        adj: dict[str, list[str]] = defaultdict(list)
        for t in transitions:
            adj[t["from"]].append(t["to"])

        # Verify primary path exists
        # To Do -> Assessed -> Specified -> (Researched or Planned) -> Planned
        # -> In Implementation -> Validated -> Deployed -> Done
        assert "Assessed" in adj["To Do"], "No transition from 'To Do' to 'Assessed'"
        assert "Specified" in adj["Assessed"], (
            "No transition from 'Assessed' to 'Specified'"
        )
        # Specified can go to Researched or Planned
        assert "Researched" in adj["Specified"] or "Planned" in adj["Specified"], (
            "No transition from 'Specified'"
        )
        # Planned comes from either Specified or Researched
        assert "Planned" in adj.get("Specified", []) or "Planned" in adj.get(
            "Researched", []
        )
        assert "In Implementation" in adj["Planned"], "No transition from 'Planned'"
        assert "Validated" in adj["In Implementation"], (
            "No transition from 'In Implementation'"
        )
        assert "Deployed" in adj["Validated"], "No transition from 'Validated'"
        assert "Done" in adj["Deployed"], "No transition from 'Deployed'"


class TestStateReachability:
    """Test that all states are reachable from initial state."""

    def test_all_states_reachable_from_initial(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify all states can be reached from 'To Do'."""
        transitions = workflow_config["transitions"]
        states = set(workflow_config["states"])

        # Build adjacency list
        adj: dict[str, list[str]] = defaultdict(list)
        for t in transitions:
            adj[t["from"]].append(t["to"])

        # BFS from initial state (using deque for O(1) popleft)
        visited: set[str] = set()
        queue: deque[str] = deque(["To Do"])
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for neighbor in adj.get(current, []):
                if neighbor not in visited:
                    queue.append(neighbor)

        # Check all states are reachable
        unreachable = states - visited
        assert len(unreachable) == 0, f"Unreachable states from 'To Do': {unreachable}"


class TestNoCyclesInPrimaryPath:
    """Test that the primary workflow path has no cycles (is a DAG)."""

    def test_no_cycles_in_forward_transitions(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify no cycles in forward (non-rework/rollback) transitions."""
        transitions = workflow_config["transitions"]

        # Filter out rework and rollback transitions
        forward_transitions = [
            t
            for t in transitions
            if t.get("via") not in ["rework", "rollback", "manual"]
        ]

        # Build adjacency list (excluding self-loops as they don't block forward progress)
        adj: dict[str, list[str]] = defaultdict(list)
        for t in forward_transitions:
            # Self-loops (from == to) are allowed as they don't prevent forward progress
            if t["from"] != t["to"]:
                adj[t["from"]].append(t["to"])

        # Check for cycles using DFS
        def has_cycle(node: str, visited: set[str], rec_stack: set[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        visited: set[str] = set()
        states = list(workflow_config["states"])
        for state in states:
            if state not in visited:
                if has_cycle(state, visited, set()):
                    pytest.fail(f"Cycle detected starting from state: {state}")


class TestAgentLoopClassification:
    """Test agent loop classification matches documented inner/outer loops."""

    def test_agent_loops_has_inner_and_outer(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify agent_loops has both inner and outer classifications."""
        agent_loops = workflow_config["agent_loops"]
        assert "inner" in agent_loops, "Missing 'inner' loop classification"
        assert "outer" in agent_loops, "Missing 'outer' loop classification"

    def test_inner_loop_has_implementation_agents(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify inner loop includes frontend and backend engineers."""
        inner_agents = workflow_config["agent_loops"]["inner"]["agents"]
        assert "frontend-engineer" in inner_agents
        assert "backend-engineer" in inner_agents

    def test_outer_loop_has_planning_and_ops_agents(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify outer loop includes planning and operations agents."""
        outer_agents = workflow_config["agent_loops"]["outer"]["agents"]
        # Planning agents
        assert "product-requirements-manager" in outer_agents
        assert "software-architect" in outer_agents
        assert "platform-engineer" in outer_agents
        # Validation agents
        assert "quality-guardian" in outer_agents
        assert "secure-by-design-engineer" in outer_agents
        # Operations agents
        assert "sre-agent" in outer_agents

    def test_all_workflow_agents_classified(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify all agents from workflows are classified in agent_loops."""
        # Collect all agents from workflows
        workflow_agents: set[str] = set()
        for workflow in workflow_config["workflows"].values():
            for agent in workflow["agents"]:
                workflow_agents.add(agent["name"])

        # Collect all agents from classifications
        inner_agents = set(workflow_config["agent_loops"]["inner"]["agents"])
        outer_agents = set(workflow_config["agent_loops"]["outer"]["agents"])
        classified_agents = inner_agents | outer_agents

        # Check all workflow agents are classified
        unclassified = workflow_agents - classified_agents
        assert len(unclassified) == 0, f"Unclassified agents: {unclassified}"

    def test_no_agent_in_both_loops(self, workflow_config: dict[str, Any]) -> None:
        """Verify no agent is classified in both inner and outer loops."""
        inner_agents = set(workflow_config["agent_loops"]["inner"]["agents"])
        outer_agents = set(workflow_config["agent_loops"]["outer"]["agents"])
        overlap = inner_agents & outer_agents
        assert len(overlap) == 0, f"Agents in both loops: {overlap}"


class TestMetadataAccuracy:
    """Test that metadata counts are accurate."""

    def test_state_count_accurate(self, workflow_config: dict[str, Any]) -> None:
        """Verify metadata state_count matches actual count."""
        actual = len(workflow_config["states"])
        expected = workflow_config["metadata"]["state_count"]
        assert actual == expected, (
            f"state_count mismatch: actual={actual}, metadata={expected}"
        )

    def test_workflow_count_accurate(self, workflow_config: dict[str, Any]) -> None:
        """Verify metadata workflow_count matches actual count."""
        actual = len(workflow_config["workflows"])
        expected = workflow_config["metadata"]["workflow_count"]
        assert actual == expected, (
            f"workflow_count mismatch: actual={actual}, metadata={expected}"
        )

    def test_agent_count_accurate(self, workflow_config: dict[str, Any]) -> None:
        """Verify metadata agent_count matches actual unique agents."""
        # Count unique agents from workflows
        unique_agents: set[str] = set()
        for workflow in workflow_config["workflows"].values():
            for agent in workflow["agents"]:
                unique_agents.add(agent["name"])

        actual = len(unique_agents)
        expected = workflow_config["metadata"]["agent_count"]
        assert actual == expected, (
            f"agent_count mismatch: actual={actual}, metadata={expected}"
        )

    def test_inner_loop_agent_count_accurate(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify metadata inner_loop_agent_count matches actual count."""
        actual = len(workflow_config["agent_loops"]["inner"]["agents"])
        expected = workflow_config["metadata"]["inner_loop_agent_count"]
        assert actual == expected, (
            f"inner_loop_agent_count mismatch: actual={actual}, metadata={expected}"
        )

    def test_outer_loop_agent_count_accurate(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify metadata outer_loop_agent_count matches actual count."""
        actual = len(workflow_config["agent_loops"]["outer"]["agents"])
        expected = workflow_config["metadata"]["outer_loop_agent_count"]
        assert actual == expected, (
            f"outer_loop_agent_count mismatch: actual={actual}, metadata={expected}"
        )


class TestWorkflowStateConsistency:
    """Test workflow states are consistent with transitions."""

    def test_workflow_output_has_transition(
        self, workflow_config: dict[str, Any]
    ) -> None:
        """Verify each workflow's output_state is a valid transition target."""
        workflows = workflow_config["workflows"]
        transitions = workflow_config["transitions"]

        # Build set of (from, to) pairs from transitions
        transition_pairs: set[tuple[str, str]] = set()
        for t in transitions:
            transition_pairs.add((t["from"], t["to"]))

        # Check each workflow has at least one valid transition
        for name, workflow in workflows.items():
            output_state = workflow["output_state"]
            input_states = workflow["input_states"]

            # At least one input_state should transition to output_state
            has_valid_transition = any(
                (input_state, output_state) in transition_pairs
                for input_state in input_states
            )

            # Allow manual transitions for terminal states
            if output_state == "Done":
                continue

            assert has_valid_transition, (
                f"Workflow '{name}': no transition from any input state "
                f"{input_states} to output state '{output_state}'"
            )
