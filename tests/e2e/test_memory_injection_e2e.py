"""E2E Tests for Agent Context Injection.

This module tests the injection of task memory into agent context through:
- CLAUDE.md @import directives
- MCP resource access
- Manual file reading fallback
"""

import pytest
from specify_cli.memory import TaskMemoryStore, LifecycleManager
from specify_cli.memory.injector import ContextInjector
from specify_cli.memory.mcp import register_memory_resources


@pytest.fixture
def injection_project(tmp_path):
    """Create project structure for injection testing."""
    # Create directories
    backlog_dir = tmp_path / "backlog"
    memory_dir = backlog_dir / "memory"
    archive_dir = memory_dir / "archive"
    template_dir = tmp_path / "templates" / "memory"
    claude_dir = tmp_path / ".claude"

    backlog_dir.mkdir(parents=True)
    memory_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)
    template_dir.mkdir(parents=True)
    claude_dir.mkdir(parents=True)

    # Create template
    template_content = """# Task Memory: {task_id}

**Created**: {created_date}
**Last Updated**: {updated_date}
**Task**: {task_title}

## Context
{task_title} implementation context.

## Key Decisions
- Decision tracking

## Approaches Tried
- Approach documentation

## Open Questions
- Question tracking

## Resources
- Resource links

## Notes
- Implementation notes
"""
    (template_dir / "default.md").write_text(template_content)

    # Create CLAUDE.md
    claude_md = claude_dir / "CLAUDE.md"
    claude_md.write_text("""# Project Instructions

This is a test project for context injection.

## Task Memory

@import backlog/memory/active-tasks.md

## Architecture

Project architecture documentation.
""")

    return tmp_path


@pytest.fixture
def injector(injection_project):
    """Create ContextInjector instance."""
    return ContextInjector(project_root=injection_project)


@pytest.fixture
def store(injection_project):
    """Create TaskMemoryStore instance."""
    return TaskMemoryStore(base_path=injection_project)


@pytest.fixture
def manager(store):
    """Create LifecycleManager instance."""
    return LifecycleManager(store=store)


class TestCLAUDEMDImport:
    """Tests for CLAUDE.md @import injection."""

    def test_inject_single_active_task(self, manager, injector, injection_project):
        """Test injecting single active task memory into CLAUDE.md."""
        task_id = "task-100"

        # Create active task
        manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Feature A",
        )

        # Inject into CLAUDE.md
        injector.inject_active_tasks()

        # Verify active-tasks.md created
        active_tasks_path = injection_project / "backlog" / "memory" / "active-tasks.md"
        assert active_tasks_path.exists(), "active-tasks.md should be created"

        # Verify content includes task
        content = active_tasks_path.read_text()
        assert task_id in content, "Task ID should be in active-tasks.md"
        assert "Feature A" in content, "Task title should be in active-tasks.md"

    def test_inject_multiple_active_tasks(self, manager, injector, injection_project):
        """Test injecting multiple active tasks."""
        tasks = [
            ("task-101", "Feature B"),
            ("task-102", "Feature C"),
            ("task-103", "Feature D"),
        ]

        # Create multiple active tasks
        for task_id, title in tasks:
            manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=title,
            )

        # Inject
        injector.inject_active_tasks()

        # Verify all tasks in active-tasks.md
        active_tasks_path = injection_project / "backlog" / "memory" / "active-tasks.md"
        content = active_tasks_path.read_text()

        for task_id, title in tasks:
            assert task_id in content, f"{task_id} should be in active-tasks.md"
            assert title in content, f"{title} should be in active-tasks.md"

    def test_inject_updates_on_state_change(self, manager, injector, injection_project):
        """Test that injection updates when task state changes."""
        task_id = "task-104"

        # Create task
        manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Feature E",
        )
        injector.inject_active_tasks()

        # Verify task present
        active_tasks_path = injection_project / "backlog" / "memory" / "active-tasks.md"
        content = active_tasks_path.read_text()
        assert task_id in content

        # Complete task (archive)
        manager.on_state_change(
            task_id=task_id,
            old_state="In Progress",
            new_state="Done",
            task_title="Feature E",
        )
        injector.inject_active_tasks()

        # Verify task removed from active-tasks.md
        content = active_tasks_path.read_text()
        assert task_id not in content, "Completed task should be removed"

    def test_inject_preserves_claude_md_content(
        self, manager, injector, injection_project
    ):
        """Test that injection preserves existing CLAUDE.md content."""
        claude_md = injection_project / ".claude" / "CLAUDE.md"

        # Create task and inject
        manager.on_state_change(
            task_id="task-105",
            old_state="To Do",
            new_state="In Progress",
            task_title="Feature F",
        )
        injector.inject_active_tasks()

        # Verify original content preserved
        updated_content = claude_md.read_text()
        assert "This is a test project" in updated_content
        assert "Architecture" in updated_content
        assert "@import backlog/memory/active-tasks.md" in updated_content

    def test_inject_empty_active_tasks(self, injector, injection_project):
        """Test injecting when no active tasks exist."""
        # Inject with no active tasks
        injector.inject_active_tasks()

        # Verify active-tasks.md created but empty/minimal
        active_tasks_path = injection_project / "backlog" / "memory" / "active-tasks.md"
        assert active_tasks_path.exists()

        content = active_tasks_path.read_text()
        assert "No active tasks" in content or len(content.strip()) < 100

    def test_inject_handles_missing_claude_md(
        self, manager, injector, injection_project
    ):
        """Test injection when CLAUDE.md doesn't exist."""
        # Remove CLAUDE.md
        claude_md = injection_project / ".claude" / "CLAUDE.md"
        claude_md.unlink()

        # Create task and inject
        manager.on_state_change(
            task_id="task-106",
            old_state="To Do",
            new_state="In Progress",
            task_title="Feature G",
        )

        # Should handle gracefully (create or skip)
        injector.inject_active_tasks()

        # Verify active-tasks.md still created
        active_tasks_path = injection_project / "backlog" / "memory" / "active-tasks.md"
        assert active_tasks_path.exists()

    def test_inject_with_task_content_updates(
        self, manager, store, injector, injection_project
    ):
        """Test that content updates to tasks are reflected in injection."""
        task_id = "task-107"

        # Create task
        manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Feature H",
        )

        # Add content
        store.append(task_id, "Key decision: Use PostgreSQL")
        store.append(task_id, "Tried approach: Redis caching")

        # Inject
        injector.inject_active_tasks()

        # Verify content in active-tasks.md
        active_tasks_path = injection_project / "backlog" / "memory" / "active-tasks.md"
        content = active_tasks_path.read_text()

        # Should include task reference, content may be summarized or linked
        assert task_id in content


