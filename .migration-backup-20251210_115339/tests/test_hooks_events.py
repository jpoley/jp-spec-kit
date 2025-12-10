"""Tests for hook event model schema.

Tests event creation, serialization, factory functions, and event matching.
"""

import json


from specify_cli.hooks.events import (
    Artifact,
    Event,
    EventType,
    create_agent_completed_event,
    create_agent_handoff_event,
    create_agent_progress_event,
    create_agent_started_event,
    create_implement_completed_event,
    create_spec_created_event,
    create_task_completed_event,
)


class TestArtifact:
    """Test Artifact dataclass."""

    def test_artifact_creation(self):
        """Test creating an artifact."""
        artifact = Artifact(
            type="source_code",
            path="./src/auth/",
            files_changed=12,
        )
        assert artifact.type == "source_code"
        assert artifact.path == "./src/auth/"
        assert artifact.files_changed == 12

    def test_artifact_to_dict(self):
        """Test artifact serialization to dict."""
        artifact = Artifact(type="report", path="./report.html")
        result = artifact.to_dict()
        assert result["type"] == "report"
        assert result["path"] == "./report.html"
        assert "files_changed" not in result  # None fields excluded

    def test_artifact_from_dict(self):
        """Test artifact deserialization from dict."""
        data = {"type": "prd", "path": "./docs/spec.md", "files_changed": 1}
        artifact = Artifact.from_dict(data)
        assert artifact.type == "prd"
        assert artifact.path == "./docs/spec.md"
        assert artifact.files_changed == 1


class TestEvent:
    """Test Event dataclass."""

    def test_event_creation_minimal(self):
        """Test creating event with minimal required fields."""
        event = Event(
            event_type="spec.created",
            project_root="/tmp/project",
        )
        assert event.event_type == "spec.created"
        assert event.project_root == "/tmp/project"
        assert event.event_id.startswith("evt_")
        assert event.schema_version == "1.0"
        assert event.timestamp.endswith("Z")  # UTC timestamp

    def test_event_creation_full(self):
        """Test creating event with all fields."""
        artifact = Artifact(type="prd", path="./docs/spec.md")
        event = Event(
            event_type="spec.created",
            project_root="/tmp/project",
            feature="user-auth",
            context={"agent": "pm-planner"},
            artifacts=[artifact],
            metadata={"cli_version": "0.0.179"},
        )
        assert event.feature == "user-auth"
        assert event.context == {"agent": "pm-planner"}
        assert len(event.artifacts) == 1
        assert event.metadata == {"cli_version": "0.0.179"}

    def test_event_to_dict(self):
        """Test event serialization to dict."""
        event = Event(
            event_type="task.completed",
            project_root="/tmp/project",
            context={"task_id": "task-189"},
        )
        result = event.to_dict()
        assert result["event_type"] == "task.completed"
        assert result["project_root"] == "/tmp/project"
        assert result["context"] == {"task_id": "task-189"}
        assert "feature" not in result  # None fields excluded

    def test_event_to_json(self):
        """Test event serialization to JSON."""
        event = Event(
            event_type="spec.created",
            project_root="/tmp/project",
        )
        json_str = event.to_json()
        data = json.loads(json_str)
        assert data["event_type"] == "spec.created"
        assert data["project_root"] == "/tmp/project"

    def test_event_from_dict(self):
        """Test event deserialization from dict."""
        data = {
            "event_type": "plan.created",
            "project_root": "/tmp/project",
            "feature": "auth",
        }
        event = Event.from_dict(data)
        assert event.event_type == "plan.created"
        assert event.project_root == "/tmp/project"
        assert event.feature == "auth"

    def test_event_from_json(self):
        """Test event deserialization from JSON."""
        json_str = '{"event_type": "task.created", "project_root": "/tmp"}'
        event = Event.from_json(json_str)
        assert event.event_type == "task.created"
        assert event.project_root == "/tmp"

    def test_event_roundtrip(self):
        """Test event serialization and deserialization roundtrip."""
        original = Event(
            event_type="implement.completed",
            project_root="/tmp/project",
            feature="auth",
            context={"agent": "backend-engineer"},
        )
        json_str = original.to_json()
        restored = Event.from_json(json_str)

        assert restored.event_type == original.event_type
        assert restored.project_root == original.project_root
        assert restored.feature == original.feature
        assert restored.context == original.context


class TestEventType:
    """Test EventType enum."""

    def test_workflow_event_types(self):
        """Test workflow event types are defined."""
        assert EventType.SPEC_CREATED.value == "spec.created"
        assert EventType.SPEC_UPDATED.value == "spec.updated"
        assert EventType.PLAN_CREATED.value == "plan.created"
        assert EventType.IMPLEMENT_STARTED.value == "implement.started"
        assert EventType.IMPLEMENT_COMPLETED.value == "implement.completed"
        assert EventType.VALIDATE_COMPLETED.value == "validate.completed"

    def test_task_event_types(self):
        """Test task event types are defined."""
        assert EventType.TASK_CREATED.value == "task.created"
        assert EventType.TASK_UPDATED.value == "task.updated"
        assert EventType.TASK_COMPLETED.value == "task.completed"
        assert EventType.TASK_AC_CHECKED.value == "task.ac_checked"

    def test_agent_event_types(self):
        """Test agent event types for multi-machine observability."""
        assert EventType.AGENT_STARTED.value == "agent.started"
        assert EventType.AGENT_PROGRESS.value == "agent.progress"
        assert EventType.AGENT_BLOCKED.value == "agent.blocked"
        assert EventType.AGENT_COMPLETED.value == "agent.completed"
        assert EventType.AGENT_ERROR.value == "agent.error"
        assert EventType.AGENT_HANDOFF.value == "agent.handoff"


