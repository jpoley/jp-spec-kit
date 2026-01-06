---
id: task-535
title: Implement Automated Cleanup Orchestrator
status: To Do
assignee:
  - '@chamonix'
created_date: '2025-12-14 03:35'
updated_date: '2026-01-06 18:52'
labels:
  - agent-event-system
  - phase-7
  - architecture
  - automation
dependencies:
  - task-516
  - task-529
priority: medium
ordinal: 69000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create orchestrator that monitors events and triggers cleanup actions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CleanupOrchestrator class listening for completion events
- [ ] #2 Triggers worktree cleanup on task.completed
- [ ] #3 Triggers container cleanup on task.archived
- [ ] #4 Configurable cleanup delays and conditions
- [ ] #5 Emits lifecycle.cleanup_completed events
<!-- AC:END -->
