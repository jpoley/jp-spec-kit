# ADR-005: Event Model Architecture

**Status**: Proposed
**Date**: 2025-12-02
**Author**: @software-architect
**Context**: Agent Hooks Feature (task-198, task-210)

---

## Context

Flowspec operates as a **linear, synchronous workflow system** where each /flowspec command executes agents in isolation. This creates critical automation gaps:

1. **No automated quality gates**: Tests must be run manually after implementation
2. **No workflow orchestration**: Documentation updates and code reviews require manual coordination
3. **Limited extensibility**: Third-party tools (CI/CD, notifications) cannot integrate with workflow events

The system needs an event abstraction that:
- Captures workflow state transitions as discrete events
- Provides structured, versioned payloads for automation
- Remains tool-agnostic (works with Claude Code, Gemini, Copilot, etc.)
- Enables asynchronous, decoupled automation without blocking workflows

**Key Constraint**: Event emission must add <50ms overhead to any workflow command.

---

## Decision

Implement a **canonical event model** with the following design:

### 1. Event Type Taxonomy

Events follow a `<domain>.<action>` naming convention:

**Workflow Events**:
- `workflow.assessed` - /flow:assess completed
- `spec.created` - /flow:specify completed
- `spec.updated` - PRD file modified
- `research.completed` - /flow:research completed
- `plan.created` - /flow:plan completed
- `plan.updated` - Plan file modified
- `adr.created` - ADR document created
- `implement.started` - /flow:implement started
- `implement.completed` - /flow:implement completed
- `validate.started` - /flow:validate started
- `validate.completed` - /flow:validate completed
- `deploy.started` - /flow:operate started
- `deploy.completed` - /flow:operate completed

**Task Events**:
- `task.created` - New backlog task created
- `task.updated` - Task metadata changed
- `task.status_changed` - Task status transition
- `task.ac_checked` - Acceptance criterion marked complete
- `task.ac_unchecked` - Acceptance criterion unmarked
- `task.completed` - Task marked as Done
- `task.archived` - Task moved to archive

**Naming Conventions**:
- Past tense for completed actions: `created`, `completed`, `updated`
- Present tense for ongoing actions: `started`, `running`
- Domains align with workflow phases and backlog operations

### 2. Event Payload Schema

**Base Event Structure** (all events inherit):
```json
{
  "event_type": "implement.completed",
  "event_id": "evt_01HQZX123ABC",
  "schema_version": "1.0",
  "timestamp": "2025-12-02T15:30:45.123Z",
  "project_root": "/home/user/project",
  "feature": "user-authentication",
  "context": {
    "workflow_state": "In Implementation",
    "task_id": "task-189",
    "agent": "backend-engineer"
  },
  "artifacts": [
    {
      "type": "source_code",
      "path": "./src/auth/",
      "files_changed": 12
    }
  ],
  "metadata": {
    "cli_version": "0.0.179",
    "python_version": "3.11.9"
  }
}
```

**Required Fields** (all events):
- `event_type`: Canonical event identifier
- `event_id`: Unique identifier (sortable, globally unique)
- `schema_version`: Event schema version for backward compatibility
- `timestamp`: ISO 8601 UTC timestamp
- `project_root`: Absolute path to project directory

**Optional Fields** (context-dependent):
- `feature`: Feature name/identifier
- `context`: Event-specific context (agent, task_id, state)
- `artifacts`: Array of produced artifacts (files, reports)
- `metadata`: System metadata (versions, environment)

### 3. Event ID Generation

Event IDs use **ULIDs** (Universally Unique Lexicographically Sortable Identifiers):
- Format: `evt_01HQZX123ABC` (prefix + 26-character ULID)
- Properties: Sortable by creation time, globally unique, URL-safe
- Rationale: Enables chronological ordering, distributed generation, audit trail correlation

### 4. Event Versioning Strategy

**Schema Version Field**:
```json
{
  "schema_version": "1.0"
}
```

**Versioning Rules**:
- **Major version** (1.0 → 2.0): Breaking changes (removed fields, incompatible types)
- **Minor version** (1.0 → 1.1): Additive changes (new fields, new event types)
- **Backward compatibility**: Maintain support for 2 major versions
- **Deprecation warnings**: Include in payload when fields are deprecated:
  ```json
  {
    "deprecated_fields": ["old_field_name"],
    "deprecation_notice": "Use new_field_name instead. old_field_name will be removed in v2.0."
  }
  ```

