---
description: Execute parallel implementation using specialized frontend and backend engineer agents.
loop: inner
# Loop Classification: INNER LOOP
# This command executes the core implementation work via specialized agents.
---

## User Input

```text
$ARGUMENTS
```

## Execution Instructions

This command launches implementation agents in parallel for maximum efficiency. Engineers work exclusively from backlog tasks with defined acceptance criteria.

### Extract Task Context

```bash
# Derive TASK_ID from current branch (e.g., "task-1234")
TASK_ID=${TASK_ID:-$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")}
```

### Prerequisites

Before running this command:
1. Quality gate must pass (`/flow:gate`)
2. Rigor rules must pass (`/flow:rigor`)
3. Backlog tasks must exist with acceptance criteria

### Decision Logging (EXEC-003)

Log all significant decisions during implementation:

```bash
./scripts/bash/rigor-decision-log.sh \
  --task $TASK_ID \
  --phase execution \
  --decision "What was decided" \
  --rationale "Why this choice" \
  --actor "@<agent-name>" \
  --alternatives "Alternative1,Alternative2"
```

**When to log**:
- Technology choices (library, framework, pattern selection)
- Architecture changes
- Trade-off resolutions
- Deferred work decisions

### Frontend Implementation

For UI/mobile components, launch frontend engineer agent:

**Agent Identity**: @frontend-engineer

**Before coding**:
1. Pick a task: `backlog task <task-id> --plain`
2. Assign yourself: `backlog task edit <task-id> -s "In Progress" -a @frontend-engineer`
3. Add implementation plan: `backlog task edit <task-id> --plan $'1. Step 1\n2. Step 2'`

**During implementation**:
- Check ACs as completed: `backlog task edit <task-id> --check-ac 1`

**Requirements**:
1. Build React/React Native components with TypeScript
2. Implement proper state management (Zustand, TanStack Query)
3. Ensure accessibility (WCAG 2.1 AA)
4. Responsive design with design system/tokens
5. Unit tests and integration tests

### Backend Implementation

For API/services, launch backend engineer agent:

**Agent Identity**: @backend-engineer

**Before coding**:
1. Pick a task: `backlog task <task-id> --plain`
2. Assign yourself: `backlog task edit <task-id> -s "In Progress" -a @backend-engineer`
3. Add implementation plan: `backlog task edit <task-id> --plan $'1. Step 1\n2. Step 2'`

**During implementation**:
- Check ACs as completed: `backlog task edit <task-id> --check-ac 1`

**Requirements**:
1. API development (REST, GraphQL, gRPC, CLI)
2. Business logic with input validation
3. Database integration with proper indexes
4. Security (auth, injection prevention)
5. Unit tests and integration tests

**Code Hygiene (MANDATORY)**:
- Remove ALL unused imports before completion
- Run `ruff check --select F401,F841` (Python)
- Validate inputs at API boundaries
- Type hints on all public functions

### AI/ML Implementation

For ML components, launch AI/ML engineer agent:

**Agent Identity**: @ai-ml-engineer

**Before coding**:
1. Pick a task: `backlog task <task-id> --plain`
2. Assign yourself: `backlog task edit <task-id> -s "In Progress" -a @ai-ml-engineer`
3. Add implementation plan: `backlog task edit <task-id> --plan $'1. Step 1\n2. Step 2'`

**During implementation**:
- Check ACs as completed: `backlog task edit <task-id> --check-ac 1`
- Link experiment tracking runs in task notes
- Document model choices and alternatives considered

**Requirements**:
1. Training pipeline implementation
2. MLOps infrastructure (experiment tracking)
3. Model deployment and optimization
4. Performance monitoring

### Parallel Execution

Launch applicable agents in parallel:

| Component | Agent | Criteria |
|-----------|-------|----------|
| UI/Mobile | @frontend-engineer | Task has `frontend` label |
| API/Services | @backend-engineer | Task has `backend` label |
| ML Components | @ai-ml-engineer | Task has `ml` or `ai` label |

### Pre-Completion Checklist

Before marking build complete:

- [ ] No unused imports - Run linter
- [ ] All inputs validated at boundaries
- [ ] Types annotated on public functions
- [ ] Errors handled explicitly
- [ ] Tests pass
- [ ] Linter passes
- [ ] ACs checked in backlog

### Composability

This command can be invoked:
- Standalone: `/flow:build` for implementation-only work
- As part of `/flow:implement` orchestration
- Iteratively after review feedback
