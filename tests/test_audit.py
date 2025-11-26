"""Unit tests for the AuditLogger and related classes."""

import json
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest

from specify_cli.satellite.audit import (
    AuditEvent,
    AuditEventType,
    AuditLogger,
    AuditQuery,
    AuditSeverity,
    JSONFormatter,
    MarkdownFormatter,
    SLSAAttestation,
)


class TestAuditEvent:
    """Tests for AuditEvent dataclass."""

    def test_create_basic_event(self):
        """Should create event with required fields."""
        event = AuditEvent(event_type=AuditEventType.SYNC_START)
        assert event.event_type == AuditEventType.SYNC_START
        assert event.severity == AuditSeverity.INFO
        assert event.timestamp is not None

    def test_create_full_event(self):
        """Should create event with all fields."""
        ts = datetime.now(timezone.utc)
        event = AuditEvent(
            event_type=AuditEventType.TASK_PUSHED,
            timestamp=ts,
            severity=AuditSeverity.INFO,
            provider="github",
            operation="push",
            task_id="task-42",
            remote_id="123",
            user="agent",
            status="success",
            details={"key": "value"},
            correlation_id="corr-123",
            duration_ms=500,
        )
        assert event.provider == "github"
        assert event.task_id == "task-42"
        assert event.duration_ms == 500

    def test_to_dict(self):
        """Should convert event to dictionary."""
        event = AuditEvent(
            event_type=AuditEventType.AUTH_SUCCESS,
            provider="jira",
            status="success",
        )
        d = event.to_dict()
        assert d["event_type"] == "auth_success"
        assert d["provider"] == "jira"
        assert d["status"] == "success"
        assert "timestamp" in d

    def test_to_json(self):
        """Should serialize event to JSON."""
        event = AuditEvent(
            event_type=AuditEventType.ERROR,
            severity=AuditSeverity.ERROR,
            details={"message": "test error"},
        )
        json_str = event.to_json()
        parsed = json.loads(json_str)
        assert parsed["event_type"] == "error"
        assert parsed["severity"] == "error"
        assert parsed["details"]["message"] == "test error"

    def test_from_dict(self):
        """Should create event from dictionary."""
        data = {
            "event_type": "sync_complete",
            "timestamp": "2024-01-15T10:30:00+00:00",
            "severity": "info",
            "provider": "github",
            "status": "success",
        }
        event = AuditEvent.from_dict(data)
        assert event.event_type == AuditEventType.SYNC_COMPLETE
        assert event.provider == "github"
        assert event.severity == AuditSeverity.INFO

    def test_optional_fields_omitted_in_dict(self):
        """Optional fields should be omitted when None."""
        event = AuditEvent(event_type=AuditEventType.SYNC_START)
        d = event.to_dict()
        assert "provider" not in d
        assert "task_id" not in d
        assert "duration_ms" not in d


class TestAuditEventType:
    """Tests for AuditEventType enum."""

    def test_all_event_types_have_values(self):
        """All event types should have string values."""
        for event_type in AuditEventType:
            assert isinstance(event_type.value, str)
            assert len(event_type.value) > 0

    def test_sync_events_exist(self):
        """Sync-related events should be defined."""
        assert AuditEventType.SYNC_START.value == "sync_start"
        assert AuditEventType.SYNC_COMPLETE.value == "sync_complete"
        assert AuditEventType.SYNC_FAILED.value == "sync_failed"

    def test_auth_events_exist(self):
        """Auth-related events should be defined."""
        assert AuditEventType.AUTH_SUCCESS.value == "auth_success"
        assert AuditEventType.AUTH_FAILED.value == "auth_failed"


class TestJSONFormatter:
    """Tests for JSONFormatter."""

    def test_format_event_compact(self):
        """Should format event as compact JSON."""
        formatter = JSONFormatter(pretty=False)
        event = AuditEvent(
            event_type=AuditEventType.TASK_CREATED,
            provider="notion",
        )
        result = formatter.format(event)
        assert "\n" not in result
        parsed = json.loads(result)
        assert parsed["event_type"] == "task_created"

    def test_format_event_pretty(self):
        """Should format event as pretty JSON."""
        formatter = JSONFormatter(pretty=True)
        event = AuditEvent(
            event_type=AuditEventType.TASK_CREATED,
            provider="notion",
        )
        result = formatter.format(event)
        assert "\n" in result
        parsed = json.loads(result)
        assert parsed["event_type"] == "task_created"


