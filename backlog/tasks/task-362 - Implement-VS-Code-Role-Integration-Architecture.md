---
id: task-362
title: 'Implement: VS Code Role Integration Architecture'
status: To Do
assignee: []
created_date: '2025-12-09 15:14'
updated_date: '2025-12-09 15:47'
labels:
  - infrastructure
  - vscode
  - phase-3
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Configure VS Code Copilot to respect role selection. Generate .vscode/settings.json with role-appropriate agent pinning. DEPENDS ON: task-364 (schema), task-367 (command files).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 .vscode/settings.json configuration schema designed
- [ ] #2 Agent filtering mechanism defined (de-prioritize vs hide)
- [ ] #3 Handoff customization per role documented
- [ ] #4 Cross-role handoff approval gates specified
- [ ] #5 VS Code agent pinning integration designed

- [ ] #6 .vscode/settings.json generated with role config
- [ ] #7 Primary role agents pinned to top
- [ ] #8 Handoff priorities reflect role workflow
- [ ] #9 Works in VS Code and VS Code Insiders
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
DEPENDS ON: task-364, task-367

1. Read primary role from specflow_workflow.yml
2. Generate .vscode/settings.json with github.copilot.chat.agents
3. Pin role-appropriate agents to top of list
4. Configure handoff priorities based on role
5. Add chat.promptFiles configuration
6. Test in VS Code and VS Code Insiders
<!-- SECTION:PLAN:END -->
