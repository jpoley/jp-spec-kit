"""Exception hierarchy for Satellite Mode operations."""

from typing import Any, Dict, List, Optional


class SatelliteError(Exception):
    """Base exception for all Satellite Mode errors."""

    def __init__(
        self, message: str, code: str, details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a SatelliteError.

        Args:
            message: Human-readable error description
            code: Machine-readable error code
            details: Additional context for debugging
        """
        super().__init__(message)
        self.code = code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize error for logging or API response."""
        return {
            "error": self.__class__.__name__,
            "code": self.code,
            "message": str(self),
            "details": self.details,
        }


# === Authentication Errors ===


class AuthenticationError(SatelliteError):
    """Token is invalid or expired."""

    def __init__(self, provider: str, reason: str):
        super().__init__(
            f"Authentication failed for {provider}: {reason}",
            code="AUTH_FAILED",
            details={"provider": provider, "reason": reason},
        )


class TokenExpiredError(AuthenticationError):
    """Token has expired and needs refresh."""

    def __init__(self, provider: str):
        super().__init__(provider, "Token expired")
        self.code = "TOKEN_EXPIRED"


class SecretStorageUnavailableError(SatelliteError):
    """System keychain or secret storage is not available."""

    def __init__(self, message: str):
        super().__init__(message, code="SECRET_STORAGE_UNAVAILABLE")


class InvalidTokenError(SatelliteError):
    """Token validation failed."""

    def __init__(self, provider: str):
        super().__init__(
            f"Invalid token for {provider}",
            code="INVALID_TOKEN",
            details={"provider": provider},
        )


# === Resource Errors ===


class TaskNotFoundError(SatelliteError):
    """Task does not exist on remote."""

    def __init__(self, task_id: str, provider: str):
        super().__init__(
            f"Task {task_id} not found on {provider}",
            code="TASK_NOT_FOUND",
            details={"task_id": task_id, "provider": provider},
        )


class PermissionDeniedError(SatelliteError):
    """User lacks permission for operation."""

    def __init__(self, operation: str, resource: str):
        super().__init__(
            f"Permission denied: cannot {operation} {resource}",
            code="PERMISSION_DENIED",
            details={"operation": operation, "resource": resource},
        )


# === Sync Errors ===


class ConflictError(SatelliteError):
    """Conflict between local and remote versions."""

    def __init__(self, task_id: str, field: str, local_value: Any, remote_value: Any):
        super().__init__(
            f"Conflict detected for task {task_id} on field {field}",
            code="CONFLICT",
            details={
                "task_id": task_id,
                "field": field,
                "local_value": str(local_value),
                "remote_value": str(remote_value),
            },
        )


class SyncError(SatelliteError):
    """General sync operation failure."""

    def __init__(self, message: str, failed_tasks: List[str]):
        super().__init__(
            message, code="SYNC_FAILED", details={"failed_tasks": failed_tasks}
        )


class SyncCancelledError(SatelliteError):
    """User cancelled the sync operation."""

    def __init__(self, reason: str = "User cancelled"):
        super().__init__(reason, code="SYNC_CANCELLED")


# === Provider Errors ===


class RateLimitError(SatelliteError):
    """Rate limit exceeded."""

    def __init__(self, provider: str, retry_after: int):
        super().__init__(
            f"Rate limit exceeded for {provider}. Retry after {retry_after}s",
            code="RATE_LIMITED",
            details={"provider": provider, "retry_after": retry_after},
        )
        self.retry_after = retry_after


class ProviderUnavailableError(SatelliteError):
    """Provider API is unavailable."""

    def __init__(self, provider: str, status_code: Optional[int] = None):
        super().__init__(
            f"Provider {provider} is unavailable",
            code="PROVIDER_UNAVAILABLE",
            details={"provider": provider, "status_code": status_code},
        )


class ProviderNotFoundError(SatelliteError):
    """Unknown provider type requested."""

    def __init__(self, provider: str):
        super().__init__(
            f"Unknown provider: {provider}",
            code="PROVIDER_NOT_FOUND",
            details={"provider": provider},
        )


# === Validation Errors ===


class ValidationError(SatelliteError):
    """Input validation failed."""

    def __init__(self, field: str, reason: str):
        super().__init__(
            f"Validation failed for {field}: {reason}",
            code="VALIDATION_ERROR",
            details={"field": field, "reason": reason},
        )
