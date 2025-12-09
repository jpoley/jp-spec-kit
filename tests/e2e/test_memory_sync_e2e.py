"""E2E Tests for Cross-Machine Task Memory Sync.

This module tests git-based synchronization of task memory files across
multiple machines. Tests cover:
- Basic sync scenarios
- Conflict resolution
- Append-only merge behavior
- Branch synchronization

Uses a bare git repository as the shared remote to simulate multi-machine sync.

NOTE: Tests that use remote git sync (clone_repo, git push/pull) are marked with
@pytest.mark.git_sync and should be skipped in CI with: -m "not git_sync"

These tests are environment-dependent because:
1. Git template file tracking varies between git versions
2. Temp directory handling differs across systems
3. Git config (user.name, user.email) affects commit behavior

Local development testing: pytest tests/e2e/test_memory_sync_e2e.py
CI testing: pytest tests/e2e/test_memory_sync_e2e.py -m "not git_sync"
"""

import subprocess

import pytest
from specify_cli.memory import TaskMemoryStore


@pytest.fixture
def bare_remote(tmp_path):
    """Create a bare git repository to act as the remote origin."""
    remote_path = tmp_path / "remote.git"
    remote_path.mkdir()
    subprocess.run(
        ["git", "init", "--bare"],
        cwd=remote_path,
        check=True,
        capture_output=True,
    )
    return remote_path


@pytest.fixture
def git_repo(tmp_path, bare_remote):
    """Create a git repository with task memory structure connected to remote."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    # Initialize git repo with main as default branch
    subprocess.run(
        ["git", "init", "-b", "main"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Add remote
    subprocess.run(
        ["git", "remote", "add", "origin", str(bare_remote)],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    # Create directory structure
    memory_dir = repo_path / "backlog" / "memory"
    archive_dir = memory_dir / "archive"
    template_dir = repo_path / "templates" / "memory"

    memory_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)
    template_dir.mkdir(parents=True)

    # Create default template
    template_content = """# Task Memory: {task_id}

**Created**: {created_date}
**Last Updated**: {updated_date}
**Task**: {task_title}

## Context

## Key Decisions

