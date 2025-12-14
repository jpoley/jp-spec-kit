"""Unit tests for the telemetry module."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

from specify_cli.telemetry import (
    RoleEvent,
    TelemetryEvent,
    TelemetryWriter,
    hash_pii,
    reset_writer,
    sanitize_path,
    sanitize_value,
    track_role_event,
)


class TestRoleEvent:
    """Tests for the RoleEvent enum."""

    def test_role_event_values(self):
        """Test that RoleEvent has expected values."""
        assert RoleEvent.ROLE_SELECTED.value == "role.selected"
        assert RoleEvent.AGENT_INVOKED.value == "agent.invoked"
        assert RoleEvent.HANDOFF_CLICKED.value == "handoff.clicked"

    def test_role_event_str(self):
        """Test string representation of RoleEvent."""
        assert str(RoleEvent.ROLE_SELECTED) == "role.selected"
        assert str(RoleEvent.AGENT_COMPLETED) == "agent.completed"

    def test_role_event_from_string(self):
        """Test creating RoleEvent from string value."""
        event = RoleEvent("role.selected")
        assert event == RoleEvent.ROLE_SELECTED

    def test_all_event_types_defined(self):
        """Test that all expected event types are defined."""
        expected_events = [
            "role.selected",
            "role.changed",
            "agent.invoked",
            "agent.started",
            "agent.completed",
            "agent.failed",
            "handoff.clicked",
            "command.executed",
            "workflow.started",
        ]
        actual_events = [e.value for e in RoleEvent]
        for expected in expected_events:
            assert expected in actual_events, f"Missing event: {expected}"


class TestTelemetryEvent:
    """Tests for the TelemetryEvent dataclass."""

    def test_create_event(self):
        """Test creating a telemetry event."""
        event = TelemetryEvent.create(
            RoleEvent.ROLE_SELECTED,
            role="dev",
            command="/flow:implement",
        )
        assert event.event_type == RoleEvent.ROLE_SELECTED
        assert event.role == "dev"
        assert event.command == "/flow:implement"
        assert event.timestamp is not None

    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        event = TelemetryEvent.create(
            RoleEvent.AGENT_INVOKED,
            role="qa",
            agent="qa-engineer",
            context={"task_id": "task-123"},
        )
        data = event.to_dict()

        assert data["event_type"] == "agent.invoked"
        assert data["role"] == "qa"
        assert data["agent"] == "qa-engineer"
        assert data["context"]["task_id"] == "task-123"
        assert "timestamp" in data

    def test_event_optional_fields(self):
        """Test that optional fields are excluded if not set."""
        event = TelemetryEvent.create(RoleEvent.WORKFLOW_STARTED)
        data = event.to_dict()

        assert "event_type" in data
        assert "timestamp" in data
        assert "role" not in data  # Optional, not set
        assert "command" not in data  # Optional, not set


class TestHashPii:
    """Tests for the hash_pii function."""

    def test_hash_returns_string(self):
        """Test that hash returns a string."""
        result = hash_pii("test-value")
        assert isinstance(result, str)

    def test_hash_length(self):
        """Test that hash is 12 characters."""
        result = hash_pii("any-value")
        assert len(result) == 12

    def test_hash_deterministic(self):
        """Test that same input produces same hash."""
        hash1 = hash_pii("consistent-input")
        hash2 = hash_pii("consistent-input")
        assert hash1 == hash2

    def test_hash_different_inputs(self):
        """Test that different inputs produce different hashes."""
        hash1 = hash_pii("value-one")
        hash2 = hash_pii("value-two")
        assert hash1 != hash2

    def test_hash_with_salt(self):
        """Test that salt changes the hash."""
        hash1 = hash_pii("value", salt="")
        hash2 = hash_pii("value", salt="secret")
        assert hash1 != hash2


class TestSanitizePath:
    """Tests for the sanitize_path function."""

    def test_sanitize_linux_home_path(self):
        """Test sanitizing Linux home directory path."""
        result = sanitize_path("/home/jpoley/project/file.py")
        assert "jpoley" not in result
        assert "/home/<" in result
        assert ">/project/file.py" in result

    def test_sanitize_mac_home_path(self):
        """Test sanitizing macOS home directory path."""
        result = sanitize_path("/Users/john/Documents/code.py")
        assert "john" not in result
        assert "/home/<" in result or "/Users/<" in result

    def test_non_home_path_unchanged(self):
        """Test that non-home paths are not modified."""
        result = sanitize_path("/var/log/app.log")
        assert result == "/var/log/app.log"

    def test_relative_path_unchanged(self):
        """Test that relative paths are not modified."""
        result = sanitize_path("src/main.py")
        assert result == "src/main.py"


class TestSanitizeValue:
    """Tests for the sanitize_value function."""

    def test_sanitize_email(self):
        """Test sanitizing email addresses."""
        result = sanitize_value("Contact: user@example.com for info")
        assert "user@example.com" not in result
        assert "<email:" in result

    def test_sanitize_username(self):
        """Test sanitizing usernames."""
        result = sanitize_value("Assigned to @johndoe")
        assert "@johndoe" not in result
        assert "@<" in result

    def test_sanitize_dict(self):
        """Test sanitizing dictionary values."""
        data = {
            "user": "@admin",
            "email": "admin@company.com",
            "count": 42,
        }
        result = sanitize_value(data)
        assert "@admin" not in result["user"]
        assert "admin@company.com" not in result["email"]
        assert result["count"] == 42

    def test_sanitize_list(self):
        """Test sanitizing list values."""
        data = ["@user1", "@user2", "normal-text"]
        result = sanitize_value(data)
        assert "@user1" not in result[0]
        assert "@user2" not in result[1]
        assert result[2] == "normal-text"

    def test_sanitize_project_field(self):
        """Test that project field names trigger hashing."""
        result = sanitize_value("my-secret-project", field_name="project")
        assert "my-secret-project" not in result
        assert "<project:" in result

    def test_sanitize_none(self):
        """Test that None is returned unchanged."""
        assert sanitize_value(None) is None


class TestTelemetryWriter:
    """Tests for the TelemetryWriter class."""

    @pytest.fixture
    def temp_telemetry_file(self) -> Path:
        """Create a temporary telemetry file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "telemetry.jsonl"

    def test_write_event(self, temp_telemetry_file: Path):
        """Test writing a single event."""
        writer = TelemetryWriter(temp_telemetry_file)
        event = TelemetryEvent.create(RoleEvent.ROLE_SELECTED, role="dev")

        result = writer.write_event(event)

        assert result is True
        assert temp_telemetry_file.exists()

        # Verify content
        content = temp_telemetry_file.read_text()
        data = json.loads(content.strip())
        assert data["event_type"] == "role.selected"
        assert data["role"] == "dev"

    def test_write_multiple_events(self, temp_telemetry_file: Path):
        """Test writing multiple events."""
        writer = TelemetryWriter(temp_telemetry_file)
        events = [
            TelemetryEvent.create(RoleEvent.WORKFLOW_STARTED),
            TelemetryEvent.create(RoleEvent.AGENT_INVOKED, agent="test"),
            TelemetryEvent.create(RoleEvent.WORKFLOW_COMPLETED),
        ]

        written = writer.write_events(events)

        assert written == 3
        assert writer.count_events() == 3

    def test_read_events(self, temp_telemetry_file: Path):
        """Test reading events from file."""
        writer = TelemetryWriter(temp_telemetry_file)
        for i in range(5):
            event = TelemetryEvent.create(
                RoleEvent.AGENT_PROGRESS, context={"index": i}
            )
            writer.write_event(event)

        events = writer.read_events(limit=3)

        assert len(events) == 3
        # Most recent first
        assert events[0]["context"]["index"] == 4

    def test_clear_events(self, temp_telemetry_file: Path):
        """Test clearing all events."""
        writer = TelemetryWriter(temp_telemetry_file)
        event = TelemetryEvent.create(RoleEvent.ROLE_SELECTED)
        writer.write_event(event)

        assert writer.count_events() == 1

        writer.clear()

        assert writer.count_events() == 0
        assert not temp_telemetry_file.exists()

    def test_creates_parent_directories(self, temp_telemetry_file: Path):
        """Test that parent directories are created."""
        nested_path = temp_telemetry_file.parent / "deep" / "nested" / "telemetry.jsonl"
        writer = TelemetryWriter(nested_path)
        event = TelemetryEvent.create(RoleEvent.ROLE_SELECTED)

        writer.write_event(event)

        assert nested_path.exists()


