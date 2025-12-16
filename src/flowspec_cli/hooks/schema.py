"""Hook definition schema for flowspec hooks.

This module defines the structure and validation logic for hook definitions
in .specify/hooks/hooks.yaml. Hooks define event matchers, execution methods,
and security constraints.

Example:
    >>> hook = HookDefinition(
    ...     name="run-tests",
    ...     events=[EventMatcher(type="implement.completed")],
    ...     script="run-tests.sh",
    ...     timeout=300,
    ...     fail_mode="stop"
    ... )
    >>> hook.is_enabled()
    True
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatch
from typing import Any

from .events import Event


@dataclass
class EventMatcher:
    """Event matcher for hook triggering.

    Matches events by type (with wildcard support) and optional filters
    on event context fields. Multiple matchers use OR semantics.

    Attributes:
        type: Event type pattern (supports * wildcards)
        filter: Optional filters on event context fields

    Example:
        >>> # Simple match
        >>> matcher = EventMatcher(type="spec.created")
        >>> matcher.matches(Event(event_type="spec.created", project_root="/tmp"))
        True

        >>> # Wildcard match
        >>> matcher = EventMatcher(type="task.*")
        >>> matcher.matches(Event(event_type="task.completed", project_root="/tmp"))
        True

        >>> # Filtered match
        >>> matcher = EventMatcher(
        ...     type="task.completed",
        ...     filter={"priority": ["high", "critical"]}
        ... )
    """

    type: str
    filter: dict[str, Any] | None = None

    def matches(self, event: Event) -> bool:
        """Check if event matches this matcher.

        Args:
            event: Event to check.

        Returns:
            True if event matches type pattern and all filters.

        Example:
            >>> matcher = EventMatcher(type="task.*")
            >>> event = Event(event_type="task.completed", project_root="/tmp")
            >>> matcher.matches(event)
            True
        """
        # Match event type (supports wildcards)
        if not fnmatch(event.event_type, self.type):
            return False

        # Match filters if present
        if self.filter is not None:
            if not self._match_filters(event):
                return False

        return True

    def _match_filters(self, event: Event) -> bool:
        """Match event against filters.

        Args:
            event: Event to check.

        Returns:
            True if all filters match.
        """
        if self.filter is None:
            return True

        event_context = event.context or {}

        for filter_field, expected_value in self.filter.items():
            # Handle special filter types
            if filter_field.endswith("_any"):
                # labels_any: At least one label matches
                base_field = filter_field[:-4]  # Remove "_any"
                actual_labels = event_context.get(base_field, [])
                if not isinstance(actual_labels, list):
                    return False
                if not any(label in expected_value for label in actual_labels):
                    return False

            elif filter_field.endswith("_all"):
                # labels_all: All expected labels present
                base_field = filter_field[:-4]  # Remove "_all"
                actual_labels = event_context.get(base_field, [])
                if not isinstance(actual_labels, list):
                    return False
                if not all(label in actual_labels for label in expected_value):
                    return False

            elif isinstance(expected_value, list):
                # Array match (OR): actual must be one of expected
                actual_value = event_context.get(filter_field)
                if actual_value not in expected_value:
                    return False

            else:
                # Exact match
                actual_value = event_context.get(filter_field)
                if actual_value != expected_value:
                    return False

        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert matcher to dictionary.

        Returns:
            Dictionary representation.
        """
        result: dict[str, Any] = {"type": self.type}
        if self.filter is not None:
            result["filter"] = self.filter
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EventMatcher:
        """Create matcher from dictionary.

        Args:
            data: Dictionary with matcher fields.

        Returns:
            EventMatcher instance.
        """
        return cls(
            type=data["type"],
            filter=data.get("filter"),
        )


