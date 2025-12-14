"""Backlog CLI shim with automatic event emission.

This module provides wrapper functions around the backlog CLI that automatically
emit flowspec events for task lifecycle operations. This is the preferred way
for flowspec agents and workflows to interact with backlog.md.

The shim ensures consistent event emission regardless of whether operations
are triggered via CLI, MCP tools, or programmatic calls.

Design:
    - Each function wraps a backlog CLI operation
    - Events are emitted AFTER successful operations (fail-safe)
    - Functions return structured results including operation success and event emission status
    - All functions are designed to be called from Python code (agents, workflows)

Example:
    >>> from specify_cli.backlog.shim import task_edit, task_create
    >>>
    >>> # Create a task with auto event emission
    >>> result = task_create(title="Implement feature", priority="high")
    >>> if result.success:
    ...     print(f"Created {result.task_id}")
    >>>
    >>> # Edit task status with auto event emission
    >>> result = task_edit("task-123", status="Done")
    >>> # Automatically emits task.completed event
"""

from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ShimResult:
    """Result of a backlog shim operation.

    Attributes:
        success: Whether the backlog operation succeeded.
        exit_code: Exit code from the backlog CLI.
        output: Stdout from the backlog CLI.
        stderr: Stderr from the backlog CLI.
        task_id: Task ID (extracted from output for create operations, or passed in).
        event_emitted: Whether an event was successfully emitted.
        events_emitted: List of event types that were emitted (e.g., ['task.completed', 'task.ac_checked']).
        error: Error message if operation failed.
        metadata: Additional operation metadata (e.g., status, labels, priority).
    """

    success: bool
    exit_code: int
    output: str
    stderr: str
    task_id: str | None = None
    event_emitted: bool = False
    events_emitted: list[str] = field(default_factory=list)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def _run_backlog_command(args: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """Run a backlog CLI command and capture output.

    Args:
        args: Command arguments (excluding 'backlog').
        timeout: Command timeout in seconds.

    Returns:
        Tuple of (exit_code, stdout, stderr).
    """
    cmd = ["backlog"] + args
    logger.debug(f"Running backlog command: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        logger.error(f"Backlog command timed out after {timeout}s: {' '.join(cmd)}")
        return -1, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        logger.error("Backlog CLI not found. Is it installed?")
        return -1, "", "Backlog CLI not found"
    except Exception as e:
        logger.error(f"Backlog command failed: {e}")
        return -1, "", str(e)


def _emit_event(
    event_type: str,
    task_id: str,
    workspace_root: Path | None = None,
    **kwargs: Any,
) -> bool:
    """Emit a flowspec event for a task operation.

    Args:
        event_type: Event type (e.g., 'task.created', 'task.completed').
        task_id: Task identifier.
        workspace_root: Project root directory. Defaults to current directory.
        **kwargs: Additional event context.

    Returns:
        True if event was emitted successfully, False otherwise.
    """
    if workspace_root is None:
        workspace_root = Path.cwd()

    try:
        # Import here to avoid circular imports and make this module standalone
        from specify_cli.hooks.events import Event
        from specify_cli.hooks.emitter import emit_event as _emit

        # Build context
        context: dict[str, Any] = {"task_id": task_id}
        context.update(kwargs)

        # Create event
        event = Event(
            event_type=event_type,
            project_root=str(workspace_root),
            context=context,
        )

        # Emit event
        results = _emit(event, workspace_root=workspace_root)

        # Log results
        for result in results:
            if result.success:
                logger.info(f"Hook '{result.hook_name}' executed for {event_type}")
            else:
                logger.warning(f"Hook '{result.hook_name}' failed: {result.error}")

        return True

    except ImportError as e:
        logger.warning(f"Could not import hooks module: {e}")
        return False
    except Exception as e:
        logger.warning(f"Failed to emit event {event_type}: {e}")
        return False


def _extract_task_id_from_create_output(output: str) -> str | None:
    """Extract task ID from backlog create command output.

    Args:
        output: Stdout from backlog task create command.

    Returns:
        Task ID (e.g., 'task-123') or None if not found.
    """
    # Pattern matches "Created task task-123" or similar
    pattern = r"Created\s+task\s+(task-\d+(?:\.\d+)*)"
    match = re.search(pattern, output, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def task_create(
    title: str,
    description: str | None = None,
    priority: str | None = None,
    labels: list[str] | None = None,
    acceptance_criteria: list[str] | None = None,
    parent_task_id: str | None = None,
    workspace_root: Path | None = None,
) -> ShimResult:
    """Create a new backlog task with automatic event emission.

    This function:
    1. Calls `backlog task create` with the provided arguments
    2. Extracts the created task ID from output
    3. Emits a `task.created` event

    Args:
        title: Task title (required).
        description: Task description.
        priority: Priority level ('high', 'medium', 'low').
        labels: List of labels to apply.
        acceptance_criteria: List of acceptance criteria.
        parent_task_id: Parent task ID for subtasks.
        workspace_root: Project root directory.

    Returns:
        ShimResult with operation details.

    Example:
        >>> result = task_create(
        ...     title="Implement user authentication",
        ...     priority="high",
        ...     labels=["backend", "security"],
        ...     acceptance_criteria=["Users can login", "Sessions expire after 1h"],
        ... )
        >>> if result.success:
        ...     print(f"Created {result.task_id}")
    """
    if workspace_root is None:
        workspace_root = Path.cwd()

    # Build command arguments
    args = ["task", "create", title]

    if description:
        args.extend(["--description", description])
    if priority:
        args.extend(["--priority", priority])
    if labels:
        for label in labels:
            args.extend(["--label", label])
    if acceptance_criteria:
        for ac in acceptance_criteria:
            args.extend(["--ac", ac])
    if parent_task_id:
        args.extend(["--parent", parent_task_id])

    # Run backlog command
    exit_code, stdout, stderr = _run_backlog_command(args)

    if exit_code != 0:
        return ShimResult(
            success=False,
            exit_code=exit_code,
            output=stdout,
            stderr=stderr,
            error=stderr or "Task creation failed",
        )

    # Extract task ID from output
    task_id = _extract_task_id_from_create_output(stdout)

    if not task_id:
        logger.warning(f"Could not extract task ID from output: {stdout}")

    # Emit task.created event
    event_emitted = False
    if task_id:
        event_emitted = _emit_event(
            event_type="task.created",
            task_id=task_id,
            workspace_root=workspace_root,
            title=title,
            priority=priority,
            labels=labels,
        )

    return ShimResult(
        success=True,
        exit_code=exit_code,
        output=stdout,
        stderr=stderr,
        task_id=task_id,
        event_emitted=event_emitted,
        events_emitted=["task.created"] if event_emitted else [],
        metadata={
            "title": title,
            "priority": priority,
            "labels": labels,
        },
    )


def task_edit(
    task_id: str,
    status: str | None = None,
    title: str | None = None,
    priority: str | None = None,
    labels: list[str] | None = None,
    assignees: list[str] | None = None,
    check_ac: list[int] | None = None,
    uncheck_ac: list[int] | None = None,
    plan: str | None = None,
    notes: str | None = None,
    workspace_root: Path | None = None,
) -> ShimResult:
    """Edit a backlog task with automatic event emission.

    This function:
    1. Calls `backlog task edit` with the provided arguments
    2. Detects what type of change was made
    3. Emits appropriate event(s):
       - `task.completed` if status changed to "Done"
       - `task.status_changed` if status changed to another value
       - `task.ac_checked` if acceptance criteria were checked/unchecked

    Args:
        task_id: Task ID to edit (e.g., 'task-123').
        status: New status value.
        title: New title.
        priority: New priority.
        labels: New labels (replaces existing).
        assignees: New assignees (replaces existing).
        check_ac: Acceptance criteria indices to check (1-based).
        uncheck_ac: Acceptance criteria indices to uncheck (1-based).
        plan: Implementation plan content.
        notes: Implementation notes content.
        workspace_root: Project root directory.

    Returns:
        ShimResult with operation details.

    Example:
        >>> # Mark task as done
        >>> result = task_edit("task-123", status="Done")
        >>> # Emits task.completed event
        >>>
        >>> # Check acceptance criteria
        >>> result = task_edit("task-123", check_ac=[1, 2])
        >>> # Emits task.ac_checked event
    """
    if workspace_root is None:
        workspace_root = Path.cwd()

    # Build command arguments
    args = ["task", "edit", task_id]

    if status:
        args.extend(["-s", status])
    if title:
        args.extend(["--title", title])
    if priority:
        args.extend(["--priority", priority])
    if labels:
        for label in labels:
            args.extend(["-l", label])
    if assignees:
        for assignee_name in assignees:
            args.extend(["-a", assignee_name])
    if check_ac:
        for ac_num in check_ac:
            args.extend(["--check-ac", str(ac_num)])
    if uncheck_ac:
        for ac_num in uncheck_ac:
            args.extend(["--uncheck-ac", str(ac_num)])
    if plan:
        args.extend(["--plan", plan])
    if notes:
        args.extend(["--notes", notes])

    # Run backlog command
    exit_code, stdout, stderr = _run_backlog_command(args)

    if exit_code != 0:
        return ShimResult(
            success=False,
            exit_code=exit_code,
            output=stdout,
            stderr=stderr,
            task_id=task_id,
            error=stderr or "Task edit failed",
        )

    # Determine which event(s) to emit
    events_emitted: list[str] = []

    # Status change events
    if status:
        if status.lower() == "done":
            if _emit_event(
                event_type="task.completed",
                task_id=task_id,
                workspace_root=workspace_root,
                status_to="Done",
            ):
                events_emitted.append("task.completed")
        else:
            if _emit_event(
                event_type="task.status_changed",
                task_id=task_id,
                workspace_root=workspace_root,
                status_to=status,
            ):
                events_emitted.append("task.status_changed")

    # AC check/uncheck events
    if check_ac or uncheck_ac:
        if _emit_event(
            event_type="task.ac_checked",
            task_id=task_id,
            workspace_root=workspace_root,
            checked=check_ac or [],
            unchecked=uncheck_ac or [],
        ):
            events_emitted.append("task.ac_checked")

    return ShimResult(
        success=True,
        exit_code=exit_code,
        output=stdout,
        stderr=stderr,
        task_id=task_id,
        event_emitted=len(events_emitted) > 0,
        events_emitted=events_emitted,
        metadata={
            "status": status,
            "check_ac": check_ac,
            "uncheck_ac": uncheck_ac,
        },
    )


def task_view(
    task_id: str,
    plain: bool = True,
) -> ShimResult:
    """View a backlog task.

    This is a read-only operation that does NOT emit events.

    Args:
        task_id: Task ID to view.
        plain: Use plain text output (AI-friendly).

    Returns:
        ShimResult with task content in output.
    """
    args = ["task", task_id]
    if plain:
        args.append("--plain")

    exit_code, stdout, stderr = _run_backlog_command(args)

    return ShimResult(
        success=exit_code == 0,
        exit_code=exit_code,
        output=stdout,
        stderr=stderr,
        task_id=task_id,
        error=stderr if exit_code != 0 else None,
    )


def task_list(
    status: str | None = None,
    labels: list[str] | None = None,
    assignee: str | None = None,
    plain: bool = True,
) -> ShimResult:
    """List backlog tasks.

    This is a read-only operation that does NOT emit events.

    Args:
        status: Filter by status.
        labels: Filter by labels.
        assignee: Filter by assignee.
        plain: Use plain text output (AI-friendly).

    Returns:
        ShimResult with task list in output.
    """
    args = ["task", "list"]

    if status:
        args.extend(["-s", status])
    if labels:
        for label in labels:
            args.extend(["-l", label])
    if assignee:
        args.extend(["-a", assignee])
    if plain:
        args.append("--plain")

    exit_code, stdout, stderr = _run_backlog_command(args)

    return ShimResult(
        success=exit_code == 0,
        exit_code=exit_code,
        output=stdout,
        stderr=stderr,
        error=stderr if exit_code != 0 else None,
    )


def task_search(
    query: str,
    status: str | None = None,
    priority: str | None = None,
    limit: int | None = None,
) -> ShimResult:
    """Search backlog tasks.

    This is a read-only operation that does NOT emit events.

    Args:
        query: Search query string.
        status: Filter by status.
        priority: Filter by priority.
        limit: Maximum number of results.

    Returns:
        ShimResult with search results in output.
    """
    args = ["task", "search", query]

    if status:
        args.extend(["--status", status])
    if priority:
        args.extend(["--priority", priority])
    if limit:
        args.extend(["--limit", str(limit)])

    exit_code, stdout, stderr = _run_backlog_command(args)

    return ShimResult(
        success=exit_code == 0,
        exit_code=exit_code,
        output=stdout,
        stderr=stderr,
        error=stderr if exit_code != 0 else None,
    )


def task_archive(
    task_id: str,
    workspace_root: Path | None = None,
) -> ShimResult:
    """Archive a backlog task with automatic event emission.

    This function:
    1. Calls `backlog task archive`
    2. Emits a `task.archived` event

    Args:
        task_id: Task ID to archive.
        workspace_root: Project root directory.

    Returns:
        ShimResult with operation details.
    """
    if workspace_root is None:
        workspace_root = Path.cwd()

    args = ["task", "archive", task_id]

    exit_code, stdout, stderr = _run_backlog_command(args)

    if exit_code != 0:
        return ShimResult(
            success=False,
            exit_code=exit_code,
            output=stdout,
            stderr=stderr,
            task_id=task_id,
            error=stderr or "Task archive failed",
        )

    # Emit task.archived event
    event_emitted = _emit_event(
        event_type="task.archived",
        task_id=task_id,
        workspace_root=workspace_root,
    )

    return ShimResult(
        success=True,
        exit_code=exit_code,
        output=stdout,
        stderr=stderr,
        task_id=task_id,
        event_emitted=event_emitted,
        events_emitted=["task.archived"] if event_emitted else [],
    )


# --- Convenience aliases ---


def create_task(
    title: str,
    description: str | None = None,
    priority: str | None = None,
    labels: list[str] | None = None,
    acceptance_criteria: list[str] | None = None,
    workspace_root: Path | None = None,
) -> ShimResult:
    """Alias for task_create (more Pythonic naming)."""
    return task_create(
        title=title,
        description=description,
        priority=priority,
        labels=labels,
        acceptance_criteria=acceptance_criteria,
        workspace_root=workspace_root,
    )


def edit_task(
    task_id: str,
    status: str | None = None,
    check_ac: list[int] | None = None,
    workspace_root: Path | None = None,
    **kwargs: Any,
) -> ShimResult:
    """Alias for task_edit (more Pythonic naming)."""
    return task_edit(
        task_id=task_id,
        status=status,
        check_ac=check_ac,
        workspace_root=workspace_root,
        **kwargs,
    )


def complete_task(
    task_id: str,
    workspace_root: Path | None = None,
) -> ShimResult:
    """Mark a task as Done (convenience wrapper).

    Args:
        task_id: Task ID to complete.
        workspace_root: Project root directory.

    Returns:
        ShimResult with operation details.

    Example:
        >>> result = complete_task("task-123")
        >>> # Equivalent to: task_edit("task-123", status="Done")
    """
    return task_edit(task_id=task_id, status="Done", workspace_root=workspace_root)


def start_task(
    task_id: str,
    assignees: list[str] | None = None,
    workspace_root: Path | None = None,
) -> ShimResult:
    """Start a task by setting status to In Progress (convenience wrapper).

    Args:
        task_id: Task ID to start.
        assignees: List of assignees to add.
        workspace_root: Project root directory.

    Returns:
        ShimResult with operation details.

    Example:
        >>> result = start_task("task-123", assignees=["@backend-engineer"])
        >>> # Equivalent to: task_edit("task-123", status="In Progress", assignees=["@backend-engineer"])
    """
    return task_edit(
        task_id=task_id,
        status="In Progress",
        assignees=assignees,
        workspace_root=workspace_root,
    )


def check_acceptance_criteria(
    task_id: str,
    criteria_indices: list[int],
    workspace_root: Path | None = None,
) -> ShimResult:
    """Check acceptance criteria on a task (convenience wrapper).

    Args:
        task_id: Task ID.
        criteria_indices: List of AC indices to check (1-based).
        workspace_root: Project root directory.

    Returns:
        ShimResult with operation details.

    Example:
        >>> result = check_acceptance_criteria("task-123", [1, 2, 3])
        >>> # Equivalent to: task_edit("task-123", check_ac=[1, 2, 3])
    """
    return task_edit(
        task_id=task_id,
        check_ac=criteria_indices,
        workspace_root=workspace_root,
    )
