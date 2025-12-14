---
id: task-405
title: 'Telemetry: Event integration with role system'
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-10 00:11'
updated_date: '2025-12-14 18:44'
labels:
  - implement
  - backend
  - telemetry
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Integrate telemetry tracking into role selection, agent invocation, and handoff clicks. Track when users interact with role-based commands.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Hook role selection events in init/configure commands
- [x] #2 Hook agent invocation events in /flow:implement, /flow:validate, etc.
- [x] #3 Hook handoff click events in VS Code Copilot agent handoffs
- [x] #4 Check telemetry consent before tracking (fail-safe if disabled)
- [x] #5 Integration tests verifying events are tracked for role/agent/handoff interactions
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation complete:

1. src/specify_cli/telemetry/integration.py
   - track_role_selection() for init/configure commands
   - track_role_change() for role changes
   - track_agent_invocation() context manager
   - track_agent_invocation_decorator() for function decoration
   - track_handoff() for VS Code Copilot handoffs
   - track_command_execution() for /flow commands
   - track_workflow() context manager for workflow lifecycle
   - is_telemetry_enabled() for consent checking

2. Updated src/specify_cli/telemetry/__init__.py
   - Exported all integration helpers

3. tests/test_telemetry_integration.py
   - 15 integration tests
   - TestTelemetryConsent: 4 tests
   - TestRoleSelectionTracking: 3 tests
   - TestAgentInvocationTracking: 3 tests
   - TestHandoffTracking: 1 test
   - TestCommandTracking: 1 test
   - TestWorkflowTracking: 2 tests
   - TestEndToEndIntegration: 1 test (full workflow)

All tests pass. Integration points documented in module docstrings.

Commit: 523abd4
<!-- SECTION:NOTES:END -->