class TestMarkdownFormatter:
    """Tests for MarkdownFormatter."""

    def test_format_event_basic(self):
        """Should format event as markdown."""
        formatter = MarkdownFormatter()
        event = AuditEvent(
            event_type=AuditEventType.SYNC_COMPLETE,
            provider="github",
            status="success",
        )
        result = formatter.format(event)
        assert "**sync_complete**" in result
        assert "github" in result
        assert "success" in result

    def test_format_includes_time(self):
        """Formatted output should include timestamp."""
        formatter = MarkdownFormatter()
        event = AuditEvent(event_type=AuditEventType.ERROR)
        result = formatter.format(event)
        assert "Time:" in result

    def test_format_includes_duration(self):
        """Formatted output should include duration when present."""
        formatter = MarkdownFormatter()
        event = AuditEvent(
            event_type=AuditEventType.SYNC_COMPLETE,
            duration_ms=1500,
        )
        result = formatter.format(event)
        assert "1500ms" in result


class TestAuditQuery:
    """Tests for AuditQuery builder."""

    def test_empty_query_matches_all(self):
        """Empty query should match all events."""
        query = AuditQuery()
        event = AuditEvent(event_type=AuditEventType.SYNC_START)
        assert query.matches(event)

    def test_filter_by_event_type(self):
        """Should filter by event type."""
        query = AuditQuery().event_type(AuditEventType.SYNC_START)

        event1 = AuditEvent(event_type=AuditEventType.SYNC_START)
        event2 = AuditEvent(event_type=AuditEventType.SYNC_COMPLETE)

        assert query.matches(event1)
        assert not query.matches(event2)

    def test_filter_by_multiple_event_types(self):
        """Should filter by multiple event types."""
        query = AuditQuery().event_type(
            AuditEventType.SYNC_START,
            AuditEventType.SYNC_COMPLETE,
        )

        event1 = AuditEvent(event_type=AuditEventType.SYNC_START)
        event2 = AuditEvent(event_type=AuditEventType.SYNC_COMPLETE)
        event3 = AuditEvent(event_type=AuditEventType.ERROR)

        assert query.matches(event1)
        assert query.matches(event2)
        assert not query.matches(event3)

    def test_filter_by_severity(self):
        """Should filter by severity."""
        query = AuditQuery().severity(AuditSeverity.ERROR)

        event1 = AuditEvent(
            event_type=AuditEventType.ERROR,
            severity=AuditSeverity.ERROR,
        )
        event2 = AuditEvent(
            event_type=AuditEventType.SYNC_START,
            severity=AuditSeverity.INFO,
        )

        assert query.matches(event1)
        assert not query.matches(event2)

    def test_filter_by_provider(self):
        """Should filter by provider."""
        query = AuditQuery().provider("github")

        event1 = AuditEvent(
            event_type=AuditEventType.SYNC_START,
            provider="github",
        )
        event2 = AuditEvent(
            event_type=AuditEventType.SYNC_START,
            provider="jira",
        )

        assert query.matches(event1)
        assert not query.matches(event2)

    def test_filter_by_task_id(self):
        """Should filter by task ID."""
        query = AuditQuery().task_id("task-42")

        event1 = AuditEvent(
            event_type=AuditEventType.TASK_PUSHED,
            task_id="task-42",
        )
        event2 = AuditEvent(
            event_type=AuditEventType.TASK_PUSHED,
            task_id="task-99",
        )

        assert query.matches(event1)
        assert not query.matches(event2)

    def test_filter_by_date_range(self):
        """Should filter by date range."""
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        query = AuditQuery().since(yesterday).until(tomorrow)

        event = AuditEvent(
            event_type=AuditEventType.SYNC_START,
            timestamp=now,
        )

        assert query.matches(event)

    def test_combined_filters(self):
        """Should combine multiple filters."""
        query = (
            AuditQuery()
            .event_type(AuditEventType.SYNC_COMPLETE)
            .provider("github")
            .status("success")
        )

        event1 = AuditEvent(
            event_type=AuditEventType.SYNC_COMPLETE,
            provider="github",
            status="success",
        )
        event2 = AuditEvent(
            event_type=AuditEventType.SYNC_COMPLETE,
            provider="github",
            status="failed",
        )

        assert query.matches(event1)
        assert not query.matches(event2)


