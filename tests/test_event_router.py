"""Tests for the Event Router system (task-487).

Tests cover:
- EventRouter registration and dispatch
- Pattern matching with wildcards
- EventFilter criteria matching
- Built-in handlers (JsonlHandler, McpHandler, LoggingHandler, etc.)
- Priority ordering and handler chaining
- Thread safety
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from specify_cli.events.handlers import (
    BufferHandler,
    CallbackHandler,
    CompositeHandler,
    FilteringHandler,
    JsonlHandler,
    LoggingHandler,
    McpHandler,
)
from specify_cli.events.router import (
    EventFilter,
    EventHandler,
    EventRouter,
    HandlerRegistration,
    _compile_pattern,
    dispatch,
    get_default_router,
    register_handler,
    reset_default_router,
)


# --- Test fixtures ---


@pytest.fixture
def router() -> EventRouter:
    """Create a fresh router for testing."""
    return EventRouter()


@pytest.fixture
def sample_event() -> dict[str, Any]:
    """Create a sample event for testing."""
    return {
        "event_type": "lifecycle.started",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_id": "@backend-engineer",
        "message": "Test event",
        "context": {
            "task_id": "task-487",
        },
    }


class MockHandler(EventHandler):
    """Mock handler that tracks calls."""

    def __init__(self, return_value: bool = True):
        self.calls: list[dict[str, Any]] = []
        self.return_value = return_value

    def handle(self, event: dict[str, Any]) -> bool:
        self.calls.append(event)
        return self.return_value


class FailingHandler(EventHandler):
    """Handler that always raises an exception."""

    def handle(self, event: dict[str, Any]) -> bool:
        raise RuntimeError("Handler failed")


# --- Pattern Matching Tests ---


class TestPatternMatching:
    """Tests for wildcard pattern matching."""

    def test_exact_match(self):
        """Test exact pattern matching."""
        pattern = _compile_pattern("lifecycle.started")
        assert pattern.match("lifecycle.started")
        assert not pattern.match("lifecycle.completed")
        assert not pattern.match("git.commit")

    def test_wildcard_suffix(self):
        """Test wildcard at end of pattern."""
        pattern = _compile_pattern("git.*")
        assert pattern.match("git.commit")
        assert pattern.match("git.push")
        assert pattern.match("git.branch")
        assert not pattern.match("lifecycle.started")
        assert not pattern.match("gitx.commit")

    def test_catch_all(self):
        """Test catch-all wildcard."""
        pattern = _compile_pattern("*")
        assert pattern.match("lifecycle.started")
        assert pattern.match("git.commit")
        assert pattern.match("anything")

    def test_partial_wildcard(self):
        """Test partial wildcard matching."""
        pattern = _compile_pattern("task_*")
        assert pattern.match("task_started")
        assert pattern.match("task_completed")
        assert not pattern.match("other_started")

    def test_question_mark_wildcard(self):
        """Test single character wildcard."""
        pattern = _compile_pattern("git.commit?")
        assert pattern.match("git.commit1")
        assert pattern.match("git.commitA")
        assert not pattern.match("git.commit")
        assert not pattern.match("git.commit12")


# --- HandlerRegistration Tests ---


class TestHandlerRegistration:
    """Tests for HandlerRegistration dataclass."""

    def test_registration_creation(self):
        """Test creating a handler registration."""
        handler = MockHandler()
        reg = HandlerRegistration(
            pattern="git.*",
            handler=handler,
            priority=10,
            name="git-handler",
        )

        assert reg.pattern == "git.*"
        assert reg.handler is handler
        assert reg.priority == 10
        assert reg.name == "git-handler"
        assert reg.enabled is True

    def test_registration_matches(self):
        """Test pattern matching on registration."""
        handler = MockHandler()
        reg = HandlerRegistration(pattern="lifecycle.*", handler=handler)

        assert reg.matches("lifecycle.started")
        assert reg.matches("lifecycle.completed")
        assert not reg.matches("git.commit")


# --- EventFilter Tests ---


class TestEventFilter:
    """Tests for EventFilter criteria matching."""

    def test_filter_by_task_id(self):
        """Test filtering by task ID."""
        filter = EventFilter(task_id="task-487")

        event_match = {"context": {"task_id": "task-487"}}
        event_no_match = {"context": {"task_id": "task-486"}}
        event_no_context = {"event_type": "test"}

        assert filter.matches(event_match)
        assert not filter.matches(event_no_match)
        assert not filter.matches(event_no_context)

    def test_filter_by_agent_id(self):
        """Test filtering by agent ID."""
        filter = EventFilter(agent_id="@backend-engineer")

        event_match = {"agent_id": "@backend-engineer"}
        event_no_match = {"agent_id": "@frontend-engineer"}

        assert filter.matches(event_match)
        assert not filter.matches(event_no_match)

    def test_filter_by_namespaces(self):
        """Test filtering by namespace."""
        filter = EventFilter(namespaces=["lifecycle", "git"])

        event_lifecycle = {"event_type": "lifecycle.started"}
        event_git = {"event_type": "git.commit"}
        event_task = {"event_type": "task.created"}

        assert filter.matches(event_lifecycle)
        assert filter.matches(event_git)
        assert not filter.matches(event_task)

    def test_filter_by_event_types(self):
        """Test filtering by exact event types."""
        filter = EventFilter(event_types=["lifecycle.started", "lifecycle.completed"])

        event_match = {"event_type": "lifecycle.started"}
        event_no_match = {"event_type": "lifecycle.error"}

        assert filter.matches(event_match)
        assert not filter.matches(event_no_match)

    def test_filter_by_time_range(self):
        """Test filtering by time range."""
        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=1)
        end = now + timedelta(hours=1)

        filter = EventFilter(start_time=start, end_time=end)

        event_in_range = {"timestamp": now.isoformat()}
        event_before = {"timestamp": (now - timedelta(hours=2)).isoformat()}
        event_after = {"timestamp": (now + timedelta(hours=2)).isoformat()}

        assert filter.matches(event_in_range)
        assert not filter.matches(event_before)
        assert not filter.matches(event_after)

    def test_filter_with_custom_function(self):
        """Test filtering with custom function."""
        filter = EventFilter(custom=lambda e: e.get("priority") == "high")

        event_match = {"priority": "high"}
        event_no_match = {"priority": "low"}

        assert filter.matches(event_match)
        assert not filter.matches(event_no_match)

    def test_filter_multiple_criteria(self):
        """Test filtering with multiple criteria (AND logic)."""
        filter = EventFilter(
            agent_id="@backend-engineer",
            task_id="task-487",
        )

        event_match = {
            "agent_id": "@backend-engineer",
            "context": {"task_id": "task-487"},
        }
        event_wrong_agent = {
            "agent_id": "@frontend-engineer",
            "context": {"task_id": "task-487"},
        }
        event_wrong_task = {
            "agent_id": "@backend-engineer",
            "context": {"task_id": "task-486"},
        }

        assert filter.matches(event_match)
        assert not filter.matches(event_wrong_agent)
        assert not filter.matches(event_wrong_task)

    def test_filter_none_criteria_matches_all(self):
        """Test that None criteria match any value."""
        filter = EventFilter()  # All None

        assert filter.matches({"event_type": "anything"})
        assert filter.matches({"agent_id": "@any"})


# --- EventRouter Tests ---


class TestEventRouter:
    """Tests for EventRouter class."""

    def test_register_handler(self, router: EventRouter):
        """Test registering a handler."""
        handler = MockHandler()
        router.register_handler("git.*", handler, name="git-handler")

        handlers = router.list_handlers()
        assert len(handlers) == 1
        assert handlers[0]["pattern"] == "git.*"
        assert handlers[0]["name"] == "git-handler"

    def test_register_multiple_handlers(self, router: EventRouter):
        """Test registering multiple handlers."""
        handler1 = MockHandler()
        handler2 = MockHandler()

        router.register_handler("git.*", handler1, name="git")
        router.register_handler("lifecycle.*", handler2, name="lifecycle")

        handlers = router.list_handlers()
        assert len(handlers) == 2

    def test_dispatch_to_matching_handler(self, router: EventRouter, sample_event: dict):
        """Test dispatching to matching handlers."""
        handler = MockHandler()
        router.register_handler("lifecycle.*", handler)

        results = router.dispatch(sample_event)

        assert len(results) == 1
        assert results[0][1] is True  # Success
        assert len(handler.calls) == 1
        assert handler.calls[0] == sample_event

    def test_dispatch_to_multiple_handlers(self, router: EventRouter, sample_event: dict):
        """Test dispatching to multiple matching handlers."""
        handler1 = MockHandler()
        handler2 = MockHandler()

        router.register_handler("lifecycle.*", handler1, name="h1")
        router.register_handler("*", handler2, name="h2")

        results = router.dispatch(sample_event)

        assert len(results) == 2
        assert len(handler1.calls) == 1
        assert len(handler2.calls) == 1

    def test_dispatch_skips_non_matching(self, router: EventRouter, sample_event: dict):
        """Test that non-matching handlers are skipped."""
        handler = MockHandler()
        router.register_handler("git.*", handler)

        results = router.dispatch(sample_event)  # lifecycle.started

        assert len(results) == 0
        assert len(handler.calls) == 0

    def test_priority_ordering(self, router: EventRouter, sample_event: dict):
        """Test handlers are called in priority order."""
        call_order = []

        def make_handler(name: str):
            handler = MockHandler()
            original_handle = handler.handle
            def tracking_handle(event):
                call_order.append(name)
                return original_handle(event)
            handler.handle = tracking_handle
            return handler

        h_low = make_handler("low")
        h_high = make_handler("high")
        h_medium = make_handler("medium")

        router.register_handler("*", h_low, priority=0, name="low")
        router.register_handler("*", h_high, priority=100, name="high")
        router.register_handler("*", h_medium, priority=50, name="medium")

        router.dispatch(sample_event)

        assert call_order == ["high", "medium", "low"]

    def test_handler_exception_caught(self, router: EventRouter, sample_event: dict):
        """Test that handler exceptions are caught."""
        failing = FailingHandler()
        success = MockHandler()

        router.register_handler("*", failing, priority=10, name="failing")
        router.register_handler("*", success, priority=0, name="success")

        results = router.dispatch(sample_event)

        assert len(results) == 2
        assert results[0] == ("failing", False)
        assert results[1] == ("success", True)
        assert len(success.calls) == 1  # Still called despite earlier failure

    def test_unregister_by_pattern(self, router: EventRouter):
        """Test unregistering handlers by pattern."""
        handler = MockHandler()
        router.register_handler("git.*", handler)
        router.register_handler("lifecycle.*", handler)

        removed = router.unregister_handler(pattern="git.*")

        assert removed == 1
        assert len(router.list_handlers()) == 1

    def test_unregister_by_name(self, router: EventRouter):
        """Test unregistering handlers by name."""
        handler = MockHandler()
        router.register_handler("*", handler, name="to-remove")
        router.register_handler("*", handler, name="to-keep")

        removed = router.unregister_handler(name="to-remove")

        assert removed == 1
        handlers = router.list_handlers()
        assert len(handlers) == 1
        assert handlers[0]["name"] == "to-keep"

    def test_enable_disable_handler(self, router: EventRouter, sample_event: dict):
        """Test enabling/disabling handlers."""
        handler = MockHandler()
        router.register_handler("*", handler, name="test")

        # Disable
        result = router.disable_handler("test")
        assert result is True

        router.dispatch(sample_event)
        assert len(handler.calls) == 0

        # Re-enable
        result = router.enable_handler("test")
        assert result is True

        router.dispatch(sample_event)
        assert len(handler.calls) == 1

    def test_global_filter(self, router: EventRouter):
        """Test global filter applies to all dispatches."""
        handler = MockHandler()
        router.register_handler("*", handler)

        router.set_global_filter(EventFilter(agent_id="@backend-engineer"))

        event_match = {"event_type": "test", "agent_id": "@backend-engineer"}
        event_no_match = {"event_type": "test", "agent_id": "@frontend-engineer"}

        router.dispatch(event_match)
        router.dispatch(event_no_match)

        assert len(handler.calls) == 1
        assert handler.calls[0]["agent_id"] == "@backend-engineer"

    def test_dispatch_filter(self, router: EventRouter, sample_event: dict):
        """Test per-dispatch filter."""
        handler = MockHandler()
        router.register_handler("*", handler)

        filter = EventFilter(task_id="task-999")  # Won't match sample_event

        results = router.dispatch(sample_event, filter=filter)

        assert len(results) == 0
        assert len(handler.calls) == 0

    def test_get_matching_handlers(self, router: EventRouter):
        """Test getting handlers that match an event type."""
        h1 = MockHandler()
        h2 = MockHandler()
        h3 = MockHandler()

        router.register_handler("git.*", h1, name="git")
        router.register_handler("*", h2, name="catchall")
        router.register_handler("lifecycle.*", h3, name="lifecycle")

        matches = router.get_matching_handlers("git.commit")

        assert len(matches) == 2
        names = [m.name for m in matches]
        assert "git" in names
        assert "catchall" in names

    def test_close_closes_handlers(self, router: EventRouter):
        """Test closing router closes all handlers."""
        handler = MockHandler()
        handler.close = MagicMock()

        router.register_handler("*", handler)
        router.close()

        handler.close.assert_called_once()
        assert len(router.list_handlers()) == 0

    def test_dispatch_async(self, router: EventRouter, sample_event: dict):
        """Test async dispatch."""
        handler = MockHandler()
        router.register_handler("*", handler)

        router.dispatch_async(sample_event)

        # Wait a bit for async thread
        time.sleep(0.1)

        assert len(handler.calls) == 1


class TestEventRouterThreadSafety:
    """Tests for thread safety of EventRouter."""

    def test_concurrent_dispatch(self, router: EventRouter):
        """Test concurrent dispatch from multiple threads."""
        handler = MockHandler()
        router.register_handler("*", handler)

        event = {"event_type": "test"}
        num_threads = 10
        events_per_thread = 100

        def dispatch_events():
            for _ in range(events_per_thread):
                router.dispatch(event)

        threads = [
            threading.Thread(target=dispatch_events)
            for _ in range(num_threads)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(handler.calls) == num_threads * events_per_thread

    def test_concurrent_registration(self, router: EventRouter):
        """Test concurrent handler registration."""
        num_threads = 10

        def register_handler(i: int):
            handler = MockHandler()
            router.register_handler("*", handler, name=f"handler-{i}")

        threads = [
            threading.Thread(target=register_handler, args=(i,))
            for i in range(num_threads)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(router.list_handlers()) == num_threads


# --- Module-level Function Tests ---


class TestModuleFunctions:
    """Tests for module-level convenience functions."""

    def setup_method(self):
        """Reset default router before each test."""
        reset_default_router()

    def teardown_method(self):
        """Reset default router after each test."""
        reset_default_router()

    def test_get_default_router(self):
        """Test getting default router singleton."""
        router1 = get_default_router()
        router2 = get_default_router()

        assert router1 is router2

    def test_register_handler_module_function(self):
        """Test module-level register_handler."""
        handler = MockHandler()
        register_handler("*", handler, name="test")

        router = get_default_router()
        handlers = router.list_handlers()

        assert len(handlers) == 1
        assert handlers[0]["name"] == "test"

    def test_dispatch_module_function(self):
        """Test module-level dispatch."""
        handler = MockHandler()
        register_handler("*", handler)

        event = {"event_type": "test"}
        results = dispatch(event)

        assert len(results) == 1
        assert len(handler.calls) == 1


# --- Built-in Handler Tests ---


class TestJsonlHandler:
    """Tests for JsonlHandler."""

    def test_jsonl_handler_writes(self, tmp_path: Path):
        """Test JsonlHandler writes events."""
        handler = JsonlHandler(project_root=tmp_path, validate=False)

        event = {
            "event_type": "test",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        result = handler.handle(event)
        assert result is True

        handler.close()

    def test_jsonl_handler_close(self, tmp_path: Path):
        """Test JsonlHandler close resets writer."""
        handler = JsonlHandler(project_root=tmp_path, validate=False)

        # Force writer creation
        handler._get_writer()
        assert handler._writer is not None

        handler.close()
        assert handler._writer is None


class TestMcpHandler:
    """Tests for McpHandler."""

    def test_mcp_handler_no_config(self):
        """Test McpHandler with no config returns False."""
        handler = McpHandler()

        result = handler.handle({"event_type": "test"})

        assert result is False

    def test_mcp_handler_http_forward(self):
        """Test McpHandler HTTP forwarding."""
        handler = McpHandler(server_url="http://localhost:8080/events")

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            result = handler.handle({"event_type": "test"})

            assert result is True
            mock_urlopen.assert_called_once()

    def test_mcp_handler_http_error(self):
        """Test McpHandler handles HTTP errors."""
        handler = McpHandler(server_url="http://localhost:8080/events")

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = Exception("Connection refused")

            result = handler.handle({"event_type": "test"})

            assert result is False

    def test_mcp_handler_local_forward(self):
        """Test McpHandler local forwarding (logs debug)."""
        handler = McpHandler(server_name="test-server")

        result = handler.handle({"event_type": "test"})

        assert result is True


class TestLoggingHandler:
    """Tests for LoggingHandler."""

    def test_logging_handler_logs(self, caplog):
        """Test LoggingHandler logs events."""
        handler = LoggingHandler(level="INFO")

        event = {
            "event_type": "lifecycle.started",
            "agent_id": "@backend-engineer",
            "message": "Test message",
        }

        with caplog.at_level(logging.INFO):
            result = handler.handle(event)

        assert result is True
        assert "lifecycle.started" in caplog.text
        assert "@backend-engineer" in caplog.text

    def test_logging_handler_full_event(self, caplog):
        """Test LoggingHandler with full event logging."""
        handler = LoggingHandler(level="DEBUG", include_full_event=True)

        event = {"event_type": "test", "data": "value"}

        with caplog.at_level(logging.DEBUG):
            handler.handle(event)

        assert '"event_type": "test"' in caplog.text


class TestCallbackHandler:
    """Tests for CallbackHandler."""

    def test_callback_handler_calls(self):
        """Test CallbackHandler calls callback."""
        calls = []

        def callback(event):
            calls.append(event)
            return True

        handler = CallbackHandler(callback)

        event = {"event_type": "test"}
        result = handler.handle(event)

        assert result is True
        assert len(calls) == 1
        assert calls[0] == event

    def test_callback_handler_exception(self):
        """Test CallbackHandler catches exceptions."""
        def bad_callback(event):
            raise ValueError("Bad")

        handler = CallbackHandler(bad_callback, name="bad")

        result = handler.handle({"event_type": "test"})

        assert result is False


class TestBufferHandler:
    """Tests for BufferHandler."""

    def test_buffer_handler_buffers(self):
        """Test BufferHandler buffers events."""
        flush_calls = []

        def on_flush(events):
            flush_calls.append(events)
            return True

        handler = BufferHandler(max_size=5, on_flush=on_flush)

        # Add events under threshold
        for i in range(3):
            handler.handle({"event_type": f"test-{i}"})

        assert len(flush_calls) == 0

        # Manual flush
        handler.flush()

        assert len(flush_calls) == 1
        assert len(flush_calls[0]) == 3

    def test_buffer_handler_auto_flush_size(self):
        """Test BufferHandler auto-flushes at max size."""
        flush_calls = []

        def on_flush(events):
            flush_calls.append(events)
            return True

        handler = BufferHandler(max_size=3, on_flush=on_flush)

        for i in range(3):
            handler.handle({"event_type": f"test-{i}"})

        assert len(flush_calls) == 1
        assert len(flush_calls[0]) == 3

    def test_buffer_handler_close_flushes(self):
        """Test BufferHandler flushes on close."""
        flush_calls = []

        def on_flush(events):
            flush_calls.append(events)
            return True

        handler = BufferHandler(max_size=100, on_flush=on_flush)

        handler.handle({"event_type": "test"})
        handler.close()

        assert len(flush_calls) == 1


class TestFilteringHandler:
    """Tests for FilteringHandler."""

    def test_filtering_handler_passes(self):
        """Test FilteringHandler passes matching events."""
        inner = MockHandler()
        filter = EventFilter(agent_id="@backend-engineer")
        handler = FilteringHandler(inner, filter)

        event = {"event_type": "test", "agent_id": "@backend-engineer"}
        result = handler.handle(event)

        assert result is True
        assert len(inner.calls) == 1

    def test_filtering_handler_filters(self):
        """Test FilteringHandler filters non-matching events."""
        inner = MockHandler()
        filter = EventFilter(agent_id="@backend-engineer")
        handler = FilteringHandler(inner, filter)

        event = {"event_type": "test", "agent_id": "@frontend-engineer"}
        result = handler.handle(event)

        assert result is True  # Filtered out is not an error
        assert len(inner.calls) == 0


class TestCompositeHandler:
    """Tests for CompositeHandler."""

    def test_composite_handler_forwards_all(self):
        """Test CompositeHandler forwards to all handlers."""
        h1 = MockHandler()
        h2 = MockHandler()

        handler = CompositeHandler([h1, h2])

        event = {"event_type": "test"}
        result = handler.handle(event)

        assert result is True
        assert len(h1.calls) == 1
        assert len(h2.calls) == 1

    def test_composite_handler_require_all_false(self):
        """Test CompositeHandler require_all=False (any success)."""
        h1 = MockHandler(return_value=True)
        h2 = MockHandler(return_value=False)

        handler = CompositeHandler([h1, h2], require_all=False)

        result = handler.handle({"event_type": "test"})

        assert result is True  # At least one succeeded

    def test_composite_handler_require_all_true(self):
        """Test CompositeHandler require_all=True (all must succeed)."""
        h1 = MockHandler(return_value=True)
        h2 = MockHandler(return_value=False)

        handler = CompositeHandler([h1, h2], require_all=True)

        result = handler.handle({"event_type": "test"})

        assert result is False  # Not all succeeded

    def test_composite_handler_close_all(self):
        """Test CompositeHandler closes all handlers."""
        h1 = MockHandler()
        h2 = MockHandler()
        h1.close = MagicMock()
        h2.close = MagicMock()

        handler = CompositeHandler([h1, h2])
        handler.close()

        h1.close.assert_called_once()
        h2.close.assert_called_once()