@dataclass
class HookDefinition:
    """Hook definition with execution method and constraints.

    A hook defines:
    - Event matchers: What events trigger this hook
    - Execution method: How to run (script, command, or webhook)
    - Security constraints: Timeout, working directory, environment
    - Error handling: Fail mode (continue or stop)

    Attributes:
        name: Unique hook identifier
        events: List of event matchers (OR semantics)
        script: Path to executable script (relative to .specify/hooks/)
        command: Inline shell command
        webhook: Webhook configuration (v2 feature)
        description: Human-readable description
        timeout: Maximum execution time in seconds (default: 30)
        working_directory: Working directory for execution (default: ".")
        shell: Shell to use for command execution (default: "/bin/bash")
        env: Environment variables
        fail_mode: Error handling mode ("continue" or "stop")
        enabled: Whether hook is enabled (default: True)

    Example:
        >>> hook = HookDefinition(
        ...     name="run-tests",
        ...     events=[EventMatcher(type="implement.completed")],
        ...     script="run-tests.sh",
        ...     timeout=300,
        ...     fail_mode="stop"
        ... )
    """

    name: str
    events: list[EventMatcher]
    script: str | None = None
    command: str | None = None
    webhook: dict[str, Any] | None = None
    description: str | None = None
    timeout: int = 30
    working_directory: str = "."
    shell: str = "/bin/bash"
    env: dict[str, str] = field(default_factory=dict)
    fail_mode: str = "continue"  # "continue" or "stop"
    enabled: bool = True

    def is_enabled(self) -> bool:
        """Check if hook is enabled.

        Returns:
            True if enabled.
        """
        return self.enabled

    def matches_event(self, event: Event) -> bool:
        """Check if any event matcher matches the event.

        Args:
            event: Event to check.

        Returns:
            True if at least one matcher matches (OR semantics).

        Example:
            >>> hook = HookDefinition(
            ...     name="test",
            ...     events=[
            ...         EventMatcher(type="spec.created"),
            ...         EventMatcher(type="spec.updated"),
            ...     ]
            ... )
            >>> hook.matches_event(Event(event_type="spec.created", project_root="/tmp"))
            True
        """
        return any(matcher.matches(event) for matcher in self.events)

    def get_execution_method(self) -> tuple[str, str | dict[str, Any]]:
        """Get execution method and value.

        Returns:
            Tuple of (method_type, value) where method_type is one of
            "script", "command", or "webhook".

        Raises:
            ValueError: If no execution method is defined.

        Example:
            >>> hook = HookDefinition(name="test", events=[], script="test.sh")
            >>> hook.get_execution_method()
            ('script', 'test.sh')
        """
        if self.script is not None:
            return ("script", self.script)
        if self.command is not None:
            return ("command", self.command)
        if self.webhook is not None:
            return ("webhook", self.webhook)
        raise ValueError(f"Hook '{self.name}' has no execution method defined")

    def to_dict(self) -> dict[str, Any]:
        """Convert hook to dictionary.

        Returns:
            Dictionary representation.
        """
        result: dict[str, Any] = {
            "name": self.name,
            "events": [m.to_dict() for m in self.events],
            "timeout": self.timeout,
            "working_directory": self.working_directory,
            "shell": self.shell,
            "env": self.env,
            "fail_mode": self.fail_mode,
            "enabled": self.enabled,
        }

        # Add execution method
        if self.script is not None:
            result["script"] = self.script
        if self.command is not None:
            result["command"] = self.command
        if self.webhook is not None:
            result["webhook"] = self.webhook

        # Add optional fields
        if self.description is not None:
            result["description"] = self.description

        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HookDefinition:
        """Create hook from dictionary.

        Args:
            data: Dictionary with hook fields.

        Returns:
            HookDefinition instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If no execution method is defined.
        """
        # Parse event matchers
        events = [EventMatcher.from_dict(m) for m in data["events"]]

        # Verify at least one execution method
        has_execution = any(key in data for key in ["script", "command", "webhook"])
        if not has_execution:
            raise ValueError(
                f"Hook '{data.get('name', 'unknown')}' must have at least one "
                "execution method (script, command, or webhook)"
            )

        return cls(
            name=data["name"],
            events=events,
            script=data.get("script"),
            command=data.get("command"),
            webhook=data.get("webhook"),
            description=data.get("description"),
            timeout=data.get("timeout", 30),
            working_directory=data.get("working_directory", "."),
            shell=data.get("shell", "/bin/bash"),
            env=data.get("env", {}),
            fail_mode=data.get("fail_mode", "continue"),
            enabled=data.get("enabled", True),
        )


