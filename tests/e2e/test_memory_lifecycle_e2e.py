"""E2E Tests for Task Memory Lifecycle.

This module tests the complete lifecycle of task memory files from creation
through archival and deletion. Tests cover state transitions, rollback scenarios,
concurrent operations, and CLAUDE.md integration.
"""

import pytest
from specify_cli.memory import TaskMemoryStore, LifecycleManager
from specify_cli.memory.injector import ContextInjector
import shutil


@pytest.fixture
def e2e_project(tmp_path):
    """Create full E2E project structure."""
    # Create directory structure
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

    # Create default template
    template_content = """# Task Memory: {task_id}

**Created**: {created_date}
**Last Updated**: {updated_date}
**Task**: {task_title}

## Context

<!-- Brief description of what this task is about -->

## Key Decisions

<!-- Record important decisions made during implementation -->

## Approaches Tried

<!-- Document approaches attempted and their outcomes -->

## Open Questions

<!-- Track unresolved questions -->

## Resources

<!-- Links to relevant documentation, PRs, discussions -->

## Notes

<!-- Freeform notes section -->
"""
    (template_dir / "default.md").write_text(template_content)

    # Create CLAUDE.md in .claude directory
    claude_md = claude_dir / "CLAUDE.md"
    claude_md.write_text("""# Project Instructions

This is a test project.

## Task Memory

@import backlog/memory/active-tasks.md
""")

    # Create backlog/CLAUDE.md for ContextInjector
    backlog_claude_md = backlog_dir / "CLAUDE.md"
    backlog_claude_md.write_text("""# Backlog Task Management

This is a test project for context injection.

## Task Memory

Task memory files are stored in `backlog/memory/`.
""")

    return tmp_path


@pytest.fixture
def lifecycle_manager(e2e_project):
    """Create lifecycle manager with full project setup."""
    store = TaskMemoryStore(base_path=e2e_project)
    return LifecycleManager(store=store)


@pytest.fixture
def context_injector(e2e_project):
    """Create context injector for CLAUDE.md integration."""
    return ContextInjector(base_path=e2e_project)


