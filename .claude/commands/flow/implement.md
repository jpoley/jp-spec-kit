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

**For /flow:implement**: Required input state is `workflow:Planned`. Output state will be `workflow:In Implementation`.

### Phase 1: Discover Tasks and Context

Search for implementation tasks:
```bash
backlog search "$ARGUMENTS" --plain
backlog task list -s "To Do" --plain
```

If no tasks found, suggest running `/flow:specify` first.

Discover related specs and ADRs in `docs/prd/`, `docs/specs/`, `docs/adr/`.

### Phase 2: Quality Gate

Run quality gate validation:
```
/flow:gate
```

Validates spec quality meets threshold (default 70/100). Proceed only if gate passes.

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

Emit workflow event:
```bash
flowspec hooks emit implement.completed --spec-id "$FEATURE_ID" --task-id "$TASK_ID"
```
