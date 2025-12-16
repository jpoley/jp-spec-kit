"""Event model schema for flowspec hooks.

This module defines the canonical event types and payload structure for the
hook system. Events are emitted by /flowspec commands and backlog operations,
and hooks respond to these events with automation.

Example:
    >>> event = Event(
    ...     event_type="spec.created",
    ...     feature="user-authentication",
    ...     context={"agent": "pm-planner"}
    ... )
    >>> event_json = event.to_json()
    >>> restored = Event.from_json(event_json)
"""

from __future__ import annotations

import json
import socket
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class EventType(str, Enum):
    """Canonical event types for flowspec workflow.

    Event naming follows <domain>.<action> convention:
    - Domain: workflow phase or component (spec, plan, task, implement, etc.)
    - Action: past tense verb (created, updated, completed, etc.)

    Workflow Events:
        WORKFLOW_ASSESSED: /flow:assess completed
        SPEC_CREATED: /flow:specify completed (new spec)
        SPEC_UPDATED: Spec file modified
        RESEARCH_COMPLETED: /flow:research completed
        PLAN_CREATED: /flow:plan completed (new plan)
        PLAN_UPDATED: Plan file modified
        ADR_CREATED: Architecture Decision Record created
        IMPLEMENT_STARTED: /flow:implement started
        IMPLEMENT_COMPLETED: /flow:implement completed
        VALIDATE_STARTED: /flow:validate started
        VALIDATE_COMPLETED: /flow:validate completed
        DEPLOY_STARTED: /flow:operate started
        DEPLOY_COMPLETED: /flow:operate completed

    Task Events:
        TASK_CREATED: New backlog task created
        TASK_UPDATED: Task metadata changed
        TASK_STATUS_CHANGED: Task status transition
        TASK_AC_CHECKED: Acceptance criterion marked complete
        TASK_AC_UNCHECKED: Acceptance criterion unmarked
        TASK_COMPLETED: Task marked as Done
        TASK_ARCHIVED: Task moved to archive

    Agent Events (multi-machine observability):
        AGENT_STARTED: Agent began working on task
        AGENT_PROGRESS: Agent reports progress (percentage, status message)
        AGENT_BLOCKED: Agent is waiting for something
        AGENT_COMPLETED: Agent finished task
        AGENT_ERROR: Agent encountered error
        AGENT_HANDOFF: Agent handing off to another agent/machine
    """

    # Workflow events
    WORKFLOW_ASSESSED = "workflow.assessed"
    SPEC_CREATED = "spec.created"
    SPEC_UPDATED = "spec.updated"
    RESEARCH_COMPLETED = "research.completed"
    PLAN_CREATED = "plan.created"
    PLAN_UPDATED = "plan.updated"
    ADR_CREATED = "adr.created"
    IMPLEMENT_STARTED = "implement.started"
    IMPLEMENT_COMPLETED = "implement.completed"
    VALIDATE_STARTED = "validate.started"
    VALIDATE_COMPLETED = "validate.completed"
    DEPLOY_STARTED = "deploy.started"
    DEPLOY_COMPLETED = "deploy.completed"

    # Task events
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_STATUS_CHANGED = "task.status_changed"
    TASK_AC_CHECKED = "task.ac_checked"
    TASK_AC_UNCHECKED = "task.ac_unchecked"
    TASK_COMPLETED = "task.completed"
    TASK_ARCHIVED = "task.archived"

    # Agent events (multi-machine observability)
    AGENT_STARTED = "agent.started"
    AGENT_PROGRESS = "agent.progress"
    AGENT_BLOCKED = "agent.blocked"
    AGENT_COMPLETED = "agent.completed"
    AGENT_ERROR = "agent.error"
    AGENT_HANDOFF = "agent.handoff"


