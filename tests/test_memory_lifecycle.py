"""Tests for LifecycleManager component."""

import pytest
from specify_cli.memory import TaskMemoryStore
from specify_cli.memory.lifecycle import LifecycleManager


@pytest.fixture
def temp_project(tmp_path):
    """Create temporary project structure with templates."""
    # Create directory structure
    backlog_dir = tmp_path / "backlog" / "memory"
    archive_dir = backlog_dir / "archive"
    template_dir = tmp_path / "templates" / "memory"

    backlog_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)
    template_dir.mkdir(parents=True)

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

    return tmp_path


@pytest.fixture
def store(temp_project):
    """Create TaskMemoryStore instance."""
    return TaskMemoryStore(base_path=temp_project)


@pytest.fixture
def manager(store):
    """Create LifecycleManager instance."""
    return LifecycleManager(store=store)


class TestLifecycleManagerInitialization:
    """Tests for LifecycleManager initialization."""

    def test_init_with_default_store(self):
        """Test initialization with default store."""
        manager = LifecycleManager()
        assert manager.store is not None
        assert isinstance(manager.store, TaskMemoryStore)

    def test_init_with_custom_store(self, store):
        """Test initialization with custom store."""
        manager = LifecycleManager(store=store)
        assert manager.store is store


class TestStateNormalization:
    """Tests for state name normalization."""

    def test_normalize_to_do(self, manager):
        """Test normalization of To Do state."""
        assert manager._normalize_state("To Do") == "to_do"
        assert manager._normalize_state("to do") == "to_do"
        assert manager._normalize_state("TO DO") == "to_do"

    def test_normalize_in_progress(self, manager):
        """Test normalization of In Progress state."""
        assert manager._normalize_state("In Progress") == "in_progress"
        assert manager._normalize_state("in progress") == "in_progress"
        assert manager._normalize_state("IN PROGRESS") == "in_progress"

    def test_normalize_done(self, manager):
        """Test normalization of Done state."""
        assert manager._normalize_state("Done") == "done"
        assert manager._normalize_state("done") == "done"
        assert manager._normalize_state("DONE") == "done"

    def test_normalize_archive(self, manager):
        """Test normalization of Archive state."""
        assert manager._normalize_state("Archive") == "archive"
        assert manager._normalize_state("archive") == "archive"

    def test_normalize_with_hyphens(self, manager):
        """Test normalization of states with hyphens."""
        assert manager._normalize_state("In-Progress") == "in_progress"
        assert manager._normalize_state("to-do") == "to_do"


class TestTaskStartTransition:
    """Tests for To Do → In Progress transition."""

    def test_task_start_creates_memory(self, manager):
        """Test that starting task creates memory file."""
        task_id = "task-375"
        manager.on_state_change(task_id, "To Do", "In Progress", "Test Task")

        # Verify memory file created
        memory_path = manager.store.get_path(task_id)
        assert memory_path.exists()

        # Verify content
        content = manager.store.read(task_id)
        assert task_id in content
        assert "Test Task" in content

    def test_task_start_with_existing_memory(self, manager):
        """Test that starting task with existing memory doesn't fail."""
        task_id = "task-375"

        # Create memory manually
        manager.store.create(task_id, task_title="Existing")

        # Should not raise error
        manager.on_state_change(task_id, "To Do", "In Progress", "Test Task")

        # Memory should still exist
        assert manager.store.exists(task_id)

    def test_task_start_updates_claude_md(self, manager, temp_project):
        """Test that starting task updates backlog/CLAUDE.md."""
        task_id = "task-375"
        claude_md = temp_project / "backlog" / "CLAUDE.md"

        # Start task
        manager.on_state_change(task_id, "To Do", "In Progress", "Test Task")

        # Verify CLAUDE.md updated
        assert claude_md.exists()
        content = claude_md.read_text()
        assert f"@import memory/{task_id}.md" in content

    def test_task_start_without_title(self, manager):
        """Test starting task without title."""
        task_id = "task-375"
        manager.on_state_change(task_id, "To Do", "In Progress")

        # Should still create memory
        assert manager.store.exists(task_id)


