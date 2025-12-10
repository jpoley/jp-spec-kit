# Command Cleanup Plan

**Date**: 2025-12-10
**Status**: IMPLEMENTED
**Related**: task-433, `docs/audit/command-taxonomy-current-state.md`

---

## Target Architecture

**2 Workflows + Many Utilities**

```
WORKFLOWS (stateful, sequential stages)
├── /speckit:*    → Lightweight SDD workflow
└── /specflow:*   → Full agent-based SDD workflow

UTILITIES (stateless, run anytime)
├── /dev:*        → Developer utilities
├── /sec:*        → Security utilities
├── /arch:*       → Architecture utilities
├── /ops:*        → Operations utilities
└── /qa:*         → QA utilities
```

---

## Workflows

### `/speckit:*` - Lightweight SDD

Simple, script-based workflow for smaller features.

| Command | Purpose | Keep/Change |
|---------|---------|-------------|
| `/speckit:init` | Initialize project | KEEP |
| `/speckit:specify` | Create spec from natural language | KEEP |
| `/speckit:clarify` | Refine spec with questions | KEEP |
| `/speckit:plan` | Generate design artifacts | KEEP |
| `/speckit:tasks` | Generate task backlog | KEEP |
| `/speckit:implement` | Execute tasks | KEEP |
| `/speckit:analyze` | Cross-artifact validation | KEEP |
| `/speckit:checklist` | Generate feature checklist | KEEP |
| `/speckit:constitution` | Generate constitution from tech stack | KEEP |
| `/speckit:configure` | Configure workflow settings | KEEP |

**Total: 10 commands - NO CHANGES**

### `/specflow:*` - Full Agent-Based SDD

Comprehensive workflow with specialized agents, workflow state, constitution checks.

| Command | Purpose | Keep/Change |
|---------|---------|-------------|
| `/specflow:init` | Initialize constitution (greenfield/brownfield) | KEEP |
| `/specflow:assess` | Evaluate SDD appropriateness | KEEP |
| `/specflow:specify` | Full PRD with PM Planner agent | KEEP |
| `/specflow:research` | Research and validation | KEEP |
| `/specflow:plan` | Architecture planning with agents | KEEP |
| `/specflow:implement` | Implementation with frontend/backend agents | KEEP |
| `/specflow:validate` | QA and security validation | KEEP |
| `/specflow:operate` | SRE operations workflow | KEEP |
| `/specflow:reset` | Reset workflow configuration | KEEP |
| `/specflow:security_workflow` | Security scanning integration | KEEP |
| `/specflow:security_fix` | Apply security patches | KEEP |
| `/specflow:security_report` | Generate security report | KEEP |
| `/specflow:security_triage` | Triage security findings | KEEP |
| `/specflow:security_web` | Web security scanning | KEEP |
| `/specflow:prune-branch` | Git branch cleanup | MOVE to `/dev:cleanup` |

**Total: 15 commands → 14 commands (move 1)**

---

## Utilities

Stateless commands that can run anytime, outside of workflow context.

### `/dev:*` - Developer Utilities

| Command | Purpose | Action |
|---------|---------|--------|
| `/dev:debug` | Debugging assistance | KEEP |
| `/dev:refactor` | Refactoring guidance | KEEP |
| `/dev:cleanup` | Prune merged branches | KEEP (absorb `/specflow:prune-branch`) |
| `/dev:build` | - | **DELETE** (duplicate of `/specflow:implement`) |

### `/sec:*` - Security Utilities

| Command | Purpose | Action |
|---------|---------|--------|
| `/sec:scan` | Security scanning | KEEP |
| `/sec:triage` | Triage findings | KEEP |
| `/sec:fix` | Apply patches | KEEP |
| `/sec:report` | Generate report | KEEP |
| `/sec:audit` | - | **DELETE** (duplicate of `/specflow:security_workflow`) |

### `/arch:*` - Architecture Utilities

| Command | Purpose | Action |
|---------|---------|--------|
| `/arch:decide` | Create ADRs | KEEP |
| `/arch:model` | Create data models, API contracts | KEEP |
| `/arch:design` | - | **DELETE** (duplicate of `/specflow:plan`) |

### `/ops:*` - Operations Utilities

| Command | Purpose | Action |
|---------|---------|--------|
| `/ops:monitor` | Setup monitoring | KEEP |
| `/ops:respond` | Incident response | KEEP |
| `/ops:scale` | Scaling guidance | KEEP |
| `/ops:deploy` | - | **DELETE** (duplicate of `/specflow:operate`) |

