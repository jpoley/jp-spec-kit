"""Tests for the Event Query API (task-504).

Tests cover:
- EventQuery fluent API
- Filtering by various criteria
- Aggregation functions (count_by, group_by, time_series)
- Export capabilities (JSON, CSV, markdown)
- Performance with large datasets
"""

from __future__ import annotations

import json
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest

from specify_cli.events.query import (
    EventQuery,
    QueryResult,
    _flatten_event,
    _get_csv_fieldnames,
    _get_nested_value,
    _parse_interval,
    count_events,
    get_events,
    query,
)


# --- Test fixtures ---


@pytest.fixture
def events_dir(tmp_path: Path) -> Path:
    """Create a temporary events directory with test data."""
    events_dir = tmp_path / ".speckit" / "events"
    events_dir.mkdir(parents=True)
    return events_dir


@pytest.fixture
def sample_events() -> list[dict[str, Any]]:
    """Create sample events for testing."""
    now = datetime.now(timezone.utc)
    return [
        {
            "event_type": "lifecycle.started",
            "timestamp": now.isoformat(),
            "agent_id": "@backend-engineer",
            "message": "Starting task",
            "context": {"task_id": "task-504"},
        },
        {
            "event_type": "lifecycle.completed",
            "timestamp": (now + timedelta(minutes=5)).isoformat(),
            "agent_id": "@backend-engineer",
            "message": "Completed task",
            "context": {"task_id": "task-504"},
        },
        {
            "event_type": "git.commit",
            "timestamp": (now + timedelta(minutes=10)).isoformat(),
            "agent_id": "@backend-engineer",
            "message": "Committed changes",
            "context": {"task_id": "task-504", "branch_name": "feature/events"},
        },
        {
            "event_type": "task.state_change",
            "timestamp": (now + timedelta(minutes=15)).isoformat(),
            "agent_id": "@pm-planner",
            "message": "Task moved to Done",
            "task": {"task_id": "task-504", "status": "Done"},
        },
        {
            "event_type": "activity.progress",
            "timestamp": (now + timedelta(minutes=20)).isoformat(),
            "agent_id": "@frontend-engineer",
            "message": "50% complete",
            "progress": 0.5,
            "context": {"task_id": "task-505"},
        },
    ]


@pytest.fixture
def populated_events_dir(events_dir: Path, sample_events: list[dict]) -> Path:
    """Create events directory with sample data."""
    today = datetime.now().strftime("%Y-%m-%d")
    file_path = events_dir / f"events-{today}.jsonl"

    with open(file_path, "w") as f:
        for event in sample_events:
            f.write(json.dumps(event) + "\n")

    return events_dir


# --- Helper function tests ---


class TestHelperFunctions:
    """Tests for query helper functions."""

    def test_parse_interval_seconds(self):
        """Test parsing second intervals."""
        assert _parse_interval("30s") == 30
        assert _parse_interval("60s") == 60

    def test_parse_interval_minutes(self):
        """Test parsing minute intervals."""
        assert _parse_interval("1m") == 60
        assert _parse_interval("5m") == 300
        assert _parse_interval("15m") == 900

    def test_parse_interval_hours(self):
        """Test parsing hour intervals."""
        assert _parse_interval("1h") == 3600
        assert _parse_interval("2h") == 7200

    def test_parse_interval_days(self):
        """Test parsing day intervals."""
        assert _parse_interval("1d") == 86400
        assert _parse_interval("7d") == 604800

    def test_parse_interval_invalid(self):
        """Test invalid interval defaults to 1 hour."""
        assert _parse_interval("invalid") == 3600
        assert _parse_interval("") == 3600

    def test_get_nested_value_simple(self):
        """Test getting simple values."""
        obj = {"key": "value"}
        assert _get_nested_value(obj, "key") == "value"

    def test_get_nested_value_nested(self):
        """Test getting nested values."""
        obj = {"level1": {"level2": {"level3": "value"}}}
        assert _get_nested_value(obj, "level1.level2.level3") == "value"
        assert _get_nested_value(obj, "level1.level2") == {"level3": "value"}

    def test_get_nested_value_missing(self):
        """Test getting missing values."""
        obj = {"key": "value"}
        assert _get_nested_value(obj, "missing") is None
        assert _get_nested_value(obj, "key.nested") is None

    def test_flatten_event_simple(self):
        """Test flattening simple event."""
        event = {"key": "value", "number": 123}
        flat = _flatten_event(event)
        assert flat["key"] == "value"
        assert flat["number"] == "123"

    def test_flatten_event_nested(self):
        """Test flattening nested event."""
        event = {"top": "value", "nested": {"inner": "deep"}}
        flat = _flatten_event(event)
        assert flat["top"] == "value"
        assert flat["nested.inner"] == "deep"

    def test_get_csv_fieldnames(self):
        """Test getting CSV fieldnames from events."""
        events = [
            {"timestamp": "2025-01-01", "event_type": "test", "custom": "value"},
            {"timestamp": "2025-01-02", "event_type": "test2", "other": "field"},
        ]
        fieldnames = _get_csv_fieldnames(events)

        # Priority fields should come first
        assert fieldnames[0] == "timestamp"
        assert fieldnames[1] == "event_type"
        assert "custom" in fieldnames
        assert "other" in fieldnames


