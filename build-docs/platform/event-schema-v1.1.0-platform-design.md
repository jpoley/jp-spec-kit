# Platform Design: Core Event Schema v1.1.0 Implementation

**Task**: task-485
**Author**: Platform Engineer
**Date**: 2025-12-15
**Schema Version**: v1.1.0
**Status**: Design Phase

---

## Executive Summary

This document provides a comprehensive platform engineering design for implementing the Event Schema v1.1.0, covering 60 event types across 11 namespaces. The implementation focuses on operational excellence, developer experience, and production-grade quality with automated validation, testing, and CI/CD integration.

**Key Deliverables**:
- JSON Schema draft-07 definition with comprehensive validation
- Runtime validation tooling (jsonschema + optional pydantic)
- Automated test suite validating 60+ sample events
- CI/CD pipeline integration with quality gates
- Migration utilities for v1.0 → v1.1.0 upgrade
- Developer documentation and type generation

---

## 1. Schema File Organization

### 1.1 Directory Structure

```
flowspec/
├── schemas/                           # JSON Schema definitions (NEW)
│   ├── events/                        # Event schema versioned directory
│   │   ├── event-v1.1.0.json         # Main schema (task-485 deliverable)
│   │   ├── event-v1.0.0.json         # Legacy schema (for reference)
│   │   └── README.md                  # Schema version history
│   ├── flowspec_workflow.schema.json  # Existing workflow schema
│   └── decision-log.schema.json       # Existing decision schema
│
├── src/specify_cli/
│   ├── hooks/
│   │   ├── events.py                  # Existing v1.0 dataclasses
│   │   ├── events_v1_1.py            # New v1.1.0 dataclasses (GENERATED)
│   │   └── validators.py             # Runtime validation (NEW)
│   │
│   └── migration/
│       ├── __init__.py
│       └── event_migration.py         # v1.0 → v1.1.0 migration (NEW)
│
├── tests/
│   ├── test_event_schema_v1_1.py      # Schema validation tests (NEW)
│   ├── test_event_migration.py        # Migration tests (NEW)
│   └── fixtures/
│       └── sample_events_v1_1.jsonl   # 60+ sample events (NEW)
│
└── scripts/
    ├── generate_types_from_schema.py  # Type generation script (NEW)
    └── validate_events.py             # Standalone validator (NEW)
```

**Rationale**:
- **`schemas/events/`**: Centralized schema management with versioning, aligns with existing `schemas/` pattern
- **Generated types**: Keep human-written (`events.py`) and generated code (`events_v1_1.py`) separate
- **Migration module**: Isolated upgrade logic for clean separation of concerns
- **Test fixtures**: JSONL format matches production event logs for realistic testing

### 1.2 Schema Versioning Strategy

```
schemas/events/
├── event-v1.1.0.json      # Current production schema
├── event-v1.0.0.json      # Legacy schema (reference)
└── event-v2.0.0.json      # Future (when breaking changes occur)
```

**Version Selection Logic**:
```python
# In events_v1_1.py
DEFAULT_SCHEMA_VERSION = "1.1.0"
SCHEMA_PATH = Path(__file__).parent.parent.parent / "schemas" / "events" / f"event-v{DEFAULT_SCHEMA_VERSION}.json"
```

---

## 2. Tool Selection & Rationale

### 2.1 Runtime Validation: `jsonschema` (Primary)

**Selected**: `jsonschema>=4.0.0` (already in `pyproject.toml`)

**Rationale**:
1. **Zero new dependencies**: Already included for workflow validation
2. **Production-ready**: Battle-tested, widely adopted in Python ecosystem
3. **Draft-07 support**: Matches schema specification requirement
4. **Performance**: Fast C-accelerated validation with `python-rapidjson` (optional)
5. **Rich error messages**: Detailed validation errors with JSONPath context

