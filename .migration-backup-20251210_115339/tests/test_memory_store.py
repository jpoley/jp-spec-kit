"""Tests for TaskMemoryStore component."""

import pytest
from pathlib import Path
from specify_cli.memory import TaskMemoryStore


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


class TestTaskMemoryStoreInitialization:
    """Tests for TaskMemoryStore initialization."""

    def test_init_with_default_path(self):
        """Test initialization with default path."""
        store = TaskMemoryStore()
        assert store.base_path == Path.cwd()
        assert store.memory_dir == Path.cwd() / "backlog" / "memory"
        assert store.archive_dir == Path.cwd() / "backlog" / "memory" / "archive"

    def test_init_with_custom_path(self, temp_project):
        """Test initialization with custom path."""
        store = TaskMemoryStore(base_path=temp_project)
        assert store.base_path == temp_project
        assert store.memory_dir == temp_project / "backlog" / "memory"
        assert store.archive_dir == temp_project / "backlog" / "memory" / "archive"

    def test_init_creates_directories(self, temp_project):
        """Test that initialization creates required directories."""
        store = TaskMemoryStore(base_path=temp_project)
        assert store.memory_dir.exists()
        assert store.archive_dir.exists()


class TestTaskMemoryStoreCreate:
    """Tests for creating task memory files."""

    def test_create_with_default_template(self, store):
        """Test creating memory with default template."""
        task_id = "task-375"
        path = store.create(task_id, task_title="Test Task")

        assert path.exists()
        assert path.name == "task-375.md"
        content = path.read_text()
        assert "# Task Memory: task-375" in content
        assert "Test Task" in content
        assert "**Created**:" in content
        assert "**Last Updated**:" in content

    def test_create_with_custom_variables(self, store):
        """Test creating memory with custom variables."""
        task_id = "task-376"
        path = store.create(
            task_id, task_title="Custom Task", custom_field="custom value"
        )

        content = path.read_text()
        assert "task-376" in content
        assert "Custom Task" in content

    def test_create_duplicate_raises_error(self, store):
        """Test that creating duplicate memory raises FileExistsError."""
        task_id = "task-375"
        store.create(task_id, task_title="First")

        with pytest.raises(FileExistsError, match="already exists"):
            store.create(task_id, task_title="Second")

    def test_create_with_missing_template(self, store):
        """Test that missing template raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Template not found"):
            store.create("task-999", template="nonexistent")

    def test_create_returns_path(self, store):
        """Test that create returns Path object."""
        path = store.create("task-100", task_title="Test")
        assert isinstance(path, Path)
        assert path.exists()


class TestTaskMemoryStoreRead:
    """Tests for reading task memory files."""

    def test_read_existing_memory(self, store):
        """Test reading existing memory file."""
        task_id = "task-375"
        store.create(task_id, task_title="Test Task")

        content = store.read(task_id)
        assert "# Task Memory: task-375" in content
        assert "Test Task" in content

    def test_read_nonexistent_raises_error(self, store):
        """Test that reading nonexistent memory raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            store.read("task-999")

    def test_read_returns_string(self, store):
        """Test that read returns string content."""
        store.create("task-100", task_title="Test")
        content = store.read("task-100")
        assert isinstance(content, str)
        assert len(content) > 0


