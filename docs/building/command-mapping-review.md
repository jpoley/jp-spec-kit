# Flowspec Command Mapping Review

**Date**: 2026-01-03
**Purpose**: Review all commands to identify core 5 vs supporting, ensure parity between GitHub Copilot and Claude Code

## Core Commands (5 Key Commands)

These are the primary workflow commands that should be prominently featured:

| Command | Description | Copilot Agent | Claude Code Skill |
|---------|-------------|---------------|-------------------|
| `/flow:specify` | Product Requirements Manager | flow-specify.agent.md | workflow-executor |
| `/flow:plan` | Architecture & Platform Planning | flow-plan.agent.md | workflow-executor |
| `/flow:implement` | Multi-Agent Implementation | flow-implement.agent.md | workflow-executor |
| `/flow:validate` | QA, Security, Release Validation | flow-validate.agent.md | workflow-executor |
| `/flow:submit-n-watch-pr` | Submit PR and watch CI/reviews | flow-submit-n-watch-pr.agent.md | workflow-executor |

## REMOVED Commands

| Command | Status | Notes |
|---------|--------|-------|
| `/flow:operate` | **REMOVED** | Outer loop - not flowspec scope. Use `/ops:*` commands or external CI/CD |

### Cleanup Status (as of 2026-01-03):

1. `.flowspec-plugin.yml` - **FIXED** (removed)
2. `templates/commands/flow/_DEPRECATED_operate.md` - **KEPT** as deprecated marker
3. `memory/flowspec_workflow.yml` - **FIXED** (NOTE added, workflow removed)
4. `memory/constitution.md` - **BLOCKED** (protected file)
5. `src/flowspec_cli/__init__.py` - **FIXED** (3 occurrences updated)
6. `.claude/hooks/post-slash-command-emit.py` - **FIXED** (event mapping updated)
7. `tests/` - **FIXED** (all workflow tests updated and passing)
8. `user-docs/` - **STALE** (docs reference deprecated workflow, low priority)
9. `build-docs/` - **STALE** (internal docs, low priority)

## Supporting Commands (Non-Core)

### Flow Namespace - Secondary

| Command | Description | Use Case | Review Status |
|---------|-------------|----------|---------------|
| `/flow:assess` | Evaluate SDD suitability | Before starting work | Keep - important gating |
| `/flow:research` | Market Research & Analysis | Optional phase | Keep - useful but optional |
| `/flow:init` | Initialize constitution | Project setup | Keep - essential for setup |
| `/flow:reset` | Re-run workflow config | Reconfiguration | Keep - utility |
| `/flow:intake` | Process INITIAL docs | Document processing | Keep - intake workflow |
| `/flow:generate-prp` | Generate PRP context | Context bundling | Keep - utility |
| `/flow:map-codebase` | Generate directory trees | Exploration | Consider deprecating |
| `/flow:custom` | Execute custom workflow | Power users | Keep - extensibility |

### Flow Namespace - Security (sec: alias exists)

| Command | Description | Primary Alias | Review Status |
|---------|-------------|---------------|---------------|
| `/flow:security_fix` | Apply security patches | `/sec:fix` | Keep both |
| `/flow:security_report` | Generate security report | `/sec:report` | Keep both |
| `/flow:security_triage` | Triage findings | `/sec:triage` | Keep both |
| `/flow:security_web` | DAST web scanning | `/sec:scan` | Keep both |
| `/flow:security_workflow` | Security workflow | N/A | Review - may consolidate |

### Spec Namespace

| Command | Description | Review Status |
|---------|-------------|---------------|
| `/spec:specify` | Create specifications | Keep - core alt |
| `/spec:plan` | Planning workflow | Keep - core alt |
| `/spec:implement` | Implementation workflow | Keep - core alt |
| `/spec:tasks` | Generate task backlog | Keep |
| `/spec:checklist` | Generate checklist | Keep |
| `/spec:clarify` | Clarification questions | Keep |
| `/spec:analyze` | Cross-artifact analysis | Keep |
| `/spec:init` | Initialize project | Keep |
| `/spec:configure` | Configure settings | Keep |
| `/spec:constitution` | Create constitution | Keep |

### Sec Namespace

| Command | Description | Review Status |
|---------|-------------|---------------|
| `/sec:scan` | Security scanning | Keep - primary |
| `/sec:triage` | Triage findings | Keep - primary |
| `/sec:fix` | Apply patches | Keep - primary |
| `/sec:report` | Generate report | Keep - primary |

### QA Namespace

| Command | Description | Review Status |
|---------|-------------|---------------|
| `/qa:test` | Execute tests | Keep |
| `/qa:review` | Generate checklist | Keep |

### Dev Namespace

| Command | Description | Review Status |
|---------|-------------|---------------|
| `/dev:debug` | Debugging assistance | Keep |
| `/dev:refactor` | Refactoring guidance | Keep |
| `/dev:cleanup` | Prune merged branches | Keep |

### Ops Namespace

| Command | Description | Review Status |
|---------|-------------|---------------|
| `/ops:monitor` | Setup monitoring | Keep - replaces /flow:operate |
| `/ops:respond` | Incident response | Keep |
| `/ops:scale` | Scaling guidance | Keep |

### Arch Namespace

| Command | Description | Review Status |
|---------|-------------|---------------|
| `/arch:decide` | Create ADRs | Keep |
| `/arch:model` | Create data models | Keep |

### Vibe Namespace

