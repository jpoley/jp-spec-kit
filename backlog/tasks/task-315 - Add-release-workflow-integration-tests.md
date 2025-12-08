---
id: task-315
title: Add release workflow integration tests
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-12-08 02:06'
updated_date: '2025-12-08 02:08'
labels:
  - testing
  - ci
  - github-actions
  - version-management
dependencies:
  - task-313
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Testing

Create integration tests for the release workflow to prevent regression.

**Test Scenarios**:
1. Normal release flow (direct push succeeds)
2. Branch protection flow (PR fallback)
3. PR creation failure (cleanup verification)
4. Version format validation

**Implementation**:
- Use `act` for local GitHub Actions testing
- Create test workflow that validates version consistency
- Add pre-merge check that version files match expected pattern

**Test Assertions**:
- After release, `pyproject.toml` version == latest tag (minus v prefix)
- After release, `__init__.py` __version__ == latest tag (minus v prefix)
- No orphaned branches remain
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Test validates version file/tag consistency
- [ ] #2 Test runs in CI on workflow changes
- [ ] #3 Test can run locally with act
- [ ] #4 Documents test scenarios in test file comments
<!-- AC:END -->