class TestEventFactories:
    """Test event factory functions."""

    def test_create_spec_created_event(self):
        """Test creating spec.created event."""
        event = create_spec_created_event(
            project_root="/tmp/project",
            feature="user-auth",
            spec_path="docs/prd/auth-spec.md",
        )
        assert event.event_type == "spec.created"
        assert event.feature == "user-auth"
        assert event.context["agent"] == "pm-planner"
        assert len(event.artifacts) == 1
        assert event.artifacts[0].type == "prd"

    def test_create_task_completed_event(self):
        """Test creating task.completed event."""
        event = create_task_completed_event(
            project_root="/tmp/project",
            task_id="task-189",
            task_title="Implement auth",
            priority="high",
            labels=["backend", "security"],
        )
        assert event.event_type == "task.completed"
        assert event.context["task_id"] == "task-189"
        assert event.context["priority"] == "high"
        assert event.context["labels"] == ["backend", "security"]

    def test_create_implement_completed_event(self):
        """Test creating implement.completed event."""
        event = create_implement_completed_event(
            project_root="/tmp/project",
            feature="auth",
            task_id="task-189",
            files_changed=15,
            source_path="./src/auth/",
        )
        assert event.event_type == "implement.completed"
        assert event.feature == "auth"
        assert event.context["task_id"] == "task-189"
        assert len(event.artifacts) == 1
        assert event.artifacts[0].files_changed == 15


class TestAgentEventFactories:
    """Test agent event factory functions for multi-machine observability."""

    def test_create_agent_progress_event(self):
        """Test creating agent.progress event with all fields."""
        event = create_agent_progress_event(
            project_root="/tmp/project",
            agent_id="claude-code@kinsale",
            task_id="task-229",
            feature="agent-hooks",
            progress_percent=60,
            status_message="Implementing event emission",
            machine="kinsale",
        )
        assert event.event_type == "agent.progress"
        assert event.feature == "agent-hooks"
        assert event.context["agent_id"] == "claude-code@kinsale"
        assert event.context["task_id"] == "task-229"
        assert event.context["progress_percent"] == 60
        assert event.context["status_message"] == "Implementing event emission"
        assert event.context["machine"] == "kinsale"

    def test_create_agent_progress_event_auto_detects_machine(self):
        """Test agent.progress event auto-detects machine hostname."""
        import socket

        event = create_agent_progress_event(
            project_root="/tmp/project",
            agent_id="claude-code@test",
            progress_percent=50,
        )
        assert event.context["machine"] == socket.gethostname()

    def test_create_agent_started_event(self):
        """Test creating agent.started event."""
        event = create_agent_started_event(
            project_root="/tmp/project",
            agent_id="claude-code@galway",
            task_id="task-198",
            feature="security-scanner",
        )
        assert event.event_type == "agent.started"
        assert event.feature == "security-scanner"
        assert event.context["agent_id"] == "claude-code@galway"
        assert event.context["task_id"] == "task-198"
        assert "machine" in event.context

    def test_create_agent_completed_event(self):
        """Test creating agent.completed event."""
        event = create_agent_completed_event(
            project_root="/tmp/project",
            agent_id="claude-code@muckross",
            task_id="task-100",
            feature="cleanup",
            status_message="All tasks completed successfully",
        )
        assert event.event_type == "agent.completed"
        assert event.context["agent_id"] == "claude-code@muckross"
        assert event.context["status_message"] == "All tasks completed successfully"

    def test_create_agent_handoff_event(self):
        """Test creating agent.handoff event for multi-machine coordination."""
        event = create_agent_handoff_event(
            project_root="/tmp/project",
            agent_id="claude-code@muckross",
            target_agent="claude-code@galway",
            target_machine="galway",
            task_id="task-198",
            feature="security-scanner",
            handoff_message="Planning complete, ready for implementation",
        )
        assert event.event_type == "agent.handoff"
        assert event.context["agent_id"] == "claude-code@muckross"
        assert event.context["target_agent"] == "claude-code@galway"
        assert event.context["target_machine"] == "galway"
        assert event.context["task_id"] == "task-198"
        assert (
            event.context["handoff_message"]
            == "Planning complete, ready for implementation"
        )

    def test_agent_events_have_event_id_and_timestamp(self):
        """Test all agent events get proper event_id and timestamp."""
        event = create_agent_progress_event(
            project_root="/tmp/project",
            agent_id="test-agent",
        )
        assert event.event_id.startswith("evt_")
        assert event.timestamp.endswith("Z")
        assert event.schema_version == "1.0"


class TestEventIdGeneration:
    """Test event ID generation."""

    def test_event_id_format(self):
        """Test event ID format is correct."""
        event = Event(event_type="test", project_root="/tmp")
        assert event.event_id.startswith("evt_")
        # ULID is 26 characters, so total is 30 (evt_ + 26)
        # Fallback is evt_ + 16 hex chars = 20
        assert len(event.event_id) >= 20

    def test_event_ids_unique(self):
        """Test event IDs are unique."""
        import time

        event1 = Event(event_type="test", project_root="/tmp")
        time.sleep(0.001)  # Ensure different timestamp
        event2 = Event(event_type="test", project_root="/tmp")
        assert event1.event_id != event2.event_id


class TestTimestampGeneration:
    """Test timestamp generation."""

    def test_timestamp_format(self):
        """Test timestamp is ISO 8601 UTC."""
        event = Event(event_type="test", project_root="/tmp")
        assert event.timestamp.endswith("Z")
        assert "T" in event.timestamp
        # Should be parseable as ISO format
        from datetime import datetime

        datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))
