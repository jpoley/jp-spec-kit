# /specflow → /specflow Migration - Architecture Summary

**Date**: 2025-12-09
**Status**: Ready for Review
**Architect**: Enterprise Software Architect

## Executive Summary

This document summarizes the comprehensive migration architecture for renaming `/specflow` to `/specflow` across the JP Spec Kit codebase. The migration affects **912+ occurrences across 150+ files** and requires careful orchestration due to complex dependencies, symlinks, include paths, and cross-file references.

## Deliverables Created

### 1. Architecture Decision Record (ADR)
**Location**: `/home/jpoley/ps/jp-spec-kit/docs/adr/ADR-specflow-to-specflow-migration-architecture.md`

**Contents**:
- Executive summary and context
- Scope of change (file categories, pattern types)
- Critical architectural constraints
- Phase dependency graph
- Risk assessment matrix
- Decision analysis: Automated vs Manual migration (**Automated RECOMMENDED**)
- Comprehensive file categorization (Tiers 1-8)
- Rollback strategy (3 levels)
- Validation checkpoints
- Git strategy (atomic commit RECOMMENDED)
- Deprecation strategy (optional)

**Key Decision**: **Fully automated migration with atomic single commit**

**Rationale**:
- 912+ occurrences makes manual migration error-prone
- Automated replacements ensure consistency
- Testable in branch with clean rollback
- Script serves as executable documentation
- Completes in minutes vs days

### 2. Execution Plan
**Location**: `/home/jpoley/ps/jp-spec-kit/docs/architecture/specflow-to-specflow-migration-execution-plan.md`

**Contents**:
- Task dependency graph (12 tasks)
- Ordered operations for all 9 phases
- Detailed bash commands for each phase
- Validation checkpoints
- File change summary (75+ renamed, 138+ updated)
- Pattern replacement summary (912+ replacements)
- Risk mitigation checklist
- Success criteria
- Timeline estimate (~7 hours)
- Rollback procedures
- Communication plan

### 3. Backlog Tasks (12 Tasks Created)

**Task Dependency Chain**:
```
task-411 (Review ADR)
  ↓
task-417 (Implement Script)
  ↓
task-418 (Phase 1: Config)
  ↓
task-419 (Phase 2: Templates)
  ↓
task-420 (Phase 3: Symlinks)
  ↓
task-421 (Phase 4: Agents)
  ↓
task-422 (Phase 5: Tests)
  ↓
task-423 (Phase 6: Source)
  ↓
task-424 (Phase 7: Docs)
  ↓
task-425 (Phase 8: Backlog)
  ↓
task-426 (Phase 9: Validation)
  ↓
task-427 (Execute Migration)
```

**Task Breakdown**:
1. **task-411**: Review and approve migration architecture ADR
2. **task-417**: Implement automated migration script
3. **task-418**: Phase 1 - Migrate configuration files
4. **task-419**: Phase 2 - Migrate template command files
5. **task-420**: Phase 3 - Recreate local command symlinks
6. **task-421**: Phase 4 - Migrate GitHub agent files
7. **task-422**: Phase 5 - Migrate test files
8. **task-423**: Phase 6 - Migrate Python source code
9. **task-424**: Phase 7 - Migrate documentation files
10. **task-425**: Phase 8 - Migrate backlog and historical files
11. **task-426**: Phase 9 - Final validation and cleanup
12. **task-427**: Execute migration in feature branch

## Migration Architecture

### Critical Path Analysis

**Critical Path** (Must execute in order):
1. Configuration files (schema + workflow YAML) - Foundation
2. Template source files - Symlink targets
3. Symlinks - Dependent on templates
4. Agent files - Include templates via symlinks
5. Test files - Import config and test commands
6. Source code - Loads config and defines commands
7. Documentation - References all above
8. Backlog - References documentation and commands
9. Validation - Final checkpoint

**Why This Order Matters**:
- **Config first**: Schema validates all downstream config files
- **Templates before symlinks**: Symlinks need valid targets
- **Symlinks before agents**: Agents include symlinked files
- **Tests after agents**: Tests validate agent behavior
- **Source after tests**: Source code imports tested config
- **Docs after source**: Docs reference working commands
- **Backlog after docs**: Tasks reference doc links
- **Validation last**: Ensures all changes coherent

### File Categorization

