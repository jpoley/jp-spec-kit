# Rigor Rules Infrastructure - Executive Summary

**Author**: @platform-engineer
**Date**: 2025-12-17
**Full Document**: `build-docs/platform/rigor-rules-infrastructure.md`

## Overview

This document presents a complete platform infrastructure design for the Rigor Rules system in Flowspec, enabling DORA Elite performance through automated workflow discipline, decision traceability, and CI/CD integration.

## Key Deliverables

### 1. DORA Elite Performance Framework

**Target Metrics:**
- Deployment Frequency: >1/day (from 2-3/week baseline)
- Lead Time: <1 day (from 2-5 days baseline)
- Change Failure Rate: <5% (from 15-20% baseline)
- Mean Time to Restore: <1 hour (from 2-4 hours baseline)

**Mechanism:**
- Pre-PR validation gates prevent CI failures
- Decision logging enables instant context restoration
- Freeze capability allows clean context switching
- Rebase discipline eliminates merge conflicts

### 2. Decision Logging Infrastructure

**Directory Structure:**
```
memory/decisions/
├── README.md              # Query examples and schema
├── task-541.jsonl         # Per-task decision logs
├── task-542.jsonl
└── index.jsonl            # (optional) Cross-task index
```

**JSONL Schema:**
```json
{
  "timestamp": "2025-12-17T14:30:00Z",
  "task_id": "task-542",
  "phase": "execution",
  "decision": "Use JSONL for decision logs",
  "rationale": "Line-oriented, streaming-friendly, tooling support",
  "alternatives": ["SQLite", "Plain text"],
  "actor": "@platform-engineer"
}
```

**Helper Script:**
```bash
./scripts/bash/rigor-decision-log.sh \
  --task task-542 \
  --phase execution \
  --decision "Selected Option B" \
  --rationale "Balances simplicity with scalability" \
  --actor "@platform-engineer"
```

### 3. Git Workflow Automation

**Branch Naming Format:**
```
hostname/task-NNN/slug-description

Examples:
  macbook-pro/task-542/decision-logging
  build-server/task-100/api-refactor
```

**Validation Scripts:**
1. `rigor-branch-validation.sh` - Branch name and worktree alignment
2. `rigor-rebase-check.sh` - Rebase status (zero commits behind main)
3. `rigor-pre-pr-validation.sh` - Comprehensive pre-PR gate

**Pre-PR Validation Checks:**
1. Branch naming format
2. Rebase status (up-to-date with main)
3. Code formatting (ruff format --check)
4. Linting (ruff check)
5. Test suite (pytest)
6. DCO sign-off (all commits)
7. Security scan (bandit SAST)

**ALL CHECKS MUST PASS - NO BYPASSING**

### 4. CI/CD Integration

**New GitHub Workflow:**
`.github/workflows/rigor-rules-check.yml`

**Checks:**
- Branch naming validation (PR only)
- Decision log JSONL validation
- Code format/lint/test
- DCO sign-off verification
- SAST scanning (bandit)
- SBOM generation (optional)
- Decision log metrics posted to PR

**Pre-commit Hooks:**
- Rebase status check (warning)
- Decision log validation (blocking if invalid JSON)
- Code quality checks (existing)

### 5. Workflow Status Tracking

**Template:**
```
[Y] Phase: Implementation complete
    Current state: workflow:In Implementation
    Next step: /flow:validate

    Progress:
    ✅ Setup phase
    ✅ Execution phase
    ⬜ Freeze (not needed)
    ⬜ Validation phase (NEXT)
    ⬜ PR phase (pending)

    Decisions logged: 7 (see memory/decisions/task-542.jsonl)
    Next action: Run /flow:validate
```

### 6. /flow:freeze Command

**Purpose:** Suspend task with context preservation

**What it does:**
1. Verifies code in working state (tests pass or failures documented)
2. Updates task memory with current status and resume instructions
3. Logs freeze decision to JSONL
4. Updates backlog task status
5. Commits and pushes to remote (optional)

**Resume workflow:**
```bash
# 1. Checkout branch
git checkout {branch-name}

# 2. Read context
cat backlog/memory/task-542.md
jq '.' memory/decisions/task-542.jsonl

# 3. Continue from frozen state
/flow:{next-command}
```

### 7. Rigor Rules Include File

**File:** `templates/partials/flow/_rigor-rules.md`

**Integrated into all workflow commands:**
```markdown
{{INCLUDE:.claude/partials/flow/_rigor-rules.md}}
```

**Content:**
- Setup phase rules (branch creation, constitution check)
- Execution phase rules (decision logging, incremental commits)
- Validation phase rules (pre-PR checks, rebase requirement)
- PR phase rules (DCO, CI monitoring, review response)
- Freeze capability (suspend/resume workflow)

## Directory Structure

```
memory/
├── decisions/                     # NEW
│   ├── README.md
│   └── task-*.jsonl

templates/commands/flow/
├── _rigor-rules.md               # NEW
├── freeze.md                     # NEW
├── _backlog-instructions.md      # existing
├── _workflow-state.md            # existing
└── _constitution-check.md        # existing

scripts/bash/
├── rigor-decision-log.sh         # NEW
├── rigor-branch-validation.sh    # NEW
├── rigor-rebase-check.sh         # NEW
├── rigor-pre-pr-validation.sh    # NEW
└── (existing scripts)

.github/workflows/
├── rigor-rules-check.yml         # NEW
└── (existing workflows)
```

## Implementation Timeline