### 5. Event Emission Points

**Workflow Commands** (all /flowspec commands):
- Emit AFTER successful command completion
- Failures don't emit events (only success events in v1)
- Emit synchronously before command returns
- Errors in event emission logged but don't break command (fail-safe)

**Backlog Operations**:
- `backlog task create` → `task.created`
- `backlog task edit -s "In Progress"` → `task.status_changed`
- `backlog task edit --check-ac 1` → `task.ac_checked`
- `backlog task edit -s Done` → `task.status_changed` + `task.completed`

---

## Consequences

### Positive

1. **Extensibility**: Third-party tools can integrate without modifying flowspec core
2. **Observability**: Event stream creates audit trail for compliance and debugging
3. **Decoupling**: Automation logic lives in hooks, not embedded in workflow commands
4. **Tool Agnostic**: Works with Claude Code, Gemini, Copilot, or headless automation
5. **Familiar Pattern**: Follows industry precedents (GitHub Actions, GitLab CI, AWS EventBridge)

### Negative

1. **Performance Overhead**: Event serialization and emission adds latency to every command
   - Mitigation: Benchmark requirement <50ms, async emission in v2 if needed
2. **Schema Evolution Complexity**: Breaking changes require coordinated upgrades across hooks
   - Mitigation: Versioning strategy with deprecation warnings, support 2 major versions
3. **Testing Burden**: Event contracts must be tested for all commands
   - Mitigation: JSON Schema validation, integration tests for all event types

### Neutral

1. **Event Ordering**: Events emitted in command execution order, but no global ordering guarantees across concurrent operations
   - Trade-off: Simplicity vs. strict causality tracking (acceptable for v1)
2. **Event Storage**: Events not persisted by default, only passed to hooks
   - Trade-off: Stateless (simpler) vs. event sourcing (more powerful but complex)

---

## Alternatives Considered

### Alternative 1: Callback Functions Instead of Events

**Approach**: Workflow commands accept callback functions instead of emitting events.

**Example**:
```python
def implement_command(feature: str, on_complete: Callable):
    # ... implementation ...
    on_complete({"feature": feature, "status": "success"})
```

