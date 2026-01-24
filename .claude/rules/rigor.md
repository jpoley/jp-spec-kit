# Rigor Rules

Quality gates that enforce workflow discipline. These apply to ALL Flowspec users.

## Enforcement Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| **strict** | Block workflow if violated | Default for BLOCKING rules |
| **warn** | Warn but allow continuation | Advisory rules |
| **off** | Disable rule | Emergency use only |

Configure in `.flowspec/rigor-config.yml` (optional, created per-project) or accept defaults.

## Key Blocking Rules

### Setup Phase (assess, specify)

| Rule | Requirement |
|------|-------------|
| SETUP-001 | Clear implementation plan required |
| SETUP-002 | Dependencies must be documented |
| SETUP-003 | Testable acceptance criteria required |

### Execution Phase (implement)

| Rule | Requirement |
|------|-------------|
| EXEC-001 | Git worktree required |
| EXEC-002 | Branch naming convention |
| EXEC-003 | Decision logging required |
| EXEC-004 | Backlog task linkage |
| EXEC-006 | Workflow state tracking |

### Validation Phase (validate)

| Rule | Requirement |
|------|-------------|
| VALID-002 | Lint and SAST must pass |
| VALID-004 | Zero merge conflicts |
| VALID-005 | All acceptance criteria met |
| VALID-007 | CI checks pass locally |

### PR Phase

| Rule | Requirement |
|------|-------------|
| PR-001 | DCO sign-off required |

## Common Violations and Fixes

```bash
# SETUP-001: Missing implementation plan
backlog task edit <task-id> --plan $'1. Research\n2. Implement\n3. Test'

# EXEC-001: Git worktree required
BRANCH="$(hostname -s | tr '[:upper:]' '[:lower:]')/task-<id>/slug"
git worktree add "../$(basename "$BRANCH")" "$BRANCH"

# EXEC-003: Decision logging required
./scripts/bash/rigor-decision-log.sh \
  --task task-<id> \
  --phase execution \
  --decision "Description" \
  --rationale "Why this choice" \
  --actor "@developer"

# VALID-005: Unchecked acceptance criteria
backlog task edit <task-id> --check-ac 1 --check-ac 2
```

## Override (Emergency Only)

In `.flowspec/rigor-config.yml`:

```yaml
enforcement:
  rules:
    EXEC-005: warn  # Set specific rule to warn mode
```

**Never disable BLOCKING rules without team approval.**

## Full Reference

See `.claude/partials/flow/_rigor-rules.md` for complete rule definitions, validation scripts, and remediation steps.
