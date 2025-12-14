"""Telemetry module for flowspec role and workflow tracking.

This module provides telemetry collection with PII protection:
- RoleEvent enum for event types
- track_role_event() for logging events
- JSONL writer for persistent storage

All PII (project names, paths, usernames) is automatically hashed.

Example:
    from specify_cli.telemetry import RoleEvent, track_role_event

    # Track a role selection
    track_role_event(
        RoleEvent.ROLE_SELECTED,
        role="dev",
        command="/flow:implement"
    )

    # Track an agent invocation
    track_role_event(
        RoleEvent.AGENT_INVOKED,
        role="dev",
        agent="backend-engineer",
        context={"task_id": "task-123"}
    )

Environment Variables:
    FLOWSPEC_TELEMETRY_DISABLED: Set to "1" to disable telemetry
    FLOWSPEC_TELEMETRY_DEBUG: Set to "1" for debug output on errors
"""

from .events import RoleEvent, TelemetryEvent
from .integration import (
    is_telemetry_enabled,
    track_agent_invocation,
    track_agent_invocation_decorator,
    track_command_execution,
    track_handoff,
    track_role_change,
    track_role_selection,
    track_workflow,
)
from .tracker import (
    hash_pii,
    reset_writer,
    sanitize_path,
    sanitize_value,
    track_role_event,
)
from .writer import TelemetryWriter

__all__ = [
    # Events
    "RoleEvent",
    "TelemetryEvent",
    # Tracking
    "track_role_event",
    "hash_pii",
    "sanitize_path",
    "sanitize_value",
    "reset_writer",
    # Integration helpers
    "is_telemetry_enabled",
    "track_role_selection",
    "track_role_change",
    "track_agent_invocation",
    "track_agent_invocation_decorator",
    "track_handoff",
    "track_command_execution",
    "track_workflow",
    # Writer
    "TelemetryWriter",
]
