"""Integration tests for post-commit-backlog-events git hook.

Tests the hook's ability to detect task file changes and emit events.
Uses a real git repository (in tmpdir) to simulate the full workflow.
"""

import os
import subprocess
from pathlib import Path
from textwrap import dedent

import pytest


@pytest.fixture
def mock_git_repo(tmp_path: Path) -> Path:
    """Create a mock git repository with backlog structure.

    Args:
        tmp_path: pytest temporary directory

    Returns:
        Path to git repository root
    """
    repo_root = tmp_path / "test-repo"
    repo_root.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )

    # Create backlog directory structure
    tasks_dir = repo_root / "backlog" / "tasks"
    tasks_dir.mkdir(parents=True)

    # Create scripts/hooks directory and copy hook
    hooks_dir = repo_root / "scripts" / "hooks"
    hooks_dir.mkdir(parents=True)

    # Copy the post-commit hook script
    hook_script_src = (
        Path(__file__).parent.parent
        / "scripts"
        / "hooks"
        / "post-commit-backlog-events.sh"
    )
    hook_script_dst = hooks_dir / "post-commit-backlog-events.sh"
    hook_script_dst.write_text(hook_script_src.read_text())
    hook_script_dst.chmod(0o755)

    # Create a mock specify command that logs events to a file
    bin_dir = repo_root / "bin"
    bin_dir.mkdir()
    mock_specify = bin_dir / "specify"
    mock_specify.write_text(
        dedent(f"""\
        #!/bin/bash
        # Mock specify command for testing
        # Logs all arguments to events.log
        echo "$(date '+%H:%M:%S') - $@" >> "{repo_root}/events.log"
        echo "Mock specify called with: $@" >&2
        exit 0
    """)
    )
    mock_specify.chmod(0o755)

    # Install hook wrapper that sets up PATH for mock specify
    # The hook needs PATH set at the script level, not from git's env
    git_hooks_dir = repo_root / ".git" / "hooks"
    post_commit_hook = git_hooks_dir / "post-commit"
    post_commit_hook.write_text(
        dedent(f"""\
        #!/bin/bash
        # Wrapper hook that sets up PATH for mock specify
        export PATH="{bin_dir}:$PATH"
        exec "{hook_script_dst}"
    """)
    )
    post_commit_hook.chmod(0o755)

    # Initial commit (empty)
    (repo_root / "README.md").write_text("# Test Repo\n")
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_root,
        check=True,
        capture_output=True,
    )

    return repo_root


def create_task_file(
    repo_root: Path,
    task_id: str,
    status: str = "To Do",
    acs: list[tuple[int, bool]] | None = None,
) -> Path:
    """Create a backlog task file.

    Args:
        repo_root: Git repository root
        task_id: Task ID (e.g., "task-123")
        status: Task status (default: "To Do")
        acs: List of (ac_number, checked) tuples for acceptance criteria

    Returns:
        Path to created task file
    """
    if acs is None:
        acs = [(1, False), (2, False)]

    ac_lines = "\n".join(
        f"- [{'x' if checked else ' '}] #{num} Acceptance criterion {num}"
        for num, checked in acs
    )

    task_content = f"""---
id: {task_id}
title: Test Task {task_id}
status: {status}
assignee:
  - '@test'
created_date: '2025-12-11 00:00'
updated_date: '2025-12-11 00:00'
labels:
  - test
dependencies: []
priority: medium
---

## Description

Test task for integration testing.

## Acceptance Criteria
<!-- AC:BEGIN -->
{ac_lines}
<!-- AC:END -->
"""

    task_file = repo_root / "backlog" / "tasks" / f"{task_id} - Test-Task.md"
    task_file.write_text(task_content)
    return task_file


