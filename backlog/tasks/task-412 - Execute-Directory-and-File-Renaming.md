---
id: task-412
title: Execute Directory and File Renaming
status: To Do
assignee: []
created_date: '2025-12-10 02:58'
labels:
  - infrastructure
  - migration
  - rename
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rename directories (templates/commands/specflow, .claude/commands/specflow) and all files containing 'specflow' in their names to 'specflow'.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 templates/commands/specflow renamed to templates/commands/specflow
- [ ] #2 .claude/commands/specflow renamed to .claude/commands/specflow
- [ ] #3 All test files renamed (test_specflow_*.py → test_specflow_*.py)
- [ ] #4 All agent files renamed (.github/agents/specflow-*.agent.md → specflow-*.agent.md)
- [ ] #5 All documentation files renamed (docs/*specflow* → docs/*specflow*)
- [ ] #6 Workflow YAML files renamed (specflow_workflow.yml → specflow_workflow.yml)
<!-- AC:END -->