**Usage Pattern**:
```python
# src/specify_cli/hooks/validators.py
import json
from pathlib import Path
from jsonschema import Draft7Validator, ValidationError

class EventValidator:
    """Runtime validator for v1.1.0 events."""

    _schema: dict | None = None
    _validator: Draft7Validator | None = None

    @classmethod
    def load_schema(cls) -> dict:
        """Load schema once and cache."""
        if cls._schema is None:
            schema_path = Path(__file__).parent.parent.parent / "schemas" / "events" / "event-v1.1.0.json"
            cls._schema = json.loads(schema_path.read_text())
            cls._validator = Draft7Validator(cls._schema)
        return cls._schema

    @classmethod
    def validate(cls, event: dict) -> tuple[bool, list[str]]:
        """Validate event against schema.

        Returns:
            (is_valid, error_messages)
        """
        cls.load_schema()
        errors = list(cls._validator.iter_errors(event))
        if not errors:
            return True, []
        return False, [f"{e.json_path}: {e.message}" for e in errors]
```

### 2.2 Type Generation: `datamodel-code-generator` (Optional)

**Selected**: `datamodel-code-generator` (dev dependency)

**Rationale**:
1. **Pydantic generation**: Creates type-safe Python dataclasses from JSON Schema
2. **IDE support**: Full autocomplete and type checking
3. **Validation**: Pydantic provides runtime validation with detailed errors
4. **Maintainability**: Single source of truth (schema), types auto-generated

**Generation Command**:
```bash
# Run during development or in pre-commit hook
uv run datamodel-codegen \
  --input schemas/events/event-v1.1.0.json \
  --output src/specify_cli/hooks/events_v1_1.py \
  --target-python-version 3.11 \
  --use-standard-collections \
  --use-schema-description \
  --field-constraints \
  --use-default \
  --enable-faux-immutability
```

**Developer Choice**:
- **Option A**: Use `jsonschema` for validation + Python dataclasses (manual)
- **Option B**: Use generated Pydantic models (type-safe, auto-validated)

Both approaches supported; Pydantic recommended for new code.

### 2.3 CLI Validation Tool

**Script**: `scripts/validate_events.py`

```python
#!/usr/bin/env python3
"""Standalone event validator for JSONL files.

Usage:
    uv run python scripts/validate_events.py events.jsonl
    uv run python scripts/validate_events.py --schema-version 1.1.0 events.jsonl
"""
import sys
import json
from pathlib import Path
from specify_cli.hooks.validators import EventValidator

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate JSONL event stream")
    parser.add_argument("file", help="JSONL file to validate")
    parser.add_argument("--schema-version", default="1.1.0", help="Schema version")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    events_file = Path(args.file)
    if not events_file.exists():
        print(f"Error: File not found: {events_file}", file=sys.stderr)
        sys.exit(1)

    total = 0
    valid = 0
    invalid = 0

    with events_file.open() as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue

            total += 1
            try:
                event = json.loads(line)
                is_valid, errors = EventValidator.validate(event)

                if is_valid:
                    valid += 1
                    if args.verbose:
                        print(f"✓ Line {line_num}: {event.get('event_type', 'unknown')}")
                else:
                    invalid += 1
                    print(f"✗ Line {line_num}: {event.get('event_type', 'unknown')}", file=sys.stderr)
                    for error in errors:
                        print(f"  - {error}", file=sys.stderr)
            except json.JSONDecodeError as e:
                invalid += 1
                print(f"✗ Line {line_num}: Invalid JSON - {e}", file=sys.stderr)

    print(f"\nResults: {valid}/{total} valid, {invalid} invalid")
    sys.exit(0 if invalid == 0 else 1)

if __name__ == "__main__":
    main()
```

---

## 3. Test Strategy

### 3.1 Sample Event Extraction

**Approach**: Extract all 60 example events from `build-docs/jsonl-event-system.md` into test fixtures.

