---
id: task-276
title: Create command migration script for users
status: Done
assignee:
  - '@galway'
created_date: '2025-12-03 14:01'
updated_date: '2025-12-05 01:35'
labels:
  - tooling
  - migration
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Write migration script to convert existing projects from flat structure to subdirectory structure
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create scripts/bash/migrate-commands-to-subdirs.sh
- [x] #2 Script moves jpspec.*.md files to jpspec/ subdirectory
- [x] #3 Script moves speckit.*.md files to speckit/ subdirectory
- [x] #4 Script provides clear output showing file moves
- [x] #5 Test script on sample flat structure
- [x] #6 Document script usage in upgrade guide
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
PR #502 created with migration script.

Implementation:
- Created `scripts/bash/migrate-commands-to-subdirs.sh`
- Script supports --dry-run and --path options
- Migrates jpspec.*.md -> jpspec/*.md
- Migrates speckit.*.md -> speckit/*.md
- Includes broken symlink detection
- Documentation added to scripts/CLAUDE.md

AC #6 (document in upgrade guide) covered in task-279.

Merged via PR #505 (which included all content from closed PR #502 + symlink fix).
<!-- SECTION:NOTES:END -->
