"""Telemetry event types for flowspec role tracking.

This module defines the event types and structures used for
telemetry collection in flowspec workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class RoleEvent(str, Enum):
    """Event types for role-based telemetry tracking.

    Events track user interactions with roles, agents, and workflows
    to help improve the flowspec experience.
    """

    # Role selection events
    ROLE_SELECTED = "role.selected"
    ROLE_CHANGED = "role.changed"

    # Agent invocation events
    AGENT_INVOKED = "agent.invoked"
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    AGENT_PROGRESS = "agent.progress"

    # Handoff events
    HANDOFF_CLICKED = "handoff.clicked"
    HANDOFF_COMPLETED = "handoff.completed"

    # Command events
    COMMAND_EXECUTED = "command.executed"
    COMMAND_COMPLETED = "command.completed"
    COMMAND_FAILED = "command.failed"

    # Workflow events
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"

    def __str__(self) -> str:
        """Return the event type string value."""
        return self.value


@dataclass
class TelemetryEvent:
    """A telemetry event with metadata.

    Attributes:
        event_type: The type of event (from RoleEvent enum)
        timestamp: When the event occurred (UTC ISO format)
        role: The user's current role (e.g., dev, pm, qa)
        command: The command that triggered the event
        agent: The agent involved (if applicable)
        context: Additional context data
        metadata: Extra metadata (hashed PII)
    """

    event_type: RoleEvent
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    role: str | None = None
    command: str | None = None
    agent: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary for JSON serialization."""
        data = {
            "event_type": str(self.event_type),
            "timestamp": self.timestamp,
        }

        if self.role:
            data["role"] = self.role
        if self.command:
            data["command"] = self.command
        if self.agent:
            data["agent"] = self.agent
        if self.context:
            data["context"] = self.context
        if self.metadata:
            data["metadata"] = self.metadata

        return data

    @classmethod
    def create(
        cls,
        event_type: RoleEvent | str,
        *,
        role: str | None = None,
        command: str | None = None,
        agent: str | None = None,
        context: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TelemetryEvent:
        """Create a new telemetry event.

        Args:
            event_type: The type of event
            role: The user's current role
            command: The command that triggered the event
            agent: The agent involved
            context: Additional context data
            metadata: Extra metadata

        Returns:
            A new TelemetryEvent instance
        """
        if isinstance(event_type, str):
            event_type = RoleEvent(event_type)

        return cls(
            event_type=event_type,
            role=role,
            command=command,
            agent=agent,
            context=context or {},
            metadata=metadata or {},
        )


__all__ = ["RoleEvent", "TelemetryEvent"]
