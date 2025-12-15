"""JSONL Event Writer with daily rotation and schema validation.

This module provides the core event persistence layer for the flowspec
event system. Events are written to JSONL files with automatic daily
rotation and configurable retention.

Features:
    - JSONL format for streaming-friendly event logs
    - Daily file rotation (events-YYYY-MM-DD.jsonl)
    - Configurable retention policy with automatic cleanup
    - Schema validation before write (v1.1.0)
    - Thread-safe synchronous writes
    - Non-blocking async writes for performance-critical paths
    - Fail-safe design (write failures don't break workflows)

Directory Structure:
    .flowspec/events/
        events-2025-12-15.jsonl
        events-2025-12-14.jsonl
        ...

Example:
    >>> from specify_cli.events.writer import emit_event, EventWriterConfig
    >>>
    >>> # Simple emission with defaults
    >>> emit_event(
    ...     event_type="lifecycle.started",
    ...     agent_id="@backend-engineer",
    ...     message="Starting implementation"
    ... )
    >>>
    >>> # Custom configuration
    >>> config = EventWriterConfig(
    ...     events_dir=Path(".flowspec/events"),
    ...     retention_days=30,
    ...     validate_schema=True
    ... )
    >>> writer = EventWriter(config)
    >>> writer.write_event({...})
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Version constant
SCHEMA_VERSION = "1.1.0"

# Default events directory relative to project root
DEFAULT_EVENTS_DIR = ".flowspec/events"

# Default retention in days
DEFAULT_RETENTION_DAYS = 30


@dataclass
class EventWriterConfig:
    """Configuration for the JSONL event writer.

    Attributes:
        events_dir: Directory for event files. Defaults to .flowspec/events.
        retention_days: Number of days to retain event files. Defaults to 30.
        validate_schema: Whether to validate events against schema before write.
        fail_silently: If True, suppress write errors instead of raising.

    Example:
        >>> config = EventWriterConfig(
        ...     events_dir=Path("/project/.flowspec/events"),
        ...     retention_days=14,
        ...     validate_schema=True
        ... )
    """

    events_dir: Path = field(default_factory=lambda: Path(DEFAULT_EVENTS_DIR))
    retention_days: int = DEFAULT_RETENTION_DAYS
    validate_schema: bool = True
    fail_silently: bool = True

    def __post_init__(self) -> None:
        """Ensure events_dir is a Path object."""
        if isinstance(self.events_dir, str):
            self.events_dir = Path(self.events_dir)


class EventWriter:
    """JSONL event file writer with daily rotation.

    Thread-safe writer that persists events to JSONL files. Files are
    automatically rotated daily and old files are cleaned up based on
    the retention policy.

    Attributes:
        config: Writer configuration.
        _lock: Threading lock for thread-safe writes.
        _current_date: Current date for rotation tracking.
        _current_file: Currently open file handle.

    Example:
        >>> writer = EventWriter(EventWriterConfig())
        >>> event = {
        ...     "version": "1.1.0",
        ...     "event_type": "lifecycle.started",
        ...     "timestamp": "2025-12-15T10:00:00Z",
        ...     "agent_id": "@backend-engineer"
        ... }
        >>> success = writer.write_event(event)
    """

    def __init__(self, config: EventWriterConfig | None = None) -> None:
        """Initialize the event writer.

        Args:
            config: Writer configuration. Uses defaults if not provided.
        """
        self.config = config or EventWriterConfig()
        self._lock = threading.Lock()
        self._current_date: str | None = None
        self._current_file: Any = None  # File handle

    def _ensure_directory(self) -> None:
        """Ensure the events directory exists."""
        self.config.events_dir.mkdir(parents=True, exist_ok=True)

    def _get_filename_for_date(self, date_str: str) -> Path:
        """Get the filename for a given date.

        Args:
            date_str: Date string in YYYY-MM-DD format.

        Returns:
            Path to the event file for that date.
        """
        return self.config.events_dir / f"events-{date_str}.jsonl"

    def _get_current_filename(self) -> Path:
        """Get the filename for the current date.

        Returns:
            Path to today's event file.
        """
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return self._get_filename_for_date(today)

    def _validate_event(self, event: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate event against schema.

        Args:
            event: Event dictionary to validate.

        Returns:
            Tuple of (is_valid, error_messages).
        """
        if not self.config.validate_schema:
            return True, []

        try:
            from specify_cli.hooks.validators import EventValidator

            return EventValidator.validate(event)
        except ImportError:
            logger.warning("EventValidator not available, skipping validation")
            return True, []
        except Exception as e:
            logger.warning(f"Validation error: {e}")
            return False, [str(e)]

    def _cleanup_old_files(self) -> int:
        """Remove event files older than retention period.

        Returns:
            Number of files removed.
        """
        if not self.config.events_dir.exists():
            return 0

        cutoff_date = datetime.now(timezone.utc) - timedelta(
            days=self.config.retention_days
        )
        removed_count = 0

        for file_path in self.config.events_dir.glob("events-*.jsonl"):
            try:
                # Extract date from filename
                date_str = file_path.stem.replace("events-", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )

                if file_date < cutoff_date:
                    file_path.unlink()
                    removed_count += 1
                    logger.info(f"Removed old event file: {file_path.name}")
            except (ValueError, OSError) as e:
                logger.warning(f"Could not process file {file_path}: {e}")

        return removed_count

    def write_event(self, event: dict[str, Any]) -> bool:
        """Write a single event to the JSONL file.

        Thread-safe write with automatic rotation and validation.

        Args:
            event: Event dictionary to write.

        Returns:
            True if write succeeded, False otherwise.

        Raises:
            ValueError: If event fails validation and fail_silently is False.
            IOError: If write fails and fail_silently is False.
        """
        # Validate event
        is_valid, errors = self._validate_event(event)
        if not is_valid:
            error_msg = f"Event validation failed: {'; '.join(errors)}"
            if self.config.fail_silently:
                logger.warning(error_msg)
                return False
            raise ValueError(error_msg)

        with self._lock:
            try:
                self._ensure_directory()
                file_path = self._get_current_filename()

                # Write event as single line JSON
                with open(file_path, "a", encoding="utf-8") as f:
                    json_line = json.dumps(event, separators=(",", ":"))
                    f.write(json_line + "\n")

                logger.debug(f"Event written to {file_path}: {event.get('event_type')}")
                return True

            except OSError as e:
                error_msg = f"Failed to write event: {e}"
                if self.config.fail_silently:
                    logger.error(error_msg)
                    return False
                raise IOError(error_msg) from e

    def write_events(self, events: list[dict[str, Any]]) -> int:
        """Write multiple events to the JSONL file.

        Args:
            events: List of event dictionaries.

        Returns:
            Number of events successfully written.
        """
        written = 0
        for event in events:
            if self.write_event(event):
                written += 1
        return written

    def cleanup(self) -> int:
        """Run retention cleanup to remove old event files.

        Returns:
            Number of files removed.
        """
        return self._cleanup_old_files()

    def read_events(
        self,
        date: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """Read events from JSONL files.

        Args:
            date: Specific date in YYYY-MM-DD format (reads single file).
            start_date: Start date for range query (inclusive).
            end_date: End date for range query (inclusive).

        Returns:
            List of event dictionaries.
        """
        events: list[dict[str, Any]] = []

        if date:
            # Single date
            file_path = self._get_filename_for_date(date)
            if file_path.exists():
                events.extend(self._read_file(file_path))
        elif start_date or end_date:
            # Date range
            start = (
                datetime.strptime(start_date, "%Y-%m-%d")
                if start_date
                else datetime.min
            )
            end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.max

            for file_path in sorted(self.config.events_dir.glob("events-*.jsonl")):
                try:
                    date_str = file_path.stem.replace("events-", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if start <= file_date <= end:
                        events.extend(self._read_file(file_path))
                except ValueError:
                    continue
        else:
            # All events (today only for performance)
            file_path = self._get_current_filename()
            if file_path.exists():
                events.extend(self._read_file(file_path))

        return events

    def _read_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Read events from a single JSONL file.

        Args:
            file_path: Path to JSONL file.

        Returns:
            List of event dictionaries.
        """
        events: list[dict[str, Any]] = []
        try:
            with open(file_path, encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            logger.warning(
                                f"Invalid JSON at {file_path}:{line_num}: {e}"
                            )
        except OSError as e:
            logger.error(f"Failed to read {file_path}: {e}")
        return events


# --- Global writer instance ---

_default_writer: EventWriter | None = None
_writer_lock = threading.Lock()


def get_default_writer(
    events_dir: Path | str | None = None,
    project_root: Path | str | None = None,
) -> EventWriter:
    """Get or create the default event writer.

    Args:
        events_dir: Override events directory. If not specified, uses
            project_root/.flowspec/events or cwd/.flowspec/events.
        project_root: Project root directory for default events_dir.

    Returns:
        Singleton EventWriter instance.
    """
    global _default_writer

    with _writer_lock:
        if _default_writer is None:
            if events_dir is None:
                if project_root:
                    events_dir = Path(project_root) / DEFAULT_EVENTS_DIR
                else:
                    events_dir = Path.cwd() / DEFAULT_EVENTS_DIR

            config = EventWriterConfig(events_dir=Path(events_dir))
            _default_writer = EventWriter(config)

        return _default_writer


def reset_default_writer() -> None:
    """Reset the default writer (for testing)."""
    global _default_writer
    with _writer_lock:
        _default_writer = None


# --- Convenience functions ---


def _now_utc_iso() -> str:
    """Get current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _build_event(
    event_type: str,
    agent_id: str,
    message: str | None = None,
    progress: float | None = None,
    context: dict[str, Any] | None = None,
    task: dict[str, Any] | None = None,
    git: dict[str, Any] | None = None,
    decision: dict[str, Any] | None = None,
    action: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Build a v1.1.0 event dictionary.

    Args:
        event_type: Namespaced event type (e.g., "lifecycle.started").
        agent_id: Agent identifier (e.g., "@backend-engineer").
        message: Human-readable message.
        progress: Completion percentage (0.0-1.0).
        context: Cross-reference context (task_id, branch_name, etc.).
        task: Task namespace data.
        git: Git namespace data.
        decision: Decision namespace data.
        action: Action namespace data.
        metadata: Arbitrary metadata.
        **kwargs: Additional fields to include.

    Returns:
        Event dictionary conforming to v1.1.0 schema.
    """
    event: dict[str, Any] = {
        "version": SCHEMA_VERSION,
        "event_type": event_type,
        "timestamp": _now_utc_iso(),
        "agent_id": agent_id,
        "event_id": str(uuid.uuid4()),
    }

    # Add optional fields
    if message:
        event["message"] = message
    if progress is not None:
        event["progress"] = progress
    if context:
        event["context"] = context
    if task:
        event["task"] = task
    if git:
        event["git"] = git
    if decision:
        event["decision"] = decision
    if action:
        event["action"] = action
    if metadata:
        event["metadata"] = metadata

    # Add any additional kwargs
    for key, value in kwargs.items():
        if value is not None and key not in event:
            event[key] = value

    return event


def emit_event(
    event_type: str,
    agent_id: str,
    message: str | None = None,
    progress: float | None = None,
    context: dict[str, Any] | None = None,
    task: dict[str, Any] | None = None,
    git: dict[str, Any] | None = None,
    decision: dict[str, Any] | None = None,
    action: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    project_root: Path | str | None = None,
    validate: bool = True,
    **kwargs: Any,
) -> bool:
    """Emit an event synchronously to the JSONL event log.

    This is the primary function for emitting events. It builds a v1.1.0
    event, validates it against the schema, and writes it to the daily
    JSONL file.

    Args:
        event_type: Namespaced event type (e.g., "lifecycle.started").
        agent_id: Agent identifier (e.g., "@backend-engineer").
        message: Human-readable message.
        progress: Completion percentage (0.0-1.0).
        context: Cross-reference context (task_id, branch_name, etc.).
        task: Task namespace data.
        git: Git namespace data.
        decision: Decision namespace data.
        action: Action namespace data.
        metadata: Arbitrary metadata.
        project_root: Project root for events directory.
        validate: Whether to validate against schema (default True).
        **kwargs: Additional event fields.

    Returns:
        True if event was written successfully, False otherwise.

    Example:
        >>> emit_event(
        ...     event_type="lifecycle.started",
        ...     agent_id="@backend-engineer",
        ...     message="Starting task-486 implementation",
        ...     context={"task_id": "task-486"}
        ... )
        True
    """
    event = _build_event(
        event_type=event_type,
        agent_id=agent_id,
        message=message,
        progress=progress,
        context=context,
        task=task,
        git=git,
        decision=decision,
        action=action,
        metadata=metadata,
        **kwargs,
    )

    writer = get_default_writer(project_root=project_root)

    # Temporarily disable validation if requested
    original_validate = writer.config.validate_schema
    if not validate:
        writer.config.validate_schema = False

    try:
        return writer.write_event(event)
    finally:
        writer.config.validate_schema = original_validate


def emit_event_async(
    event_type: str,
    agent_id: str,
    message: str | None = None,
    progress: float | None = None,
    context: dict[str, Any] | None = None,
    task: dict[str, Any] | None = None,
    git: dict[str, Any] | None = None,
    decision: dict[str, Any] | None = None,
    action: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    project_root: Path | str | None = None,
    validate: bool = True,
    **kwargs: Any,
) -> None:
    """Emit an event asynchronously (fire-and-forget).

    Non-blocking event emission that runs in a background thread.
    Useful for performance-critical paths where event emission
    shouldn't block the main workflow.

    Args:
        event_type: Namespaced event type (e.g., "lifecycle.started").
        agent_id: Agent identifier.
        message: Human-readable message.
        progress: Completion percentage (0.0-1.0).
        context: Cross-reference context.
        task: Task namespace data.
        git: Git namespace data.
        decision: Decision namespace data.
        action: Action namespace data.
        metadata: Arbitrary metadata.
        project_root: Project root for events directory.
        validate: Whether to validate against schema.
        **kwargs: Additional event fields.

    Example:
        >>> emit_event_async(
        ...     event_type="activity.progress",
        ...     agent_id="@backend-engineer",
        ...     progress=0.5,
        ...     message="50% complete"
        ... )
        >>> # Returns immediately, write happens in background
    """

    def _emit_in_background() -> None:
        try:
            emit_event(
                event_type=event_type,
                agent_id=agent_id,
                message=message,
                progress=progress,
                context=context,
                task=task,
                git=git,
                decision=decision,
                action=action,
                metadata=metadata,
                project_root=project_root,
                validate=validate,
                **kwargs,
            )
        except Exception as e:
            logger.error(f"Background event emission failed: {e}", exc_info=True)

    thread = threading.Thread(
        target=_emit_in_background,
        name=f"event-emit-{event_type}",
        daemon=True,
    )
    thread.start()
    logger.debug(f"Event {event_type} emission started in background")


async def emit_event_awaitable(
    event_type: str,
    agent_id: str,
    message: str | None = None,
    progress: float | None = None,
    context: dict[str, Any] | None = None,
    task: dict[str, Any] | None = None,
    git: dict[str, Any] | None = None,
    decision: dict[str, Any] | None = None,
    action: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    project_root: Path | str | None = None,
    validate: bool = True,
    **kwargs: Any,
) -> bool:
    """Emit an event as an awaitable coroutine.

    For use in async contexts where you want non-blocking emission
    but still want to await the result.

    Args:
        event_type: Namespaced event type.
        agent_id: Agent identifier.
        message: Human-readable message.
        progress: Completion percentage (0.0-1.0).
        context: Cross-reference context.
        task: Task namespace data.
        git: Git namespace data.
        decision: Decision namespace data.
        action: Action namespace data.
        metadata: Arbitrary metadata.
        project_root: Project root for events directory.
        validate: Whether to validate against schema.
        **kwargs: Additional event fields.

    Returns:
        True if event was written successfully.

    Example:
        >>> async def my_workflow():
        ...     success = await emit_event_awaitable(
        ...         event_type="lifecycle.started",
        ...         agent_id="@backend-engineer"
        ...     )
        ...     return success
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: emit_event(
            event_type=event_type,
            agent_id=agent_id,
            message=message,
            progress=progress,
            context=context,
            task=task,
            git=git,
            decision=decision,
            action=action,
            metadata=metadata,
            project_root=project_root,
            validate=validate,
            **kwargs,
        ),
    )


# --- Event emission helpers for common event types ---


def emit_lifecycle_started(
    agent_id: str,
    message: str | None = None,
    task_id: str | None = None,
    **kwargs: Any,
) -> bool:
    """Emit a lifecycle.started event."""
    context = {"task_id": task_id} if task_id else None
    return emit_event(
        event_type="lifecycle.started",
        agent_id=agent_id,
        message=message,
        context=context,
        **kwargs,
    )


def emit_lifecycle_completed(
    agent_id: str,
    message: str | None = None,
    task_id: str | None = None,
    **kwargs: Any,
) -> bool:
    """Emit a lifecycle.completed event."""
    context = {"task_id": task_id} if task_id else None
    return emit_event(
        event_type="lifecycle.completed",
        agent_id=agent_id,
        message=message,
        context=context,
        **kwargs,
    )


def emit_activity_progress(
    agent_id: str,
    progress: float,
    message: str | None = None,
    task_id: str | None = None,
    **kwargs: Any,
) -> bool:
    """Emit an activity.progress event."""
    context = {"task_id": task_id} if task_id else None
    return emit_event(
        event_type="activity.progress",
        agent_id=agent_id,
        progress=progress,
        message=message,
        context=context,
        **kwargs,
    )


def emit_task_state_change(
    agent_id: str,
    task_id: str,
    from_state: str,
    to_state: str,
    title: str | None = None,
    **kwargs: Any,
) -> bool:
    """Emit a task.state_change event."""
    task_data: dict[str, Any] = {
        "task_id": task_id,
        "from_state": from_state,
        "to_state": to_state,
    }
    if title:
        task_data["title"] = title

    return emit_event(
        event_type="task.state_change",
        agent_id=agent_id,
        task=task_data,
        context={"task_id": task_id},
        **kwargs,
    )


def emit_git_commit(
    agent_id: str,
    sha: str,
    message: str,
    branch_name: str | None = None,
    files_changed: int | None = None,
    **kwargs: Any,
) -> bool:
    """Emit a git.commit event."""
    git_data: dict[str, Any] = {
        "operation": "commit",
        "sha": sha,
        "message": message,
    }
    if branch_name:
        git_data["branch_name"] = branch_name
    if files_changed is not None:
        git_data["files_changed"] = files_changed

    context = {"branch_name": branch_name} if branch_name else None

    return emit_event(
        event_type="git.commit",
        agent_id=agent_id,
        git=git_data,
        context=context,
        **kwargs,
    )


def emit_decision_made(
    agent_id: str,
    decision_id: str,
    category: str,
    message: str,
    reversibility_type: str = "two-way-door",
    alternatives_considered: list[dict[str, str]] | None = None,
    **kwargs: Any,
) -> bool:
    """Emit a decision.made event."""
    decision_data: dict[str, Any] = {
        "decision_id": decision_id,
        "category": category,
        "reversibility": {"type": reversibility_type},
    }
    if alternatives_considered:
        decision_data["alternatives_considered"] = alternatives_considered

    return emit_event(
        event_type="decision.made",
        agent_id=agent_id,
        message=message,
        decision=decision_data,
        context={"decision_id": decision_id},
        **kwargs,
    )
