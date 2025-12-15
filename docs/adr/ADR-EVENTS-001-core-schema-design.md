# ADR-EVENTS-001: Core Event Schema v1.1.0 Design

**Status**: Proposed
**Date**: 2025-12-15
**Author**: @architect (Software Architect)
**Related Task**: task-485

---

## Context and Problem Statement

We need to define a JSON Schema (draft-07) for the unified event system that supports:
- 60+ event types across 11 namespaces (lifecycle, activity, coordination, hook, git, task, container, decision, system, action, security)
- Required base fields: version, event_type, timestamp, agent_id
- Optional context fields for cross-referencing (task_id, branch_name, container_id, etc.)
- Namespace-specific objects (tool, hook, git, task, container, decision, action, security, correlation)
- Backward compatibility with existing v1.0 Python dataclass (~26 event types)
- Forward compatibility via versioning

The schema must balance strictness (ensuring data quality) with flexibility (supporting future evolution).

### Architectural Principles (Hohpe's Architect Elevator)

**Penthouse View**: This schema is the contract for our entire observability platform. It's the foundation for compliance auditing, multi-agent coordination, and event-driven workflows. Poor schema design creates technical debt that compounds over time.

**Engine Room View**: The schema must validate events at emit-time with minimal performance overhead (<10ms), support streaming JSONL parsing, and integrate seamlessly with existing Python Event dataclass.

---

## Decision Drivers

1. **Backward Compatibility**: Must support v1.0 events (existing 26 event types) without breaking changes
2. **Validation Strictness**: Prevent invalid events from corrupting the stream, but allow evolution
3. **Performance**: Validation must be fast enough for high-volume producers (target: <10ms)
4. **Developer Experience**: Schema should be intuitive, self-documenting, and error messages helpful
5. **Future-Proofing**: Support adding new namespaces and event types without schema version bumps
6. **Integration**: Work with existing Python Event class and jsonschema library
7. **Compliance**: Enable audit trails, security attestation, and decision tracking

---

## Considered Options

### Option 1: Strict Schema with `oneOf` for Event Types

**Approach**: Use JSON Schema `oneOf` to enforce event-type-specific field requirements.

**Example**:
```json
{
  "oneOf": [
    {
      "properties": {
        "event_type": {"const": "git.commit"},
        "git": {"type": "object", "required": ["sha", "message"]}
      },
      "required": ["git"]
    },
    {
      "properties": {
        "event_type": {"const": "task.created"},
        "task": {"type": "object", "required": ["task_id"]}
      },
      "required": ["task"]
    }
  ]
}
```

**Pros**:
- Maximum validation: ensures event-specific fields are present
- Catches errors early (e.g., git.commit without git.sha)
- Self-documenting: schema defines exact structure for each event type

**Cons**:
- **High maintenance burden**: Every new event type requires schema update
- **Poor error messages**: oneOf failures are cryptic ("event did not match any schema")
- **Lock-in**: Adding event types is a breaking change (requires schema version bump)
- **Performance**: oneOf validation is slower (must test all branches)
- **Complexity**: 60 oneOf branches is unmanageable

**Reversibility Assessment**:
- Type: **One-way door** (somewhat)
- Reversal Cost: **Medium** - would require schema migration
- Lock-in Factors: All event producers depend on strict validation

---

### Option 2: Permissive Schema with Namespace Pattern Matching

**Approach**: Validate base fields strictly, but allow any namespace-specific objects without field-level validation.

**Example**:
```json
{
  "required": ["version", "event_type", "timestamp", "agent_id"],
  "properties": {
    "event_type": {"pattern": "^(lifecycle|activity|git|...)\\.[a-z_]+$"},
    "git": {"type": "object"},
    "task": {"type": "object"},
    "context": {"type": "object"}
  }
}
```

**Pros**:
- **Low maintenance**: Adding event types doesn't require schema changes
- **Flexible**: Supports evolution without breaking changes
- **Fast validation**: No oneOf branches to test
- **Simple error messages**: Clear which base field is missing

**Cons**:
- **Weak validation**: Doesn't catch missing event-specific fields (e.g., git.commit without sha)
- **Reliance on runtime**: Validation pushed to application logic
- **Less self-documenting**: Schema doesn't specify event-specific structure

**Reversibility Assessment**:
- Type: **Two-way door**
- Reversal Cost: **Low** - can add stricter validation later
- Lock-in Factors: None - schema is extensible

---

### Option 3: Hybrid Schema with Optional Namespace Validation

**Approach**: Strict validation for base fields + defined structure for namespace objects, but no enforcement of event-type-specific requirements.

