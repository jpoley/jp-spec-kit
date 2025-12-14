# JSONL Event System Specification

## Overview

This document defines the comprehensive JSONL message passing structure for the Agent Updates Collector system. Each event is a single-line JSON object with schema validation, enabling structured logging, inter-agent coordination, and audit trails.

**Design Goals:**
- **Simplicity**: Flat JSONL format, one event per line
- **Extensibility**: Namespaced event types, metadata field for custom data
- **Observability**: Correlation IDs for distributed tracing
- **Backward Compatibility**: Maps to existing status values

---

## Schema Version

```
Version: 1.0.0
Format: JSONL (JSON Lines)
Encoding: UTF-8
```

---

## Event Structure

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `version` | string | Schema version (semver) | `"1.0.0"` |
| `event_type` | string | Namespaced event type | `"lifecycle.started"` |
| `timestamp` | string | ISO 8601 with timezone | `"2025-12-13T20:45:00.123Z"` |
| `agent_id` | string | Unique agent identifier | `"@backend-engineer@galway"` |

### Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `event_id` | string | UUID for this event | `"550e8400-e29b-41d4-a716-446655440000"` |
| `session_id` | string | Session grouping identifier | `"sess-abc123"` |
| `source` | enum | Event origin: `"mcp"` \| `"hook"` | `"hook"` |
| `status` | enum | Legacy status (backward compat) | `"started"` |
| `message` | string | Human-readable description | `"Starting API implementation"` |
| `progress` | number | Completion percentage (0.0-1.0) | `0.75` |
| `tool` | object | Tool execution details | See Tool Object |
| `hook` | object | Hook-specific payload | See Hook Object |
| `correlation` | object | Distributed tracing context | See Correlation Object |
| `metadata` | object | Arbitrary extensible data | `{"custom_key": "value"}` |

### Tool Object

```json
{
  "tool_name": "Read",
  "tool_input": {"file_path": "/src/main.py"},
  "tool_result": "success",
  "duration_ms": 150
}
```

### Hook Object

```json
{
  "hook_type": "PreToolUse",
  "raw_payload": {...}
}
```

### Correlation Object

```json
{
  "trace_id": "abc123def456",
  "span_id": "span001",
  "parent_span_id": "span000",
  "root_agent_id": "@orchestrator"
}
```

---

## Event Types

### 1. Lifecycle Namespace (`lifecycle.*`)

Agent state machine transitions.

| Event Type | Description | When Emitted |
|------------|-------------|--------------|
| `lifecycle.started` | Agent begins execution | Agent initialization |
| `lifecycle.completed` | Agent finishes successfully | Task completion |
| `lifecycle.error` | Agent fails with error | Unrecoverable failure |
| `lifecycle.terminated` | Agent forcibly stopped | External termination |

**Example:**
```json
{"version":"1.0.0","event_type":"lifecycle.started","timestamp":"2025-12-13T20:45:00.123Z","agent_id":"@backend-engineer","session_id":"sess-abc123","source":"mcp","message":"Beginning API implementation"}
```

### 2. Activity Namespace (`activity.*`)

What the agent is currently doing.

| Event Type | Description | When Emitted |
|------------|-------------|--------------|
| `activity.thinking` | Reasoning/planning phase | Between tool uses |
| `activity.tool_use` | Executing a specific tool | Tool invocation |
| `activity.progress` | Measurable progress update | Task milestone |

**Example:**
```json
{"version":"1.0.0","event_type":"activity.tool_use","timestamp":"2025-12-13T20:45:05.456Z","agent_id":"@backend-engineer","tool":{"tool_name":"Read","tool_input":{"file_path":"/src/api.py"}},"message":"Reading API source file"}
```

### 3. Coordination Namespace (`coordination.*`)

Inter-agent synchronization events.

| Event Type | Description | When Emitted |
|------------|-------------|--------------|
| `coordination.waiting` | Waiting for dependency | Awaiting another agent/resource |
| `coordination.blocked` | Blocked, needs intervention | Permission denied, resource unavailable |
| `coordination.handoff` | Handing off to another agent | Pipeline transitions |

