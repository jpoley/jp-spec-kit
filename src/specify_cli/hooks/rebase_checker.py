"""Rebase enforcement module for detecting merge commits in branch history.

This module provides functions to detect merge commits in a branch's history
since it diverged from a base branch. It supports git worktrees and provides
clear error messages with remediation guidance.

Example:
    >>> from specify_cli.hooks.rebase_checker import find_merge_commits
    >>> commits = find_merge_commits("main", "feature/auth")
    >>> if commits:
    ...     print(f"Found {len(commits)} merge commits")
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class RebaseCheckerError(Exception):
    """Base exception for rebase checker errors."""

    pass


class GitCommandError(RebaseCheckerError):
    """Raised when a git command fails."""

    def __init__(self, command: str, returncode: int, stderr: str) -> None:
        self.command = command
        self.returncode = returncode
        self.stderr = stderr
        super().__init__(
            f"Git command failed (exit {returncode}): {command}\n{stderr.strip()}"
        )


class BranchNotFoundError(RebaseCheckerError):
    """Raised when a branch does not exist."""

    def __init__(self, branch: str) -> None:
        self.branch = branch
        super().__init__(f"Branch not found: {branch}")


class NotAGitRepositoryError(RebaseCheckerError):
    """Raised when not in a git repository."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path
        msg = "Not in a git repository"
        if path:
            msg = f"Not a git repository: {path}"
        super().__init__(msg)


@dataclass
class MergeCommit:
    """Represents a merge commit in the branch history.

    Attributes:
        sha: The full SHA-1 hash of the commit.
        short_sha: The abbreviated SHA (7 characters).
        subject: The first line of the commit message.
        parents: List of parent commit SHAs (merge commits have 2+ parents).
    """

    sha: str
    short_sha: str
    subject: str
    parents: list[str]

    @classmethod
    def from_log_line(cls, line: str) -> "MergeCommit":
        """Parse a merge commit from git log output.

        Expected format: SHA|SHORT_SHA|SUBJECT|PARENT1 PARENT2 ...

        Args:
            line: Single line from git log --format output.

        Returns:
            MergeCommit instance.

        Raises:
            ValueError: If the line format is invalid.
        """
        parts = line.split("|")
        if len(parts) < 4:
            raise ValueError(f"Invalid log line format: {line}")

        return cls(
            sha=parts[0],
            short_sha=parts[1],
            subject=parts[2],
            parents=parts[3].split() if parts[3] else [],
        )


@dataclass
class RebaseCheckResult:
    """Result of a rebase status check.

    Attributes:
        is_rebased: True if the branch has no merge commits.
        merge_commits: List of merge commits found (empty if rebased).
        base_branch: The branch rebased against.
        current_branch: The branch being checked.
        merge_base: The common ancestor commit SHA.
        remediation: Suggested command to fix the issue.
    """

    is_rebased: bool
    merge_commits: list[MergeCommit]
    base_branch: str
    current_branch: str
    merge_base: str
    remediation: Optional[str] = None

    @property
    def error_message(self) -> Optional[str]:
        """Generate error message if not rebased."""
        if self.is_rebased:
            return None

        count = len(self.merge_commits)
        commit_word = "commit" if count == 1 else "commits"

        lines = [
            f"Found {count} merge {commit_word} in branch '{self.current_branch}':",
            "",
        ]

        for mc in self.merge_commits[:5]:  # Limit to 5 for readability
            lines.append(f"  - {mc.short_sha}: {mc.subject[:60]}")

        if count > 5:
            lines.append(f"  ... and {count - 5} more")

        lines.extend(
            [
                "",
                f"Branch must be rebased on '{self.base_branch}' before pushing.",
            ]
        )

        return "\n".join(lines)


