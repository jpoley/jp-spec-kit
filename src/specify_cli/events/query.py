"""Event Query API with fluent interface and aggregations.

This module provides a high-performance query API for analyzing events from
JSONL files. Supports filtering, aggregation, and multiple export formats.

Key Features:
    - Fluent API for building queries
    - Streaming reads for memory efficiency
    - Aggregation functions: count_by, group_by, time_series
    - Export to JSON, CSV, markdown
    - Performance target: 100k events in <5 seconds

Example:
    >>> from specify_cli.events.query import EventQuery
    >>>
    >>> # Simple query
    >>> events = EventQuery().filter(agent_id="@backend-engineer").execute()
    >>>
    >>> # Aggregation
    >>> counts = EventQuery().count_by("event_type").execute()
    >>>
    >>> # Time series
    >>> series = EventQuery().time_series("1h").execute()
    >>>
    >>> # Export
    >>> EventQuery().filter(namespace="lifecycle").export_csv("events.csv")
"""

from __future__ import annotations

import csv
import fnmatch
import io
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

from .writer import DEFAULT_EVENTS_DIR


@dataclass
class QueryResult:
    """Result of an event query.

    Attributes:
        events: List of matching events.
        count: Total count of matching events.
        aggregations: Aggregation results if requested.
        metadata: Query metadata (timing, files scanned, etc.).
    """

    events: list[dict[str, Any]] = field(default_factory=list)
    count: int = 0
    aggregations: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_json(self, indent: int = 2) -> str:
        """Export result as JSON string."""
        return json.dumps(
            {
                "events": self.events,
                "count": self.count,
                "aggregations": self.aggregations,
                "metadata": self.metadata,
            },
            indent=indent,
            default=str,
        )

    def to_csv(self) -> str:
        """Export events as CSV string."""
        if not self.events:
            return ""

        output = io.StringIO()
        # Flatten events for CSV
        fieldnames = _get_csv_fieldnames(self.events)
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for event in self.events:
            flat = _flatten_event(event)
            writer.writerow(flat)

        return output.getvalue()

    def to_markdown(self) -> str:
        """Export result as markdown table."""
        lines = []

        if self.events:
            lines.append("## Events\n")
            lines.append("| Timestamp | Type | Agent | Message |")
            lines.append("|-----------|------|-------|---------|")

            for event in self.events[:100]:  # Limit for readability
                timestamp = event.get("timestamp", "")[:19]
                event_type = event.get("event_type", "")
                agent_id = event.get("agent_id", "")
                message = (event.get("message") or "")[:50]
                lines.append(f"| {timestamp} | {event_type} | {agent_id} | {message} |")

            if len(self.events) > 100:
                lines.append(f"\n*...and {len(self.events) - 100} more events*\n")

        if self.aggregations:
            lines.append("\n## Aggregations\n")
            for name, data in self.aggregations.items():
                lines.append(f"### {name}\n")
                if isinstance(data, dict):
                    lines.append("| Key | Count |")
                    lines.append("|-----|-------|")
                    for key, value in list(data.items())[:20]:
                        lines.append(f"| {key} | {value} |")
                    if len(data) > 20:
                        lines.append(f"\n*...and {len(data) - 20} more entries*\n")
                else:
                    lines.append(f"{data}\n")

        lines.append(f"\n---\n*Total: {self.count} events*\n")
        return "\n".join(lines)


@dataclass
class TimeSeriesPoint:
    """A point in a time series aggregation."""

    bucket: datetime
    count: int
    events: list[dict[str, Any]] = field(default_factory=list)


