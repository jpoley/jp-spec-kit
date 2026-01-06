---
id: task-310.01
title: Fix version detection after upgrade install
status: Done
assignee:
  - '@adare'
created_date: '2025-12-08 01:41'
updated_date: '2025-12-29 12:12'
labels:
  - bug
  - cli
  - upgrade-tools
dependencies: []
parent_task_id: task-310
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fix `_get_installed_jp_spec_kit_version()` to correctly detect the newly installed version after `uv tool install --force` completes.

**Current Problem**: The function runs `specify version` which may return stale version due to shell/OS caching.

**Options**:
1. Trust the install and use `install_version` directly
2. Read version from package metadata via `uv tool list`
3. Use absolute path to the newly installed binary

**Location**: `src/specify_cli/__init__.py:3888-3921` and `4007-4010`
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Version detection returns correct version after fresh install
- [x] #2 No reliance on shell PATH cache
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Already implemented - code trusts install_version directly instead of re-detecting (lines 5157-5159)
<!-- SECTION:NOTES:END -->
