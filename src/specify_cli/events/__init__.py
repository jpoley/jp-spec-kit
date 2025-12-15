"""JSONL Event System for Flowspec.

This module provides persistent event storage using JSONL format with
daily rotation and configurable retention, plus event routing with
namespace dispatch.

Key Components:
    - EventWriter: JSONL file writer with daily rotation
    - emit_event: Synchronous event emission with schema validation
    - emit_event_async: Non-blocking event emission
    - EventRouter: Routes events to handlers based on patterns
    - EventFilter: Filter events by task_id, agent_id, time_range
    - Built-in handlers: JsonlHandler, McpHandler, LoggingHandler

Example:
    >>> from specify_cli.events import emit_event, EventRouter, JsonlHandler
    >>>
    >>> # Direct emission
    >>> emit_event(
    ...     event_type="lifecycle.started",
    ...     agent_id="@backend-engineer",
    ...     message="Starting task implementation"
    ... )
    >>>
    >>> # Router-based dispatch
    >>> router = EventRouter()
    >>> router.register_handler("*", JsonlHandler())
    >>> router.dispatch({"event_type": "lifecycle.started", ...})
"""

from specify_cli.events.handlers import (
    BufferHandler,
    CallbackHandler,
    CompositeHandler,
    EventHandler,
    FilteringHandler,
    JsonlHandler,
    LoggingHandler,
    McpHandler,
)
from specify_cli.events.query import (
    EventQuery,
    QueryResult,
    count_events,
    get_events,
    query,
)
from specify_cli.events.router import (
    EventFilter,
    EventRouter,
    HandlerRegistration,
    dispatch,
    get_default_router,
    register_handler,
    reset_default_router,
)
from specify_cli.events.writer import (
    EventWriter,
    EventWriterConfig,
    emit_event,
    emit_event_async,
    get_default_writer,
)

__all__ = [
    # Writer (task-486)
    "EventWriter",
    "EventWriterConfig",
    "emit_event",
    "emit_event_async",
    "get_default_writer",
    # Router (task-487)
    "EventRouter",
    "EventFilter",
    "EventHandler",
    "HandlerRegistration",
    "dispatch",
    "get_default_router",
    "register_handler",
    "reset_default_router",
    # Handlers (task-487)
    "JsonlHandler",
    "McpHandler",
    "LoggingHandler",
    "CallbackHandler",
    "BufferHandler",
    "FilteringHandler",
    "CompositeHandler",
    # Query (task-504)
    "EventQuery",
    "QueryResult",
    "query",
    "count_events",
    "get_events",
]