**Example**:
```json
{
  "required": ["version", "event_type", "timestamp", "agent_id"],
  "properties": {
    "event_type": {"pattern": "^(lifecycle|activity|...)\\.[a-z_]+$"},
    "git": {
      "type": "object",
      "properties": {
        "sha": {"type": "string"},
        "message": {"type": "string"},
        "branch_name": {"type": "string"}
      }
    },
    "task": {
      "type": "object",
      "properties": {
        "task_id": {"type": "string"},
        "title": {"type": "string"}
      }
    }
  }
}
```

**Pros**:
- **Balanced**: Validates structure without enforcing presence
- **Moderate maintenance**: Defines schema for namespace objects, but adding event types is easy
- **Good error messages**: Clear feedback on field type mismatches
- **Performance**: Fast validation (no oneOf)
- **Documentation**: Schema documents expected fields for each namespace

**Cons**:
- **Partial validation**: Won't catch missing required fields (e.g., git.commit without sha)
- **Application-level checks**: Must validate event-type-specific requirements in code

**Reversibility Assessment**:
- Type: **Two-way door**
- Reversal Cost: **Low-Medium** - can add stricter validation or relax further
- Lock-in Factors: Minimal - namespace objects are documented but not enforced

---

## Decision Outcome

**Chosen Option**: **Option 3 - Hybrid Schema with Optional Namespace Validation**

### Rationale

Using Hohpe's "Selling Options" framework:

**Volatility Assessment**: The event schema will evolve rapidly as we add:
- New namespaces (CI/CD, monitoring, deployment)
- New event types within existing namespaces
- New fields to existing events (e.g., git.commit adds `gpg_fingerprint`)

**Option Valuation**:
- **Option 1 (Strict)**: High initial cost + ongoing maintenance burden = **expensive option** with high lock-in
- **Option 2 (Permissive)**: Low cost but weak guarantees = **cheap option** with potential technical debt
- **Option 3 (Hybrid)**: Moderate cost + good balance = **optimal option** for current volatility

**Investment Justification**:
- We're "buying an option" to evolve the schema without breaking existing consumers
- The schema provides **structural documentation** while preserving **flexibility**
- Validation catches common errors (type mismatches) without locking us into rigid event-type-specific validation

### Consequences

#### Positive Consequences

1. **Low Maintenance Burden**: Adding new event types doesn't require schema updates
2. **Fast Validation**: No oneOf branches, validation completes in <5ms (well under 10ms target)
3. **Clear Documentation**: Schema serves as canonical reference for namespace object structure
4. **Backward Compatible**: v1.0 events validate successfully (all required fields present)
5. **Forward Compatible**: New fields can be added to namespace objects without schema version bump
6. **Good Error Messages**: jsonschema provides clear feedback on type mismatches

#### Negative Consequences

1. **Incomplete Validation**: Schema won't catch event-type-specific missing fields
2. **Application-Level Checks**: Must implement validation helpers for critical events (e.g., git.commit requires sha)
3. **Potential Data Quality Issues**: Invalid events may slip through if application logic has bugs

#### Risk Mitigation

**Risk**: Invalid events corrupt the stream
**Mitigation**:
- Implement event factory functions with built-in validation (e.g., `emit_git_commit(sha, message)`)
- Create validation helper: `validate_event_complete(event)` for critical events
- Run periodic async validator to scan event logs for malformed events
- Add linting rules to catch invalid event emission in code review

**Risk**: Schema drift over time
**Mitigation**:
- Maintain comprehensive test suite with 60+ sample events (one per event type)
- Document expected fields for each event type in `jsonl-event-system.md`
- Use JSON Schema `examples` field to provide canonical event samples
- Run schema validation tests in CI/CD

---

## Implementation Details

