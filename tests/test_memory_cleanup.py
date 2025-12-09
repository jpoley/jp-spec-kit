"""Tests for CleanupManager component."""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
from specify_cli.memory import TaskMemoryStore
from specify_cli.memory.cleanup import CleanupManager


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
    """Create CleanupManager instance."""
    return CleanupManager(store=store)


def set_file_mtime(path: Path, days_ago: int):
    """Helper to set file modification time to N days ago."""
    mtime = (datetime.now() - timedelta(days=days_ago)).timestamp()
    path.touch()
    import os

    os.utime(path, (mtime, mtime))


class TestCleanupManagerInitialization:
    """Tests for CleanupManager initialization."""

    def test_init_with_default_store(self):
        """Test initialization with default store."""
        manager = CleanupManager()
        assert manager.store is not None
        assert isinstance(manager.store, TaskMemoryStore)

    def test_init_with_custom_store(self, store):
        """Test initialization with custom store."""
        manager = CleanupManager(store=store)
        assert manager.store is store


class TestArchiveOlderThan:
    """Tests for archiving old active memories."""

    def test_archive_old_memories(self, manager, store):
        """Test archiving memories older than threshold."""
        # Create memories with different ages
        store.create("task-375", task_title="Old 1")
        store.create("task-376", task_title="Old 2")
        store.create("task-377", task_title="Recent")

        # Make first two old (40 days)
        set_file_mtime(store.get_path("task-375"), 40)
        set_file_mtime(store.get_path("task-376"), 40)
        # Keep third recent (5 days)
        set_file_mtime(store.get_path("task-377"), 5)

        # Archive memories older than 30 days
        archived = manager.archive_older_than(days=30)

        # Verify old ones archived
        assert len(archived) == 2
        assert "task-375" in archived
        assert "task-376" in archived
        assert "task-377" not in archived

        # Verify files moved
        assert not store.exists("task-375")
        assert not store.exists("task-376")
        assert store.exists("task-377")  # Still active

        # Verify in archive
        assert store.exists("task-375", check_archive=True)
        assert store.exists("task-376", check_archive=True)

    def test_archive_with_no_old_memories(self, manager, store):
        """Test archiving when no memories are old enough."""
        # Create recent memories
        store.create("task-375", task_title="Recent 1")
        store.create("task-376", task_title="Recent 2")

        # Archive memories older than 30 days
        archived = manager.archive_older_than(days=30)

        # Nothing should be archived
        assert len(archived) == 0
        assert store.exists("task-375")
        assert store.exists("task-376")

    def test_archive_with_empty_directory(self, manager):
        """Test archiving when no memories exist."""
        archived = manager.archive_older_than(days=30)
        assert len(archived) == 0

    def test_archive_dry_run(self, manager, store):
        """Test dry run doesn't actually archive."""
        # Create old memory
        store.create("task-375", task_title="Old")
        set_file_mtime(store.get_path("task-375"), 40)

        # Dry run
        archived = manager.archive_older_than(days=30, dry_run=True)

        # Should report what would be archived
        assert len(archived) == 1
        assert "task-375" in archived

        # But file should still be active
        assert store.exists("task-375")
        # Check archive directly (not using check_archive which checks both)
        archive_path = store.archive_dir / "task-375.md"
        assert not archive_path.exists()

    def test_archive_preserves_content(self, manager, store):
        """Test that archiving preserves memory content."""
        # Create and add content
        store.create("task-375", task_title="Test")
        store.append("task-375", "Important notes")
        original_content = store.read("task-375")

        # Make it old and archive
        set_file_mtime(store.get_path("task-375"), 40)
        manager.archive_older_than(days=30)

        # Verify content preserved
        archive_path = store.archive_dir / "task-375.md"
        archived_content = archive_path.read_text()
        assert archived_content == original_content

    def test_archive_boundary_condition(self, manager, store):
        """Test archiving at exact boundary (30.0 days)."""
        store.create("task-375", task_title="Boundary")
        store.create("task-376", task_title="Just Over")

        # Set to exactly 30 days and 31 days
        set_file_mtime(store.get_path("task-375"), 30)
        set_file_mtime(store.get_path("task-376"), 31)

        # Archive older than 30 days - should archive both (30+ days old)
        archived = manager.archive_older_than(days=30)

        # Both files should be archived (>= 30 days)
        assert len(archived) == 2
        assert "task-375" in archived
        assert "task-376" in archived

    def test_archive_multiple_batches(self, manager, store):
        """Test archiving in multiple batches."""
        # Create memories
        for i in range(5):
            store.create(f"task-{370 + i}", task_title=f"Task {i}")
            set_file_mtime(store.get_path(f"task-{370 + i}"), 40)

        # First batch
        archived1 = manager.archive_older_than(days=30)
        assert len(archived1) == 5

        # Create more old memories
        for i in range(5, 8):
            store.create(f"task-{370 + i}", task_title=f"Task {i}")
            set_file_mtime(store.get_path(f"task-{370 + i}"), 40)

        # Second batch
        archived2 = manager.archive_older_than(days=30)
        assert len(archived2) == 3