**Rejected Because**:
- Tightly couples automation to Python codebase (not tool-agnostic)
- Requires recompiling CLI for new callbacks
- No serialization format (can't integrate external tools)
- Synchronous execution blocks workflow

### Alternative 2: Database Event Log

**Approach**: Store all events in SQLite database, hooks query event log.

**Example**:
```sql
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  event_type TEXT,
  timestamp TEXT,
  payload JSON
);
```

**Rejected Because**:
- Adds database dependency (increases complexity)
- Persistence not required for v1 use cases
- Introduces state management (migrations, backups)
- Performance overhead (disk I/O on every event)

**Note**: This could be revisited for v2 if event replay or historical queries become requirements.

### Alternative 3: Message Queue (Redis, RabbitMQ)

**Approach**: Emit events to external message broker, hooks consume from queue.

**Example**:
```python
redis_client.publish("flowspec.events", json.dumps(event))
```

**Rejected Because**:
- Requires external infrastructure (not local-first)
- Increases operational complexity (Redis must be running)
- Network latency adds >50ms overhead
- Overkill for local development workflows

**Note**: Webhooks in v2 provide external integration without requiring always-on broker.

### Alternative 4: File-Based Event Stream

**Approach**: Append events to `.flowspec/events.jsonl` file, hooks tail the file.

**Example**:
```jsonl
{"event_type": "spec.created", "timestamp": "2025-12-02T15:30:45Z"}
{"event_type": "task.completed", "timestamp": "2025-12-02T16:45:30Z"}
```

**Rejected Because**:
- File locking issues on concurrent writes
- Hooks must poll file (inefficient)
- No cleanup strategy (file grows unbounded)
- Doesn't solve immediate hook dispatch problem

**Note**: Audit logging uses this pattern, but for historical record, not real-time dispatch.

---

## Implementation Guidance

### Event Emitter Module

**Location**: `src/specify_cli/events/emitter.py`

**Interface**:
```python
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class Artifact:
    type: str
    path: str
    files_changed: Optional[int] = None

@dataclass
class Event:
    event_type: str
    event_id: str
    schema_version: str = "1.0"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    project_root: str = field(default_factory=lambda: os.getcwd())
    feature: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    artifacts: Optional[List[Artifact]] = None
    metadata: Optional[Dict[str, Any]] = None

class EventEmitter:
    """Emits workflow events to configured hooks."""

    def emit(
        self,
        event_type: str,
        feature: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        artifacts: Optional[List[Artifact]] = None,
    ) -> Event:
        """
        Emit an event and trigger matching hooks.

        Fails gracefully if hook execution errors occur.
        """
        event = Event(
            event_type=event_type,
            event_id=self._generate_event_id(),
            feature=feature,
            context=context,
            artifacts=artifacts,
            metadata=self._get_metadata(),
        )

        try:
            self._dispatch_hooks(event)
        except Exception as e:
            logger.warning(f"Hook dispatch failed: {e}")
            # Fail-safe: don't break workflow on hook errors

        return event

    def _generate_event_id(self) -> str:
        """Generate ULID-based event ID."""
        import ulid
        return f"evt_{ulid.ulid()}"

    def _dispatch_hooks(self, event: Event):
        """Dispatch event to hook runner (sync in v1, async in v2)."""
        # Call hook runner with event payload
        pass
```

### JSON Schema Definition

**Location**: `src/specify_cli/events/schemas/base-event.schema.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Flowspec Base Event",
  "type": "object",
  "required": ["event_type", "event_id", "schema_version", "timestamp", "project_root"],
  "properties": {
    "event_type": {
      "type": "string",
      "pattern": "^[a-z]+\\.[a-z_]+$",
      "description": "Canonical event type (domain.action)"
    },
    "event_id": {
      "type": "string",
      "pattern": "^evt_[0-9A-HJKMNP-TV-Z]{26}$",
      "description": "Unique event identifier (ULID)"
    },
    "schema_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$",
      "description": "Event schema version (major.minor)"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 UTC timestamp"
    },
    "project_root": {
      "type": "string",
      "description": "Absolute path to project directory"
    },
    "feature": {
      "type": "string",
      "description": "Feature name/identifier"
    },
    "context": {
      "type": "object",
      "description": "Event-specific context"
    },
    "artifacts": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["type", "path"],
        "properties": {
          "type": {"type": "string"},
          "path": {"type": "string"},
          "files_changed": {"type": "integer"}
        }
      }
    },
    "metadata": {
      "type": "object",
      "description": "System metadata"
    }
  }
}
```

---

## Testing Strategy

### Unit Tests

**Test Event Generation**:
```python
def test_event_id_format():
    emitter = EventEmitter()
    event_id = emitter._generate_event_id()
    assert event_id.startswith("evt_")
    assert len(event_id) == 30  # evt_ + 26 chars

def test_event_payload_structure():
    emitter = EventEmitter()
    event = emitter.emit(
        event_type="spec.created",
        feature="authentication",
        context={"agent": "pm-planner"}
    )
    assert event.event_type == "spec.created"
    assert event.feature == "authentication"
    assert "agent" in event.context
```

### Integration Tests

**Test Event Emission from Commands**:
```python
def test_implement_command_emits_event(tmp_path):
    # Setup test project
    project = setup_test_project(tmp_path)

    # Execute command
    result = run_command(["flow:implement", "auth"])

    # Verify event emitted
    events = get_emitted_events()
    assert len(events) == 1
    assert events[0].event_type == "implement.completed"
    assert events[0].feature == "auth"
```

### Schema Validation Tests

```python
def test_event_validates_against_schema():
    event = create_test_event()
    schema = load_json_schema("base-event.schema.json")

    # Should not raise ValidationError
    jsonschema.validate(event.to_dict(), schema)
```

---

## References

- **PRD**: `docs/prd/agent-hooks-prd.md` - Full requirements document
- **Assessment**: `docs/assess/agent-hooks-assessment.md` - Complexity and risk analysis
- **Related ADR-003**: Stop Hook Quality Gate - Example of existing hook pattern
- **task-198**: Define Event Model Schema (implementation task)
- **task-201**: Implement Event Emitter Module (implementation task)

---

## Revision History

- **2025-12-02**: Initial decision (v1.0) - @software-architect
