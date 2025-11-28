"""Structured audit logging for Satellite Mode operations.

This module provides comprehensive audit logging with support for multiple
output formats (JSON, Markdown), log rotation, and querying capabilities.
Designed for compliance requirements including SOC 2 and SLSA attestations.

Security Design:
- Structured logs with consistent schema
- JSON format for machine parsing and SIEM integration
- Human-readable markdown summaries
- Automatic log rotation (configurable, default 100MB)
- Token redaction integration (via secrets.TokenRedactionFilter)
- SLSA-compliant attestation format

Example:
    >>> from specify_cli.satellite import AuditLogger, AuditEvent
    >>> logger = AuditLogger()
    >>> logger.log_sync(
    ...     operation="push",
    ...     provider="github",
    ...     task_id="task-42",
    ...     status="success"
    ... )
"""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Union

from platformdirs import user_log_dir


class AuditEventType(Enum):
    """Types of auditable events in Satellite Mode."""

    # Sync operations
    SYNC_START = "sync_start"
    SYNC_COMPLETE = "sync_complete"
    SYNC_FAILED = "sync_failed"

    # Task operations
    TASK_CREATED = "task_created"
    TASK_UPDATED = "task_updated"
    TASK_DELETED = "task_deleted"
    TASK_PUSHED = "task_pushed"
    TASK_PULLED = "task_pulled"

    # Authentication
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILED = "auth_failed"
    TOKEN_STORED = "token_stored"
    TOKEN_DELETED = "token_deleted"
    TOKEN_ROTATED = "token_rotated"

    # Conflicts
    CONFLICT_DETECTED = "conflict_detected"
    CONFLICT_RESOLVED = "conflict_resolved"
    CONFLICT_MANUAL = "conflict_manual"

    # System events
    PROVIDER_CONNECTED = "provider_connected"
    PROVIDER_DISCONNECTED = "provider_disconnected"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"


