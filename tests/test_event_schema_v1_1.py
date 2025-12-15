"""Test suite for Event Schema v1.1.0.

Validates:
1. Schema file structure and validity
2. Sample events from specification
3. Namespace coverage (11 namespaces)
4. Required field enforcement
5. Optional object validation
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft7Validator

SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "events" / "event-v1.1.0.json"
FIXTURES_PATH = Path(__file__).parent / "fixtures" / "sample_events_v1_1.jsonl"


@pytest.fixture
def schema() -> dict:
    """Load event schema v1.1.0."""
    return json.loads(SCHEMA_PATH.read_text())


@pytest.fixture
def validator(schema: dict) -> Draft7Validator:
    """Create JSON Schema validator."""
    return Draft7Validator(schema)


@pytest.fixture
def sample_events() -> list[dict]:
    """Load all sample events from fixture."""
    if not FIXTURES_PATH.exists():
        pytest.skip(f"Fixtures not found: {FIXTURES_PATH}")

    events = []
    with FIXTURES_PATH.open() as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return events


class TestSchemaStructure:
    """Test schema file structure and metadata."""

    def test_schema_exists(self) -> None:
        """Schema file exists at expected location."""
        assert SCHEMA_PATH.exists(), f"Schema not found: {SCHEMA_PATH}"

    def test_schema_is_valid_json(self, schema: dict) -> None:
        """Schema is valid JSON."""
        assert isinstance(schema, dict)

    def test_schema_metadata(self, schema: dict) -> None:
        """Schema has required metadata fields."""
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert "$id" in schema
        assert "flowspec" in schema["$id"]
        assert schema["title"] == "Agent Event"
        assert "description" in schema

    def test_required_fields(self, schema: dict) -> None:
        """Schema enforces required fields."""
        required = set(schema["required"])
        expected = {"version", "event_type", "timestamp", "agent_id"}
        assert required == expected

    def test_namespace_pattern(self, schema: dict) -> None:
        """event_type pattern matches 11 namespaces."""
        pattern = schema["properties"]["event_type"]["pattern"]
        expected_namespaces = [
            "lifecycle",
            "activity",
            "coordination",
            "hook",
            "git",
            "task",
            "container",
            "decision",
            "system",
            "action",
            "security",
        ]
        for ns in expected_namespaces:
            assert ns in pattern, f"Namespace {ns} not in pattern"

    def test_additional_properties_disabled(self, schema: dict) -> None:
        """Schema rejects unknown fields at root level."""
        assert schema.get("additionalProperties") is False


class TestRequiredFields:
    """Test required field validation."""

    def test_valid_minimal_event(self, validator: Draft7Validator) -> None:
        """Valid event with only required fields passes."""
        event = {
            "version": "1.1.0",
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test-agent",
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) == 0

    def test_missing_version(self, validator: Draft7Validator) -> None:
        """Event without version fails validation."""
        event = {
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) > 0
        assert any("version" in str(e.message) for e in errors)

    def test_missing_event_type(self, validator: Draft7Validator) -> None:
        """Event without event_type fails validation."""
        event = {
            "version": "1.1.0",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) > 0

    def test_invalid_event_type_pattern(self, validator: Draft7Validator) -> None:
        """Invalid event_type format fails validation."""
        event = {
            "version": "1.1.0",
            "event_type": "invalid-format",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) > 0

    def test_invalid_version_format(self, validator: Draft7Validator) -> None:
        """Invalid version format fails validation."""
        event = {
            "version": "1.1",  # Missing patch version
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) > 0

    def test_unknown_field_rejected(self, validator: Draft7Validator) -> None:
        """Unknown fields are rejected due to additionalProperties: false."""
        event = {
            "version": "1.1.0",
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
            "unknown_field": "should fail",
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) > 0
        assert any("additional" in str(e.message).lower() for e in errors)


class TestNamespaceObjects:
    """Test namespace-specific object validation."""

    def test_git_object(self, validator: Draft7Validator) -> None:
        """Git object with valid fields passes."""
        event = {
            "version": "1.1.0",
            "event_type": "git.commit",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@backend-engineer",
            "git": {
                "operation": "commit",
                "sha": "abc123def456",
                "branch_name": "main",
                "files_changed": 5,
            },
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) == 0

    def test_git_sha_too_short(self, validator: Draft7Validator) -> None:
        """Git SHA shorter than 7 chars fails."""
        event = {
            "version": "1.1.0",
            "event_type": "git.commit",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@backend-engineer",
            "git": {"sha": "abc"},
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) > 0

    def test_task_object(self, validator: Draft7Validator) -> None:
        """Task object with valid fields passes."""
        event = {
            "version": "1.1.0",
            "event_type": "task.state_changed",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@orchestrator",
            "task": {
                "task_id": "task-485",
                "title": "Implement schema",
                "from_state": "Planned",
                "to_state": "In Implementation",
            },
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) == 0

    def test_decision_object(self, validator: Draft7Validator) -> None:
        """Decision object with reversibility passes."""
        event = {
            "version": "1.1.0",
            "event_type": "decision.made",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@architect",
            "decision": {
                "decision_id": "ARCH-001",
                "category": "architecture",
                "reversibility": {"type": "two-way-door", "reversal_cost": "low"},
            },
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) == 0

    def test_decision_invalid_reversibility_type(
        self, validator: Draft7Validator
    ) -> None:
        """Invalid reversibility type fails validation."""
        event = {
            "version": "1.1.0",
            "event_type": "decision.made",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@architect",
            "decision": {
                "reversibility": {"type": "three-way-door"}  # Invalid
            },
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) > 0

    def test_container_object(self, validator: Draft7Validator) -> None:
        """Container object with resource limits passes."""
        event = {
            "version": "1.1.0",
            "event_type": "container.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "system",
            "container": {
                "container_id": "abc123",
                "image": "flowspec-agents:latest",
                "resource_limits": {"memory_mb": 2048, "cpu_cores": 2},
            },
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) == 0

    def test_action_object(self, validator: Draft7Validator) -> None:
        """Action object with error passes."""
        event = {
            "version": "1.1.0",
            "event_type": "action.failed",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@backend-engineer",
            "action": {
                "verb": "validate",
                "duration_ms": 5000,
                "error": {"code": "VALIDATION_FAILED", "message": "Schema failed"},
            },
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) == 0

    def test_security_object(self, validator: Draft7Validator) -> None:
        """Security object with artifact and signature passes."""
        event = {
            "version": "1.1.0",
            "event_type": "security.artifact_signed",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "system",
            "security": {
                "artifact": {"type": "container", "ref": "ghcr.io/org/app:v1.0.0"},
                "signature": {
                    "algorithm": "cosign",
                    "key_id": "KEY-001",
                    "signature_ref": "sig-abc123",
                },
                "attestation": {"type": "in-toto", "predicate": "slsa.v1"},
            },
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) == 0


class TestBackwardCompatibility:
    """Test backward compatibility with v1.0."""

    def test_status_field_allowed(self, validator: Draft7Validator) -> None:
        """Legacy status field is allowed."""
        event = {
            "version": "1.1.0",
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
            "status": "started",
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) == 0

    def test_invalid_status_rejected(self, validator: Draft7Validator) -> None:
        """Invalid status enum value fails validation."""
        event = {
            "version": "1.1.0",
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
            "status": "invalid_status",
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) > 0


class TestContextObject:
    """Test context object for cross-referencing."""

    def test_context_with_all_fields(self, validator: Draft7Validator) -> None:
        """Context with all fields passes."""
        event = {
            "version": "1.1.0",
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
            "context": {
                "task_id": "task-123",
                "branch_name": "task-123-feature",
                "worktree_path": "/worktrees/task-123",
                "container_id": "abc123",
                "pr_number": 456,
                "decision_id": "ARCH-001",
            },
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) == 0

    def test_context_pr_number_must_be_positive(
        self, validator: Draft7Validator
    ) -> None:
        """Context pr_number must be >= 1."""
        event = {
            "version": "1.1.0",
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
            "context": {"pr_number": 0},
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) > 0


class TestSampleEvents:
    """Test sample events from specification."""

    def test_fixture_exists(self) -> None:
        """Sample events fixture exists."""
        assert FIXTURES_PATH.exists(), f"Fixtures not found: {FIXTURES_PATH}"

    def test_all_events_valid(
        self, validator: Draft7Validator, sample_events: list[dict]
    ) -> None:
        """All sample events pass schema validation."""
        invalid_events = []

        for i, event in enumerate(sample_events, 1):
            errors = list(validator.iter_errors(event))
            if errors:
                invalid_events.append(
                    {
                        "index": i,
                        "event_type": event.get("event_type", "unknown"),
                        "errors": [e.message for e in errors],
                    }
                )

        if invalid_events:
            for inv in invalid_events:
                print(f"Event {inv['index']} ({inv['event_type']}): {inv['errors']}")

        assert len(invalid_events) == 0, (
            f"{len(invalid_events)} events failed validation"
        )

    def test_namespace_coverage(self, sample_events: list[dict]) -> None:
        """All 11 namespaces represented in samples."""
        namespaces = set()
        for event in sample_events:
            event_type = event.get("event_type", "")
            if "." in event_type:
                namespace = event_type.split(".")[0]
                namespaces.add(namespace)

        expected = {
            "lifecycle",
            "activity",
            "coordination",
            "hook",
            "git",
            "task",
            "container",
            "decision",
            "system",
            "action",
            "security",
        }

        missing = expected - namespaces
        assert len(missing) == 0, f"Missing namespaces: {missing}"

    def test_minimum_event_count(self, sample_events: list[dict]) -> None:
        """At least 30 sample events extracted."""
        assert len(sample_events) >= 30, f"Only {len(sample_events)} events found"


class TestEventValidator:
    """Test EventValidator class."""

    def test_validator_import(self) -> None:
        """EventValidator can be imported."""
        from specify_cli.hooks.validators import EventValidator

        assert EventValidator is not None

    def test_validate_valid_event(self) -> None:
        """Validator accepts valid event."""
        from specify_cli.hooks.validators import EventValidator

        event = {
            "version": "1.1.0",
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
        }

        is_valid, errors = EventValidator.validate(event)
        assert is_valid
        assert len(errors) == 0

    def test_validate_invalid_event(self) -> None:
        """Validator rejects invalid event."""
        from specify_cli.hooks.validators import EventValidator

        event = {
            "version": "1.1.0",
            # Missing event_type
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
        }

        is_valid, errors = EventValidator.validate(event)
        assert not is_valid
        assert len(errors) > 0

    def test_is_valid_helper(self) -> None:
        """is_valid helper returns boolean."""
        from specify_cli.hooks.validators import EventValidator

        valid_event = {
            "version": "1.1.0",
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
        }

        assert EventValidator.is_valid(valid_event) is True
        assert EventValidator.is_valid({}) is False

    def test_validate_or_raise_valid(self) -> None:
        """validate_or_raise does not raise for valid event."""
        from specify_cli.hooks.validators import EventValidator

        event = {
            "version": "1.1.0",
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
        }

        # Should not raise
        EventValidator.validate_or_raise(event)

    def test_validate_or_raise_invalid(self) -> None:
        """validate_or_raise raises for invalid event."""
        from jsonschema import ValidationError

        from specify_cli.hooks.validators import EventValidator

        event = {"bad": "event"}

        with pytest.raises(ValidationError):
            EventValidator.validate_or_raise(event)


class TestMessageMaxLength:
    """Test message field max length constraint."""

    def test_message_under_limit(self, validator: Draft7Validator) -> None:
        """Message under 2000 chars passes."""
        event = {
            "version": "1.1.0",
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
            "message": "x" * 2000,
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) == 0

    def test_message_over_limit(self, validator: Draft7Validator) -> None:
        """Message over 2000 chars fails."""
        event = {
            "version": "1.1.0",
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
            "message": "x" * 2001,
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) > 0
