# PRD: Version Management System Fix

**Status**: Draft
**Author**: @pm-planner
**Date**: 2025-12-07
**Priority**: High

---

## 1. Executive Summary

### Problem Statement
The version management system between git tags and `pyproject.toml` is fundamentally broken. Tags are created before source files are updated, leading to persistent version desync. The fallback mechanism for version bump commits creates orphaned branches and uses buggy naming conventions.

### Proposed Solution
Refactor the release workflow to update version files BEFORE creating tags, ensuring source-of-truth consistency. Fix branch naming bugs and add proper cleanup automation.

### Success Metrics
- **North Star**: Version in `pyproject.toml` matches the latest git tag 100% of the time
- **Leading indicators**: Zero orphaned `chore/version-bump-*` branches
- **Lagging indicators**: Zero manual version sync interventions needed

### Business Value
- Eliminates manual version sync interventions
- Reduces developer confusion about current version
- Improves release reliability and trustworthiness

---

## 2. User Stories and Use Cases

### Primary Persona
**Developer** - Uses `specify --version` or checks `pyproject.toml` to know what version is installed/current.

### User Stories

**US-1**: As a developer, I want `pyproject.toml` version to always match the latest git tag so I know what version I'm working with.

**US-2**: As a release maintainer, I want the release workflow to not leave orphaned branches so the repository stays clean.

**US-3**: As a CI system, I want version updates to complete successfully even with branch protection so releases are fully automated.

### Edge Cases
- Branch protection prevents direct push to main
- PR creation fails due to permissions
- Multiple releases in quick succession

---

## 3. DVF+V Risk Assessment

### Value Risk (Desirability)
- **Risk**: Low - developers consistently report confusion about version mismatches
- **Validation**: Current state analysis shows 6+ version gap (pyproject says 0.2.328, tags show v0.2.334)

### Usability Risk (Experience)
- **Risk**: Low - this is a backend/workflow fix, no UI changes
- **Validation**: N/A

### Feasibility Risk (Technical)
- **Risk**: Medium - need to handle branch protection edge cases
- **Validation**:
  - Option A: Update files, commit, then tag (requires push before tag)
  - Option B: Use GitHub API to update files
  - Option C: Use a bot account with write access

### Business Viability Risk (Organizational)
- **Risk**: Low - this is a critical infrastructure fix
- **Validation**: Existing bugs already documented in task-311.*

---

## 4. Functional Requirements

### Core Features

**FR-1: Version File First Update**
- Update `pyproject.toml` and `__init__.py` BEFORE creating the git tag
- Commit version changes with `[skip ci]` to prevent loop
- Create tag pointing to the version bump commit

**FR-2: Branch Naming Fix**
- Strip `v` prefix from version before creating branch name
- Branch format: `chore/version-bump-X.Y.Z` (no double dash)

**FR-3: Branch Cleanup**
- Delete branch after PR is merged (GitHub setting)
- Delete branch if PR creation fails
- Add scheduled workflow to prune stale version-bump branches

**FR-4: Fallback Resilience**
- If direct push fails, create PR properly
- If PR creation fails, still clean up branch
- Log clear error messages for manual intervention if all else fails

### API Requirements
N/A - This is a CI/CD workflow fix.

### Integration Requirements
- GitHub Actions workflow modification
- GitHub repository settings (auto-delete branches)

### Data Requirements
N/A

---

## 5. Non-Functional Requirements

### Performance
- Release workflow should complete in < 5 minutes

### Reliability
- Version sync must succeed 100% of the time or fail loudly

### Security
- Use `GITHUB_TOKEN` with minimal required permissions
- No secrets exposure in logs

---

## 6. Task Breakdown (Backlog Tasks)

### Existing Related Tasks
The following tasks already exist and should be referenced:
- **task-311**: Fix orphaned chore/version-bump branches not being cleaned up (MEDIUM)
- **task-311.01**: Fix double-dash in version-bump branch name (HIGH)
- **task-311.03**: Enable auto-delete branch on PR merge in GitHub repo settings (MEDIUM)
- **task-311.04**: Add scheduled workflow to cleanup stale version-bump branches (LOW)

### New Tasks Needed

See task creation below.

---

## 7. Discovery and Validation Plan

### Learning Goals
1. Confirm the root cause of version desync
2. Validate that version-first approach works with branch protection

### Validation Experiments
1. Test workflow locally with `act`
2. Create test branch to verify workflow changes

### Go/No-Go Decision Points
- If version-first approach conflicts with branch protection, evaluate GitHub API option

---

## 8. Acceptance Criteria and Testing

### Definition of Done
- [ ] `pyproject.toml` version matches latest git tag after release
- [ ] No orphaned `chore/version-bump-*` branches after release
- [ ] Branch names use single dash: `chore/version-bump-0.2.335`
- [ ] All related tests pass

### Test Scenarios
1. Successful release with direct push
2. Release with branch protection (PR path)
3. Release when PR creation fails (cleanup path)

---

## 9. Dependencies and Constraints

### Technical Dependencies
- GitHub Actions
- Repository branch protection rules

### External Dependencies
- GitHub API availability

### Constraints
- Must work with existing branch protection
- Cannot disable branch protection

### Risk Factors
- Branch protection may prevent any direct updates to main
- May need to evaluate GitHub App with elevated permissions

---

## 10. Success Metrics (Outcome-Focused)

### North Star Metric
**Version Consistency Rate**: % of releases where `pyproject.toml` matches the latest tag = 100%

### Leading Indicators
- Zero orphaned branches created per release
- Release workflow completion rate = 100%

### Lagging Indicators
- Zero manual version sync PRs needed
- Zero developer complaints about version mismatch

### Measurement Approach
- Monitor release workflow logs
- Periodic audit of branches matching `chore/version-bump-*`

### Target Values
- Version consistency: 100%
- Orphaned branches: 0
- Manual interventions: 0

---

## Appendix: Root Cause Analysis

### Current Workflow (Buggy)
```
1. Determine next version from tags
2. Create git tag  <-- TAG CREATED HERE
3. Create GitHub release
4. Update pyproject.toml and __init__.py  <-- VERSION FILES UPDATED AFTER TAG
5. Commit and push (may fail)
6. If push fails, create branch and PR (may fail)
7. If PR fails, leave orphaned branch  <-- BUG
```

### Proposed Workflow (Fixed)
```
1. Determine next version from tags
2. Update pyproject.toml and __init__.py  <-- VERSION FILES FIRST
3. Commit with [skip ci]
4. Push (or create PR if protected)
5. Create git tag pointing to version commit  <-- TAG AFTER VERSION
6. Create GitHub release
7. Cleanup any temp branches on failure
```

### Files to Modify
- `.github/workflows/release.yml` (main workflow)
- `.github/workflows/scripts/update-version.sh` (may need changes)
- Repository settings (enable auto-delete branches)