# --- QueryResult tests ---


class TestQueryResult:
    """Tests for QueryResult class."""

    def test_to_json_empty(self):
        """Test JSON export with empty result."""
        result = QueryResult()
        json_str = result.to_json()
        data = json.loads(json_str)

        assert data["events"] == []
        assert data["count"] == 0
        assert data["aggregations"] == {}

    def test_to_json_with_events(self, sample_events: list[dict]):
        """Test JSON export with events."""
        result = QueryResult(events=sample_events, count=len(sample_events))
        json_str = result.to_json()
        data = json.loads(json_str)

        assert len(data["events"]) == 5
        assert data["count"] == 5

    def test_to_csv_empty(self):
        """Test CSV export with empty result."""
        result = QueryResult()
        csv_str = result.to_csv()
        assert csv_str == ""

    def test_to_csv_with_events(self, sample_events: list[dict]):
        """Test CSV export with events."""
        result = QueryResult(events=sample_events, count=len(sample_events))
        csv_str = result.to_csv()

        # Should have header and data rows
        lines = csv_str.strip().split("\n")
        assert len(lines) == 6  # Header + 5 events

        # Header should contain expected columns
        header = lines[0]
        assert "timestamp" in header
        assert "event_type" in header

    def test_to_markdown(self, sample_events: list[dict]):
        """Test markdown export."""
        result = QueryResult(events=sample_events, count=len(sample_events))
        md_str = result.to_markdown()

        assert "## Events" in md_str
        assert "| Timestamp | Type | Agent | Message |" in md_str
        assert "lifecycle.started" in md_str
        assert f"*Total: {len(sample_events)} events*" in md_str

    def test_to_markdown_with_aggregations(self):
        """Test markdown export with aggregations."""
        result = QueryResult(
            events=[],
            count=10,
            aggregations={"count_by": {"type_a": 6, "type_b": 4}},
        )
        md_str = result.to_markdown()

        assert "## Aggregations" in md_str
        assert "count_by" in md_str


# --- EventQuery tests ---