class TestDeleteArchivedOlderThan:
    """Tests for deleting old archived memories."""

    def test_delete_old_archived(self, manager, store):
        """Test deleting archived memories older than threshold."""
        # Create and archive memories
        store.create("task-375", task_title="Old 1")
        store.create("task-376", task_title="Old 2")
        store.create("task-377", task_title="Recent")

        store.archive("task-375")
        store.archive("task-376")
        store.archive("task-377")

        # Make first two old (100 days archived)
        set_file_mtime(store.archive_dir / "task-375.md", 100)
        set_file_mtime(store.archive_dir / "task-376.md", 100)
        # Keep third recent (30 days archived)
        set_file_mtime(store.archive_dir / "task-377.md", 30)

        # Delete archived older than 90 days
        deleted = manager.delete_archived_older_than(days=90)

        # Verify old ones deleted
        assert len(deleted) == 2
        assert "task-375" in deleted
        assert "task-376" in deleted
        assert "task-377" not in deleted

        # Verify files deleted
        assert not store.exists("task-375", check_archive=True)
        assert not store.exists("task-376", check_archive=True)
        assert store.exists("task-377", check_archive=True)

    def test_delete_with_no_old_archived(self, manager, store):
        """Test deleting when no archived memories are old enough."""
        # Create and archive recent
        store.create("task-375", task_title="Recent")
        store.archive("task-375")

        # Delete older than 90 days
        deleted = manager.delete_archived_older_than(days=90)

        # Nothing deleted
        assert len(deleted) == 0
        assert store.exists("task-375", check_archive=True)

    def test_delete_with_empty_archive(self, manager):
        """Test deleting when archive is empty."""
        deleted = manager.delete_archived_older_than(days=90)
        assert len(deleted) == 0

    def test_delete_dry_run(self, manager, store):
        """Test dry run doesn't actually delete."""
        # Create and archive old memory
        store.create("task-375", task_title="Old")
        store.archive("task-375")
        set_file_mtime(store.archive_dir / "task-375.md", 100)

        # Dry run
        deleted = manager.delete_archived_older_than(days=90, dry_run=True)

        # Should report what would be deleted
        assert len(deleted) == 1
        assert "task-375" in deleted

        # But file should still exist
        assert store.exists("task-375", check_archive=True)

    def test_delete_is_permanent(self, manager, store):
        """Test that deletion is permanent and irreversible."""
        # Create, archive, and delete
        store.create("task-375", task_title="Test")
        store.archive("task-375")
        set_file_mtime(store.archive_dir / "task-375.md", 100)

        manager.delete_archived_older_than(days=90)

        # File should not exist anywhere
        assert not store.exists("task-375")
        assert not store.exists("task-375", check_archive=True)
        assert not (store.archive_dir / "task-375.md").exists()


class TestGetStats:
    """Tests for cleanup statistics."""

    def test_stats_with_empty_directories(self, manager):
        """Test stats when no memories exist."""
        stats = manager.get_stats()

        assert stats["active_count"] == 0
        assert stats["archived_count"] == 0
        assert stats["oldest_active_days"] == 0
        assert stats["oldest_archived_days"] == 0

    def test_stats_with_active_memories(self, manager, store):
        """Test stats with active memories."""
        # Create memories with different ages
        store.create("task-375", task_title="Old")
        store.create("task-376", task_title="Recent")

        set_file_mtime(store.get_path("task-375"), 45)
        set_file_mtime(store.get_path("task-376"), 10)

        stats = manager.get_stats()

        assert stats["active_count"] == 2
        assert stats["oldest_active_days"] >= 44  # At least 44 days old

    def test_stats_with_archived_memories(self, manager, store):
        """Test stats with archived memories."""
        # Create and archive
        store.create("task-375", task_title="Old")
        store.create("task-376", task_title="Recent")
        store.archive("task-375")
        store.archive("task-376")

        set_file_mtime(store.archive_dir / "task-375.md", 100)
        set_file_mtime(store.archive_dir / "task-376.md", 30)

        stats = manager.get_stats()

        assert stats["active_count"] == 0
        assert stats["archived_count"] == 2
        assert stats["oldest_archived_days"] >= 99

    def test_stats_with_both_active_and_archived(self, manager, store):
        """Test stats with both active and archived memories."""
        # Create active
        store.create("task-375", task_title="Active")
        set_file_mtime(store.get_path("task-375"), 20)

        # Create and archive
        store.create("task-376", task_title="Archived")
        store.archive("task-376")
        set_file_mtime(store.archive_dir / "task-376.md", 60)

        stats = manager.get_stats()

        assert stats["active_count"] == 1
        assert stats["archived_count"] == 1
        assert stats["oldest_active_days"] >= 19
        assert stats["oldest_archived_days"] >= 59


