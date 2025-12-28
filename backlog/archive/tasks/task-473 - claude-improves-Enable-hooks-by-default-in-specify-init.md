---
id: task-473
title: 'claude-improves: Enable hooks by default in specify init'
status: Done
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2025-12-15 02:18'
labels:
  - claude-improves
  - cli
  - specify-init
  - hooks
  - phase-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
All 4 hooks in .specify/hooks/hooks.yaml are created with `enabled: false`:
- run-tests (post-implementation)
- update-changelog (on spec creation)
- lint-code (on task completion)
- quality-gate (before validation)

Critical hooks should be enabled by default or user should be prompted during init.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 run-tests hook enabled by default
- [x] #2 lint-code hook enabled by default
- [x] #3 quality-gate hook enabled by default
- [x] #4 update-changelog remains opt-in (disabled by default)
- [x] #5 Add --no-hooks flag to disable all hooks
- [x] #6 Document enabled hooks in init output summary
<!-- AC:END -->
