# Daily Logs Directory

This directory contains daily operational logs for AI-assisted development work.

## Log Files

### Active Work Log (`active-work-<date>.jsonl`)

Tracks AI micro-tasks and active work items for the day.

**Format**: JSONL (one JSON object per line)

```jsonl
{"timestamp": "2024-12-19T10:30:00Z", "task_id": "task-123", "action": "started", "description": "Implementing user auth endpoint"}
{"timestamp": "2024-12-19T11:45:00Z", "task_id": "task-123", "action": "completed", "description": "Implemented user auth endpoint", "artifacts": ["src/auth/handler.py"]}
```

**Fields**:
- `timestamp`: ISO 8601 timestamp
- `task_id`: Reference to backlog task or beads issue
- `action`: `started`, `progress`, `completed`, `blocked`, `deferred`
- `description`: Brief description of the work
- `artifacts`: (optional) Files created/modified
- `blockers`: (optional) What's blocking progress

### Decision Log (`decision-log-<date>.jsonl`)

Records significant decisions made during development.

**Format**: JSONL (one JSON object per line)

```jsonl
{"timestamp": "2024-12-19T10:00:00Z", "decision": "Use JWT for session management", "context": "Evaluating auth approaches for API", "rationale": "Stateless, scalable, industry standard", "alternatives": ["session cookies", "OAuth only"], "impact": "medium", "reversible": true}
```

**Fields**:
- `timestamp`: ISO 8601 timestamp
- `decision`: The decision made
- `context`: What prompted this decision
- `rationale`: Why this choice was made
- `alternatives`: Other options considered
- `impact`: `low`, `medium`, `high`, `critical`
- `reversible`: Boolean - can this be easily changed later?
- `related_tasks`: (optional) Backlog task IDs affected

## Usage

### Creating Logs

Logs are created automatically when following the RIGOR rules (EXEC-009, EXEC-010).

**Manual creation**:
```bash
# Create today's decision log
echo '{"timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'", "decision": "...", "context": "...", "rationale": "...", "alternatives": [], "impact": "medium", "reversible": true}' >> logs/decision-log-$(date +%Y-%m-%d).jsonl

# Create today's active work log
echo '{"timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'", "task_id": "task-xxx", "action": "started", "description": "..."}' >> logs/active-work-$(date +%Y-%m-%d).jsonl
```

### Querying Logs

```bash
# View today's decisions
cat logs/decision-log-$(date +%Y-%m-%d).jsonl | jq .

# Find high-impact decisions
cat logs/decision-log-*.jsonl | jq 'select(.impact == "high" or .impact == "critical")'

# List completed work today
cat logs/active-work-$(date +%Y-%m-%d).jsonl | jq 'select(.action == "completed")'
```

## Integration with RIGOR Rules

- **EXEC-009**: Advisory rule requiring daily active work logging
- **EXEC-010**: Blocking rule requiring daily decision logging

These rules ensure continuity across AI sessions and human review of AI-made decisions.

## Retention

Logs should be committed to git for project history. Consider:
- Weekly/monthly archival for large projects
- Summarization scripts for long-running projects
