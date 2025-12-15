---
id: task-315
title: Add release workflow integration tests
status: Done
assignee:
  - '@galway'
created_date: '2025-12-08 02:06'
updated_date: '2025-12-15 02:17'
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
- [x] #1 Test validates version file/tag consistency
- [x] #2 Test runs in CI on workflow changes
- [x] #3 Test can run locally with act
- [x] #4 Documents test scenarios in test file comments
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Complete (v2)

**PR**: https://github.com/jpoley/flowspec/pull/637
**Branch**: 315-workflow-tests
**Commit**: 9c9ed91

### Review Fixes (v2)
1. Clarified fetch-depth comment
2. Added validation for pyproject.toml extraction
3. Added validation for __init__.py extraction
4. Handle gracefully when no tags exist
5. Summary only runs on success()

### Created
`.github/workflows/version-check.yml`

### Checks
- pyproject.toml == __init__.py version
- Version format validation (MAJOR.MINOR.PATCH)
- Extraction success validation
- Graceful no-tags handling
<!-- SECTION:NOTES:END -->
