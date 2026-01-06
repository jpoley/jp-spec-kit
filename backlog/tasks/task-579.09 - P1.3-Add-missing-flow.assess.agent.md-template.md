---
id: task-579.09
title: 'P1.3: Add missing flow.assess.agent.md template'
status: In Progress
assignee: []
created_date: '2026-01-06 17:20'
updated_date: '2026-01-06 18:50'
labels:
  - phase-1
  - agents
  - templates
  - release-blocker
dependencies: []
parent_task_id: task-579
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add the missing flow.assess.agent.md agent template. Currently only 5 agents exist, should be 6.

Current agents (5):
- flow.specify.agent.md
- flow.plan.agent.md
- flow.implement.agent.md
- flow.validate.agent.md
- flow.submit-n-watch-pr.agent.md

Missing:
- flow.assess.agent.md

The assess agent evaluates feature complexity and determines SDD workflow suitability (full SDD, spec-light, or skip).

Format:
```yaml
---
name: FlowAssess
description: Evaluate feature complexity and determine SDD workflow approach
target: "chat"
tools: [...]
handoffs:
  - label: "Create Specification"
    agent: "FlowSpecify"
---
```
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 flow.assess.agent.md template created
- [ ] #2 Agent added to COPILOT_AGENT_TEMPLATES in __init__.py
- [ ] #3 Template on disk at templates/.github/agents/
- [ ] #4 Agent includes proper handoff to FlowSpecify
- [ ] #5 VSCode shows exactly 6 flow agents
<!-- AC:END -->