class TestEventQueryBasic:
    """Basic tests for EventQuery class."""

    def test_create_query(self, events_dir: Path):
        """Test creating a query."""
        q = EventQuery(events_dir=events_dir)
        assert q is not None

    def test_query_empty_dir(self, events_dir: Path):
        """Test querying empty directory."""
        q = EventQuery(events_dir=events_dir)
        result = q.execute()

        assert result.count == 0
        assert result.events == []

    def test_query_today(self, populated_events_dir: Path):
        """Test querying today's events."""
        q = EventQuery(events_dir=populated_events_dir).today()
        result = q.execute()

        assert result.count == 5

    def test_query_specific_date(self, events_dir: Path, sample_events: list[dict]):
        """Test querying specific date."""
        # Create file for specific date
        file_path = events_dir / "events-2025-12-01.jsonl"
        with open(file_path, "w") as f:
            for event in sample_events:
                f.write(json.dumps(event) + "\n")

        q = EventQuery(events_dir=events_dir).date("2025-12-01")
        result = q.execute()

        assert result.count == 5

    def test_query_date_range(self, events_dir: Path, sample_events: list[dict]):
        """Test querying date range."""
        # Create files for multiple dates
        for day in ["2025-12-01", "2025-12-02", "2025-12-03"]:
            file_path = events_dir / f"events-{day}.jsonl"
            with open(file_path, "w") as f:
                f.write(json.dumps(sample_events[0]) + "\n")

        q = EventQuery(events_dir=events_dir).date_range("2025-12-01", "2025-12-02")
        result = q.execute()

        assert result.count == 2  # 2 days

    def test_query_last_n_days(self, events_dir: Path, sample_events: list[dict]):
        """Test querying last N days."""
        # Create files for recent days
        today = datetime.now()
        for i in range(3):
            day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            file_path = events_dir / f"events-{day}.jsonl"
            with open(file_path, "w") as f:
                f.write(json.dumps(sample_events[0]) + "\n")

        q = EventQuery(events_dir=events_dir).last_n_days(2)
        result = q.execute()

        assert result.count >= 2


class TestEventQueryFiltering:
    """Tests for EventQuery filtering."""

    def test_filter_by_event_type(self, populated_events_dir: Path):
        """Test filtering by event type."""
        q = EventQuery(events_dir=populated_events_dir).filter(
            event_type="lifecycle.*"
        )
        result = q.execute()

        assert result.count == 2
        for event in result.events:
            assert event["event_type"].startswith("lifecycle.")

    def test_filter_by_namespace(self, populated_events_dir: Path):
        """Test filtering by namespace."""
        q = EventQuery(events_dir=populated_events_dir).filter(namespace="git")
        result = q.execute()

        assert result.count == 1
        assert result.events[0]["event_type"] == "git.commit"

    def test_filter_by_agent_id(self, populated_events_dir: Path):
        """Test filtering by agent ID."""
        q = EventQuery(events_dir=populated_events_dir).filter(
            agent_id="@backend-engineer"
        )
        result = q.execute()

        assert result.count == 3
        for event in result.events:
            assert event["agent_id"] == "@backend-engineer"

    def test_filter_by_task_id(self, populated_events_dir: Path):
        """Test filtering by task ID."""
        q = EventQuery(events_dir=populated_events_dir).filter(task_id="task-505")
        result = q.execute()

        assert result.count == 1
        assert result.events[0]["event_type"] == "activity.progress"

    def test_filter_multiple_criteria(self, populated_events_dir: Path):
        """Test filtering with multiple criteria."""
        q = (
            EventQuery(events_dir=populated_events_dir)
            .filter(agent_id="@backend-engineer")
            .filter(namespace="lifecycle")
        )
        result = q.execute()

        assert result.count == 2

    def test_filter_custom(self, populated_events_dir: Path):
        """Test filtering with custom function."""
        q = EventQuery(events_dir=populated_events_dir).filter(
            custom=lambda e: e.get("progress") is not None
        )
        result = q.execute()

        assert result.count == 1
        assert result.events[0]["progress"] == 0.5

    def test_limit(self, populated_events_dir: Path):
        """Test limiting results."""
        q = EventQuery(events_dir=populated_events_dir).limit(2)
        result = q.execute()

        assert len(result.events) == 2

    def test_offset(self, populated_events_dir: Path):
        """Test offsetting results."""
        q = EventQuery(events_dir=populated_events_dir).offset(2).limit(2)
        result = q.execute()

        # Should skip first 2, return next 2
        assert len(result.events) == 2


