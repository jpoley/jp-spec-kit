---
id: task-529
title: Implement Container Cleanup Automation
status: To Do
assignee:
  - '@chamonix'
created_date: '2025-12-14 03:35'
updated_date: '2026-01-06 18:52'
labels:
  - agent-event-system
  - phase-5
  - infrastructure
  - devops
  - container
dependencies:
  - task-526
priority: medium
ordinal: 63000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Automatically stop and remove containers when tasks complete.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Cleanup triggered by task.completed or task.archived events
- [ ] #2 Script container-cleanup.sh task-id
- [ ] #3 Saves container logs before removal
- [ ] #4 Emits container.stopped event with exit code
- [ ] #5 Force-kill containers running over 24 hours
<!-- AC:END -->