**Script**: `scripts/extract_sample_events.py`
```python
#!/usr/bin/env python3
"""Extract sample events from specification to test fixture.

Parses build-docs/jsonl-event-system.md and extracts all JSON examples
into tests/fixtures/sample_events_v1_1.jsonl for automated testing.
"""
import re
from pathlib import Path

def extract_json_examples(md_file: Path) -> list[str]:
    """Extract JSON examples from markdown code blocks."""
    content = md_file.read_text()

    # Find all ```json or ```jsonl code blocks
    pattern = r'```json(?:l)?\s*\n(.*?)\n```'
    matches = re.findall(pattern, content, re.DOTALL)

    events = []
    for match in matches:
        # Each match might be a single event or multiple lines
        for line in match.strip().split('\n'):
            if line.strip() and line.strip().startswith('{'):
                events.append(line.strip())

    return events

def main():
    spec_file = Path("build-docs/jsonl-event-system.md")
    output_file = Path("tests/fixtures/sample_events_v1_1.jsonl")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    events = extract_json_examples(spec_file)

    with output_file.open('w') as f:
        for event in events:
            f.write(event + '\n')

    print(f"Extracted {len(events)} sample events to {output_file}")

if __name__ == "__main__":
    main()
```

### 3.2 Automated Test Suite

**File**: `tests/test_event_schema_v1_1.py`

