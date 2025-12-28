"""Tests for workflow orchestrator."""

from flowspec_cli.workflow.orchestrator import WorkflowOrchestrator


def test_orchestrator_initialization(tmp_path):
    """Test that orchestrator initializes correctly."""
    # Create a minimal workflow config
    config_file = tmp_path / "flowspec_workflow.yml"
    config_file.write_text("""
version: "2.0"
states: ["To Do", "Done"]
workflows:
  specify:
    command: "/flow:specify"
    agents: ["pm-planner"]
    input_states: ["To Do"]
    output_state: "Done"
transitions:
  - from: "To Do"
    to: "Done"
    via: "specify"
custom_workflows:
  test_workflow:
    name: "Test Workflow"
    mode: "vibing"
    steps:
      - workflow: "specify"
    rigor:
      log_decisions: true
      log_events: true
      backlog_integration: true
      memory_tracking: true
      follow_constitution: true
""")

    # Initialize orchestrator
    orchestrator = WorkflowOrchestrator(tmp_path, "test-001")

    # Verify it loaded the custom workflow
    assert "test_workflow" in orchestrator.custom_workflows
    assert orchestrator.custom_workflows["test_workflow"]["name"] == "Test Workflow"


def test_list_custom_workflows(tmp_path):
    """Test listing custom workflows."""
    config_file = tmp_path / "flowspec_workflow.yml"
    config_file.write_text("""
version: "2.0"
states: ["To Do", "Done"]
workflows:
  specify:
    command: "/flow:specify"
    agents: ["pm-planner"]
    input_states: ["To Do"]
    output_state: "Done"
transitions:
  - from: "To Do"
    to: "Done"
    via: "specify"
custom_workflows:
  workflow1:
    name: "Workflow 1"
    mode: "vibing"
    steps:
      - workflow: "specify"
    rigor:
      log_decisions: true
      log_events: true
      backlog_integration: true
      memory_tracking: true
      follow_constitution: true
  workflow2:
    name: "Workflow 2"
    mode: "spec-ing"
    steps:
      - workflow: "plan"
    rigor:
      log_decisions: true
      log_events: true
      backlog_integration: true
      memory_tracking: true
      follow_constitution: true
""")

    orchestrator = WorkflowOrchestrator(tmp_path, "test-002")
    workflows = orchestrator.list_custom_workflows()

    assert len(workflows) == 2
    assert "workflow1" in workflows
    assert "workflow2" in workflows


def test_condition_evaluation(tmp_path):
    """Test condition evaluation logic."""
    config_file = tmp_path / "flowspec_workflow.yml"
    config_file.write_text("""
version: "2.0"
states: ["To Do", "Done"]
workflows:
  specify:
    command: "/flow:specify"
    agents: ["pm-planner"]
    input_states: ["To Do"]
    output_state: "Done"
transitions:
  - from: "To Do"
    to: "Done"
    via: "specify"
custom_workflows: {}
""")

    orchestrator = WorkflowOrchestrator(tmp_path, "test-003")

    # Test various conditions
    assert orchestrator._evaluate_condition("complexity >= 5", {"complexity": 7})
    assert not orchestrator._evaluate_condition("complexity >= 5", {"complexity": 3})
    assert orchestrator._evaluate_condition("complexity <= 5", {"complexity": 3})
    assert orchestrator._evaluate_condition("complexity == 5", {"complexity": 5})
    assert orchestrator._evaluate_condition("complexity != 5", {"complexity": 3})