class TestTaskMemoryLifecycleE2E:
    """E2E tests for complete task memory lifecycle."""

    def test_full_lifecycle_to_do_to_done_to_archive(
        self, lifecycle_manager, e2e_project
    ):
        """Test complete lifecycle: To Do → In Progress → Done → Archive."""
        task_id = "task-100"
        task_title = "Implement feature X"
        store = lifecycle_manager.store

        # Step 1: To Do → In Progress (create memory)
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title=task_title,
        )

        # Verify memory file created
        memory_path = store.get_path(task_id)
        assert memory_path.exists(), "Memory file should be created"
        content = memory_path.read_text()
        assert task_id in content
        assert task_title in content

        # Step 2: Append some work to memory
        store.append(task_id, "Implemented database schema")
        updated_content = store.read(task_id)
        assert "Implemented database schema" in updated_content

        # Step 3: In Progress → Done (archive memory)
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="In Progress",
            new_state="Done",
            task_title=task_title,
        )

        # Verify memory file archived
        assert not memory_path.exists(), "Memory file should be removed from active"
        archive_path = store.archive_dir / f"{task_id}.md"
        assert archive_path.exists(), "Memory file should be in archive"

        # Verify archived content preserved
        archived_content = archive_path.read_text()
        assert "Implemented database schema" in archived_content

        # Step 4: Done → Archive (delete memory permanently)
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="Done",
            new_state="Archive",
            task_title=task_title,
        )

        # Verify memory file deleted
        assert not archive_path.exists(), "Memory file should be deleted from archive"

    def test_rollback_scenario_done_to_in_progress(
        self, lifecycle_manager, e2e_project
    ):
        """Test rollback: Done → In Progress restores memory from archive."""
        task_id = "task-101"
        task_title = "Fix critical bug"
        store = lifecycle_manager.store

        # Setup: Create and archive a memory
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title=task_title,
        )
        store.append(task_id, "Fixed null pointer exception")

        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="In Progress",
            new_state="Done",
            task_title=task_title,
        )

        # Verify archived
        memory_path = store.get_path(task_id)
        archive_path = store.archive_dir / f"{task_id}.md"
        assert not memory_path.exists()
        assert archive_path.exists()

        # Rollback: Done → In Progress (restore from archive)
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="Done",
            new_state="In Progress",
            task_title=task_title,
        )

        # Verify memory restored
        assert memory_path.exists(), "Memory should be restored to active"
        assert not archive_path.exists(), "Archive should be removed"

        # Verify content preserved
        restored_content = store.read(task_id)
        assert "Fixed null pointer exception" in restored_content

    def test_reset_scenario_in_progress_to_to_do(self, lifecycle_manager, e2e_project):
        """Test reset: In Progress → To Do deletes memory."""
        task_id = "task-102"
        task_title = "Refactor module"
        store = lifecycle_manager.store

        # Create memory
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title=task_title,
        )

        memory_path = store.get_path(task_id)
        assert memory_path.exists()

        # Reset: In Progress → To Do (delete memory)
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="In Progress",
            new_state="To Do",
            task_title=task_title,
        )

        # Verify memory deleted
        assert not memory_path.exists(), "Memory should be deleted on reset"
        archive_path = store.archive_dir / f"{task_id}.md"
        assert not archive_path.exists(), "Memory should not be archived on reset"

    def test_concurrent_multiple_tasks(self, lifecycle_manager, e2e_project):
        """Test lifecycle with multiple concurrent tasks."""
        store = lifecycle_manager.store
        tasks = [
            ("task-200", "Feature A"),
            ("task-201", "Feature B"),
            ("task-202", "Feature C"),
        ]

        # Start all tasks
        for task_id, title in tasks:
            lifecycle_manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title=title,
            )

        # Verify all memories created
        for task_id, _ in tasks:
            memory_path = store.get_path(task_id)
            assert memory_path.exists(), f"Memory for {task_id} should exist"

        # Complete first task
        lifecycle_manager.on_state_change(
            task_id="task-200",
            old_state="In Progress",
            new_state="Done",
            task_title="Feature A",
        )

        # Verify only first task archived
        assert not store.get_path("task-200").exists()
        assert store.get_path("task-201").exists()
        assert store.get_path("task-202").exists()

        # Complete remaining tasks
        for task_id, title in tasks[1:]:
            lifecycle_manager.on_state_change(
                task_id=task_id,
                old_state="In Progress",
                new_state="Done",
                task_title=title,
            )

        # Verify all archived
        for task_id, _ in tasks:
            assert not store.get_path(task_id).exists()
            archive_path = store.archive_dir / f"{task_id}.md"
            assert archive_path.exists()

    def test_error_recovery_missing_template(self, lifecycle_manager, e2e_project):
        """Test error handling when template is missing."""
        task_id = "task-103"

        # Remove template
        template_path = e2e_project / "templates" / "memory" / "default.md"
        template_path.unlink()

        # Attempt to create memory
        with pytest.raises(FileNotFoundError, match="Template not found"):
            lifecycle_manager.on_state_change(
                task_id=task_id,
                old_state="To Do",
                new_state="In Progress",
                task_title="Test Task",
            )

    def test_error_recovery_duplicate_creation(self, lifecycle_manager, e2e_project):
        """Test error handling when creating duplicate memory."""
        task_id = "task-104"
        store = lifecycle_manager.store

        # Create memory
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Test Task",
        )

        # Attempt to create duplicate
        with pytest.raises(FileExistsError, match="already exists"):
            store.create(task_id, task_title="Duplicate")

    def test_memory_content_persistence_across_transitions(
        self, lifecycle_manager, e2e_project
    ):
        """Test that memory content persists through state transitions."""
        task_id = "task-105"
        store = lifecycle_manager.store

        # Create and add content
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Test Persistence",
        )

        # Add multiple entries
        entries = [
            "Decision: Use PostgreSQL for storage",
            "Tried: Redis caching - performance improved 2x",
            "Question: Should we shard database?",
            "Resource: https://example.com/docs",
        ]

        for entry in entries:
            store.append(task_id, entry)

        # Archive
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="In Progress",
            new_state="Done",
            task_title="Test Persistence",
        )

        # Verify all content in archive
        archive_path = store.archive_dir / f"{task_id}.md"
        archived_content = archive_path.read_text()
        for entry in entries:
            assert entry in archived_content, f"Entry should be preserved: {entry}"

        # Restore and verify
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="Done",
            new_state="In Progress",
            task_title="Test Persistence",
        )

        restored_content = store.read(task_id)
        for entry in entries:
            assert entry in restored_content, f"Entry should be restored: {entry}"


class TestCLAUDEMDIntegrationE2E:
    """E2E tests for CLAUDE.md @import integration."""

    def test_claude_md_import_updated_on_state_change(
        self, lifecycle_manager, context_injector, e2e_project
    ):
        """Test that CLAUDE.md @import is updated when tasks change state."""
        task_id = "task-300"
        backlog_claude_md = e2e_project / "backlog" / "CLAUDE.md"

        # Start task (this creates memory and updates CLAUDE.md via lifecycle manager)
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Test Import",
        )

        # Verify CLAUDE.md was updated with @import
        # LifecycleManager uses ContextInjector format: @import ../memory/{task_id}.md
        content = backlog_claude_md.read_text()
        assert f"@import ../memory/{task_id}.md" in content

    def test_claude_md_preserves_existing_content(
        self, lifecycle_manager, context_injector, e2e_project
    ):
        """Test that CLAUDE.md preserves existing content when updating imports."""
        task_id = "task-301"
        backlog_claude_md = e2e_project / "backlog" / "CLAUDE.md"

        # Get original content
        original_content = backlog_claude_md.read_text()
        assert "Backlog Task Management" in original_content

        # Start task
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Test Preservation",
        )

        # Verify original content preserved
        updated_content = backlog_claude_md.read_text()
        assert "Backlog Task Management" in updated_content
        assert "test project for context injection" in updated_content
        # Also verify @import was added (ContextInjector uses ../memory/ format)
        assert f"@import ../memory/{task_id}.md" in updated_content