## Notes
"""
    (template_dir / "default.md").write_text(template_content)

    # Create initial commit
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "push", "-u", "origin", "main"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )

    return repo_path


def clone_repo(bare_remote, tmp_path, name):
    """Clone the bare repository to simulate another machine."""
    clone_path = tmp_path / name
    subprocess.run(
        ["git", "clone", str(bare_remote), str(clone_path)],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", f"{name}@example.com"],
        cwd=clone_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", f"User {name}"],
        cwd=clone_path,
        check=True,
        capture_output=True,
    )
    return clone_path


def git_commit_and_push(repo_path, message):
    """Commit all changes and push to remote."""
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", message],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "push"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )


def git_pull(repo_path):
    """Pull latest changes from remote."""
    subprocess.run(
        ["git", "pull"],
        cwd=repo_path,
        check=True,
        capture_output=True,
    )


# --- Test: Basic Sync ---


@pytest.mark.git_sync
class TestBasicSync:
    """Tests for basic sync scenarios between machines.

    These tests use git clone/push/pull to sync between simulated machines.
    Mark with git_sync to skip in CI environments where git behavior varies.
    """

    def test_create_memory_on_machine_a_sync_to_machine_b(
        self, tmp_path, bare_remote, git_repo
    ):
        """Test creating memory on one machine and syncing to another."""
        # Machine A creates memory
        store_a = TaskMemoryStore(base_path=git_repo)
        store_a.create("task-100", task_title="Test Task")
        store_a.append("task-100", "Started on machine A")

        git_commit_and_push(git_repo, "Add task-100 memory")

        # Machine B clones and sees the memory
        machine_b = clone_repo(bare_remote, tmp_path, "machine_b")
        store_b = TaskMemoryStore(base_path=machine_b)

        assert store_b.exists("task-100")
        content = store_b.read("task-100")
        assert "Started on machine A" in content

    def test_bidirectional_sync(self, tmp_path, bare_remote, git_repo):
        """Test changes from both machines sync correctly."""
        # Machine A creates task-100
        store_a = TaskMemoryStore(base_path=git_repo)
        store_a.create("task-100", task_title="Task A")
        git_commit_and_push(git_repo, "Add task-100")

        # Machine B clones and creates task-101
        machine_b = clone_repo(bare_remote, tmp_path, "machine_b")
        store_b = TaskMemoryStore(base_path=machine_b)
        store_b.create("task-101", task_title="Task B")
        git_commit_and_push(machine_b, "Add task-101")

        # Machine A pulls and sees both
        git_pull(git_repo)
        assert store_a.exists("task-100")
        assert store_a.exists("task-101")

    def test_archive_sync(self, tmp_path, bare_remote, git_repo):
        """Test archived memories sync between machines."""
        # Machine A creates and archives
        store_a = TaskMemoryStore(base_path=git_repo)
        store_a.create("task-100", task_title="Done Task")
        store_a.archive("task-100")
        git_commit_and_push(git_repo, "Archive task-100")

        # Machine B sees archived memory
        machine_b = clone_repo(bare_remote, tmp_path, "machine_b")
        store_b = TaskMemoryStore(base_path=machine_b)

        assert not store_b.exists("task-100")  # Not in active
        archived = store_b.list_archived()
        assert "task-100" in archived


# --- Test: Conflict Resolution ---


@pytest.mark.git_sync
class TestConflictResolution:
    """Tests for handling merge conflicts.

    Uses git clone/push/pull between simulated machines.
    """

    def test_concurrent_append_no_conflict(self, tmp_path, bare_remote, git_repo):
        """Test appending to different tasks doesn't conflict."""
        # Setup: Create two tasks
        store_a = TaskMemoryStore(base_path=git_repo)
        store_a.create("task-100", task_title="Task 100")
        store_a.create("task-101", task_title="Task 101")
        git_commit_and_push(git_repo, "Initial tasks")

        # Machine B clones
        machine_b = clone_repo(bare_remote, tmp_path, "machine_b")
        store_b = TaskMemoryStore(base_path=machine_b)

        # Machine A appends to task-100
        store_a.append("task-100", "Update from A")
        git_commit_and_push(git_repo, "Update task-100")

        # Machine B appends to task-101
        store_b.append("task-101", "Update from B")

        # Machine B pulls (should merge cleanly)
        git_pull(machine_b)

        # Machine B pushes
        git_commit_and_push(machine_b, "Update task-101")

        # Machine A pulls and sees both updates
        git_pull(git_repo)
        content_100 = store_a.read("task-100")
        content_101 = store_a.read("task-101")

        assert "Update from A" in content_100
        assert "Update from B" in content_101

    def test_concurrent_state_changes(self, tmp_path, bare_remote, git_repo):
        """Test concurrent state changes to different tasks."""
        # Setup: Create tasks
        store_a = TaskMemoryStore(base_path=git_repo)
        store_a.create("task-100", task_title="Task 100")
        store_a.create("task-101", task_title="Task 101")
        git_commit_and_push(git_repo, "Initial tasks")

        # Machine B clones
        machine_b = clone_repo(bare_remote, tmp_path, "machine_b")
        store_b = TaskMemoryStore(base_path=machine_b)

        # Machine A archives task-100
        store_a.archive("task-100")
        git_commit_and_push(git_repo, "Archive task-100")

        # Machine B archives task-101
        store_b.archive("task-101")

        # Machine B pulls and pushes
        git_pull(machine_b)
        git_commit_and_push(machine_b, "Archive task-101")

        # Verify both archived on both machines
        git_pull(git_repo)

        assert "task-100" in store_a.list_archived()
        assert "task-101" in store_a.list_archived()

    def test_same_file_conflict_requires_manual_resolution(
        self, tmp_path, bare_remote, git_repo
    ):
        """Test that concurrent edits to same file may require manual resolution."""
        # Setup
        store_a = TaskMemoryStore(base_path=git_repo)
        store_a.create("task-100", task_title="Task 100")
        git_commit_and_push(git_repo, "Initial task")

        # Machine B clones
        machine_b = clone_repo(bare_remote, tmp_path, "machine_b")
        store_b = TaskMemoryStore(base_path=machine_b)

        # Both machines modify same file
        store_a.append("task-100", "Note from machine A", section="Notes")
        git_commit_and_push(git_repo, "A's update")

        store_b.append("task-100", "Note from machine B", section="Notes")

        # Machine B's push should fail due to conflict
        subprocess.run(
            ["git", "add", "."], cwd=machine_b, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "B's update"],
            cwd=machine_b,
            check=True,
            capture_output=True,
        )

        # Pull will have conflicts or auto-merge depending on content
        result = subprocess.run(
            ["git", "pull", "--no-rebase"],
            cwd=machine_b,
            capture_output=True,
            text=True,
        )

        # Either merged successfully or has conflicts
        assert result.returncode in [0, 1]  # 0=merged, 1=conflict