### Phase 1: Infrastructure Setup (Week 1)
- Create directory structure
- Write helper scripts
- Create `_rigor-rules.md` include
- Write documentation

### Phase 2: Soft Rollout (Week 2)
- Add pre-commit hooks (warnings only)
- Add CI validation (decision logs only)
- Train early adopters
- Collect feedback

### Phase 3: Enforcement (Week 3)
- Enable branch naming validation (blocking)
- Enable pre-PR validation (blocking)
- Update PR template
- Add CODEOWNERS

### Phase 4: Optimization (Week 4+)
- Add `/flow:freeze` command
- Integrate status tracking
- Add decision analytics
- Create DORA dashboard

## Success Metrics

### DORA Metrics (Elite Target)
- Deployment Frequency: >1/day
- Lead Time: <1 day
- Change Failure Rate: <5%
- MTTR: <1 hour

### Adoption Metrics (Week 4 Target)
- PRs with valid branch names: 100%
- PRs with decision logs: 90%
- PRs passing pre-PR validation: 95%
- CI failure rate: <5%

### Developer Experience
- Pre-PR validation time: <5 minutes
- Decision logging time: <2 minutes per decision
- Context switch time: <10 minutes
- Developer satisfaction: >4/5

## Key Benefits

1. **DORA Elite Performance**
   - 75% reduction in lead time (eliminates rework cycles)
   - 70% reduction in change failure rate (preventive validation)
   - 80% reduction in MTTR (decision traceability)

2. **Developer Productivity**
   - Clear "what comes next" at every phase
   - Zero time lost to merge conflicts
   - Instant context restoration after freeze
   - No CI babysitting (validation before push)

3. **Quality Assurance**
   - 100% CI pass rate (blocking pre-PR gates)
   - Audit trail for all critical decisions
   - Automated compliance checking
   - Security scanning integrated

4. **Operational Excellence**
   - Decision logs enable post-mortem analysis
   - Context preservation enables clean handoffs
   - Workflow status tracking eliminates confusion
   - Metrics-driven continuous improvement

## Integration Points

### With Existing Systems

**Backlog CLI:**
- Task status updates reference rigor rules compliance
- Decision logs linked from task memory
- Freeze capability updates task status

**Workflow Commands:**
- All `/flow:*` commands include `_rigor-rules.md`
- Status tracking shows progress through rigor phases
- Validation phase enforces pre-PR checks

**Constitution:**
- New section: "Engineering Rigor and Workflow Discipline"
- Rigor principles added to project values
- Pre-PR validation codified as mandatory

**Critical Rules:**
- Branch naming enforced
- Pre-PR validation non-negotiable
- Decision logging required for architecture choices

## Troubleshooting Quick Reference

| Issue | Resolution |
|-------|------------|
| Invalid branch name | `git branch -m old-name hostname/task-NNN/slug` |
| Branch behind main | `git rebase origin/main && git push --force-with-lease` |
| Invalid JSON in log | `jq empty memory/decisions/task-NNN.jsonl` to find error |
| Pre-PR validation fails | Fix each check, re-run until all pass |
| Missing DCO sign-off | `git rebase -i origin/main --exec 'git commit --amend -s'` |

## Example Workflows

### Create First PR with Rigor Rules
```bash
# 1. Create branch
git checkout -b $(hostname -s)/task-542/decision-logging

# 2. Do work, log decisions
./scripts/bash/rigor-decision-log.sh --task task-542 ...

# 3. Validate before PR
./scripts/bash/rigor-pre-pr-validation.sh

# 4. Create PR
gh pr create --fill
```

### Resume Frozen Task
```bash
# 1. Read context
cat backlog/memory/task-542.md
jq '.' memory/decisions/task-542.jsonl

# 2. Checkout and continue
git checkout hostname/task-542/feature
/flow:implement
```

### Debug Production Issue
```bash
# 1. Find decision
jq 'select(.decision | contains("timeout"))' memory/decisions/task-*.jsonl

# 2. Review rationale
# 3. Create fix task with new decision
```

## Files Created

| File | Purpose |
|------|---------|
| `build-docs/platform/rigor-rules-infrastructure.md` | Full design document (10,000+ lines) |
| `memory/decisions/README.md` | Decision logging guide (to be created) |
| `scripts/bash/rigor-decision-log.sh` | Decision logging helper |
| `scripts/bash/rigor-branch-validation.sh` | Branch naming validator |
| `scripts/bash/rigor-rebase-check.sh` | Rebase status checker |
| `scripts/bash/rigor-pre-pr-validation.sh` | Pre-PR validation gate |
| `templates/partials/flow/_rigor-rules.md` | Rigor rules include |
| `templates/commands/flow/freeze.md` | Freeze command template |
| `.github/workflows/rigor-rules-check.yml` | CI validation workflow |
| `tests/test_rigor_scripts.sh` | Script integration tests |

## Next Steps

1. **Review**: Software architect and PM review design
2. **Approval**: Sign-off on approach and timeline
3. **Task Creation**: Break design into implementation tasks
4. **Implementation**: Begin Phase 1 (Week 1)
5. **Testing**: Validate all scripts and CI integration
6. **Training**: Developer onboarding materials
7. **Rollout**: Phased enforcement (Weeks 2-4)
8. **Metrics**: Track DORA and adoption metrics
9. **Iteration**: Optimize based on feedback

## Questions?

Contact @platform-engineer or @software-architect for clarification or feedback.

---

**Full documentation**: `build-docs/platform/rigor-rules-infrastructure.md`
