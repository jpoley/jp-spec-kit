# JSONL Event System Specification

## Overview

This document defines the comprehensive JSONL message passing structure for unified observability across agents, tasks, git workflows, containers, and decisions. Each event is a single-line JSON object with schema validation, enabling structured logging, inter-agent coordination, and complete audit trails.

**Design Goals:**
- **Simplicity**: Flat JSONL format, one event per line
- **Extensibility**: Namespaced event types, metadata field for custom data
- **Observability**: Correlation IDs for distributed tracing
- **Unified Tracking**: Cross-reference fields link events to tasks, branches, containers
- **Single Source of Truth**: All observability flows through this event system
- **Backward Compatibility**: Maps to existing status values

---

## Schema Version

```
Version: 1.1.0
Format: JSONL (JSON Lines)
Encoding: UTF-8
```

---

## Event Structure

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `version` | string | Schema version (semver) | `"1.1.0"` |
| `event_type` | string | Namespaced event type | `"lifecycle.started"` |
| `timestamp` | string | ISO 8601 with timezone | `"2025-12-13T20:45:00.123Z"` |
| `agent_id` | string | Unique agent identifier | `"@backend-engineer@galway"` |

### Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `event_id` | string | UUID for this event | `"550e8400-e29b-41d4-a716-446655440000"` |
| `session_id` | string | Session grouping identifier | `"sess-abc123"` |
| `source` | enum | Event origin: `"mcp"` \| `"hook"` \| `"cli"` \| `"system"` | `"hook"` |
| `status` | enum | Legacy status (backward compat) | `"started"` |
| `message` | string | Human-readable description | `"Starting API implementation"` |
| `progress` | number | Completion percentage (0.0-1.0) | `0.75` |
| `tool` | object | Tool execution details | See Tool Object |
| `hook` | object | Hook-specific payload | See Hook Object |
| `git` | object | Git operation details | See Git Object |
| `task` | object | Task operation details | See Task Object |
| `container` | object | Container details | See Container Object |
| `decision` | object | Decision details | See Decision Object |
| `context` | object | Cross-reference context | See Context Object |
| `correlation` | object | Distributed tracing context | See Correlation Object |
| `metadata` | object | Arbitrary extensible data | `{"custom_key": "value"}` |

### Context Object (Cross-Referencing)

The context object enables unified tracking across dimensions:

```json
{
  "task_id": "task-123",
  "branch_name": "task-123-feature-name",
  "worktree_path": "/path/to/worktree",
  "container_id": "abc123def456",
  "pr_number": 456,
  "decision_id": "ARCH-001"
}
```

**Purpose**: Links any event to the task, branch, container, or decision it relates to. Enables queries like "show me all events for task-123" across all namespaces.

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

### Git Object

```json
{
  "operation": "commit",
  "sha": "abc123def456",
  "branch_name": "task-123-feature",
  "from_branch": "main",
  "gpg_key_id": "ABCD1234",
  "gpg_fingerprint": "1234 5678 ABCD ...",
  "signer_agent_id": "@backend-engineer",
  "message": "feat: add user authentication",
  "files_changed": 5,
  "insertions": 120,
  "deletions": 30
}
```

### Task Object

```json
{
  "task_id": "task-123",
  "title": "Implement user authentication",
  "from_state": "To Do",
  "to_state": "In Progress",
  "assigned_to": "@backend-engineer",
  "labels": ["backend", "security"],
  "ac_index": 1,
  "ac_text": "Users can log in with email/password"
}
```

### Container Object

```json
{
  "container_id": "abc123def456",
  "image": "jpoley/flowspec-agents:latest",
  "exit_code": 0,
  "secrets_injected": ["GITHUB_TOKEN", "OPENAI_API_KEY"],
  "network_mode": "isolated",
  "resource_limits": {"memory_mb": 2048, "cpu_cores": 2}
}
```

### Decision Object