**Example:**
```json
{"version":"1.0.0","event_type":"coordination.waiting","timestamp":"2025-12-13T20:46:00.789Z","agent_id":"@qa-engineer","message":"Waiting for @backend-engineer to complete","metadata":{"waiting_for":"@backend-engineer","expected_status":"completed"}}
```

### 4. Hook Namespace (`hook.*`)

Claude Code hook-triggered events.

| Event Type | Hook Trigger | Default Status | Description |
|------------|--------------|----------------|-------------|
| `hook.session_start` | SessionStart | `started` | New Claude Code session |
| `hook.session_end` | SessionEnd | `completed` | Session terminated |
| `hook.prompt_submit` | UserPromptSubmit | `thinking` | User submitted prompt |
| `hook.pre_tool_use` | PreToolUse | `tool_use` | About to execute tool |
| `hook.post_tool_use` | PostToolUse | `progress` | Tool execution completed |
| `hook.permission_request` | PermissionRequest | `waiting` | Awaiting user permission |
| `hook.notification` | Notification | `progress` | System notification |
| `hook.stop` | Stop | `completed` | Main agent stopped |
| `hook.subagent_stop` | SubagentStop | `completed` | Subagent completed |
| `hook.pre_compact` | PreCompact | `progress` | About to compact context |

**Example:**
```json
{"version":"1.0.0","event_type":"hook.pre_tool_use","timestamp":"2025-12-13T20:45:10.111Z","agent_id":"session-abc12345","source":"hook","status":"tool_use","hook":{"hook_type":"PreToolUse"},"tool":{"tool_name":"Bash"},"message":"Using Bash"}
```

### 5. Decision Namespace (`decision.*`)

Decision logging for audit trails.

| Event Type | Description | When Emitted |
|------------|-------------|--------------|
| `decision.made` | A decision was recorded | After reasoning |
| `decision.rationale` | Extended reasoning | Complex decisions |
| `decision.rejected` | Option rejected | Alternative considered |

**Example:**
```json
{"version":"1.0.0","event_type":"decision.made","timestamp":"2025-12-13T20:47:00.000Z","agent_id":"@architect","message":"Chose PostgreSQL over MySQL","metadata":{"decision_id":"arch-001","options_considered":["PostgreSQL","MySQL","SQLite"],"chosen":"PostgreSQL","rationale":"Better JSON support and concurrent write performance"}}
```

### 6. System Namespace (`system.*`)

Infrastructure and system events.

| Event Type | Description | When Emitted |
|------------|-------------|--------------|
| `system.heartbeat` | Agent health check | Periodic interval |
| `system.config_change` | Configuration updated | Settings modified |
| `system.error` | System-level error | Infrastructure failure |

**Example:**
```json
{"version":"1.0.0","event_type":"system.heartbeat","timestamp":"2025-12-13T20:48:00.000Z","agent_id":"@backend-engineer","metadata":{"uptime_ms":120000,"memory_mb":256}}
```

---

## Backward Compatibility

### Status → Event Type Mapping

| Legacy Status | New Event Type |
|---------------|----------------|
| `started` | `lifecycle.started` |
| `thinking` | `activity.thinking` |
| `tool_use` | `activity.tool_use` |
| `progress` | `activity.progress` |
| `waiting` | `coordination.waiting` |
| `blocked` | `coordination.blocked` |
| `completed` | `lifecycle.completed` |
| `error` | `lifecycle.error` |

### Hook Event → Event Type Mapping

| Hook Event | Event Type | Status |
|------------|------------|--------|
| SessionStart | `hook.session_start` | `started` |
| SessionEnd | `hook.session_end` | `completed` |
| UserPromptSubmit | `hook.prompt_submit` | `thinking` |
| PreToolUse | `hook.pre_tool_use` | `tool_use` |
| PostToolUse | `hook.post_tool_use` | `progress` |
| PermissionRequest | `hook.permission_request` | `waiting` |
| Notification | `hook.notification` | `progress` |
| Stop | `hook.stop` | `completed` |
| SubagentStop | `hook.subagent_stop` | `completed` |
| PreCompact | `hook.pre_compact` | `progress` |

