"""Tests for MCP backlog client."""

from pathlib import Path

from flowspec_cli.backlog.mcp_client import MCPBacklogClient


def test_client_initialization(tmp_path):
    """Test client initializes with workspace root."""
    client = MCPBacklogClient(tmp_path)

    assert client.workspace_root == tmp_path


def test_client_default_workspace():
    """Test client uses cwd as default workspace."""
    client = MCPBacklogClient()

    assert client.workspace_root == Path.cwd()


def test_task_view(tmp_path):
    """Test viewing task via MCP."""
    client = MCPBacklogClient(tmp_path)

    result = client.task_view("task-123")

    assert "id" in result
    assert "status" in result
    assert "title" in result


def test_task_edit(tmp_path):
    """Test editing task via MCP."""
    client = MCPBacklogClient(tmp_path)

    success = client.task_edit("task-123", status="In Progress")

    assert success is True


def test_task_edit_with_title(tmp_path):
    """Test editing task title via MCP."""
    client = MCPBacklogClient(tmp_path)

    success = client.task_edit("task-123", title="New Title", status="Done")

    assert success is True


def test_task_list(tmp_path):
    """Test listing tasks via MCP."""
    client = MCPBacklogClient(tmp_path)

    tasks = client.task_list(status="To Do")

    assert isinstance(tasks, list)


def test_task_list_with_filters(tmp_path):
    """Test listing tasks with filters."""
    client = MCPBacklogClient(tmp_path)

    tasks = client.task_list(status="In Progress", assignee="@user", limit=10)

    assert isinstance(tasks, list)


def test_task_create(tmp_path):
    """Test creating task via MCP."""
    client = MCPBacklogClient(tmp_path)

    task_id = client.task_create(
        title="New Task",
        description="Test task",
        labels=["backend"],
        acceptance_criteria=["AC1", "AC2"],
    )

    assert task_id is not None
    assert isinstance(task_id, str)


def test_task_create_minimal(tmp_path):
    """Test creating task with minimal parameters."""
    client = MCPBacklogClient(tmp_path)

    task_id = client.task_create(title="Minimal Task")

    assert task_id is not None


def test_mcp_availability_check(tmp_path):
    """Test MCP availability check."""
    client = MCPBacklogClient(tmp_path)

    # Should return True (assumes MCP available)
    assert client._check_mcp_availability() is True