```json
{
  "decision_id": "ARCH-003",
  "category": "architecture",
  "reversibility": {
    "type": "one-way-door",
    "lock_in_factors": ["schema design", "data migration"],
    "reversal_cost": "prohibitive",
    "reversal_window": "before v1.0 launch"
  },
  "alternatives_considered": [
    {"option": "Alternative A", "rejected_reason": "Performance issues"}
  ],
  "supporting_material": {
    "links": [{"url": "https://example.com", "title": "Reference", "type": "documentation"}],
    "internal_refs": ["docs/adr/ADR-001.md"]
  }
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
{"version":"1.1.0","event_type":"lifecycle.started","timestamp":"2025-12-13T20:45:00.123Z","agent_id":"@backend-engineer","session_id":"sess-abc123","source":"mcp","message":"Beginning API implementation","context":{"task_id":"task-123","branch_name":"task-123-auth"}}
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
{"version":"1.1.0","event_type":"activity.tool_use","timestamp":"2025-12-13T20:45:05.456Z","agent_id":"@backend-engineer","tool":{"tool_name":"Read","tool_input":{"file_path":"/src/api.py"}},"message":"Reading API source file","context":{"task_id":"task-123"}}
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
{"version":"1.1.0","event_type":"coordination.waiting","timestamp":"2025-12-13T20:46:00.789Z","agent_id":"@qa-engineer","message":"Waiting for @backend-engineer to complete","context":{"task_id":"task-123"},"metadata":{"waiting_for":"@backend-engineer","expected_status":"completed"}}
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
{"version":"1.1.0","event_type":"hook.pre_tool_use","timestamp":"2025-12-13T20:45:10.111Z","agent_id":"session-abc12345","source":"hook","status":"tool_use","hook":{"hook_type":"PreToolUse"},"tool":{"tool_name":"Bash"},"message":"Using Bash"}
```

### 5. Git Namespace (`git.*`)

Git operations and workflow events. **New in v1.1.0.**

| Event Type | Description | When Emitted |
|------------|-------------|--------------|
| `git.worktree_created` | New worktree created for task | Task work begins |
| `git.worktree_removed` | Worktree cleaned up | Task completion or abandonment |
| `git.branch_created` | New branch created | Branch checkout |
| `git.branch_deleted` | Branch removed | Post-merge cleanup |
| `git.commit` | Commit made | After code changes |
| `git.local_pr_submitted` | Local PR submitted for review | Before push |
| `git.local_pr_approved` | Local PR passed quality gates | All checks pass |
| `git.local_pr_rejected` | Local PR failed quality gates | Check failure |
| `git.pushed` | Push to remote | After local approval |
| `git.pr_created` | GitHub PR created | After push |
| `git.merged` | Branch merged | PR merge |

**Example - Commit with GPG Signing:**
```json
{"version":"1.1.0","event_type":"git.commit","timestamp":"2025-12-13T21:00:00.000Z","agent_id":"@backend-engineer","message":"feat: add user authentication","context":{"task_id":"task-123","branch_name":"task-123-auth"},"git":{"operation":"commit","sha":"abc123def456","branch_name":"task-123-auth","gpg_key_id":"ABCD1234EF56","signer_agent_id":"@backend-engineer","message":"feat: add user authentication","files_changed":5,"insertions":120,"deletions":30}}
```

**Example - Local PR Approval:**
```json
{"version":"1.1.0","event_type":"git.local_pr_approved","timestamp":"2025-12-13T21:15:00.000Z","agent_id":"system","message":"Local PR passed all quality gates","context":{"task_id":"task-123","branch_name":"task-123-auth"},"metadata":{"approval_mode":"auto","checks":{"lint":"pass","test":"pass","sast":"pass","conflicts":"none"}}}
```

### 6. Task Namespace (`task.*`)

Task lifecycle events from Backlog.md. **New in v1.1.0.**

| Event Type | Description | When Emitted |
|------------|-------------|--------------|
| `task.created` | New task in backlog | Task creation |
| `task.assigned` | Agent assigned to task | Assignment |
| `task.state_changed` | State transition | Status update |
| `task.ac_checked` | Acceptance criterion met | AC completion |
| `task.blocked` | Task blocked | Blocker identified |
| `task.unblocked` | Task unblocked | Blocker resolved |
| `task.completed` | Task done | All ACs met |
| `task.archived` | Task archived | Cleanup |