class TestSLSAAttestation:
    """Tests for SLSAAttestation."""

    def test_create_attestation(self):
        """Should create attestation with required fields."""
        attestation = SLSAAttestation(
            subject=[{"name": "task-42", "digest": {"sha256": "abc123"}}],
        )
        assert len(attestation.subject) == 1
        assert attestation.builder_id == "backlog-satellite"

    def test_to_dict_format(self):
        """Should convert to SLSA v1 format."""
        attestation = SLSAAttestation(
            subject=[{"name": "sync-op", "digest": {"sha256": "xyz"}}],
            build_type="sync",
        )
        d = attestation.to_dict()
        assert d["_type"] == "https://in-toto.io/Statement/v1"
        assert "predicateType" in d
        assert "predicate" in d
        assert "buildDefinition" in d["predicate"]

    def test_to_json(self):
        """Should serialize to JSON."""
        attestation = SLSAAttestation(
            subject=[{"name": "test", "digest": {"sha256": "123"}}],
        )
        json_str = attestation.to_json()
        parsed = json.loads(json_str)
        assert parsed["_type"] == "https://in-toto.io/Statement/v1"


class TestAuditLogger:
    """Tests for AuditLogger."""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary directory for logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_create_logger(self, temp_log_dir):
        """Should create logger with default settings."""
        logger = AuditLogger(log_dir=temp_log_dir)
        assert logger.log_dir == temp_log_dir
        assert logger.max_bytes == AuditLogger.DEFAULT_MAX_BYTES

    def test_log_creates_files(self, temp_log_dir):
        """Should create log files on first log."""
        logger = AuditLogger(log_dir=temp_log_dir)
        logger.log(AuditEvent(event_type=AuditEventType.SYNC_START))

        assert logger.json_file.exists()
        assert logger.markdown_file.exists()

    def test_log_writes_json(self, temp_log_dir):
        """Should write JSON line to log file."""
        logger = AuditLogger(log_dir=temp_log_dir)
        logger.log(AuditEvent(
            event_type=AuditEventType.SYNC_COMPLETE,
            provider="github",
        ))

        content = logger.json_file.read_text()
        parsed = json.loads(content.strip())
        assert parsed["event_type"] == "sync_complete"
        assert parsed["provider"] == "github"

    def test_log_writes_markdown(self, temp_log_dir):
        """Should write markdown to log file."""
        logger = AuditLogger(log_dir=temp_log_dir)
        logger.log(AuditEvent(
            event_type=AuditEventType.SYNC_COMPLETE,
            provider="github",
        ))

        content = logger.markdown_file.read_text()
        assert "sync_complete" in content
        assert "github" in content

    def test_log_sync_success(self, temp_log_dir):
        """Should log sync operations."""
        logger = AuditLogger(log_dir=temp_log_dir)
        logger.log_sync(
            operation="push",
            provider="github",
            task_id="task-42",
            status="success",
            duration_ms=100,
        )

        content = logger.json_file.read_text()
        parsed = json.loads(content.strip())
        assert parsed["event_type"] == "sync_complete"
        assert parsed["operation"] == "push"

    def test_log_sync_failure(self, temp_log_dir):
        """Should log failed sync operations."""
        logger = AuditLogger(log_dir=temp_log_dir)
        logger.log_sync(
            operation="pull",
            provider="jira",
            status="failed",
        )

        content = logger.json_file.read_text()
        parsed = json.loads(content.strip())
        assert parsed["event_type"] == "sync_failed"
        assert parsed["severity"] == "error"

    def test_log_auth(self, temp_log_dir):
        """Should log authentication events."""
        logger = AuditLogger(log_dir=temp_log_dir)
        logger.log_auth(provider="notion", success=True, user="test-user")

        content = logger.json_file.read_text()
        parsed = json.loads(content.strip())
        assert parsed["event_type"] == "auth_success"
        assert parsed["user"] == "test-user"

    def test_log_auth_failure(self, temp_log_dir):
        """Should log authentication failures."""
        logger = AuditLogger(log_dir=temp_log_dir)
        logger.log_auth(provider="github", success=False)

        content = logger.json_file.read_text()
        parsed = json.loads(content.strip())
        assert parsed["event_type"] == "auth_failed"
        assert parsed["severity"] == "warning"

    def test_log_conflict(self, temp_log_dir):
        """Should log conflict events."""
        logger = AuditLogger(log_dir=temp_log_dir)
        logger.log_conflict(
            provider="github",
            task_id="task-42",
            resolution="local",
        )

        content = logger.json_file.read_text()
        parsed = json.loads(content.strip())
        assert parsed["event_type"] == "conflict_resolved"

    def test_log_error(self, temp_log_dir):
        """Should log errors with exception details."""
        logger = AuditLogger(log_dir=temp_log_dir)
        try:
            raise ValueError("test error")
        except ValueError as e:
            logger.log_error("Something went wrong", exception=e)

        content = logger.json_file.read_text()
        parsed = json.loads(content.strip())
        assert parsed["event_type"] == "error"
        assert parsed["details"]["exception_type"] == "ValueError"
        assert "test error" in parsed["details"]["exception_message"]

    def test_query_events(self, temp_log_dir):
        """Should query logged events."""
        logger = AuditLogger(log_dir=temp_log_dir)

        # Log some events
        logger.log_sync(operation="push", provider="github", status="success")
        logger.log_sync(operation="pull", provider="jira", status="success")
        logger.log_sync(operation="push", provider="github", status="failed")

        # Query github events
        query = AuditQuery().provider("github")
        results = list(logger.query(query))

        assert len(results) == 2
        assert all(e.provider == "github" for e in results)

    def test_query_with_limit(self, temp_log_dir):
        """Should respect query limit."""
        logger = AuditLogger(log_dir=temp_log_dir)

        for i in range(10):
            logger.log_sync(operation="push", provider="github", status="success")

        query = AuditQuery().limit(3)
        results = list(logger.query(query))

        assert len(results) == 3

    def test_get_stats(self, temp_log_dir):
        """Should calculate statistics."""
        logger = AuditLogger(log_dir=temp_log_dir)

        logger.log_sync(operation="push", provider="github", status="success")
        logger.log_sync(operation="pull", provider="jira", status="success")
        logger.log_error("Test error")
        logger.log_conflict(provider="github", task_id="task-1")

        stats = logger.get_stats()

        assert stats["total_events"] == 4
        assert stats["sync_operations"] == 2
        assert stats["errors"] == 1
        assert stats["conflicts"] == 1
        assert "github" in stats["by_provider"]

    def test_generate_report(self, temp_log_dir):
        """Should generate markdown report."""
        logger = AuditLogger(log_dir=temp_log_dir)

        logger.log_sync(operation="push", provider="github", status="success")
        logger.log_sync(operation="pull", provider="jira", status="success")

        report = logger.generate_report()

        assert "# Audit Report" in report
        assert "Total Events" in report
        assert "github" in report
        assert "jira" in report

    def test_create_attestation(self, temp_log_dir):
        """Should create SLSA attestation."""
        logger = AuditLogger(log_dir=temp_log_dir)

        attestation = logger.create_attestation(
            operation="sync",
            subjects=[{"name": "task-42", "digest": {"sha256": "abc"}}],
        )

        assert attestation.build_type == "sync"
        assert len(attestation.subject) == 1

    def test_export_attestation(self, temp_log_dir):
        """Should export attestation to file."""
        logger = AuditLogger(log_dir=temp_log_dir)

        attestation = logger.create_attestation(
            operation="sync",
            subjects=[{"name": "task-42", "digest": {"sha256": "abc"}}],
        )

        output_path = logger.export_attestation(attestation)

        assert output_path.exists()
        content = json.loads(output_path.read_text())
        assert content["_type"] == "https://in-toto.io/Statement/v1"

    def test_clear_logs(self, temp_log_dir):
        """Should clear all log files."""
        logger = AuditLogger(log_dir=temp_log_dir)

        # Create some logs
        logger.log_sync(operation="push", provider="github", status="success")
        assert logger.json_file.exists()

        # Clear
        logger.clear()

        assert not logger.json_file.exists()
        assert not logger.markdown_file.exists()


class TestAuditLoggerRotation:
    """Tests for log rotation functionality."""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary directory for logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_rotation_settings(self, temp_log_dir):
        """Should accept custom rotation settings."""
        logger = AuditLogger(
            log_dir=temp_log_dir,
            max_bytes=1024,
            backup_count=3,
        )
        assert logger.max_bytes == 1024
        assert logger.backup_count == 3
