---
id: task-464
title: "claude-improves: Archive deprecated prompts"
status: To Do
assignee: []
created_date: '2025-12-12 01:15'
labels:
  - claude-improves
  - source-repo
  - prompts
  - cleanup
  - phase-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
13 deprecated prompts exist in .github/prompts/ that should be archived or removed:
- specflow._DEPRECATED_*.prompt.md (13 files)

These clutter the prompts directory and may cause confusion.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create .github/prompts/archive/ directory
- [ ] #2 Move all *DEPRECATED* files to archive directory
- [ ] #3 Verify no deprecated files remain in main prompts directory
- [ ] #4 Update any documentation referencing these prompts
<!-- AC:END -->