class TestMCPResourceAccess:
    """Tests for MCP resource-based memory access."""

    def test_register_memory_resources(self, store, manager, injection_project):
        """Test registering task memories as MCP resources."""
        # Create tasks
        tasks = [
            ("task-200", "Backend Task"),
            ("task-201", "Frontend Task"),
        ]

        for task_id, title in tasks:
            manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=title,
            )

        # Register resources
        resources = register_memory_resources(project_root=injection_project)

        # Verify resources created
        assert len(resources) >= 2, "Should have resources for active tasks"

        # Verify resource structure
        task_ids = [r["uri"].split("/")[-1].replace(".md", "") for r in resources]
        assert "task-200" in task_ids
        assert "task-201" in task_ids

    def test_mcp_server_list_resources(self, store, manager, injection_project):
        """Test MCP server lists available memory resources."""
        # Create tasks
        manager.on_state_change(
            task_id="task-202",
            old_state="To Do",
            new_state="In Progress",
            task_title="Test Task",
        )

        # Create MCP server (returns resource list)
        resources = register_memory_resources(project_root=injection_project)

        # Verify at least one resource
        assert len(resources) > 0

        # Verify resource has required fields
        resource = resources[0]
        assert "uri" in resource
        assert "name" in resource
        assert "memory://" in resource["uri"]

    def test_mcp_server_read_resource(self, store, manager, injection_project):
        """Test reading memory content via MCP resource."""
        task_id = "task-203"

        # Create task with content
        manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="MCP Read Test",
        )
        store.append(task_id, "MCP accessible content")

        # Read via resource URI
        memory_path = store.get_path(task_id)
        content = memory_path.read_text()

        # Verify content accessible
        assert "MCP accessible content" in content

    def test_mcp_server_archive_resources(self, store, manager, injection_project):
        """Test that archived memories are available as resources."""
        task_id = "task-204"

        # Create and archive
        manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Archive Resource Test",
        )
        manager.on_state_change(
            task_id=task_id,
            old_state="In Progress",
            new_state="Done",
            task_title="Archive Resource Test",
        )

        # Register resources (should include archives)
        resources = register_memory_resources(
            project_root=injection_project, include_archive=True
        )

        # Verify archived resource exists
        archived_uris = [r["uri"] for r in resources if "archive" in r["uri"]]
        assert len(archived_uris) > 0, "Should have archived resources"

    def test_mcp_resource_uri_format(self, store, manager, injection_project):
        """Test MCP resource URI format correctness."""
        task_id = "task-205"

        # Create task
        manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="URI Test",
        )

        # Register resources
        resources = register_memory_resources(project_root=injection_project)

        # Find our task's resource
        task_resource = next((r for r in resources if task_id in r["uri"]), None)

        assert task_resource is not None
        assert task_resource["uri"].startswith("memory://")
        assert task_id in task_resource["uri"]

    def test_mcp_server_handles_no_memories(self, injection_project):
        """Test MCP server when no memories exist."""
        # Register resources with no tasks
        resources = register_memory_resources(project_root=injection_project)

        # Should return empty list or placeholder
        assert isinstance(resources, list)


