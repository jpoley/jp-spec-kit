---
id: task-407
title: 'Telemetry: CLI viewer for viewing and managing telemetry data'
status: Done
assignee:
  - '@adare'
created_date: '2025-12-10 00:11'
updated_date: '2025-12-15 02:18'
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
- [x] #1 specify telemetry view command shows recent events in table format
- [x] #2 specify telemetry export command exports to JSON/CSV
- [x] #3 specify telemetry clear command deletes telemetry file with confirmation
- [ ] #4 specify telemetry stats command shows aggregated usage statistics
- [ ] #5 All commands respect privacy - show hashed values, not raw PII
- [ ] #6 Integration tests for view, export, clear, stats commands
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented in commit 83ec6e8:
- specify telemetry stats
- specify telemetry view
- specify telemetry clear
- specify telemetry export
<!-- SECTION:NOTES:END -->