class TestTaskCompleteTransition:
    """Tests for In Progress → Done transition."""

    def test_task_complete_archives_memory(self, manager):
        """Test that completing task archives memory file."""
        task_id = "task-375"

        # Create and start task
        manager.store.create(task_id, task_title="Test")

        # Complete task
        manager.on_state_change(task_id, "In Progress", "Done")

        # Verify archived
        assert not manager.store.exists(task_id)
        assert manager.store.exists(task_id, check_archive=True)

    def test_task_complete_without_memory(self, manager):
        """Test completing task without memory doesn't fail."""
        task_id = "task-375"

        # Should not raise error
        manager.on_state_change(task_id, "In Progress", "Done")

    def test_task_complete_clears_claude_md(self, manager, temp_project):
        """Test that completing task clears CLAUDE.md import."""
        task_id = "task-375"
        claude_md = temp_project / "backlog" / "CLAUDE.md"

        # Start task (creates import)
        manager.on_state_change(task_id, "To Do", "In Progress", "Test")

        # Complete task
        manager.on_state_change(task_id, "In Progress", "Done")

        # Verify import cleared
        content = claude_md.read_text()
        assert f"@import memory/{task_id}.md" not in content

    def test_task_complete_preserves_content(self, manager):
        """Test that archiving preserves memory content."""
        task_id = "task-375"

        # Create and add content
        manager.store.create(task_id, task_title="Test")
        manager.store.append(task_id, "Important notes")
        original_content = manager.store.read(task_id)

        # Complete task
        manager.on_state_change(task_id, "In Progress", "Done")

        # Verify content preserved in archive
        archive_path = manager.store.archive_dir / f"{task_id}.md"
        archived_content = archive_path.read_text()
        assert archived_content == original_content


class TestTaskArchiveTransition:
    """Tests for Done → Archive transition."""

    def test_task_archive_deletes_memory(self, manager):
        """Test that archiving task deletes memory file permanently."""
        task_id = "task-375"

        # Create, complete, and archive
        manager.store.create(task_id, task_title="Test")
        manager.store.archive(task_id)

        # Archive task
        manager.on_state_change(task_id, "Done", "Archive")

        # Verify deleted from archive
        assert not manager.store.exists(task_id)
        assert not manager.store.exists(task_id, check_archive=True)

    def test_task_archive_without_memory(self, manager):
        """Test archiving task without memory doesn't fail."""
        task_id = "task-375"

        # Should not raise error
        manager.on_state_change(task_id, "Done", "Archive")


class TestTaskReopenTransition:
    """Tests for Done → In Progress transition."""

    def test_task_reopen_restores_memory(self, manager):
        """Test that reopening task restores memory from archive."""
        task_id = "task-375"

        # Create, add content, and archive
        manager.store.create(task_id, task_title="Test")
        manager.store.append(task_id, "Important notes")
        original_content = manager.store.read(task_id)
        manager.store.archive(task_id)

        # Reopen task
        manager.on_state_change(task_id, "Done", "In Progress")

        # Verify restored (file moved from archive to active)
        assert manager.store.exists(task_id)
        # Check that archive no longer has the file
        archive_path = manager.store.archive_dir / f"{task_id}.md"
        assert not archive_path.exists()

        # Verify content preserved
        restored_content = manager.store.read(task_id)
        assert restored_content == original_content

    def test_task_reopen_without_archive(self, manager):
        """Test reopening task without archived memory doesn't fail."""
        task_id = "task-375"

        # Should not raise error
        manager.on_state_change(task_id, "Done", "In Progress")

    def test_task_reopen_with_existing_active(self, manager):
        """Test reopening when active memory exists doesn't fail."""
        task_id = "task-375"

        # Create active memory
        manager.store.create(task_id, task_title="Test")

        # Also create archived (simulate conflict)
        manager.store.archive(task_id)
        manager.store.create(task_id, task_title="New")

        # Should not raise error (logs warning)
        manager.on_state_change(task_id, "Done", "In Progress")

    def test_task_reopen_updates_claude_md(self, manager, temp_project):
        """Test that reopening task updates CLAUDE.md."""
        task_id = "task-375"
        claude_md = temp_project / "backlog" / "CLAUDE.md"

        # Create, archive, and reopen
        manager.store.create(task_id, task_title="Test")
        manager.store.archive(task_id)
        manager.on_state_change(task_id, "Done", "In Progress")

        # Verify CLAUDE.md updated
        content = claude_md.read_text()
        assert f"@import memory/{task_id}.md" in content


class TestTaskResetTransition:
    """Tests for In Progress → To Do transition."""

    def test_task_reset_deletes_memory(self, manager):
        """Test that resetting task deletes memory file."""
        task_id = "task-375"

        # Create memory
        manager.store.create(task_id, task_title="Test")

        # Reset task
        manager.on_state_change(task_id, "In Progress", "To Do")

        # Verify deleted
        assert not manager.store.exists(task_id)

    def test_task_reset_without_memory(self, manager):
        """Test resetting task without memory doesn't fail."""
        task_id = "task-375"

        # Should not raise error
        manager.on_state_change(task_id, "In Progress", "To Do")


