---
id: task-516
title: Implement Worktree Cleanup Automation
status: To Do
assignee:
  - '@chamonix'
created_date: '2025-12-14 03:35'
updated_date: '2026-01-06 18:52'
labels:
  - agent-event-system
  - phase-4
  - infrastructure
  - scm
  - git-workflow
dependencies:
  - task-515
priority: medium
ordinal: 50000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create cleanup automation for completed or abandoned task worktrees.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Script worktree-cleanup.sh task-id
- [ ] #2 Removes worktree safely checks for uncommitted changes
- [ ] #3 Optionally deletes branch if merged
- [ ] #4 Emits git.worktree_removed and git.branch_deleted events
- [ ] #5 Post-merge hook triggers automatic cleanup
<!-- AC:END -->
