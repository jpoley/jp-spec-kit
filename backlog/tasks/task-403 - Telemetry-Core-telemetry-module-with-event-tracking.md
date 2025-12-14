---
id: task-403
title: 'Telemetry: Core telemetry module with event tracking'
status: To Do
assignee:
  - '@muckross'
created_date: '2025-12-10 00:10'
updated_date: '2025-12-14 17:48'
labels:
  - implement
  - backend
  - telemetry
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create RoleEvent enum, track_role_event() function, and JSONL telemetry writer. This is the foundation module for telemetry collection.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 RoleEvent enum with event types (role.selected, agent.invoked, handoff.clicked)
- [ ] #2 track_role_event() function with PII hashing for project names, paths, usernames
- [ ] #3 JSONL writer that appends to .flowspec/telemetry.jsonl
- [ ] #4 Event payload includes: timestamp, event_type, role, command, agent (hashed PII)
- [ ] #5 Unit tests for RoleEvent, track_role_event(), JSONL writer
<!-- AC:END -->