**Example - State Change:**
```json
{"version":"1.1.0","event_type":"task.state_changed","timestamp":"2025-12-13T20:30:00.000Z","agent_id":"@backend-engineer","message":"Task moved to In Progress","context":{"task_id":"task-123"},"task":{"task_id":"task-123","title":"Implement user authentication","from_state":"To Do","to_state":"In Progress","assigned_to":"@backend-engineer","labels":["backend","security"]}}
```

**Example - Acceptance Criterion Checked:**
```json
{"version":"1.1.0","event_type":"task.ac_checked","timestamp":"2025-12-13T22:00:00.000Z","agent_id":"@backend-engineer","message":"Acceptance criterion 1 completed","context":{"task_id":"task-123"},"task":{"task_id":"task-123","ac_index":1,"ac_text":"Users can log in with email/password"}}
```

### 7. Container Namespace (`container.*`)

Container and devcontainer events. **New in v1.1.0.**

| Event Type | Description | When Emitted |
|------------|-------------|--------------|
| `container.started` | Container spawned | Container creation |
| `container.agent_attached` | Agent attached to container | Agent initialization |
| `container.secrets_injected` | Secrets provided at runtime | Container setup |
| `container.resource_limit_hit` | Resource limit reached | Resource exhaustion |
| `container.stopped` | Container stopped | Container termination |

**Example - Container Started:**
```json
{"version":"1.1.0","event_type":"container.started","timestamp":"2025-12-13T20:25:00.000Z","agent_id":"system","message":"Devcontainer started for task-123","context":{"task_id":"task-123","container_id":"abc123def456"},"container":{"container_id":"abc123def456","image":"jpoley/flowspec-agents:latest","network_mode":"isolated","resource_limits":{"memory_mb":2048,"cpu_cores":2}}}
```

**Example - Secrets Injected (without exposing values):**
```json
{"version":"1.1.0","event_type":"container.secrets_injected","timestamp":"2025-12-13T20:25:05.000Z","agent_id":"system","message":"Runtime secrets injected","context":{"container_id":"abc123def456"},"container":{"container_id":"abc123def456","secrets_injected":["GITHUB_TOKEN","OPENAI_API_KEY"]}}
```

### 8. Decision Namespace (`decision.*`)

Decision logging for audit trails. Integrates with decision-tracker.md format.

| Event Type | Description | When Emitted |
|------------|-------------|--------------|
| `decision.made` | A decision was recorded | After reasoning |
| `decision.rationale` | Extended reasoning | Complex decisions |
| `decision.rejected` | Option rejected | Alternative considered |

**Example - Full Decision with Reversibility:**
```json
{"version":"1.1.0","event_type":"decision.made","timestamp":"2025-12-13T20:47:00.000Z","agent_id":"@architect","message":"Chose PostgreSQL over MySQL","context":{"task_id":"task-45","branch_name":"task-45-database","decision_id":"ARCH-001"},"decision":{"decision_id":"ARCH-001","category":"technology","reversibility":{"type":"two-way-door","lock_in_factors":[],"reversal_cost":"medium","reversal_window":"before production data"},"alternatives_considered":[{"option":"MySQL","rejected_reason":"Weaker JSON support"},{"option":"SQLite","rejected_reason":"Not suitable for production scale"}]},"metadata":{"options_considered":["PostgreSQL","MySQL","SQLite"],"chosen":"PostgreSQL","rationale":"Better JSON support and concurrent write performance"}}
```

### 9. System Namespace (`system.*`)

Infrastructure and system events.

| Event Type | Description | When Emitted |
|------------|-------------|--------------|
| `system.heartbeat` | Agent health check | Periodic interval |
| `system.config_change` | Configuration updated | Settings modified |
| `system.error` | System-level error | Infrastructure failure |

**Example:**
```json
{"version":"1.1.0","event_type":"system.heartbeat","timestamp":"2025-12-13T20:48:00.000Z","agent_id":"@backend-engineer","metadata":{"uptime_ms":120000,"memory_mb":256}}
```

