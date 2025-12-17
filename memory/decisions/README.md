# Decision Logs

This directory contains JSONL decision logs for all workflow decisions. Each task has its own decision log file.

## Directory Structure

```
memory/decisions/
├── README.md           # This file
├── task-541.jsonl      # Decision log for task-541
├── task-542.jsonl      # Decision log for task-542
└── ...                 # One file per task
```

## JSONL Schema

Each line in a `.jsonl` file is a valid JSON object with this schema:

```json
{
  "timestamp": "2025-12-17T14:30:00Z",
  "task_id": "task-542",
  "phase": "setup|execution|freeze|validation|pr",
  "decision": "What was decided",
  "rationale": "Why this decision was made",
  "alternatives": ["Option A considered", "Option B considered"],
  "actor": "@agent-name",
  "context": {
    "files_affected": ["src/file.py"],
    "related_tasks": ["task-120"],
    "tags": ["architecture", "security"]
  }
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO 8601 | When the decision was made |
| `task_id` | string | Task ID (e.g., "task-542") |
| `phase` | enum | Workflow phase: setup, execution, freeze, validation, pr |
| `decision` | string | What was decided |
| `rationale` | string | Why this decision was made |
| `actor` | string | Who made the decision (e.g., "@backend-engineer") |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `alternatives` | array | Other options that were considered |
| `context.files_affected` | array | Files impacted by this decision |
| `context.related_tasks` | array | Other task IDs related to this decision |
| `context.tags` | array | Categorization tags |

## Query Examples

### View all decisions for a task

```bash
cat memory/decisions/task-542.jsonl | jq '.'
```

### Filter by phase

```bash
jq 'select(.phase == "execution")' memory/decisions/task-542.jsonl
```

### Search by keyword

```bash
jq 'select(.decision | contains("timeout"))' memory/decisions/task-*.jsonl
```

### Count decisions per phase

```bash
jq -s 'group_by(.phase) | map({phase: .[0].phase, count: length})' memory/decisions/task-542.jsonl
```

### Find all architecture decisions

```bash
jq 'select(.context.tags | index("architecture"))' memory/decisions/task-*.jsonl
```

### Get decisions by actor

```bash
jq 'select(.actor == "@backend-engineer")' memory/decisions/task-*.jsonl
```

## Logging Decisions

### Using the helper script

```bash
./scripts/bash/rigor-decision-log.sh \
  --task task-542 \
  --phase execution \
  --decision "Selected JSONL format for decision logs" \
  --rationale "Append-only, git-friendly, streaming-compatible" \
  --actor "@platform-engineer" \
  --alternatives "SQLite,Plain text,YAML"
```

### Manual logging

```bash
echo '{"timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","task_id":"task-542","phase":"execution","decision":"...","rationale":"...","actor":"@agent"}' >> memory/decisions/task-542.jsonl
```

## Best Practices

1. **Log Early, Log Often**: Record decisions as they're made, not after
2. **Include Rationale**: Future readers need to understand WHY
3. **Document Alternatives**: Record what was considered and rejected
4. **Use Consistent Tags**: Makes searching easier later
5. **Link Related Tasks**: Creates traceability across the project

## Decision Types to Log

- Architecture choices
- Technology selections
- Design pattern decisions
- Security approach choices
- Performance trade-offs
- API design decisions
- Data model changes
- Breaking changes

## Integration with Rigor Rules

Decision logging is enforced by rigor rule **EXEC-003**:

> All significant decisions must be logged with task traceability in JSONL format.

See `templates/commands/flow/_rigor-rules.md` for full rule details.
