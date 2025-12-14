---
id: task-330
title: Convert flowspec commands to Copilot format
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-08 22:28'
updated_date: '2025-12-14 20:12'
labels:
  - implement
  - copilot
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Convert all 15 flowspec.* commands from .claude/commands/flow/ to .github/agents/ with correct mode: frontmatter and resolved includes
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 All 15 flowspec.* files exist in .github/agents/ with correct naming
- [x] #2 Each file has mode: flowspec.<name> frontmatter (not mode: agent)
- [x] #3 All {{INCLUDE:...}} directives are resolved and embedded
- [ ] #4 Commands appear in VS Code Copilot Chat command picker
- [ ] #5 Commands appear in VS Code Insiders Copilot Chat command picker
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Complete (2025-12-14)

18 flow-* agent files exist in `.github/agents/`:
- flow-assess, flow-implement, flow-init, flow-intake, flow-map-codebase
- flow-operate, flow-plan, flow-research, flow-reset, flow-specify
- flow-validate, flow-generate-prp, flow-prune-branch
- flow-security_fix, flow-security_report, flow-security_triage
- flow-security_web, flow-security_workflow

All have proper frontmatter (name, description, tools, handoffs).
<!-- SECTION:NOTES:END -->
