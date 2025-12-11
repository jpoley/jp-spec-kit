# MASTER PLAN: flowspec → flowspec Command Namespace Rename

**Status**: COMPREHENSIVE PLANNING COMPLETE
**Date**: 2025-12-10
**Architect**: Enterprise Software Architect
**Approvals Required**: Technical Lead, Product Owner

---

## Executive Summary

This master plan consolidates all planning artifacts for the comprehensive `flowspec` → `flowspec` command namespace rename across the jp-spec-kit project.

**Core Motivation**: Eliminate UX friction where `/spec` command completion conflicts between `/flow:*` and `/speckit:*` commands.

**Impact**: 397 files, 8-12 hours effort, MEDIUM risk with mitigation strategies in place.

---

## Planning Artifacts

### 1. Architecture Plan (Detailed Technical Blueprint)
**Location**: `/Users/jasonpoley/ps/jp-spec-kit/docs/architecture/flowspec-to-flowspec-rename-plan.md`

**Contains**:
- Strategic framing (penthouse view)
- Architectural blueprint (engine room view)
- Architecture Decision Record (ADR)
- File rename strategy (9 categories A-I)
- Content update strategy (regex patterns)
- Testing strategy (6 phases)
- Risk mitigation and rollback plans
- Implementation checklist
- Timeline and success criteria

**Audience**: Implementation engineers, code reviewers

### 2. Executive Summary (Quick Reference)
**Location**: `/Users/jasonpoley/ps/jp-spec-kit/docs/architecture/flowspec-to-flowspec-rename-summary.md`

**Contains**:
- Quick overview and rationale
- Impact summary
- Implementation phases
- Backward compatibility strategy
- Backlog task list
- Next steps

**Audience**: Project managers, stakeholders, quick reference

### 3. Master Plan (This Document)
**Location**: `/Users/jasonpoley/ps/jp-spec-kit/docs/architecture/flowspec-to-flowspec-MASTER-PLAN.md`

**Contains**:
- Consolidated view of all planning artifacts
- Backlog task mapping
- Execution roadmap
- Final approval checklist

**Audience**: Technical leads, project coordinators

---

## Backlog Task Mapping

### Existing Tasks (Created 2025-12-11 01:32)

| Task | Title | Category | Priority |
|------|-------|----------|----------|
| task-437 | Update GitHub workflow files | Infrastructure | HIGH |
| task-438 | Rename schema files | Schema & Config (Category A) | HIGH |
| task-439 | Migrate command directory structure | Command Directories (Category C) | HIGH |
| task-440 | Rename test files | Tests (Category F) | HIGH |
| task-441 | Update Python source code | Source Code (Category B) | HIGH |
| task-442 | Update shell scripts | Shell Scripts (Category H) | HIGH |
| task-443 | Update documentation files | Documentation (Category G) | MEDIUM |
| task-444 | Create verification suite | Validation | HIGH |
| task-445 | Update example configs | Documentation | MEDIUM |
| task-446 | Create migration guide | Documentation | MEDIUM |

### New Tasks (Created 2025-12-11 01:36)

| Task | Title | Category | Priority |
|------|-------|----------|----------|
| task-447 | Create ADR for rename | Documentation | HIGH |
| task-448 | Rename workflow schema and config files | Schema & Config (Category A) | HIGH |
| task-449 | Update Python source code | Source Code (Category B) | HIGH |
| task-450 | Rename command directories | Command Directories (Category C) | HIGH |
| task-451 | Rename GitHub agents | GitHub Agents (Category D) | MEDIUM |
| task-452 | Rename GitHub prompts | GitHub Prompts (Category E) | MEDIUM |
| task-453 | Rename test files | Tests (Category F) | HIGH |
| task-454 | Update documentation | Documentation (Category G) | HIGH |
| task-455 | Create migration guide | Documentation | MEDIUM |
| task-456 | E2E integration testing | Validation | HIGH |

### Task Consolidation Analysis

**Duplicate Scope** (merge recommended):
- task-438 ≈ task-448 (schema rename)
- task-439 ≈ task-450 (command directories)
- task-440 ≈ task-453 (test files)
- task-441 ≈ task-449 (Python source)
- task-443 ≈ task-454 (documentation)
- task-446 ≈ task-455 (migration guide)
- task-444 ≈ task-456 (validation)

**Unique Tasks**:
- task-437 (GitHub workflows) - infrastructure specific
- task-442 (shell scripts) - separate category
- task-445 (example configs) - subset of documentation
- task-447 (ADR) - architecture documentation
- task-451 (GitHub agents) - new scope
- task-452 (GitHub prompts) - new scope

**Recommendation**: Use tasks 447-456 as primary (more comprehensive acceptance criteria), archive/close tasks 437-446 as superseded.

---

## Execution Roadmap

### Pre-Flight Checklist (Before Starting)

- [ ] **Review & Approval**
  - [ ] Architecture plan reviewed by technical lead
  - [ ] ADR reviewed and approved
  - [ ] Risk mitigation strategies accepted
  - [ ] Rollback plan validated

