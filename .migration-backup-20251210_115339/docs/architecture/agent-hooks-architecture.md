# Agent Hooks System Architecture

**Version**: 1.0
**Date**: 2025-12-02
**Author**: @software-architect
**Status**: Proposed

---

## Executive Summary

The Agent Hooks system transforms JP Spec Kit from a **linear, synchronous workflow engine** into an **event-driven automation platform**. It enables automated quality gates, workflow orchestration, and third-party integrations without modifying core workflow commands.

**Core Design Principles**:
1. **Tool-Agnostic**: Works with Claude Code, Gemini, Copilot, or headless automation
2. **Fail-Safe**: Hook errors don't break workflows (fail-open by default)
3. **Secure**: Multi-layer sandbox prevents malicious scripts
4. **Observable**: Comprehensive audit logging for debugging and compliance
5. **Extensible**: Supports future features (webhooks, parallel execution) without breaking changes

**System Components**:
- **Event Model**: Canonical event types (spec.created, task.completed, implement.completed)
- **Hook Configuration**: YAML-based declarative hook definitions
- **Hook Runner**: Secure execution engine with timeout enforcement
- **Audit Logger**: JSON Lines audit trail for compliance

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         JP Spec Kit CLI                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐        │
│  │ /jpspec:specify│  │/jpspec:implement│  │ backlog task   │        │
│  │                │  │                 │  │   operations   │        │
│  └────────┬───────┘  └────────┬────────┘  └────────┬───────┘        │
│           │                   │                     │                │
│           └───────────────────┴─────────────────────┘                │
│                               │                                      │
│                    ┌──────────▼──────────┐                           │
│                    │   Event Emitter     │                           │
│                    │  - Generate Event   │                           │
│                    │  - Assign ULID      │                           │
│                    │  - Add Metadata     │                           │
│                    └──────────┬──────────┘                           │
│                               │                                      │
│                    ┌──────────▼──────────┐                           │
│                    │    Event Object     │                           │
│                    │  {                  │                           │
│                    │   event_type,       │                           │
│                    │   event_id,         │                           │
│                    │   timestamp,        │                           │
│                    │   context,          │                           │
│                    │   artifacts         │                           │
│                    │  }                  │                           │
│                    └──────────┬──────────┘                           │
└───────────────────────────────┼──────────────────────────────────────┘
                                │
                     ┌──────────▼──────────┐
                     │   Hook Dispatcher   │
                     │  - Load hooks.yaml  │
                     │  - Match events     │
                     │  - Dispatch hooks   │
                     └──────────┬──────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
   ┌──────────▼──────┐ ┌────────▼────────┐ ┌────▼──────────┐
   │ Hook Matcher    │ │ Hook Matcher    │ │ Hook Matcher  │
   │ - Event type    │ │ - Event type    │ │ - Event type  │
   │ - Filters       │ │ - Filters       │ │ - Filters     │
   │ ✓ Matched       │ │ ✗ No match      │ │ ✓ Matched     │
   └──────────┬──────┘ └─────────────────┘ └────┬──────────┘
              │                                  │
   ┌──────────▼──────────────────────────────────▼──────────┐
   │              Hook Execution Engine                     │
   │  ┌──────────────────────────────────────────────────┐  │
   │  │ Security Validation                              │  │
   │  │  - Path allowlist (.specify/hooks/)              │  │
   │  │  - No path traversal                             │  │
   │  │  - Script exists                                 │  │
   │  └──────────────────────────────────────────────────┘  │
   │  ┌──────────────────────────────────────────────────┐  │
   │  │ Environment Setup                                │  │
   │  │  - Sanitize environment variables                │  │
   │  │  - Set working directory                         │  │
   │  │  - Prepare stdin (event JSON)                    │  │
   │  └──────────────────────────────────────────────────┘  │
   │  ┌──────────────────────────────────────────────────┐  │
   │  │ Script Execution (subprocess)                    │  │
   │  │  - Timeout enforcement (SIGTERM → SIGKILL)       │  │
   │  │  - Capture stdout/stderr                         │  │
   │  │  - Return exit code                              │  │
   │  └──────────────────────────────────────────────────┘  │
   │  ┌──────────────────────────────────────────────────┐  │
   │  │ Error Handling                                   │  │
   │  │  - fail_mode: continue → log, continue           │  │
   │  │  - fail_mode: stop → log, raise error            │  │
   │  └──────────────────────────────────────────────────┘  │
   └────────────────────────┬───────────────────────────────┘
                            │
                 ┌──────────▼──────────┐
                 │   Audit Logger      │
                 │ - JSONL format      │
                 │ - Append-only       │
                 │ - Log rotation      │
                 │ - 10MB chunks       │
                 └──────────┬──────────┘
                            │
                            ▼
              .specify/hooks/audit.log
