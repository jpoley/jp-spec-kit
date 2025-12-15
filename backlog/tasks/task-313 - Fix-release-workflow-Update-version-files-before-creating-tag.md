---
id: task-313
title: 'Fix release workflow: Update version files before creating tag'
status: Done
assignee:
  - '@galway'
created_date: '2025-12-08 02:05'
updated_date: '2025-12-15 13:43'
labels:
  - implement
  - ci
  - github-actions
  - version-management
dependencies:
  - task-312
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Core Fix

Refactor `.github/workflows/release.yml` to update version files BEFORE creating the git tag.

**Current Order (Buggy)**:
1. Determine next version
2. Create git tag
3. Create release
4. Update version files (often fails)

**New Order (Fixed)**:
1. Determine next version
2. Update version files (pyproject.toml, __init__.py)
3. Commit with [skip ci]
4. Push to main (or create PR if protected)
5. Create git tag pointing to version commit
6. Create release

**Key Changes**:
- Move "Update version in source files" step BEFORE "Create git tag"
- Tag must point to the commit that has the updated version
- Handle branch protection gracefully

**Related PRD**: docs/prd/version-management-fix-prd.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Version files updated before tag creation
- [ ] #2 Tag points to commit with updated version
- [ ] #3 Works with branch protection (PR fallback)
- [ ] #4 [skip ci] prevents infinite loop
- [ ] #5 Tested with act locally before merge
<!-- AC:END -->