- [ ] **Environment Preparation**
  - [ ] Create feature branch: `git checkout -b feature/flowspec-to-flowspec-rename`
  - [ ] Create backup branch: `git branch backup/pre-flowspec-rename`
  - [ ] Capture baseline metrics (tests, coverage, linting)
  - [ ] Document current state for comparison

- [ ] **Team Coordination**
  - [ ] Notify team of upcoming rename
  - [ ] Schedule code review time
  - [ ] Block calendar for focused execution (8-12 hours)

### Execution Phases

#### Phase 1: Infrastructure Foundation (2-3 hours)

**Critical Path** (must be done first):

1. **task-447**: Create ADR
   - Document decision rationale
   - Explain options and consequences
   - Link to implementation plan

2. **task-448**: Rename schema and config files
   - `flowspec_workflow.yml` → `flowspec_workflow.yml`
   - `schemas/flowspec_workflow.schema.json` → `schemas/flowspec_workflow.schema.json`
   - Update `src/specify_cli/workflow/config.py` default paths
   - Test config loading

3. **task-450**: Rename command directories
   - `templates/commands/flowspec/` → `templates/commands/flow/`
   - Recreate symlinks in `.claude/commands/flow/`
   - Create backward-compatible symlink
   - Verify command discovery

4. **task-437**: Update GitHub workflows
   - Update workflow file references
   - Update validation scripts
   - Test CI pipelines

**Validation Gate 1**: Schema and config files load correctly, commands discoverable

#### Phase 2: Code & Infrastructure Updates (3-4 hours)

**Parallel Workstreams**:

**Stream A: Source Code**
- **task-449**: Update Python source code (20 files)
- **task-442**: Update shell scripts (7 files)

**Stream B: GitHub Infrastructure**
- **task-451**: Rename GitHub agents (15 files)
- **task-452**: Rename GitHub prompts (31 files)

**Validation Gate 2**: No import errors, linting passes

#### Phase 3: Testing (1-2 hours)

1. **task-453**: Rename test files
   - Rename 14 test files
   - Update imports and fixtures
   - Update assertions
   - Run full test suite

**Validation Gate 3**: All tests pass, coverage ≥ 85%

#### Phase 4: Documentation (2-3 hours)

**Parallel Workstreams**:

**Stream A: Content Updates**
- **task-454**: Update documentation files (300+ files)
- **task-445**: Update example configs

**Stream B: Migration Materials**
- **task-455**: Create migration guide
- Document deprecation timeline
- Create migration scripts

**Validation Gate 4**: No broken links, documentation consistent

#### Phase 5: Final Validation (1-2 hours)

1. **task-456**: E2E integration testing
   - Test all `/flow:*` commands
   - Test workflow state transitions
   - Test backlog integration
   - Test MCP server integration
   - Verify no remaining `flowspec` references

2. **task-444**: Comprehensive verification suite
   - Run automated verification scripts
   - Check for edge cases
   - Final linting and formatting

**Validation Gate 5**: E2E workflows validated, ready for merge

### Post-Execution

- [ ] **Code Review**
  - Create comprehensive pull request
  - Link to architecture plan and ADR
  - Include before/after screenshots
  - Summarize test results

- [ ] **Final Validation**
  - Reviewer runs full test suite
  - Manual verification of key workflows
  - Documentation review

- [ ] **Merge & Release**
  - Merge to main branch
  - Tag release (v0.3.0)
  - Publish release notes
  - Announce in team channels

---

## Risk Management

### Critical Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Breaking existing user workflows** | MEDIUM | HIGH | Phased deprecation (v0.3 → v0.4 → v1.0) |
| **Test failures after rename** | HIGH | HIGH | Comprehensive test suite, baseline metrics |
| **Missed references in edge cases** | MEDIUM | MEDIUM | Automated grep verification, manual review |
| **Documentation drift** | MEDIUM | LOW | Automated link checking, consistency validation |
| **CI/CD pipeline failures** | LOW | HIGH | Test in feature branch, validate before merge |

### Rollback Procedures

**If critical issues discovered during execution**:

1. **Immediate Stop**: Halt execution, document current state
2. **Assess Impact**: Identify root cause, scope of issue
3. **Decision Point**:
   - **Minor issue**: Fix incrementally, continue
   - **Major blocker**: Rollback to backup branch, re-plan

**Rollback Command**:
```bash
git checkout main
git branch -D feature/flowspec-to-flowspec-rename
git checkout backup/pre-flowspec-rename
git checkout -b feature/flowspec-to-flowspec-rename-v2
```

### Quality Gates (Cannot Proceed Without Passing)

**Gate 1: Schema & Config** ✓
- Config files renamed and loading
- Backward compatibility verified

**Gate 2: Source Code** ✓
- No import errors
- Linting passes (ruff check)

**Gate 3: Tests** ✓
- All tests pass (100%)
- Coverage ≥ 85%