### `/qa:*` - QA Utilities

| Command | Purpose | Action |
|---------|---------|--------|
| `/qa:test` | Execute tests | KEEP |
| `/qa:review` | Generate checklist | KEEP |
| `/qa:verify` | - | **DELETE** (duplicate of `/specflow:validate`) |

### `/pm:*` - Product Manager

| Command | Purpose | Action |
|---------|---------|--------|
| `/pm:assess` | - | **DELETE** (duplicate of `/specflow:assess`) |
| `/pm:define` | - | **DELETE** (duplicate of `/specflow:specify`) |
| `/pm:discover` | - | **DELETE** (duplicate of `/specflow:research`) |

**DELETE ENTIRE NAMESPACE** - PM work IS the workflow.

---

## Files to Delete

### Deprecated Command Files

All `_DEPRECATED_*.md` files in `templates/commands/specflow/`:

```
templates/commands/specflow/_DEPRECATED_assess.md
templates/commands/specflow/_DEPRECATED_implement.md
templates/commands/specflow/_DEPRECATED_operate.md
templates/commands/specflow/_DEPRECATED_plan.md
templates/commands/specflow/_DEPRECATED_prune-branch.md
templates/commands/specflow/_DEPRECATED_research.md
templates/commands/specflow/_DEPRECATED_security_fix.md
templates/commands/specflow/_DEPRECATED_security_report.md
templates/commands/specflow/_DEPRECATED_security_triage.md
templates/commands/specflow/_DEPRECATED_security_web.md
templates/commands/specflow/_DEPRECATED_security_workflow.md
templates/commands/specflow/_DEPRECATED_specify.md
templates/commands/specflow/_DEPRECATED_validate.md
```

**Total: 13 files**

### Workflow Duplicate Commands

```
templates/commands/pm/assess.md
templates/commands/pm/define.md
templates/commands/pm/discover.md
templates/commands/arch/design.md
templates/commands/dev/build.md
templates/commands/qa/verify.md
templates/commands/ops/deploy.md
templates/commands/sec/audit.md
```

**Total: 8 files**

### Entire Namespace

```
templates/commands/pm/           (entire directory)
.claude/commands/pm              (symlink)
```

---

## Symlinks to Update

After deleting files, update `.claude/commands/`:

```bash
# Remove broken symlinks in specflow/
rm .claude/commands/specflow/_DEPRECATED_*.md

# Remove pm namespace entirely
rm .claude/commands/pm

# Keep other role namespaces (they still have utility commands)
```

---

## Summary of Changes

| Action | Count |
|--------|-------|
| Commands KEPT | 35 |
| Commands DELETED | 21 |
| Namespaces DELETED | 1 (`/pm`) |
| Deprecated files DELETED | 13 |

### Final Command Count by Namespace

| Namespace | Before | After |
|-----------|--------|-------|
| `/speckit:*` | 10 | 10 |
| `/specflow:*` | 29 | 14 |
| `/pm:*` | 3 | **0 (deleted)** |
| `/arch:*` | 3 | 2 |
| `/dev:*` | 4 | 3 |
| `/qa:*` | 3 | 2 |
| `/sec:*` | 5 | 4 |
| `/ops:*` | 4 | 3 |
| **TOTAL** | **61** | **38** |

---

## Implementation Order

1. **Delete deprecated files** (13 files)
   - All `_DEPRECATED_*.md` in specflow
   - Update symlinks

2. **Delete `/pm` namespace** (3 files + symlink)
   - `templates/commands/pm/` directory
   - `.claude/commands/pm` symlink

3. **Delete workflow duplicates** (5 files)
   - `/arch:design`
   - `/dev:build`
   - `/qa:verify`
   - `/ops:deploy`
   - `/sec:audit`

4. **Move `/specflow:prune-branch`** to `/dev:cleanup`
   - Verify `/dev:cleanup` has same functionality
   - Delete `/specflow:prune-branch`

5. **Update documentation**
   - CLAUDE.md command references
   - Any guides referencing deleted commands

6. **Test**
   - Verify all kept commands work
   - Verify no broken symlinks

---

## Rollback Plan

If issues found:
1. Git revert the cleanup commit
2. All files restored from git history

---

*This plan requires approval before implementation.*
