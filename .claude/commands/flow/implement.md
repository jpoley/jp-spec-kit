---
description: Orchestrate implementation workflow using composable commands.
loop: inner
# Loop Classification: INNER LOOP
# This command orchestrates the implementation phase via composable sub-commands.
---

## User Input

```text
$ARGUMENTS
```

## Execution Instructions

This command orchestrates the implementation workflow by invoking composable sub-commands in sequence. Each phase can also be run independently.

**For /flow:implement**: Output state will be `workflow:In Implementation`.

### Phase 0: Extract Context Variables

Derive task and feature IDs from current branch:
```bash
# Derive TASK_ID from current branch (e.g., "task-1234")
TASK_ID=${TASK_ID:-$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")}

# Derive FEATURE_ID from current branch (e.g., "feature-1234" or "feat-1234")
FEATURE_ID=${FEATURE_ID:-$(git branch --show-current 2>/dev/null | grep -Eo '(feature|feat)-[0-9]+' || echo "")}
```

Check for PRP context bundle (`docs/prp/<task-id>.md`) and load if present.

### Phase 1: Discover Tasks and Context

Search for implementation tasks. Use TASK_ID from branch if available, otherwise fall back to user arguments:
```bash
if [ -n "$TASK_ID" ]; then
  backlog task "$TASK_ID" --plain
else
  backlog search "$ARGUMENTS" --plain
  backlog task list -s "To Do" --plain
fi
```

If no tasks found, suggest running `/flow:specify` first.

Discover related specs and ADRs in `docs/prd/`, `docs/specs/`, `docs/adr/`.

### Phase 2: Quality Gate

Run quality gate validation:
```
/flow:gate
```

Validates spec quality meets threshold (default 70/100). Proceed only if gate passes.

**Note**: Each sub-command (`/flow:gate`, `/flow:rigor`, etc.) exits on failure. If a phase fails, the orchestration stops and the error is reported.

### Phase 3: Rigor Rules

Validate rigor rules:
```
/flow:rigor
```

Validates branch naming (EXEC-002), worktree (EXEC-001), and backlog linkage (EXEC-004).

### Phase 4: Implementation

Execute parallel implementation:
```
/flow:build
```

Launches frontend/backend/AI-ML agents based on task labels.

### Phase 5: Code Review

Conduct code review:
```
/flow:review
```

Verifies code quality and acceptance criteria completion.

### Phase 6: Pre-PR Validation

Run pre-PR checks:
```
/flow:pre-pr
```

Validates lint, tests, formatting, DCO sign-off, and all acceptance criteria.

### Deliverables

Implementation is **code + documents + tests**:
1. **Code**: Reviewed, passing CI
2. **Docs**: API docs, comments, ADRs
3. **Tests**: Unit, integration, coverage met

### Post-Completion

Emit workflow event (using variables from Phase 0):
```bash
flowspec hooks emit implement.completed --spec-id "$FEATURE_ID" --task-id "$TASK_ID"
```