class TestTrackRoleEvent:
    """Tests for the track_role_event function."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset writer before each test."""
        reset_writer()
        # Ensure telemetry is enabled for tests
        os.environ.pop("FLOWSPEC_TELEMETRY_DISABLED", None)
        yield
        reset_writer()

    def test_track_role_event_basic(self, tmp_path: Path):
        """Test basic event tracking."""
        telemetry_path = tmp_path / ".flowspec" / "telemetry.jsonl"

        event = track_role_event(
            RoleEvent.ROLE_SELECTED,
            role="dev",
            project_root=tmp_path,
        )

        assert event is not None
        assert event.role == "dev"
        assert telemetry_path.exists()

    def test_track_role_event_with_context(self, tmp_path: Path):
        """Test tracking event with context."""
        event = track_role_event(
            RoleEvent.AGENT_INVOKED,
            role="qa",
            agent="qa-engineer",
            context={"task_id": "task-123"},
            project_root=tmp_path,
        )

        assert event is not None
        assert event.agent == "qa-engineer"
        # Context should be preserved (task_id doesn't contain PII)
        assert event.context["task_id"] == "task-123"

    def test_track_role_event_sanitizes_pii(self, tmp_path: Path):
        """Test that PII is sanitized in tracked events."""
        event = track_role_event(
            RoleEvent.COMMAND_EXECUTED,
            command="/flow:implement",
            context={"assignee": "@johndoe"},
            project_root=tmp_path,
        )

        assert event is not None
        # Username should be hashed
        assert "@johndoe" not in str(event.context)

    def test_track_role_event_disabled(self, tmp_path: Path):
        """Test that tracking returns None when disabled."""
        event = track_role_event(
            RoleEvent.ROLE_SELECTED,
            role="dev",
            enabled=False,
            project_root=tmp_path,
        )

        assert event is None

    def test_track_role_event_env_disabled(self, tmp_path: Path):
        """Test that tracking respects FLOWSPEC_TELEMETRY_DISABLED."""
        os.environ["FLOWSPEC_TELEMETRY_DISABLED"] = "1"

        event = track_role_event(
            RoleEvent.ROLE_SELECTED,
            role="dev",
            project_root=tmp_path,
        )

        assert event is None

        # Cleanup
        os.environ.pop("FLOWSPEC_TELEMETRY_DISABLED")

    def test_track_role_event_string_event_type(self, tmp_path: Path):
        """Test tracking with string event type."""
        event = track_role_event(
            "role.selected",
            role="pm",
            project_root=tmp_path,
        )

        assert event is not None
        assert event.event_type == RoleEvent.ROLE_SELECTED