---

## Complete Event Type Reference

### Summary Table (46 Event Types)

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
| git | `git.worktree_created` | - | Worktree created |
| git | `git.worktree_removed` | - | Worktree removed |
| git | `git.branch_created` | - | Branch created |
| git | `git.branch_deleted` | - | Branch deleted |
| git | `git.commit` | - | Commit made |
| git | `git.local_pr_submitted` | waiting | Local PR submitted |
| git | `git.local_pr_approved` | progress | Local PR approved |
| git | `git.local_pr_rejected` | blocked | Local PR rejected |
| git | `git.pushed` | progress | Pushed to remote |
| git | `git.pr_created` | - | GitHub PR created |
| git | `git.merged` | completed | Branch merged |
| task | `task.created` | - | Task created |
| task | `task.assigned` | - | Task assigned |
| task | `task.state_changed` | - | State changed |
| task | `task.ac_checked` | progress | AC completed |
| task | `task.blocked` | blocked | Task blocked |
| task | `task.unblocked` | - | Task unblocked |
| task | `task.completed` | completed | Task completed |
| task | `task.archived` | - | Task archived |
| container | `container.started` | - | Container started |
| container | `container.agent_attached` | - | Agent attached |
| container | `container.secrets_injected` | - | Secrets injected |
| container | `container.resource_limit_hit` | blocked | Resource limit hit |
| container | `container.stopped` | - | Container stopped |
| decision | `decision.made` | - | Decision recorded |
| decision | `decision.rationale` | - | Extended reasoning |
| decision | `decision.rejected` | - | Option rejected |
| system | `system.heartbeat` | - | Health check |
| system | `system.config_change` | - | Config updated |
| system | `system.error` | error | System error |

---

## Unified Workflow: Task to Merge

This example shows the complete event flow for a task from creation to merge:

