# dev-setup Architecture Recovery Plan

**Created**: 2025-12-03
**Status**: In Progress
**Source**: dogfood-cli and dogfood-templates worktrees

---

## Executive Summary

The `dogfood-cli` worktree (now referred to as `dev-setup`) contains valuable architecture documentation and planning artifacts for completing the dev-setup command improvements. However, the worktree is 554 commits behind main and includes deletions of security/workflow/hooks code that we want to keep. This plan extracts the valuable work while preserving main's codebase.

---

## Current State Analysis

### Branch Comparison

| Aspect | Main Branch | dogfood-cli Worktree |
|--------|-------------|---------------------|
| **Divergence** | - | 554 commits behind main |
| **dev-setup cmd** | ✅ Basic (PR #271) | ✅ Enhanced with renames |
| **Security code** | ✅ Extensive (triage engine, etc.) | ❌ DELETED |
| **Workflow code** | ✅ Present | ❌ DELETED |
| **Hooks code** | ✅ Present | ❌ DELETED |
| **Voice module** | ❌ Missing | ✅ Complete with tests |
| **Architecture ADRs** | ❌ Missing | ✅ 3 ADRs for dev-setup |
| **Dev-setup tasks** | ❌ Missing | ✅ Tasks 259-279 |
| **Makefile** | ❌ Missing | ✅ Dev helper targets |

### PR History

| PR | Branch | Status | Description |
|----|--------|--------|-------------|
| #271 | dev-setup-v4 | ✅ MERGED | Basic dev-setup command with symlinks |
| #269 | dev-setup-v3 | ❌ CLOSED | Earlier attempt |
| #268 | dev-setup-fix-v2 | ❌ CLOSED | Earlier attempt |
| #266 | dev-setup-fix | ❌ CLOSED | Earlier attempt |
| #265 | dev-setup-fix | ❌ CLOSED | Earlier attempt |

### Why dogfood-cli Cannot Be Merged As-Is

The worktree **deletes ~112,000 lines** including:

1. **Security scanning module** - Actively developed with recent PRs (#373, #374, #378)
2. **Workflow engine** - Required for /flowspec command state management
3. **Hooks system** - Required for quality gates and automation
4. **Quality module** - Used for spec validation

These deletions would break the current functionality.

---

## Recovery Strategy: Selective Cherry-Pick

### Phase 1: Extract Architecture Docs ✅

**Status**: In Progress

Copy these files from dogfood-cli to main:

```
docs/architecture/adr-001-single-source-of-truth.md
docs/architecture/adr-002-directory-structure.md
docs/architecture/adr-003-shared-content-strategy.md
docs/architecture/command-single-source-of-truth.md
docs/architecture/IMPLEMENTATION-READINESS-REPORT.md
docs/architecture/README.md (if updated)
docs/fix-dogfood.md
docs/platform/dev-setup-deliverables.md
docs/platform/dev-setup-principles.md
docs/runbooks/dev-setup-recovery.md
```

**Value**: Comprehensive architecture documentation with ADRs, implementation plans, and runbooks.

### Phase 2: Import Makefile

**Status**: Pending

```
Makefile
```

**Targets provided**:
- `make dev-validate` - Validate dev setup
- `make dev-fix` - Fix dev setup (recreate symlinks)
- `make dev-status` - Show dev setup status
- `make test-dev` - Run dev setup tests

### Phase 3: Import Backlog Tasks

**Status**: Pending

Import tasks 259-279 from dogfood-cli:

| Task | Title |
|------|-------|
| 259 | Create dev-setup validation GitHub Action |
| 260 | Create dev-setup validation test suite |
| 261 | Add dev-setup validation pre-commit hook |
| 262 | Add dev-setup management Makefile commands |
| 263 | Document dev-setup workflow for contributors |
| 264 | Migrate flowspec commands to templates |
| 265 | Add flowspec commands to specify init distribution |
| 266 | Create dev-setup operational runbook |
| 267 | ADR: Single Source of Truth for Commands |
| 268 | ADR: Directory Structure Convention |
| 269 | ADR: Shared Content Strategy |
| 270 | Design Unified Command Template Structure |
| 271 | Migrate flowspec commands to templates |
| 272 | Migrate speckit commands to subdirectory |
| 273 | Update dev-setup command for flowspec symlinks |
| 274 | Replace source repo commands with symlinks |
| 275 | Update init command for subdirectory structure |
| 276 | Create command migration script for users |
| 277 | Create dev-setup/init equivalence validation tests |
| 278 | Add CI validation for command structure |
| 279 | Update documentation for new architecture |

### Phase 4: Consider Voice Module (Optional)

**Status**: Pending evaluation

```
src/specify_cli/voice/
├── __init__.py
├── bot.py
├── config.py
├── flows/
├── processors/
├── services/
└── tools/

tests/voice/
├── __init__.py
├── test_bot.py
├── test_config.py
├── test_llm.py
├── test_stt.py
└── test_tts.py
```

**Decision needed**: Is voice assistant feature still wanted?

### Phase 5: Cleanup Worktrees

**Status**: Pending

After extraction complete:

```bash
# Remove worktree directories
rm -rf /home/jpoley/ps/dogfood-cli
rm -rf /home/jpoley/ps/dogfood-templates

# Prune git worktree references
git worktree prune

# Delete local branches
git branch -D dogfood-cli
git branch -D dogfood-templates
```

---

## What We're NOT Taking

The following changes in dogfood-cli are **intentionally excluded**:

- ❌ Deletion of `src/specify_cli/security/` module
- ❌ Deletion of `src/specify_cli/workflow/` module
- ❌ Deletion of `src/specify_cli/hooks/` module
- ❌ Deletion of `src/specify_cli/quality/` module
- ❌ Deletion of associated test files
- ❌ Removal of `flowspec_workflow.yml` and schema
- ❌ Removal of memory/ directory files
- ❌ The comprehensive "rename dogfood to dev-setup everywhere" commits (CLI name already changed)

---

## Implementation Checklist

### Phase 1: Architecture Docs
- [ ] Create feature branch from main
- [ ] Copy architecture ADRs (3 files)
- [ ] Copy command-single-source-of-truth.md
- [ ] Copy IMPLEMENTATION-READINESS-REPORT.md
- [ ] Copy fix-dogfood.md
- [ ] Copy platform docs (2 files)
- [ ] Copy runbook
- [ ] Verify no conflicts with existing docs
- [ ] Run tests

### Phase 2: Makefile
- [ ] Copy Makefile
- [ ] Verify targets work
- [ ] Update if needed for current structure

### Phase 3: Backlog Tasks
- [ ] Copy task files 259-279
- [ ] Verify task format is correct
- [ ] Update any stale references

### Phase 4: Voice Module (if proceeding)
- [ ] Copy voice module source
- [ ] Copy voice tests
- [ ] Add dependencies to pyproject.toml
- [ ] Run voice tests
- [ ] Update CLI with voice command

### Phase 5: Cleanup
- [ ] Remove dogfood-cli worktree directory
- [ ] Remove dogfood-templates worktree directory
- [ ] Run `git worktree prune`
- [ ] Delete local branches
- [ ] Verify git status clean

---

## Related Tasks

- **task-134**: Integrate diagrams and documentation into project structure (still To Do)

---

## Notes

- The dev-setup command (`specify dev-setup`) is already functional from PR #271
- The architecture docs describe enhancements to make dev-setup match init output
- Main has continued active development on security scanning features
- The voice module is a separate feature that could be extracted independently
