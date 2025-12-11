# Command Namespace Rename: flowspec → flowspec - Executive Summary

**Date**: 2025-12-10
**Status**: Planning Complete
**Architecture Plan**: [flowspec-to-flowspec-rename-plan.md](./flowspec-to-flowspec-rename-plan.md)

---

## Quick Overview

This document summarizes the comprehensive architecture plan for renaming the `flowspec` command namespace to `flowspec` (and `/flow:` to `/flow:`) across the jp-spec-kit project.

## Why This Rename?

**Problem**: When users type `/spec` in command completion:
- Both `/flow:*` and `/speckit:*` commands appear
- Creates cognitive load and poor UX
- Users must type more characters to disambiguate

**Solution**: Rename `/flow:*` → `/flow:*`
- Eliminates namespace collision
- "Flow" clearly indicates workflow commands
- Opens `/spec*` namespace for future expansion

## Impact Summary

**Scope**: 397 files requiring changes
- 32 command/template files
- 46 GitHub agents and prompts
- 14 test files
- 20 Python source files
- 3 config/schema files
- 300+ documentation files

**Effort**: 8-12 hours (excluding extensive testing)

**Risk**: MEDIUM (large surface area, but precedent exists from `jpspec` → `flowspec` rename)

## Implementation Phases

### Phase 1: Infrastructure (2-3 hours)
- Rename schema/config files (`flowspec_workflow.yml` → `flowspec_workflow.yml`)
- Rename command directories (`.claude/commands/flowspec/` → `.claude/commands/flow/`)
- Rename GitHub agents (15 files)
- Rename GitHub prompts (31 files)

### Phase 2: Code & Tests (3-4 hours)
- Update Python source code (20 files)
- Rename and update tests (14 files)
- Ensure all tests pass

### Phase 3: Documentation (2-3 hours)
- Update all documentation (300+ files)
- Create migration guide
- Verify no broken links

### Phase 4: Validation (1-2 hours)
- E2E testing of all workflows
- Comprehensive validation
- Final checks before merge

## Backward Compatibility Strategy

**Phase 1 (v0.3.x)**: Dual Support
- Both `/flow:*` and `/flow:*` work
- Deprecation warnings for `/flow:*`
- Both config filenames supported

**Phase 2 (v0.4.x)**: Deprecation Warnings
- `/flow:*` marked deprecated in CLI help
- Warning messages guide to `/flow:*`

**Phase 3 (v1.0.0)**: Removal
- Remove `/flow:*` aliases
- Only `flowspec_workflow.yml` supported

## Backlog Tasks Created

10 tasks created in backlog.md:

| Task | Title | Priority | Dependencies |
|------|-------|----------|--------------|
| task-447 | Create ADR for rename | High | None |
| task-448 | Rename schema and config files | High | None (CRITICAL - blocks others) |
| task-449 | Update Python source code | High | task-448 |
| task-450 | Rename command directories | High | task-448 |
| task-451 | Rename GitHub agents | Medium | task-450 |
| task-452 | Rename GitHub prompts | Medium | task-450 |
| task-453 | Rename test files | High | task-449 |
| task-454 | Update documentation | High | task-453 |
| task-455 | Create migration guide | Medium | task-454 |
| task-456 | E2E integration testing | High | task-453, task-454 |

**View tasks**: `backlog task list --plain | grep -i flowspec`

## Critical Success Factors

1. **Comprehensive Testing**: Full test suite must pass with ≥85% coverage
2. **No Broken References**: Automated checks for remaining `flowspec` references
3. **Backward Compatibility**: Dual support during Phase 1 (v0.3.x)
4. **Clear Documentation**: Migration guide and updated docs
5. **Validation Gates**: 5 checkpoints before final merge

## Next Steps

1. **Review**: Team reviews architecture plan
2. **Approve**: Get stakeholder approval to proceed
3. **Execute**: Start with task-448 (schema rename)
4. **Test**: Continuous testing at each phase
5. **Merge**: Final validation before merge to main

## Key Files

**Architecture Documentation**:
- `/Users/jasonpoley/ps/jp-spec-kit/docs/architecture/flowspec-to-flowspec-rename-plan.md` (full plan)
- `/Users/jasonpoley/ps/jp-spec-kit/docs/architecture/flowspec-to-flowspec-rename-summary.md` (this file)

**Backlog Tasks**:
- `/Users/jasonpoley/ps/jp-spec-kit/backlog/tasks/task-447*.md` through `task-456*.md`

**Critical Files to Rename**:
- `flowspec_workflow.yml` → `flowspec_workflow.yml`
- `schemas/flowspec_workflow.schema.json` → `schemas/flowspec_workflow.schema.json`
- `.claude/commands/flowspec/` → `.claude/commands/flow/`
- `templates/commands/flowspec/` → `templates/commands/flow/`

## Risk Mitigation

**Rollback Plan**: Backup branch created before starting (`backup/pre-flowspec-rename`)

**Validation Gates**:
- Gate 1: Schema & config files renamed and loading
- Gate 2: Source code updated, no import errors
- Gate 3: Tests pass, coverage maintained
- Gate 4: Documentation complete, no broken links
- Gate 5: E2E workflows validated

## Questions for Review

1. Is the 2-3 release cycle deprecation timeline acceptable?
2. Should we add telemetry to track `/flow:` usage before final removal?
3. Any edge cases not covered in the architecture plan?
4. Should we create a release announcement template?

---

**Status**: Ready for Implementation
**Estimated Completion**: 1-2 days (serial execution) or ~6 hours (parallel execution)
**Architecture Plan Approval**: Pending
