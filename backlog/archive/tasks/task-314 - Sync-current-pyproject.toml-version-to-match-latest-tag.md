---
id: task-314
title: Sync current pyproject.toml version to match latest tag
status: Done
assignee:
  - '@galway'
created_date: '2025-12-08 02:06'
updated_date: '2025-12-15 02:17'
labels:
  - implement
  - version-management
  - quick-fix
dependencies:
  - task-313
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Immediate Fix

Manually sync `pyproject.toml` and `__init__.py` to match the latest git tag.

**Current State**:
- pyproject.toml: `0.2.328`
- Latest tag: `v0.2.334`

**Action**:
1. Update pyproject.toml version to `0.2.334`
2. Update src/specify_cli/__init__.py __version__ to `0.2.334`
3. Commit and push to main

This is a one-time fix while we implement the proper workflow fix in task-313.

**Note**: This should be done AFTER the workflow fix is merged to prevent the old workflow from creating more desynced versions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 pyproject.toml version matches latest git tag
- [x] #2 __init__.py __version__ matches latest git tag
- [x] #3 Changes committed to main
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Complete

**PR**: https://github.com/jpoley/flowspec/pull/635
**Branch**: 314-sync-version
**Commit**: 197df31

### Changes
- pyproject.toml: 0.2.328 → 0.2.343
- __init__.py: 0.2.328 → 0.2.343

One-time sync after task-313 workflow fix.
<!-- SECTION:NOTES:END -->
