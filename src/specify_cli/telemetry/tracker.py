"""Telemetry event tracking with PII protection.

This module provides functions for tracking telemetry events
while ensuring sensitive data (PII) is properly hashed.
"""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Any

from .events import RoleEvent, TelemetryEvent
from .writer import TelemetryWriter

# Default telemetry file location
DEFAULT_TELEMETRY_DIR = ".flowspec"
DEFAULT_TELEMETRY_FILE = "telemetry.jsonl"

# PII patterns to detect and hash
PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "username": re.compile(r"@[a-zA-Z0-9_-]+"),
    "home_path": re.compile(r"/(?:home|Users)/[^/\s]+"),
}

# Singleton writer instance
_writer: TelemetryWriter | None = None


def _get_writer(project_root: Path | None = None) -> TelemetryWriter:
    """Get or create the telemetry writer singleton."""
    global _writer
    if _writer is None:
        if project_root is None:
            project_root = Path.cwd()
        telemetry_path = project_root / DEFAULT_TELEMETRY_DIR / DEFAULT_TELEMETRY_FILE
        _writer = TelemetryWriter(telemetry_path)
    return _writer


def hash_pii(value: str, salt: str = "") -> str:
    """Hash a PII value using SHA-256.

    Args:
        value: The value to hash
        salt: Optional salt for additional security

    Returns:
        First 12 characters of the SHA-256 hash (sufficient for anonymization)
    """
    combined = f"{salt}{value}".encode("utf-8")
    return hashlib.sha256(combined).hexdigest()[:12]


def sanitize_path(path: str | Path) -> str:
    """Sanitize a file path by hashing user-specific parts.

    Converts paths like /home/jpoley/project to /home/<hash>/project

    Args:
        path: The path to sanitize

    Returns:
        Sanitized path string
    """
    path_str = str(path)

    # Hash home directory usernames
    match = PII_PATTERNS["home_path"].search(path_str)
    if match:
        home_path = match.group()
        parts = home_path.split("/")
        if len(parts) >= 3:
            username = parts[2]
            hashed = hash_pii(username)
            path_str = path_str.replace(f"/{username}/", f"/<{hashed}>/")

    return path_str


def sanitize_value(value: Any, field_name: str = "") -> Any:
    """Sanitize a value, hashing any detected PII.

    Args:
        value: The value to sanitize
        field_name: Hint about the field type

    Returns:
        Sanitized value
    """
    if value is None:
        return None

    if isinstance(value, dict):
        return {k: sanitize_value(v, k) for k, v in value.items()}

    if isinstance(value, list):
        return [sanitize_value(item, field_name) for item in value]

    if isinstance(value, (Path, str)):
        value_str = str(value)

        # Check if it looks like a path
        if "/" in value_str or "\\" in value_str:
            return sanitize_path(value_str)

        # Check for email
        if PII_PATTERNS["email"].search(value_str):
            return PII_PATTERNS["email"].sub(
                lambda m: f"<email:{hash_pii(m.group())}>", value_str
            )

        # Check for username
        if PII_PATTERNS["username"].search(value_str):
            return PII_PATTERNS["username"].sub(
                lambda m: f"@<{hash_pii(m.group())}>", value_str
            )

        # Hash project names if field suggests it
        if field_name.lower() in ("project", "project_name", "repo", "repository"):
            return f"<project:{hash_pii(value_str)}>"

        return value_str

    return value


def track_role_event(
    event_type: RoleEvent | str,
    *,
    role: str | None = None,
    command: str | None = None,
    agent: str | None = None,
    context: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    project_root: Path | None = None,
    enabled: bool = True,
) -> TelemetryEvent | None:
    """Track a telemetry event with PII protection.

    This function creates a telemetry event, sanitizes any PII,
    and writes it to the telemetry log.

    Args:
        event_type: The type of event to track
        role: The user's current role (e.g., dev, pm, qa)
        command: The command that triggered the event
        agent: The agent involved (if applicable)
        context: Additional context data (will be sanitized)
        metadata: Extra metadata (will be sanitized)
        project_root: Project root directory (for telemetry file location)
        enabled: Whether telemetry is enabled (default: True)

    Returns:
        The created TelemetryEvent if telemetry is enabled, None otherwise

    Example:
        >>> track_role_event(
        ...     RoleEvent.ROLE_SELECTED,
        ...     role="dev",
        ...     command="/flow:implement",
        ...     context={"project": "my-secret-project"}
        ... )
    """
    if not enabled:
        return None

    # Check environment variable for telemetry opt-out
    if os.environ.get("FLOWSPEC_TELEMETRY_DISABLED", "").lower() in (
        "1",
        "true",
        "yes",
    ):
        return None

    # Sanitize context and metadata
    sanitized_context = sanitize_value(context) if context else {}
    sanitized_metadata = sanitize_value(metadata) if metadata else {}

    # Add system metadata
    sanitized_metadata["hostname_hash"] = hash_pii(
        os.environ.get("HOSTNAME", "unknown")
    )

    # Create the event
    event = TelemetryEvent.create(
        event_type=event_type,
        role=role,
        command=command,
        agent=agent,
        context=sanitized_context,
        metadata=sanitized_metadata,
    )

    # Write the event
    writer = _get_writer(project_root)
    writer.write_event(event)

    return event


def reset_writer() -> None:
    """Reset the telemetry writer singleton (useful for testing)."""
    global _writer
    _writer = None


__all__ = [
    "track_role_event",
    "hash_pii",
    "sanitize_path",
    "sanitize_value",
    "reset_writer",
]
