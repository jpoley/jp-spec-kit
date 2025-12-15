"""Event Router with namespace dispatch and pattern matching.

This module provides event routing infrastructure that dispatches events
to registered handlers based on event type patterns. Supports wildcards
for flexible namespace-based routing.

Features:
    - Pattern matching with wildcards (e.g., "git.*" matches all git events)
    - Multiple handlers per pattern
    - Handler priority ordering
    - Event filtering by task_id, agent_id, time_range
    - Synchronous and asynchronous dispatch
    - Built-in handlers for JSONL and MCP

Example:
    >>> from specify_cli.events.router import EventRouter
    >>> from specify_cli.events.handlers import JsonlHandler, LoggingHandler
    >>>
    >>> router = EventRouter()
    >>> router.register_handler("lifecycle.*", LoggingHandler())
    >>> router.register_handler("git.*", JsonlHandler())
    >>> router.register_handler("*", JsonlHandler())  # Catch-all
    >>>
    >>> event = {"event_type": "lifecycle.started", ...}
    >>> router.dispatch(event)
"""

from __future__ import annotations

import fnmatch
import logging
import re
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

logger = logging.getLogger(__name__)


class EventHandler(ABC):
    """Abstract base class for event handlers.

    Implement this interface to create custom event handlers that can
    be registered with the EventRouter.

    Example:
        >>> class MyHandler(EventHandler):
        ...     def handle(self, event: dict[str, Any]) -> bool:
        ...         print(f"Received: {event['event_type']}")
        ...         return True
    """

    @abstractmethod
    def handle(self, event: dict[str, Any]) -> bool:
        """Handle an event.

        Args:
            event: Event dictionary to handle.

        Returns:
            True if handled successfully, False otherwise.
        """
        pass

    def close(self) -> None:
        """Clean up handler resources.

        Override this method to perform cleanup when the router is closed.
        """
        pass


