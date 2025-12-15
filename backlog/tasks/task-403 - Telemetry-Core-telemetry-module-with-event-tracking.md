---
id: task-403
title: 'Telemetry: Core telemetry module with event tracking'
status: Done
assignee:
  - '@adare'
created_date: '2025-12-10 00:10'
updated_date: '2025-12-15 02:18'
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
- [x] #1 RoleEvent enum with event types (role.selected, agent.invoked, handoff.clicked)
- [x] #2 track_role_event() function with PII hashing for project names, paths, usernames
- [x] #3 JSONL writer that appends to .flowspec/telemetry.jsonl
- [x] #4 Event payload includes: timestamp, event_type, role, command, agent (hashed PII)
- [x] #5 Unit tests for RoleEvent, track_role_event(), JSONL writer
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation complete:

1. src/specify_cli/telemetry/events.py
   - RoleEvent enum with 14 event types
   - TelemetryEvent dataclass with to_dict() serialization

2. src/specify_cli/telemetry/tracker.py
   - track_role_event() function
   - hash_pii() for SHA-256 hashing (12 chars)
   - sanitize_path() for home directory paths
   - sanitize_value() for recursive PII detection
   - FLOWSPEC_TELEMETRY_DISABLED env var support

3. src/specify_cli/telemetry/writer.py
   - TelemetryWriter class with JSONL append
   - write_event(), write_events(), read_events()
   - count_events(), clear()

4. tests/test_telemetry.py
   - 33 unit tests covering all functionality
   - All tests pass

Commit: 66d4d66
<!-- SECTION:NOTES:END -->