def _run_git_command(
    args: list[str],
    cwd: Optional[Path] = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Run a git command and return the result.

    Args:
        args: Git command arguments (without 'git' prefix).
        cwd: Working directory for the command.
        check: If True, raise GitCommandError on non-zero exit.

    Returns:
        CompletedProcess with stdout/stderr.

    Raises:
        GitCommandError: If check=True and command fails.
        NotAGitRepositoryError: If not in a git repository.
    """
    full_cmd = ["git"] + args

    try:
        result = subprocess.run(
            full_cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,  # Reasonable timeout for git operations
        )
    except subprocess.TimeoutExpired:
        raise GitCommandError(" ".join(full_cmd), -1, "Command timed out")
    except FileNotFoundError:
        raise GitCommandError(" ".join(full_cmd), -1, "git command not found")

    # Check for "not a git repository" error
    if result.returncode != 0 and "not a git repository" in result.stderr.lower():
        raise NotAGitRepositoryError(cwd)

    if check and result.returncode != 0:
        raise GitCommandError(" ".join(full_cmd), result.returncode, result.stderr)

    return result


def get_current_branch(cwd: Optional[Path] = None) -> str:
    """Get the name of the current branch.

    Handles both normal branches and detached HEAD state (worktrees).

    Args:
        cwd: Working directory (for worktree support).

    Returns:
        Branch name or 'HEAD' if detached.

    Raises:
        NotAGitRepositoryError: If not in a git repository.
    """
    # Try symbolic-ref first (normal branch)
    result = _run_git_command(
        ["symbolic-ref", "--short", "HEAD"],
        cwd=cwd,
        check=False,
    )

    if result.returncode == 0:
        return result.stdout.strip()

    # Detached HEAD - try to get the branch from HEAD
    result = _run_git_command(
        ["rev-parse", "--abbrev-ref", "HEAD"],
        cwd=cwd,
        check=True,
    )
    return result.stdout.strip()


def branch_exists(branch: str, cwd: Optional[Path] = None) -> bool:
    """Check if a branch exists (local or remote-tracking).

    Args:
        branch: Branch name to check.
        cwd: Working directory.

    Returns:
        True if branch exists.
    """
    result = _run_git_command(
        ["rev-parse", "--verify", f"refs/heads/{branch}"],
        cwd=cwd,
        check=False,
    )
    if result.returncode == 0:
        return True

    # Also check origin/branch for remote tracking
    result = _run_git_command(
        ["rev-parse", "--verify", f"refs/remotes/origin/{branch}"],
        cwd=cwd,
        check=False,
    )
    return result.returncode == 0


def get_merge_base(
    base_branch: str,
    current_branch: str,
    cwd: Optional[Path] = None,
) -> str:
    """Find the common ancestor of two branches.

    Args:
        base_branch: The base branch (e.g., 'main').
        current_branch: The feature branch.
        cwd: Working directory.

    Returns:
        SHA of the merge base commit.

    Raises:
        BranchNotFoundError: If either branch doesn't exist.
        GitCommandError: If merge-base fails.
    """
    # Resolve branches to SHAs to handle remote tracking branches
    base_ref = base_branch
    if not branch_exists(base_branch, cwd):
        # Try remote tracking branch
        if branch_exists(f"origin/{base_branch}", cwd):
            base_ref = f"origin/{base_branch}"
        else:
            raise BranchNotFoundError(base_branch)

    result = _run_git_command(
        ["merge-base", base_ref, current_branch],
        cwd=cwd,
        check=True,
    )
    return result.stdout.strip()


def find_merge_commits(
    base_branch: str,
    current_branch: Optional[str] = None,
    cwd: Optional[Path] = None,
) -> list[MergeCommit]:
    """Find all merge commits in a branch since diverging from base.

    This function detects merge commits by looking for commits with
    more than one parent in the branch history.

    Args:
        base_branch: The base branch to compare against (e.g., 'main').
        current_branch: The branch to check. If None, uses current branch.
        cwd: Working directory (for worktree support).

    Returns:
        List of MergeCommit objects, empty if no merge commits found.

    Raises:
        BranchNotFoundError: If branches don't exist.
        NotAGitRepositoryError: If not in a git repository.

    Example:
        >>> commits = find_merge_commits("main")
        >>> for c in commits:
        ...     print(f"{c.short_sha}: {c.subject}")
    """
    if current_branch is None:
        current_branch = get_current_branch(cwd)

    # Get merge base (common ancestor)
    merge_base = get_merge_base(base_branch, current_branch, cwd)

    # Find merge commits in range
    # --merges only shows commits with 2+ parents
    # Format: SHA|SHORT_SHA|SUBJECT|PARENTS
    result = _run_git_command(
        [
            "log",
            "--merges",
            "--format=%H|%h|%s|%P",
            f"{merge_base}..{current_branch}",
        ],
        cwd=cwd,
        check=True,
    )

    output = result.stdout.strip()
    if not output:
        return []

    merge_commits = []
    for line in output.split("\n"):
        if line.strip():
            try:
                merge_commits.append(MergeCommit.from_log_line(line))
            except ValueError:
                # Skip malformed lines
                continue

    return merge_commits


def is_branch_rebased(
    base_branch: str,
    current_branch: Optional[str] = None,
    cwd: Optional[Path] = None,
) -> bool:
    """Check if a branch is cleanly rebased on the base branch.

    A branch is considered "rebased" if it has no merge commits
    in its history since diverging from the base branch.

    Args:
        base_branch: The base branch to check against.
        current_branch: The branch to check. If None, uses current branch.
        cwd: Working directory (for worktree support).

    Returns:
        True if the branch has no merge commits.

    Example:
        >>> if not is_branch_rebased("main"):
        ...     print("Please rebase your branch")
    """
    merge_commits = find_merge_commits(base_branch, current_branch, cwd)
    return len(merge_commits) == 0


def check_rebase_status(
    base_branch: str,
    current_branch: Optional[str] = None,
    cwd: Optional[Path] = None,
) -> RebaseCheckResult:
    """Comprehensive rebase status check with remediation guidance.

    Args:
        base_branch: The base branch to check against.
        current_branch: The branch to check. If None, uses current branch.
        cwd: Working directory (for worktree support).

    Returns:
        RebaseCheckResult with full details and remediation.

    Example:
        >>> result = check_rebase_status("main")
        >>> if not result.is_rebased:
        ...     print(result.error_message)
        ...     print(f"Fix: {result.remediation}")
    """
    if current_branch is None:
        current_branch = get_current_branch(cwd)

    merge_base = get_merge_base(base_branch, current_branch, cwd)
    merge_commits = find_merge_commits(base_branch, current_branch, cwd)

    is_rebased = len(merge_commits) == 0

    remediation = None
    if not is_rebased:
        remediation = f"git rebase -i {base_branch}"

    return RebaseCheckResult(
        is_rebased=is_rebased,
        merge_commits=merge_commits,
        base_branch=base_branch,
        current_branch=current_branch,
        merge_base=merge_base,
        remediation=remediation,
    )


def format_rebase_error(
    result: RebaseCheckResult,
    *,
    include_commits: bool = True,
    include_remediation: bool = True,
) -> str:
    """Format a rebase check failure for display.

    Args:
        result: The RebaseCheckResult to format.
        include_commits: Whether to list the merge commits.
        include_remediation: Whether to include the fix command.

    Returns:
        Formatted error message string.
    """
    if result.is_rebased:
        return ""

    lines = [
        "✗ Branch is not rebased",
        "",
    ]

    count = len(result.merge_commits)
    commit_word = "commit" if count == 1 else "commits"
    lines.append(
        f"Found {count} merge {commit_word} in '{result.current_branch}' "
        f"since diverging from '{result.base_branch}':"
    )

    if include_commits:
        lines.append("")
        for mc in result.merge_commits[:5]:
            subject = mc.subject[:50] + "..." if len(mc.subject) > 50 else mc.subject
            lines.append(f"  {mc.short_sha}  {subject}")

        if count > 5:
            lines.append(f"  ... and {count - 5} more merge commits")

    if include_remediation and result.remediation:
        lines.extend(
            [
                "",
                "To fix this, rebase your branch:",
                "",
                f"  {result.remediation}",
                "",
                "This will replay your commits on top of the latest "
                f"'{result.base_branch}'.",
            ]
        )

    return "\n".join(lines)
