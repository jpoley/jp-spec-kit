"""Tests for Memory CLI commands.

Tests the specify memory CLI subcommands:
- init: Initialize a new task memory file
- show: Display task memory content
- append: Append content to task memory
- list: List all task memories
- search: Search across task memories
- clear: Clear task memory content
- cleanup: Cleanup old task memories
- stats: Show task memory statistics
"""

from __future__ import annotations

import json
import time

import pytest
from typer.testing import CliRunner

from specify_cli.memory.cli import memory_app
from specify_cli.memory.store import TaskMemoryStore

# Create CLI runner
runner = CliRunner()


# --- Fixtures ---


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace with memory directory."""
    memory_dir = tmp_path / "backlog" / "memory"
    memory_dir.mkdir(parents=True)
    (memory_dir / "archive").mkdir(parents=True)

    # Create template directory
    template_dir = tmp_path / "templates" / "memory"
    template_dir.mkdir(parents=True)

    # Create default template
    template_content = """# Task Memory: {task_id}

**Created**: {created_date}
**Last Updated**: {updated_date}
**Task**: {task_title}

## Context

<!-- Brief description -->

## Key Decisions

<!-- Important decisions -->

## Notes

<!-- Freeform notes -->
"""
    (template_dir / "default.md").write_text(template_content)

    return tmp_path


@pytest.fixture
def sample_memories(temp_workspace):
    """Create sample task memory files."""
    store = TaskMemoryStore(base_path=temp_workspace)

    # Create active memories
    store.create("task-389", task_title="Implement Append Command")
    store.append("task-389", "Started implementation")
    store.append("task-389", "Decision: Use Typer for CLI", section="Key Decisions")

    store.create("task-390", task_title="Implement List Command")
    store.append("task-390", "API implementation complete")

    # Create archived memory
    store.create("task-100", task_title="Old Task")
    store.append("task-100", "This task is completed")
    store.archive("task-100")

    return store


# --- Test: memory init ---


def test_init_creates_memory(temp_workspace):
    """Test initializing a new task memory."""
    result = runner.invoke(
        memory_app,
        ["init", "task-500", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0
    assert "Created task memory" in result.stdout

    # Verify file was created
    store = TaskMemoryStore(base_path=temp_workspace)
    assert store.exists("task-500")


def test_init_with_title(temp_workspace):
    """Test initializing memory with custom title."""
    result = runner.invoke(
        memory_app,
        [
            "init",
            "task-501",
            "--title",
            "Implement Custom Feature",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0

    # Verify content includes title
    store = TaskMemoryStore(base_path=temp_workspace)
    content = store.read("task-501")
    assert "Implement Custom Feature" in content


def test_init_existing_memory_fails(temp_workspace, sample_memories):
    """Test that init fails for existing memory without --force."""
    result = runner.invoke(
        memory_app,
        ["init", "task-389", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 1
    assert "already exists" in result.stdout


def test_init_force_overwrites(temp_workspace, sample_memories):
    """Test that --force overwrites existing memory."""
    # Get original content
    store = TaskMemoryStore(base_path=temp_workspace)
    original_content = store.read("task-389")

    result = runner.invoke(
        memory_app,
        [
            "init",
            "task-389",
            "--force",
            "--title",
            "New Title",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "Created task memory" in result.stdout

    # Verify content was replaced
    new_content = store.read("task-389")
    assert "New Title" in new_content
    assert new_content != original_content


# --- Test: memory show ---


def test_show_active_memory(temp_workspace, sample_memories):
    """Test showing active task memory."""
    result = runner.invoke(
        memory_app,
        ["show", "task-389", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0
    assert "task-389" in result.stdout
    # Rich formatting may wrap text, so check for partial match
    assert "Implement" in result.stdout and "Append" in result.stdout


def test_show_archived_memory(temp_workspace, sample_memories):
    """Test showing archived task memory."""
    result = runner.invoke(
        memory_app,
        [
            "show",
            "task-100",
            "--archived",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "task-100" in result.stdout
    assert "archive" in result.stdout


def test_show_plain_output(temp_workspace, sample_memories):
    """Test plain text output."""
    result = runner.invoke(
        memory_app,
        ["show", "task-389", "--plain", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0
    assert "# Task Memory: task-389" in result.stdout
    assert "Implement Append Command" in result.stdout


def test_show_nonexistent_memory(temp_workspace, sample_memories):
    """Test showing nonexistent memory."""
    result = runner.invoke(
        memory_app,
        ["show", "task-999", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 1
    assert "not found" in result.stdout


# --- Test: memory append ---


def test_append_basic(temp_workspace, sample_memories):
    """Test basic content append."""
    result = runner.invoke(
        memory_app,
        [
            "append",
            "task-389",
            "New entry added",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "✓" in result.stdout
    assert "task-389" in result.stdout

    # Verify content was appended
    store = TaskMemoryStore(base_path=temp_workspace)
    content = store.read("task-389")
    assert "New entry added" in content


def test_append_to_section(temp_workspace, sample_memories):
    """Test appending to specific section."""
    result = runner.invoke(
        memory_app,
        [
            "append",
            "task-389",
            "Another decision made",
            "--section",
            "Key Decisions",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "✓" in result.stdout

    # Verify content was appended to section
    store = TaskMemoryStore(base_path=temp_workspace)
    content = store.read("task-389")
    assert "Another decision made" in content


def test_append_nonexistent_memory(temp_workspace, sample_memories):
    """Test appending to nonexistent memory."""
    result = runner.invoke(
        memory_app,
        [
            "append",
            "task-999",
            "Content",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 1
    assert "not found" in result.stdout


def test_append_multiline_content(temp_workspace, sample_memories):
    """Test appending multi-line content."""
    content = "Line 1\nLine 2\nLine 3"
    result = runner.invoke(
        memory_app,
        [
            "append",
            "task-389",
            content,
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0

    # Verify multi-line content
    store = TaskMemoryStore(base_path=temp_workspace)
    memory_content = store.read("task-389")
    assert "Line 1" in memory_content
    assert "Line 2" in memory_content
    assert "Line 3" in memory_content


# --- Test: memory list ---


def test_list_active_memories(temp_workspace, sample_memories):
    """Test listing active memories."""
    result = runner.invoke(
        memory_app,
        ["list", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0
    assert "task-389" in result.stdout
    assert "task-390" in result.stdout
    assert "task-100" not in result.stdout  # Archived


def test_list_archived_memories(temp_workspace, sample_memories):
    """Test listing archived memories."""
    result = runner.invoke(
        memory_app,
        ["list", "--archived", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0
    assert "task-100" in result.stdout
    assert "task-389" not in result.stdout  # Active


def test_list_all_memories(temp_workspace, sample_memories):
    """Test listing all memories."""
    result = runner.invoke(
        memory_app,
        ["list", "--all", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0
    assert "task-389" in result.stdout
    assert "task-390" in result.stdout
    assert "task-100" in result.stdout


def test_list_plain_output(temp_workspace, sample_memories):
    """Test plain text output."""
    result = runner.invoke(
        memory_app,
        ["list", "--plain", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0
    assert "task-389\t" in result.stdout
    assert "task-390\t" in result.stdout


def test_list_empty_directory(temp_workspace):
    """Test listing when no memories exist."""
    result = runner.invoke(
        memory_app,
        ["list", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0
    assert "No" in result.stdout


def test_list_sorting_by_modified(temp_workspace):
    """Test that list sorts by modified time (newest first)."""
    store = TaskMemoryStore(base_path=temp_workspace)

    # Create memories with delays to ensure different timestamps
    store.create("task-001", task_title="First")
    time.sleep(0.1)
    store.create("task-002", task_title="Second")
    time.sleep(0.1)
    store.create("task-003", task_title="Third")

    result = runner.invoke(
        memory_app,
        ["list", "--plain", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0

    # Parse output to check order
    lines = [line for line in result.stdout.split("\n") if line.strip()]
    task_ids = [line.split("\t")[0] for line in lines]

    # Newest first
    assert task_ids == ["task-003", "task-002", "task-001"]


# --- Test: memory search ---


def test_search_basic(temp_workspace, sample_memories):
    """Test basic text search."""
    result = runner.invoke(
        memory_app,
        ["search", "Typer", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0
    assert "task-389" in result.stdout
    assert "Typer" in result.stdout


def test_search_regex_pattern(temp_workspace, sample_memories):
    """Test regex pattern search."""
    result = runner.invoke(
        memory_app,
        ["search", "impl.*command", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0
    # Should match "implementation" or "Implement...Command"


def test_search_include_archived(temp_workspace, sample_memories):
    """Test search including archived memories."""
    result = runner.invoke(
        memory_app,
        [
            "search",
            "completed",
            "--archived",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "task-100" in result.stdout


def test_search_limit_results(temp_workspace, sample_memories):
    """Test limiting search results."""
    result = runner.invoke(
        memory_app,
        [
            "search",
            "task",
            "--limit",
            "1",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    # Should show only 1 result


def test_search_context_lines(temp_workspace, sample_memories):
    """Test context lines around matches."""
    result = runner.invoke(
        memory_app,
        [
            "search",
            "Typer",
            "--context",
            "3",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    # Should show lines before/after match


def test_search_plain_output(temp_workspace, sample_memories):
    """Test plain text search output."""
    result = runner.invoke(
        memory_app,
        [
            "search",
            "Typer",
            "--plain",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "task-389:" in result.stdout


def test_search_no_matches(temp_workspace, sample_memories):
    """Test search with no matches."""
    result = runner.invoke(
        memory_app,
        [
            "search",
            "NONEXISTENT_PATTERN_12345",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "No matches" in result.stdout


def test_search_invalid_regex(temp_workspace, sample_memories):
    """Test search with invalid regex."""
    result = runner.invoke(
        memory_app,
        ["search", "[invalid(regex", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 1
    assert "Invalid regex" in result.stdout


# --- Test: memory clear ---


def test_clear_with_confirmation(temp_workspace, sample_memories):
    """Test clearing memory with confirmation."""
    result = runner.invoke(
        memory_app,
        [
            "clear",
            "task-389",
            "--confirm",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "✓" in result.stdout
    assert "cleared" in result.stdout

    # Verify memory was deleted
    store = TaskMemoryStore(base_path=temp_workspace)
    assert not store.exists("task-389")


def test_clear_creates_backup(temp_workspace, sample_memories):
    """Test that clear creates backup by default."""
    result = runner.invoke(
        memory_app,
        [
            "clear",
            "task-389",
            "--confirm",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "Backup created" in result.stdout

    # Verify backup exists
    backup_dir = temp_workspace / ".specify" / "backups"
    backups = list(backup_dir.glob("task-389.*.bak"))
    assert len(backups) > 0


def test_clear_no_backup(temp_workspace, sample_memories):
    """Test clearing without backup."""
    result = runner.invoke(
        memory_app,
        [
            "clear",
            "task-389",
            "--confirm",
            "--no-backup",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0

    # Verify no backup was created
    backup_dir = temp_workspace / ".specify" / "backups"
    if backup_dir.exists():
        backups = list(backup_dir.glob("task-389.*.bak"))
        assert len(backups) == 0


def test_clear_nonexistent_memory(temp_workspace, sample_memories):
    """Test clearing nonexistent memory."""
    result = runner.invoke(
        memory_app,
        [
            "clear",
            "task-999",
            "--confirm",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 1
    assert "not found" in result.stdout


# --- Test: memory cleanup ---


def test_cleanup_dry_run(temp_workspace, sample_memories):
    """Test cleanup in dry-run mode."""
    result = runner.invoke(
        memory_app,
        [
            "cleanup",
            "--archive-older-than",
            "0",
            "--dry-run",
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "DRY RUN" in result.stdout
    assert "task-389" in result.stdout or "task-390" in result.stdout

    # Verify no changes made
    store = TaskMemoryStore(base_path=temp_workspace)
    assert len(store.list_active()) == 2  # Still have active memories


def test_cleanup_archive_old_memories(temp_workspace):
    """Test archiving old memories."""
    store = TaskMemoryStore(base_path=temp_workspace)

    # Create old memory (modify mtime)
    store.create("task-old", task_title="Old Task")
    old_path = store.get_path("task-old")
    old_time = time.time() - (31 * 24 * 60 * 60)  # 31 days ago
    old_path.touch()
    import os

    os.utime(old_path, (old_time, old_time))

    # Create new memory
    store.create("task-new", task_title="New Task")

    result = runner.invoke(
        memory_app,
        [
            "cleanup",
            "--archive-older-than",
            "30",
            "--execute",
            "--project-root",
            str(temp_workspace),
        ],
        input="y\n",  # Confirm
    )

    assert result.exit_code == 0

    # Verify old memory was archived
    assert not store.exists("task-old")
    assert store.exists("task-old", check_archive=True)

    # Verify new memory is still active
    assert store.exists("task-new")


def test_cleanup_delete_old_archived(temp_workspace):
    """Test deleting old archived memories."""
    store = TaskMemoryStore(base_path=temp_workspace)

    # Create and archive old memory
    store.create("task-archived", task_title="Archived Task")
    store.archive("task-archived")

    # Make it old
    archived_path = store.archive_dir / "task-archived.md"
    old_time = time.time() - (91 * 24 * 60 * 60)  # 91 days ago
    import os

    os.utime(archived_path, (old_time, old_time))

    result = runner.invoke(
        memory_app,
        [
            "cleanup",
            "--delete-older-than",
            "90",
            "--execute",
            "--project-root",
            str(temp_workspace),
        ],
        input="y\n",  # Confirm
    )

    assert result.exit_code == 0

    # Verify memory was deleted
    assert not store.exists("task-archived", check_archive=True)


def test_cleanup_combined_operations(temp_workspace):
    """Test combined archive and delete operations."""
    store = TaskMemoryStore(base_path=temp_workspace)

    # Create old active memory
    store.create("task-active-old", task_title="Old Active")
    active_path = store.get_path("task-active-old")
    old_time = time.time() - (31 * 24 * 60 * 60)
    import os

    os.utime(active_path, (old_time, old_time))

    # Create old archived memory
    store.create("task-archived-old", task_title="Old Archived")
    store.archive("task-archived-old")
    archived_path = store.archive_dir / "task-archived-old.md"
    os.utime(archived_path, (old_time, old_time))

    result = runner.invoke(
        memory_app,
        [
            "cleanup",
            "--archive-older-than",
            "30",
            "--delete-older-than",
            "30",
            "--execute",
            "--project-root",
            str(temp_workspace),
        ],
        input="y\n",
    )

    assert result.exit_code == 0
    assert "Archive: 1" in result.stdout
    assert "Delete:  1" in result.stdout


def test_cleanup_no_operations_needed(temp_workspace, sample_memories):
    """Test cleanup when no operations needed."""
    result = runner.invoke(
        memory_app,
        [
            "cleanup",
            "--archive-older-than",
            "365",  # 1 year
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0
    assert "No cleanup operations" in result.stdout


# --- Test: memory stats ---


def test_stats_basic(temp_workspace, sample_memories):
    """Test basic statistics display."""
    result = runner.invoke(
        memory_app,
        ["stats", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0
    assert "Task Memory Statistics" in result.stdout
    assert "Active Memories" in result.stdout
    assert "Archived Memories" in result.stdout
    assert "Count:" in result.stdout


def test_stats_json_output(temp_workspace, sample_memories):
    """Test JSON statistics output."""
    result = runner.invoke(
        memory_app,
        ["stats", "--json", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0

    # Parse JSON
    stats = json.loads(result.stdout)
    assert "active" in stats
    assert "archived" in stats
    assert "total" in stats
    assert stats["active"]["count"] == 2
    assert stats["archived"]["count"] == 1


def test_stats_empty_directory(temp_workspace):
    """Test statistics with no memories."""
    result = runner.invoke(
        memory_app,
        ["stats", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0
    assert "Count:       0" in result.stdout


def test_stats_size_calculations(temp_workspace, sample_memories):
    """Test size calculations in stats."""
    result = runner.invoke(
        memory_app,
        ["stats", "--json", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0

    stats = json.loads(result.stdout)

    # Verify size fields exist and are reasonable
    assert stats["active"]["total_size"] > 0
    assert stats["active"]["avg_size"] > 0
    assert stats["active"]["max_size"] > 0
    assert stats["total"]["total_size"] > 0


def test_stats_age_calculations(temp_workspace):
    """Test age calculations in stats."""
    store = TaskMemoryStore(base_path=temp_workspace)

    # Create memory with known age
    store.create("task-recent", task_title="Recent")

    # Create old memory
    store.create("task-old", task_title="Old")
    old_path = store.get_path("task-old")
    old_time = time.time() - (10 * 24 * 60 * 60)  # 10 days ago
    import os

    os.utime(old_path, (old_time, old_time))

    result = runner.invoke(
        memory_app,
        ["stats", "--json", "--project-root", str(temp_workspace)],
    )

    assert result.exit_code == 0

    stats = json.loads(result.stdout)

    # Verify age fields
    assert stats["active"]["oldest_days"] > 9  # ~10 days
    assert stats["active"]["newest_days"] < 1  # Recent


# --- Test: Edge Cases ---


def test_concurrent_append_operations(temp_workspace, sample_memories):
    """Test multiple append operations (simulating concurrency)."""
    # Rapidly append multiple entries
    for i in range(5):
        result = runner.invoke(
            memory_app,
            [
                "append",
                "task-389",
                f"Entry {i}",
                "--project-root",
                str(temp_workspace),
            ],
        )
        assert result.exit_code == 0

    # Verify all entries are present
    store = TaskMemoryStore(base_path=temp_workspace)
    content = store.read("task-389")
    for i in range(5):
        assert f"Entry {i}" in content


def test_large_memory_file(temp_workspace):
    """Test operations on large memory file."""
    store = TaskMemoryStore(base_path=temp_workspace)
    store.create("task-large", task_title="Large File")

    # Append large content
    large_content = "\n".join([f"Line {i}" for i in range(1000)])
    store.append("task-large", large_content)

    # Test list (should handle large file)
    result = runner.invoke(
        memory_app,
        ["list", "--project-root", str(temp_workspace)],
    )
    assert result.exit_code == 0

    # Test search (should handle large file)
    result = runner.invoke(
        memory_app,
        ["search", "Line 500", "--project-root", str(temp_workspace)],
    )
    assert result.exit_code == 0
    assert "Line 500" in result.stdout


def test_special_characters_in_content(temp_workspace, sample_memories):
    """Test handling special characters in content."""
    special_content = "Content with $pecial ch@rs: <>\"'&"

    result = runner.invoke(
        memory_app,
        [
            "append",
            "task-389",
            special_content,
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0

    # Verify content preserved
    store = TaskMemoryStore(base_path=temp_workspace)
    content = store.read("task-389")
    assert special_content in content


def test_unicode_content(temp_workspace, sample_memories):
    """Test handling unicode content."""
    unicode_content = "Unicode: 你好世界 🚀 café"

    result = runner.invoke(
        memory_app,
        [
            "append",
            "task-389",
            unicode_content,
            "--project-root",
            str(temp_workspace),
        ],
    )

    assert result.exit_code == 0

    # Verify unicode preserved
    store = TaskMemoryStore(base_path=temp_workspace)
    content = store.read("task-389")
    assert unicode_content in content
