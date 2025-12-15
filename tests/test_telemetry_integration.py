"""Integration tests for telemetry event tracking."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from specify_cli.telemetry import (
    enable_telemetry,
    is_telemetry_enabled,
    reset_writer,
    track_agent_invocation,
    track_agent_invocation_decorator,
    track_command_execution,
    track_handoff,
    track_role_change,
    track_role_selection,
    track_workflow,
)


class TestTelemetryConsent:
    """Tests for telemetry consent checking."""

    def test_telemetry_disabled_by_default(self, tmp_path: Path):
        """Test that telemetry is disabled by default (opt-in required)."""
        os.environ.pop("FLOWSPEC_TELEMETRY_DISABLED", None)
        assert is_telemetry_enabled(tmp_path) is False

    def test_telemetry_enabled_via_config(self, tmp_path: Path):
        """Test that telemetry can be enabled via config."""
        os.environ.pop("FLOWSPEC_TELEMETRY_DISABLED", None)
        enable_telemetry(tmp_path)
        assert is_telemetry_enabled(tmp_path) is True

    def test_telemetry_disabled_with_1(self, tmp_path: Path):
        """Test that telemetry is disabled with '1' env var."""
        enable_telemetry(tmp_path)  # Enable first
        os.environ["FLOWSPEC_TELEMETRY_DISABLED"] = "1"
        try:
            assert is_telemetry_enabled(tmp_path) is False
        finally:
            os.environ.pop("FLOWSPEC_TELEMETRY_DISABLED", None)

    def test_telemetry_disabled_with_true(self, tmp_path: Path):
        """Test that telemetry is disabled with 'true' env var."""
        enable_telemetry(tmp_path)
        os.environ["FLOWSPEC_TELEMETRY_DISABLED"] = "true"
        try:
            assert is_telemetry_enabled(tmp_path) is False
        finally:
            os.environ.pop("FLOWSPEC_TELEMETRY_DISABLED", None)

    def test_telemetry_disabled_with_yes(self, tmp_path: Path):
        """Test that telemetry is disabled with 'yes' env var."""
        enable_telemetry(tmp_path)
        os.environ["FLOWSPEC_TELEMETRY_DISABLED"] = "yes"
        try:
            assert is_telemetry_enabled(tmp_path) is False
        finally:
            os.environ.pop("FLOWSPEC_TELEMETRY_DISABLED", None)


class TestRoleSelectionTracking:
    """Tests for role selection event tracking."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: Path):
        """Setup for each test."""
        reset_writer()
        os.environ.pop("FLOWSPEC_TELEMETRY_DISABLED", None)
        enable_telemetry(tmp_path)  # Enable telemetry for tests
        self.telemetry_path = tmp_path / ".flowspec" / "telemetry.jsonl"
        yield
        reset_writer()

    def test_track_role_selection(self, tmp_path: Path):
        """Test tracking role selection."""
        track_role_selection(
            role="dev",
            command="specify init",
            project_root=tmp_path,
        )

        # Read and verify event
        events = self._read_events(tmp_path)
        assert len(events) == 1
        assert events[0]["event_type"] == "role.selected"
        assert events[0]["role"] == "dev"
        assert events[0]["command"] == "specify init"

    def test_track_role_change(self, tmp_path: Path):
        """Test tracking role change."""
        track_role_change(
            new_role="qa",
            old_role="dev",
            command="specify configure",
            project_root=tmp_path,
        )

        events = self._read_events(tmp_path)
        assert len(events) == 1
        assert events[0]["event_type"] == "role.changed"
        assert events[0]["role"] == "qa"
        assert events[0]["context"]["previous_role"] == "dev"

    def test_no_tracking_when_disabled(self, tmp_path: Path):
        """Test that no events are tracked when telemetry is disabled."""
        os.environ["FLOWSPEC_TELEMETRY_DISABLED"] = "1"

        track_role_selection(role="dev", project_root=tmp_path)

        # Verify no events written
        telemetry_path = tmp_path / ".flowspec" / "telemetry.jsonl"
        assert not telemetry_path.exists()

        os.environ.pop("FLOWSPEC_TELEMETRY_DISABLED", None)

    def _read_events(self, project_root: Path) -> list[dict]:
        """Read events from telemetry file."""
        telemetry_path = project_root / ".flowspec" / "telemetry.jsonl"
        if not telemetry_path.exists():
            return []
        return [
            json.loads(line)
            for line in telemetry_path.read_text().strip().split("\n")
            if line
        ]


