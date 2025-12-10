---
id: task-409
title: 'Telemetry: Comprehensive test suite and privacy verification'
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-12-10 00:11'
labels:
  - implement
  - backend
  - telemetry
  - testing
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create comprehensive test suite covering all telemetry functionality including privacy verification tests. Ensures telemetry is secure and privacy-preserving.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Unit tests for all telemetry modules (RoleEvent, tracking, config, privacy)
- [ ] #2 Integration tests for end-to-end telemetry flow (event -> tracking -> storage)
- [ ] #3 Privacy verification tests - assert no raw PII in telemetry.jsonl
- [ ] #4 Consent enforcement tests - verify tracking fails when disabled
- [ ] #5 Performance tests - telemetry overhead < 50ms per event
- [ ] #6 Test coverage > 90% for telemetry modules
<!-- AC:END -->