@dataclass
class Artifact:
    """Artifact produced by a workflow event.

    Represents files, reports, or other outputs generated during workflow
    execution. Includes metadata about the artifact type and location.

    Attributes:
        type: Type of artifact (source_code, report, documentation, etc.)
        path: Relative path to artifact from project root
        files_changed: Number of files modified (optional)

    Example:
        >>> artifact = Artifact(
        ...     type="source_code",
        ...     path="./src/auth/",
        ...     files_changed=12
        ... )
    """

    type: str
    path: str
    files_changed: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert artifact to dictionary for JSON serialization.

        Returns:
            Dictionary representation with non-None fields.
        """
        result: dict[str, Any] = {
            "type": self.type,
            "path": self.path,
        }
        if self.files_changed is not None:
            result["files_changed"] = self.files_changed
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Artifact:
        """Create artifact from dictionary.

        Args:
            data: Dictionary with artifact fields.

        Returns:
            Artifact instance.
        """
        return cls(
            type=data["type"],
            path=data["path"],
            files_changed=data.get("files_changed"),
        )


@dataclass
class Event:
    """Workflow event with structured payload.

    All workflow events and task operations emit Event instances with
    standardized fields. Events include a unique ID, timestamp, and
    optional context and artifacts.

    Required Fields:
        event_type: Canonical event identifier (see EventType enum)
        event_id: Unique ULID identifier (auto-generated)
        schema_version: Event schema version (default: "1.0")
        timestamp: ISO 8601 UTC timestamp (auto-generated)
        project_root: Absolute path to project directory

    Optional Fields:
        feature: Feature name/identifier
        context: Event-specific context (agent, task_id, state, etc.)
        artifacts: List of produced artifacts
        metadata: System metadata (versions, environment)

    Example:
        >>> event = Event(
        ...     event_type="implement.completed",
        ...     project_root="/home/user/project",
        ...     feature="user-auth",
        ...     context={"agent": "backend-engineer", "task_id": "task-189"}
        ... )
        >>> event.event_id  # Auto-generated ULID
        'evt_01HQZX123ABC...'
    """

    event_type: str
    project_root: str
    event_id: str = field(default_factory=lambda: _generate_event_id())
    schema_version: str = "1.0"
    timestamp: str = field(default_factory=lambda: _now_utc_iso())
    feature: str | None = None
    context: dict[str, Any] | None = None
    artifacts: list[Artifact] | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for JSON serialization.

        Returns:
            Dictionary with all event fields, omitting None values for
            optional fields.

        Example:
            >>> event = Event(event_type="spec.created", project_root="/tmp")
            >>> event.to_dict()
            {'event_type': 'spec.created', 'event_id': '...', ...}
        """
        result: dict[str, Any] = {
            "event_type": self.event_type,
            "event_id": self.event_id,
            "schema_version": self.schema_version,
            "timestamp": self.timestamp,
            "project_root": self.project_root,
        }

        # Add optional fields if present
        if self.feature is not None:
            result["feature"] = self.feature
        if self.context is not None:
            result["context"] = self.context
        if self.artifacts is not None:
            result["artifacts"] = [a.to_dict() for a in self.artifacts]
        if self.metadata is not None:
            result["metadata"] = self.metadata

        return result

    def to_json(self, indent: int | None = None) -> str:
        """Serialize event to JSON string.

        Args:
            indent: Number of spaces for indentation (None for compact).

        Returns:
            JSON string representation of event.

        Example:
            >>> event = Event(event_type="spec.created", project_root="/tmp")
            >>> json_str = event.to_json(indent=2)
            >>> print(json_str)
            {
              "event_type": "spec.created",
              ...
            }
        """
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Event:
        """Create event from dictionary.

        Args:
            data: Dictionary with event fields.

        Returns:
            Event instance.

        Raises:
            KeyError: If required fields are missing.
            TypeError: If field types are invalid.

        Example:
            >>> data = {"event_type": "spec.created", "project_root": "/tmp"}
            >>> event = Event.from_dict(data)
        """
        # Parse artifacts if present
        artifacts = None
        if "artifacts" in data and data["artifacts"] is not None:
            artifacts = [Artifact.from_dict(a) for a in data["artifacts"]]

        return cls(
            event_type=data["event_type"],
            event_id=data.get("event_id", _generate_event_id()),
            schema_version=data.get("schema_version", "1.0"),
            timestamp=data.get("timestamp", _now_utc_iso()),
            project_root=data["project_root"],
            feature=data.get("feature"),
            context=data.get("context"),
            artifacts=artifacts,
            metadata=data.get("metadata"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> Event:
        """Deserialize event from JSON string.

        Args:
            json_str: JSON string representation of event.

        Returns:
            Event instance.

        Raises:
            json.JSONDecodeError: If JSON is invalid.
            KeyError: If required fields are missing.

        Example:
            >>> json_str = '{"event_type": "spec.created", "project_root": "/tmp"}'
            >>> event = Event.from_json(json_str)
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


# --- Event factory functions ---


def create_spec_created_event(
    project_root: str | Path,
    feature: str,
    spec_path: str,
    agent: str = "pm-planner",
) -> Event:
    """Create a spec.created event.

    Args:
        project_root: Project root directory.
        feature: Feature name.
        spec_path: Path to created spec file.
        agent: Agent that created the spec (default: pm-planner).

    Returns:
        Event instance for spec.created.

    Example:
        >>> event = create_spec_created_event(
        ...     project_root="/home/user/project",
        ...     feature="user-auth",
        ...     spec_path="docs/prd/user-auth-spec.md"
        ... )
    """
    return Event(
        event_type=EventType.SPEC_CREATED.value,
        project_root=str(project_root),
        feature=feature,
        context={
            "agent": agent,
            "workflow_state": "Specified",
        },
        artifacts=[
            Artifact(type="prd", path=spec_path, files_changed=1),
        ],
    )


def create_task_completed_event(
    project_root: str | Path,
    task_id: str,
    task_title: str,
    priority: str | None = None,
    labels: list[str] | None = None,
) -> Event:
    """Create a task.completed event.

    Args:
        project_root: Project root directory.
        task_id: Task identifier (e.g., "task-189").
        task_title: Task title.
        priority: Task priority (high, medium, low).
        labels: Task labels.

    Returns:
        Event instance for task.completed.

    Example:
        >>> event = create_task_completed_event(
        ...     project_root="/home/user/project",
        ...     task_id="task-189",
        ...     task_title="Implement authentication",
        ...     priority="high",
        ...     labels=["backend", "security"]
        ... )
    """
    context: dict[str, Any] = {
        "task_id": task_id,
        "task_title": task_title,
        "status_from": "In Progress",
        "status_to": "Done",
    }
    if priority:
        context["priority"] = priority
    if labels:
        context["labels"] = labels

    return Event(
        event_type=EventType.TASK_COMPLETED.value,
        project_root=str(project_root),
        context=context,
    )


def create_implement_completed_event(
    project_root: str | Path,
    feature: str,
    task_id: str | None = None,
    files_changed: int | None = None,
    source_path: str = "./src/",
) -> Event:
    """Create an implement.completed event.

    Args:
        project_root: Project root directory.
        feature: Feature name.
        task_id: Associated task ID (optional).
        files_changed: Number of files modified.
        source_path: Path to modified source code.

    Returns:
        Event instance for implement.completed.

    Example:
        >>> event = create_implement_completed_event(
        ...     project_root="/home/user/project",
        ...     feature="user-auth",
        ...     task_id="task-189",
        ...     files_changed=15,
        ...     source_path="./src/auth/"
        ... )
    """
    context: dict[str, Any] = {
        "agent": "backend-engineer",
        "workflow_state": "In Implementation",
    }
    if task_id:
        context["task_id"] = task_id

    return Event(
        event_type=EventType.IMPLEMENT_COMPLETED.value,
        project_root=str(project_root),
        feature=feature,
        context=context,
        artifacts=[
            Artifact(
                type="source_code",
                path=source_path,
                files_changed=files_changed,
            ),
        ],
    )


def create_agent_progress_event(
    project_root: str | Path,
    agent_id: str,
    task_id: str | None = None,
    feature: str | None = None,
    progress_percent: int | None = None,
    status_message: str | None = None,
    machine: str | None = None,
) -> Event:
    """Create an agent.progress event for multi-machine observability.

    Args:
        project_root: Project root directory.
        agent_id: Agent identifier (e.g., "claude-code@kinsale").
        task_id: Associated task ID (optional).
        feature: Feature being worked on (optional).
        progress_percent: Completion percentage 0-100 (optional).
        status_message: Human-readable status message (optional).
        machine: Machine hostname (optional, auto-detected if not provided).

    Returns:
        Event instance for agent.progress.

    Example:
        >>> event = create_agent_progress_event(
        ...     project_root="/home/user/project",
        ...     agent_id="claude-code@kinsale",
        ...     task_id="task-229",
        ...     progress_percent=60,
        ...     status_message="Implementing event emission"
        ... )
    """
    context: dict[str, Any] = {
        "agent_id": agent_id,
    }

    if task_id:
        context["task_id"] = task_id
    if progress_percent is not None:
        context["progress_percent"] = progress_percent
    if status_message:
        context["status_message"] = status_message

    # Auto-detect machine hostname if not provided
    context["machine"] = machine or socket.gethostname()

    return Event(
        event_type=EventType.AGENT_PROGRESS.value,
        project_root=str(project_root),
        feature=feature,
        context=context,
    )


def create_agent_started_event(
    project_root: str | Path,
    agent_id: str,
    task_id: str | None = None,
    feature: str | None = None,
    machine: str | None = None,
) -> Event:
    """Create an agent.started event.

    Args:
        project_root: Project root directory.
        agent_id: Agent identifier (e.g., "claude-code@kinsale").
        task_id: Associated task ID (optional).
        feature: Feature being worked on (optional).
        machine: Machine hostname (optional, auto-detected if not provided).

    Returns:
        Event instance for agent.started.
    """
    context: dict[str, Any] = {
        "agent_id": agent_id,
        "machine": machine or socket.gethostname(),
    }

    if task_id:
        context["task_id"] = task_id

    return Event(
        event_type=EventType.AGENT_STARTED.value,
        project_root=str(project_root),
        feature=feature,
        context=context,
    )


def create_agent_completed_event(
    project_root: str | Path,
    agent_id: str,
    task_id: str | None = None,
    feature: str | None = None,
    machine: str | None = None,
    status_message: str | None = None,
) -> Event:
    """Create an agent.completed event.

    Args:
        project_root: Project root directory.
        agent_id: Agent identifier (e.g., "claude-code@kinsale").
        task_id: Associated task ID (optional).
        feature: Feature being worked on (optional).
        machine: Machine hostname (optional, auto-detected if not provided).
        status_message: Completion summary message (optional).

    Returns:
        Event instance for agent.completed.
    """
    context: dict[str, Any] = {
        "agent_id": agent_id,
        "machine": machine or socket.gethostname(),
    }

    if task_id:
        context["task_id"] = task_id
    if status_message:
        context["status_message"] = status_message

    return Event(
        event_type=EventType.AGENT_COMPLETED.value,
        project_root=str(project_root),
        feature=feature,
        context=context,
    )


def create_agent_handoff_event(
    project_root: str | Path,
    agent_id: str,
    target_agent: str,
    target_machine: str | None = None,
    task_id: str | None = None,
    feature: str | None = None,
    machine: str | None = None,
    handoff_message: str | None = None,
) -> Event:
    """Create an agent.handoff event for multi-machine coordination.

    Args:
        project_root: Project root directory.
        agent_id: Source agent identifier.
        target_agent: Target agent identifier for handoff.
        target_machine: Target machine for handoff (optional).
        task_id: Associated task ID (optional).
        feature: Feature being worked on (optional).
        machine: Source machine hostname (optional, auto-detected).
        handoff_message: Message for the receiving agent (optional).

    Returns:
        Event instance for agent.handoff.

    Example:
        >>> event = create_agent_handoff_event(
        ...     project_root="/home/user/project",
        ...     agent_id="claude-code@muckross",
        ...     target_agent="claude-code@galway",
        ...     task_id="task-198",
        ...     handoff_message="Planning complete, ready for implementation"
        ... )
    """
    context: dict[str, Any] = {
        "agent_id": agent_id,
        "target_agent": target_agent,
        "machine": machine or socket.gethostname(),
    }

    if target_machine:
        context["target_machine"] = target_machine
    if task_id:
        context["task_id"] = task_id
    if handoff_message:
        context["handoff_message"] = handoff_message

    return Event(
        event_type=EventType.AGENT_HANDOFF.value,
        project_root=str(project_root),
        feature=feature,
        context=context,
    )


# --- Private helper functions ---


def _generate_event_id() -> str:
    """Generate ULID-based event ID.

    Returns:
        Event ID in format "evt_<ULID>".

    Example:
        >>> event_id = _generate_event_id()
        >>> event_id.startswith("evt_")
        True
        >>> len(event_id)
        30  # evt_ (4) + ULID (26)
    """
    try:
        from ulid import ULID

        return f"evt_{ULID()}"
    except ImportError:
        # Fallback to timestamp-based ID if ulid not installed
        import time

        timestamp_ms = int(time.time() * 1000)
        return f"evt_{timestamp_ms:016x}"


def _now_utc_iso() -> str:
    """Get current UTC timestamp in ISO 8601 format.

    Returns:
        ISO 8601 UTC timestamp string with 'Z' suffix.

    Example:
        >>> timestamp = _now_utc_iso()
        >>> timestamp.endswith("Z")
        True
        >>> "T" in timestamp
        True
    """
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