---

## JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://example.com/agent-event-v1.0.0.json",
  "title": "Agent Event",
  "description": "Agent Updates Collector JSONL event schema",
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
      "pattern": "^(lifecycle|activity|coordination|hook|decision|system)\\.[a-z_]+$",
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
    "event_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID for this event"
    },
    "session_id": {
      "type": "string",
      "description": "Session grouping identifier"
    },
    "source": {
      "type": "string",
      "enum": ["mcp", "hook"],
      "description": "Event origin"
    },
    "status": {
      "type": "string",
      "enum": ["started", "thinking", "tool_use", "progress", "waiting", "blocked", "completed", "error"],
      "description": "Legacy status value"
    },
    "message": {
      "type": "string",
      "description": "Human-readable description"
    },
    "progress": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Completion percentage"
    },
    "tool": {
      "type": "object",
      "properties": {
        "tool_name": {"type": "string"},
        "tool_input": {"type": "object"},
        "tool_result": {"type": "string"},
        "duration_ms": {"type": "integer"}
      },
      "description": "Tool execution details"
    },
    "hook": {
      "type": "object",
      "properties": {
        "hook_type": {"type": "string"},
        "raw_payload": {"type": "object"}
      },
      "description": "Hook-specific payload"
    },
    "correlation": {
      "type": "object",
      "properties": {
        "trace_id": {"type": "string"},
        "span_id": {"type": "string"},
        "parent_span_id": {"type": "string"},
        "root_agent_id": {"type": "string"}
      },
      "description": "Distributed tracing context"
    },
    "metadata": {
      "type": "object",
      "additionalProperties": true,
      "description": "Arbitrary extensible data"
    }
  }
}
```

---

## Complete Event Type Reference

### Summary Table (22 Event Types)

| Namespace | Event Type | Status Equivalent | Description |
|-----------|------------|-------------------|-------------|
| lifecycle | `lifecycle.started` | started | Agent begins execution |
| lifecycle | `lifecycle.completed` | completed | Agent finishes successfully |
| lifecycle | `lifecycle.error` | error | Agent fails with error |
| lifecycle | `lifecycle.terminated` | - | Agent forcibly stopped |
| activity | `activity.thinking` | thinking | Reasoning/planning phase |
| activity | `activity.tool_use` | tool_use | Executing a tool |
| activity | `activity.progress` | progress | Progress update |
| coordination | `coordination.waiting` | waiting | Waiting for dependency |
| coordination | `coordination.blocked` | blocked | Blocked, needs intervention |
| coordination | `coordination.handoff` | - | Handing off to another agent |
| hook | `hook.session_start` | started | New Claude Code session |
| hook | `hook.session_end` | completed | Session terminated |
| hook | `hook.prompt_submit` | thinking | User submitted prompt |
| hook | `hook.pre_tool_use` | tool_use | About to execute tool |
| hook | `hook.post_tool_use` | progress | Tool completed |
| hook | `hook.permission_request` | waiting | Awaiting permission |
| hook | `hook.notification` | progress | System notification |
| hook | `hook.stop` | completed | Main agent stopped |
| hook | `hook.subagent_stop` | completed | Subagent completed |
| hook | `hook.pre_compact` | progress | About to compact context |
| decision | `decision.made` | - | Decision recorded |
| decision | `decision.rationale` | - | Extended reasoning |
| decision | `decision.rejected` | - | Option rejected |
| system | `system.heartbeat` | - | Health check |
| system | `system.config_change` | - | Config updated |
| system | `system.error` | error | System error |

---

## Usage Examples

### Multi-Agent Pipeline

```jsonl
{"version":"1.0.0","event_type":"lifecycle.started","timestamp":"2025-12-13T20:00:00.000Z","agent_id":"@pm-agent","session_id":"pipeline-001","message":"Starting PRD creation","correlation":{"trace_id":"trace-abc","span_id":"span-001"}}
{"version":"1.0.0","event_type":"activity.thinking","timestamp":"2025-12-13T20:00:05.000Z","agent_id":"@pm-agent","session_id":"pipeline-001","message":"Analyzing requirements","correlation":{"trace_id":"trace-abc","span_id":"span-002","parent_span_id":"span-001"}}
{"version":"1.0.0","event_type":"lifecycle.completed","timestamp":"2025-12-13T20:05:00.000Z","agent_id":"@pm-agent","session_id":"pipeline-001","message":"PRD complete","correlation":{"trace_id":"trace-abc","span_id":"span-003","parent_span_id":"span-001"}}
{"version":"1.0.0","event_type":"lifecycle.started","timestamp":"2025-12-13T20:05:01.000Z","agent_id":"@architect-agent","session_id":"pipeline-001","message":"Starting architecture design","correlation":{"trace_id":"trace-abc","span_id":"span-004","parent_span_id":"span-003"}}
```

### Tool Usage Tracking

```jsonl
{"version":"1.0.0","event_type":"hook.pre_tool_use","timestamp":"2025-12-13T20:10:00.000Z","agent_id":"@backend-engineer","source":"hook","status":"tool_use","tool":{"tool_name":"Grep","tool_input":{"pattern":"async def","path":"src/"}},"message":"Using Grep"}
{"version":"1.0.0","event_type":"hook.post_tool_use","timestamp":"2025-12-13T20:10:02.500Z","agent_id":"@backend-engineer","source":"hook","status":"progress","tool":{"tool_name":"Grep","duration_ms":2500},"message":"Grep completed"}
```

### Decision Logging

```jsonl
{"version":"1.0.0","event_type":"decision.made","timestamp":"2025-12-13T20:15:00.000Z","agent_id":"@architect","message":"Selected FastAPI over Flask","metadata":{"decision_id":"fw-001","category":"framework","options":["FastAPI","Flask","Django"],"chosen":"FastAPI","rationale":"Async support, automatic OpenAPI, better performance"}}
{"version":"1.0.0","event_type":"decision.rejected","timestamp":"2025-12-13T20:15:00.000Z","agent_id":"@architect","message":"Rejected Django","metadata":{"decision_id":"fw-001","option":"Django","reason":"Overkill for microservice, slower startup"}}
```

---

## Implementation Notes

### File Naming Convention

```
events-{date}.jsonl          # Daily event log
events-{agent_id}-{date}.jsonl   # Per-agent log
decisions-{date}.jsonl       # Decision audit log
```

### Validation Code (Python)

```python
import json
import jsonschema
from pathlib import Path

