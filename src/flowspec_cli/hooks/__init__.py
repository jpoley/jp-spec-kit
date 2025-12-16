"""Agent Hooks system for flowspec.

This module provides event-driven hook functionality for the flowspec
workflow system. Hooks enable automation of quality gates, notifications,
and integrations with external tools.

Main components:
- events: Event model schema and JSON serialization
- schema: Hook definition format and validation
- config: Hook configuration parser and loader
- emitter: Event emission and hook triggering
- runner: Secure hook execution with audit logging

Example:
    >>> from flowspec_cli.hooks import Event, EventEmitter, load_hooks_config
    >>> event = Event(event_type="spec.created", feature="auth")
    >>> emitter = EventEmitter(workspace_root=Path("/project"))
    >>> results = emitter.emit(event)
"""

from .config import (
    HooksConfigError,
    HooksConfigNotFoundError,
    HooksConfigValidationError,
    HooksSecurityError,
    load_hooks_config,
    validate_hooks_config_file,
)
from .emitter import (
    EventEmitter,
    emit_event,
    emit_implement_completed,
    emit_spec_created,
    emit_task_completed,
)
from .events import (
    Artifact,
    Event,
    EventType,
    create_implement_completed_event,
    create_spec_created_event,
    create_task_completed_event,
)
from .runner import HookResult, HookRunner
from .schema import EventMatcher, HookDefinition, HooksConfig
from .security import AuditLogger, SecurityConfig, SecurityValidator

__all__ = [
    # Events
    "Event",
    "EventType",
    "Artifact",
    "create_spec_created_event",
    "create_task_completed_event",
    "create_implement_completed_event",
    # Schema
    "EventMatcher",
    "HookDefinition",
    "HooksConfig",
    # Config
    "load_hooks_config",
    "validate_hooks_config_file",
    "HooksConfigError",
    "HooksConfigNotFoundError",
    "HooksConfigValidationError",
    "HooksSecurityError",
    # Emitter
    "EventEmitter",
    "emit_event",
    "emit_spec_created",
    "emit_task_completed",
    "emit_implement_completed",
    # Runner
    "HookRunner",
    "HookResult",
    # Security
    "SecurityConfig",
    "SecurityValidator",
    "AuditLogger",
]
