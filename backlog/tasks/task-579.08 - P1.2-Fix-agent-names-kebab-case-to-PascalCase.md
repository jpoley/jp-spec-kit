---
id: task-579.08
title: 'P1.2: Fix agent names - kebab-case to PascalCase'
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
Fix the agent name field in COPILOT_AGENT_TEMPLATES frontmatter to use PascalCase instead of kebab-case.

Current (WRONG):
```yaml
name: "flow-specify"
name: "flow-implement"
```

Target (CORRECT):
```yaml
name: FlowSpecify
name: FlowImplement
```

The name field controls what appears in VSCode's agent dropdown menu.

Location: src/flowspec_cli/__init__.py (COPILOT_AGENT_TEMPLATES dictionary, lines 191-551)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Agent name fields use PascalCase (FlowSpecify, FlowPlan, etc.)
- [ ] #2 VSCode agent menu shows professional names
- [ ] #3 Test: verify agent names display correctly in VSCode dropdown
<!-- AC:END -->
