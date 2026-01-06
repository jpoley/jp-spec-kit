---
id: task-507
title: Integrate Claude Code Hooks with Event Emission
status: To Do
assignee:
  - '@chamonix'
created_date: '2025-12-14 03:35'
updated_date: '2026-01-06 18:52'
labels:
  - agent-event-system
  - phase-2
  - architecture
  - hooks
  - event-emission
dependencies:
  - task-486
priority: high
ordinal: 41000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Wire Claude Code hooks to emit events using unified schema.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All 10 Claude Code hook types emit events
- [ ] #2 Events include proper context with task_id branch_name
- [ ] #3 Correlation IDs propagated across hook chains
- [ ] #4 Performance impact under 50ms per hook
- [ ] #5 Backward compatible with existing hook configurations
<!-- AC:END -->