```

---

## Component Specifications

### 1. Event Emitter

**Responsibility**: Generate and emit workflow events

**Location**: `src/specify_cli/events/emitter.py`

**Interface**:
```python
class EventEmitter:
    def emit(
        self,
        event_type: str,
        feature: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        artifacts: Optional[List[Artifact]] = None,
    ) -> Event:
        """
        Emit workflow event and trigger matching hooks.

        Args:
            event_type: Canonical event type (e.g., "implement.completed")
            feature: Feature name/identifier
            context: Event-specific context (agent, task_id, state)
            artifacts: Produced artifacts (files, reports)

        Returns:
            Event object with generated ID and timestamp

        Raises:
            No exceptions (fails gracefully on hook errors)
        """
```

**Event Types Emitted**:
- **Workflow Events**: workflow.assessed, spec.created, plan.created, implement.completed, validate.completed, deploy.completed
- **Task Events**: task.created, task.updated, task.status_changed, task.ac_checked, task.completed

**Event ID Generation**: ULID-based (`evt_01HQZX123ABC`)
- Sortable by creation time
- Globally unique
- URL-safe

**Performance Requirement**: Event emission adds <50ms to workflow commands

### 2. Hook Configuration Parser

**Responsibility**: Load and validate hooks.yaml configuration

**Location**: `src/specify_cli/hooks/config_parser.py`

**Configuration File**: `.specify/hooks/hooks.yaml`

**Schema Validation**: JSON Schema (`hooks-config.schema.json`)

**Validation Checks**:
1. JSON Schema compliance
2. Hook names unique
3. Scripts exist in `.specify/hooks/`
4. No path traversal in script paths
5. Timeouts within 1-600s range
6. Event types recognized

**Error Handling**:
- Invalid config: Log error, disable hooks
- Missing config: No hooks configured (valid state)
- Schema errors: Detailed error messages with line numbers

### 3. Event Matcher

**Responsibility**: Match events to hook configurations

**Location**: `src/specify_cli/hooks/matcher.py`

**Matching Logic**:

**Simple Match**:
```yaml
events:
  - type: "spec.created"
```
Matches if `event.event_type == "spec.created"`

**Wildcard Match**:
```yaml
events:
  - type: "task.*"  # All task events
```
Uses `fnmatch` for wildcard expansion

**Filtered Match**:
```yaml
events:
  - type: "task.completed"
    filter:
      priority: ["high", "critical"]
      labels_any: ["backend", "frontend"]
```

**Filter Semantics**:
- **Exact match**: `priority: "high"` - Field must equal value
- **Array match (OR)**: `priority: ["high", "critical"]` - Field in list
- **Array match (ANY)**: `labels_any: ["a", "b"]` - At least one label present
- **Array match (ALL)**: `labels_all: ["a", "b"]` - All labels present

**Performance**: O(n*m) where n=hooks, m=event matchers per hook
- Acceptable for v1 (<100 hooks, <5 matchers each)
- Can optimize with indexing in v2 if needed

### 4. Hook Execution Engine

**Responsibility**: Execute hooks securely with timeout enforcement

**Location**: `src/specify_cli/hooks/runner.py`

**Execution Flow**:
1. **Security Validation**: Path allowlist, no path traversal
2. **Environment Setup**: Sanitize env vars, set working directory
3. **Script Execution**: subprocess with timeout, capture output
4. **Error Handling**: Fail-open (continue) or fail-stop (block)

**Security Sandbox**:

**Path Allowlist**:
```python
allowed_dir = Path(project_root) / ".specify/hooks"
script_path.resolve().is_relative_to(allowed_dir)  # Must be True
```

**Timeout Enforcement**:
```python
subprocess.run(
    [script_path],
    timeout=hook.timeout,  # SIGTERM after timeout
    # SIGKILL after timeout + 5s
)
```

**Environment Sanitization**:
```python
# Block shell metacharacters in env values
blocked_chars = [";", "|", "&", "$", "`", "(", ")"]
if any(char in value for char in blocked_chars):
    logger.warning(f"Skipping env var with shell metacharacters")
