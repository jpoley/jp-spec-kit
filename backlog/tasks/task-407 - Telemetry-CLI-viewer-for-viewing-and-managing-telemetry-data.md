---
id: task-407
title: 'Telemetry: CLI viewer for viewing and managing telemetry data'
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-12-10 00:11'
labels:
  - implement
  - backend
  - telemetry
  - cli
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create CLI commands for users to view, export, and delete their telemetry data. Supports transparency and user control requirements.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 specify telemetry view command shows recent events in table format
- [ ] #2 specify telemetry export command exports to JSON/CSV
- [ ] #3 specify telemetry clear command deletes telemetry file with confirmation
- [ ] #4 specify telemetry stats command shows aggregated usage statistics
- [ ] #5 All commands respect privacy - show hashed values, not raw PII
- [ ] #6 Integration tests for view, export, clear, stats commands
<!-- AC:END -->
