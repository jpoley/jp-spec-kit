"""Tests for JSONL Event Writer (task-486).

Comprehensive test suite covering:
- EventWriter class with daily rotation
- emit_event synchronous emission
- emit_event_async non-blocking emission
- Schema validation integration
- Retention cleanup
- Event reading and querying
"""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from specify_cli.events.writer import (
    DEFAULT_EVENTS_DIR,
    DEFAULT_RETENTION_DAYS,
    SCHEMA_VERSION,
    EventWriter,
    EventWriterConfig,
    _build_event,
    emit_activity_progress,
    emit_decision_made,
    emit_event,
    emit_event_async,
    emit_git_commit,
    emit_lifecycle_completed,
    emit_lifecycle_started,
    emit_task_state_change,
    get_default_writer,
    reset_default_writer,
)


class TestEventWriterConfig:
    """Tests for EventWriterConfig dataclass."""

    def test_default_config(self):
        """Default config uses expected values."""
        config = EventWriterConfig()
        assert config.events_dir == Path(DEFAULT_EVENTS_DIR)
        assert config.retention_days == DEFAULT_RETENTION_DAYS
        assert config.validate_schema is True
        assert config.fail_silently is True

    def test_custom_config(self, tmp_path):
        """Custom config values are respected."""
        config = EventWriterConfig(
            events_dir=tmp_path / "custom_events",
            retention_days=7,
            validate_schema=False,
            fail_silently=False,
        )
        assert config.events_dir == tmp_path / "custom_events"
        assert config.retention_days == 7
        assert config.validate_schema is False
        assert config.fail_silently is False

    def test_string_path_conversion(self, tmp_path):
        """String paths are converted to Path objects."""
        config = EventWriterConfig(events_dir=str(tmp_path))
        assert isinstance(config.events_dir, Path)
        assert config.events_dir == tmp_path


