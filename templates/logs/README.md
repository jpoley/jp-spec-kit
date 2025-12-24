# Project Logs Directory

This directory contains operational logs for AI-assisted development work.

## Directory Structure

```
logs/
├── events/           # Event logs (sessions, workflows, hooks, git)
│   └── YYYY-MM-DD.jsonl
├── decisions/        # Decision logs (architectural, implementation)
│   └── YYYY-MM-DD.jsonl
└── README.md         # This file
```

## Log Types

### Event Log (`events/<date>.jsonl`)

Records significant events during development sessions.

**Format**: JSONL (one JSON object per line)

```jsonl
{"timestamp": "2024-12-19T10:30:00Z", "entry_id": "log_abc123", "source": "workflow", "category": "workflow.completed", "message": "Completed /flow:implement", "task_id": "task-123", "workflow_phase": "implement", "success": true}
```

**Event Categories**:
- `session.start`, `session.end` - Claude Code session lifecycle
- `workflow.started`, `workflow.completed`, `workflow.failed` - Flowspec workflow events
- `task.created`, `task.updated`, `task.status_changed`, `task.completed` - Backlog task events
- `hook.executed`, `hook.failed` - Claude/git hook execution
- `git.commit`, `git.push`, `git.branch` - Git operations
- `decision.made` - Decision event (cross-reference to decisions log)
- `error.occurred` - Error events

**Sources**:
- `agent` - AI agent action
- `human` - Human operator action
- `hook` - Claude or git hook
- `backlog` - Backlog status change
- `workflow` - Flowspec workflow command
- `system` - System-generated event

### Decision Log (`decisions/<date>.jsonl`)

Records significant decisions made during development.

**Format**: JSONL (one JSON object per line)

```jsonl
{"timestamp": "2024-12-19T10:00:00Z", "entry_id": "log_def456", "source": "agent", "decision": "Use JWT for session management", "context": "Evaluating auth approaches for API", "rationale": "Stateless, scalable, industry standard", "alternatives": ["session cookies", "OAuth only"], "impact": "medium", "reversible": true, "related_tasks": ["task-123"]}
```

**Fields**:
- `timestamp`: ISO 8601 UTC timestamp
- `entry_id`: Unique log entry identifier
- `source`: Who/what made the decision (agent, human, system)
- `decision`: The decision made
- `context`: What prompted this decision
- `rationale`: Why this choice was made
- `alternatives`: Other options considered
- `impact`: `low`, `medium`, `high`, `critical`
- `reversible`: Boolean - can this be easily changed later?
- `related_tasks`: (optional) Backlog task IDs affected
- `category`: (optional) Decision category (architecture, implementation, tooling)

## Automatic Logging

When using Flowspec with Claude Code, logs are created automatically:

1. **Session events**: Logged on session start/end via Claude hooks
2. **Workflow events**: Logged when running `/flow:*` commands
3. **Task events**: Logged on backlog task status changes
4. **Hook events**: Logged on hook execution
5. **Git events**: Logged on commits and pushes (via git hooks)

## Manual Logging

### Using the CLI

```bash
# Log a session event
python -m flowspec_cli.logging.cli session-start

# Log a decision
python -m flowspec_cli.logging.cli decision \
  --decision "Use PostgreSQL for persistence" \
  --context "Choosing database for user data" \
  --rationale "ACID compliance, proven reliability" \
  --alternatives SQLite MongoDB DynamoDB \
  --impact high \
  --reversible

# Log a custom event
python -m flowspec_cli.logging.cli event \
  --category workflow.completed \
  --message "Completed implementation" \
  --task-id task-123

# Log git operations
python -m flowspec_cli.logging.cli git-commit \
  --hash abc123def \
  --message "Add user authentication" \
  --files-changed 5
```

### Querying Logs

```bash
# View today's events
cat logs/events/$(date +%Y-%m-%d).jsonl | jq .

# Find workflow failures
cat logs/events/*.jsonl | jq 'select(.category == "workflow.failed")'

# Find high-impact decisions
cat logs/decisions/*.jsonl | jq 'select(.impact == "high" or .impact == "critical")'

# List session starts
cat logs/events/*.jsonl | jq 'select(.category == "session.start")'
```

## Integration with Flowspec

- **RIGOR Rules**: EXEC-009 (advisory) and EXEC-010 (blocking) enforce logging
- **Hooks**: Session start/end hooks automatically log events
- **Workflows**: `/flow:*` commands log workflow events
- **Backlog**: Task status changes are automatically logged

## Retention

Logs should be committed to git for project history. Consider:
- Weekly/monthly archival for large projects
- Summarization scripts for long-running projects
- Periodic cleanup of old logs (beyond retention period)
