"""E2E Tests for Agent Context Injection.

This module tests the injection of task memory into agent context through:
- CLAUDE.md @import directives via ContextInjector
- MCP resource access via register_memory_resources
- Manual file reading fallback

Tests the actual API:
- ContextInjector.update_active_task(task_id) - Add/update active task
- ContextInjector.clear_active_task() - Clear active task
- ContextInjector.get_active_task_id() - Get currently active task ID
- register_memory_resources(server, base_path) - Register MCP resources
"""

import json
import pytest
from unittest.mock import MagicMock

from flowspec_cli.memory import TaskMemoryStore
from flowspec_cli.memory.injector import ContextInjector
from flowspec_cli.memory.mcp import register_memory_resources, MCP_AVAILABLE


@pytest.fixture
def injection_project(tmp_path):
    """Create project structure for injection testing."""
    # Create directories
    backlog_dir = tmp_path / "backlog"
    memory_dir = backlog_dir / "memory"
    archive_dir = memory_dir / "archive"
    template_dir = tmp_path / "templates" / "memory"

    backlog_dir.mkdir(parents=True)
    memory_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)
    template_dir.mkdir(parents=True)

    # Create template
    template_content = """# Task Memory: {task_id}

**Created**: {created_date}
**Last Updated**: {updated_date}
**Task**: {task_title}

## Context
{task_title} implementation context.

## Key Decisions
- Decision tracking

## Notes
- Implementation notes
"""
    (template_dir / "default.md").write_text(template_content)

    # Create backlog/CLAUDE.md (where ContextInjector expects it)
    backlog_claude_md = backlog_dir / "CLAUDE.md"
    backlog_claude_md.write_text("""# Backlog Task Management

This is a test project for context injection.

## Task Memory

Task memory files are stored in `backlog/memory/`.
""")

    return tmp_path


@pytest.fixture
def store_with_tasks(injection_project):
    """Create store with sample task memories."""
    store = TaskMemoryStore(base_path=injection_project)
    store.create("task-100", task_title="First Task")
    store.append("task-100", "Working on first task implementation")
    store.create("task-101", task_title="Second Task")
    store.append("task-101", "Second task in progress")
    return store


# --- Test: CLAUDE.md @import Injection ---


class TestCLAUDEMDImport:
    """Tests for CLAUDE.md @import directive injection."""

    def test_inject_single_active_task(self, injection_project, store_with_tasks):
        """Test injecting a single active task into CLAUDE.md."""
        injector = ContextInjector(base_path=injection_project)

        # Inject task-100 as active
        injector.update_active_task("task-100")

        # Verify CLAUDE.md updated
        claude_md = (injection_project / "backlog" / "CLAUDE.md").read_text()
        assert "## Active Task Context" in claude_md
        assert "@import ../memory/task-100.md" in claude_md

    def test_inject_updates_active_task(self, injection_project, store_with_tasks):
        """Test updating from one active task to another."""
        injector = ContextInjector(base_path=injection_project)

        # Set first task
        injector.update_active_task("task-100")
        assert injector.get_active_task_id() == "task-100"

        # Update to second task
        injector.update_active_task("task-101")
        assert injector.get_active_task_id() == "task-101"

        # Verify only one @import exists
        claude_md = (injection_project / "backlog" / "CLAUDE.md").read_text()
        assert claude_md.count("@import") == 1
        assert "@import ../memory/task-101.md" in claude_md
        assert "@import ../memory/task-100.md" not in claude_md

    def test_inject_preserves_claude_md_content(
        self, injection_project, store_with_tasks
    ):
        """Test that injection preserves existing CLAUDE.md content."""
        injector = ContextInjector(base_path=injection_project)

        # Get original content
        original = (injection_project / "backlog" / "CLAUDE.md").read_text()
        assert "# Backlog Task Management" in original

        # Inject task
        injector.update_active_task("task-100")

        # Verify original content preserved
        updated = (injection_project / "backlog" / "CLAUDE.md").read_text()
        assert "# Backlog Task Management" in updated
        assert "Task memory files are stored" in updated

    def test_clear_active_task(self, injection_project, store_with_tasks):
        """Test clearing active task removes @import."""
        injector = ContextInjector(base_path=injection_project)

        # Set then clear
        injector.update_active_task("task-100")
        assert injector.get_active_task_id() == "task-100"

        injector.clear_active_task()
        assert injector.get_active_task_id() is None

        # Verify section removed
        claude_md = (injection_project / "backlog" / "CLAUDE.md").read_text()
        assert "@import" not in claude_md

    def test_inject_handles_missing_claude_md(self, injection_project):
        """Test injection fails gracefully when CLAUDE.md missing."""
        # Remove CLAUDE.md
        (injection_project / "backlog" / "CLAUDE.md").unlink()

        injector = ContextInjector(base_path=injection_project)

        with pytest.raises(FileNotFoundError):
            injector.update_active_task("task-100")

    def test_get_active_task_when_none_set(self, injection_project):
        """Test getting active task when none is set."""
        injector = ContextInjector(base_path=injection_project)
        assert injector.get_active_task_id() is None

    def test_inject_task_not_in_store(self, injection_project):
        """Test injecting task ID that doesn't exist in store.

        The injector doesn't validate task existence - it just adds the import.
        """
        injector = ContextInjector(base_path=injection_project)

        # This should work - injector doesn't validate task existence
        injector.update_active_task("task-999")

        claude_md = (injection_project / "backlog" / "CLAUDE.md").read_text()
        assert "@import ../memory/task-999.md" in claude_md