```

**Event Payload Delivery**:
```python
# Pass event as JSON via stdin (not command-line args)
result = subprocess.run(
    [script_path],
    input=json.dumps(event.to_dict()).encode(),
    capture_output=True,
)
```

**Fail-Safe Design**:
- Default `fail_mode: continue` - log errors, don't block workflow
- Opt-in `fail_mode: stop` - block workflow on hook failure
- Security errors always fail-stop (never continue)

### 5. Audit Logger

**Responsibility**: Log all hook executions for debugging and compliance

**Location**: `src/specify_cli/hooks/audit_logger.py`

**Log Format**: JSON Lines (JSONL)

**Log File**: `.specify/hooks/audit.log`

**Log Entry Schema**:
```json
{
  "timestamp": "2025-12-02T15:30:45.123Z",
  "event_id": "evt_123ABC",
  "hook": "run-tests",
  "status": "success",
  "exit_code": 0,
  "duration_ms": 30333,
  "pid": 12345,
  "stdout_lines": 120,
  "stderr_lines": 0
}
```

**Status Values**:
- `started`: Hook execution began
- `success`: Hook completed with exit code 0
- `failed`: Hook exited with non-zero code
- `timeout`: Hook exceeded timeout
- `error`: Hook execution error (script not found, security error)

**Log Rotation**:
- Rotate when audit.log exceeds 10MB
- Keep last 5 rotated files (audit.log.1 through audit.log.5)
- Total storage: ~50MB max

**Retention**: 30 days (configurable)

---

## Data Flow

### End-to-End Example: Run Tests After Implementation

**Step 1**: User runs workflow command
```bash
/jpspec:implement authentication
```

**Step 2**: Implementation completes, event emitted
```python
# In /jpspec:implement command handler
event_emitter.emit(
    event_type="implement.completed",
    feature="authentication",
    context={"task_id": "task-189", "agent": "backend-engineer"},
    artifacts=[
        Artifact(type="source_code", path="./src/auth/", files_changed=12),
        Artifact(type="tests", path="./tests/test_auth.py", files_changed=3),
    ]
)
```

**Step 3**: Event object created
```json
{
  "event_type": "implement.completed",
  "event_id": "evt_01HQZX123ABC",
  "timestamp": "2025-12-02T15:30:45.123Z",
  "feature": "authentication",
  "context": {
    "task_id": "task-189",
    "agent": "backend-engineer"
  },
  "artifacts": [
    {"type": "source_code", "path": "./src/auth/", "files_changed": 12}
  ]
}
```

**Step 4**: Hook dispatcher loads configuration
```yaml
# .specify/hooks/hooks.yaml
hooks:
  - name: "run-tests"
    events:
      - type: "implement.completed"
    script: "run-tests.sh"
    timeout: 300
    fail_mode: "stop"
```

**Step 5**: Event matcher finds matching hook
```python
matcher.match_hooks(hooks_config, event)
# Returns: [HookConfig(name="run-tests", ...)]
```

**Step 6**: Hook execution engine runs script
```bash
# .specify/hooks/run-tests.sh receives event via stdin
#!/bin/bash
EVENT=$(cat)
FEATURE=$(echo "$EVENT" | jq -r '.feature')

echo "Running tests for feature: $FEATURE"
pytest tests/ -v --cov=src