```jsonl
{"version":"1.1.0","event_type":"task.created","timestamp":"2025-12-13T20:00:00.000Z","agent_id":"@pm-agent","context":{"task_id":"task-123"},"task":{"task_id":"task-123","title":"Add user authentication","labels":["backend","security"]}}
{"version":"1.1.0","event_type":"git.branch_created","timestamp":"2025-12-13T20:01:00.000Z","agent_id":"system","context":{"task_id":"task-123","branch_name":"task-123-auth"},"git":{"operation":"branch","branch_name":"task-123-auth","from_branch":"main"}}
{"version":"1.1.0","event_type":"git.worktree_created","timestamp":"2025-12-13T20:01:05.000Z","agent_id":"system","context":{"task_id":"task-123","branch_name":"task-123-auth","worktree_path":"/worktrees/task-123-auth"}}
{"version":"1.1.0","event_type":"container.started","timestamp":"2025-12-13T20:01:10.000Z","agent_id":"system","context":{"task_id":"task-123","container_id":"dev-abc123"},"container":{"container_id":"dev-abc123","image":"jpoley/flowspec-agents:latest"}}
{"version":"1.1.0","event_type":"container.secrets_injected","timestamp":"2025-12-13T20:01:12.000Z","agent_id":"system","context":{"container_id":"dev-abc123"},"container":{"secrets_injected":["GITHUB_TOKEN"]}}
{"version":"1.1.0","event_type":"task.assigned","timestamp":"2025-12-13T20:01:15.000Z","agent_id":"@orchestrator","context":{"task_id":"task-123"},"task":{"task_id":"task-123","assigned_to":"@backend-engineer"}}
{"version":"1.1.0","event_type":"lifecycle.started","timestamp":"2025-12-13T20:02:00.000Z","agent_id":"@backend-engineer","context":{"task_id":"task-123","branch_name":"task-123-auth","container_id":"dev-abc123"},"correlation":{"trace_id":"trace-xyz","span_id":"span-001"}}
{"version":"1.1.0","event_type":"activity.thinking","timestamp":"2025-12-13T20:02:30.000Z","agent_id":"@backend-engineer","message":"Planning authentication approach","context":{"task_id":"task-123"},"correlation":{"trace_id":"trace-xyz","span_id":"span-002","parent_span_id":"span-001"}}
{"version":"1.1.0","event_type":"decision.made","timestamp":"2025-12-13T20:03:00.000Z","agent_id":"@backend-engineer","message":"Using JWT for session management","context":{"task_id":"task-123","decision_id":"IMPL-001"},"decision":{"decision_id":"IMPL-001","category":"technology","reversibility":{"type":"two-way-door","reversal_cost":"low"}}}
{"version":"1.1.0","event_type":"activity.tool_use","timestamp":"2025-12-13T20:10:00.000Z","agent_id":"@backend-engineer","context":{"task_id":"task-123"},"tool":{"tool_name":"Write","tool_input":{"file_path":"/src/auth.py"}}}
{"version":"1.1.0","event_type":"git.commit","timestamp":"2025-12-13T20:30:00.000Z","agent_id":"@backend-engineer","context":{"task_id":"task-123","branch_name":"task-123-auth"},"git":{"sha":"abc123","message":"feat: add JWT authentication","gpg_key_id":"AGENT-BE-001","signer_agent_id":"@backend-engineer","files_changed":3}}
{"version":"1.1.0","event_type":"task.ac_checked","timestamp":"2025-12-13T20:31:00.000Z","agent_id":"@backend-engineer","context":{"task_id":"task-123"},"task":{"ac_index":1,"ac_text":"Users can log in with email/password"}}
{"version":"1.1.0","event_type":"git.local_pr_submitted","timestamp":"2025-12-13T20:35:00.000Z","agent_id":"@backend-engineer","context":{"task_id":"task-123","branch_name":"task-123-auth"},"message":"Submitting for local review"}
{"version":"1.1.0","event_type":"git.local_pr_approved","timestamp":"2025-12-13T20:36:00.000Z","agent_id":"system","context":{"task_id":"task-123","branch_name":"task-123-auth"},"metadata":{"checks":{"lint":"pass","test":"pass","sast":"pass"}}}
{"version":"1.1.0","event_type":"git.pushed","timestamp":"2025-12-13T20:36:30.000Z","agent_id":"system","context":{"task_id":"task-123","branch_name":"task-123-auth"},"git":{"branch_name":"task-123-auth"}}
{"version":"1.1.0","event_type":"git.pr_created","timestamp":"2025-12-13T20:37:00.000Z","agent_id":"system","context":{"task_id":"task-123","branch_name":"task-123-auth","pr_number":456},"metadata":{"pr_url":"https://github.com/org/repo/pull/456"}}
{"version":"1.1.0","event_type":"git.merged","timestamp":"2025-12-13T21:00:00.000Z","agent_id":"system","context":{"task_id":"task-123","branch_name":"task-123-auth","pr_number":456},"git":{"operation":"merge","branch_name":"task-123-auth","merge_method":"squash"}}
{"version":"1.1.0","event_type":"task.completed","timestamp":"2025-12-13T21:00:05.000Z","agent_id":"system","context":{"task_id":"task-123"}}
{"version":"1.1.0","event_type":"lifecycle.completed","timestamp":"2025-12-13T21:00:10.000Z","agent_id":"@backend-engineer","context":{"task_id":"task-123"},"correlation":{"trace_id":"trace-xyz","span_id":"span-final"}}
{"version":"1.1.0","event_type":"git.worktree_removed","timestamp":"2025-12-13T21:01:00.000Z","agent_id":"system","context":{"task_id":"task-123","worktree_path":"/worktrees/task-123-auth"}}
{"version":"1.1.0","event_type":"container.stopped","timestamp":"2025-12-13T21:01:05.000Z","agent_id":"system","context":{"task_id":"task-123","container_id":"dev-abc123"},"container":{"container_id":"dev-abc123","exit_code":0}}
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

## Querying Events

### Using jq

```bash
# All events for a specific task
jq -c 'select(.context.task_id == "task-123")' events.jsonl

