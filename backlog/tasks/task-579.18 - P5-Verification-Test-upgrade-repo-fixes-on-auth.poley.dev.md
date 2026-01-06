---
id: task-579.18
title: 'P5: Verification - Test upgrade-repo fixes on auth.poley.dev'
status: To Do
assignee: []
created_date: '2026-01-06 17:21'
updated_date: '2026-01-06 18:52'
labels:
  - phase-5
  - verification
  - testing
  - release-blocker
dependencies:
  - task-579.01
  - task-579.02
  - task-579.03
  - task-579.04
  - task-579.05
  - task-579.06
  - task-579.07
  - task-579.08
  - task-579.09
  - task-579.10
  - task-579.11
  - task-579.12
  - task-579.13
  - task-579.14
parent_task_id: task-579
priority: high
ordinal: 91000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After all fixes are implemented, re-run flowspec upgrade-repo on auth.poley.dev to verify fixes work correctly.

Verification checklist:
- [ ] Agent files created with dot notation (flow.assess.agent.md)
- [ ] Agent names are PascalCase in VSCode dropdown
- [ ] .mcp.json updated with required servers
- [ ] flowspec_workflow.yml upgraded to v2.0
- [ ] .specify/ directory removed
- [ ] _DEPRECATED_operate.md removed
- [ ] Skills synced (21 skills present)
- [ ] No {{INCLUDE:}} directives in command files
- [ ] No /flow:operate references
- [ ] No /spec:* commands

This is the final gate before release.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 flowspec upgrade-repo runs successfully on auth.poley.dev
- [ ] #2 All verification checklist items pass
- [ ] #3 VSCode shows 6 FlowXxx agents with correct names
- [ ] #4 All MCP servers configured and functional
- [ ] #5 No deprecated artifacts remain
<!-- AC:END -->
