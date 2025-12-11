---
id: task-405
title: 'Telemetry: Event integration with role system'
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-12-10 00:11'
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
- [ ] #1 Hook role selection events in init/configure commands
- [ ] #2 Hook agent invocation events in /flow:implement, /flow:validate, etc.
- [ ] #3 Hook handoff click events in VS Code Copilot agent handoffs
- [ ] #4 Check telemetry consent before tracking (fail-safe if disabled)
- [ ] #5 Integration tests verifying events are tracked for role/agent/handoff interactions
<!-- AC:END -->
