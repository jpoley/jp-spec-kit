# Flowspec Logging System

Flowspec provides a centralized logging system for tracking events and decisions during AI-assisted development. The system uses dual-path logging to separate internal development logs from user project logs.

## Overview

The logging system captures:
- **Events**: Session lifecycle, workflow execution, hook execution, git operations, task changes
- **Decisions**: Architectural decisions, implementation choices, tool selections

### Dual-Path Architecture

| Context | Events Location | Decisions Location |
|---------|----------------|-------------------|
| User projects | `./logs/events/` | `./logs/decisions/` |
| Flowspec development | `.flowspec/logs/events/` | `.flowspec/logs/decisions/` |

The system automatically detects which mode to use based on the project structure.

## Log Format

All logs use JSONL (JSON Lines) format - one JSON object per line, organized by date:

```
logs/
├── events/
│   ├── 2024-12-24.jsonl
│   └── 2024-12-25.jsonl
└── decisions/
    ├── 2024-12-24.jsonl
    └── 2024-12-25.jsonl
```

### Event Schema

```json
{
  "timestamp": "2024-12-24T10:30:00Z",
  "entry_id": "log_abc123def456",
  "source": "workflow",
  "category": "workflow.completed",
  "message": "Completed /flow:implement workflow",
  "details": {"phase": "implement"},
  "task_id": "task-123",
  "workflow_phase": "implement",
  "duration_ms": 5000,
  "success": true
}
```

**Event Categories**:
- `session.start`, `session.end` - Session lifecycle
- `workflow.started`, `workflow.completed`, `workflow.failed` - Workflow execution
- `task.created`, `task.updated`, `task.status_changed`, `task.completed` - Task events
- `hook.executed`, `hook.failed` - Hook execution
- `git.commit`, `git.push`, `git.branch` - Git operations
- `decision.made` - Cross-reference to decision log
- `error.occurred` - Error events

### Decision Schema

```json
{
  "timestamp": "2024-12-24T10:00:00Z",
  "entry_id": "log_xyz789",
  "source": "agent",
  "decision": "Use PostgreSQL for persistence",
  "context": "Choosing database for user data storage",
  "rationale": "ACID compliance, JSON support, proven reliability",
  "alternatives": ["SQLite", "MongoDB", "DynamoDB"],
  "impact": "high",
  "reversible": false,
  "related_tasks": ["task-42"],
  "category": "architecture"
}
```

**Impact Levels**: `low`, `medium`, `high`, `critical`

**Sources**: `agent`, `human`, `hook`, `backlog`, `workflow`, `system`

## Automatic Logging

### Session Events

Session start/end events are logged automatically by Claude hooks:

```bash
# Logged on session start (via .claude/hooks/session-start.sh)
{"category": "session.start", "message": "Claude Code session started", ...}

# Logged on session end
{"category": "session.end", "message": "Claude Code session ended", ...}
```

### Workflow Events

Flowspec commands (`/flow:*`) log workflow events:

```bash
/flow:implement  # Logs workflow.started and workflow.completed
/flow:validate   # Logs workflow.started and workflow.completed
```

### Task Status Changes

Backlog task status changes are logged via the lifecycle hook:

```bash
backlog task edit 42 -s "In Progress"
# Logs: {"category": "task.status_changed", "details": {"old_status": "To Do", "new_status": "In Progress"}}
```

### Hook Execution

All hook executions are logged:

```json
{"category": "hook.executed", "details": {"hook_name": "session-start", "event_type": "session.start"}, "success": true}
```

## Manual Logging

### CLI Interface

```bash
# Log session events
python -m flowspec_cli.logging.cli session-start
python -m flowspec_cli.logging.cli session-end

# Log a decision
python -m flowspec_cli.logging.cli decision \
  --decision "Use REST API" \
  --context "API design phase" \
  --rationale "Simpler to implement" \
  --alternatives GraphQL gRPC \
  --impact medium

# Log custom events
python -m flowspec_cli.logging.cli event \
  --category workflow.completed \
  --message "Completed implementation" \
  --task-id task-123

# Log git operations
python -m flowspec_cli.logging.cli git-commit \
  --hash abc123 \
  --message "Add authentication" \
  --files-changed 5

python -m flowspec_cli.logging.cli git-push \
  --branch feature/auth \
  --remote origin \
  --commits 3

# Show configuration
python -m flowspec_cli.logging.cli config
```

### Python API

```python
from flowspec_cli.logging import DecisionLogger, EventLogger
from flowspec_cli.logging.schemas import DecisionImpact, EventCategory, LogSource

# Log a decision
decision_logger = DecisionLogger()
decision_logger.log(
    decision="Use PostgreSQL",
    context="Database selection",
    rationale="ACID compliance",
    alternatives=["SQLite", "MongoDB"],
    impact=DecisionImpact.HIGH,
    reversible=False,
    related_tasks=["task-42"],
)

# Log an event
event_logger = EventLogger()
event_logger.log(
    category=EventCategory.WORKFLOW_COMPLETED,
    message="Completed implementation",
    task_id="task-42",
    workflow_phase="implement",
    duration_ms=5000,
)

# Convenience methods
event_logger.log_session_start(details={"project": "my-app"})
event_logger.log_workflow_completed(phase="implement", task_id="task-42")
event_logger.log_task_status_changed(task_id="task-42", old_status="To Do", new_status="In Progress")
event_logger.log_git_commit(commit_hash="abc123", message="Add feature", files_changed=5)
```

## Querying Logs

```bash
# View today's events
cat logs/events/$(date +%Y-%m-%d).jsonl | jq .

# Find workflow failures
cat logs/events/*.jsonl | jq 'select(.category == "workflow.failed")'

# Find high-impact decisions
cat logs/decisions/*.jsonl | jq 'select(.impact == "high" or .impact == "critical")'

# Session activity
cat logs/events/*.jsonl | jq 'select(.category | startswith("session."))'

# Task history
cat logs/events/*.jsonl | jq 'select(.task_id == "task-42")'
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `FLOWSPEC_PROJECT_ROOT` | Override project root detection |

### Detection Logic

The system detects flowspec development mode when:
1. `src/flowspec_cli/` directory exists
2. `pyproject.toml` contains `name = "flowspec-cli"`

Otherwise, it uses user project mode.

## Release Workflow

Internal development logs are automatically cleaned during the release process:

```bash
# Dry run - show what would be deleted
./scripts/release.py --dry-run

# Actual release - cleans .flowspec/logs/ before commit
./scripts/release.py
```

This ensures users don't see internal development logs in releases.

## Best Practices

1. **Let automation log events**: Most events are logged automatically via hooks
2. **Log decisions explicitly**: Use the decision logger for important choices
3. **Include rationale**: Always document why a decision was made
4. **Tag with tasks**: Link decisions and events to backlog tasks
5. **Review logs periodically**: Use logs for retrospectives and knowledge transfer

## Integration with RIGOR Rules

The logging system supports RIGOR rules enforcement:
- **EXEC-009** (Advisory): Daily active work logging
- **EXEC-010** (Blocking): Daily decision logging

These rules ensure continuity across AI sessions and human review of AI-made decisions.