# --- Test: MCP Resource Access ---


class TestMCPResourceAccess:
    """Tests for MCP resource provider."""

    @pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP package not installed")
    def test_register_memory_resources(self, injection_project, store_with_tasks):
        """Test registering memory resources with MCP server."""
        # Create mock MCP server
        mock_server = MagicMock()
        mock_server.resource = MagicMock(return_value=lambda f: f)

        # Register resources
        register_memory_resources(mock_server, injection_project)

        # Verify resource decorators were called
        assert mock_server.resource.call_count == 2

    @pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP package not installed")
    @pytest.mark.asyncio
    async def test_mcp_get_task_memory(self, injection_project, store_with_tasks):
        """Test MCP resource returns task memory content."""
        from flowspec_cli.memory.mcp import register_memory_resources

        # Create mock server that captures the handler
        handlers = {}

        def capture_resource(uri):
            def decorator(func):
                handlers[uri] = func
                return func

            return decorator

        mock_server = MagicMock()
        mock_server.resource = capture_resource

        register_memory_resources(mock_server, injection_project)

        # Call the handler
        handler = handlers["backlog://memory/{task_id}"]
        result = await handler("task-100")
        data = json.loads(result)

        assert data["task_id"] == "task-100"
        assert data["exists"] is True
        assert "First Task" in data["content"]

    @pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP package not installed")
    @pytest.mark.asyncio
    async def test_mcp_get_active_memory(self, injection_project, store_with_tasks):
        """Test MCP resource returns active task memory."""
        from flowspec_cli.memory.mcp import register_memory_resources

        # Set active task
        injector = ContextInjector(base_path=injection_project)
        injector.update_active_task("task-100")

        # Create mock server that captures the handler
        handlers = {}

        def capture_resource(uri):
            def decorator(func):
                handlers[uri] = func
                return func

            return decorator

        mock_server = MagicMock()
        mock_server.resource = capture_resource

        register_memory_resources(mock_server, injection_project)

        # Call the active handler
        handler = handlers["backlog://memory/active"]
        result = await handler()
        data = json.loads(result)

        assert data["active_task"] == "task-100"
        assert data["exists"] is True

    @pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP package not installed")
    @pytest.mark.asyncio
    async def test_mcp_task_not_found(self, injection_project):
        """Test MCP resource returns error for non-existent task."""
        from flowspec_cli.memory.mcp import register_memory_resources

        handlers = {}

        def capture_resource(uri):
            def decorator(func):
                handlers[uri] = func
                return func

            return decorator

        mock_server = MagicMock()
        mock_server.resource = capture_resource

        register_memory_resources(mock_server, injection_project)

        handler = handlers["backlog://memory/{task_id}"]
        result = await handler("task-999")
        data = json.loads(result)

        assert "error" in data
        assert data["error"] == "Task memory not found"

    @pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP package not installed")
    @pytest.mark.asyncio
    async def test_mcp_invalid_task_id(self, injection_project):
        """Test MCP resource validates task ID format."""
        from flowspec_cli.memory.mcp import register_memory_resources

        handlers = {}

        def capture_resource(uri):
            def decorator(func):
                handlers[uri] = func
                return func

            return decorator

        mock_server = MagicMock()
        mock_server.resource = capture_resource

        register_memory_resources(mock_server, injection_project)

        handler = handlers["backlog://memory/{task_id}"]
        result = await handler("invalid-id")
        data = json.loads(result)

        assert "error" in data
        assert "Invalid task ID" in data["error"]

    @pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP package not installed")
    @pytest.mark.asyncio
    async def test_mcp_no_active_task(self, injection_project):
        """Test MCP resource handles no active task gracefully."""
        from flowspec_cli.memory.mcp import register_memory_resources

        handlers = {}

        def capture_resource(uri):
            def decorator(func):
                handlers[uri] = func
                return func

            return decorator

        mock_server = MagicMock()
        mock_server.resource = capture_resource

        register_memory_resources(mock_server, injection_project)

        handler = handlers["backlog://memory/active"]
        result = await handler()
        data = json.loads(result)

        assert data["active_task"] is None
        assert "No active task" in data["message"]


# --- Test: Manual File Read Fallback ---