@dataclass
class HooksConfig:
    """Complete hooks configuration.

    Contains version, defaults, and all hook definitions.

    Attributes:
        version: Configuration schema version
        defaults: Default values applied to all hooks
        hooks: List of hook definitions

    Example:
        >>> config = HooksConfig(
        ...     version="1.0",
        ...     defaults={"timeout": 30, "fail_mode": "continue"},
        ...     hooks=[
        ...         HookDefinition(
        ...             name="run-tests",
        ...             events=[EventMatcher(type="implement.completed")],
        ...             script="run-tests.sh",
        ...         )
        ...     ]
        ... )
    """

    version: str
    hooks: list[HookDefinition]
    defaults: dict[str, Any] = field(default_factory=dict)

    def get_matching_hooks(self, event: Event) -> list[HookDefinition]:
        """Get all enabled hooks that match an event.

        Args:
            event: Event to match.

        Returns:
            List of matching hook definitions.

        Example:
            >>> config = HooksConfig(version="1.0", hooks=[...])
            >>> event = Event(event_type="spec.created", project_root="/tmp")
            >>> matching = config.get_matching_hooks(event)
        """
        return [
            hook
            for hook in self.hooks
            if hook.is_enabled() and hook.matches_event(event)
        ]

    def get_hook_by_name(self, name: str) -> HookDefinition | None:
        """Get hook by name.

        Args:
            name: Hook name.

        Returns:
            Hook definition or None if not found.
        """
        for hook in self.hooks:
            if hook.name == name:
                return hook
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary.

        Returns:
            Dictionary representation.
        """
        result: dict[str, Any] = {
            "version": self.version,
            "hooks": [h.to_dict() for h in self.hooks],
        }
        if self.defaults:
            result["defaults"] = self.defaults
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HooksConfig:
        """Create config from dictionary.

        Args:
            data: Dictionary with config fields.

        Returns:
            HooksConfig instance.

        Raises:
            KeyError: If required fields are missing.
        """
        # Get defaults
        defaults = data.get("defaults", {})

        # Parse hooks with defaults applied
        hooks = []
        for hook_data in data.get("hooks", []):
            # Merge defaults with hook-specific config
            merged = {**defaults, **hook_data}
            hooks.append(HookDefinition.from_dict(merged))

        return cls(
            version=data["version"],
            hooks=hooks,
            defaults=defaults,
        )

    @classmethod
    def empty(cls) -> HooksConfig:
        """Create empty configuration.

        Returns:
            Empty HooksConfig with no hooks.
        """
        return cls(version="1.0", hooks=[], defaults={})


# JSON Schema for hooks.yaml validation
HOOKS_CONFIG_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Flowspec Hooks Configuration",
    "type": "object",
    "required": ["version", "hooks"],
    "properties": {
        "version": {
            "type": "string",
            "pattern": r"^\d+\.\d+$",
            "description": "Configuration schema version",
        },
        "defaults": {
            "type": "object",
            "properties": {
                "timeout": {"type": "integer", "minimum": 1, "maximum": 600},
                "working_directory": {"type": "string"},
                "shell": {"type": "string"},
                "fail_mode": {"type": "string", "enum": ["continue", "stop"]},
                "enabled": {"type": "boolean"},
            },
        },
        "hooks": {
            "type": "array",
            "minItems": 0,
            "items": {
                "type": "object",
                "required": ["name", "events"],
                "oneOf": [
                    {"required": ["script"]},
                    {"required": ["command"]},
                    {"required": ["webhook"]},
                ],
                "properties": {
                    "name": {
                        "type": "string",
                        "pattern": "^[a-z0-9-]+$",
                        "description": "Unique hook identifier",
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 500,
                    },
                    "events": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["type"],
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "pattern": "^[a-z*]+\\.[a-z_*]+$",
                                },
                                "filter": {
                                    "type": "object",
                                    "additionalProperties": True,
                                },
                            },
                        },
                    },
                    "script": {"type": "string"},
                    "command": {"type": "string"},
                    "webhook": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "format": "uri"},
                            "method": {
                                "type": "string",
                                "enum": ["GET", "POST", "PUT"],
                            },
                            "headers": {"type": "object"},
                        },
                    },
                    "timeout": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 600,
                    },
                    "working_directory": {"type": "string"},
                    "shell": {"type": "string"},
                    "env": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                    },
                    "fail_mode": {
                        "type": "string",
                        "enum": ["continue", "stop"],
                    },
                    "enabled": {"type": "boolean"},
                },
            },
        },
    },
}