class TestEventQueryAggregations:
    """Tests for EventQuery aggregation functions."""

    def test_count_by(self, populated_events_dir: Path):
        """Test count_by aggregation."""
        q = EventQuery(events_dir=populated_events_dir).count_by("agent_id")
        result = q.execute()

        assert "count_by" in result.aggregations
        counts = result.aggregations["count_by"]
        assert counts["@backend-engineer"] == 3
        assert counts["@pm-planner"] == 1
        assert counts["@frontend-engineer"] == 1

    def test_count_by_event_type(self, populated_events_dir: Path):
        """Test count_by event_type."""
        q = EventQuery(events_dir=populated_events_dir).count_by("event_type")
        result = q.execute()

        counts = result.aggregations["count_by"]
        assert counts["lifecycle.started"] == 1
        assert counts["lifecycle.completed"] == 1
        assert counts["git.commit"] == 1

    def test_group_by_single_field(self, populated_events_dir: Path):
        """Test group_by with single field."""
        q = EventQuery(events_dir=populated_events_dir).group_by("agent_id")
        result = q.execute()

        assert "group_by" in result.aggregations
        groups = result.aggregations["group_by"]
        assert "@backend-engineer" in groups
        assert groups["@backend-engineer"]["count"] == 3

    def test_group_by_multiple_fields(self, populated_events_dir: Path):
        """Test group_by with multiple fields."""
        q = EventQuery(events_dir=populated_events_dir).group_by(
            "agent_id", "event_type"
        )
        result = q.execute()

        groups = result.aggregations["group_by"]
        # Key format is "agent_id|event_type"
        assert any("@backend-engineer|lifecycle.started" in k for k in groups.keys())

    def test_time_series_hourly(self, populated_events_dir: Path):
        """Test time_series with hourly buckets."""
        q = EventQuery(events_dir=populated_events_dir).time_series("1h")
        result = q.execute()

        assert "time_series" in result.aggregations
        buckets = result.aggregations["time_series"]
        # All events are within the same hour
        assert len(buckets) >= 1

        # Check bucket structure
        for bucket_data in buckets.values():
            assert "bucket" in bucket_data
            assert "count" in bucket_data

    def test_time_series_with_events(self, populated_events_dir: Path):
        """Test time_series with events included."""
        q = EventQuery(events_dir=populated_events_dir).time_series(
            "1h", include_events=True
        )
        result = q.execute()

        buckets = result.aggregations["time_series"]
        for bucket_data in buckets.values():
            assert bucket_data["events"] is not None


class TestEventQueryExport:
    """Tests for EventQuery export methods."""

    def test_export_json(self, populated_events_dir: Path, tmp_path: Path):
        """Test exporting to JSON file."""
        output = tmp_path / "export.json"
        q = EventQuery(events_dir=populated_events_dir)
        count = q.export_json(output)

        assert count == 5
        assert output.exists()

        data = json.loads(output.read_text())
        assert len(data["events"]) == 5

    def test_export_csv(self, populated_events_dir: Path, tmp_path: Path):
        """Test exporting to CSV file."""
        output = tmp_path / "export.csv"
        q = EventQuery(events_dir=populated_events_dir)
        count = q.export_csv(output)

        assert count == 5
        assert output.exists()

        lines = output.read_text().strip().split("\n")
        assert len(lines) == 6  # Header + 5 events

    def test_export_markdown(self, populated_events_dir: Path, tmp_path: Path):
        """Test exporting to markdown file."""
        output = tmp_path / "export.md"
        q = EventQuery(events_dir=populated_events_dir)
        count = q.export_markdown(output)

        assert count == 5
        assert output.exists()

        content = output.read_text()
        assert "## Events" in content