class TestUnsupportedTransitions:
    """Tests for transitions that don't trigger memory operations."""

    def test_to_do_to_done(self, manager):
        """Test To Do → Done doesn't trigger operations."""
        task_id = "task-375"

        # Should not raise error or create files
        manager.on_state_change(task_id, "To Do", "Done")

        assert not manager.store.exists(task_id)

    def test_archive_to_done(self, manager):
        """Test Archive → Done doesn't trigger operations."""
        task_id = "task-375"

        # Should not raise error
        manager.on_state_change(task_id, "Archive", "Done")

    def test_in_progress_to_archive(self, manager):
        """Test In Progress → Archive doesn't trigger operations."""
        task_id = "task-375"

        # Create memory
        manager.store.create(task_id, task_title="Test")

        # Transition directly to archive (unusual)
        manager.on_state_change(task_id, "In Progress", "Archive")

        # Memory should still exist (no automatic delete)
        assert manager.store.exists(task_id)


class TestClaudeMdManagement:
    """Tests for CLAUDE.md import management."""

    def test_update_active_task_import(self, manager, temp_project):
        """Test updating CLAUDE.md with active task import."""
        task_id = "task-375"
        claude_md = temp_project / "backlog" / "CLAUDE.md"

        manager.update_active_task_import(task_id)

        assert claude_md.exists()
        content = claude_md.read_text()
        assert f"@import memory/{task_id}.md" in content

    def test_clear_active_task_import(self, manager, temp_project):
        """Test clearing CLAUDE.md import."""
        task_id = "task-375"
        claude_md = temp_project / "backlog" / "CLAUDE.md"

        # Add import
        manager.update_active_task_import(task_id)

        # Clear import
        manager.update_active_task_import(None)

        content = claude_md.read_text()
        assert f"@import memory/{task_id}.md" not in content

    def test_replace_active_task_import(self, manager, temp_project):
        """Test replacing one task import with another."""
        claude_md = temp_project / "backlog" / "CLAUDE.md"

        # Add first task
        manager.update_active_task_import("task-375")

        # Replace with second task
        manager.update_active_task_import("task-376")

        content = claude_md.read_text()
        assert "@import memory/task-375.md" not in content
        assert "@import memory/task-376.md" in content

    def test_create_claude_md_if_missing(self, manager, temp_project):
        """Test that CLAUDE.md is created if it doesn't exist."""
        claude_md = temp_project / "backlog" / "CLAUDE.md"

        # Ensure it doesn't exist
        if claude_md.exists():
            claude_md.unlink()

        # Update import
        manager.update_active_task_import("task-375")

        # Verify created
        assert claude_md.exists()

    def test_preserve_other_content_in_claude_md(self, manager, temp_project):
        """Test that updating import preserves other CLAUDE.md content."""
        claude_md = temp_project / "backlog" / "CLAUDE.md"

        # Create with existing content
        original_content = """# Backlog Context

Some important documentation here.

## Guidelines

Follow these rules.
"""
        claude_md.parent.mkdir(parents=True, exist_ok=True)
        claude_md.write_text(original_content)

        # Add import
        manager.update_active_task_import("task-375")

        content = claude_md.read_text()
        assert "@import memory/task-375.md" in content
        assert "Some important documentation here" in content
        assert "## Guidelines" in content


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_multiple_transitions_same_task(self, manager):
        """Test multiple transitions on same task."""
        task_id = "task-375"

        # Start task
        manager.on_state_change(task_id, "To Do", "In Progress", "Test")
        assert manager.store.exists(task_id)

        # Complete task
        manager.on_state_change(task_id, "In Progress", "Done")
        assert manager.store.exists(task_id, check_archive=True)

        # Reopen task
        manager.on_state_change(task_id, "Done", "In Progress")
        assert manager.store.exists(task_id)

        # Complete again
        manager.on_state_change(task_id, "In Progress", "Done")
        assert manager.store.exists(task_id, check_archive=True)

    def test_case_insensitive_state_transitions(self, manager):
        """Test that state transitions are case-insensitive."""
        task_id = "task-375"

        # Mixed case states
        manager.on_state_change(task_id, "to do", "in progress", "Test")
        assert manager.store.exists(task_id)

        manager.on_state_change(task_id, "IN PROGRESS", "DONE")
        assert manager.store.exists(task_id, check_archive=True)

    def test_unicode_task_title(self, manager):
        """Test handling of unicode task titles."""
        task_id = "task-375"

        manager.on_state_change(task_id, "To Do", "In Progress", "测试任务 🚀")

        content = manager.store.read(task_id)
        assert "测试任务 🚀" in content

    def test_concurrent_task_transitions(self, manager):
        """Test handling multiple tasks transitioning."""
        # Start multiple tasks
        for i in range(5):
            task_id = f"task-{370 + i}"
            manager.on_state_change(task_id, "To Do", "In Progress", f"Task {i}")

        # Verify all created
        for i in range(5):
            task_id = f"task-{370 + i}"
            assert manager.store.exists(task_id)
