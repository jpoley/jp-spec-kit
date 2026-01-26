# Rigor Rules

Rigor rules apply to ALL Flowspec users, enforcing workflow quality gates.

## Enforcement Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| **strict** | Block workflow if violated | Default for BLOCKING rules |
| **warn** | Warn but allow continuation | Advisory rules |
| **off** | Disable rule | Emergency use only |

Configure in `.flowspec/rigor-config.yml` or accept defaults (all BLOCKING rules = strict).

## Key Blocking Rules

| Rule | Phase | Requirement |
|------|-------|-------------|
| SETUP-001 | Specify | Clear Plan Required |
| SETUP-002 | Specify | Dependencies Mapped |
| SETUP-003 | Specify | Testable Acceptance Criteria |
| EXEC-001 | Implement | Git Worktree Required |
| EXEC-002 | Implement | Branch Naming Convention |
| EXEC-003 | Implement | Decision Logging Required |
| EXEC-004 | Implement | Backlog Task Linkage |
| VALID-005 | Validate | Acceptance Criteria Met |
| PR-001 | PR | DCO Sign-off Required |

## Branch Naming Convention

Pattern: `{hostname}/task-{id}/{slug-description}`

Example: `macbook-pro/task-541/rigor-rules-include`

## Decision Logging

All significant decisions MUST be logged:

```bash
./scripts/bash/rigor-decision-log.sh \
  --task task-123 \
  --phase execution \
  --decision "Description" \
  --rationale "Why" \
  --actor "@backend-engineer"
```

## Common Violations and Fixes

```bash
# SETUP-001: Missing implementation plan
backlog task edit <task-id> --plan $'1. Research\n2. Implement\n3. Test'

# EXEC-001: Git worktree required
BRANCH="$(hostname -s | tr '[:upper:]' '[:lower:]')/task-<task-id>/feature-slug"
git worktree add "../$(basename $BRANCH)" "$BRANCH"

# VALID-005: Unchecked acceptance criteria
backlog task edit <task-id> --check-ac 1 --check-ac 2
```

## Workflow State Tracking

Tasks MUST have both `workflow:Current` and `workflow-next:Next` labels.

**Workflow States**: Assessed -> Specified -> Planned -> In Implementation -> Validated -> Deployed

## Full Reference

See `.claude/partials/flow/_rigor-rules.md` for complete rule documentation including:
- All validation scripts
- FREEZE phase rules
- VALIDATION phase rules
- PR phase rules
- Utility scripts
