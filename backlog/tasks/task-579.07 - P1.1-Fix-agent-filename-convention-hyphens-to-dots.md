---
id: task-579.07
title: 'P1.1: Fix agent filename convention - hyphens to dots'
status: In Progress
assignee: []
created_date: '2026-01-06 17:20'
updated_date: '2026-01-06 18:49'
labels:
  - phase-1
  - agents
  - naming
  - release-blocker
dependencies: []
parent_task_id: task-579
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fix the agent filename convention in COPILOT_AGENT_TEMPLATES to use DOT notation instead of HYPHEN notation.

Current (WRONG):
- flow-specify.agent.md
- flow-plan.agent.md
- flow-implement.agent.md

Target (CORRECT):
- flow.specify.agent.md
- flow.plan.agent.md
- flow.implement.agent.md

Location: src/flowspec_cli/__init__.py (COPILOT_AGENT_TEMPLATES dictionary, lines 191-551)

This aligns with VSCode Copilot agent discovery conventions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 COPILOT_AGENT_TEMPLATES keys use dot notation (flow.specify.agent.md)
- [ ] #2 Templates on disk renamed to dot notation
- [ ] #3 flowspec init creates agents with dot-notation filenames
- [ ] #4 Test: verify agent files created with correct naming
<!-- AC:END -->