class TestEventWriter:
    """Tests for EventWriter class."""

    @pytest.fixture
    def events_dir(self, tmp_path):
        """Create a temporary events directory."""
        events_dir = tmp_path / "events"
        events_dir.mkdir()
        return events_dir

    @pytest.fixture
    def writer(self, events_dir):
        """Create a writer with test configuration."""
        config = EventWriterConfig(
            events_dir=events_dir,
            validate_schema=False,  # Skip validation for basic tests
            fail_silently=True,
        )
        return EventWriter(config)

    @pytest.fixture
    def validating_writer(self, events_dir):
        """Create a writer with validation enabled."""
        config = EventWriterConfig(
            events_dir=events_dir,
            validate_schema=True,
            fail_silently=True,
        )
        return EventWriter(config)

    def test_write_event_creates_file(self, writer, events_dir):
        """Writing an event creates the daily JSONL file."""
        event = {
            "version": SCHEMA_VERSION,
            "event_type": "lifecycle.started",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": "@test",
        }

        success = writer.write_event(event)

        assert success
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        file_path = events_dir / f"events-{today}.jsonl"
        assert file_path.exists()

    def test_write_event_appends_jsonl(self, writer, events_dir):
        """Multiple events are appended to the same file."""
        event1 = {
            "version": SCHEMA_VERSION,
            "event_type": "lifecycle.started",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": "@test1",
        }
        event2 = {
            "version": SCHEMA_VERSION,
            "event_type": "lifecycle.completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": "@test2",
        }

        writer.write_event(event1)
        writer.write_event(event2)

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        file_path = events_dir / f"events-{today}.jsonl"

        lines = file_path.read_text().strip().split("\n")
        assert len(lines) == 2

        parsed1 = json.loads(lines[0])
        parsed2 = json.loads(lines[1])
        assert parsed1["agent_id"] == "@test1"
        assert parsed2["agent_id"] == "@test2"

    def test_write_events_batch(self, writer, events_dir):
        """write_events writes multiple events in batch."""
        events = [
            {
                "version": SCHEMA_VERSION,
                "event_type": f"lifecycle.event{i}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": f"@test{i}",
            }
            for i in range(5)
        ]

        written = writer.write_events(events)

        assert written == 5

    def test_validation_rejects_invalid_event(self, validating_writer):
        """Invalid events are rejected when validation is enabled."""
        invalid_event = {
            "version": "1.1.0",
            # Missing required fields: event_type, timestamp, agent_id
        }

        success = validating_writer.write_event(invalid_event)

        assert not success  # fail_silently=True, so no exception

    def test_validation_accepts_valid_event(self, validating_writer, events_dir):
        """Valid events pass validation."""
        valid_event = {
            "version": "1.1.0",
            "event_type": "lifecycle.started",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "agent_id": "@test",
        }

        success = validating_writer.write_event(valid_event)

        assert success

    def test_validation_disabled(self, writer, events_dir):
        """Invalid events are accepted when validation is disabled."""
        # Missing required fields
        invalid_event = {"custom_field": "value"}

        success = writer.write_event(invalid_event)

        assert success  # No validation

    def test_read_events_single_date(self, writer, events_dir):
        """Read events from a specific date."""
        event = {
            "version": SCHEMA_VERSION,
            "event_type": "lifecycle.started",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": "@test",
        }
        writer.write_event(event)

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        events = writer.read_events(date=today)

        assert len(events) == 1
        assert events[0]["agent_id"] == "@test"

    def test_read_events_default_today(self, writer, events_dir):
        """read_events() without args returns today's events."""
        event = {
            "version": SCHEMA_VERSION,
            "event_type": "lifecycle.started",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": "@test",
        }
        writer.write_event(event)

        events = writer.read_events()

        assert len(events) == 1

    def test_read_events_date_range(self, writer, events_dir):
        """Read events from date range."""
        # Create files for multiple dates
        dates = [
            (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%d"),
            (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d"),
            datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        ]

        for i, date_str in enumerate(dates):
            file_path = events_dir / f"events-{date_str}.jsonl"
            event = {"event_type": f"test.event{i}", "agent_id": f"@test{i}"}
            file_path.write_text(json.dumps(event) + "\n")

        events = writer.read_events(start_date=dates[0], end_date=dates[2])

        assert len(events) == 3

    def test_cleanup_removes_old_files(self, tmp_path):
        """Cleanup removes files older than retention period."""
        events_dir = tmp_path / "events"
        events_dir.mkdir()

        # Create old file (32 days ago)
        old_date = (datetime.now(timezone.utc) - timedelta(days=32)).strftime(
            "%Y-%m-%d"
        )
        old_file = events_dir / f"events-{old_date}.jsonl"
        old_file.write_text('{"test": true}\n')

        # Create recent file (today)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_file = events_dir / f"events-{today}.jsonl"
        today_file.write_text('{"test": true}\n')

        config = EventWriterConfig(events_dir=events_dir, retention_days=30)
        writer = EventWriter(config)

        removed = writer.cleanup()

        assert removed == 1
        assert not old_file.exists()
        assert today_file.exists()

    def test_thread_safe_writes(self, writer, events_dir):
        """Concurrent writes are thread-safe."""
        results = []

        def write_event(i):
            event = {
                "version": SCHEMA_VERSION,
                "event_type": "lifecycle.started",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": f"@thread{i}",
            }
            success = writer.write_event(event)
            results.append(success)

        threads = [threading.Thread(target=write_event, args=(i,)) for i in range(10)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(results)

        # Verify all events written
        events = writer.read_events()
        assert len(events) == 10


class TestBuildEvent:
    """Tests for _build_event helper."""

    def test_required_fields(self):
        """Event has all required fields."""
        event = _build_event(
            event_type="lifecycle.started",
            agent_id="@test",
        )

        assert event["version"] == SCHEMA_VERSION
        assert event["event_type"] == "lifecycle.started"
        assert event["agent_id"] == "@test"
        assert "timestamp" in event
        assert "event_id" in event

    def test_optional_fields(self):
        """Optional fields are included when provided."""
        event = _build_event(
            event_type="lifecycle.started",
            agent_id="@test",
            message="Test message",
            progress=0.5,
            context={"task_id": "task-123"},
        )

        assert event["message"] == "Test message"
        assert event["progress"] == 0.5
        assert event["context"]["task_id"] == "task-123"

    def test_namespace_objects(self):
        """Namespace objects are included correctly."""
        event = _build_event(
            event_type="task.state_change",
            agent_id="@test",
            task={"task_id": "task-123", "from_state": "To Do", "to_state": "In Progress"},
            git={"sha": "abc123", "branch_name": "main"},
        )

        assert event["task"]["task_id"] == "task-123"
        assert event["git"]["sha"] == "abc123"


class TestEmitEvent:
    """Tests for emit_event function."""

    @pytest.fixture(autouse=True)
    def reset_writer(self):
        """Reset global writer between tests."""
        reset_default_writer()
        yield
        reset_default_writer()

    def test_emit_event_basic(self, tmp_path):
        """Basic event emission works."""
        success = emit_event(
            event_type="lifecycle.started",
            agent_id="@test",
            message="Test event",
            project_root=tmp_path,
            validate=False,
        )

        assert success
        events_file = tmp_path / DEFAULT_EVENTS_DIR / f"events-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        assert events_file.exists()

    def test_emit_event_with_context(self, tmp_path):
        """Event with context is written correctly."""
        success = emit_event(
            event_type="task.state_change",
            agent_id="@backend-engineer",
            context={"task_id": "task-486", "branch_name": "feature/events"},
            project_root=tmp_path,
            validate=False,
        )

        assert success

        # Read and verify
        events_file = tmp_path / DEFAULT_EVENTS_DIR / f"events-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        event = json.loads(events_file.read_text().strip())
        assert event["context"]["task_id"] == "task-486"


class TestEmitEventAsync:
    """Tests for emit_event_async function."""

    @pytest.fixture(autouse=True)
    def reset_writer(self):
        """Reset global writer between tests."""
        reset_default_writer()
        yield
        reset_default_writer()

    def test_emit_event_async_returns_immediately(self, tmp_path):
        """Async emission returns immediately."""
        start = time.time()

        emit_event_async(
            event_type="lifecycle.started",
            agent_id="@test",
            project_root=tmp_path,
            validate=False,
        )

        elapsed = time.time() - start
        assert elapsed < 0.1  # Should return almost immediately

        # Wait for background thread
        time.sleep(0.5)

        # Verify event was written
        events_file = tmp_path / DEFAULT_EVENTS_DIR / f"events-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        assert events_file.exists()


class TestEmitHelpers:
    """Tests for convenience emit_* functions."""

    @pytest.fixture(autouse=True)
    def reset_writer(self):
        """Reset global writer between tests."""
        reset_default_writer()
        yield
        reset_default_writer()

    def test_emit_lifecycle_started(self, tmp_path):
        """emit_lifecycle_started helper works."""
        success = emit_lifecycle_started(
            agent_id="@test",
            message="Starting task",
            task_id="task-486",
            project_root=tmp_path,
            validate=False,
        )

        assert success

    def test_emit_lifecycle_completed(self, tmp_path):
        """emit_lifecycle_completed helper works."""
        success = emit_lifecycle_completed(
            agent_id="@test",
            message="Task complete",
            project_root=tmp_path,
            validate=False,
        )

        assert success

    def test_emit_activity_progress(self, tmp_path):
        """emit_activity_progress helper works."""
        success = emit_activity_progress(
            agent_id="@test",
            progress=0.75,
            message="75% complete",
            project_root=tmp_path,
            validate=False,
        )

        assert success

    def test_emit_task_state_change(self, tmp_path):
        """emit_task_state_change helper works."""
        success = emit_task_state_change(
            agent_id="@test",
            task_id="task-486",
            from_state="To Do",
            to_state="In Progress",
            title="Implement Event Writer",
            project_root=tmp_path,
            validate=False,
        )

        assert success

        # Verify event structure
        events_file = tmp_path / DEFAULT_EVENTS_DIR / f"events-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        event = json.loads(events_file.read_text().strip())
        assert event["event_type"] == "task.state_change"
        assert event["task"]["task_id"] == "task-486"
        assert event["task"]["from_state"] == "To Do"
        assert event["task"]["to_state"] == "In Progress"

    def test_emit_git_commit(self, tmp_path):
        """emit_git_commit helper works."""
        success = emit_git_commit(
            agent_id="@test",
            sha="abc123def456",
            message="feat: implement event writer",
            branch_name="feature/events",
            files_changed=5,
            project_root=tmp_path,
            validate=False,
        )

        assert success

        # Verify event structure
        events_file = tmp_path / DEFAULT_EVENTS_DIR / f"events-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        event = json.loads(events_file.read_text().strip())
        assert event["event_type"] == "git.commit"
        assert event["git"]["sha"] == "abc123def456"
        assert event["git"]["files_changed"] == 5

    def test_emit_decision_made(self, tmp_path):
        """emit_decision_made helper works."""
        success = emit_decision_made(
            agent_id="@architect",
            decision_id="ARCH-001",
            category="architecture",
            message="Chose JSONL format for events",
            reversibility_type="two-way-door",
            alternatives_considered=[
                {"option": "SQLite", "rejected_reason": "Complexity"},
                {"option": "PostgreSQL", "rejected_reason": "Overhead"},
            ],
            project_root=tmp_path,
            validate=False,
        )

        assert success

        # Verify event structure
        events_file = tmp_path / DEFAULT_EVENTS_DIR / f"events-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        event = json.loads(events_file.read_text().strip())
        assert event["event_type"] == "decision.made"
        assert event["decision"]["decision_id"] == "ARCH-001"
        assert len(event["decision"]["alternatives_considered"]) == 2


class TestGetDefaultWriter:
    """Tests for singleton writer management."""

    @pytest.fixture(autouse=True)
    def reset_writer(self):
        """Reset global writer between tests."""
        reset_default_writer()
        yield
        reset_default_writer()

    def test_singleton_instance(self, tmp_path):
        """get_default_writer returns singleton."""
        writer1 = get_default_writer(project_root=tmp_path)
        writer2 = get_default_writer()

        assert writer1 is writer2

    def test_reset_creates_new_instance(self, tmp_path):
        """reset_default_writer creates new instance."""
        writer1 = get_default_writer(project_root=tmp_path)
        reset_default_writer()
        writer2 = get_default_writer(project_root=tmp_path)

        assert writer1 is not writer2


class TestValidationIntegration:
    """Tests for schema validation integration."""

    @pytest.fixture(autouse=True)
    def reset_writer(self):
        """Reset global writer between tests."""
        reset_default_writer()
        yield
        reset_default_writer()

    def test_valid_lifecycle_event(self, tmp_path):
        """Valid lifecycle event passes validation."""
        success = emit_event(
            event_type="lifecycle.started",
            agent_id="@backend-engineer",
            message="Starting implementation",
            project_root=tmp_path,
            validate=True,
        )

        assert success

    def test_valid_activity_event(self, tmp_path):
        """Valid activity event passes validation."""
        success = emit_event(
            event_type="activity.progress",
            agent_id="@backend-engineer",
            progress=0.5,
            message="50% complete",
            project_root=tmp_path,
            validate=True,
        )

        assert success

    def test_invalid_event_type_namespace(self, tmp_path):
        """Invalid namespace in event_type fails validation."""
        success = emit_event(
            event_type="invalid_namespace.event",  # Not a valid namespace
            agent_id="@test",
            project_root=tmp_path,
            validate=True,
        )

        # Should fail validation (but fail_silently=True by default)
        assert not success

    def test_missing_required_field(self, tmp_path):
        """Event missing required field fails validation."""
        config = EventWriterConfig(
            events_dir=tmp_path / DEFAULT_EVENTS_DIR,
            validate_schema=True,
            fail_silently=True,
        )
        writer = EventWriter(config)

        # Missing agent_id
        event = {
            "version": "1.1.0",
            "event_type": "lifecycle.started",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            # Missing agent_id
        }

        success = writer.write_event(event)

        assert not success
