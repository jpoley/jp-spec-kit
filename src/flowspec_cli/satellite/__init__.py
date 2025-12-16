"""Satellite Mode - Remote provider integration for Backlog.md."""

__all__ = [
    # Enums
    "ProviderType",
    "SyncOperation",
    "SyncDirection",
    "ResolutionResult",
    # Entities
    "RemoteUser",
    "RemoteTask",
    "TaskUpdate",
    "TaskCreate",
    "RemotePullRequest",
    "TaskHistoryEntry",
    "ConnectionStatus",
    "RateLimitStatus",
    "TaskSyncOp",
    "ConflictData",
    "SyncResult",
    # Provider
    "RemoteProvider",
    # Registry
    "ProviderRegistry",
    "LazyProvider",
    "PROVIDER_PATTERNS",
    # Secrets
    "SecretManager",
    "TokenRedactionFilter",
    "ENV_VAR_NAMES",
    "TOKEN_PATTERNS",
    # Audit
    "AuditLogger",
    "AuditEvent",
    "AuditEventType",
    "AuditSeverity",
    "AuditQuery",
    "SLSAAttestation",
    "JSONFormatter",
    "MarkdownFormatter",
    # Errors
    "SatelliteError",
    "AuthenticationError",
    "TokenExpiredError",
    "SecretStorageUnavailableError",
    "InvalidTokenError",
    "TaskNotFoundError",
    "PermissionDeniedError",
    "ConflictError",
    "SyncError",
    "SyncCancelledError",
    "RateLimitError",
    "ProviderUnavailableError",
    "ProviderNotFoundError",
    "ValidationError",
    # Migration
    "TaskMigrator",
    "MigrationError",
    "migrate_tasks_cli",
    "cleanup_backups",
]

# Enums
from .enums import (
    ProviderType,
    SyncOperation,
    SyncDirection,
    ResolutionResult,
)

# Entities
from .entities import (
    RemoteUser,
    RemoteTask,
    TaskUpdate,
    TaskCreate,
    RemotePullRequest,
    TaskHistoryEntry,
    ConnectionStatus,
    RateLimitStatus,
    TaskSyncOp,
    ConflictData,
    SyncResult,
)

# Provider ABC
from .provider import RemoteProvider

# Registry
from .registry import ProviderRegistry, LazyProvider, PROVIDER_PATTERNS

# Errors
from .errors import (
    SatelliteError,
    AuthenticationError,
    TokenExpiredError,
    SecretStorageUnavailableError,
    InvalidTokenError,
    TaskNotFoundError,
    PermissionDeniedError,
    ConflictError,
    SyncError,
    SyncCancelledError,
    RateLimitError,
    ProviderUnavailableError,
    ProviderNotFoundError,
    ValidationError,
)

# Migration
from .migration import TaskMigrator, MigrationError, migrate_tasks_cli, cleanup_backups

# Secrets
from .secrets import SecretManager, TokenRedactionFilter, ENV_VAR_NAMES, TOKEN_PATTERNS

# Audit
from .audit import (
    AuditLogger,
    AuditEvent,
    AuditEventType,
    AuditSeverity,
    AuditQuery,
    SLSAAttestation,
    JSONFormatter,
    MarkdownFormatter,
)
