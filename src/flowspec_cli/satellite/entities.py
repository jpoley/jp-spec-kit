"""Domain entities for Satellite Mode sync operations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from .enums import ProviderType, SyncOperation, SyncDirection


@dataclass
class RemoteUser:
    """User reference from remote provider."""

    id: str
    username: str
    display_name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None


@dataclass
class RemoteTask:
    """
    Domain entity representing a task from a remote provider.

    This is the canonical representation used across all providers.
    Provider-specific fields are stored in `extra_fields`.
    """

    # === Identity ===
    id: str
    provider: ProviderType
    url: str

    # === Core Fields ===
    title: str
    description: Optional[str] = None
    status: str = "To Do"

    # === Assignment ===
    assignee: Optional[RemoteUser] = None
    reporter: Optional[RemoteUser] = None

    # === Classification ===
    labels: List[str] = field(default_factory=list)
    priority: Optional[str] = None
    task_type: Optional[str] = None

    # === Hierarchy ===
    parent_id: Optional[str] = None
    subtask_ids: List[str] = field(default_factory=list)

    # === Timestamps ===
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    due_date: Optional[datetime] = None

    # === Sync Metadata ===
    etag: Optional[str] = None
    version: Optional[int] = None

    # === Provider-Specific ===
    extra_fields: Dict[str, Any] = field(default_factory=dict)
    raw_response: Optional[Dict[str, Any]] = None

    def to_local_task(self) -> Dict[str, Any]:
        """Convert to Backlog.md task format."""
        return {
            "id": f"remote-{self.provider.value}-{self.id}",
            "title": self.title,
            "description": self.description,
            "status": self._map_status_to_local(),
            "assignee": f"@{self.assignee.username}" if self.assignee else None,
            "labels": self.labels,
            "upstream": {
                "provider": self.provider.value,
                "id": self.id,
                "url": self.url,
                "synced_at": datetime.utcnow().isoformat(),
                "etag": self.etag,
            },
            "schema_version": "2",
        }

    def _map_status_to_local(self) -> str:
        """Map provider status to Backlog.md status."""
        status_map = {
            # GitHub
            "open": "To Do",
            "closed": "Done",
            # Jira (common)
            "to do": "To Do",
            "in progress": "In Progress",
            "done": "Done",
            "backlog": "To Do",
            # Notion
            "not started": "To Do",
            "complete": "Done",
        }
        return status_map.get(self.status.lower(), self.status)


@dataclass
class TaskUpdate:
    """Fields that can be updated on a remote task."""

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    assignee: Optional[str] = None
    labels: Optional[List[str]] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    extra_fields: Optional[Dict[str, Any]] = None

    def has_changes(self) -> bool:
        """Check if any fields are set."""
        return any(
            [
                self.title,
                self.description,
                self.status,
                self.assignee,
                self.labels,
                self.priority,
                self.due_date,
                self.extra_fields,
            ]
        )


@dataclass
class TaskCreate:
    """Fields required to create a new remote task."""

    title: str
    description: Optional[str] = None
    assignee: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    priority: Optional[str] = None
    parent_id: Optional[str] = None
    task_type: str = "task"
    extra_fields: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RemotePullRequest:
    """Representation of a pull request from remote provider."""

    id: str
    number: int
    url: str
    title: str
    body: Optional[str] = None
    state: str = "open"
    head_branch: str = ""
    base_branch: str = "main"
    created_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None


@dataclass
class TaskHistoryEntry:
    """Single entry in task change history."""

    timestamp: datetime
    field: str
    old_value: Any
    new_value: Any
    actor: Optional[RemoteUser] = None
    action: str = "updated"


@dataclass
class ConnectionStatus:
    """Status of provider connection test."""

    connected: bool
    latency_ms: Optional[int] = None
    user: Optional[RemoteUser] = None
    error: Optional[str] = None


@dataclass
class RateLimitStatus:
    """Current rate limit status for a provider."""

    limit: int
    remaining: int
    reset_at: Optional[datetime] = None
    resource: str = "core"


@dataclass
class TaskSyncOp:
    """Result of syncing a single task."""

    task_id: str
    remote_id: Optional[str]
    operation: SyncOperation
    changes: List[str] = field(default_factory=list)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "task_id": self.task_id,
            "remote_id": self.remote_id,
            "operation": self.operation.value,
            "changes": self.changes,
            "error": self.error,
        }


@dataclass
class ConflictData:
    """Details about a sync conflict."""

    field: str
    local_value: Any
    remote_value: Any
    local_updated: datetime
    remote_updated: datetime
    resolution: Optional[str] = None


@dataclass
class SyncResult:
    """
    Result of a sync operation.

    Captures what happened, what changed, and any issues encountered.
    Used for audit logging and user feedback.
    """

    # === Identity ===
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    direction: SyncDirection = SyncDirection.BIDIRECTIONAL

    # === Scope ===
    provider: ProviderType = ProviderType.GITHUB
    task_ids: List[str] = field(default_factory=list)

    # === Results ===
    operations: List[TaskSyncOp] = field(default_factory=list)

    # === Summary Properties ===
    @property
    def created_count(self) -> int:
        """Number of tasks created."""
        return sum(1 for op in self.operations if op.operation == SyncOperation.CREATED)

    @property
    def updated_count(self) -> int:
        """Number of tasks updated."""
        return sum(1 for op in self.operations if op.operation == SyncOperation.UPDATED)

    @property
    def conflict_count(self) -> int:
        """Number of conflicts encountered."""
        return sum(
            1 for op in self.operations if op.operation == SyncOperation.CONFLICT
        )

    @property
    def failed_count(self) -> int:
        """Number of failed operations."""
        return sum(1 for op in self.operations if op.operation == SyncOperation.FAILED)

    @property
    def skipped_count(self) -> int:
        """Number of skipped operations."""
        return sum(1 for op in self.operations if op.operation == SyncOperation.SKIPPED)

    @property
    def success(self) -> bool:
        """True if no failures or conflicts occurred."""
        return self.failed_count == 0 and self.conflict_count == 0

    def to_audit_log(self) -> Dict[str, Any]:
        """Generate audit log entry for compliance."""
        return {
            "operation_id": self.operation_id,
            "timestamp": self.timestamp.isoformat(),
            "provider": self.provider.value,
            "direction": self.direction.value,
            "summary": {
                "total": len(self.operations),
                "created": self.created_count,
                "updated": self.updated_count,
                "skipped": self.skipped_count,
                "conflicts": self.conflict_count,
                "failed": self.failed_count,
            },
            "tasks": [op.to_dict() for op in self.operations],
        }