```python
"""Test suite for Event Schema v1.1.0.

Validates:
1. Schema file structure and validity
2. All 60 sample events from specification
3. Namespace coverage (11 namespaces)
4. Required field enforcement
5. Optional object validation
"""
import json
from pathlib import Path
import pytest
from jsonschema import Draft7Validator, ValidationError

SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "events" / "event-v1.1.0.json"
FIXTURES_PATH = Path(__file__).parent / "fixtures" / "sample_events_v1_1.jsonl"

@pytest.fixture
def schema():
    """Load event schema v1.1.0."""
    return json.loads(SCHEMA_PATH.read_text())

@pytest.fixture
def validator(schema):
    """Create JSON Schema validator."""
    return Draft7Validator(schema)

@pytest.fixture
def sample_events():
    """Load all sample events from fixture."""
    events = []
    with FIXTURES_PATH.open() as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))
    return events

class TestSchemaStructure:
    """Test schema file structure and metadata."""

    def test_schema_exists(self):
        """Schema file exists at expected location."""
        assert SCHEMA_PATH.exists(), f"Schema not found: {SCHEMA_PATH}"

    def test_schema_is_valid_json(self, schema):
        """Schema is valid JSON."""
        assert isinstance(schema, dict)

    def test_schema_metadata(self, schema):
        """Schema has required metadata fields."""
        assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
        assert "$id" in schema
        assert schema["$id"] == "https://flowspec.dev/schemas/agent-event-v1.1.0.json"
        assert schema["title"] == "Agent Event"
        assert "description" in schema

    def test_required_fields(self, schema):
        """Schema enforces required fields."""
        required = schema["required"]
        assert set(required) == {"version", "event_type", "timestamp", "agent_id"}

    def test_namespace_pattern(self, schema):
        """event_type pattern matches 11 namespaces."""
        pattern = schema["properties"]["event_type"]["pattern"]
        expected_namespaces = [
            "lifecycle", "activity", "coordination", "hook",
            "git", "task", "container", "decision",
            "system", "action", "security"
        ]
        # Pattern should include all namespaces
        assert "lifecycle" in pattern
        assert "git" in pattern
        assert "security" in pattern

class TestSampleEvents:
    """Test all sample events from specification."""

    def test_fixture_exists(self):
        """Sample events fixture exists."""
        assert FIXTURES_PATH.exists(), f"Fixture not found: {FIXTURES_PATH}"

    def test_all_events_valid(self, validator, sample_events):
        """All sample events pass schema validation."""
        invalid_events = []

        for i, event in enumerate(sample_events, 1):
            errors = list(validator.iter_errors(event))
            if errors:
                invalid_events.append({
                    "index": i,
                    "event_type": event.get("event_type", "unknown"),
                    "errors": [e.message for e in errors]
                })

        if invalid_events:
            print("\n=== Invalid Events ===")
            for inv in invalid_events:
                print(f"Event {inv['index']} ({inv['event_type']}):")
                for err in inv['errors']:
                    print(f"  - {err}")

        assert len(invalid_events) == 0, f"{len(invalid_events)} events failed validation"

    def test_minimum_event_count(self, sample_events):
        """At least 60 sample events extracted."""
        assert len(sample_events) >= 60, f"Expected >= 60 events, got {len(sample_events)}"

    def test_namespace_coverage(self, sample_events):
        """All 11 namespaces represented in samples."""
        namespaces = set()
        for event in sample_events:
            event_type = event.get("event_type", "")
            if "." in event_type:
                namespace = event_type.split(".")[0]
                namespaces.add(namespace)

        expected_namespaces = {
            "lifecycle", "activity", "coordination", "hook",
            "git", "task", "container", "decision",
            "system", "action", "security"
        }

        missing = expected_namespaces - namespaces
        assert len(missing) == 0, f"Missing namespaces: {missing}"

class TestRequiredFields:
    """Test required field validation."""

    def test_missing_version(self, validator):
        """Event without version fails validation."""
        event = {
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test"
        }
        errors = list(validator.iter_errors(event))
        assert any("version" in e.message for e in errors)

    def test_missing_event_type(self, validator):
        """Event without event_type fails validation."""
        event = {
            "version": "1.1.0",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test"
        }
        errors = list(validator.iter_errors(event))
        assert any("event_type" in e.message for e in errors)

    def test_invalid_event_type_pattern(self, validator):
        """Invalid event_type format fails validation."""
        event = {
            "version": "1.1.0",
            "event_type": "invalid-format",  # Missing namespace
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test"
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) > 0

class TestOptionalObjects:
    """Test optional object structures."""

    def test_git_object_validation(self, validator):
        """Git object with valid fields passes."""
        event = {
            "version": "1.1.0",
            "event_type": "git.commit",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@backend-engineer",
            "git": {
                "operation": "commit",
                "sha": "abc123",
                "branch_name": "main",
                "gpg_key_id": "KEY001",
                "files_changed": 5
            }
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) == 0

    def test_task_object_validation(self, validator):
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
                "to_state": "In Implementation"
            }
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) == 0

    def test_decision_object_validation(self, validator):
        """Decision object with reversibility passes."""
        event = {
            "version": "1.1.0",
            "event_type": "decision.made",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@architect",
            "decision": {
                "decision_id": "ARCH-001",
                "category": "architecture",
                "reversibility": {
                    "type": "one-way-door",
                    "lock_in_factors": ["schema design"],
                    "reversal_cost": "high",
                    "reversal_window": "before production"
                }
            }
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) == 0

class TestBackwardCompatibility:
    """Test backward compatibility with v1.0 status field."""

    def test_status_field_allowed(self, validator):
        """Legacy status field is optional and validated."""
        event = {
            "version": "1.1.0",
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
            "status": "started"  # Legacy field
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) == 0

    def test_invalid_status_rejected(self, validator):
        """Invalid status enum value fails validation."""
        event = {
            "version": "1.1.0",
            "event_type": "lifecycle.started",
            "timestamp": "2025-12-15T00:00:00Z",
            "agent_id": "@test",
            "status": "invalid_status"
        }
        errors = list(validator.iter_errors(event))
        assert len(errors) > 0
```

**Coverage Goals**:
- **Schema validation**: 100% coverage of schema structure
- **Sample events**: All 60+ events from spec pass validation
- **Namespace coverage**: All 11 namespaces tested
- **Error cases**: Invalid events properly rejected

---

## 4. CI/CD Pipeline Integration

### 4.1 GitHub Actions Workflow Enhancement

**File**: `.github/workflows/ci.yml` (additions)