# All git events
jq -c 'select(.event_type | startswith("git."))' events.jsonl

# One-way door decisions
jq -c 'select(.decision.reversibility.type == "one-way-door")' events.jsonl

# Events in a specific container
jq -c 'select(.context.container_id == "dev-abc123")' events.jsonl

# Failed quality gates
jq -c 'select(.event_type == "git.local_pr_rejected")' events.jsonl

# Agent activity timeline
jq -c 'select(.agent_id == "@backend-engineer")' events.jsonl | jq -s 'sort_by(.timestamp)'

# Commits by agent with GPG info
jq -c 'select(.event_type == "git.commit") | {agent: .agent_id, sha: .git.sha, gpg: .git.gpg_key_id}' events.jsonl
```

### Extracting Decision Log

Generate `decision-log.jsonl` from the unified event stream:

```bash
jq -c 'select(.event_type | startswith("decision."))' events.jsonl > decision-log.jsonl
```

---

## JSON Schema

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
      "pattern": "^(lifecycle|activity|coordination|hook|git|task|container|decision|system)\\.[a-z_]+$",
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
      "enum": ["mcp", "hook", "cli", "system"],
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
    "context": {
      "type": "object",
      "properties": {
        "task_id": {"type": "string"},
        "branch_name": {"type": "string"},
        "worktree_path": {"type": "string"},
        "container_id": {"type": "string"},
        "pr_number": {"type": "integer"},
        "decision_id": {"type": "string"}
      },
      "description": "Cross-reference context for unified tracking"
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
    "git": {
      "type": "object",
      "properties": {
        "operation": {"type": "string"},
        "sha": {"type": "string"},
        "branch_name": {"type": "string"},
        "from_branch": {"type": "string"},
        "gpg_key_id": {"type": "string"},
        "gpg_fingerprint": {"type": "string"},
        "signer_agent_id": {"type": "string"},
        "message": {"type": "string"},
        "files_changed": {"type": "integer"},
        "insertions": {"type": "integer"},
        "deletions": {"type": "integer"},
        "merge_method": {"type": "string", "enum": ["merge", "squash", "rebase"]}
      },
      "description": "Git operation details"
    },
    "task": {
      "type": "object",
      "properties": {
        "task_id": {"type": "string"},
        "title": {"type": "string"},
        "from_state": {"type": "string"},
        "to_state": {"type": "string"},
        "assigned_to": {"type": "string"},
        "labels": {"type": "array", "items": {"type": "string"}},
        "ac_index": {"type": "integer"},
        "ac_text": {"type": "string"}
      },
      "description": "Task operation details"
    },
    "container": {
      "type": "object",
      "properties": {
        "container_id": {"type": "string"},
        "image": {"type": "string"},
        "exit_code": {"type": "integer"},
        "secrets_injected": {"type": "array", "items": {"type": "string"}},
        "network_mode": {"type": "string"},
        "resource_limits": {
          "type": "object",
          "properties": {
            "memory_mb": {"type": "integer"},
            "cpu_cores": {"type": "number"}
          }
        }
      },
      "description": "Container details"
    },
    "decision": {
      "type": "object",
      "properties": {
        "decision_id": {"type": "string"},
        "category": {"type": "string"},
        "reversibility": {
          "type": "object",
          "properties": {
            "type": {"type": "string", "enum": ["one-way-door", "two-way-door"]},
            "lock_in_factors": {"type": "array", "items": {"type": "string"}},
            "reversal_cost": {"type": "string", "enum": ["trivial", "low", "medium", "high", "prohibitive"]},
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
      },
      "description": "Decision details (integrates with decision-tracker)"
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

## State Machine

Events drive state transitions. The git workflow becomes a state machine:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           Task Lifecycle State Machine                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  IDLE ──[task.created]──► TASK_READY                                        │
│                              │                                               │
│                    [git.branch_created]                                      │
│                              ▼                                               │
│                         BRANCH_READY                                         │
│                              │                                               │
│                   [git.worktree_created]                                     │
│                              ▼                                               │
│                        WORKTREE_READY                                        │
│                              │                                               │
│                     [container.started]                                      │
│                              ▼                                               │
│                       CONTAINER_READY                                        │
│                              │                                               │
│                     [lifecycle.started]                                      │
│                              ▼                                               │
│                        AGENT_WORKING ◄───────────────────┐                   │
│                              │                           │                   │
│                     [git.local_pr_submitted]    [git.local_pr_rejected]      │
│                              ▼                           │                   │
│                      AWAITING_APPROVAL ──────────────────┘                   │
│                              │                                               │
│                    [git.local_pr_approved]                                   │
│                              ▼                                               │
│                          APPROVED                                            │
│                              │                                               │
│                        [git.pushed]                                          │
│                              ▼                                               │
│                           PUSHED                                             │
│                              │                                               │
│                       [git.pr_created]                                       │
│                              ▼                                               │
│                          PR_OPEN                                             │
│                              │                                               │
│                        [git.merged]                                          │
│                              ▼                                               │
│                           MERGED                                             │
│                              │                                               │
│                      [task.completed]                                        │
│                              ▼                                               │
│                            DONE                                              │
│                              │                                               │
│            [git.worktree_removed + container.stopped]                        │
│                              ▼                                               │
│                         CLEANED_UP                                           │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Notes

### File Naming Convention

```
events-{date}.jsonl              # Daily event log
events-{agent_id}-{date}.jsonl   # Per-agent log (optional)
decision-log.jsonl               # Filtered view: decision.* events only
```

### Validation Code (Python)

```python
import json
import jsonschema
from pathlib import Path
from datetime import datetime

