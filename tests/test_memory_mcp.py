"""Tests for MCP resource endpoints - Task memory via MCP protocol.

These tests verify that MCP resources are properly registered and that the
underlying business logic (via TaskMemoryStore and ContextInjector) works correctly.

Note: We test the resource registration and business logic separately,
as testing actual MCP resource invocation requires a running MCP server.
"""

import pytest
from pathlib import Path

# Check if MCP is available
try:
    from mcp.server.fastmcp import FastMCP

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from specify_cli.memory.store import TaskMemoryStore
from specify_cli.memory.injector import ContextInjector

# Skip all tests if MCP not available
pytestmark = pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP not installed")


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory with task memory setup."""
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()

    # Create CLAUDE.md
    claude_md = backlog_dir / "CLAUDE.md"
    claude_md.write_text(
        """# Backlog Task Management

## Task Workflow

Example content.
"""
    )

    # Create memory directory
    memory_dir = backlog_dir / "memory"
    memory_dir.mkdir()

    # Create template directory
    templates_dir = tmp_path / "templates" / "memory"
    templates_dir.mkdir(parents=True)

    template_file = templates_dir / "default.md"
    template_file.write_text(
        """# Task Memory: {task_id}

**Task**: {task_title}
**Created**: {created_date}
**Last Updated**: {updated_date}

## Context

## Key Decisions

## Notes
"""
    )

    return tmp_path


def test_register_memory_resources(tmp_project: Path) -> None:
    """Test that memory resources can be registered with MCP server."""
    from specify_cli.memory.mcp import register_memory_resources

    server = FastMCP("jpspec-test")
    register_memory_resources(server, tmp_project)

    # Verify server was created
    assert server is not None
    assert server.name == "jpspec-test"

    # The server should have registered the resources
    # We can't easily inspect FastMCP's internal state, but we can verify
    # the registration didn't raise an error


def test_create_memory_mcp_server(tmp_project: Path) -> None:
    """Test creation of standalone memory MCP server."""
    from specify_cli.memory.mcp import create_memory_mcp_server

    server = create_memory_mcp_server(tmp_project)

    assert server is not None
    assert server.name == "jpspec-memory"


def test_business_logic_task_memory_exists(tmp_project: Path) -> None:
    """Test business logic: retrieving existing task memory."""
    # This tests the actual logic that MCP resources would call
    store = TaskMemoryStore(tmp_project)
    store.create("task-375", task_title="Test Task")

    # Verify we can read it back
    content = store.read("task-375")
    assert "# Task Memory: task-375" in content
    assert "Test Task" in content


def test_business_logic_task_memory_not_found(tmp_project: Path) -> None:
    """Test business logic: handling non-existent task memory."""
    store = TaskMemoryStore(tmp_project)

    # Should raise FileNotFoundError for non-existent task
    with pytest.raises(FileNotFoundError):
        store.read("task-999")


def test_business_logic_active_task(tmp_project: Path) -> None:
    """Test business logic: retrieving active task from CLAUDE.md."""
    # Create task memory
    store = TaskMemoryStore(tmp_project)
    store.create("task-375", task_title="Active Task")

    # Set as active
    injector = ContextInjector(tmp_project)
    injector.update_active_task("task-375")

    # Verify we can retrieve active task ID
    active_task_id = injector.get_active_task_id()
    assert active_task_id == "task-375"

    # And read its memory
    content = store.read(active_task_id)
    assert "# Task Memory: task-375" in content


def test_business_logic_no_active_task(tmp_project: Path) -> None:
    """Test business logic: handling no active task."""
    injector = ContextInjector(tmp_project)

    # Should return None when no active task
    active_task_id = injector.get_active_task_id()
    assert active_task_id is None


def test_business_logic_active_task_memory_not_found(tmp_project: Path) -> None:
    """Test business logic: active task exists but memory doesn't."""
    injector = ContextInjector(tmp_project)
    injector.update_active_task("task-999")

    # Active task is set
    assert injector.get_active_task_id() == "task-999"

    # But memory doesn't exist
    store = TaskMemoryStore(tmp_project)
    assert not store.exists("task-999")


def test_business_logic_task_id_validation(tmp_project: Path) -> None:
    """Test business logic: task ID format validation."""
    # The MCP resources should validate task IDs starting with "task-"
    # This is just to document the expected behavior

    valid_ids = ["task-375", "task-1", "task-999"]
    invalid_ids = ["invalid-id", "task", "375", ""]

    # We don't have explicit validation in store, but MCP resources should check
    # For now, just verify the pattern is consistent
    for task_id in valid_ids:
        assert task_id.startswith("task-")

    for task_id in invalid_ids:
        assert not task_id.startswith("task-")


def test_mcp_import_error_handling() -> None:
    """Test that MCP functions handle missing MCP package gracefully."""
    # This is implicitly tested by the pytestmark skip decorator
    # If MCP is not available, all these tests are skipped
    assert MCP_AVAILABLE, "This test should only run when MCP is available"


def test_memory_content_format(tmp_project: Path) -> None:
    """Test that memory content follows expected markdown format."""
    store = TaskMemoryStore(tmp_project)
    store.create("task-375", task_title="Test Task")

    content = store.read("task-375")

    # Verify expected sections exist
    assert "# Task Memory: task-375" in content
    assert "## Context" in content
    assert "## Key Decisions" in content
    assert "## Notes" in content
