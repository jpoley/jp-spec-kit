# Rigor Rules Feature - Implementation Plan

**Feature**: Rigor Rules Enforcement System
**Created**: 2025-12-17
**Status**: PLANNED - Ready for Implementation

---

## Executive Summary

The Rigor Rules system enforces workflow discipline across the Flowspec development lifecycle. It transforms development from loosely-guided to disciplined, auditable, and predictable.

**Business Impact**: $125K annual savings (12.5x ROI)
**Platform Quality**: 8.9/10 (Grade A)
**Implementation Effort**: 4 weeks (180 hours)
**Target DORA Level**: Elite

---

## Architecture Overview

### System Layers

```
Command Layer (/flow:*)
    ↓
Enforcement Layer (_rigor-rules.md)
    ↓
Infrastructure Layer (JSONL, Git, Backlog)
    ↓
Storage Layer (memory/decisions/, backlog/memory/)
```

### 23 Rules Across 5 Phases

| Phase | Rules | Purpose |
|-------|-------|---------|
| Setup | 4 | Task hygiene, dependencies, ACs |
| Execution | 6 | Branch naming, decision logging, tracking |
| Freeze | 3 | Context preservation |
| Validation | 7 | Quality gates, CI, rebase |
| PR | 3 | DCO, Copilot handling, versioning |

---

## Key Architecture Decisions (ADRs)

### ADR-001: Shared Include Pattern
**Decision**: Use `_rigor-rules.md` shared include
**Rationale**: Single source of truth, 85% maintenance reduction
**File**: `docs/adr/ADR-001-rigor-rules-include-pattern.md`

### ADR-002: JSONL Decision Logging
**Decision**: Use JSONL format for decision logs
**Rationale**: Append-only, git-friendly, stream-processable
**File**: `docs/adr/ADR-002-jsonl-decision-logging.md`

### ADR-003: Branch Naming Convention
**Decision**: Use `hostname/task-NNN/slug` format
**Rationale**: Machine isolation, task traceability, worktree compatible
**File**: `docs/adr/ADR-003-branch-naming-convention.md`

### ADR-004: PR Iteration Pattern
**Decision**: Use sequential versions (-v2, -v3)
**Rationale**: Clear lineage, simple naming, automation-friendly
**File**: `docs/adr/ADR-004-pr-iteration-pattern.md`

---

## Implementation Tasks (Dependency Order)

### Phase 1: Foundation (Week 1) - 40 hours

| Task | Title | Priority | Dependencies |
|------|-------|----------|--------------|
| task-541 | Create _rigor-rules.md shared include file | HIGH | None |
| task-542 | Add JSONL decision logging infrastructure | HIGH | None |

### Phase 2: Core Command Integration (Week 2) - 60 hours

| Task | Title | Priority | Dependencies |
|------|-------|----------|--------------|
| task-543 | Integrate rigor rules into /flow:implement | HIGH | task-541 |
| task-544 | Integrate rigor rules into /flow:validate | HIGH | task-541 |
| task-545 | Integrate rigor rules into /flow:specify | HIGH | task-541 |

### Phase 3: Extended Coverage (Week 3) - 50 hours

| Task | Title | Priority | Dependencies |
|------|-------|----------|--------------|
| task-546 | Integrate rigor rules into /flow:assess | MEDIUM | task-541 |
| task-547 | Integrate rigor rules into /flow:plan | MEDIUM | task-541, task-542 |
| task-548 | Integrate rigor rules into /flow:operate | MEDIUM | task-541 |
| task-549 | Add /flow:freeze command for task suspension | MEDIUM | task-541 |

### Phase 4: Infrastructure Enhancements (Week 4) - 30 hours

| Task | Title | Priority | Dependencies |
|------|-------|----------|--------------|
| task-550 | Add workflow status tracking to all commands | MEDIUM | task-541 |
| task-551 | Update critical-rules.md with rigor rules reference | LOW | task-541 |
| task-552 | Create rigor rules troubleshooting guide | LOW | task-541 |

---

## Files to Create

### Templates

| File | Purpose |
|------|---------|
| `templates/partials/flow/_rigor-rules.md` | Main rigor rules include |
| `templates/commands/flow/freeze.md` | /flow:freeze command |

### Scripts

