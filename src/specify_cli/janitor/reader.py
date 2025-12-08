"""Janitor state reader module.

This module provides functions to read janitor state files including
the last run timestamp and pending cleanup items.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class PendingBranch:
    """A branch pending cleanup.

    Attributes:
        name: Branch name.
        reason: Why it's pending cleanup (e.g., "upstream gone", "merged").
        identified_at: When the branch was identified for cleanup.
    """

    name: str
    reason: str
    identified_at: Optional[datetime] = None


@dataclass
class PendingWorktree:
    """A worktree pending cleanup.

    Attributes:
        path: Absolute path to the worktree.
        identified_at: When the worktree was identified for cleanup.
    """

    path: str
    identified_at: Optional[datetime] = None


@dataclass
class PendingCleanup:
    """Pending cleanup items from janitor scan.

    Attributes:
        last_updated: When the pending cleanup was last updated.
        merged_branches: Branches that are merged/gone and can be deleted.
        orphaned_worktrees: Worktrees that are orphaned and can be pruned.
        non_compliant_branches: Branches with naming issues (warnings only).
    """

    last_updated: Optional[datetime] = None
    merged_branches: list[PendingBranch] = field(default_factory=list)
    orphaned_worktrees: list[PendingWorktree] = field(default_factory=list)
    non_compliant_branches: dict[str, str] = field(default_factory=dict)

    @property
    def total_pending(self) -> int:
        """Total number of items pending cleanup."""
        return len(self.merged_branches) + len(self.orphaned_worktrees)

    @property
    def has_pending(self) -> bool:
        """Whether there are any items pending cleanup."""
        return self.total_pending > 0 or len(self.non_compliant_branches) > 0

    @property
    def summary(self) -> str:
        """Human-readable summary of pending items."""
        parts = []
        if self.merged_branches:
            parts.append(f"{len(self.merged_branches)} branch(es) to prune")
        if self.orphaned_worktrees:
            parts.append(f"{len(self.orphaned_worktrees)} worktree(s) to clean")
        if self.non_compliant_branches:
            parts.append(
                f"{len(self.non_compliant_branches)} branch(es) with naming issues"
            )
        return ", ".join(parts) if parts else "no cleanup needed"


@dataclass
class JanitorState:
    """Complete janitor state.

    Attributes:
        last_run: When janitor was last run successfully.
        pending: Pending cleanup items.
        state_dir: Path to the state directory.
    """

    last_run: Optional[datetime] = None
    pending: PendingCleanup = field(default_factory=PendingCleanup)
    state_dir: Optional[Path] = None

    @property
    def needs_run(self) -> bool:
        """Whether janitor should be run (has pending items)."""
        return self.pending.has_pending

    @property
    def hours_since_last_run(self) -> Optional[float]:
        """Hours since last janitor run, or None if never run."""
        if self.last_run is None:
            return None
        delta = datetime.now(timezone.utc) - self.last_run
        return delta.total_seconds() / 3600


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse ISO 8601 datetime string."""
    if not value:
        return None
    try:
        # Handle timezone-aware and naive datetime strings
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def read_janitor_timestamp(state_dir: Path) -> Optional[datetime]:
    """Read the janitor-last-run timestamp.

    Args:
        state_dir: Path to .specify/state/ directory.

    Returns:
        Datetime of last run, or None if never run.
    """
    timestamp_file = state_dir / "janitor-last-run"
    if not timestamp_file.exists():
        return None

    try:
        content = timestamp_file.read_text(encoding="utf-8").strip()
        return _parse_datetime(content)
    except OSError:
        return None


def read_pending_cleanup(state_dir: Path) -> PendingCleanup:
    """Read pending cleanup items from state file.

    Args:
        state_dir: Path to .specify/state/ directory.

    Returns:
        PendingCleanup with parsed items, or empty if file doesn't exist.
    """
    cleanup_file = state_dir / "pending-cleanup.json"
    if not cleanup_file.exists():
        return PendingCleanup()

    try:
        content = cleanup_file.read_text(encoding="utf-8")
        data = json.loads(content)
    except (OSError, json.JSONDecodeError):
        return PendingCleanup()

    # Parse merged branches
    merged = []
    for branch_data in data.get("merged_branches", []):
        if isinstance(branch_data, dict):
            merged.append(
                PendingBranch(
                    name=branch_data.get("name", ""),
                    reason=branch_data.get("reason", "unknown"),
                    identified_at=_parse_datetime(branch_data.get("identified_at")),
                )
            )
        elif isinstance(branch_data, str):
            merged.append(PendingBranch(name=branch_data, reason="unknown"))

    # Parse orphaned worktrees
    worktrees = []
    for wt_data in data.get("orphaned_worktrees", []):
        if isinstance(wt_data, dict):
            worktrees.append(
                PendingWorktree(
                    path=wt_data.get("path", ""),
                    identified_at=_parse_datetime(wt_data.get("identified_at")),
                )
            )
        elif isinstance(wt_data, str):
            worktrees.append(PendingWorktree(path=wt_data))

    # Parse non-compliant branches
    non_compliant = data.get("non_compliant_branches", {})
    if not isinstance(non_compliant, dict):
        non_compliant = {}

    return PendingCleanup(
        last_updated=_parse_datetime(data.get("last_updated")),
        merged_branches=merged,
        orphaned_worktrees=worktrees,
        non_compliant_branches=non_compliant,
    )


def read_janitor_state(state_dir: Path) -> JanitorState:
    """Read complete janitor state.

    Args:
        state_dir: Path to .specify/state/ directory.

    Returns:
        JanitorState with last run time and pending cleanup items.
    """
    return JanitorState(
        last_run=read_janitor_timestamp(state_dir),
        pending=read_pending_cleanup(state_dir),
        state_dir=state_dir,
    )


def format_janitor_warning(state: JanitorState) -> Optional[str]:
    """Format a warning message if janitor should be run.

    Args:
        state: Current janitor state.

    Returns:
        Warning message string, or None if no warning needed.
    """
    if not state.needs_run:
        return None

    pending = state.pending
    lines = [
        "⚠ Repository cleanup pending:",
    ]

    if pending.merged_branches:
        lines.append(f"  - {len(pending.merged_branches)} merged branch(es) to prune")

    if pending.orphaned_worktrees:
        lines.append(f"  - {len(pending.orphaned_worktrees)} orphaned worktree(s)")

    if pending.non_compliant_branches:
        lines.append(
            f"  - {len(pending.non_compliant_branches)} branch(es) with naming issues"
        )

    lines.append("")
    lines.append("Run `/jpspec:github-janitor prune` to clean up.")

    return "\n".join(lines)
