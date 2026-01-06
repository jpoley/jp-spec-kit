---
id: task-579.12
title: 'P1.6: Update agent handoffs to use new naming convention'
status: To Do
assignee: []
created_date: '2026-01-06 17:20'
updated_date: '2026-01-06 18:52'
labels:
  - phase-1
  - agents
  - naming
  - release-blocker
dependencies:
  - task-579.08
parent_task_id: task-579
priority: high
ordinal: 85000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update all agent handoff references to use the new PascalCase agent names.

Current handoffs use kebab-case:
```yaml
handoffs:
  - label: "Create Technical Design"
    agent: "flow-plan"
```

Should use PascalCase:
```yaml
handoffs:
  - label: "Create Technical Design"
    agent: "FlowPlan"
```

Affects all agent templates in COPILOT_AGENT_TEMPLATES and templates/.github/agents/
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All handoff agent references use PascalCase
- [ ] #2 Agent handoff chain works correctly
- [ ] #3 Test: verify handoffs resolve to correct agents
<!-- AC:END -->
