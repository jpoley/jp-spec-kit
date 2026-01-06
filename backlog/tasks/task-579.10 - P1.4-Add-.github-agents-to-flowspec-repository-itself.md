---
id: task-579.10
title: 'P1.4: Add .github/agents/ to flowspec repository itself'
status: To Do
assignee: []
created_date: '2026-01-06 17:20'
updated_date: '2026-01-06 18:52'
labels:
  - phase-1
  - agents
  - infrastructure
  - release-blocker
dependencies: []
parent_task_id: task-579
priority: high
ordinal: 83000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add deployed .github/agents/ directory to the flowspec repository itself so VSCode Copilot integration works when developing flowspec.

Currently flowspec only has:
- templates/.github/agents/ (template sources)

Should also have:
- .github/agents/ (deployed for flowspec repo)

This enables flowspec developers to use the VSCode agent integration while working on flowspec itself.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 .github/agents/ directory created in flowspec repo
- [ ] #2 All 6 agents deployed with correct naming
- [ ] #3 VSCode agent integration works in flowspec repo
- [ ] #4 Agents match templates/.github/agents/ content
<!-- AC:END -->