# --- Test: Merge Strategies ---


@pytest.mark.git_sync
class TestMergeStrategies:
    """Tests for different merge strategies.

    Uses git clone/push/pull between simulated machines.
    """

    def test_fast_forward_merge(self, tmp_path, bare_remote, git_repo):
        """Test fast-forward merge when no conflicts."""
        # Setup
        store_a = TaskMemoryStore(base_path=git_repo)
        store_a.create("task-100", task_title="Task 100")
        git_commit_and_push(git_repo, "Initial task")

        # Machine B clones
        machine_b = clone_repo(bare_remote, tmp_path, "machine_b")

        # Machine A makes changes
        store_a.append("task-100", "Update 1")
        git_commit_and_push(git_repo, "Update 1")

        store_a.append("task-100", "Update 2")
        git_commit_and_push(git_repo, "Update 2")

        # Machine B pulls (should fast-forward)
        result = subprocess.run(
            ["git", "pull"],
            cwd=machine_b,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        store_b = TaskMemoryStore(base_path=machine_b)
        content = store_b.read("task-100")
        assert "Update 1" in content
        assert "Update 2" in content

    def test_three_way_merge(self, tmp_path, bare_remote, git_repo):
        """Test three-way merge with non-conflicting changes."""
        # Setup with two tasks
        store_a = TaskMemoryStore(base_path=git_repo)
        store_a.create("task-100", task_title="Task 100")
        store_a.create("task-101", task_title="Task 101")
        git_commit_and_push(git_repo, "Initial tasks")

        # Machine B clones
        machine_b = clone_repo(bare_remote, tmp_path, "machine_b")
        store_b = TaskMemoryStore(base_path=machine_b)

        # Machine A updates task-100
        store_a.append("task-100", "A's note")
        git_commit_and_push(git_repo, "A's update")

        # Machine B updates task-101 (divergent history)
        store_b.append("task-101", "B's note")
        subprocess.run(
            ["git", "add", "."], cwd=machine_b, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "B's update"],
            cwd=machine_b,
            check=True,
            capture_output=True,
        )

        # Machine B pulls with three-way merge
        result = subprocess.run(
            ["git", "pull", "--no-rebase"],
            cwd=machine_b,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

        # Both changes present
        content_100 = store_b.read("task-100")
        content_101 = store_b.read("task-101")
        assert "A's note" in content_100
        assert "B's note" in content_101


# --- Test: Branch Sync ---


class TestBranchSync:
    """Tests for memory sync across branches."""

    def test_feature_branch_memory(self, tmp_path, bare_remote, git_repo):
        """Test memory changes on feature branch."""
        store = TaskMemoryStore(base_path=git_repo)

        # Create feature branch
        subprocess.run(
            ["git", "checkout", "-b", "feature-123"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        # Create memory on feature branch (just commit, don't push)
        store.create("task-100", task_title="Feature Task")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Add feature task"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        # Switch back to main - memory shouldn't exist
        subprocess.run(
            ["git", "checkout", "main"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        assert not store.exists("task-100")

        # Switch to feature - memory should exist
        subprocess.run(
            ["git", "checkout", "feature-123"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        assert store.exists("task-100")

    def test_merge_feature_branch_memory(self, tmp_path, bare_remote, git_repo):
        """Test memory persists after merging feature branch."""
        store = TaskMemoryStore(base_path=git_repo)

        # Create feature branch with memory
        subprocess.run(
            ["git", "checkout", "-b", "feature-123"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )
        store.create("task-100", task_title="Feature Task")
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Add feature task"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        # Merge to main
        subprocess.run(
            ["git", "checkout", "main"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "merge", "feature-123"],
            cwd=git_repo,
            check=True,
            capture_output=True,
        )

        # Memory should exist on main after merge
        assert store.exists("task-100")


# --- Test: Sync Performance ---


@pytest.mark.git_sync
class TestSyncPerformance:
    """Tests for sync performance with many memories.

    Uses git clone/push/pull between simulated machines.
    """

    def test_sync_multiple_memories(self, tmp_path, bare_remote, git_repo):
        """Test syncing multiple memory files at once."""
        store_a = TaskMemoryStore(base_path=git_repo)

        # Create multiple memories
        for i in range(10):
            store_a.create(f"task-{100 + i}", task_title=f"Task {100 + i}")

        git_commit_and_push(git_repo, "Add 10 tasks")

        # Machine B clones and gets all
        machine_b = clone_repo(bare_remote, tmp_path, "machine_b")
        store_b = TaskMemoryStore(base_path=machine_b)

        active = store_b.list_active()
        assert len(active) == 10

    def test_incremental_sync(self, tmp_path, bare_remote, git_repo):
        """Test incremental sync only transfers changes."""
        store_a = TaskMemoryStore(base_path=git_repo)

        # Initial batch
        for i in range(5):
            store_a.create(f"task-{100 + i}", task_title=f"Task {100 + i}")
        git_commit_and_push(git_repo, "Initial 5 tasks")

        # Machine B clones
        machine_b = clone_repo(bare_remote, tmp_path, "machine_b")
        store_b = TaskMemoryStore(base_path=machine_b)
        assert len(store_b.list_active()) == 5

        # Machine A adds more
        for i in range(5, 10):
            store_a.create(f"task-{100 + i}", task_title=f"Task {100 + i}")
        git_commit_and_push(git_repo, "Add 5 more tasks")

        # Machine B pulls incrementally
        git_pull(machine_b)
        assert len(store_b.list_active()) == 10


# --- Test: Edge Cases ---


class TestSyncEdgeCases:
    """Tests for edge cases in sync scenarios."""

    def test_sync_empty_memory_directory(self, tmp_path, bare_remote, git_repo):
        """Test syncing when memory directory is empty."""
        store_a = TaskMemoryStore(base_path=git_repo)

        # Ensure directory exists but is empty
        assert store_a.memory_dir.exists()
        assert len(store_a.list_active()) == 0

        # Machine B clones empty state
        machine_b = clone_repo(bare_remote, tmp_path, "machine_b")
        store_b = TaskMemoryStore(base_path=machine_b)

        assert len(store_b.list_active()) == 0

    @pytest.mark.git_sync
    def test_sync_after_delete(self, tmp_path, bare_remote, git_repo):
        """Test syncing deletions between machines."""
        store_a = TaskMemoryStore(base_path=git_repo)

        # Create then delete
        store_a.create("task-100", task_title="To Delete")
        git_commit_and_push(git_repo, "Add task")

        # Machine B clones
        machine_b = clone_repo(bare_remote, tmp_path, "machine_b")
        store_b = TaskMemoryStore(base_path=machine_b)
        assert store_b.exists("task-100")

        # Machine A deletes
        store_a.delete("task-100")
        git_commit_and_push(git_repo, "Delete task")

        # Machine B pulls - deletion should sync
        git_pull(machine_b)
        assert not store_b.exists("task-100")

    @pytest.mark.git_sync
    def test_sync_with_gitignore(self, tmp_path, bare_remote, git_repo):
        """Test that gitignored files don't sync."""
        store_a = TaskMemoryStore(base_path=git_repo)

        # Add gitignore for specific task
        gitignore = git_repo / "backlog" / "memory" / ".gitignore"
        gitignore.write_text("task-ignored.md\n")

        store_a.create("task-100", task_title="Tracked Task")

        # Create ignored file manually
        ignored_file = store_a.memory_dir / "task-ignored.md"
        ignored_file.write_text("# Ignored task memory")

        git_commit_and_push(git_repo, "Add tracked task and gitignore")

        # Machine B clones - should only see tracked task
        machine_b = clone_repo(bare_remote, tmp_path, "machine_b")
        store_b = TaskMemoryStore(base_path=machine_b)

        assert store_b.exists("task-100")
        assert not (store_b.memory_dir / "task-ignored.md").exists()