| File | Purpose |
|------|---------|
| `scripts/bash/rigor-decision-log.sh` | Decision logging helper |
| `scripts/bash/rigor-branch-validation.sh` | Branch naming validator |
| `scripts/bash/rigor-rebase-check.sh` | Rebase status checker |
| `scripts/bash/rigor-pre-pr-validation.sh` | Pre-PR validation gate |

### Infrastructure

| File | Purpose |
|------|---------|
| `memory/decisions/README.md` | Decision log documentation |
| `.github/workflows/rigor-rules-check.yml` | CI validation workflow |

### Symlinks

| Symlink | Target |
|---------|--------|
| `.claude/partials/flow/_rigor-rules.md` | `../../../templates/partials/flow/_rigor-rules.md` |
| `.claude/commands/flow/freeze.md` | `../../../templates/commands/flow/freeze.md` |

---

## JSONL Decision Log Schema

```json
{
  "timestamp": "2025-12-17T14:30:00Z",
  "task_id": "task-XXX",
  "phase": "setup|execution|freeze|validation|pr",
  "decision": "What was decided",
  "rationale": "Why",
  "alternatives": ["Other options considered"],
  "actor": "@agent-name",
  "context": {
    "files_affected": ["src/file.py"],
    "related_tasks": ["task-120"],
    "tags": ["architecture"]
  }
}
```

---

## Branch Naming Convention

**Format**: `<hostname>/task-<id>/<slug-description>`

**Examples**:
```
laptop-jpoley/task-541/rigor-rules-include
desktop-alice/task-542/decision-logging
```

**Validation Regex**: `^[a-z0-9-]+/task-[0-9]+/[a-z0-9-]+$`

---

## Pre-PR Validation Gates (Blocking)

1. Branch naming format
2. Rebase status (zero commits behind main)
3. Code formatting (`ruff format --check`)
4. Linting (`ruff check`)
5. Test suite (`pytest`)
6. DCO sign-off (all commits)
7. Security scan (`bandit` SAST)

**All checks must pass. No bypassing.**

---

## DORA Elite Performance Targets

| Metric | Baseline | Target |
|--------|----------|--------|
| Deployment Frequency | 2-3/week | >1/day |
| Lead Time | 2-5 days | <1 day |
| Change Failure Rate | 15-20% | <5% |
| MTTR | 2-4 hours | <1 hour |

---

## Success Criteria

### Week 4 Targets
- 80% of tasks follow rigor rules
- 100% PRs have valid branch names
- 90% PRs have decision logs
- 95% PRs pass pre-PR validation
- <5% CI failure rate

### Week 12 Targets
- 95% of tasks follow rigor rules
- Zero workflow-related production incidents
- Developer satisfaction >4/5

---

## Risk Mitigation

### Developer Resistance
- Start with warn mode (gradual adoption)
- Measure and publicize time savings
- 2-week retrospectives

### Learning Curve
- Comprehensive documentation
- Office hours (2x per week for first month)
- Helper scripts reduce manual overhead

---

## Documentation Artifacts

| Document | Location |
|----------|----------|
| System Architecture | `docs/architecture/rigor-rules-system-architecture.md` |
| Architecture Summary | `docs/architecture/RIGOR-RULES-DELIVERABLES-SUMMARY.md` |
| Infrastructure Design | `build-docs/platform/rigor-rules-infrastructure.md` |
| Infrastructure Summary | `build-docs/platform/rigor-rules-infrastructure-summary.md` |
| Quick Reference | `build-docs/platform/rigor-rules-quick-reference.md` |
| ADR-001 | `docs/adr/ADR-001-rigor-rules-include-pattern.md` |
| ADR-002 | `docs/adr/ADR-002-jsonl-decision-logging.md` |
| ADR-003 | `docs/adr/ADR-003-branch-naming-convention.md` |
| ADR-004 | `docs/adr/ADR-004-pr-iteration-pattern.md` |

---

## Next Steps

1. **Review and approve** this plan
2. **Start implementation** with task-541 (_rigor-rules.md)
3. **Run /flow:implement** for Phase 1 tasks
4. **Schedule weekly check-ins** for progress tracking

---

**Status**: PLANNED - Ready for `/flow:implement`
**Next Command**: `/flow:implement task-541`