```yaml
jobs:
  # ... existing lint, test, build jobs ...

  schema-validation:
    name: Event Schema Validation
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync

      - name: Validate event schema structure
        run: |
          # Use check-jsonschema to validate the schema itself
          uv tool run check-jsonschema \
            --check-metaschema schemas/events/event-v1.1.0.json

      - name: Extract sample events from spec
        run: uv run python scripts/extract_sample_events.py

      - name: Run event schema tests
        run: |
          uv run pytest tests/test_event_schema_v1_1.py \
            -v \
            --cov=src/specify_cli/hooks/validators \
            --cov-report=term-missing

      - name: Validate production event logs (if exist)
        continue-on-error: true
        run: |
          if [ -f .flowspec/events/events-*.jsonl ]; then
            for file in .flowspec/events/events-*.jsonl; do
              echo "Validating $file"
              uv run python scripts/validate_events.py "$file"
            done
          fi

      - name: Upload schema as artifact
        uses: actions/upload-artifact@v4
        with:
          name: event-schema-v1.1.0
          path: schemas/events/event-v1.1.0.json
```

### 4.2 Pre-commit Hook (Optional)

**File**: `.pre-commit-config.yaml` (addition)

```yaml
repos:
  # ... existing hooks ...

  - repo: local
    hooks:
      - id: validate-event-schema
        name: Validate Event Schema
        entry: uv run check-jsonschema --check-metaschema
        files: ^schemas/events/.*\.json$
        language: system
        pass_filenames: true

      - id: regenerate-event-types
        name: Regenerate Event Types from Schema
        entry: uv run python scripts/generate_types_from_schema.py
        files: ^schemas/events/event-v1\.1\.0\.json$
        language: system
        pass_filenames: false
```

### 4.3 Quality Gates

**Pipeline Failure Conditions**:
1. Schema validation fails (malformed JSON Schema)
2. Any sample event fails validation
3. Missing namespace coverage
4. Test coverage < 95% for validators module
5. Production event logs contain invalid events (warning, not failure)

**DORA Metrics Impact**:
- **Deployment Frequency**: No impact (schema validation runs in parallel)
- **Lead Time**: +30 seconds for schema validation job
- **Change Failure Rate**: Reduced (catch schema bugs before merge)
- **MTTR**: Reduced (validation errors provide clear JSONPath context)

---

## 5. Migration Path: v1.0 → v1.1.0

### 5.1 Breaking Changes Analysis

**v1.0 → v1.1.0 is BACKWARD COMPATIBLE**:
- All v1.0 fields remain valid in v1.1.0
- New optional fields added (context, git, task, container, decision, action, security)
- New namespaces added (git, task, container, decision, action, security)
- Legacy `status` field remains supported

**No code changes required for v1.0 event emitters**.

### 5.2 Migration Utility

**File**: `src/specify_cli/migration/event_migration.py`

```python
"""Event schema migration utilities.

Provides tools to upgrade v1.0 events to v1.1.0 format.
"""
from typing import Any

def migrate_v1_0_to_v1_1(event: dict[str, Any]) -> dict[str, Any]:
    """Migrate v1.0 event to v1.1.0 format.

    Args:
        event: v1.0 event dictionary.

    Returns:
        v1.1.0 event dictionary.

    Changes:
        - Set version to "1.1.0"
        - Add empty context object if not present
        - Preserve all existing fields

    Example:
        >>> v1_event = {"version": "1.0", "event_type": "spec.created", ...}
        >>> v1_1_event = migrate_v1_0_to_v1_1(v1_event)
        >>> v1_1_event["version"]
        '1.1.0'
    """
    migrated = event.copy()

    # Update version
    migrated["version"] = "1.1.0"

    # Add empty context if not present (for unified tracking)
    if "context" not in migrated:
        migrated["context"] = {}

    return migrated

def migrate_jsonl_file(input_path: str, output_path: str) -> int:
    """Migrate JSONL file from v1.0 to v1.1.0.

    Args:
        input_path: Path to v1.0 JSONL file.
        output_path: Path for v1.1.0 JSONL file.

    Returns:
        Number of events migrated.
    """
    import json
    from pathlib import Path

    input_file = Path(input_path)
    output_file = Path(output_path)

    count = 0
    with input_file.open() as infile, output_file.open('w') as outfile:
        for line in infile:
            if not line.strip():
                continue

            v1_event = json.loads(line)
            v1_1_event = migrate_v1_0_to_v1_1(v1_event)

            outfile.write(json.dumps(v1_1_event) + '\n')
            count += 1

    return count
```