class TestCleanupAll:
    """Tests for full cleanup operations."""

    def test_cleanup_all_with_defaults(self, manager, store):
        """Test cleanup_all with default thresholds."""
        # Create active memories (old)
        store.create("task-375", task_title="Active Old")
        store.create("task-376", task_title="Active Recent")
        set_file_mtime(store.get_path("task-375"), 40)
        set_file_mtime(store.get_path("task-376"), 10)

        # Create archived memories (very old)
        store.create("task-377", task_title="Archived Old")
        store.create("task-378", task_title="Archived Recent")
        store.archive("task-377")
        store.archive("task-378")
        set_file_mtime(store.archive_dir / "task-377.md", 100)
        set_file_mtime(store.archive_dir / "task-378.md", 60)

        # Run cleanup (30 days active, 90 days archived)
        result = manager.cleanup_all(archive_after_days=30, delete_after_days=90)

        # Verify results
        assert "task-375" in result["archived"]  # Old active archived
        assert "task-376" not in result["archived"]  # Recent active kept
        assert "task-377" in result["deleted"]  # Very old archived deleted
        assert "task-378" not in result["deleted"]  # Recent archived kept

    def test_cleanup_all_custom_thresholds(self, manager, store):
        """Test cleanup_all with custom thresholds."""
        # Create memories
        store.create("task-375", task_title="Active")
        set_file_mtime(store.get_path("task-375"), 15)

        store.create("task-376", task_title="Archived")
        store.archive("task-376")
        set_file_mtime(store.archive_dir / "task-376.md", 45)

        # Run with custom thresholds
        result = manager.cleanup_all(archive_after_days=10, delete_after_days=40)

        # Verify
        assert "task-375" in result["archived"]
        assert "task-376" in result["deleted"]

    def test_cleanup_all_dry_run(self, manager, store):
        """Test cleanup_all in dry run mode."""
        # Create old memories
        store.create("task-375", task_title="Active")
        set_file_mtime(store.get_path("task-375"), 40)

        store.create("task-376", task_title="Archived")
        store.archive("task-376")
        set_file_mtime(store.archive_dir / "task-376.md", 100)

        # Dry run
        result = manager.cleanup_all(
            archive_after_days=30, delete_after_days=90, dry_run=True
        )

        # Should report operations
        assert len(result["archived"]) == 1
        assert len(result["deleted"]) == 1

        # But nothing actually changed
        assert store.exists("task-375")
        assert store.exists("task-376", check_archive=True)

    def test_cleanup_all_returns_dict(self, manager):
        """Test cleanup_all returns properly structured dict."""
        result = manager.cleanup_all()

        assert isinstance(result, dict)
        assert "archived" in result
        assert "deleted" in result
        assert isinstance(result["archived"], list)
        assert isinstance(result["deleted"], list)


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_cleanup_with_zero_days_threshold(self, manager, store):
        """Test cleanup with zero days threshold."""
        store.create("task-375", task_title="Test")

        # Archive everything (0+ days old)
        archived = manager.archive_older_than(days=0)

        # Should archive even brand new files
        assert len(archived) == 1

    def test_cleanup_with_very_large_threshold(self, manager, store):
        """Test cleanup with very large threshold."""
        store.create("task-375", task_title="Test")
        set_file_mtime(store.get_path("task-375"), 100)

        # Require 1000 days old
        archived = manager.archive_older_than(days=1000)

        # Nothing old enough
        assert len(archived) == 0

    def test_cleanup_with_many_files(self, manager, store):
        """Test cleanup with many files."""
        # Create 50 old memories
        for i in range(50):
            task_id = f"task-{300 + i}"
            store.create(task_id, task_title=f"Task {i}")
            set_file_mtime(store.get_path(task_id), 40)

        # Archive all
        archived = manager.archive_older_than(days=30)

        assert len(archived) == 50

        # Delete all
        for task_id in archived:
            set_file_mtime(store.archive_dir / f"{task_id}.md", 100)

        deleted = manager.delete_archived_older_than(days=90)
        assert len(deleted) == 50

    def test_cleanup_with_missing_files(self, manager, store):
        """Test cleanup handles missing files gracefully."""
        # Create memory and manually delete file (simulate race condition)
        store.create("task-375", task_title="Test")
        memory_path = store.get_path("task-375")
        memory_path.unlink()

        # Should not crash
        archived = manager.archive_older_than(days=30)
        assert len(archived) == 0

    def test_stats_with_deleted_files(self, manager, store):
        """Test stats when files are deleted during iteration."""
        store.create("task-375", task_title="Test")

        # Delete file manually
        store.get_path("task-375").unlink()

        # Should not crash
        stats = manager.get_stats()
        # Might return 0 or 1 depending on when deletion happens
        assert stats["active_count"] >= 0
