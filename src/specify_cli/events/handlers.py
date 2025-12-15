"""Built-in event handlers for the event routing system.

This module provides ready-to-use handlers for common event destinations:
- JsonlHandler: Write events to JSONL files (integrates with task-486 writer)
- McpHandler: Forward events to MCP server
- LoggingHandler: Log events to Python logging
- CallbackHandler: Execute a callback function
- BufferHandler: Buffer events for batch processing

Example:
    >>> from specify_cli.events.router import EventRouter
    >>> from specify_cli.events.handlers import JsonlHandler, LoggingHandler
    >>>
    >>> router = EventRouter()
    >>> router.register_handler("*", JsonlHandler())
    >>> router.register_handler("lifecycle.*", LoggingHandler(level="INFO"))
"""

from __future__ import annotations

import json
import logging
import threading
import time
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from .router import EventHandler

if TYPE_CHECKING:
    from .router import EventFilter

logger = logging.getLogger(__name__)


class JsonlHandler(EventHandler):
    """Handler that writes events to JSONL files.

    Integrates with the EventWriter from task-486 for daily rotation
    and retention management.

    Attributes:
        project_root: Project root directory for events.
        validate: Whether to validate events before writing.

    Example:
        >>> handler = JsonlHandler(project_root=Path("/project"))
        >>> router.register_handler("*", handler)
    """

    def __init__(
        self,
        project_root: Path | str | None = None,
        validate: bool = True,
    ) -> None:
        """Initialize the JSONL handler.

        Args:
            project_root: Project root directory. Uses cwd if not specified.
            validate: Whether to validate events against schema.
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.validate = validate
        self._writer = None

    def _get_writer(self):
        """Lazy-load the event writer."""
        if self._writer is None:
            from .writer import get_default_writer

            self._writer = get_default_writer(project_root=self.project_root)
        return self._writer

    def handle(self, event: dict[str, Any]) -> bool:
        """Write event to JSONL file.

        Args:
            event: Event dictionary to write.

        Returns:
            True if write succeeded.
        """
        try:
            writer = self._get_writer()
            # Temporarily set validation based on handler config
            original_validate = writer.config.validate_schema
            writer.config.validate_schema = self.validate
            try:
                return writer.write_event(event)
            finally:
                writer.config.validate_schema = original_validate
        except Exception as e:
            logger.error(f"JsonlHandler write failed: {e}")
            return False

    def close(self) -> None:
        """Close the handler (writer cleanup is handled globally)."""
        self._writer = None


class McpHandler(EventHandler):
    """Handler that forwards events to an MCP server.

    Sends events to a configured MCP server endpoint for external
    processing, aggregation, or forwarding.

    Attributes:
        server_url: MCP server URL.
        timeout: Request timeout in seconds.

    Example:
        >>> handler = McpHandler(server_url="http://localhost:8080/events")
        >>> router.register_handler("*", handler)
    """

    def __init__(
        self,
        server_url: str | None = None,
        server_name: str | None = None,
        timeout: float = 5.0,
    ) -> None:
        """Initialize the MCP handler.

        Args:
            server_url: MCP server URL for HTTP forwarding.
            server_name: MCP server name for local forwarding.
            timeout: Request timeout in seconds.
        """
        self.server_url = server_url
        self.server_name = server_name
        self.timeout = timeout
        self._session = None

    def handle(self, event: dict[str, Any]) -> bool:
        """Forward event to MCP server.

        Args:
            event: Event dictionary to forward.

        Returns:
            True if forwarding succeeded.
        """
        if self.server_url:
            return self._forward_http(event)
        elif self.server_name:
            return self._forward_local(event)
        else:
            logger.warning("McpHandler: No server_url or server_name configured")
            return False

    def _forward_http(self, event: dict[str, Any]) -> bool:
        """Forward event via HTTP."""
        try:
            import urllib.request

            data = json.dumps(event).encode("utf-8")
            req = urllib.request.Request(
                self.server_url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                return response.status == 200

        except Exception as e:
            logger.error(f"McpHandler HTTP forward failed: {e}")
            return False

    def _forward_local(self, event: dict[str, Any]) -> bool:
        """Forward event to local MCP server via tool call."""
        # This would integrate with the MCP client if available
        logger.debug(f"McpHandler would forward to {self.server_name}: {event.get('event_type')}")
        # For now, just log (actual MCP integration depends on runtime context)
        return True

    def close(self) -> None:
        """Close any open connections."""
        self._session = None


class LoggingHandler(EventHandler):
    """Handler that logs events to Python logging.

    Useful for debugging and development. Logs event details at
    a configurable level.

    Attributes:
        level: Logging level (DEBUG, INFO, WARNING, ERROR).
        logger_name: Logger name to use.

    Example:
        >>> handler = LoggingHandler(level="INFO")
        >>> router.register_handler("lifecycle.*", handler)
    """

    def __init__(
        self,
        level: str = "INFO",
        logger_name: str = "specify_cli.events",
        include_full_event: bool = False,
    ) -> None:
        """Initialize the logging handler.

        Args:
            level: Logging level name.
            logger_name: Logger name to use.
            include_full_event: Whether to log full event JSON.
        """
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.logger = logging.getLogger(logger_name)
        self.include_full_event = include_full_event

    def handle(self, event: dict[str, Any]) -> bool:
        """Log the event.

        Args:
            event: Event dictionary to log.

        Returns:
            Always returns True.
        """
        event_type = event.get("event_type", "unknown")
        agent_id = event.get("agent_id", "unknown")
        message = event.get("message", "")

        log_message = f"[{event_type}] agent={agent_id}"
        if message:
            log_message += f" - {message}"

        if self.include_full_event:
            log_message += f"\n{json.dumps(event, indent=2)}"

        self.logger.log(self.level, log_message)
        return True


class CallbackHandler(EventHandler):
    """Handler that executes a callback function.

    Allows custom event processing without creating a full handler class.

    Attributes:
        callback: Function to call with event.

    Example:
        >>> def my_callback(event):
        ...     print(f"Received: {event['event_type']}")
        ...     return True
        >>> handler = CallbackHandler(my_callback)
        >>> router.register_handler("*", handler)
    """

    def __init__(
        self,
        callback: Callable[[dict[str, Any]], bool],
        name: str | None = None,
    ) -> None:
        """Initialize the callback handler.

        Args:
            callback: Function to call with event. Should return bool.
            name: Optional handler name for debugging.
        """
        self.callback = callback
        self.name = name or callback.__name__

    def handle(self, event: dict[str, Any]) -> bool:
        """Execute the callback with the event.

        Args:
            event: Event dictionary.

        Returns:
            Return value from callback.
        """
        try:
            return self.callback(event)
        except Exception as e:
            logger.error(f"CallbackHandler '{self.name}' raised: {e}")
            return False


class BufferHandler(EventHandler):
    """Handler that buffers events for batch processing.

    Collects events until a threshold is reached or timeout expires,
    then calls a flush callback with all buffered events.

    Attributes:
        max_size: Maximum buffer size before flush.
        max_age_seconds: Maximum age of oldest event before flush.
        on_flush: Callback to process buffered events.

    Example:
        >>> def process_batch(events):
        ...     print(f"Processing {len(events)} events")
        ...     return True
        >>> handler = BufferHandler(max_size=100, on_flush=process_batch)
        >>> router.register_handler("*", handler)
    """

    def __init__(
        self,
        max_size: int = 100,
        max_age_seconds: float = 60.0,
        on_flush: Callable[[list[dict[str, Any]]], bool] | None = None,
    ) -> None:
        """Initialize the buffer handler.

        Args:
            max_size: Maximum events before flush.
            max_age_seconds: Maximum time before flush.
            on_flush: Callback to process events.
        """
        self.max_size = max_size
        self.max_age_seconds = max_age_seconds
        self.on_flush = on_flush
        self._buffer: deque = deque()
        self._oldest_time: float | None = None
        self._lock = threading.Lock()

    def handle(self, event: dict[str, Any]) -> bool:
        """Buffer an event.

        Args:
            event: Event dictionary to buffer.

        Returns:
            True if buffered/flushed successfully.
        """
        with self._lock:
            now = time.time()

            # Record oldest event time
            if self._oldest_time is None:
                self._oldest_time = now

            self._buffer.append(event)

            # Check flush conditions
            should_flush = (
                len(self._buffer) >= self.max_size
                or (now - self._oldest_time) >= self.max_age_seconds
            )

            if should_flush:
                return self._flush()

        return True

    def _flush(self) -> bool:
        """Flush buffered events.

        Returns:
            True if flush succeeded.
        """
        if not self._buffer:
            return True

        events = list(self._buffer)
        self._buffer.clear()
        self._oldest_time = None

        if self.on_flush:
            try:
                return self.on_flush(events)
            except Exception as e:
                logger.error(f"BufferHandler flush callback failed: {e}")
                return False

        return True

    def flush(self) -> bool:
        """Manually flush buffered events.

        Returns:
            True if flush succeeded.
        """
        with self._lock:
            return self._flush()

    def close(self) -> None:
        """Flush and close the handler."""
        self.flush()


class FilteringHandler(EventHandler):
    """Handler wrapper that applies additional filtering.

    Wraps another handler and only forwards events that pass
    the specified filter.

    Attributes:
        inner: Wrapped handler.
        filter: Event filter to apply.

    Example:
        >>> from specify_cli.events.router import EventFilter
        >>> inner = JsonlHandler()
        >>> filter = EventFilter(agent_id="@backend-engineer")
        >>> handler = FilteringHandler(inner, filter)
        >>> router.register_handler("*", handler)
    """

    def __init__(
        self,
        inner: EventHandler,
        filter: "EventFilter",
    ) -> None:
        """Initialize the filtering handler.

        Args:
            inner: Handler to wrap.
            filter: Filter to apply.
        """

        self.inner = inner
        self.filter = filter

    def handle(self, event: dict[str, Any]) -> bool:
        """Handle event if it passes filter.

        Args:
            event: Event dictionary.

        Returns:
            True if filtered out or handled successfully.
        """
        if not self.filter.matches(event):
            return True  # Filtered out, but not an error

        return self.inner.handle(event)

    def close(self) -> None:
        """Close the inner handler."""
        self.inner.close()


class CompositeHandler(EventHandler):
    """Handler that forwards to multiple handlers.

    Useful for sending events to multiple destinations with a
    single registration.

    Attributes:
        handlers: List of handlers to forward to.
        require_all: If True, return False if any handler fails.

    Example:
        >>> handlers = [JsonlHandler(), LoggingHandler()]
        >>> composite = CompositeHandler(handlers)
        >>> router.register_handler("*", composite)
    """

    def __init__(
        self,
        handlers: list[EventHandler],
        require_all: bool = False,
    ) -> None:
        """Initialize the composite handler.

        Args:
            handlers: List of handlers to forward to.
            require_all: Whether all handlers must succeed.
        """
        self.handlers = handlers
        self.require_all = require_all

    def handle(self, event: dict[str, Any]) -> bool:
        """Forward event to all handlers.

        Args:
            event: Event dictionary.

        Returns:
            True if successful (based on require_all setting).
        """
        results = []
        for handler in self.handlers:
            try:
                result = handler.handle(event)
                results.append(result)
            except Exception as e:
                logger.error(f"CompositeHandler child failed: {e}")
                results.append(False)

        if self.require_all:
            return all(results)
        else:
            return any(results) if results else True

    def close(self) -> None:
        """Close all handlers."""
        for handler in self.handlers:
            try:
                handler.close()
            except Exception as e:
                logger.error(f"Error closing handler: {e}")
