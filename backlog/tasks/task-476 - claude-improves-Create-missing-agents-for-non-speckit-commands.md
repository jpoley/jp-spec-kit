---
id: task-476
title: 'claude-improves: Create missing agents for non-speckit commands'
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2026-01-06 18:52'
labels:
  - claude-improves
  - source-repo
  - agents
  - copilot
  - phase-2
dependencies: []
priority: high
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
9 agents exist for speckit commands, but 14 other commands (dev/*, ops/*, qa/*, sec/*, arch/*) have prompts without corresponding agents.

Each command namespace should have agent support for GitHub Copilot users.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create agents for dev/* commands (debug, refactor, cleanup)
- [ ] #2 Create agents for ops/* commands (monitor, respond, scale)
- [ ] #3 Create agents for qa/* commands (review, test)
- [ ] #4 Create agents for sec/* commands (fix, report, scan, triage)
- [ ] #5 Create agents for arch/* commands (decide, model)
- [ ] #6 All agents follow consistent naming: namespace-command.agent.md
- [ ] #7 Agents reference corresponding command prompts
<!-- AC:END -->