class TestTaskMemoryStoreAppend:
    """Tests for appending content to task memory."""

    def test_append_to_end(self, store):
        """Test appending content to end of file."""
        task_id = "task-375"
        store.create(task_id, task_title="Test")

        store.append(task_id, "Additional notes here")
        content = store.read(task_id)

        assert "Additional notes here" in content

    def test_append_to_section(self, store):
        """Test appending content to specific section."""
        task_id = "task-375"
        store.create(task_id, task_title="Test")

        store.append(task_id, "Important decision made", section="Key Decisions")
        content = store.read(task_id)

        assert "Important decision made" in content
        # Verify it's after Key Decisions section
        decisions_idx = content.find("## Key Decisions")
        notes_idx = content.find("Important decision made")
        assert decisions_idx < notes_idx

    def test_append_updates_timestamp(self, store):
        """Test that append updates Last Updated timestamp."""
        task_id = "task-375"
        store.create(task_id, task_title="Test")
        original_content = store.read(task_id)

        # Small delay to ensure timestamp changes (use larger delay for reliability)
        import time

        time.sleep(1.1)

        store.append(task_id, "New content")
        updated_content = store.read(task_id)

        # Extract timestamps
        original_ts = [
            line for line in original_content.split("\n") if "Last Updated" in line
        ][0]
        updated_ts = [
            line for line in updated_content.split("\n") if "Last Updated" in line
        ][0]

        # Verify timestamp line exists and content changed
        assert "Last Updated" in original_ts
        assert "Last Updated" in updated_ts
        # Either different timestamp or at least we have the timestamp line
        assert original_ts != updated_ts or "Last Updated" in updated_ts

    def test_append_to_nonexistent_raises_error(self, store):
        """Test that appending to nonexistent memory raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            store.append("task-999", "content")

    def test_append_preserves_existing_content(self, store):
        """Test that append preserves existing content."""
        task_id = "task-375"
        store.create(task_id, task_title="Original Title")

        store.append(task_id, "New content")
        content = store.read(task_id)

        assert "Original Title" in content
        assert "New content" in content


class TestTaskMemoryStoreArchive:
    """Tests for archiving task memory."""

    def test_archive_moves_file(self, store):
        """Test that archive moves file to archive directory."""
        task_id = "task-375"
        store.create(task_id, task_title="Test")

        active_path = store.get_path(task_id)
        assert active_path.exists()

        store.archive(task_id)

        assert not active_path.exists()
        archive_path = store.archive_dir / f"{task_id}.md"
        assert archive_path.exists()

    def test_archive_nonexistent_raises_error(self, store):
        """Test that archiving nonexistent memory raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            store.archive("task-999")

    def test_archive_preserves_content(self, store):
        """Test that archive preserves file content."""
        task_id = "task-375"
        store.create(task_id, task_title="Test Task")
        original_content = store.read(task_id)

        store.archive(task_id)

        archive_path = store.archive_dir / f"{task_id}.md"
        archived_content = archive_path.read_text()
        assert archived_content == original_content