SCHEMA = json.loads(Path("schemas/event-v1.1.0.json").read_text())

def validate_event(event: dict) -> bool:
    """Validate event against JSON Schema."""
    try:
        jsonschema.validate(event, SCHEMA)
        return True
    except jsonschema.ValidationError as e:
        print(f"Validation error: {e.message}")
        return False

def emit_event(event_type: str, agent_id: str, **kwargs) -> dict:
    """Create and return a valid event."""
    event = {
        "version": "1.1.0",
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent_id": agent_id,
        **kwargs
    }
    if validate_event(event):
        return event
    raise ValueError("Invalid event")

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

# Example: Emit a git commit event
commit_event = emit_event(
    "git.commit",
    "@backend-engineer",
    message="feat: add authentication",
    context={"task_id": "task-123", "branch_name": "task-123-auth"},
    git={
        "sha": "abc123",
        "gpg_key_id": "AGENT-001",
        "files_changed": 3
    }
)
```

---

## Integration with Flowspec

Events are emitted at each workflow stage:

| Flowspec Command | Events Emitted |
|-----------------|----------------|
| `/flow:assess` | `task.created`, `decision.made` (assessment decisions) |
| `/flow:specify` | `task.state_changed`, `decision.made` (spec decisions) |
| `/flow:plan` | `decision.made` (architecture decisions), `task.state_changed` |
| `/flow:implement` | `lifecycle.*`, `activity.*`, `git.commit`, `task.ac_checked` |
| `/flow:validate` | `decision.made` (review decisions), `git.local_pr_*` |
| `/flow:operate` | `container.*`, `system.*` |

---

## Migration Path

1. **Phase 1** (v1.0.0 → v1.1.0): Add `context`, `git`, `task`, `container` objects
2. **Phase 2**: Migrate decision-tracker to use unified event stream
3. **Phase 3**: Implement git workflow event emission
4. **Phase 4** (v2.0.0): Deprecate legacy `status` field

---

## Related Documents

- [Decision Tracker](decision-tracker.md) - Decision logging format (now unified)
- [Git Workflow Objectives](git-workflow-objectives.md) - Git workflow requirements

## References

- [JSON Lines Specification](https://jsonlines.org/)
- [JSON Schema Draft-07](https://json-schema.org/draft-07/json-schema-release-notes.html)
- [OpenTelemetry Trace Context](https://www.w3.org/TR/trace-context/)
- [Claude Code Hooks Documentation](https://docs.anthropic.com/en/docs/claude-code/hooks)
