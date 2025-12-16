"""Enumerations for the Satellite Mode sync system."""

from enum import Enum


class ProviderType(Enum):
    """Supported remote provider types."""

    GITHUB = "github"
    JIRA = "jira"
    NOTION = "notion"


class SyncOperation(Enum):
    """Type of sync operation performed on a task."""

    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    SKIPPED = "skipped"
    CONFLICT = "conflict"
    FAILED = "failed"


class SyncDirection(Enum):
    """Direction of sync operation."""

    PULL = "pull"
    PUSH = "push"
    BIDIRECTIONAL = "both"


class ResolutionResult(Enum):
    """Outcome of conflict resolution."""

    LOCAL_WINS = "local_wins"
    REMOTE_WINS = "remote_wins"
    MERGED = "merged"
    SKIP = "skip"
    USER_CANCELLED = "user_cancelled"
