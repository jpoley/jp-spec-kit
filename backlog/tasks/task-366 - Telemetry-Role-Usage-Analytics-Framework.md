---
id: task-366
title: 'Telemetry: Role Usage Analytics Framework'
status: To Do
assignee: []
created_date: '2025-12-09 15:14'
updated_date: '2025-12-09 15:48'
labels:
  - infrastructure
  - telemetry
  - phase-4
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add optional telemetry for role usage analytics. DEPENDS ON: All previous tasks. LOW priority - can be deferred.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 RoleEvent enum with event types (role.selected, agent.invoked, handoff.clicked)
- [ ] #2 track_role_event() function with PII hashing
- [ ] #3 JSONL telemetry file format (.jpspec/telemetry.jsonl)
- [ ] #4 Opt-in telemetry via config (telemetry.enabled)
- [ ] #5 Feedback prompt UI designed
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
DEPENDS ON: task-361, task-367

OPTIONAL - can defer

1. Add opt-in telemetry for role selection
2. Track which commands used per role
3. Privacy-preserving aggregation
4. Dashboard for role usage insights
<!-- SECTION:PLAN:END -->