### Schema Structure

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://flowspec.dev/schemas/event-v1.1.0.json",
  "title": "Agent Event v1.1.0",
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
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp with timezone"
    },
    "agent_id": {
      "type": "string",
      "minLength": 1,
      "description": "Unique agent identifier"
    },

    // Optional base fields
    "event_id": {"type": "string", "format": "uuid"},
    "session_id": {"type": "string"},
    "source": {"enum": ["mcp", "hook", "cli", "system"]},
    "status": {"enum": ["started", "thinking", "tool_use", "progress", "waiting", "blocked", "completed", "error"]},
    "message": {"type": "string"},
    "progress": {"type": "number", "minimum": 0.0, "maximum": 1.0},

    // Context object (cross-referencing)
    "context": {
      "type": "object",
      "properties": {
        "task_id": {"type": "string"},
        "branch_name": {"type": "string"},
        "worktree_path": {"type": "string"},
        "container_id": {"type": "string"},
        "pr_number": {"type": "integer"},
        "decision_id": {"type": "string"}
      }
    },

    // Namespace-specific objects (structure defined, not required)
    "tool": { /* Tool object schema */ },
    "hook": { /* Hook object schema */ },
    "git": { /* Git object schema */ },
    "task": { /* Task object schema */ },
    "container": { /* Container object schema */ },
    "decision": { /* Decision object schema */ },
    "action": { /* Action object schema */ },
    "security": { /* Security object schema */ },
    "correlation": { /* Correlation object schema */ },
    "metadata": {"type": "object", "additionalProperties": true}
  },

  "additionalProperties": false
}
```

### Integration with Python Event Class

**Backward Compatibility Strategy**:
1. Existing `Event` class (v1.0) already has required fields (event_type, timestamp, project_root)
2. Map `project_root` → `agent_id` for v1.0 events (or add agent_id field to Event class)
3. Python validation function wraps jsonschema validator
4. Event factory functions ensure complete event structure

**Migration Path**:
- **Phase 1** (v1.1.0): Add schema validation to emit path (optional flag to skip)
- **Phase 2**: Retrofit existing event emission to use factory functions
- **Phase 3**: Add event-specific validation helpers for critical events
- **Phase 4** (v2.0.0): Deprecate legacy `status` field (breaking change)

---

## Validation Strategy (ADR-002 Reference)

Per ADR-002 (Event Validation Approach):
- **Default**: Validate against JSON Schema at emit time
- **Optional**: `--skip-validation` flag for trusted producers (system)
- **Async**: Periodic validator scans event logs for schema drift

**Validation Function**:
```python
def validate_event(event: dict, strict: bool = False) -> bool:
    """Validate event against JSON Schema.

    Args:
        event: Event dictionary to validate
        strict: If True, also validate event-type-specific requirements

    Returns:
        True if valid, raises ValidationError otherwise
    """
    # Step 1: JSON Schema validation (structure + types)
    jsonschema.validate(event, EVENT_SCHEMA)

    # Step 2: Event-type-specific validation (optional strict mode)
    if strict:
        validate_event_complete(event)

    return True
```

---

## Examples and Test Coverage

The schema must validate all 60 event types from `jsonl-event-system.md`. Test plan:

### Test Categories

1. **Base Structure Tests** (10 tests)
   - Valid minimal event (required fields only)
   - Missing required field (version, event_type, timestamp, agent_id)
   - Invalid event_type namespace
   - Invalid timestamp format
   - Invalid version format

2. **Namespace Tests** (11 tests, one per namespace)
   - lifecycle.* event with valid structure
   - activity.* event with tool object
   - git.* event with git object
   - task.* event with task object
   - ... (all 11 namespaces)

3. **Backward Compatibility Tests** (5 tests)
   - v1.0 event validates successfully
   - Legacy status field allowed
   - Missing optional fields allowed
   - Extra fields rejected (additionalProperties: false)

4. **Integration Tests** (5 tests)
   - Parse JSONL file with 60+ events
   - Validate mixed event types
   - Correlation object propagation
   - Context object cross-referencing

**Total Test Count**: 31 unit tests + integration tests

---

## Performance Benchmarks

**Validation Performance Targets**:
- Single event validation: <5ms (p95)
- Batch validation (100 events): <100ms
- JSONL streaming parse: >1000 events/second

**Measurement Approach**:
```python
import time
import jsonschema

schema = load_schema("event-v1.1.0.json")
validator = jsonschema.Draft7Validator(schema)

# Benchmark
events = [generate_sample_event() for _ in range(1000)]
start = time.perf_counter()
for event in events:
    validator.validate(event)
duration = time.perf_counter() - start