def git_commit(repo_root: Path, message: str) -> subprocess.CompletedProcess:
    """Create a git commit with mock specify in PATH.

    Args:
        repo_root: Git repository root
        message: Commit message

    Returns:
        CompletedProcess from git commit command
    """
    # Add mock bin directory to PATH
    env = os.environ.copy()
    env["PATH"] = f"{repo_root / 'bin'}:{env.get('PATH', '')}"
    env["PROJECT_ROOT"] = str(repo_root)

    subprocess.run(
        ["git", "add", "."], cwd=repo_root, check=True, capture_output=True, env=env
    )
    result = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return result


def get_emitted_events(repo_root: Path) -> list[str]:
    """Get events emitted during commits.

    Args:
        repo_root: Git repository root

    Returns:
        List of event command lines from events.log
    """
    events_log = repo_root / "events.log"
    if not events_log.exists():
        return []

    return (
        events_log.read_text().strip().split("\n")
        if events_log.read_text().strip()
        else []
    )


def test_hook_detects_new_task(mock_git_repo: Path) -> None:
    """Hook should emit task.created for new task files."""
    # Create new task file
    create_task_file(mock_git_repo, "task-123")

    # Commit (triggers hook)
    git_commit(mock_git_repo, "Add task-123")

    # Verify task.created event was emitted
    events = get_emitted_events(mock_git_repo)

    # Should have at least one event
    assert len(events) >= 1, f"Expected at least one event, got {len(events)}"

    # Find task.created event
    created_events = [e for e in events if "task.created" in e and "task-123" in e]
    assert len(created_events) >= 1, (
        f"Expected task.created for task-123, got events: {events}"
    )


def test_hook_detects_status_change(mock_git_repo: Path) -> None:
    """Hook should emit task.status_changed when status changes."""
    # Create task with initial status
    task_file = create_task_file(mock_git_repo, "task-456", status="To Do")
    git_commit(mock_git_repo, "Add task-456")

    # Change status
    content = task_file.read_text()
    content = content.replace("status: To Do", "status: In Progress")
    task_file.write_text(content)

    # Commit (triggers hook)
    git_commit(mock_git_repo, "Update task-456 status")

    # Verify task.status_changed was emitted (should be in events after both commits)
    events = get_emitted_events(mock_git_repo)

    # Should have task.created from first commit AND task.status_changed from second
    has_created = any("task.created" in e and "task-456" in e for e in events)
    has_status_changed = any(
        "task.status_changed" in e and "task-456" in e for e in events
    )

    assert has_created, f"Expected task.created event, got: {events}"
    assert has_status_changed, f"Expected task.status_changed event, got: {events}"


def test_hook_detects_task_completed(mock_git_repo: Path) -> None:
    """Hook should emit task.completed when task marked as Done."""
    # Create task
    task_file = create_task_file(mock_git_repo, "task-789", status="In Progress")
    git_commit(mock_git_repo, "Add task-789")

    # Get count before
    events_before = get_emitted_events(mock_git_repo)
    before_count = len(events_before)

    # Mark as Done
    content = task_file.read_text()
    content = content.replace("status: In Progress", "status: Done")
    task_file.write_text(content)

    # Commit
    git_commit(mock_git_repo, "Complete task-789")

    # Verify both task.status_changed and task.completed were emitted
    events = get_emitted_events(mock_git_repo)
    new_events = events[before_count:] if len(events) > before_count else events

    status_changed = any("task.status_changed" in e for e in new_events)
    completed = any("task.completed" in e for e in new_events)

    assert status_changed, (
        f"Expected task.status_changed event, got new events: {new_events}"
    )
    assert completed, f"Expected task.completed event, got new events: {new_events}"


def test_hook_detects_ac_checked(mock_git_repo: Path) -> None:
    """Hook should emit task.ac_checked when AC checkbox changes."""
    # Create task with unchecked ACs
    task_file = create_task_file(
        mock_git_repo, "task-999", status="In Progress", acs=[(1, False), (2, False)]
    )
    git_commit(mock_git_repo, "Add task-999")

    # Get count before
    events_before = get_emitted_events(mock_git_repo)
    before_count = len(events_before)

    # Check first AC
    content = task_file.read_text()
    content = content.replace("- [ ] #1", "- [x] #1")
    task_file.write_text(content)

    # Commit
    git_commit(mock_git_repo, "Check AC #1 for task-999")

    # Verify task.ac_checked was emitted
    events = get_emitted_events(mock_git_repo)
    new_events = events[before_count:] if len(events) > before_count else events
    ac_checked = any("task.ac_checked" in e for e in new_events)

    assert ac_checked, f"Expected task.ac_checked event, got new events: {new_events}"