class TestAgentInvocationTracking:
    """Tests for agent invocation event tracking."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: Path):
        """Setup for each test."""
        reset_writer()
        os.environ.pop("FLOWSPEC_TELEMETRY_DISABLED", None)
        enable_telemetry(tmp_path)  # Enable telemetry for tests
        yield
        reset_writer()

    def test_track_agent_invocation_success(self, tmp_path: Path):
        """Test tracking successful agent invocation."""
        with track_agent_invocation(
            agent="backend-engineer",
            role="dev",
            command="/flow:implement",
            project_root=tmp_path,
        ):
            pass  # Agent work happens here

        events = self._read_events(tmp_path)
        assert len(events) == 2
        assert events[0]["event_type"] == "agent.started"
        assert events[0]["agent"] == "backend-engineer"
        assert events[1]["event_type"] == "agent.completed"
        assert events[1]["agent"] == "backend-engineer"

    def test_track_agent_invocation_failure(self, tmp_path: Path):
        """Test tracking failed agent invocation."""
        with pytest.raises(ValueError):
            with track_agent_invocation(
                agent="qa-engineer",
                role="qa",
                project_root=tmp_path,
            ):
                raise ValueError("Agent failed")

        # The code below IS reachable: pytest.raises is a context manager that
        # catches the expected exception and suppresses it, allowing the test
        # to continue and verify the events that were recorded before/during the failure.
        events = self._read_events(tmp_path)
        assert len(events) == 2
        assert events[0]["event_type"] == "agent.started"
        assert events[1]["event_type"] == "agent.failed"
        assert events[1]["agent"] == "qa-engineer"

    def test_track_agent_invocation_decorator(self, tmp_path: Path, monkeypatch):
        """Test tracking agent invocation with decorator."""
        # Change cwd to tmp_path since decorator uses cwd() for project_root
        monkeypatch.chdir(tmp_path)
        enable_telemetry(tmp_path)  # Re-enable after chdir

        @track_agent_invocation_decorator(
            agent="frontend-engineer", role="dev", command="/flow:implement"
        )
        def implement_ui():
            return "done"

        # Actually call the decorated function to test the decorator
        result = implement_ui()

        assert result == "done"
        events = self._read_events(tmp_path)
        assert len(events) == 2
        assert events[0]["event_type"] == "agent.started"
        assert events[0]["agent"] == "frontend-engineer"
        assert events[1]["event_type"] == "agent.completed"
        assert events[1]["agent"] == "frontend-engineer"

    def _read_events(self, project_root: Path) -> list[dict]:
        """Read events from telemetry file."""
        telemetry_path = project_root / ".flowspec" / "telemetry.jsonl"
        if not telemetry_path.exists():
            return []
        return [
            json.loads(line)
            for line in telemetry_path.read_text().strip().split("\n")
            if line
        ]


class TestHandoffTracking:
    """Tests for handoff click event tracking."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: Path):
        """Setup for each test."""
        reset_writer()
        os.environ.pop("FLOWSPEC_TELEMETRY_DISABLED", None)
        enable_telemetry(tmp_path)  # Enable telemetry for tests
        yield
        reset_writer()

    def test_track_handoff(self, tmp_path: Path):
        """Test tracking handoff click."""
        track_handoff(
            from_agent="backend-engineer",
            to_agent="qa-engineer",
            role="dev",
            project_root=tmp_path,
        )

        events = self._read_events(tmp_path)
        assert len(events) == 1
        assert events[0]["event_type"] == "handoff.clicked"
        assert events[0]["agent"] == "qa-engineer"
        assert events[0]["context"]["from_agent"] == "backend-engineer"
        assert events[0]["context"]["to_agent"] == "qa-engineer"

    def _read_events(self, project_root: Path) -> list[dict]:
        """Read events from telemetry file."""
        telemetry_path = project_root / ".flowspec" / "telemetry.jsonl"
        if not telemetry_path.exists():
            return []
        return [
            json.loads(line)
            for line in telemetry_path.read_text().strip().split("\n")
            if line
        ]