class EventQuery:
    """Fluent query builder for events.

    Build queries incrementally and execute them against JSONL event files.
    Supports filtering, aggregation, and export to multiple formats.

    Example:
        >>> query = (
        ...     EventQuery(project_root="/path/to/project")
        ...     .filter(agent_id="@backend-engineer")
        ...     .filter(namespace="lifecycle")
        ...     .date_range("2025-12-01", "2025-12-15")
        ...     .limit(100)
        ... )
        >>> result = query.execute()
        >>> print(result.count)
    """

    def __init__(
        self,
        project_root: Path | str | None = None,
        events_dir: Path | str | None = None,
    ) -> None:
        """Initialize the query builder.

        Args:
            project_root: Project root directory (uses events_dir inside).
            events_dir: Direct path to events directory (overrides project_root).
        """
        if events_dir:
            self._events_dir = Path(events_dir)
        elif project_root:
            self._events_dir = Path(project_root) / DEFAULT_EVENTS_DIR
        else:
            self._events_dir = Path.cwd() / DEFAULT_EVENTS_DIR

        # Filter state
        self._date: str | None = None
        self._start_date: str | None = None
        self._end_date: str | None = None
        self._event_types: list[str] = []
        self._namespaces: list[str] = []
        self._agent_ids: list[str] = []
        self._task_ids: list[str] = []
        self._custom_filters: list[Callable[[dict[str, Any]], bool]] = []

        # Result options
        self._limit: int | None = None
        self._offset: int = 0
        self._order_by: str = "timestamp"
        self._order_desc: bool = True

        # Aggregation state
        self._count_by_field: str | None = None
        self._group_by_fields: list[str] = []
        self._time_series_interval: str | None = None
        self._include_events: bool = True

    def filter(
        self,
        event_type: str | None = None,
        namespace: str | None = None,
        agent_id: str | None = None,
        task_id: str | None = None,
        custom: Callable[[dict[str, Any]], bool] | None = None,
    ) -> "EventQuery":
        """Add filter criteria.

        All criteria are ANDed together. Multiple calls to filter() stack.

        Args:
            event_type: Event type pattern (supports wildcards: "git.*").
            namespace: Namespace filter (first part of event_type).
            agent_id: Agent ID to match.
            task_id: Task ID in context to match.
            custom: Custom filter function.

        Returns:
            Self for chaining.

        Example:
            >>> query.filter(agent_id="@backend-engineer").filter(namespace="git")
        """
        if event_type:
            self._event_types.append(event_type)
        if namespace:
            self._namespaces.append(namespace)
        if agent_id:
            self._agent_ids.append(agent_id)
        if task_id:
            self._task_ids.append(task_id)
        if custom:
            self._custom_filters.append(custom)
        return self

    def date(self, date: str) -> "EventQuery":
        """Filter to a specific date.

        Args:
            date: Date string in YYYY-MM-DD format.

        Returns:
            Self for chaining.
        """
        self._date = date
        self._start_date = None
        self._end_date = None
        return self

    def date_range(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> "EventQuery":
        """Filter to a date range.

        Args:
            start_date: Start date (inclusive) YYYY-MM-DD.
            end_date: End date (inclusive) YYYY-MM-DD.

        Returns:
            Self for chaining.
        """
        self._date = None
        self._start_date = start_date
        self._end_date = end_date
        return self

    def today(self) -> "EventQuery":
        """Filter to today's events.

        Returns:
            Self for chaining.
        """
        self._date = datetime.now().strftime("%Y-%m-%d")
        return self

    def last_n_days(self, days: int) -> "EventQuery":
        """Filter to events from the last N days.

        Args:
            days: Number of days to look back.

        Returns:
            Self for chaining.
        """
        end = datetime.now()
        start = end - timedelta(days=days)
        self._start_date = start.strftime("%Y-%m-%d")
        self._end_date = end.strftime("%Y-%m-%d")
        return self

    def limit(self, n: int) -> "EventQuery":
        """Limit the number of results.

        Args:
            n: Maximum number of events to return.

        Returns:
            Self for chaining.
        """
        self._limit = n
        return self

    def offset(self, n: int) -> "EventQuery":
        """Skip the first N results.

        Args:
            n: Number of events to skip.

        Returns:
            Self for chaining.
        """
        self._offset = n
        return self

    def order_by(
        self,
        field: str = "timestamp",
        descending: bool = True,
    ) -> "EventQuery":
        """Set result ordering.

        Args:
            field: Field to order by (default: timestamp).
            descending: Whether to order descending (default: True = newest first).

        Returns:
            Self for chaining.
        """
        self._order_by = field
        self._order_desc = descending
        return self

    def count_by(self, field: str) -> "EventQuery":
        """Count events grouped by a field.

        Args:
            field: Field to group by (e.g., "event_type", "agent_id").

        Returns:
            Self for chaining.

        Example:
            >>> result = EventQuery().count_by("event_type").execute()
            >>> print(result.aggregations["count_by"])
            {"lifecycle.started": 10, "git.commit": 5}
        """
        self._count_by_field = field
        return self

    def group_by(self, *fields: str) -> "EventQuery":
        """Group events by one or more fields.

        Args:
            *fields: Fields to group by.

        Returns:
            Self for chaining.

        Example:
            >>> result = EventQuery().group_by("agent_id", "event_type").execute()
        """
        self._group_by_fields = list(fields)
        return self

    def time_series(
        self,
        interval: str = "1h",
        include_events: bool = False,
    ) -> "EventQuery":
        """Aggregate events into time buckets.

        Args:
            interval: Bucket size (e.g., "1m", "5m", "1h", "1d").
            include_events: Whether to include events in each bucket.

        Returns:
            Self for chaining.

        Example:
            >>> result = EventQuery().time_series("1h").execute()
            >>> for bucket, count in result.aggregations["time_series"].items():
            ...     print(f"{bucket}: {count} events")
        """
        self._time_series_interval = interval
        self._include_events = include_events
        return self

    def execute(self) -> QueryResult:
        """Execute the query and return results.

        Returns:
            QueryResult containing events and/or aggregations.
        """
        start_time = datetime.now()

        # Stream and filter events
        events = list(self._stream_filtered_events())

        # Sort
        events = self._sort_events(events)

        # Apply offset and limit
        if self._offset:
            events = events[self._offset :]
        if self._limit:
            events = events[: self._limit]

        # Build result
        result = QueryResult(
            events=events if not self._has_aggregations() else [],
            count=len(events),
            metadata={
                "query_time_ms": (datetime.now() - start_time).total_seconds() * 1000,
                "events_dir": str(self._events_dir),
            },
        )

        # Compute aggregations
        if self._count_by_field:
            result.aggregations["count_by"] = self._compute_count_by(events)

        if self._group_by_fields:
            result.aggregations["group_by"] = self._compute_group_by(events)

        if self._time_series_interval:
            result.aggregations["time_series"] = self._compute_time_series(events)
            if not self._include_events:
                result.events = []

        return result

    def stream(self) -> Iterator[dict[str, Any]]:
        """Stream matching events without loading all into memory.

        Yields:
            Matching events one at a time.

        Example:
            >>> for event in EventQuery().filter(namespace="git").stream():
            ...     print(event["event_type"])
        """
        yield from self._stream_filtered_events()

    def count(self) -> int:
        """Count matching events without loading all into memory.

        Returns:
            Number of matching events.
        """
        return sum(1 for _ in self._stream_filtered_events())

    def first(self) -> dict[str, Any] | None:
        """Get the first matching event.

        Returns:
            First matching event or None.
        """
        for event in self._stream_filtered_events():
            return event
        return None

    def exists(self) -> bool:
        """Check if any events match the query.

        Returns:
            True if at least one event matches.
        """
        return self.first() is not None

    def export_json(self, path: Path | str, indent: int = 2) -> int:
        """Export results to JSON file.

        Args:
            path: Output file path.
            indent: JSON indentation.

        Returns:
            Number of events exported.
        """
        result = self.execute()
        Path(path).write_text(result.to_json(indent=indent))
        return result.count

    def export_csv(self, path: Path | str) -> int:
        """Export results to CSV file.

        Args:
            path: Output file path.

        Returns:
            Number of events exported.
        """
        result = self.execute()
        Path(path).write_text(result.to_csv())
        return result.count

    def export_markdown(self, path: Path | str) -> int:
        """Export results to markdown file.

        Args:
            path: Output file path.

        Returns:
            Number of events exported.
        """
        result = self.execute()
        Path(path).write_text(result.to_markdown())
        return result.count

    # --- Private methods ---

    def _has_aggregations(self) -> bool:
        """Check if any aggregations are requested."""
        return bool(
            self._count_by_field or self._group_by_fields or self._time_series_interval
        )

    def _get_files_to_scan(self) -> list[Path]:
        """Get list of JSONL files to scan based on date filters."""
        if not self._events_dir.exists():
            return []

        all_files = sorted(self._events_dir.glob("events-*.jsonl"))

        if self._date:
            # Single date
            target = self._events_dir / f"events-{self._date}.jsonl"
            return [target] if target.exists() else []

        if self._start_date or self._end_date:
            # Date range
            filtered = []
            for f in all_files:
                try:
                    date_str = f.stem.replace("events-", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d").date()

                    if self._start_date:
                        start = datetime.strptime(self._start_date, "%Y-%m-%d").date()
                        if file_date < start:
                            continue

                    if self._end_date:
                        end = datetime.strptime(self._end_date, "%Y-%m-%d").date()
                        if file_date > end:
                            continue

                    filtered.append(f)
                except ValueError:
                    continue
            return filtered

        # Default: today only
        today = datetime.now().strftime("%Y-%m-%d")
        target = self._events_dir / f"events-{today}.jsonl"
        return [target] if target.exists() else []

    def _stream_filtered_events(self) -> Iterator[dict[str, Any]]:
        """Stream events from files, applying filters."""
        # Compile patterns once
        type_patterns = [re.compile(fnmatch.translate(p)) for p in self._event_types]

        for file_path in self._get_files_to_scan():
            yield from self._stream_file(file_path, type_patterns)

    def _stream_file(
        self,
        file_path: Path,
        type_patterns: list[re.Pattern],
    ) -> Iterator[dict[str, Any]]:
        """Stream events from a single file."""
        try:
            with open(file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if self._matches_filters(event, type_patterns):
                        yield event

        except (OSError, IOError):
            pass

    def _matches_filters(
        self,
        event: dict[str, Any],
        type_patterns: list[re.Pattern],
    ) -> bool:
        """Check if event matches all filter criteria."""
        event_type = event.get("event_type", "")

        # Event type patterns
        if type_patterns:
            if not any(p.match(event_type) for p in type_patterns):
                return False

        # Namespace filter
        if self._namespaces:
            namespace = event_type.split(".")[0] if "." in event_type else ""
            if namespace not in self._namespaces:
                return False

        # Agent ID filter
        if self._agent_ids:
            if event.get("agent_id") not in self._agent_ids:
                return False

        # Task ID filter
        if self._task_ids:
            event_task_id = event.get("context", {}).get("task_id") or event.get(
                "task", {}
            ).get("task_id")
            if event_task_id not in self._task_ids:
                return False

        # Custom filters
        for custom_filter in self._custom_filters:
            if not custom_filter(event):
                return False

        return True

    def _sort_events(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Sort events by the specified field."""

        def get_sort_key(event: dict[str, Any]) -> Any:
            value = event.get(self._order_by, "")
            return value if value is not None else ""

        return sorted(events, key=get_sort_key, reverse=self._order_desc)

    def _compute_count_by(
        self,
        events: list[dict[str, Any]],
    ) -> dict[str, int]:
        """Compute count aggregation."""
        counter: Counter[str] = Counter()

        for event in events:
            value = _get_nested_value(event, self._count_by_field)
            key = str(value) if value is not None else "null"
            counter[key] += 1

        return dict(counter.most_common())

    def _compute_group_by(
        self,
        events: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Compute group by aggregation."""
        groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)

        for event in events:
            key_parts = []
            for field_name in self._group_by_fields:
                value = _get_nested_value(event, field_name)
                key_parts.append(str(value) if value is not None else "null")

            groups[tuple(key_parts)].append(event)

        # Convert to serializable format
        result = {}
        for key_tuple, group_events in groups.items():
            key_str = "|".join(key_tuple)
            result[key_str] = {
                "count": len(group_events),
                "keys": dict(zip(self._group_by_fields, key_tuple)),
            }

        return result

    def _compute_time_series(
        self,
        events: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Compute time series aggregation."""
        interval_seconds = _parse_interval(self._time_series_interval or "1h")

        buckets: dict[str, TimeSeriesPoint] = {}

        for event in events:
            timestamp_str = event.get("timestamp", "")
            try:
                # Parse timestamp
                timestamp_str = timestamp_str.replace("Z", "+00:00")
                timestamp = datetime.fromisoformat(timestamp_str)

                # Compute bucket
                bucket_ts = (
                    int(timestamp.timestamp()) // interval_seconds * interval_seconds
                )
                bucket_dt = datetime.fromtimestamp(bucket_ts, tz=timezone.utc)
                bucket_key = bucket_dt.isoformat()

                if bucket_key not in buckets:
                    buckets[bucket_key] = TimeSeriesPoint(
                        bucket=bucket_dt,
                        count=0,
                        events=[],
                    )

                buckets[bucket_key].count += 1
                if self._include_events:
                    buckets[bucket_key].events.append(event)

            except (ValueError, TypeError):
                continue

        # Convert to serializable format
        return {
            key: {
                "bucket": point.bucket.isoformat(),
                "count": point.count,
                "events": point.events if self._include_events else None,
            }
            for key, point in sorted(buckets.items())
        }


# --- Helper functions ---


def _get_nested_value(obj: dict[str, Any], path: str) -> Any:
    """Get a nested value from a dict using dot notation."""
    parts = path.split(".")
    current = obj

    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None

    return current


def _parse_interval(interval: str) -> int:
    """Parse interval string to seconds."""
    match = re.match(r"^(\d+)([smhd])$", interval.lower())
    if not match:
        return 3600  # Default 1 hour

    value = int(match.group(1))
    unit = match.group(2)

    multipliers = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
    }

    return value * multipliers.get(unit, 3600)


def _flatten_event(event: dict[str, Any], prefix: str = "") -> dict[str, str]:
    """Flatten a nested event dict for CSV export."""
    result = {}

    for key, value in event.items():
        full_key = f"{prefix}{key}" if prefix else key

        if isinstance(value, dict):
            result.update(_flatten_event(value, f"{full_key}."))
        elif isinstance(value, list):
            result[full_key] = json.dumps(value)
        else:
            result[full_key] = str(value) if value is not None else ""

    return result


def _get_csv_fieldnames(events: list[dict[str, Any]]) -> list[str]:
    """Get CSV fieldnames from events."""
    fieldnames = set()

    for event in events[:100]:  # Sample first 100
        flat = _flatten_event(event)
        fieldnames.update(flat.keys())

    # Order with common fields first
    priority = [
        "timestamp",
        "event_type",
        "agent_id",
        "message",
        "context.task_id",
        "context.branch_name",
    ]

    ordered = []
    for priority_field in priority:
        if priority_field in fieldnames:
            ordered.append(priority_field)
            fieldnames.discard(priority_field)

    ordered.extend(sorted(fieldnames))
    return ordered


# --- Convenience functions ---


def query(
    project_root: Path | str | None = None,
    events_dir: Path | str | None = None,
) -> EventQuery:
    """Create a new event query builder.

    Args:
        project_root: Project root directory.
        events_dir: Direct path to events directory.

    Returns:
        EventQuery instance for building queries.

    Example:
        >>> from specify_cli.events.query import query
        >>> events = query().filter(agent_id="@backend-engineer").execute().events
    """
    return EventQuery(project_root=project_root, events_dir=events_dir)


def count_events(
    project_root: Path | str | None = None,
    events_dir: Path | str | None = None,
    **filters: Any,
) -> int:
    """Quick count of events matching filters.

    Args:
        project_root: Project root directory.
        events_dir: Direct path to events directory (overrides project_root).
        **filters: Filter arguments passed to filter().

    Returns:
        Number of matching events.

    Example:
        >>> count = count_events(agent_id="@backend-engineer")
    """
    q = EventQuery(project_root=project_root, events_dir=events_dir)
    if filters:
        q = q.filter(**filters)
    return q.count()


def get_events(
    project_root: Path | str | None = None,
    events_dir: Path | str | None = None,
    limit: int = 100,
    **filters: Any,
) -> list[dict[str, Any]]:
    """Quick retrieval of events matching filters.

    Args:
        project_root: Project root directory.
        events_dir: Direct path to events directory (overrides project_root).
        limit: Maximum events to return.
        **filters: Filter arguments passed to filter().

    Returns:
        List of matching events.

    Example:
        >>> events = get_events(namespace="lifecycle", limit=10)
    """
    q = EventQuery(project_root=project_root, events_dir=events_dir).limit(limit)
    if filters:
        q = q.filter(**filters)
    return q.execute().events
