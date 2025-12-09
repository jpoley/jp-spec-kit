"""Tests for ContextInjector - Task memory injection into CLAUDE.md."""

import pytest
from pathlib import Path
from specify_cli.memory.injector import ContextInjector


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory with CLAUDE.md."""
    backlog_dir = tmp_path / "backlog"
    backlog_dir.mkdir()

    claude_md = backlog_dir / "CLAUDE.md"
    claude_md.write_text(
        """# Backlog Task Management

## CRITICAL: Never Edit Task Files Directly

**ALL task operations MUST use the backlog CLI.**

## Task Workflow

```bash
backlog task list -s "To Do" --plain
```

## Command Reference

| Action | Command |
|--------|---------|
| View task | `backlog task 42 --plain` |
"""
    )

    # Create memory directory
    memory_dir = backlog_dir / "memory"
    memory_dir.mkdir()

    return tmp_path


def test_update_active_task_adds_section(tmp_project: Path) -> None:
    """Test that update_active_task adds Active Task Context section."""
    injector = ContextInjector(tmp_project)

    # Update with a task
    injector.update_active_task("task-375")

    # Verify section was added
    content = (tmp_project / "backlog" / "CLAUDE.md").read_text()
    assert "## Active Task Context" in content
    assert "@import ../memory/task-375.md" in content


def test_update_active_task_replaces_existing_section(tmp_project: Path) -> None:
    """Test that update_active_task replaces existing Active Task Context."""
    injector = ContextInjector(tmp_project)

    # Add first task
    injector.update_active_task("task-375")

    # Replace with second task
    injector.update_active_task("task-376")

    # Verify only second task is present
    content = (tmp_project / "backlog" / "CLAUDE.md").read_text()
    assert "@import ../memory/task-376.md" in content
    assert "@import ../memory/task-375.md" not in content
    assert content.count("## Active Task Context") == 1


def test_update_active_task_none_removes_section(tmp_project: Path) -> None:
    """Test that update_active_task(None) removes the section."""
    injector = ContextInjector(tmp_project)

    # Add task
    injector.update_active_task("task-375")
    assert (
        "## Active Task Context" in (tmp_project / "backlog" / "CLAUDE.md").read_text()
    )

    # Clear task
    injector.update_active_task(None)

    # Verify section was removed
    content = (tmp_project / "backlog" / "CLAUDE.md").read_text()
    assert "## Active Task Context" not in content
    assert "@import ../memory/task-375.md" not in content


def test_clear_active_task_removes_section(tmp_project: Path) -> None:
    """Test that clear_active_task removes the Active Task Context section."""
    injector = ContextInjector(tmp_project)

    # Add task
    injector.update_active_task("task-375")

    # Clear using clear method
    injector.clear_active_task()

    # Verify section was removed
    content = (tmp_project / "backlog" / "CLAUDE.md").read_text()
    assert "## Active Task Context" not in content


def test_get_active_task_id_returns_task(tmp_project: Path) -> None:
    """Test that get_active_task_id returns the active task ID."""
    injector = ContextInjector(tmp_project)

    # Initially no active task
    assert injector.get_active_task_id() is None

    # Set active task
    injector.update_active_task("task-375")
    assert injector.get_active_task_id() == "task-375"

    # Change active task
    injector.update_active_task("task-376")
    assert injector.get_active_task_id() == "task-376"

    # Clear active task
    injector.clear_active_task()
    assert injector.get_active_task_id() is None


def test_multiple_rapid_transitions(tmp_project: Path) -> None:
    """Test rapid task transitions don't corrupt CLAUDE.md."""
    injector = ContextInjector(tmp_project)

    # Simulate rapid task changes
    for i in range(100, 110):
        injector.update_active_task(f"task-{i}")

    # Verify final state is correct
    content = (tmp_project / "backlog" / "CLAUDE.md").read_text()
    assert content.count("## Active Task Context") == 1
    assert "@import ../memory/task-109.md" in content

    # Verify no accumulated garbage
    assert content.count("@import") == 1


def test_no_extra_blank_lines(tmp_project: Path) -> None:
    """Test that updates don't create excessive blank lines."""
    injector = ContextInjector(tmp_project)

    # Multiple updates
    injector.update_active_task("task-375")
    injector.clear_active_task()
    injector.update_active_task("task-376")
    injector.clear_active_task()

    # Verify no triple blank lines
    content = (tmp_project / "backlog" / "CLAUDE.md").read_text()
    assert "\n\n\n" not in content


def test_update_preserves_existing_content(tmp_project: Path) -> None:
    """Test that update_active_task preserves existing CLAUDE.md content."""
    injector = ContextInjector(tmp_project)

    # Update task
    injector.update_active_task("task-375")

    # Verify original content is preserved
    new_content = (tmp_project / "backlog" / "CLAUDE.md").read_text()
    assert "# Backlog Task Management" in new_content
    assert "## CRITICAL: Never Edit Task Files Directly" in new_content
    assert "## Task Workflow" in new_content


def test_update_active_task_missing_claude_md(tmp_project: Path) -> None:
    """Test that update_active_task raises FileNotFoundError if CLAUDE.md missing."""
    # Remove CLAUDE.md
    (tmp_project / "backlog" / "CLAUDE.md").unlink()

    injector = ContextInjector(tmp_project)

    with pytest.raises(FileNotFoundError):
        injector.update_active_task("task-375")


def test_get_active_task_id_missing_claude_md(tmp_project: Path) -> None:
    """Test that get_active_task_id raises FileNotFoundError if CLAUDE.md missing."""
    # Remove CLAUDE.md
    (tmp_project / "backlog" / "CLAUDE.md").unlink()

    injector = ContextInjector(tmp_project)

    with pytest.raises(FileNotFoundError):
        injector.get_active_task_id()


def test_section_at_end_of_file(tmp_project: Path) -> None:
    """Test that Active Task Context section works at end of file."""
    injector = ContextInjector(tmp_project)

    # Add section
    injector.update_active_task("task-375")

    # Verify it's at the end
    content = (tmp_project / "backlog" / "CLAUDE.md").read_text()
    lines = content.split("\n")

    # Find the section
    section_idx = None
    for i, line in enumerate(lines):
        if line == "## Active Task Context":
            section_idx = i
            break

    assert section_idx is not None
    # Should be near the end (within last 10 lines)
    assert len(lines) - section_idx < 10


def test_section_replacement_with_other_sections(tmp_project: Path) -> None:
    """Test section replacement when other sections exist after it."""
    # Create CLAUDE.md with Active Task Context in the middle
    claude_md = tmp_project / "backlog" / "CLAUDE.md"
    claude_md.write_text(
        """# Backlog Task Management

## Active Task Context

@import ../memory/task-375.md

## Other Section

Some content here.
"""
    )

    injector = ContextInjector(tmp_project)

    # Update to new task
    injector.update_active_task("task-376")

    # Verify replacement worked and Other Section is preserved
    content = claude_md.read_text()
    assert "@import ../memory/task-376.md" in content
    assert "@import ../memory/task-375.md" not in content
    assert "## Other Section" in content
    assert "Some content here." in content
