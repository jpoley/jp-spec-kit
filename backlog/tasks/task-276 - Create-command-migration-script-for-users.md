---
id: task-276
title: Create command migration script for users
status: To Do
assignee: []
created_date: '2025-12-03 14:01'
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
- [ ] #1 Create scripts/bash/migrate-commands-to-subdirs.sh
- [ ] #2 Script moves jpspec.*.md files to jpspec/ subdirectory
- [ ] #3 Script moves speckit.*.md files to speckit/ subdirectory
- [ ] #4 Script provides clear output showing file moves
- [ ] #5 Test script on sample flat structure
- [ ] #6 Document script usage in upgrade guide
<!-- AC:END -->