class TestManualFileReadFallback:
    """Tests for manual file reading as fallback mechanism."""

    def test_manual_read_active_memory(self, manager, store, injection_project):
        """Test manually reading active task memory file."""
        task_id = "task-300"

        # Create task
        manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Manual Read Test",
        )
        store.append(task_id, "Manual read content")

        # Manual read (as agent would)
        memory_path = injection_project / "backlog" / "memory" / f"{task_id}.md"
        assert memory_path.exists(), "Memory file should be readable"

        content = memory_path.read_text()
        assert "Manual read content" in content

    def test_manual_read_archived_memory(self, manager, store, injection_project):
        """Test manually reading archived task memory."""
        task_id = "task-301"

        # Create and archive
        manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Archive Read Test",
        )
        store.append(task_id, "Archived content")
        manager.on_state_change(
            task_id=task_id,
            old_state="In Progress",
            new_state="Done",
            task_title="Archive Read Test",
        )

        # Manual read from archive
        archive_path = (
            injection_project / "backlog" / "memory" / "archive" / f"{task_id}.md"
        )
        assert archive_path.exists()

        content = archive_path.read_text()
        assert "Archived content" in content

    def test_manual_list_all_memories(self, manager, injection_project):
        """Test manually listing all memory files."""
        # Create multiple tasks
        tasks = [f"task-{310 + i}" for i in range(5)]
        for task_id in tasks:
            manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=f"Task {task_id}",
            )

        # Manual list (as agent would)
        memory_dir = injection_project / "backlog" / "memory"
        memory_files = list(memory_dir.glob("task-*.md"))

        assert len(memory_files) == 5
        for memory_file in memory_files:
            assert memory_file.stem in tasks

    def test_manual_search_memory_content(self, manager, store, injection_project):
        """Test manually searching memory files for content."""
        # Create tasks with specific content
        manager.on_state_change(
            task_id="task-320",
            old_state="To Do",
            new_state="In Progress",
            task_title="Search Test 1",
        )
        store.append("task-320", "Uses PostgreSQL database")

        manager.on_state_change(
            task_id="task-321",
            old_state="To Do",
            new_state="In Progress",
            task_title="Search Test 2",
        )
        store.append("task-321", "Uses MongoDB database")

        # Manual search (grep-like)
        memory_dir = injection_project / "backlog" / "memory"
        matches = []

        for memory_file in memory_dir.glob("task-*.md"):
            content = memory_file.read_text()
            if "PostgreSQL" in content:
                matches.append(memory_file.stem)

        assert "task-320" in matches
        assert "task-321" not in matches