exit $?
```

**Step 7**: Audit logger records execution
```json
{"timestamp": "2025-12-02T15:30:45.123Z", "event_id": "evt_01HQZX123ABC", "hook": "run-tests", "status": "started", "pid": 12345}
{"timestamp": "2025-12-02T15:31:15.456Z", "event_id": "evt_01HQZX123ABC", "hook": "run-tests", "status": "success", "exit_code": 0, "duration_ms": 30333}
```

**Step 8**: Workflow continues (if tests passed) or blocks (if tests failed)
```python
if result.exit_code != 0 and hook.fail_mode == "stop":
    raise HookExecutionError("Tests failed, blocking workflow")
```

---

## Integration Patterns

### 1. /jpspec Command Integration

**All workflow commands emit events**:
```python
# src/specify_cli/commands/jpspec.py

@cli.command("jpspec:implement")
def implement_command(feature: str):
    """Execute implementation workflow."""

    # ... existing implementation logic ...

    # Emit event at end of successful execution
    event_emitter.emit(
        event_type="implement.completed",
        feature=feature,
        context={
            "workflow_state": "In Implementation",
            "task_id": get_current_task_id(),
            "agent": "backend-engineer"
        },
        artifacts=discover_artifacts(feature),
    )
```

**Event Emission Rules**:
- Emit AFTER successful command completion
- Failures don't emit events (only success events in v1)
- Emit synchronously before command returns
- Hook errors logged but don't break command (fail-safe)

### 2. Backlog Task Integration

**Task operations emit events**:
```python
# src/specify_cli/backlog/commands.py

@cli.command("backlog task edit")
def task_edit(task_id: str, status: str):
    """Edit task metadata."""

    old_status = get_task_status(task_id)
    update_task_status(task_id, status)

    # Emit status change event
    event_emitter.emit(
        event_type="task.status_changed",
        context={
            "task_id": task_id,
            "status_from": old_status,
            "status_to": status,
        }
    )

    # Emit completion event if transitioning to Done
    if status == "Done":
        event_emitter.emit(
            event_type="task.completed",
            context=get_full_task_metadata(task_id)
        )