print(f"Validated {len(events)} events in {duration:.3f}s")
print(f"Average: {duration/len(events)*1000:.2f}ms per event")
```

---

## Related Decisions

- **ADR-002**: Event Validation Approach (referenced for validation strategy)
- **ADR-003**: Correlation and Tracing Strategy (correlation object structure)
- **ADR-005**: State Machine Implementation (event-driven state reconstruction)

---

## Review Triggers

This decision should be reviewed if:
1. Event validation performance exceeds 10ms (p95)
2. Schema validation catches <80% of invalid events in testing
3. Adding new event types requires schema changes >50% of the time
4. Developer feedback indicates schema is too restrictive or too permissive
5. Compliance requirements necessitate stricter validation

---

## Acceptance Criteria for Implementation (Task-485)

1. JSON Schema file created at `.flowspec/events/schema/event-v1.1.0.json`
2. Schema validates all 60 event types from `jsonl-event-system.md`
3. Schema supports all 11 namespaces with defined object structures
4. Unit tests validate 60+ sample events (one per event type)
5. Performance benchmarks confirm <10ms validation (p95)
6. Backward compatibility: v1.0 events validate successfully
7. Documentation includes migration notes and examples

---

## Appendix A: Complete Namespace Object Schemas

### Git Object
```json
"git": {
  "type": "object",
  "properties": {
    "operation": {"type": "string"},
    "sha": {"type": "string", "minLength": 7, "maxLength": 40},
    "branch_name": {"type": "string"},
    "from_branch": {"type": "string"},
    "gpg_key_id": {"type": "string"},
    "gpg_fingerprint": {"type": "string"},
    "signer_agent_id": {"type": "string"},
    "message": {"type": "string"},
    "files_changed": {"type": "integer", "minimum": 0},
    "insertions": {"type": "integer", "minimum": 0},
    "deletions": {"type": "integer", "minimum": 0},
    "merge_method": {"enum": ["merge", "squash", "rebase"]}
  }
}
```

### Task Object
```json
"task": {
  "type": "object",
  "properties": {
    "task_id": {"type": "string"},
    "title": {"type": "string"},
    "from_state": {"type": "string"},
    "to_state": {"type": "string"},
    "assigned_to": {"type": "string"},
    "labels": {"type": "array", "items": {"type": "string"}},
    "ac_index": {"type": "integer", "minimum": 0},
    "ac_text": {"type": "string"}
  }
}
```

### Decision Object
```json
"decision": {
  "type": "object",
  "properties": {
    "decision_id": {"type": "string"},
    "category": {"type": "string"},
    "reversibility": {
      "type": "object",
      "properties": {
        "type": {"enum": ["one-way-door", "two-way-door"]},
        "lock_in_factors": {"type": "array", "items": {"type": "string"}},
        "reversal_cost": {"enum": ["trivial", "low", "medium", "high", "prohibitive"]},
        "reversal_window": {"type": "string"},
        "notes": {"type": "string"}
      }
    },
    "alternatives_considered": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "option": {"type": "string"},
          "rejected_reason": {"type": "string"}
        }
      }
    },
    "supporting_material": {
      "type": "object",
      "properties": {
        "links": {"type": "array"},
        "internal_refs": {"type": "array", "items": {"type": "string"}}
      }
    }
  }
}
```

(Additional namespace objects follow same pattern - see jsonl-event-system.md for complete definitions)

---

## Appendix B: Sample Events for Testing

### Sample 1: Git Commit Event
```json
{
  "version": "1.1.0",
  "event_type": "git.commit",
  "timestamp": "2025-12-13T21:00:00.000Z",
  "agent_id": "@backend-engineer",
  "message": "feat: add user authentication",
  "context": {
    "task_id": "task-123",
    "branch_name": "task-123-auth"
  },
  "git": {
    "operation": "commit",
    "sha": "abc123def456",
    "branch_name": "task-123-auth",
    "gpg_key_id": "ABCD1234EF56",
    "signer_agent_id": "@backend-engineer",
    "message": "feat: add user authentication",
    "files_changed": 5,
    "insertions": 120,
    "deletions": 30
  }
}
```

### Sample 2: Task State Changed Event
```json
{
  "version": "1.1.0",
  "event_type": "task.state_changed",
  "timestamp": "2025-12-13T20:30:00.000Z",
  "agent_id": "@backend-engineer",
  "message": "Task moved to In Progress",
  "context": {
    "task_id": "task-123"
  },
  "task": {
    "task_id": "task-123",
    "title": "Implement user authentication",
    "from_state": "To Do",
    "to_state": "In Progress",
    "assigned_to": "@backend-engineer",
    "labels": ["backend", "security"]
  }
}
```

### Sample 3: Decision Made Event
```json
{
  "version": "1.1.0",
  "event_type": "decision.made",
  "timestamp": "2025-12-13T20:47:00.000Z",
  "agent_id": "@architect",
  "message": "Chose PostgreSQL over MySQL",
  "context": {
    "task_id": "task-45",
    "branch_name": "task-45-database",
    "decision_id": "ARCH-001"
  },
  "decision": {
    "decision_id": "ARCH-001",
    "category": "technology",
    "reversibility": {
      "type": "two-way-door",
      "lock_in_factors": [],
      "reversal_cost": "medium",
      "reversal_window": "before production data"
    },
    "alternatives_considered": [
      {
        "option": "MySQL",
        "rejected_reason": "Weaker JSON support"
      },
      {
        "option": "SQLite",
        "rejected_reason": "Not suitable for production scale"
      }
    ]
  },
  "metadata": {
    "options_considered": ["PostgreSQL", "MySQL", "SQLite"],
    "chosen": "PostgreSQL",
    "rationale": "Better JSON support and concurrent write performance"
  }
}
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-15 | @architect | Initial ADR for schema design decision |