class TestContextInjectionIntegration:
    """Integration tests for full context injection workflow."""

    def test_full_workflow_create_inject_read(
        self, manager, injector, store, injection_project
    ):
        """Test complete workflow: create task → inject context → agent reads."""
        task_id = "task-400"

        # Step 1: Create task (developer action)
        manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Full Workflow Test",
        )

        # Step 2: Developer adds context
        store.append(task_id, "Key decision: Use FastAPI framework")
        store.append(task_id, "Open question: How to handle auth?")

        # Step 3: Inject into CLAUDE.md (automated)
        injector.inject_active_tasks()

        # Step 4: Agent reads via @import (simulated)
        active_tasks_path = injection_project / "backlog" / "memory" / "active-tasks.md"
        assert active_tasks_path.exists()

        content = active_tasks_path.read_text()
        assert task_id in content

        # Step 5: Agent reads full memory (simulated)
        memory_content = store.read(task_id)
        assert "Use FastAPI framework" in memory_content
        assert "How to handle auth?" in memory_content

    def test_multi_agent_context_sharing(
        self, manager, injector, store, injection_project
    ):
        """Test multiple agents accessing same task context."""
        task_id = "task-401"

        # Setup: Create task with rich context
        manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Multi-Agent Task",
        )

        store.append(task_id, "Backend: Implement REST API")
        store.append(task_id, "Frontend: Create UI components")
        store.append(task_id, "QA: Write E2E tests")

        injector.inject_active_tasks()

        # Simulate multiple agents reading same context
        agents = ["backend-engineer", "frontend-engineer", "qa-engineer"]
        for agent in agents:
            # Each agent reads memory
            content = store.read(task_id)
            assert content is not None
            assert "Multi-Agent Task" in content

            # Each agent can append their perspective
            store.append(task_id, f"{agent}: Reviewed task")

        # Verify all agent notes present
        final_content = store.read(task_id)
        for agent in agents:
            assert f"{agent}: Reviewed task" in final_content

    def test_context_persistence_across_sessions(
        self, manager, injector, store, injection_project
    ):
        """Test that context persists across development sessions."""
        task_id = "task-402"

        # Session 1: Create and add initial context
        manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Persistence Test",
        )
        store.append(task_id, "Session 1: Initial implementation")
        injector.inject_active_tasks()

        # Simulate session end (agent context cleared)
        # ...

        # Session 2: Agent context reloaded
        injector.inject_active_tasks()

        # Verify previous context accessible
        content = store.read(task_id)
        assert "Session 1: Initial implementation" in content

        # Add more context
        store.append(task_id, "Session 2: Continued work")

        # Session 3: Verify full history
        content = store.read(task_id)
        assert "Session 1: Initial implementation" in content
        assert "Session 2: Continued work" in content

    def test_context_injection_performance(self, manager, injector, injection_project):
        """Test performance of context injection with many active tasks."""
        import time

        # Create 50 active tasks
        task_ids = [f"task-{500 + i}" for i in range(50)]

        for task_id in task_ids:
            manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=f"Task {task_id}",
            )

        # Time injection
        start = time.time()
        injector.inject_active_tasks()
        duration = time.time() - start

        # Should be fast (<100ms)
        assert duration < 0.1, f"Injection took {duration}s, should be <0.1s"

        # Verify all tasks injected
        active_tasks_path = injection_project / "backlog" / "memory" / "active-tasks.md"
        content = active_tasks_path.read_text()

        # Spot check a few tasks
        assert "task-500" in content
        assert "task-525" in content
        assert "task-549" in content


class TestInjectionErrorHandling:
    """Tests for error handling in context injection."""

    def test_inject_with_corrupted_memory(
        self, manager, store, injector, injection_project
    ):
        """Test injection when memory file is corrupted."""
        task_id = "task-600"

        # Create task
        manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Corruption Test",
        )

        # Corrupt memory file
        memory_path = store.get_path(task_id)
        memory_path.write_bytes(b"\x00\x01\x02 INVALID")

        # Injection should handle gracefully
        injector.inject_active_tasks()

        # Should still create active-tasks.md
        active_tasks_path = injection_project / "backlog" / "memory" / "active-tasks.md"
        assert active_tasks_path.exists()

    def test_inject_with_permission_errors(self, manager, injector, injection_project):
        """Test injection when file permissions prevent write."""
        task_id = "task-601"

        # Create task
        manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Permission Test",
        )

        # Make active-tasks.md read-only
        import os

        active_tasks_path = injection_project / "backlog" / "memory" / "active-tasks.md"
        active_tasks_path.touch()
        os.chmod(active_tasks_path, 0o444)

        try:
            # Injection should handle permission error
            with pytest.raises((PermissionError, OSError)):
                injector.inject_active_tasks()
        finally:
            # Restore permissions
            os.chmod(active_tasks_path, 0o644)

    def test_inject_with_missing_memory_directory(self, injector, injection_project):
        """Test injection when memory directory is missing."""
        import shutil

        # Remove memory directory
        memory_dir = injection_project / "backlog" / "memory"
        if memory_dir.exists():
            shutil.rmtree(memory_dir)

        # Injection should handle gracefully (recreate or skip)
        injector.inject_active_tasks()

        # Verify directory recreated or error handled
        # (behavior depends on implementation)