class TestErrorRecoveryE2E:
    """E2E tests for error recovery scenarios."""

    def test_recovery_from_corrupted_memory_file(self, lifecycle_manager, e2e_project):
        """Test recovery when memory file is corrupted."""
        task_id = "task-400"
        store = lifecycle_manager.store

        # Create memory
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Test Corruption",
        )

        # Corrupt file (write invalid content)
        memory_path = store.get_path(task_id)
        memory_path.write_text("\x00\x01\x02 INVALID BINARY DATA")

        # Should still be able to read (even if corrupted)
        content = store.read(task_id)
        assert content is not None

        # Should be able to archive
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="In Progress",
            new_state="Done",
            task_title="Test Corruption",
        )

        # Verify archived
        archive_path = store.archive_dir / f"{task_id}.md"
        assert archive_path.exists()

    def test_recovery_from_missing_directories(self, e2e_project):
        """Test recovery when memory directories are missing."""
        # Remove directories
        memory_dir = e2e_project / "backlog" / "memory"
        if memory_dir.exists():
            shutil.rmtree(memory_dir)

        # Create store (should recreate directories)
        store = TaskMemoryStore(base_path=e2e_project)

        # Verify directories recreated
        assert store.memory_dir.exists()
        assert store.archive_dir.exists()

        # Should be able to create memory
        path = store.create("task-500", task_title="Test Recovery")
        assert path.exists()

    def test_recovery_from_permission_errors(self, lifecycle_manager, e2e_project):
        """Test handling of permission errors (simulated)."""
        task_id = "task-401"
        store = lifecycle_manager.store

        # Create memory
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Test Permissions",
        )

        memory_path = store.get_path(task_id)

        # Make file read-only
        import os

        os.chmod(memory_path, 0o444)

        try:
            # Attempt to append (should fail gracefully or handle permission error)
            with pytest.raises((PermissionError, OSError)):
                store.append(task_id, "This should fail")
        finally:
            # Restore permissions for cleanup
            os.chmod(memory_path, 0o644)


class TestLifecycleEdgeCases:
    """E2E tests for edge cases in lifecycle management."""

    def test_repeated_state_transitions(self, lifecycle_manager, e2e_project):
        """Test repeated transitions between same states."""
        task_id = "task-600"
        store = lifecycle_manager.store

        # To Do → In Progress
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Test Repeated",
        )
        assert store.exists(task_id)

        # In Progress → To Do (reset)
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="In Progress",
            new_state="To Do",
            task_title="Test Repeated",
        )
        assert not store.exists(task_id)

        # To Do → In Progress again
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Test Repeated",
        )
        assert store.exists(task_id)

    def test_invalid_state_transitions(self, lifecycle_manager, e2e_project):
        """Test handling of invalid state transitions."""
        task_id = "task-601"

        # Attempt invalid transition: To Do → Done (skipping In Progress)
        # This should not create or modify memory
        lifecycle_manager.on_state_change(
            task_id=task_id,
            old_state="To Do",
            new_state="Done",
            task_title="Test Invalid",
        )

        # Should not create memory
        assert not lifecycle_manager.store.exists(task_id)

    def test_empty_task_id(self, lifecycle_manager, e2e_project):
        """Test that empty task IDs are rejected with ValueError."""
        # Empty task IDs are now validated and rejected
        with pytest.raises(ValueError, match="Task ID cannot be empty"):
            lifecycle_manager.store.create("", task_title="Empty ID")

    def test_special_characters_in_task_id(self, lifecycle_manager, e2e_project):
        """Test handling of special characters in task IDs."""
        # Valid task IDs with alphanumeric chars and hyphens are allowed
        valid_task_id = "task-700-with-extra-hyphens"

        lifecycle_manager.on_state_change(
            task_id=valid_task_id,
            old_state="To Do",
            new_state="In Progress",
            task_title="Test Special Chars",
        )

        assert lifecycle_manager.store.exists(valid_task_id)

        # Path traversal characters are blocked
        invalid_task_ids = ["task-../secret", "task-foo/bar", "task-foo\\bar"]
        for invalid_id in invalid_task_ids:
            with pytest.raises(ValueError):
                lifecycle_manager.store.get_path(invalid_id)
