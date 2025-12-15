"""Event schema validation for v1.1.0 events.

Provides runtime validation against JSON Schema for event emission.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator, ValidationError


class EventValidator:
    """Runtime validator for v1.1.0 events.

    Uses JSON Schema draft-07 validation with cached schema loading.

    Example:
        >>> event = {
        ...     "version": "1.1.0",
        ...     "event_type": "lifecycle.started",
        ...     "timestamp": "2025-12-15T00:00:00Z",
        ...     "agent_id": "@backend-engineer"
        ... }
        >>> is_valid, errors = EventValidator.validate(event)
        >>> assert is_valid
    """

    _validator: Draft7Validator | None = None

    @classmethod
    def _get_schema_path(cls) -> Path:
        """Get path to schema file.

        Returns:
            Path to event-v1.1.0.json schema file.
        """
        return (
            Path(__file__).parent.parent.parent.parent
            / "schemas"
            / "events"
            / "event-v1.1.0.json"
        )

    @classmethod
    @lru_cache(maxsize=1)
    def _load_schema(cls) -> dict[str, Any]:
        """Load schema once and cache.

        Returns:
            Parsed JSON schema dictionary.

        Raises:
            FileNotFoundError: If schema file does not exist.
        """
        schema_path = cls._get_schema_path()
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")
        return json.loads(schema_path.read_text())

    @classmethod
    def _get_validator(cls) -> Draft7Validator:
        """Get or create validator instance.

        Returns:
            Cached Draft7Validator instance.
        """
        if cls._validator is None:
            schema = cls._load_schema()
            cls._validator = Draft7Validator(schema)
        return cls._validator

    @classmethod
    def validate(cls, event: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate event against schema.

        Args:
            event: Event dictionary to validate.

        Returns:
            Tuple of (is_valid, error_messages).
            If valid, error_messages is empty list.

        Example:
            >>> event = {"version": "1.1.0", "event_type": "lifecycle.started"}
            >>> is_valid, errors = EventValidator.validate(event)
            >>> if not is_valid:
            ...     print("Errors:", errors)
        """
        validator = cls._get_validator()
        errors = list(validator.iter_errors(event))

        if not errors:
            return True, []

        error_messages = []
        for error in errors:
            path = (
                ".".join(str(p) for p in error.absolute_path)
                if error.absolute_path
                else "$"
            )
            error_messages.append(f"{path}: {error.message}")

        return False, error_messages

    @classmethod
    def is_valid(cls, event: dict[str, Any]) -> bool:
        """Check if event is valid (simple boolean check).

        Args:
            event: Event dictionary to validate.

        Returns:
            True if valid, False otherwise.

        Example:
            >>> event = {
            ...     "version": "1.1.0",
            ...     "event_type": "lifecycle.started",
            ...     "timestamp": "2025-12-15T00:00:00Z",
            ...     "agent_id": "@test"
            ... }
            >>> assert EventValidator.is_valid(event)
        """
        is_valid, _ = cls.validate(event)
        return is_valid

    @classmethod
    def validate_or_raise(cls, event: dict[str, Any]) -> None:
        """Validate event and raise on failure.

        Args:
            event: Event dictionary to validate.

        Raises:
            ValidationError: If event is invalid.

        Example:
            >>> try:
            ...     EventValidator.validate_or_raise({"bad": "event"})
            ... except ValidationError as e:
            ...     print("Validation failed:", e)
        """
        is_valid, errors = cls.validate(event)
        if not is_valid:
            raise ValidationError(f"Event validation failed: {'; '.join(errors)}")