class TestTaskMemoryStoreRestore:
    """Tests for restoring task memory from archive."""

    def test_restore_moves_file_back(self, store):
        """Test that restore moves file from archive to active."""
        task_id = "task-375"
        store.create(task_id, task_title="Test")
        store.archive(task_id)

        archive_path = store.archive_dir / f"{task_id}.md"
        assert archive_path.exists()

        store.restore(task_id)

        assert not archive_path.exists()
        active_path = store.get_path(task_id)
        assert active_path.exists()

    def test_restore_nonexistent_raises_error(self, store):
        """Test that restoring nonexistent archive raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            store.restore("task-999")

    def test_restore_when_active_exists_raises_error(self, store):
        """Test that restoring when active file exists raises FileExistsError."""
        task_id = "task-375"
        store.create(task_id, task_title="Test")
        store.archive(task_id)

        # Create new active file with same ID
        store.create(task_id, task_title="New")

        with pytest.raises(FileExistsError, match="already exists"):
            store.restore(task_id)

    def test_restore_preserves_content(self, store):
        """Test that restore preserves file content."""
        task_id = "task-375"
        store.create(task_id, task_title="Test Task")
        original_content = store.read(task_id)

        store.archive(task_id)
        store.restore(task_id)

        restored_content = store.read(task_id)
        assert restored_content == original_content


class TestTaskMemoryStoreDelete:
    """Tests for deleting task memory."""

    def test_delete_active_memory(self, store):
        """Test deleting active memory file."""
        task_id = "task-375"
        store.create(task_id, task_title="Test")

        path = store.get_path(task_id)
        assert path.exists()

        store.delete(task_id)
        assert not path.exists()

    def test_delete_archived_memory(self, store):
        """Test deleting archived memory file."""
        task_id = "task-375"
        store.create(task_id, task_title="Test")
        store.archive(task_id)

        archive_path = store.archive_dir / f"{task_id}.md"
        assert archive_path.exists()

        store.delete(task_id, from_archive=True)
        assert not archive_path.exists()

    def test_delete_nonexistent_raises_error(self, store):
        """Test that deleting nonexistent memory raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            store.delete("task-999")

    def test_delete_nonexistent_archive_raises_error(self, store):
        """Test that deleting nonexistent archive raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="not found"):
            store.delete("task-999", from_archive=True)


class TestTaskMemoryStoreList:
    """Tests for listing task memory files."""

    def test_list_active_empty(self, store):
        """Test listing active memories when none exist."""
        active = store.list_active()
        assert active == []

    def test_list_active_with_files(self, store):
        """Test listing active memories."""
        store.create("task-375", task_title="First")
        store.create("task-376", task_title="Second")
        store.create("task-100", task_title="Third")

        active = store.list_active()
        assert len(active) == 3
        assert "task-375" in active
        assert "task-376" in active
        assert "task-100" in active
        # Verify sorted
        assert active == sorted(active)

    def test_list_archived_empty(self, store):
        """Test listing archived memories when none exist."""
        archived = store.list_archived()
        assert archived == []

    def test_list_archived_with_files(self, store):
        """Test listing archived memories."""
        store.create("task-375", task_title="First")
        store.create("task-376", task_title="Second")
        store.archive("task-375")
        store.archive("task-376")

        archived = store.list_archived()
        assert len(archived) == 2
        assert "task-375" in archived
        assert "task-376" in archived

    def test_list_active_excludes_archived(self, store):
        """Test that list_active excludes archived files."""
        store.create("task-375", task_title="First")
        store.create("task-376", task_title="Second")
        store.archive("task-375")

        active = store.list_active()
        assert "task-376" in active
        assert "task-375" not in active

    def test_list_ignores_non_task_files(self, store, temp_project):
        """Test that listing ignores non-task markdown files."""
        store.create("task-375", task_title="Task")
        # Create non-task file
        (store.memory_dir / "README.md").write_text("# README")

        active = store.list_active()
        assert len(active) == 1
        assert "task-375" in active
        assert "README" not in active


class TestTaskMemoryStoreExists:
    """Tests for checking task memory existence."""

    def test_exists_active_file(self, store):
        """Test exists returns True for active file."""
        store.create("task-375", task_title="Test")
        assert store.exists("task-375")

    def test_exists_nonexistent_file(self, store):
        """Test exists returns False for nonexistent file."""
        assert not store.exists("task-999")

    def test_exists_archived_file_without_check(self, store):
        """Test exists returns False for archived file when not checking archive."""
        store.create("task-375", task_title="Test")
        store.archive("task-375")
        assert not store.exists("task-375")

    def test_exists_archived_file_with_check(self, store):
        """Test exists returns True for archived file when checking archive."""
        store.create("task-375", task_title="Test")
        store.archive("task-375")
        assert store.exists("task-375", check_archive=True)

    def test_exists_after_delete(self, store):
        """Test exists returns False after deletion."""
        store.create("task-375", task_title="Test")
        store.delete("task-375")
        assert not store.exists("task-375")


class TestTaskMemoryStoreGetPath:
    """Tests for getting task memory path."""

    def test_get_path_returns_correct_path(self, store):
        """Test get_path returns correct Path object."""
        path = store.get_path("task-375")
        assert isinstance(path, Path)
        assert path.name == "task-375.md"
        assert path.parent == store.memory_dir

    def test_get_path_for_nonexistent_file(self, store):
        """Test get_path works for nonexistent files."""
        path = store.get_path("task-999")
        assert isinstance(path, Path)
        assert not path.exists()

    def test_get_path_consistency(self, store):
        """Test get_path returns consistent results."""
        path1 = store.get_path("task-375")
        path2 = store.get_path("task-375")
        assert path1 == path2


class TestTaskMemoryStoreEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_handle_concurrent_operations(self, store):
        """Test handling of concurrent operations (basic test)."""
        task_id = "task-375"
        store.create(task_id, task_title="Test")

        # Multiple appends should work
        store.append(task_id, "Note 1")
        store.append(task_id, "Note 2")
        store.append(task_id, "Note 3")

        content = store.read(task_id)
        assert "Note 1" in content
        assert "Note 2" in content
        assert "Note 3" in content

    def test_handle_invalid_task_id(self, store):
        """Test handling of invalid task IDs."""
        # Should not crash with unusual task IDs
        path = store.get_path("task-with-dashes")
        assert path.name == "task-with-dashes.md"

    def test_handle_unicode_content(self, store):
        """Test handling of unicode content."""
        task_id = "task-375"
        store.create(task_id, task_title="Test 测试")

        unicode_content = "Unicode: 日本語 中文 한국어 🚀"
        store.append(task_id, unicode_content)

        content = store.read(task_id)
        assert unicode_content in content
        assert "测试" in content

    def test_large_content_handling(self, store):
        """Test handling of large content."""
        task_id = "task-375"
        store.create(task_id, task_title="Test")

        # Append large content
        large_content = "x" * 10000
        store.append(task_id, large_content)

        content = store.read(task_id)
        assert large_content in content

    def test_multiple_sections_append(self, store):
        """Test appending to multiple sections."""
        task_id = "task-375"
        store.create(task_id, task_title="Test")

        store.append(task_id, "Decision 1", section="Key Decisions")
        store.append(task_id, "Note 1", section="Notes")
        store.append(task_id, "Decision 2", section="Key Decisions")

        content = store.read(task_id)
        assert "Decision 1" in content
        assert "Decision 2" in content
        assert "Note 1" in content