**CLI Command**:
```bash
# Add to specify CLI
specify events migrate \
  --from-version 1.0 \
  --to-version 1.1.0 \
  --input .flowspec/events/events-2025-12-13.jsonl \
  --output .flowspec/events/events-2025-12-13-v1.1.jsonl
```

### 5.3 Migration Testing

**File**: `tests/test_event_migration.py`

```python
"""Test event schema migration."""
import json
from specify_cli.migration.event_migration import migrate_v1_0_to_v1_1

def test_migrate_preserves_all_fields():
    """Migration preserves all existing v1.0 fields."""
    v1_event = {
        "version": "1.0",
        "event_type": "spec.created",
        "event_id": "evt_123",
        "timestamp": "2025-12-15T00:00:00Z",
        "project_root": "/tmp",
        "feature": "auth",
        "artifacts": [{"type": "prd", "path": "spec.md"}]
    }

    v1_1_event = migrate_v1_0_to_v1_1(v1_event)

    assert v1_1_event["version"] == "1.1.0"
    assert v1_1_event["event_type"] == "spec.created"
    assert v1_1_event["feature"] == "auth"
    assert v1_1_event["artifacts"] == v1_event["artifacts"]

def test_migrate_adds_context():
    """Migration adds empty context object."""
    v1_event = {
        "version": "1.0",
        "event_type": "task.completed",
        "event_id": "evt_456",
        "timestamp": "2025-12-15T00:00:00Z",
        "project_root": "/tmp"
    }

    v1_1_event = migrate_v1_0_to_v1_1(v1_event)

    assert "context" in v1_1_event
    assert isinstance(v1_1_event["context"], dict)
```

---

## 6. Developer Experience

### 6.1 Type Generation Workflow

**Step 1**: Edit schema
```bash
vim schemas/events/event-v1.1.0.json
```

**Step 2**: Generate Python types
```bash
uv run python scripts/generate_types_from_schema.py
# Generates: src/specify_cli/hooks/events_v1_1.py
```

**Step 3**: Use generated types
```python
from specify_cli.hooks.events_v1_1 import (
    Event,
    GitObject,
    TaskObject,
    DecisionObject
)

# Full IDE autocomplete
event = Event(
    version="1.1.0",
    event_type="git.commit",
    timestamp="2025-12-15T00:00:00Z",
    agent_id="@backend-engineer",
    git=GitObject(
        operation="commit",
        sha="abc123",
        branch_name="main"
    )
)
```

### 6.2 Developer Documentation

**File**: `docs/guides/event-schema-guide.md`

```markdown
# Event Schema v1.1.0 Developer Guide

## Quick Start

### Emitting Events

```python
from specify_cli.hooks.validators import EventValidator
import json

# Create event
event = {
    "version": "1.1.0",
    "event_type": "task.state_changed",
    "timestamp": "2025-12-15T00:00:00Z",
    "agent_id": "@orchestrator",
    "context": {
        "task_id": "task-485"
    },
    "task": {
        "task_id": "task-485",
        "from_state": "Planned",
        "to_state": "In Implementation"
    }
}

# Validate before emitting
is_valid, errors = EventValidator.validate(event)
if not is_valid:
    print("Validation errors:", errors)
else:
    # Write to JSONL log
    with open(".flowspec/events/events.jsonl", "a") as f:
        f.write(json.dumps(event) + '\n')
```

### Querying Events

```bash
# All events for a task
jq -c 'select(.context.task_id == "task-485")' .flowspec/events/events.jsonl