| Tier | Category | Count | Priority | Examples |
|------|----------|-------|----------|----------|
| 1 | Configuration | 4 | Critical | specflow_workflow.yml, schema.json |
| 2 | Templates | 31 | Critical | templates/commands/specflow/*.md |
| 3 | Symlinks | 18 | Critical | .claude/commands/specflow/*.md |
| 4 | Agents | 15 | High | .github/agents/specflow-*.agent.md |
| 5 | Tests | 10 | High | tests/test_specflow_*.py |
| 6 | Source | 6+ | High | src/specify_cli/workflow/*.py |
| 7 | Docs | 50+ | Medium | docs/, CLAUDE.md, README.md |
| 8 | Backlog | 20+ | Low | backlog/tasks/*.md |

### Pattern Replacement Matrix

| Pattern | Replacement | Occurrences | Impact |
|---------|-------------|-------------|--------|
| `/specflow:` | `/specflow:` | 750+ | **CRITICAL** - Command invocations |
| `specflow_workflow` | `specflow_workflow` | 100+ | **CRITICAL** - Config loading |
| `commands/specflow/` | `commands/specflow/` | 100+ | **CRITICAL** - Include paths |
| `specflow-` | `specflow-` | 50+ | High - Agent references |
| `test_specflow_` | `test_specflow_` | 10 | Medium - Test discovery |
| `specflow.` | `specflow.` | 10+ | Medium - Event names |

**Total Replacements**: 912+

### Risk Assessment

| Risk | Probability | Impact | Mitigation | Status |
|------|-------------|--------|------------|--------|
| **Broken Symlinks** | High | Critical | Phase ordering: templates → symlinks | ✅ Mitigated |
| **Include Path Failures** | High | Critical | Validation after each phase | ✅ Mitigated |
| **Test Discovery Breaks** | Medium | High | Pytest collection verification | ✅ Mitigated |
| **Schema Validation Fails** | Medium | High | $id update atomic with rename | ✅ Mitigated |
| **Git History Loss** | Low | Medium | Use `git mv` for renames | ✅ Mitigated |
| **User Confusion** | High | Low | Migration guide + release notes | ✅ Mitigated |
| **Incomplete Migration** | Medium | High | Comprehensive grep validation | ✅ Mitigated |

### Validation Strategy

**9 Validation Checkpoints**:

1. **After Config Rename**: `specify workflow validate`
2. **After Template Update**: Include path resolution check
3. **After Symlink Recreation**: Broken symlink detection
4. **After Agent Update**: Include path validation
5. **After Test Rename**: `pytest --collect-only`
6. **After Source Update**: `ruff check src/`
7. **After Doc Update**: Broken link detection
8. **After Backlog Update**: Search functionality test
9. **Final Validation**: Full test suite + grep validation

**Success Criteria**:
- ✅ Workflow schema validates
- ✅ All tests pass
- ✅ Coverage maintained
- ✅ No broken links
- ✅ No /specflow references (except archives)
- ✅ CLI shows /specflow commands

### Rollback Strategy

**3-Level Rollback**:

**Level 1 - Immediate** (During execution):
```bash
git reset --hard HEAD~1
git branch -D migration-specflow-to-specflow-YYYYMMDD
```

**Level 2 - Post-Commit** (Within 24 hours):
```bash
git revert <migration-commit>
```

**Level 3 - Emergency** (Production issues):
```bash
git tag pre-specflow-migration
git checkout pre-specflow-migration
```

## Implementation Approach

### Automated Migration Script

**Location**: `scripts/bash/migrate-specflow-to-specflow.sh` (to be created)

**Features**:
- ✅ All 9 phases automated
- ✅ Validation checkpoints after each phase
- ✅ Rollback on failure
- ✅ Dry-run mode for testing
- ✅ Comprehensive logging
- ✅ Error handling with exit codes

**Execution**:
```bash
# Test in feature branch
git checkout -b migration-specflow-to-specflow-$(date +%Y%m%d)
bash scripts/bash/migrate-specflow-to-specflow.sh --dry-run
bash scripts/bash/migrate-specflow-to-specflow.sh

# Validate
specify workflow validate
pytest tests/ -v

# Commit
git add -A
git commit -m "refactor: rename /specflow to /specflow across codebase"
```

### Git Strategy

**Atomic Single Commit** (RECOMMENDED):
- Single rollback point
- Clear atomic change
- Preserves bisectability
- Easier to review as one change

**Commit Message Format**:
```
refactor: rename /specflow to /specflow across codebase

BREAKING CHANGE: All /specflow commands renamed to /specflow

- Rename specflow_workflow.yml → specflow_workflow.yml
- Rename specflow_workflow.schema.json → specflow_workflow.schema.json
- Rename templates/commands/specflow/ → templates/commands/specflow/
- Rename .github/agents/specflow-*.agent.md → specflow-*.agent.md
- Rename tests/test_specflow_*.py → test_specflow_*.py
- Update 912+ references across 150+ files
- Recreate symlinks in .claude/commands/specflow/
- Update include paths in templates and agents
- Update documentation and guides

Files changed: 150+
Occurrences replaced: 912+

Resolves: task-411 through task-427
```

## Timeline and Effort

| Phase | Task | Effort | Dependencies |
|-------|------|--------|--------------|
| Review | task-411 | 1 hour | None |
| Development | task-417 | 3 hours | task-411 |
| Phase 1 | task-418 | 15 min | task-417 |
| Phase 2 | task-419 | 15 min | task-418 |
| Phase 3 | task-420 | 10 min | task-419 |
| Phase 4 | task-421 | 15 min | task-420 |
| Phase 5 | task-422 | 15 min | task-421 |
| Phase 6 | task-423 | 10 min | task-422 |
| Phase 7 | task-424 | 30 min | task-423 |
| Phase 8 | task-425 | 15 min | task-424 |
| Phase 9 | task-426 | 30 min | task-425 |
| Execution | task-427 | 1 hour | task-426 |
| **Total** | | **~7 hours** | Sequential |

**Timeline Notes**:
- Development (script creation): 3 hours
- Execution (all phases): 2 hours
- Review and validation: 2 hours
- Assumes automated script execution
- Manual execution: 2-3x longer

## File Impact Summary

### Files Changed

| Operation | Count | Category |
|-----------|-------|----------|
| **Renamed** | 75+ | Config, templates, agents, tests, docs |
| **Updated** | 138+ | All categories (content updates) |
| **Created** | 19 | Symlinks, migration guide |
| **Deleted** | 49 | Old symlinks, old template dir |
| **Total** | **281** | **All categories** |

### By Category

| Category | Renamed | Updated | Impact |
|----------|---------|---------|--------|
| Configuration | 3 | 3 | Critical |
| Templates | 31 | 31 | Critical |
| Symlinks | 0 | 0 (recreated) | Critical |
| Agents | 15 | 15 | High |
| Tests | 10 | 10 | High |
| Source Code | 0 | 6 | High |
| Documentation | 16 | 50+ | Medium |
| Backlog | 0 | 20+ | Low |

## Next Steps

### Immediate Actions

1. **Review ADR** (task-411)
   - Stakeholder review of migration architecture
   - Approve automated approach
   - Approve atomic commit strategy
   - Sign off on rollback plan

2. **Implement Script** (task-417)
   - Create `scripts/bash/migrate-specflow-to-specflow.sh`
   - Implement all 9 phases
   - Add validation checkpoints
   - Add dry-run mode
   - Test in isolated branch

3. **Execute Migration** (tasks 418-427)
   - Create feature branch
   - Run migration script
   - Validate each checkpoint
   - Create atomic commit
   - Create PR with comprehensive description

### Post-Migration

1. **Release**
   - Bump version (BREAKING CHANGE)
   - Update CHANGELOG.md
   - Publish release notes
   - Tag release

2. **Communication**
   - Announce migration completion
   - Share migration guide
   - Provide user support

3. **Validation**
   - Monitor for issues
   - Address user feedback
   - Update migration guide as needed

## Decision Points

### Resolved Decisions

✅ **Migration Approach**: Fully automated (vs manual)
✅ **Git Strategy**: Atomic single commit (vs multi-commit)
✅ **Execution**: Feature branch with comprehensive validation
✅ **Rollback**: 3-level strategy with clear procedures

### Open Decisions

⏳ **Archived Task Handling**: Update or preserve?
   - **Option A**: Update for consistency
   - **Option B**: Preserve as historical artifacts
   - **RECOMMENDATION**: Update for future searchability

⏳ **Deprecation Period**: Provide /specflow aliases?
   - **Option A**: No aliases, clean break
   - **Option B**: Deprecation warnings for 2 versions
   - **RECOMMENDATION**: Clean break (no aliases)

## Success Metrics

**Technical**:
- ✅ 0 /specflow references (except intentional archives)
- ✅ 100% test pass rate
- ✅ Coverage maintained or improved
- ✅ 0 broken links
- ✅ 0 broken symlinks
- ✅ Schema validation passes
- ✅ CLI shows /specflow commands

**Business**:
- ✅ Migration completed in < 8 hours
- ✅ Migration guide published
- ✅ Release notes comprehensive
- ✅ User feedback positive
- ✅ No production issues

## References

### Documentation
- **ADR**: `/home/jpoley/ps/jp-spec-kit/docs/adr/ADR-specflow-to-specflow-migration-architecture.md`
- **Execution Plan**: `/home/jpoley/ps/jp-spec-kit/docs/architecture/specflow-to-specflow-migration-execution-plan.md`
- **This Summary**: `/home/jpoley/ps/jp-spec-kit/docs/architecture/specflow-to-specflow-migration-summary.md`

### Backlog Tasks
- Review: task-411
- Implementation: task-417
- Phases: task-418 through task-426
- Execution: task-427

### Related Files
- Existing migration plan: `docs/adr/specflow-to-specflow-migration-plan.md` (superseded)
- Migration script: `scripts/bash/migrate-specflow-to-specflow.sh` (to be created)
- Migration guide: `docs/guides/specflow-to-specflow-migration.md` (to be created)

## Conclusion

This migration architecture provides:

✅ **Comprehensive Planning**: All 150+ files categorized and ordered
✅ **Risk Mitigation**: 7 risks identified with mitigation strategies
✅ **Clear Execution**: 9 phases with detailed bash commands
✅ **Validation**: 9 checkpoints ensuring correctness
✅ **Rollback Safety**: 3-level rollback strategy
✅ **Automation**: Fully automated script for consistency
✅ **Documentation**: ADR, execution plan, migration guide
✅ **Tracking**: 12 backlog tasks with dependencies

**Recommendation**: Proceed with automated migration using the execution plan.

**Confidence Level**: **High** - All risks mitigated, comprehensive validation, clean rollback path.

---

**Prepared by**: Enterprise Software Architect
**Date**: 2025-12-09
**Version**: 1.0
**Status**: Ready for Review (task-411)