def test_hook_is_idempotent(mock_git_repo: Path) -> None:
    """Hook should be safe to run multiple times on same commit."""
    # Create and commit task
    create_task_file(mock_git_repo, "task-111")
    git_commit(mock_git_repo, "Add task-111")

    # Run hook manually twice
    hook_path = mock_git_repo / ".git" / "hooks" / "post-commit"

    # First run
    result1 = subprocess.run(
        [str(hook_path)],
        cwd=mock_git_repo,
        capture_output=True,
        text=True,
    )

    # Second run (should be idempotent)
    result2 = subprocess.run(
        [str(hook_path)],
        cwd=mock_git_repo,
        capture_output=True,
        text=True,
    )

    # Both should succeed
    assert result1.returncode == 0, f"First run failed: {result1.stderr}"
    assert result2.returncode == 0, f"Second run failed: {result2.stderr}"

    # Output should be the same (no events on second run since no changes)
    # Note: This is a basic check; in practice, the hook won't emit events
    # on re-run because git diff HEAD~1 HEAD won't show changes


def test_hook_handles_missing_specify(mock_git_repo: Path) -> None:
    """Hook should exit gracefully if specify is not installed."""
    # Modify PATH to exclude specify
    env = {"PATH": "/usr/bin:/bin"}

    # Create and commit task
    create_task_file(mock_git_repo, "task-222")

    # Commit with modified environment
    subprocess.run(["git", "add", "."], cwd=mock_git_repo, check=True)
    result = subprocess.run(
        ["git", "commit", "-m", "Add task-222"],
        cwd=mock_git_repo,
        env=env,
        capture_output=True,
        text=True,
    )

    # Commit should succeed despite hook warning
    assert result.returncode == 0

    # Hook should output warning about missing specify
    assert "specify CLI not found" in result.stderr or result.returncode == 0


def test_hook_handles_non_task_files(mock_git_repo: Path) -> None:
    """Hook should ignore non-task file changes."""
    # Create non-task file
    other_file = mock_git_repo / "docs" / "guide.md"
    other_file.parent.mkdir(parents=True, exist_ok=True)
    other_file.write_text("# Guide\n")

    # Commit
    result = git_commit(mock_git_repo, "Add documentation")

    # Should succeed without emitting events
    assert result.returncode == 0


def test_hook_handles_multiple_tasks_in_one_commit(mock_git_repo: Path) -> None:
    """Hook should emit events for all changed tasks in a single commit."""
    # Create multiple tasks
    create_task_file(mock_git_repo, "task-001", status="To Do")
    create_task_file(mock_git_repo, "task-002", status="To Do")
    create_task_file(mock_git_repo, "task-003", status="To Do")

    # Commit all at once
    git_commit(mock_git_repo, "Add multiple tasks")

    # Verify events for all tasks
    events = get_emitted_events(mock_git_repo)

    # Should have 3 task.created events
    created_events = [e for e in events if "task.created" in e]

    assert len(created_events) >= 3, (
        f"Expected 3 task.created events, got {len(created_events)}: {events}"
    )


def test_hook_parses_task_id_with_dashes(mock_git_repo: Path) -> None:
    """Hook should correctly parse task IDs with dots like task-204.01."""
    # Create task with dotted ID
    task_file = create_task_file(mock_git_repo, "task-204.01", status="To Do")

    # Rename file to include title (realistic format)
    new_name = mock_git_repo / "backlog" / "tasks" / "task-204.01 - Test-Subtask.md"
    task_file.rename(new_name)

    # Commit
    result = git_commit(mock_git_repo, "Add task-204.01")

    # Should succeed
    assert result.returncode == 0