**Gate 4: Documentation** ✓
- All docs updated
- No broken links

**Gate 5: E2E Validation** ✓
- Workflows execute correctly
- No remaining old references

---

## Success Criteria

### Technical Success Metrics

- [ ] All 397 files updated correctly
- [ ] Test suite: 100% pass rate
- [ ] Test coverage: ≥ 85% (maintained or improved)
- [ ] Linting: 0 errors (ruff check)
- [ ] No active references to `flowspec` (except historical docs)
- [ ] Backward compatibility: Phase 1 dual support working

### User Experience Metrics

- [ ] Command completion: `/flow` and `/speckit` separate
- [ ] No ambiguity when typing `/flow`
- [ ] Migration guide: clear and comprehensive
- [ ] Deprecation warnings: helpful and actionable
- [ ] No breaking changes for existing users (Phase 1)

### Documentation Quality Metrics

- [ ] All documentation consistent
- [ ] Code examples use `/flow:*`
- [ ] Migration path documented
- [ ] ADR explains rationale
- [ ] Link validation: 0 broken links

---

## Timeline & Effort Estimation

### Serial Execution (Conservative)
**Total**: 8-12 hours over 1-2 days

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Pre-flight | 1 hour | Baseline, branches, approvals |
| Phase 1: Infrastructure | 2-3 hours | Schema, commands, workflows |
| Phase 2: Code & Infrastructure | 3-4 hours | Python, scripts, agents, prompts |
| Phase 3: Testing | 1-2 hours | Tests renamed, all passing |
| Phase 4: Documentation | 2-3 hours | Docs updated, migration guide |
| Phase 5: Validation | 1-2 hours | E2E tests, verification |
| Post-execution | 1 hour | PR, review, merge |

### Parallel Execution (Optimistic)
**Total**: ~6 hours in 1 day

Parallel workstreams in Phases 2 and 4 can reduce total time if multiple engineers work simultaneously.

---

## Approval & Sign-Off

### Pre-Execution Approval

**Architecture Plan**:
- [ ] Technical Lead: _________________ Date: _______
- [ ] Product Owner: _________________ Date: _______

**ADR (task-447)**:
- [ ] Technical Lead: _________________ Date: _______

**Risk Assessment**:
- [ ] Engineering Manager: _________________ Date: _______

### Post-Execution Sign-Off

**Code Review**:
- [ ] Senior Engineer 1: _________________ Date: _______
- [ ] Senior Engineer 2: _________________ Date: _______

**Final Approval to Merge**:
- [ ] Technical Lead: _________________ Date: _______

---

## References

**Planning Documents**:
- [Detailed Architecture Plan](./flowspec-to-flowspec-rename-plan.md)
- [Executive Summary](./flowspec-to-flowspec-rename-summary.md)
- [Master Plan](./flowspec-to-flowspec-MASTER-PLAN.md) (this document)

**Backlog Tasks**:
- Primary tasks: task-447 through task-456
- Legacy tasks (superseded): task-437 through task-446

**Historical Context**:
- Previous rename: `jpspec` → `flowspec` (Dec 2024)
- Git history: `.git/refs/*/rename-jpspec-to-flowspec`

**Key Configuration Files**:
- Current: `flowspec_workflow.yml`, `schemas/flowspec_workflow.schema.json`
- Post-rename: `flowspec_workflow.yml`, `schemas/flowspec_workflow.schema.json`

---

## Questions & Answers

**Q: Why not just rename `/flow:` to `/flow:` and keep internal names?**
A: Creates inconsistency between external commands and internal code. Confusing for contributors and creates technical debt.

**Q: What about users already using `/flow:` commands?**
A: Phased deprecation over 2-3 releases ensures no breaking changes immediately. Dual support in v0.3.x, deprecation warnings in v0.4.x, removal in v1.0.0.

**Q: How long will the deprecation phase last?**
A: Approximately 3-6 months (2-3 release cycles) from v0.3 → v1.0.

**Q: What if we discover issues mid-execution?**
A: Stop immediately, assess severity, either fix incrementally or rollback to backup branch and re-plan.

**Q: Can we add telemetry to track `/flow:` usage?**
A: Yes, recommended. Add in Phase 1 to measure actual usage before final removal in v1.0.

---

## Status & Next Actions

**Current Status**: PLANNING COMPLETE, READY FOR APPROVAL

**Immediate Next Actions**:
1. **Technical Lead Review**: Review architecture plan and ADR
2. **Stakeholder Approval**: Get sign-off on master plan
3. **Schedule Execution**: Block calendar for focused implementation
4. **Create Feature Branch**: Begin execution with task-447 (ADR)

**Blocked Until**:
- [ ] Architecture plan approved
- [ ] Risk mitigation strategies accepted
- [ ] Calendar blocked for execution

---

**Document Version**: 1.0
**Last Updated**: 2025-12-10
**Status**: AWAITING APPROVAL
**Next Review**: After approval, before execution begins