# Git commits by agent
jq -c 'select(.event_type == "git.commit" and .agent_id == "@backend-engineer")' events.jsonl
```

## Schema Reference

See [jsonl-event-system.md](../../build-docs/jsonl-event-system.md) for complete schema documentation.
```

### 6.3 IDE Support

**Generated types provide**:
- Autocomplete for all event fields
- Type checking for nested objects
- Inline documentation from schema descriptions
- Error highlighting for invalid field names

**Example IDE Experience** (VS Code with Pylance):
```python
event = Event(
    version="1.1.0",
    event_type="git.commit",  # ← Autocomplete shows all event types
    git=GitObject(
        operation="commit",  # ← Autocomplete shows valid operations
        sha="abc123",
        # ← Type error if missing required field
    )
)
```

---

## 7. Performance Considerations

### 7.1 Validation Performance

**Benchmark Goals**:
- Single event validation: < 1ms
- 1000 event JSONL file: < 500ms
- Schema load time: < 10ms (cached after first load)

**Optimization Strategies**:
1. **Schema caching**: Load schema once per process
2. **Lazy validation**: Only validate when `--strict` flag enabled
3. **Batch validation**: Validate multiple events in single pass
4. **Optional validation**: Skip in production, enable in dev/CI

### 7.2 Schema Size

**Current schema size**: ~15KB (estimated)
- Acceptable for runtime inclusion
- No impact on CLI startup time
- Compressed in distribution packages

---

## 8. Security Considerations

### 8.1 Schema Validation as Security Control

**Threat Model**:
- **Malicious event injection**: Schema validation prevents invalid event structures
- **Type confusion**: Strict type checking prevents data type attacks
- **Denial of service**: Size limits on string fields prevent memory exhaustion

**Schema Security Features**:
```json
{
  "message": {
    "type": "string",
    "maxLength": 1000  // Prevent DoS via huge messages
  },
  "metadata": {
    "type": "object",
    "additionalProperties": true,
    "maxProperties": 50  // Limit metadata bloat
  }
}
```

### 8.2 Sensitive Data Handling

**Schema Rules**:
1. **No secrets in events**: Schema does not allow credential fields
2. **Secret references only**: `container.secrets_injected` lists secret names, not values
3. **Audit trail**: All security events logged for compliance

**Example**:
```json
{
  "event_type": "container.secrets_injected",
  "container": {
    "secrets_injected": ["GITHUB_TOKEN", "OPENAI_API_KEY"]  // Names only
  }
}
```

---

## 9. Observability & Monitoring

### 9.1 Schema Validation Metrics

**Metrics to Track**:
- `event_validation_total{result="valid|invalid"}`: Validation attempts
- `event_validation_duration_ms`: Validation latency
- `event_schema_errors{error_type}`: Error types encountered
- `event_type_distribution{namespace, event_type}`: Event type usage

**Implementation**:
```python
# In validators.py
import time

class EventValidator:
    _metrics = {
        "valid": 0,
        "invalid": 0,
        "total_duration_ms": 0.0
    }

    @classmethod
    def validate(cls, event: dict) -> tuple[bool, list[str]]:
        start = time.perf_counter()

        # ... validation logic ...

        duration_ms = (time.perf_counter() - start) * 1000
        cls._metrics["total_duration_ms"] += duration_ms
        cls._metrics["valid" if is_valid else "invalid"] += 1

        return is_valid, errors
```

### 9.2 Event Log Monitoring

**Production Monitoring**:
- Alert on invalid events in production logs
- Track event type distribution drift
- Monitor schema version distribution (v1.0 vs v1.1.0)

**Grafana Dashboard**:
```promql
# Events per second by type
rate(events_total{namespace="git"}[5m])

# Validation error rate
rate(event_validation_total{result="invalid"}[5m]) / rate(event_validation_total[5m])
```

---

## 10. Rollout Plan

### Phase 1: Schema & Validation (Week 1)
- [ ] Create `schemas/events/event-v1.1.0.json`
- [ ] Implement `EventValidator` class
- [ ] Extract sample events fixture
- [ ] Write test suite (100% coverage)
- [ ] CI/CD integration

