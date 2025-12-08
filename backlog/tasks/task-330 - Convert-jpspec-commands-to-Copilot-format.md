---
id: task-330
title: Convert jpspec commands to Copilot format
status: Done
assignee: []
created_date: '2025-12-08 22:28'
updated_date: '2025-12-08 22:48'
labels:
  - implement
  - copilot
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Convert all 15 jpspec.* commands from .claude/commands/jpspec/ to .github/agents/ with correct mode: frontmatter and resolved includes
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 All 15 jpspec.* files exist in .github/agents/ with correct naming
- [x] #2 Each file has mode: jpspec.<name> frontmatter (not mode: agent)
- [x] #3 All {{INCLUDE:...}} directives are resolved and embedded
- [ ] #4 Commands appear in VS Code Copilot Chat command picker
- [ ] #5 Commands appear in VS Code Insiders Copilot Chat command picker
<!-- AC:END -->
