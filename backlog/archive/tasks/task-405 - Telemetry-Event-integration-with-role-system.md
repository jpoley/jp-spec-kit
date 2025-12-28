---
id: task-405
title: 'Telemetry: Event integration with role system'
status: Done
assignee:
  - '@adare'
created_date: '2025-12-10 00:11'
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
Implemented in commit 83ec6e8:
- CLI track commands: track-role, track-agent, track-handoff
- Hooks added to /flow:implement, /flow:validate, /speckit:configure
- integration.py updated to use config-based consent
- All tracking uses fail-safe consent checks
<!-- SECTION:NOTES:END -->
