---
id: task-198
title: Define Event Model Schema for jp-spec-kit Hooks
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-03 00:40'
updated_date: '2025-12-03 01:13'
labels:
  - design
  - schema
  - hooks
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Define canonical event types and JSON payload structure for the jp-spec-kit hook system. This is the foundation that all other components depend on.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Document all v1 event types (spec.*, plan.*, task.*, implement.*, validate.*, operate.*)
- [x] #2 Define JSON schema for event payloads with required and optional fields
- [x] #3 Create example events for each type with realistic data
- [x] #4 Document event naming conventions and versioning strategy
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created src/specify_cli/hooks/events.py

Implemented:
- EventType enum with 21 canonical event types (workflow + task)
- Event dataclass with JSON serialization/deserialization
- Artifact dataclass for workflow outputs
- ULID-based event ID generation (evt_<ULID>)
- ISO 8601 UTC timestamps
- Event factory functions for common event types

All AC completed with full test coverage (18 tests)
<!-- SECTION:NOTES:END -->
