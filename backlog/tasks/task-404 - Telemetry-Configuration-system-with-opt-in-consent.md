---
id: task-404
title: 'Telemetry: Configuration system with opt-in consent'
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-12-10 00:10'
labels:
  - implement
  - backend
  - telemetry
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement telemetry configuration in specflow_workflow.yml with opt-in consent management. Users must explicitly enable telemetry collection.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add telemetry section to specflow_workflow.yml schema (enabled: bool, consent_date: timestamp)
- [ ] #2 Opt-in only - telemetry disabled by default
- [ ] #3 Consent management API - get_telemetry_consent(), set_telemetry_consent()
- [ ] #4 Respect SPECFLOW_TELEMETRY_ENABLED env var override
- [ ] #5 Config validation in specify workflow validate command
- [ ] #6 Unit tests for config loading, consent management, env var override
<!-- AC:END -->