```

### 3. Claude Code Hook Complementarity

**JP Spec Kit Hooks** (this system):
- **Scope**: Workflow-level events (spec.created, task.completed)
- **Trigger**: /jpspec commands, backlog operations
- **Use Cases**: Automated testing, documentation updates, CI/CD integration

**Claude Code Hooks** (separate system):
- **Scope**: Tool-level events (PreToolUse, PostToolUse, Stop)
- **Trigger**: Tool invocations (Bash, Read, Write)
- **Use Cases**: Permission requests, safety checks, session lifecycle

**Relationship**: Complementary, not overlapping
- JP Spec Kit hooks can create/modify Claude Code hooks as artifacts
- Example: `project.initialized` event creates `.claude/hooks/stop-quality-gate.py`

---

## Technology Stack

### Core Dependencies

**Language**: Python 3.11+

**Key Libraries**:
- `PyYAML` or `ruamel.yaml`: YAML parsing
- `jsonschema`: Configuration validation
- `subprocess`: Secure script execution (stdlib)
- `ulid-py`: Event ID generation
- `rich`: CLI output formatting (already used)

**No New External Dependencies**: All required libraries already in jp-spec-kit

### File System Layout

```
project-root/
├── .specify/
│   ├── hooks/
│   │   ├── hooks.yaml              # Hook configuration
│   │   ├── run-tests.sh            # Example hook script
│   │   ├── update-changelog.py     # Example hook script
│   │   └── audit.log               # Execution audit log
│   ├── plan-template.md
│   └── spec-template.md
├── src/
│   └── specify_cli/
│       ├── events/
│       │   ├── emitter.py          # Event emitter
│       │   ├── schemas/
│       │   │   └── base-event.schema.json
│       ├── hooks/
│       │   ├── config_parser.py    # Configuration parser
│       │   ├── matcher.py          # Event matcher
│       │   ├── runner.py           # Hook execution engine
│       │   ├── audit_logger.py     # Audit logger
│       │   └── schemas/
│       │       └── hooks-config.schema.json
│       └── commands/
│           └── hooks_cli.py        # CLI commands
```

---

## Performance Characteristics

### Latency Targets

**Event Emission Overhead**:
- Target: <50ms per workflow command
- Measurement: Benchmark with/without event emission
- Mitigation: Async emission in v2 if needed

**Hook Dispatch Latency**:
- Target: <100ms from event to script start
- Measurement: Timestamp delta in audit log

**Hook Execution Time**:
- Default timeout: 30 seconds
- Max timeout: 600 seconds (10 minutes)
- User-configurable per hook

### Scalability

**Hooks per Configuration**:
- v1 Target: Up to 100 hooks
- Matching Complexity: O(n*m) where n=hooks, m=matchers
- Acceptable: Most projects will have <20 hooks

**Events per Second**:
- v1 Target: 10 events/second (typical workflow rate)
- Sequential execution: Total time = sum of hook times
- Parallel execution in v2 if needed

**Audit Log Size**:
- Entry size: ~200 bytes per execution
- Rotation: 10MB chunks (50,000 entries)
- Storage: 50MB max (last 5 rotations)

---

## Security Model

### Threat Model

**Attack Vectors**:
1. Malicious script in repository
2. Command injection via event payload
3. Path traversal to execute arbitrary binaries
4. Resource exhaustion (infinite loops, forkbombs)
5. Privilege escalation
6. Data exfiltration

**Mitigations**:

**1. Malicious Scripts**:
- Mitigation: Code review catches malicious hooks.yaml changes
- Residual Risk: LOW (requires repo write access)

**2. Command Injection**:
- Mitigation: Event payload passed via stdin (JSON), not shell args
- Residual Risk: VERY LOW (no shell expansion on stdin)

**3. Path Traversal**:
- Mitigation: Path validation rejects `..` and absolute paths
- Residual Risk: VERY LOW (enforced at config load time)

**4. Resource Exhaustion**:
- Mitigation: Timeout enforcement (SIGTERM → SIGKILL)
- Residual Risk: MEDIUM (forkbomb can stress system briefly)

**5. Privilege Escalation**:
- Mitigation: Hooks run as current user (no setuid, no sudo)
- Residual Risk: LOW (same privileges as CLI user)

**6. Data Exfiltration**:
- Mitigation: Network access controls (v2), audit logging
- Residual Risk: MEDIUM (v1 doesn't restrict network)

### Security Boundaries

**Trusted Zone**: .specify/hooks/ directory
- Only scripts in this directory can execute
- Code review required for changes

**Untrusted Zone**: Event payloads
- Treated as untrusted input
- No shell expansion
- Sanitized before passing to scripts

**Audit Trail**: All executions logged
- Tamper-evident (append-only)
- Enables forensic analysis
- Compliance-ready (SOC2, ISO 27001)

---

## Observability

### Audit Logging

**Log Format**: JSON Lines (JSONL)
**Log Location**: `.specify/hooks/audit.log`

**Log Entry Fields**:
- `timestamp`: ISO 8601 UTC
- `event_id`: Correlate with triggering event
- `hook`: Hook name
- `status`: started | success | failed | timeout | error
- `exit_code`: Process exit code
- `duration_ms`: Execution time
- `pid`: Process ID
- `stdout_lines`, `stderr_lines`: Output line counts

**Log Rotation**: 10MB chunks, keep last 5

### Debugging Tools

**Validate Configuration**:
```bash
specify hooks validate
# Output: Schema errors, missing scripts, warnings
```

**List Configured Hooks**:
```bash
specify hooks list
# Output: Hook names, descriptions, event types
```

**Test Hook Matching**:
```bash
specify hooks run --event-type "task.completed" --dry-run
# Output: Matched hooks (no execution)
```

**View Audit Log**:
```bash
specify hooks audit
# Output: Recent hook executions

specify hooks audit --tail
# Output: Live tail of audit log

