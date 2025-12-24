"""Event logger for recording significant events.

Logs events to JSONL files organized by date.
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Optional

from flowspec_cli.logging.config import LoggingConfig, get_config
from flowspec_cli.logging.schemas import EventCategory, LogEvent, LogSource

logger = logging.getLogger(__name__)

# Re-export for convenience
__all__ = ["EventLogger", "LogEvent", "EventCategory", "LogSource"]


class EventLogger:
    """Logger for event entries.

    Writes events to date-organized JSONL files in the configured
    events directory.

    Usage:
        >>> logger = EventLogger()
        >>> logger.log(
        ...     category=EventCategory.WORKFLOW_COMPLETED,
        ...     message="Completed /flow:implement workflow",
        ...     details={"phase": "implement", "tasks_completed": 3},
        ...     task_id="task-42",
        ...     workflow_phase="implement",
        ... )
    """

    def __init__(self, config: Optional[LoggingConfig] = None) -> None:
        """Initialize the event logger.

        Args:
            config: Logging configuration. Auto-detected if None.
        """
        self._config = config or get_config()
        self._ensure_dir()

    def _ensure_dir(self) -> None:
        """Ensure the events directory exists."""
        self._config.events_dir.mkdir(parents=True, exist_ok=True)

    def _get_log_file(self) -> Path:
        """Get the log file for today's date."""
        today = date.today().isoformat()
        return self._config.events_dir / f"{today}.jsonl"

    def log(
        self,
        category: EventCategory,
        message: str,
        details: Optional[dict] = None,
        task_id: Optional[str] = None,
        workflow_phase: Optional[str] = None,
        duration_ms: Optional[int] = None,
        success: bool = True,
        source: LogSource = LogSource.SYSTEM,
    ) -> LogEvent:
        """Log an event.

        Args:
            category: Event category.
            message: Human-readable event description.
            details: Additional event details.
            task_id: Related backlog task ID.
            workflow_phase: Current workflow phase (assess, specify, etc).
            duration_ms: Duration in milliseconds (for timed events).
            success: Whether the event represents a success.
            source: Event source (agent, human, hook, etc).

        Returns:
            The logged LogEvent object.
        """
        entry = LogEvent(
            category=category,
            message=message,
            details=details or {},
            task_id=task_id,
            workflow_phase=workflow_phase,
            duration_ms=duration_ms,
            success=success,
            _source_override=source,
        )

        self._write_entry(entry)
        return entry

    def log_entry(self, entry: LogEvent) -> None:
        """Log a pre-constructed LogEvent entry.

        Args:
            entry: The LogEvent to log.
        """
        self._write_entry(entry)

    def _write_entry(self, entry: LogEvent) -> None:
        """Write an event entry to the log file.

        Args:
            entry: The LogEvent to write.
        """
        log_file = self._get_log_file()
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")
            logger.debug(f"Event logged: {entry.category.value} - {entry.message[:50]}")
        except OSError as e:
            logger.error(f"Failed to write event log: {e}")

    # Convenience methods for common events

    def log_session_start(
        self,
        details: Optional[dict] = None,
        source: LogSource = LogSource.HOOK,
    ) -> LogEvent:
        """Log session start event."""
        return self.log(
            category=EventCategory.SESSION_START,
            message="Claude Code session started",
            details=details or {},
            source=source,
        )

    def log_session_end(
        self,
        details: Optional[dict] = None,
        source: LogSource = LogSource.HOOK,
    ) -> LogEvent:
        """Log session end event."""
        return self.log(
            category=EventCategory.SESSION_END,
            message="Claude Code session ended",
            details=details or {},
            source=source,
        )

    def log_workflow_started(
        self,
        phase: str,
        task_id: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> LogEvent:
        """Log workflow phase started."""
        return self.log(
            category=EventCategory.WORKFLOW_STARTED,
            message=f"Started /flow:{phase} workflow",
            details=details or {},
            task_id=task_id,
            workflow_phase=phase,
            source=LogSource.WORKFLOW,
        )

    def log_workflow_completed(
        self,
        phase: str,
        task_id: Optional[str] = None,
        duration_ms: Optional[int] = None,
        details: Optional[dict] = None,
    ) -> LogEvent:
        """Log workflow phase completed."""
        return self.log(
            category=EventCategory.WORKFLOW_COMPLETED,
            message=f"Completed /flow:{phase} workflow",
            details=details or {},
            task_id=task_id,
            workflow_phase=phase,
            duration_ms=duration_ms,
            source=LogSource.WORKFLOW,
        )

    def log_workflow_failed(
        self,
        phase: str,
        error: str,
        task_id: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> LogEvent:
        """Log workflow phase failed."""
        event_details = details or {}
        event_details["error"] = error
        return self.log(
            category=EventCategory.WORKFLOW_FAILED,
            message=f"Failed /flow:{phase} workflow: {error}",
            details=event_details,
            task_id=task_id,
            workflow_phase=phase,
            success=False,
            source=LogSource.WORKFLOW,
        )

    def log_task_status_changed(
        self,
        task_id: str,
        old_status: str,
        new_status: str,
        source: LogSource = LogSource.BACKLOG,
    ) -> LogEvent:
        """Log task status change."""
        return self.log(
            category=EventCategory.TASK_STATUS_CHANGED,
            message=f"Task {task_id} status changed: {old_status} -> {new_status}",
            details={"old_status": old_status, "new_status": new_status},
            task_id=task_id,
            source=source,
        )

    def log_hook_executed(
        self,
        hook_name: str,
        event_type: str,
        success: bool = True,
        duration_ms: Optional[int] = None,
        error: Optional[str] = None,
    ) -> LogEvent:
        """Log hook execution."""
        details = {"hook_name": hook_name, "event_type": event_type}
        if error:
            details["error"] = error
        return self.log(
            category=EventCategory.HOOK_EXECUTED
            if success
            else EventCategory.HOOK_FAILED,
            message=f"Hook '{hook_name}' {'executed' if success else 'failed'}",
            details=details,
            duration_ms=duration_ms,
            success=success,
            source=LogSource.HOOK,
        )

    def log_git_commit(
        self,
        commit_hash: str,
        message: str,
        files_changed: int = 0,
    ) -> LogEvent:
        """Log git commit event."""
        return self.log(
            category=EventCategory.GIT_COMMIT,
            message=f"Git commit: {message[:50]}",
            details={
                "commit_hash": commit_hash,
                "commit_message": message,
                "files_changed": files_changed,
            },
            source=LogSource.HOOK,
        )

    def log_git_push(
        self,
        branch: str,
        remote: str = "origin",
        commits_pushed: int = 0,
    ) -> LogEvent:
        """Log git push event."""
        return self.log(
            category=EventCategory.GIT_PUSH,
            message=f"Git push to {remote}/{branch}",
            details={
                "branch": branch,
                "remote": remote,
                "commits_pushed": commits_pushed,
            },
            source=LogSource.HOOK,
        )

    def log_decision(
        self,
        decision_id: str,
        decision: str,
        impact: str,
    ) -> LogEvent:
        """Log that a decision was made (cross-reference to decision log)."""
        return self.log(
            category=EventCategory.DECISION_MADE,
            message=f"Decision: {decision[:50]}",
            details={"decision_id": decision_id, "impact": impact},
            source=LogSource.AGENT,
        )

    def read_today(self) -> list[LogEvent]:
        """Read today's events.

        Returns:
            List of LogEvent entries from today.
        """
        return self.read_date(date.today())

    def read_date(self, log_date: date) -> list[LogEvent]:
        """Read events from a specific date.

        Args:
            log_date: The date to read.

        Returns:
            List of LogEvent entries from that date.
        """
        log_file = self._config.events_dir / f"{log_date.isoformat()}.jsonl"
        if not log_file.exists():
            return []

        events = []
        try:
            with open(log_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        # Convert string values back to enums
                        if "category" in data:
                            data["category"] = EventCategory(data["category"])
                        # Handle source field - convert to _source_override
                        if "source" in data:
                            data["_source_override"] = LogSource(data.pop("source"))
                        # Preserve original timestamp and entry_id from log file
                        # by passing them as stored values for reconstruction
                        if "timestamp" in data:
                            data["_stored_timestamp"] = data.pop("timestamp")
                        if "entry_id" in data:
                            data["_stored_entry_id"] = data.pop("entry_id")
                        events.append(LogEvent(**data))
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Failed to read event log: {e}")

        return events

    @property
    def log_directory(self) -> Path:
        """Get the events log directory."""
        return self._config.events_dir

    @property
    def is_internal_dev(self) -> bool:
        """Check if logging to internal dev location."""
        return self._config.is_internal_dev