class TestCommandTracking:
    """Tests for command execution tracking."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: Path):
        """Setup for each test."""
        reset_writer()
        os.environ.pop("FLOWSPEC_TELEMETRY_DISABLED", None)
        enable_telemetry(tmp_path)  # Enable telemetry for tests
        yield
        reset_writer()

    def test_track_command_execution(self, tmp_path: Path):
        """Test tracking command execution."""
        track_command_execution(
            command="/flow:implement",
            role="dev",
            context={"task_id": "task-123"},
            project_root=tmp_path,
        )

        events = self._read_events(tmp_path)
        assert len(events) == 1
        assert events[0]["event_type"] == "command.executed"
        assert events[0]["command"] == "/flow:implement"
        assert events[0]["role"] == "dev"
        assert events[0]["context"]["task_id"] == "task-123"

    def _read_events(self, project_root: Path) -> list[dict]:
        """Read events from telemetry file."""
        telemetry_path = project_root / ".flowspec" / "telemetry.jsonl"
        if not telemetry_path.exists():
            return []
        return [
            json.loads(line)
            for line in telemetry_path.read_text().strip().split("\n")
            if line
        ]


class TestWorkflowTracking:
    """Tests for workflow lifecycle tracking."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: Path):
        """Setup for each test."""
        reset_writer()
        os.environ.pop("FLOWSPEC_TELEMETRY_DISABLED", None)
        enable_telemetry(tmp_path)  # Enable telemetry for tests
        yield
        reset_writer()

    def test_track_workflow_success(self, tmp_path: Path):
        """Test tracking successful workflow."""
        with track_workflow(
            workflow_name="implement",
            role="dev",
            command="/flow:implement",
            project_root=tmp_path,
        ):
            pass  # Workflow work here

        events = self._read_events(tmp_path)
        assert len(events) == 2
        assert events[0]["event_type"] == "workflow.started"
        assert events[0]["context"]["workflow"] == "implement"
        assert events[1]["event_type"] == "workflow.completed"

    def test_track_workflow_failure(self, tmp_path: Path):
        """Test tracking failed workflow."""
        with pytest.raises(RuntimeError):
            with track_workflow(
                workflow_name="validate",
                role="qa",
                project_root=tmp_path,
            ):
                raise RuntimeError("Validation failed")

        # The code below IS reachable: pytest.raises is a context manager that
        # catches the expected exception and suppresses it, allowing the test
        # to continue and verify the events that were recorded before/during the failure.
        events = self._read_events(tmp_path)
        assert len(events) == 2
        assert events[0]["event_type"] == "workflow.started"
        assert events[1]["event_type"] == "workflow.failed"

    def _read_events(self, project_root: Path) -> list[dict]:
        """Read events from telemetry file."""
        telemetry_path = project_root / ".flowspec" / "telemetry.jsonl"
        if not telemetry_path.exists():
            return []
        return [
            json.loads(line)
            for line in telemetry_path.read_text().strip().split("\n")
            if line
        ]


class TestEndToEndIntegration:
    """End-to-end integration tests for telemetry."""

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path: Path):
        """Setup for each test."""
        reset_writer()
        os.environ.pop("FLOWSPEC_TELEMETRY_DISABLED", None)
        enable_telemetry(tmp_path)  # Enable telemetry for tests
        yield
        reset_writer()

    def test_full_workflow_telemetry(self, tmp_path: Path):
        """Test tracking a full workflow with multiple events."""
        # User selects role
        track_role_selection(role="dev", command="specify init", project_root=tmp_path)

        # User executes command
        track_command_execution(
            command="/flow:implement",
            role="dev",
            project_root=tmp_path,
        )

        # Workflow starts
        with track_workflow(
            workflow_name="implement",
            role="dev",
            command="/flow:implement",
            project_root=tmp_path,
        ):
            # Agent is invoked
            with track_agent_invocation(
                agent="backend-engineer",
                role="dev",
                command="/flow:implement",
                project_root=tmp_path,
            ):
                pass  # Agent work

            # Handoff to QA
            track_handoff(
                from_agent="backend-engineer",
                to_agent="qa-engineer",
                role="dev",
                project_root=tmp_path,
            )

        # Verify all events were tracked
        events = self._read_events(tmp_path)
        event_types = [e["event_type"] for e in events]

        assert "role.selected" in event_types
        assert "command.executed" in event_types
        assert "workflow.started" in event_types
        assert "agent.started" in event_types
        assert "agent.completed" in event_types
        assert "handoff.clicked" in event_types
        assert "workflow.completed" in event_types

        # Should have 7 events total
        assert len(events) == 7

    def _read_events(self, project_root: Path) -> list[dict]:
        """Read events from telemetry file."""
        telemetry_path = project_root / ".flowspec" / "telemetry.jsonl"
        if not telemetry_path.exists():
            return []
        return [
            json.loads(line)
            for line in telemetry_path.read_text().strip().split("\n")
            if line
        ]