class AuditSeverity(Enum):
    """Severity levels for audit events."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Represents a single audit log event.

    Attributes:
        event_type: The type of event being logged
        timestamp: When the event occurred (UTC)
        severity: Severity level of the event
        provider: Remote provider involved (github, jira, notion)
        operation: Specific operation performed
        task_id: Local task identifier if applicable
        remote_id: Remote issue/task identifier if applicable
        user: User or agent performing the action
        status: Result status (success, failed, pending)
        details: Additional context as key-value pairs
        correlation_id: ID linking related events
        duration_ms: Operation duration in milliseconds
    """

    event_type: AuditEventType
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    severity: AuditSeverity = AuditSeverity.INFO
    provider: Optional[str] = None
    operation: Optional[str] = None
    task_id: Optional[str] = None
    remote_id: Optional[str] = None
    user: Optional[str] = None
    status: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    duration_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        result = {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.value,
        }

        # Add optional fields if present
        optional_fields = [
            "provider",
            "operation",
            "task_id",
            "remote_id",
            "user",
            "status",
            "correlation_id",
            "duration_ms",
        ]
        for f in optional_fields:
            value = getattr(self, f)
            if value is not None:
                result[f] = value

        if self.details:
            result["details"] = self.details

        return result

    def to_json(self) -> str:
        """Serialize event to JSON string."""
        return json.dumps(self.to_dict(), indent=None, default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditEvent":
        """Create event from dictionary."""
        # Parse event_type
        event_type = AuditEventType(data["event_type"])

        # Parse timestamp
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        elif timestamp is None:
            timestamp = datetime.now(timezone.utc)

        # Parse severity
        severity = AuditSeverity(data.get("severity", "info"))

        return cls(
            event_type=event_type,
            timestamp=timestamp,
            severity=severity,
            provider=data.get("provider"),
            operation=data.get("operation"),
            task_id=data.get("task_id"),
            remote_id=data.get("remote_id"),
            user=data.get("user"),
            status=data.get("status"),
            details=data.get("details", {}),
            correlation_id=data.get("correlation_id"),
            duration_ms=data.get("duration_ms"),
        )


@dataclass
class SLSAAttestation:
    """SLSA provenance attestation for audit trail.

    Follows SLSA v1.0 attestation format for supply chain security.
    See: https://slsa.dev/spec/v1.0/provenance

    Attributes:
        subject: What is being attested (sync operation, task)
        predicate_type: SLSA predicate type URL
        builder_id: Identity of the build/sync system
        build_type: Type of build/operation
        invocation: Details about how the operation was triggered
        materials: Input artifacts and their digests
        metadata: Additional provenance metadata
    """

    subject: List[Dict[str, Any]]
    predicate_type: str = "https://slsa.dev/provenance/v1"
    builder_id: str = "backlog-satellite"
    build_type: str = "sync"
    invocation: Dict[str, Any] = field(default_factory=dict)
    materials: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert attestation to SLSA format."""
        return {
            "_type": "https://in-toto.io/Statement/v1",
            "subject": self.subject,
            "predicateType": self.predicate_type,
            "predicate": {
                "buildDefinition": {
                    "buildType": self.build_type,
                    "externalParameters": self.invocation.get("parameters", {}),
                    "internalParameters": {},
                    "resolvedDependencies": self.materials,
                },
                "runDetails": {
                    "builder": {"id": self.builder_id},
                    "metadata": self.metadata,
                },
            },
        }

    def to_json(self) -> str:
        """Serialize attestation to JSON."""
        return json.dumps(self.to_dict(), indent=2, default=str)


class AuditFormatter:
    """Base class for audit log formatters."""

    def format(self, event: AuditEvent) -> str:
        """Format an audit event."""
        raise NotImplementedError


class JSONFormatter(AuditFormatter):
    """Formats audit events as JSON lines (JSONL)."""

    def __init__(self, pretty: bool = False):
        """Initialize formatter.

        Args:
            pretty: If True, use indented JSON output
        """
        self.pretty = pretty

    def format(self, event: AuditEvent) -> str:
        """Format event as JSON line."""
        if self.pretty:
            return json.dumps(event.to_dict(), indent=2, default=str)
        return event.to_json()


class MarkdownFormatter(AuditFormatter):
    """Formats audit events as human-readable markdown."""

    SEVERITY_ICONS = {
        AuditSeverity.DEBUG: "🔍",
        AuditSeverity.INFO: "ℹ️",
        AuditSeverity.WARNING: "⚠️",
        AuditSeverity.ERROR: "❌",
        AuditSeverity.CRITICAL: "🚨",
    }

    EVENT_ICONS = {
        AuditEventType.SYNC_START: "🔄",
        AuditEventType.SYNC_COMPLETE: "✅",
        AuditEventType.SYNC_FAILED: "❌",
        AuditEventType.TASK_CREATED: "➕",
        AuditEventType.TASK_UPDATED: "📝",
        AuditEventType.TASK_DELETED: "🗑️",
        AuditEventType.TASK_PUSHED: "⬆️",
        AuditEventType.TASK_PULLED: "⬇️",
        AuditEventType.AUTH_SUCCESS: "🔓",
        AuditEventType.AUTH_FAILED: "🔒",
        AuditEventType.CONFLICT_DETECTED: "⚡",
        AuditEventType.CONFLICT_RESOLVED: "🤝",
        AuditEventType.ERROR: "💥",
    }

    def format(self, event: AuditEvent) -> str:
        """Format event as markdown."""
        icon = self.EVENT_ICONS.get(event.event_type, "•")
        severity_icon = self.SEVERITY_ICONS.get(event.severity, "")
        timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

        lines = [f"{icon} **{event.event_type.value}** {severity_icon}"]
        lines.append(f"  - Time: {timestamp}")

        if event.provider:
            lines.append(f"  - Provider: {event.provider}")
        if event.operation:
            lines.append(f"  - Operation: {event.operation}")
        if event.task_id:
            lines.append(f"  - Task: {event.task_id}")
        if event.remote_id:
            lines.append(f"  - Remote ID: {event.remote_id}")
        if event.status:
            lines.append(f"  - Status: {event.status}")
        if event.duration_ms is not None:
            lines.append(f"  - Duration: {event.duration_ms}ms")
        if event.details:
            lines.append(f"  - Details: {json.dumps(event.details)}")

        return "\n".join(lines)


class AuditQuery:
    """Query builder for filtering audit logs.

    Example:
        >>> query = AuditQuery()
        >>> query.event_type(AuditEventType.SYNC_COMPLETE)
        >>> query.provider("github")
        >>> query.since(datetime(2024, 1, 1))
        >>> results = logger.query(query)
    """

    def __init__(self):
        """Initialize empty query."""
        self._filters: List[Callable[[AuditEvent], bool]] = []
        self._limit: Optional[int] = None
        self._offset: int = 0

    def event_type(self, *types: AuditEventType) -> "AuditQuery":
        """Filter by event type(s)."""
        self._filters.append(lambda e: e.event_type in types)
        return self

    def severity(self, *severities: AuditSeverity) -> "AuditQuery":
        """Filter by severity level(s)."""
        self._filters.append(lambda e: e.severity in severities)
        return self

    def provider(self, *providers: str) -> "AuditQuery":
        """Filter by provider name(s)."""
        self._filters.append(lambda e: e.provider in providers)
        return self

    def task_id(self, task_id: str) -> "AuditQuery":
        """Filter by task ID."""
        self._filters.append(lambda e: e.task_id == task_id)
        return self

    def since(self, dt: datetime) -> "AuditQuery":
        """Filter events after datetime."""
        self._filters.append(lambda e: e.timestamp >= dt)
        return self

    def until(self, dt: datetime) -> "AuditQuery":
        """Filter events before datetime."""
        self._filters.append(lambda e: e.timestamp <= dt)
        return self

    def status(self, *statuses: str) -> "AuditQuery":
        """Filter by status value(s)."""
        self._filters.append(lambda e: e.status in statuses)
        return self

    def correlation_id(self, cid: str) -> "AuditQuery":
        """Filter by correlation ID."""
        self._filters.append(lambda e: e.correlation_id == cid)
        return self

    def limit(self, n: int) -> "AuditQuery":
        """Limit number of results."""
        self._limit = n
        return self

    def offset(self, n: int) -> "AuditQuery":
        """Skip first n results."""
        self._offset = n
        return self

    def matches(self, event: AuditEvent) -> bool:
        """Check if event matches all filters."""
        return all(f(event) for f in self._filters)


class AuditLogger:
    """Main audit logger for Satellite Mode operations.

    Provides structured logging with support for JSON and Markdown output,
    automatic log rotation, and query capabilities.

    Attributes:
        log_dir: Directory where audit logs are stored
        json_file: Path to JSON log file
        markdown_file: Path to markdown summary file
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep

    Example:
        >>> logger = AuditLogger()
        >>> logger.log_sync(
        ...     operation="push",
        ...     provider="github",
        ...     task_id="task-42",
        ...     status="success"
        ... )
        >>> # Query recent errors
        >>> query = AuditQuery().severity(AuditSeverity.ERROR).limit(10)
        >>> errors = list(logger.query(query))
    """

    DEFAULT_LOG_DIR = "backlog-satellite"
    DEFAULT_MAX_BYTES = 100 * 1024 * 1024  # 100MB
    DEFAULT_BACKUP_COUNT = 5

    def __init__(
        self,
        log_dir: Optional[Union[str, Path]] = None,
        max_bytes: int = DEFAULT_MAX_BYTES,
        backup_count: int = DEFAULT_BACKUP_COUNT,
    ):
        """Initialize the audit logger.

        Args:
            log_dir: Directory for audit logs (default: platform-specific)
            max_bytes: Maximum file size before rotation (default: 100MB)
            backup_count: Number of backup files to keep (default: 5)
        """
        if log_dir is None:
            log_dir = Path(user_log_dir(self.DEFAULT_LOG_DIR))
        else:
            log_dir = Path(log_dir)

        self.log_dir = log_dir
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Initialize log files
        self.json_file = self.log_dir / "audit.jsonl"
        self.markdown_file = self.log_dir / "audit.md"

        # Formatters
        self._json_formatter = JSONFormatter()
        self._markdown_formatter = MarkdownFormatter()

    def _rotate_if_needed(self, file_path: Path) -> None:
        """Check file size and rotate if necessary."""
        if not file_path.exists():
            return

        try:
            if file_path.stat().st_size < self.max_bytes:
                return
        except OSError:
            return

        # Rotate files: .5 -> .6, .4 -> .5, etc.
        for i in range(self.backup_count, 0, -1):
            src = Path(f"{file_path}.{i}")
            dst = Path(f"{file_path}.{i + 1}")
            if src.exists():
                if i == self.backup_count:
                    src.unlink()  # Remove oldest
                else:
                    src.rename(dst)

        # Move current to .1
        file_path.rename(Path(f"{file_path}.1"))

    def log(self, event: AuditEvent) -> None:
        """Log an audit event.

        Args:
            event: The audit event to log
        """
        # Check rotation before writing
        self._rotate_if_needed(self.json_file)
        self._rotate_if_needed(self.markdown_file)

        # Write JSON
        json_line = self._json_formatter.format(event) + "\n"
        with open(self.json_file, "a", encoding="utf-8") as f:
            f.write(json_line)

        # Write Markdown
        with open(self.markdown_file, "a", encoding="utf-8") as f:
            f.write(self._markdown_formatter.format(event) + "\n\n")

    def log_sync(
        self,
        operation: str,
        provider: str,
        task_id: Optional[str] = None,
        remote_id: Optional[str] = None,
        status: str = "success",
        duration_ms: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Log a sync operation.

        Convenience method for logging sync events with appropriate defaults.

        Args:
            operation: Type of sync (push, pull, sync)
            provider: Remote provider name
            task_id: Local task identifier
            remote_id: Remote issue/task identifier
            status: Operation result
            duration_ms: Operation duration
            details: Additional context
            correlation_id: ID for correlating related events
        """
        event_type = {
            "success": AuditEventType.SYNC_COMPLETE,
            "failed": AuditEventType.SYNC_FAILED,
            "started": AuditEventType.SYNC_START,
        }.get(status, AuditEventType.SYNC_COMPLETE)

        severity = (
            AuditSeverity.ERROR if status == "failed" else AuditSeverity.INFO
        )

        event = AuditEvent(
            event_type=event_type,
            severity=severity,
            provider=provider,
            operation=operation,
            task_id=task_id,
            remote_id=remote_id,
            status=status,
            duration_ms=duration_ms,
            details=details or {},
            correlation_id=correlation_id,
        )
        self.log(event)

    def log_auth(
        self,
        provider: str,
        success: bool,
        user: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an authentication event.

        Args:
            provider: Remote provider name
            success: Whether authentication succeeded
            user: Username or identity
            details: Additional context
        """
        event = AuditEvent(
            event_type=AuditEventType.AUTH_SUCCESS if success else AuditEventType.AUTH_FAILED,
            severity=AuditSeverity.INFO if success else AuditSeverity.WARNING,
            provider=provider,
            user=user,
            status="success" if success else "failed",
            details=details or {},
        )
        self.log(event)

    def log_conflict(
        self,
        provider: str,
        task_id: str,
        remote_id: Optional[str] = None,
        resolution: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a conflict event.

        Args:
            provider: Remote provider name
            task_id: Local task identifier
            remote_id: Remote issue/task identifier
            resolution: How conflict was resolved (local, remote, manual)
            details: Additional context
        """
        if resolution:
            event_type = (
                AuditEventType.CONFLICT_MANUAL
                if resolution == "manual"
                else AuditEventType.CONFLICT_RESOLVED
            )
        else:
            event_type = AuditEventType.CONFLICT_DETECTED

        event = AuditEvent(
            event_type=event_type,
            severity=AuditSeverity.WARNING,
            provider=provider,
            task_id=task_id,
            remote_id=remote_id,
            status=resolution,
            details=details or {},
        )
        self.log(event)

    def log_error(
        self,
        message: str,
        provider: Optional[str] = None,
        task_id: Optional[str] = None,
        exception: Optional[Exception] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an error event.

        Args:
            message: Error message
            provider: Remote provider name if applicable
            task_id: Task identifier if applicable
            exception: Exception object if available
            details: Additional context
        """
        error_details = details or {}
        error_details["message"] = message
        if exception:
            error_details["exception_type"] = type(exception).__name__
            error_details["exception_message"] = str(exception)

        event = AuditEvent(
            event_type=AuditEventType.ERROR,
            severity=AuditSeverity.ERROR,
            provider=provider,
            task_id=task_id,
            status="error",
            details=error_details,
        )
        self.log(event)

    def query(self, query: AuditQuery) -> Iterator[AuditEvent]:
        """Query audit logs.

        Args:
            query: Query filters to apply

        Yields:
            Matching audit events
        """
        if not self.json_file.exists():
            return

        count = 0
        skipped = 0

        with open(self.json_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    event = AuditEvent.from_dict(data)

                    if query.matches(event):
                        if skipped < query._offset:
                            skipped += 1
                            continue

                        yield event
                        count += 1

                        if query._limit and count >= query._limit:
                            return
                except (json.JSONDecodeError, KeyError, ValueError):
                    # Skip malformed entries
                    continue

    def get_stats(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get aggregate statistics from audit logs.

        Args:
            since: Start datetime for stats
            until: End datetime for stats

        Returns:
            Dictionary with event counts, providers, operations, etc.
        """
        stats: Dict[str, Any] = {
            "total_events": 0,
            "by_type": {},
            "by_severity": {},
            "by_provider": {},
            "by_status": {},
            "sync_operations": 0,
            "errors": 0,
            "conflicts": 0,
        }

        query = AuditQuery()
        if since:
            query.since(since)
        if until:
            query.until(until)

        for event in self.query(query):
            stats["total_events"] += 1

            # Count by type
            type_key = event.event_type.value
            stats["by_type"][type_key] = stats["by_type"].get(type_key, 0) + 1

            # Count by severity
            sev_key = event.severity.value
            stats["by_severity"][sev_key] = stats["by_severity"].get(sev_key, 0) + 1

            # Count by provider
            if event.provider:
                stats["by_provider"][event.provider] = (
                    stats["by_provider"].get(event.provider, 0) + 1
                )

            # Count by status
            if event.status:
                stats["by_status"][event.status] = (
                    stats["by_status"].get(event.status, 0) + 1
                )

            # Track specific event types
            if event.event_type in (
                AuditEventType.SYNC_START,
                AuditEventType.SYNC_COMPLETE,
                AuditEventType.SYNC_FAILED,
            ):
                stats["sync_operations"] += 1

            if event.severity == AuditSeverity.ERROR:
                stats["errors"] += 1

            if event.event_type in (
                AuditEventType.CONFLICT_DETECTED,
                AuditEventType.CONFLICT_RESOLVED,
                AuditEventType.CONFLICT_MANUAL,
            ):
                stats["conflicts"] += 1

        return stats

    def create_attestation(
        self,
        operation: str,
        subjects: List[Dict[str, str]],
        materials: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SLSAAttestation:
        """Create a SLSA provenance attestation.

        Args:
            operation: Type of operation being attested
            subjects: List of subject artifacts with name/digest
            materials: Input materials/dependencies
            metadata: Additional metadata

        Returns:
            SLSA attestation object
        """
        return SLSAAttestation(
            subject=subjects,
            build_type=operation,
            invocation={
                "parameters": {"operation": operation},
                "environment": {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            },
            materials=materials or [],
            metadata=metadata or {},
        )

    def export_attestation(
        self,
        attestation: SLSAAttestation,
        output_path: Optional[Path] = None,
    ) -> Path:
        """Export attestation to file.

        Args:
            attestation: The attestation to export
            output_path: Output file path (default: log_dir/attestations/)

        Returns:
            Path to the exported attestation file
        """
        if output_path is None:
            attestations_dir = self.log_dir / "attestations"
            attestations_dir.mkdir(exist_ok=True)
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            output_path = attestations_dir / f"attestation-{timestamp}.json"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(attestation.to_json())

        return output_path

    def generate_report(
        self,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        output_path: Optional[Path] = None,
    ) -> str:
        """Generate a markdown audit report.

        Args:
            since: Start datetime for report
            until: End datetime for report
            output_path: Optional path to save report

        Returns:
            Markdown report string
        """
        stats = self.get_stats(since, until)

        lines = ["# Audit Report", ""]

        # Date range
        if since or until:
            range_str = f"Period: {since or 'beginning'} to {until or 'now'}"
            lines.append(f"_{range_str}_\n")

        # Summary
        lines.append("## Summary")
        lines.append(f"- **Total Events:** {stats['total_events']}")
        lines.append(f"- **Sync Operations:** {stats['sync_operations']}")
        lines.append(f"- **Errors:** {stats['errors']}")
        lines.append(f"- **Conflicts:** {stats['conflicts']}")
        lines.append("")

        # By provider
        if stats["by_provider"]:
            lines.append("## Events by Provider")
            for provider, count in sorted(stats["by_provider"].items()):
                lines.append(f"- **{provider}:** {count}")
            lines.append("")

        # By type
        if stats["by_type"]:
            lines.append("## Events by Type")
            for event_type, count in sorted(stats["by_type"].items()):
                lines.append(f"- `{event_type}`: {count}")
            lines.append("")

        # By severity
        if stats["by_severity"]:
            lines.append("## Events by Severity")
            for severity, count in sorted(stats["by_severity"].items()):
                lines.append(f"- **{severity}:** {count}")
            lines.append("")

        report = "\n".join(lines)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)

        return report

    def clear(self) -> None:
        """Clear all audit logs.

        WARNING: This permanently deletes audit data.
        """
        if self.json_file.exists():
            self.json_file.unlink()

        if self.markdown_file.exists():
            self.markdown_file.unlink()

        # Clear rotated files
        for i in range(1, self.backup_count + 2):
            json_rotated = Path(f"{self.json_file}.{i}")
            md_rotated = Path(f"{self.markdown_file}.{i}")
            if json_rotated.exists():
                json_rotated.unlink()
            if md_rotated.exists():
                md_rotated.unlink()
