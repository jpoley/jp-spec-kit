# ADR-010: Dev-Setup Validation System Architecture

**Status**: Accepted
**Date**: 2025-12-03
**Author**: @software-architect
**Context**: Tasks 259, 260, 261, 263, 266, 277 (dev-setup validation infrastructure)

---

## Context

The flowspec project uses a "dev-setup" (formerly "dogfood") pattern where the source repository uses its own templates through symlinks. The `.claude/commands/` directory contains ONLY symlinks pointing to `templates/commands/`, ensuring:

1. **Single Source of Truth**: All command content lives in `templates/commands/`
2. **Dev-Prod Parity**: Developers test the exact commands distributed to users
3. **Automatic Propagation**: Template changes immediately reflect in development

**Current State**:
- `flowspec dev-setup` command creates symlinks for flowspec and speckit commands
- `.claude/commands/flow/*.md` -> `templates/commands/flowspec/*.md`
- `.claude/commands/speckit/*.md` -> `templates/commands/*.md`

**Problem**: There is no automated validation to prevent:
- Direct file creation in `.claude/commands/` (violating symlink-only policy)
- Broken symlinks from template deletions
- Structural drift between dev-setup and init commands

**Solution Required**: A layered validation system with pre-commit hooks, test suite, and CI/CD enforcement.

---

## Decision

Implement a three-tier validation architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                     VALIDATION ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  TIER 1: Pre-Commit Hook (Fastest Feedback)                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ scripts/bash/pre-commit-dev-setup.sh                    │   │
│  │ - Detects non-symlink .md files                         │   │
│  │ - Detects broken symlinks                               │   │
│  │ - Runs in < 10 seconds                                  │   │
│  │ - Blocks commit on failure                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  TIER 2: Test Suite (Comprehensive Verification)                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ tests/test_dev_setup_validation.py                      │   │
│  │ tests/test_dev_setup_init_equivalence.py                │   │
│  │ - Complete symlink validation                           │   │
│  │ - Template coverage verification                        │   │
│  │ - dev-setup/init equivalence tests                      │   │
│  │ - Runs with pytest (< 30 seconds)                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  TIER 3: CI/CD Pipeline (Gate Enforcement)                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ .github/workflows/dev-setup-validation.yml              │   │
│  │ - Runs on every PR                                      │   │
│  │ - Executes full test suite                              │   │
│  │ - Blocks merge on failure                               │   │
│  │ - Provides actionable error messages                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Design

### 1. Validation Rules (All Tiers)

| Rule ID | Rule Description | Severity |
|---------|-----------------|----------|
| R1 | `.claude/commands/**/*.md` contains ONLY symlinks | ERROR |
| R2 | All symlinks resolve to existing files | ERROR |
| R3 | All symlinks point to `templates/commands/` | ERROR |
| R4 | Every template has corresponding symlink | WARNING |
| R5 | No orphan symlinks (target exists in templates) | ERROR |
| R6 | dev-setup creates same file set as init would copy | ERROR |
| R7 | Subdirectory structure matches (flowspec/, speckit/) | ERROR |

### 2. Component Responsibilities

| Component | File | Rules Enforced | Trigger |
|-----------|------|----------------|---------|
| Pre-commit hook | `scripts/bash/pre-commit-dev-setup.sh` | R1, R2 | git commit |
| Test suite | `tests/test_dev_setup_validation.py` | R1-R5 | pytest |
| Equivalence tests | `tests/test_dev_setup_init_equivalence.py` | R6, R7 | pytest |
| GitHub Action | `.github/workflows/dev-setup-validation.yml` | All | PR/push |

### 3. Error Handling and Recovery

All validation errors follow this pattern:

```
❌ ERROR: [RULE_DESCRIPTION]
[LIST_OF_VIOLATIONS]

To fix:
  [ACTIONABLE_COMMAND]
```

Recovery Procedures:

| Scenario | Command | MTTR |
|----------|---------|------|
| Non-symlink files | `flowspec dev-setup --force` | < 1 min |
| Broken symlinks | `flowspec dev-setup --force` | < 1 min |
| Corrupted structure | `rm -rf .claude/commands && flowspec dev-setup` | < 2 min |
| Template missing | `git checkout main -- templates/commands/FILE` | < 2 min |

---

## Component Interaction

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPONENT INTERACTION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Developer edits templates/commands/foo.md                       │
│           │                                                      │
│           ↓                                                      │
│  ┌──────────────────┐                                           │
│  │ Pre-commit Hook  │──→ Check symlinks ──→ PASS/FAIL           │
│  └──────────────────┘                                           │
│           │ (if passed)                                          │
│           ↓                                                      │
│  ┌──────────────────┐                                           │
│  │ git commit       │                                           │
│  └──────────────────┘                                           │
│           │                                                      │
│           ↓                                                      │
│  ┌──────────────────┐                                           │
│  │ git push         │                                           │
│  └──────────────────┘                                           │
│           │                                                      │
│           ↓                                                      │
│  ┌──────────────────┐                                           │
│  │ GitHub Actions   │──→ Run test suite ──→ PASS/FAIL          │
│  │ CI/CD Pipeline   │──→ Block merge if failed                  │
│  └──────────────────┘                                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Task to Agent Mapping

| Task ID | Task Title | Agent Type | Rationale |
|---------|-----------|------------|-----------|
| task-259 | Create dev-setup validation GitHub Action | backend-engineer | YAML workflow, shell scripts |
| task-260 | Create dev-setup validation test suite | backend-engineer | Python pytest code |
| task-261 | Add dev-setup validation pre-commit hook | backend-engineer | Bash script, config files |
| task-263 | Document dev-setup workflow for contributors | backend-engineer | Markdown documentation |
| task-266 | Create dev-setup operational runbook | backend-engineer | Markdown documentation |
| task-277 | Create dev-setup/init equivalence validation tests | backend-engineer | Python pytest code |

---

## Implementation Order

```
Phase 1: Foundation (Parallel)
├── task-260: Test suite (provides validation framework)
├── task-277: Equivalence tests (extends test suite)
└── task-261: Pre-commit hook (local validation)

Phase 2: Enforcement (Requires Phase 1)
└── task-259: GitHub Action (runs tests from Phase 1)

Phase 3: Documentation (Parallel with Phase 1-2)
├── task-263: Contributor documentation
└── task-266: Operational runbook
```

Critical Path: `task-260/task-277 → task-261 → task-259`

---

## Consequences

### Positive

- **Automated Enforcement**: CI/CD prevents non-symlink files from merging
- **Fast Feedback**: Pre-commit hook catches issues in < 10 seconds
- **Self-Healing**: `flowspec dev-setup --force` fixes most issues automatically
- **Comprehensive Testing**: Test suite covers all validation rules
- **Clear Documentation**: Contributors understand the architecture

### Negative

- **Learning Curve**: New contributors must understand symlink architecture
- **CI Time**: Additional workflow adds ~1-2 minutes to CI
- **Platform Dependency**: Windows requires Developer Mode for symlinks

### Mitigations

- Clear error messages with fix instructions
- Pre-commit hook catches issues before CI
- Comprehensive documentation and runbook
- `make dev-fix` provides one-command recovery

---

## References

- [Dev-Setup Principles](/docs/platform/dev-setup-principles.md)
- [Dev-Setup Deliverables](/docs/platform/dev-setup-deliverables.md)
- [Dev-Setup Recovery Runbook](/docs/runbooks/dev-setup-recovery.md)
