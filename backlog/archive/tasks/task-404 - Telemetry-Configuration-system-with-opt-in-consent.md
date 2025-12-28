---
id: task-404
title: 'Telemetry: Configuration system with opt-in consent'
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
Implement telemetry configuration in flowspec_workflow.yml with opt-in consent management. Users must explicitly enable telemetry collection.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add telemetry section to flowspec_workflow.yml schema (enabled: bool, consent_date: timestamp)
- [x] #2 Opt-in only - telemetry disabled by default
- [x] #3 Consent management API - get_telemetry_consent(), set_telemetry_consent()
- [x] #4 Respect FLOWSPEC_TELEMETRY_ENABLED env var override
- [ ] #5 Config validation in specify workflow validate command
- [ ] #6 Unit tests for config loading, consent management, env var override
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented in commit 83ec6e8:
- config.py with TelemetryConfig dataclass
- Persistent storage in .flowspec/telemetry-config.json
- is_telemetry_enabled() with config + env var support
- enable_telemetry() and disable_telemetry() helpers
- 15 tests in test_telemetry_config.py
<!-- SECTION:NOTES:END -->
