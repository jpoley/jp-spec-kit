---
id: task-514
title: Implement Allowed Followups Validation
status: To Do
assignee:
  - '@chamonix'
created_date: '2025-12-14 03:35'
updated_date: '2026-01-06 18:52'
labels:
  - agent-event-system
  - phase-3
  - architecture
  - action-system
dependencies:
  - task-513
priority: medium
ordinal: 48000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Validate action sequences against allowed followups graph.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Followup graph defined matching documentation
- [ ] #2 ValidationError on invalid action sequence
- [ ] #3 Warnings logged for unusual but allowed sequences
- [ ] #4 Query API for valid next actions given current state
- [ ] #5 Visualization of followup graph available
<!-- AC:END -->