@dataclass
class HandlerRegistration:
    """Registration entry for an event handler.

    Attributes:
        pattern: Event type pattern (e.g., "git.*", "lifecycle.started").
        handler: Handler instance.
        priority: Handler priority (higher = earlier execution).
        enabled: Whether the handler is currently enabled.
        name: Optional handler name for identification.
    """

    pattern: str
    handler: EventHandler
    priority: int = 0
    enabled: bool = True
    name: str | None = None
    _compiled_pattern: re.Pattern | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Compile the pattern for efficient matching."""
        self._compiled_pattern = _compile_pattern(self.pattern)

    def matches(self, event_type: str) -> bool:
        """Check if this registration matches an event type.

        Args:
            event_type: Event type string to match against.

        Returns:
            True if pattern matches event type.
        """
        if self._compiled_pattern is None:
            self._compiled_pattern = _compile_pattern(self.pattern)
        return bool(self._compiled_pattern.match(event_type))


@dataclass
class EventFilter:
    """Filter criteria for events.

    All specified criteria must match for an event to pass the filter.
    None values are ignored (match anything).

    Attributes:
        task_id: Filter by task ID in context.
        agent_id: Filter by agent ID.
        namespaces: Filter by namespace (first part of event_type).
        event_types: Filter by exact event types.
        start_time: Filter events after this time.
        end_time: Filter events before this time.
        custom: Custom filter function.

    Example:
        >>> # Filter for backend-engineer events on task-486
        >>> filter = EventFilter(
        ...     agent_id="@backend-engineer",
        ...     task_id="task-486"
        ... )
    """

    task_id: str | None = None
    agent_id: str | None = None
    namespaces: list[str] | None = None
    event_types: list[str] | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    custom: Callable[[dict[str, Any]], bool] | None = None

    def matches(self, event: dict[str, Any]) -> bool:
        """Check if event matches all filter criteria.

        Args:
            event: Event dictionary to check.

        Returns:
            True if event matches all criteria.
        """
        # Check task_id
        if self.task_id is not None:
            event_task_id = event.get("context", {}).get("task_id") or event.get(
                "task", {}
            ).get("task_id")
            if event_task_id != self.task_id:
                return False

        # Check agent_id
        if self.agent_id is not None:
            if event.get("agent_id") != self.agent_id:
                return False

        # Check namespaces
        if self.namespaces is not None:
            event_type = event.get("event_type", "")
            namespace = event_type.split(".")[0] if "." in event_type else ""
            if namespace not in self.namespaces:
                return False

        # Check event_types
        if self.event_types is not None:
            if event.get("event_type") not in self.event_types:
                return False

        # Check time range
        if self.start_time is not None or self.end_time is not None:
            timestamp_str = event.get("timestamp", "")
            try:
                # Parse ISO 8601 timestamp
                timestamp_str = timestamp_str.replace("Z", "+00:00")
                event_time = datetime.fromisoformat(timestamp_str)

                if self.start_time is not None and event_time < self.start_time:
                    return False
                if self.end_time is not None and event_time > self.end_time:
                    return False
            except (ValueError, TypeError):
                # Invalid timestamp, don't match time filters
                return False

        # Check custom filter
        if self.custom is not None:
            if not self.custom(event):
                return False

        return True


class EventRouter:
    """Routes events to handlers based on pattern matching.

    The router maintains a registry of handlers with patterns and dispatches
    events to all matching handlers. Supports wildcards for flexible routing.

    Pattern Syntax:
        - "*" matches any event type
        - "namespace.*" matches all events in namespace
        - "namespace.event" matches exact event type
        - "namespace.event_*" matches events starting with prefix

    Thread Safety:
        The router is thread-safe for concurrent dispatch and registration.

    Example:
        >>> router = EventRouter()
        >>>
        >>> # Register handlers
        >>> router.register_handler("lifecycle.*", lifecycle_handler)
        >>> router.register_handler("git.*", git_handler, priority=10)
        >>> router.register_handler("*", catch_all_handler)
        >>>
        >>> # Dispatch event
        >>> event = {"event_type": "lifecycle.started", ...}
        >>> results = router.dispatch(event)
        >>> print(f"{len(results)} handlers executed")
    """

    def __init__(self) -> None:
        """Initialize the router."""
        self._handlers: list[HandlerRegistration] = []
        self._lock = threading.RLock()
        self._global_filter: EventFilter | None = None

    def register_handler(
        self,
        pattern: str,
        handler: EventHandler,
        priority: int = 0,
        name: str | None = None,
    ) -> None:
        """Register a handler for a pattern.

        Args:
            pattern: Event type pattern (e.g., "git.*", "*").
            handler: Handler instance to register.
            priority: Handler priority (higher = earlier). Default 0.
            name: Optional name for identification.

        Example:
            >>> router.register_handler("git.*", my_handler, priority=10)
            >>> router.register_handler("*", fallback_handler, name="fallback")
        """
        registration = HandlerRegistration(
            pattern=pattern,
            handler=handler,
            priority=priority,
            name=name,
        )

        with self._lock:
            self._handlers.append(registration)
            # Sort by priority (descending)
            self._handlers.sort(key=lambda r: r.priority, reverse=True)

        logger.debug(f"Registered handler for pattern '{pattern}' (priority={priority})")

    def unregister_handler(
        self,
        pattern: str | None = None,
        handler: EventHandler | None = None,
        name: str | None = None,
    ) -> int:
        """Unregister handlers matching criteria.

        At least one of pattern, handler, or name must be specified.

        Args:
            pattern: Remove handlers with this pattern.
            handler: Remove this specific handler.
            name: Remove handlers with this name.

        Returns:
            Number of handlers removed.
        """
        if pattern is None and handler is None and name is None:
            raise ValueError("At least one of pattern, handler, or name must be specified")

        removed = 0
        with self._lock:
            original_count = len(self._handlers)
            self._handlers = [
                r
                for r in self._handlers
                if not (
                    (pattern is None or r.pattern == pattern)
                    and (handler is None or r.handler is handler)
                    and (name is None or r.name == name)
                )
            ]
            removed = original_count - len(self._handlers)

        if removed:
            logger.debug(f"Unregistered {removed} handler(s)")

        return removed

    def set_global_filter(self, filter: EventFilter | None) -> None:
        """Set a global filter applied to all events.

        Args:
            filter: Filter to apply, or None to clear.
        """
        with self._lock:
            self._global_filter = filter

    def dispatch(
        self,
        event: dict[str, Any],
        filter: EventFilter | None = None,
    ) -> list[tuple[str, bool]]:
        """Dispatch an event to all matching handlers.

        Args:
            event: Event dictionary to dispatch.
            filter: Optional additional filter to apply.

        Returns:
            List of (handler_name, success) tuples for each handler executed.

        Example:
            >>> results = router.dispatch({"event_type": "git.commit", ...})
            >>> for name, success in results:
            ...     print(f"{name}: {'OK' if success else 'FAILED'}")
        """
        event_type = event.get("event_type", "")

        # Apply global filter
        if self._global_filter is not None and not self._global_filter.matches(event):
            logger.debug(f"Event {event_type} filtered by global filter")
            return []

        # Apply dispatch filter
        if filter is not None and not filter.matches(event):
            logger.debug(f"Event {event_type} filtered by dispatch filter")
            return []

        results: list[tuple[str, bool]] = []

        with self._lock:
            handlers_snapshot = list(self._handlers)

        for registration in handlers_snapshot:
            if not registration.enabled:
                continue

            if not registration.matches(event_type):
                continue

            handler_name = registration.name or registration.pattern
            try:
                success = registration.handler.handle(event)
                results.append((handler_name, success))
                logger.debug(
                    f"Handler '{handler_name}' processed {event_type}: "
                    f"{'success' if success else 'failed'}"
                )
            except Exception as e:
                logger.error(f"Handler '{handler_name}' raised exception: {e}")
                results.append((handler_name, False))

        return results

    def dispatch_async(
        self,
        event: dict[str, Any],
        filter: EventFilter | None = None,
    ) -> None:
        """Dispatch an event asynchronously (fire-and-forget).

        Args:
            event: Event dictionary to dispatch.
            filter: Optional additional filter to apply.
        """

        def _dispatch_in_background() -> None:
            try:
                self.dispatch(event, filter)
            except Exception as e:
                logger.error(f"Async dispatch failed: {e}")

        thread = threading.Thread(
            target=_dispatch_in_background,
            name=f"router-dispatch-{event.get('event_type', 'unknown')}",
            daemon=True,
        )
        thread.start()

    def get_matching_handlers(self, event_type: str) -> list[HandlerRegistration]:
        """Get all handlers that would match an event type.

        Args:
            event_type: Event type string to check.

        Returns:
            List of matching handler registrations.
        """
        with self._lock:
            return [
                r
                for r in self._handlers
                if r.enabled and r.matches(event_type)
            ]

    def list_handlers(self) -> list[dict[str, Any]]:
        """List all registered handlers.

        Returns:
            List of handler info dictionaries.
        """
        with self._lock:
            return [
                {
                    "pattern": r.pattern,
                    "name": r.name,
                    "priority": r.priority,
                    "enabled": r.enabled,
                    "handler_type": type(r.handler).__name__,
                }
                for r in self._handlers
            ]

    def enable_handler(self, name: str) -> bool:
        """Enable a handler by name.

        Args:
            name: Handler name to enable.

        Returns:
            True if handler was found and enabled.
        """
        with self._lock:
            for r in self._handlers:
                if r.name == name:
                    r.enabled = True
                    return True
        return False

    def disable_handler(self, name: str) -> bool:
        """Disable a handler by name.

        Args:
            name: Handler name to disable.

        Returns:
            True if handler was found and disabled.
        """
        with self._lock:
            for r in self._handlers:
                if r.name == name:
                    r.enabled = False
                    return True
        return False

    def close(self) -> None:
        """Close the router and all handlers.

        Calls close() on all registered handlers to release resources.
        """
        with self._lock:
            for registration in self._handlers:
                try:
                    registration.handler.close()
                except Exception as e:
                    logger.error(f"Error closing handler: {e}")
            self._handlers.clear()


def _compile_pattern(pattern: str) -> re.Pattern:
    """Compile a wildcard pattern to a regex.

    Args:
        pattern: Wildcard pattern (e.g., "git.*", "*").

    Returns:
        Compiled regex pattern.
    """
    # Convert glob-style pattern to regex
    # "*" matches any characters
    # "?" matches single character
    # "." is escaped to match literal dot
    regex = fnmatch.translate(pattern)
    return re.compile(regex)


# --- Global router instance ---

_default_router: EventRouter | None = None
_router_lock = threading.Lock()


def get_default_router() -> EventRouter:
    """Get or create the default event router.

    Returns:
        Singleton EventRouter instance.
    """
    global _default_router

    with _router_lock:
        if _default_router is None:
            _default_router = EventRouter()

    return _default_router


def reset_default_router() -> None:
    """Reset the default router (for testing)."""
    global _default_router

    with _router_lock:
        if _default_router is not None:
            _default_router.close()
        _default_router = None


def register_handler(
    pattern: str,
    handler: EventHandler,
    priority: int = 0,
    name: str | None = None,
) -> None:
    """Register a handler with the default router.

    Args:
        pattern: Event type pattern.
        handler: Handler instance.
        priority: Handler priority.
        name: Optional handler name.
    """
    get_default_router().register_handler(pattern, handler, priority, name)


def dispatch(
    event: dict[str, Any],
    filter: EventFilter | None = None,
) -> list[tuple[str, bool]]:
    """Dispatch an event using the default router.

    Args:
        event: Event dictionary.
        filter: Optional filter.

    Returns:
        List of (handler_name, success) tuples.
    """
    return get_default_router().dispatch(event, filter)