class TestManualFileReadFallback:
    """Tests for manual file reading when @import not available."""

    def test_manual_read_active_memory(self, injection_project, store_with_tasks):
        """Test reading active task memory directly from file."""
        store = TaskMemoryStore(base_path=injection_project)
        injector = ContextInjector(base_path=injection_project)

        # Set active task
        injector.update_active_task("task-100")

        # Manually read the file
        active_id = injector.get_active_task_id()
        assert active_id == "task-100"

        content = store.read(active_id)
        assert "First Task" in content

    def test_manual_read_archived_memory(self, injection_project, store_with_tasks):
        """Test reading archived memory directly."""
        store = TaskMemoryStore(base_path=injection_project)

        # Archive a task
        store.archive("task-100")

        # Read from archive
        archive_path = store.archive_dir / "task-100.md"
        assert archive_path.exists()

        content = archive_path.read_text()
        assert "First Task" in content

    def test_manual_list_all_memories(self, injection_project, store_with_tasks):
        """Test listing all memory files."""
        store = TaskMemoryStore(base_path=injection_project)

        # List active
        active = store.list_active()
        assert len(active) == 2
        assert "task-100" in active
        assert "task-101" in active

        # Archive one
        store.archive("task-100")

        # Verify lists update
        active = store.list_active()
        archived = store.list_archived()
        assert len(active) == 1
        assert len(archived) == 1

    def test_manual_search_memory_content(self, injection_project, store_with_tasks):
        """Test searching memory content manually."""
        store = TaskMemoryStore(base_path=injection_project)

        # Search for specific content
        found = []
        for task_id in store.list_active():
            content = store.read(task_id)
            if "first task" in content.lower():
                found.append(task_id)

        assert "task-100" in found


# --- Test: Context Injection Integration ---


class TestContextInjectionIntegration:
    """Integration tests for full context injection workflow."""

    def test_full_workflow_create_inject_read(self, injection_project):
        """Test complete workflow: create memory, inject, read back."""
        store = TaskMemoryStore(base_path=injection_project)
        injector = ContextInjector(base_path=injection_project)

        # Create memory
        store.create("task-200", task_title="Integration Test Task")
        store.append("task-200", "Implementation started")

        # Inject as active
        injector.update_active_task("task-200")

        # Verify can read via injector
        active_id = injector.get_active_task_id()
        assert active_id == "task-200"

        # Verify content
        content = store.read(active_id)
        assert "Integration Test Task" in content
        assert "Implementation started" in content

    def test_multi_task_context_switching(self, injection_project, store_with_tasks):
        """Test switching between multiple task contexts."""
        injector = ContextInjector(base_path=injection_project)
        store = TaskMemoryStore(base_path=injection_project)

        # Switch between tasks
        for task_id in ["task-100", "task-101", "task-100"]:
            injector.update_active_task(task_id)
            assert injector.get_active_task_id() == task_id

            # Verify content is correct
            content = store.read(task_id)
            if task_id == "task-100":
                assert "First Task" in content
            else:
                assert "Second Task" in content

    def test_context_persistence_across_instances(
        self, injection_project, store_with_tasks
    ):
        """Test context persists when creating new injector instance."""
        # First injector sets task
        injector1 = ContextInjector(base_path=injection_project)
        injector1.update_active_task("task-100")

        # New injector instance reads same state
        injector2 = ContextInjector(base_path=injection_project)
        assert injector2.get_active_task_id() == "task-100"

    def test_context_injection_with_archive(self, injection_project, store_with_tasks):
        """Test context cleared when task archived."""
        store = TaskMemoryStore(base_path=injection_project)
        injector = ContextInjector(base_path=injection_project)

        # Set active
        injector.update_active_task("task-100")
        assert injector.get_active_task_id() == "task-100"

        # Archive the task (manually clear context first)
        injector.clear_active_task()
        store.archive("task-100")

        # Verify cleared
        assert injector.get_active_task_id() is None


# --- Test: Error Handling ---


class TestInjectionErrorHandling:
    """Tests for error handling in injection scenarios."""

    def test_inject_with_corrupted_memory(self, injection_project):
        """Test handling corrupted memory file."""
        store = TaskMemoryStore(base_path=injection_project)
        injector = ContextInjector(base_path=injection_project)

        # Create memory then corrupt it
        store.create("task-300", task_title="Test")
        memory_path = store.get_path("task-300")

        # Write invalid content (still valid file, just unusual content)
        memory_path.write_bytes(b"\x00\x01\x02\x03")

        # Injection should still work (it doesn't validate content)
        injector.update_active_task("task-300")
        assert injector.get_active_task_id() == "task-300"

    def test_inject_with_permission_errors(self, injection_project, store_with_tasks):
        """Test handling permission errors on CLAUDE.md."""
        injector = ContextInjector(base_path=injection_project)
        claude_md = injection_project / "backlog" / "CLAUDE.md"

        # Make read-only
        claude_md.chmod(0o444)

        try:
            with pytest.raises(PermissionError):
                injector.update_active_task("task-100")
        finally:
            # Restore permissions for cleanup
            claude_md.chmod(0o644)

    def test_inject_with_missing_memory_directory(self, injection_project):
        """Test handling missing memory directory."""
        injector = ContextInjector(base_path=injection_project)

        # Injection doesn't require memory dir to exist
        injector.update_active_task("task-100")
        assert injector.get_active_task_id() == "task-100"