class TestEventQueryStreamMethods:
    """Tests for EventQuery stream methods."""

    def test_stream(self, populated_events_dir: Path):
        """Test streaming events."""
        q = EventQuery(events_dir=populated_events_dir)
        events = list(q.stream())

        assert len(events) == 5

    def test_count(self, populated_events_dir: Path):
        """Test counting events."""
        q = EventQuery(events_dir=populated_events_dir)
        count = q.count()

        assert count == 5

    def test_first(self, populated_events_dir: Path):
        """Test getting first event."""
        q = EventQuery(events_dir=populated_events_dir)
        event = q.first()

        assert event is not None
        assert "event_type" in event

    def test_first_no_results(self, events_dir: Path):
        """Test first with no results."""
        q = EventQuery(events_dir=events_dir)
        event = q.first()

        assert event is None

    def test_exists_true(self, populated_events_dir: Path):
        """Test exists returns True when events exist."""
        q = EventQuery(events_dir=populated_events_dir)
        assert q.exists() is True

    def test_exists_false(self, events_dir: Path):
        """Test exists returns False when no events."""
        q = EventQuery(events_dir=events_dir)
        assert q.exists() is False


# --- Convenience function tests ---


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_query_function(self, populated_events_dir: Path):
        """Test query() convenience function."""
        q = query(events_dir=populated_events_dir)
        result = q.execute()

        assert result.count == 5

    def test_count_events_function(self, populated_events_dir: Path):
        """Test count_events() convenience function."""
        count = count_events(events_dir=populated_events_dir)
        assert count == 5

    def test_count_events_with_filter(self, populated_events_dir: Path):
        """Test count_events() with filter."""
        count = count_events(
            events_dir=populated_events_dir, agent_id="@backend-engineer"
        )
        assert count == 3

    def test_get_events_function(self, populated_events_dir: Path):
        """Test get_events() convenience function."""
        events = get_events(events_dir=populated_events_dir)
        assert len(events) == 5

    def test_get_events_with_limit(self, populated_events_dir: Path):
        """Test get_events() with limit."""
        events = get_events(events_dir=populated_events_dir, limit=2)
        assert len(events) == 2


# --- Performance tests ---


class TestEventQueryPerformance:
    """Performance tests for EventQuery."""

    def test_query_100k_events_under_5_seconds(self, events_dir: Path):
        """Test querying 100k events completes in under 5 seconds."""
        # Generate 100k events
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = events_dir / f"events-{today}.jsonl"

        base_event = {
            "event_type": "test.event",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": "@test-agent",
            "message": "Test message",
        }

        # Write 100k events
        with open(file_path, "w") as f:
            for i in range(100_000):
                event = {**base_event, "sequence": i}
                f.write(json.dumps(event) + "\n")

        # Time the query
        start = time.time()
        q = EventQuery(events_dir=events_dir)
        result = q.execute()
        elapsed = time.time() - start

        assert result.count == 100_000
        assert elapsed < 5.0, f"Query took {elapsed:.2f}s, expected <5s"

    def test_count_by_100k_events(self, events_dir: Path):
        """Test count_by aggregation with 100k events."""
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = events_dir / f"events-{today}.jsonl"

        # Write 100k events with varying types
        event_types = [f"type_{i}" for i in range(10)]
        with open(file_path, "w") as f:
            for i in range(100_000):
                event = {
                    "event_type": event_types[i % 10],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "agent_id": "@test-agent",
                }
                f.write(json.dumps(event) + "\n")

        # Time the aggregation
        start = time.time()
        q = EventQuery(events_dir=events_dir).count_by("event_type")
        result = q.execute()
        elapsed = time.time() - start

        assert result.count == 100_000
        assert len(result.aggregations["count_by"]) == 10
        assert elapsed < 5.0, f"Aggregation took {elapsed:.2f}s, expected <5s"

    def test_streaming_memory_efficiency(self, events_dir: Path):
        """Test that streaming doesn't load all events into memory."""
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = events_dir / f"events-{today}.jsonl"

        # Write 10k events
        with open(file_path, "w") as f:
            for i in range(10_000):
                event = {
                    "event_type": "test.event",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "agent_id": "@test-agent",
                    "sequence": i,
                }
                f.write(json.dumps(event) + "\n")

        # Stream and count
        q = EventQuery(events_dir=events_dir)
        count = 0
        for _ in q.stream():
            count += 1
            if count == 100:
                break  # Only process first 100

        # We should have stopped early
        assert count == 100
