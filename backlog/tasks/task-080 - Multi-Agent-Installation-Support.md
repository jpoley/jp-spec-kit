---
id: task-080
title: Multi-Agent Installation Support
status: To Do
assignee: []
created_date: '2025-11-27 21:53'
labels:
  - specify-cli
  - feature
  - multi-agent
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Allow users to install spec-kit for multiple AI coding agents (not just one) during 'specify init'. Teams often use mixed agents (Claude for backend, Copilot for frontend). Implementation: Interactive multi-select with checkboxes, comma-separated --ai flag support (e.g., --ai claude,copilot,cursor). Agent directories are already independent (no conflicts). Feasibility: HIGH, 1-3 days effort. See TODO/task-012b-summary.md for detailed plan.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Implement parse_agent_list() for comma-separated input
- [ ] #2 Create multi-select UI with checkbox interface
- [ ] #3 Update init() to accept multiple agents via --ai flag
- [ ] #4 Implement download logic for multiple templates
- [ ] #5 Update tool checks for multiple CLI-based agents
- [ ] #6 Maintain backward compatibility (single agent still works)
- [ ] #7 Update documentation with multi-agent examples
- [ ] #8 Create tests for multi-agent combinations
<!-- AC:END -->
