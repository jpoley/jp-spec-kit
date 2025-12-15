---
id: task-433
title: >-
  Fix incorrect deprecation mappings - /flowspec is primary, role commands are
  aliases
status: Done
assignee:
  - '@adare'
created_date: '2025-12-10 22:20'
updated_date: '2025-12-15 02:18'
labels:
  - bug
  - commands
  - critical
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Target Architecture

**2 Workflows + Many Utilities**

- `/speckit:*` - Lightweight SDD workflow (10 commands)
- `/flow:*` - Full agent-based SDD workflow (14 commands)
- `/dev:*`, `/sec:*`, `/arch:*`, `/ops:*`, `/qa:*` - Stateless utilities (run anytime)

## Problem

The "role-based" reorganization made things worse:
- 8 namespaces instead of 2 clear workflows
- Deprecation warnings pointing users AWAY from flowspec (wrong direction)
- Duplicate commands scattered everywhere
- PM work duplicated as both workflow AND role namespace

## Solution

1. **DELETE** all `_DEPRECATED_*.md` files (13 files) - wrong direction
2. **DELETE** entire `/pm` namespace - PM work IS the workflow
3. **DELETE** workflow duplicates from role namespaces:
   - `/arch:design` → use `/flow:plan`
   - `/dev:build` → use `/flow:implement`
   - `/qa:verify` → use `/flow:validate`
   - `/ops:deploy` → use `/flow:operate`
   - `/sec:audit` → use `/flow:security_workflow`
4. **KEEP** utility commands in role namespaces (debug, refactor, scan, etc.)

See: `docs/audit/command-cleanup-plan.md` for full implementation plan.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 All 13 _DEPRECATED_*.md files deleted from templates/commands/flow/
- [x] #2 Entire /pm namespace deleted (3 commands + symlink)
- [x] #3 Workflow duplicate commands deleted: /arch:design, /dev:build, /qa:verify, /ops:deploy, /sec:audit
- [x] #4 All symlinks in .claude/commands/ updated (no broken links)
- [x] #5 /flow:* commands work as primary workflow (no deprecation warnings)

- [x] #6 Utility commands preserved: /dev:debug, /dev:refactor, /sec:scan, etc.
- [x] #7 Documentation updated (CLAUDE.md, guides)
- [x] #8 Command count reduced from 61 to 38
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Delete 13 _DEPRECATED_*.md files from templates/commands/flow/
2. Delete entire /pm namespace (templates/commands/pm/ directory)
3. Remove .claude/commands/pm symlink
4. Delete workflow duplicate commands:
   - templates/commands/arch/design.md
   - templates/commands/dev/build.md
   - templates/commands/qa/verify.md
   - templates/commands/ops/deploy.md
   - templates/commands/sec/audit.md
5. Delete flowspec/prune-branch.md (absorbed by /dev:cleanup)
6. Update .claude/commands/flow/ symlinks if needed
7. Update documentation (CLAUDE.md)
8. Run tests and verify no broken symlinks
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Summary

Executed command cleanup per `docs/audit/command-cleanup-plan.md`:

### Files Deleted (22 total)
- 13 `_DEPRECATED_*.md` files from `templates/commands/flow/`
- 3 `/pm` namespace files (`assess.md`, `define.md`, `discover.md`)
- 5 workflow duplicates (`/arch:design`, `/dev:build`, `/qa:verify`, `/ops:deploy`, `/sec:audit`)
- 1 `prune-branch.md` (absorbed by `/dev:cleanup`)

### Symlinks Cleaned
- Removed 14 broken symlinks from `.claude/commands/flow/`
- Removed `.claude/commands/pm` symlink

### Documentation Updated
- `CLAUDE.md`: Added utility commands section with all 14 stateless utilities
- `docs/audit/command-cleanup-plan.md`: Status changed to IMPLEMENTED

### Final Command Count
| Namespace | Count |
|-----------|-------|
| `/speckit:*` | 10 |
| `/flow:*` | 14 |
| `/arch:*` | 2 |
| `/dev:*` | 3 |
| `/qa:*` | 2 |
| `/sec:*` | 4 |
| `/ops:*` | 3 |
| **TOTAL** | **38** |

### Validation
- ✅ All tests pass (3067 passed)
- ✅ Linting passes
- ✅ No broken symlinks
- ✅ No deprecation warnings in flowspec commands
<!-- SECTION:NOTES:END -->