specify hooks audit --hook run-tests --status failed
# Output: Filtered executions
```

### Metrics (v2)

**Hook Execution Metrics**:
- Execution count by hook name
- Success/failure rate
- Execution duration (p50, p95, p99)

**Event Metrics**:
- Event emission rate by type
- Events with no matching hooks (unused)
- Events with failed hooks

---

## Extensibility

### v2 Features (Future)

**Webhook Support**:
```yaml
hooks:
  - name: "trigger-deploy"
    events:
      - type: "validate.completed"
    webhook:
      url: "https://ci.example.com/deploy/staging"
      method: "POST"
      headers:
        Authorization: "Bearer ${DEPLOY_TOKEN}"
      payload: "{{ event }}"  # Jinja2 template
    retry:
      max_attempts: 3
      backoff: "exponential"
```

**Parallel Execution**:
```bash
specify hooks run --event-type "implement.completed" --parallel
```

**Conditional Execution**:
```yaml
hooks:
  - name: "deploy-prod"
    events:
      - type: "validate.completed"
        filter:
          branch: "main"
          environment: "production"
```

**Hook Composition/Chaining**:
```yaml
hooks:
  - name: "run-tests"
    output: "test-results.json"
  - name: "upload-coverage"
    input: "test-results.json"
    webhook:
      url: "https://codecov.io/upload"
```

### Plugin Architecture (v3)

**Hook Marketplace**:
```bash
specify hooks search "slack"
specify hooks install slack-notifier
specify hooks update slack-notifier
```

**Community Hooks**:
- Curated hook library for common use cases
- Versioned, tested, documented
- Easy discovery and installation

---

## Testing Strategy

### Unit Tests

**Event Emitter**:
- Event ID format (ULID)
- Payload structure
- Timestamp generation

**Configuration Parser**:
- Schema validation (valid/invalid configs)
- Defaults merging
- Error messages

**Event Matcher**:
- Exact match, wildcard match
- Filter semantics (any, all, array)
- Edge cases (missing fields, null values)

**Execution Engine**:
- Path traversal prevention
- Timeout enforcement
- Environment sanitization
- Fail-open vs fail-stop

### Integration Tests

**End-to-End Workflows**:
- /jpspec:implement → event → hook execution
- Backlog task edit → event → hook execution
- Multi-hook execution (sequential)

**Security Tests**:
- Path traversal attacks blocked
- Shell injection attempts blocked
- Resource exhaustion handled (timeout)

**Error Handling Tests**:
- Missing script (fail-open)
- Hook timeout (fail-open)
- Critical hook failure (fail-stop)

### Performance Tests

**Event Emission Overhead**:
- Benchmark: /jpspec:implement with/without events
- Target: <50ms delta

**Hook Dispatch Latency**:
- Benchmark: Event to script start time
- Target: <100ms

**Audit Log Performance**:
- Benchmark: 1000 executions, measure log write time
- Target: No blocking

---

## Migration Strategy

### v1 Rollout (MVP)

**Phase 1**: Core Infrastructure
- Event model and emitter
- Hook configuration parser
- Hook execution engine
- Audit logger

**Phase 2**: Integration
- Event emission from /jpspec commands
- Event emission from backlog operations
- Security framework

**Phase 3**: Developer Experience
- CLI commands (validate, list, test)
- Example hooks in `specify init`
- Documentation and examples

**Phase 4**: Quality Assurance
- End-to-end tests
- Security review
- Performance benchmarks

### v2 Features (Future)

- Webhook support
- Parallel execution
- Advanced filtering (JSONPath)
- Hook marketplace

---

## References

**Architecture Decision Records**:
- ADR-005: Event Model Architecture
- ADR-006: Hook Execution Model
- ADR-007: Hook Configuration Schema

**Requirements**:
- PRD: `docs/prd/agent-hooks-prd.md`
- Assessment: `docs/assess/agent-hooks-assessment.md`

**Related Systems**:
- Claude Code Hooks: `.claude/hooks/` (complementary)
- Backlog.md: Task state machine (emits task events)
- Workflow Engine: /jpspec commands (emits workflow events)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-02 | @software-architect | Initial architecture document |

---

**Status**: Proposed - Pending review by engineering team and security team.