SCHEMA = json.loads(Path("schemas/event-v1.0.0.json").read_text())

def validate_event(event: dict) -> bool:
    """Validate event against JSON Schema."""
    try:
        jsonschema.validate(event, SCHEMA)
        return True
    except jsonschema.ValidationError as e:
        print(f"Validation error: {e.message}")
        return False

def parse_jsonl(filepath: str):
    """Parse JSONL file, yielding validated events."""
    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            if line.strip():
                try:
                    event = json.loads(line)
                    if validate_event(event):
                        yield event
                except json.JSONDecodeError as e:
                    print(f"Line {line_num}: Invalid JSON - {e}")
```

---

## Migration Path

1. **Phase 1**: Add `version` and `event_type` fields to existing events
2. **Phase 2**: Populate `correlation` objects for tracing
3. **Phase 3**: Migrate storage from SQLite to JSONL files
4. **Phase 4**: Deprecate legacy `status` field (v2.0.0)

---

## References

- [JSON Lines Specification](https://jsonlines.org/)
- [JSON Schema Draft-07](https://json-schema.org/draft-07/json-schema-release-notes.html)
- [OpenTelemetry Trace Context](https://www.w3.org/TR/trace-context/)
- [Claude Code Hooks Documentation](https://docs.anthropic.com/en/docs/claude-code/hooks)
