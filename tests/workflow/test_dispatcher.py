"""Tests for workflow dispatcher."""

import pytest

from flowspec_cli.workflow.dispatcher import WorkflowDispatcher


def test_dispatcher_initialization(tmp_path):
    """Test that dispatcher initializes with all handlers."""
    dispatcher = WorkflowDispatcher(tmp_path)

    expected_handlers = [
        "specify",
        "plan",
        "implement",
        "validate",
        "assess",
        "research",
        "submit-n-watch-pr",
    ]

    for handler in expected_handlers:
        assert handler in dispatcher.handlers
        assert dispatcher.handlers[handler].startswith("/flow:")


def test_dispatch_unknown_workflow(tmp_path):
    """Test that unknown workflow raises ValueError."""
    dispatcher = WorkflowDispatcher(tmp_path)

    with pytest.raises(ValueError, match="Unknown workflow"):
        dispatcher.dispatch("nonexistent")


def test_dispatch_specify(tmp_path):
    """Test dispatching specify workflow."""
    dispatcher = WorkflowDispatcher(tmp_path)

    result = dispatcher.dispatch("specify")

    assert result["success"] is True
    assert result["workflow"] == "specify"
    assert result["command"] == "/flow:specify"
    assert result["execution_mode"] == "agent"
    assert "next_action" in result


def test_dispatch_plan(tmp_path):
    """Test dispatching plan workflow."""
    dispatcher = WorkflowDispatcher(tmp_path)

    result = dispatcher.dispatch("plan")

    assert result["success"] is True
    assert result["workflow"] == "plan"
    assert result["command"] == "/flow:plan"


def test_dispatch_implement(tmp_path):
    """Test dispatching implement workflow."""
    dispatcher = WorkflowDispatcher(tmp_path)

    result = dispatcher.dispatch("implement")

    assert result["success"] is True
    assert result["workflow"] == "implement"
    assert result["command"] == "/flow:implement"


def test_dispatch_validate(tmp_path):
    """Test dispatching validate workflow."""
    dispatcher = WorkflowDispatcher(tmp_path)

    result = dispatcher.dispatch("validate")

    assert result["success"] is True
    assert result["workflow"] == "validate"
    assert result["command"] == "/flow:validate"


def test_dispatch_with_context(tmp_path):
    """Test dispatching with context data."""
    dispatcher = WorkflowDispatcher(tmp_path)

    context = {"complexity": 7, "task_id": "task-123"}
    result = dispatcher.dispatch("plan", context)

    assert result["success"] is True
    assert result["workflow"] == "plan"


def test_can_execute_programmatically(tmp_path):
    """Test checking if workflow can be executed programmatically."""
    dispatcher = WorkflowDispatcher(tmp_path)

    # Currently all workflows are agent-based
    assert dispatcher.can_execute_programmatically("specify") is False
    assert dispatcher.can_execute_programmatically("plan") is False
    assert dispatcher.can_execute_programmatically("implement") is False


def test_get_execution_instructions(tmp_path):
    """Test getting execution instructions."""
    dispatcher = WorkflowDispatcher(tmp_path)

    instructions = dispatcher.get_execution_instructions("specify")

    assert "/flow:specify" in instructions
    assert "workflow" in instructions.lower()
    assert str(tmp_path) in instructions


def test_get_execution_instructions_unknown_workflow(tmp_path):
    """Test getting instructions for unknown workflow raises error."""
    dispatcher = WorkflowDispatcher(tmp_path)

    with pytest.raises(ValueError, match="Unknown workflow"):
        dispatcher.get_execution_instructions("nonexistent")


def test_all_core_workflows_mapped(tmp_path):
    """Test that all core workflows from flowspec_workflow.yml are mapped."""
    dispatcher = WorkflowDispatcher(tmp_path)

    # Core workflows (inner loop)
    assert "specify" in dispatcher.handlers
    assert "plan" in dispatcher.handlers
    assert "implement" in dispatcher.handlers
    assert "validate" in dispatcher.handlers

    # Supporting workflows
    assert "assess" in dispatcher.handlers
    assert "research" in dispatcher.handlers

    # Ad hoc utilities
    assert "submit-n-watch-pr" in dispatcher.handlers