**Deliverables**: AC 1, 2, 3, 4

### Phase 2: Migration Tools (Week 1)
- [ ] Implement migration utility
- [ ] Add migration tests
- [ ] Create CLI command
- [ ] Update documentation

**Deliverables**: AC 5

### Phase 3: Developer Tools (Week 2)
- [ ] Type generation script
- [ ] Developer guide
- [ ] CLI validation tool
- [ ] Pre-commit hooks

**Deliverables**: AC 6 (Developer documentation)

### Phase 4: Production Rollout (Week 2)
- [ ] Validate existing event logs
- [ ] Monitor validation metrics
- [ ] Gather developer feedback
- [ ] Iterate on schema if needed

---

## 11. Success Criteria

### Acceptance Criteria Mapping

| AC | Requirement | Implementation |
|----|-------------|----------------|
| 1 | JSON Schema validates all event types | `schemas/events/event-v1.1.0.json` |
| 2 | Supports 11 namespaces | Namespace pattern in schema |
| 3 | Enforces required fields | `required` array in schema |
| 4 | Unit tests validate 60+ events | `tests/test_event_schema_v1_1.py` |
| 5 | Semver + migration notes | Version in schema, migration utility |

### DORA Metrics Impact

**Deployment Frequency**:
- No impact (schema is data, not code)
- Enables future automated event emission

**Lead Time**:
- +30s CI validation time (acceptable)
- -15min debugging time (validation errors provide clear feedback)

**Change Failure Rate**:
- Reduced: Schema validation catches bugs before production
- Target: 0% schema-related failures

**MTTR**:
- Reduced: JSONPath error messages enable rapid debugging
- Target: < 5min to identify invalid event issue

---

## 12. References

### Documentation
- **Specification**: `/Users/jasonpoley/ps/flowspec/build-docs/jsonl-event-system.md`
- **Existing v1.0**: `/Users/jasonpoley/ps/flowspec/src/specify_cli/hooks/events.py`
- **Test Patterns**: `/Users/jasonpoley/ps/flowspec/tests/test_hooks_events.py`
- **Schema Examples**: `/Users/jasonpoley/ps/flowspec/schemas/decision-log.schema.json`

### Tools
- **jsonschema**: https://python-jsonschema.readthedocs.io/
- **datamodel-code-generator**: https://github.com/koxudaxi/datamodel-code-generator
- **check-jsonschema**: https://check-jsonschema.readthedocs.io/

### Standards
- **JSON Schema Draft-07**: https://json-schema.org/draft-07/json-schema-release-notes.html
- **JSONL**: https://jsonlines.org/
- **Semantic Versioning**: https://semver.org/

---

## Appendix A: Schema Snippet

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://flowspec.dev/schemas/agent-event-v1.1.0.json",
  "title": "Agent Event",
  "description": "Unified JSONL event schema for agents, tasks, git, and containers",
  "type": "object",
  "required": ["version", "event_type", "timestamp", "agent_id"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Schema version (semver)"
    },
    "event_type": {
      "type": "string",
      "pattern": "^(lifecycle|activity|coordination|hook|git|task|container|decision|system|action|security)\\.[a-z_]+$",
      "description": "Namespaced event type"
    }
    // ... (see full schema in jsonl-event-system.md)
  }
}
```

---

## Appendix B: Decision Log

**Decision 1**: Use `jsonschema` over custom validation
- **Rationale**: Already a dependency, well-tested, industry standard
- **Reversibility**: Two-way door (can add Pydantic later)

**Decision 2**: Generate types from schema (not reverse)
- **Rationale**: Schema is source of truth for validation
- **Reversibility**: One-way door (schema-first approach)

**Decision 3**: JSONL format for event logs
- **Rationale**: Streaming-friendly, tooling-rich (jq, grep, awk)
- **Reversibility**: One-way door (established in v1.0)

---

**End of Platform Design Document**
