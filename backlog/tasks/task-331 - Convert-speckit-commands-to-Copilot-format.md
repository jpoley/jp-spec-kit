---
id: task-331
title: Convert speckit commands to Copilot format
status: To Do
assignee:
  - '@muckross'
created_date: '2025-12-08 22:28'
updated_date: '2025-12-15 02:17'
labels:
  - implement
  - copilot
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Convert all 8 speckit.* commands from .claude/commands/speckit/ to .github/agents/ with correct mode: frontmatter and resolved includes
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All 8 speckit.* files exist in .github/agents/ with correct naming
- [ ] #2 Each file has mode: speckit.<name> frontmatter (not mode: agent)
- [ ] #3 All {{INCLUDE:...}} directives are resolved and embedded
- [ ] #4 Commands appear in VS Code Copilot Chat command picker
- [ ] #5 Commands appear in VS Code Insiders Copilot Chat command picker
<!-- AC:END -->