| Command | Description | Review Status |
|---------|-------------|---------------|
| `/vibe` | Casual development mode | Keep |

## GitHub Copilot vs Claude Code Parity Check

### Parity Status: **GOOD**

Both platforms have the same `/flow:*` commands - NO `/flow:operate` in either.

### Copilot Agents (.github/agents/)

Total: **43 agent files**

```
flow-assess.agent.md
flow-custom.agent.md
flow-generate-prp.agent.md
flow-implement.agent.md
flow-init.agent.md
flow-intake.agent.md
flow-map-codebase.agent.md
flow-plan.agent.md
flow-research.agent.md
flow-reset.agent.md
flow-security_fix.agent.md
flow-security_report.agent.md
flow-security_triage.agent.md
flow-security_web.agent.md
flow-security_workflow.agent.md
flow-specify.agent.md
flow-submit-n-watch-pr.agent.md
flow-validate.agent.md
spec-analyze.agent.md
spec-checklist.agent.md
spec-clarify.agent.md
spec-configure.agent.md
spec-constitution.agent.md
spec-implement.agent.md
spec-init.agent.md
spec-plan.agent.md
spec-specify.agent.md
spec-tasks.agent.md
sec-fix.agent.md
sec-report.agent.md
sec-scan.agent.md
sec-triage.agent.md
qa-review.agent.md
qa-test.agent.md
dev-cleanup.agent.md
dev-debug.agent.md
dev-refactor.agent.md
ops-monitor.agent.md
ops-respond.agent.md
ops-scale.agent.md
arch-decide.agent.md
arch-model.agent.md
vibe-vibe.agent.md
```

### Claude Code Commands (.claude/commands/flow/)

Total: **18 flow command symlinks** (NO operate.md)

```
assess.md -> templates/commands/flow/assess.md
custom.md -> templates/commands/flow/custom.md
generate-prp.md -> templates/commands/flow/generate-prp.md
implement.md -> templates/commands/flow/implement.md
init.md -> templates/commands/flow/init.md
intake.md -> templates/commands/flow/intake.md
map-codebase.md -> templates/commands/flow/map-codebase.md
plan.md -> templates/commands/flow/plan.md
research.md -> templates/commands/flow/research.md
reset.md -> templates/commands/flow/reset.md
security_fix.md -> templates/commands/flow/security_fix.md
security_report.md -> templates/commands/flow/security_report.md
security_triage.md -> templates/commands/flow/security_triage.md
security_web.md -> templates/commands/flow/security_web.md
security_workflow.md -> templates/commands/flow/security_workflow.md
specify.md -> templates/commands/flow/specify.md
submit-n-watch-pr.md -> templates/commands/flow/submit-n-watch-pr.md
validate.md -> templates/commands/flow/validate.md
```

### Claude Code Skills (.claude/skills/)

Total: **21 skill directories** (supporting skills, not direct commands)

```
architect/
constitution-checker/ (symlink)
context-extractor/
exploit-researcher/
fuzzing-strategist/
gather-learnings/
patch-engineer/
pm-planner/
qa-validator/
sdd-methodology/
security-analyst/
security-codeql/
security-custom-rules/
security-dast/
security-fixer/
security-reporter/
security-reviewer/
security-triage/
security-workflow/
workflow-executor/
```

### Parity Summary

| Check | Copilot | Claude Code | Status |
|-------|---------|-------------|--------|
| `/flow:specify` | flow-specify.agent.md | specify.md | **PARITY** |
| `/flow:plan` | flow-plan.agent.md | plan.md | **PARITY** |
| `/flow:implement` | flow-implement.agent.md | implement.md | **PARITY** |
| `/flow:validate` | flow-validate.agent.md | validate.md | **PARITY** |
| `/flow:submit-n-watch-pr` | flow-submit-n-watch-pr.agent.md | submit-n-watch-pr.md | **PARITY** |
| `/flow:operate` | **NOT PRESENT** | **NOT PRESENT** | **CORRECTLY REMOVED** |

### Remaining Issues

| Issue | Description | Status |
|-------|-------------|--------|
| **Docs still reference /flow:operate** | ~80+ doc files mention it | Low priority - stale docs only |
| **memory/constitution.md** | Protected file, cannot edit | BLOCKED by settings |

## Completed Cleanup (2026-01-03)

### Core Files Fixed
- ✅ `.flowspec-plugin.yml` - Replaced operate with submit-n-watch-pr
- ✅ `memory/flowspec_workflow.yml` - Removed operate workflow, updated metadata
- ✅ `src/flowspec_cli/__init__.py` - 3 occurrences fixed
- ✅ `.claude/hooks/post-slash-command-emit.py` - Event mapping updated
- ✅ `CLAUDE.md` - Already notes removal
- ❌ `memory/constitution.md` - BLOCKED (protected file)

### Test Files Fixed (all 481 workflow tests pass)
- ✅ `tests/test_flowspec_e2e.py` - Workflow ends at Validated, not Deployed
- ✅ `tests/test_flowspec_workflow_integration.py` - TestOperateTransition removed
- ✅ `tests/workflow/test_state_guard.py` - Fixture updated, 6 commands not 7
- ✅ `tests/test_workflow_schema.py` - Fixture updated

### Stale Docs (Low Priority)
The following contain historical references in context/examples but are not blocking:
- `user-docs/` (~30 files)
- `build-docs/` (~50 files)
- These can be cleaned up incrementally or left as historical context
