---
id: task-242
title: Add --constitution flag to specify init command
status: Done
assignee: []
created_date: '2025-12-03 02:36'
updated_date: '2025-12-03 04:15'
labels:
  - cli
  - init
  - constitution
dependencies:
  - task-241
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend specify init to support constitution tier selection for new projects
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add --constitution {light|medium|heavy} CLI flag to specify init
- [ ] #2 Detect empty/new repo and prompt for tier if flag not provided
- [ ] #3 Copy selected constitution template to memory/constitution.md
- [ ] #4 Update init help text with constitution options
- [ ] #5 Tests for --constitution flag behavior
<!-- AC:END -->
