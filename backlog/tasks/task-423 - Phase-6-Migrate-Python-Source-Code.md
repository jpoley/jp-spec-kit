---
id: task-423
title: 'Phase 6: Migrate Python Source Code'
status: To Do
assignee: []
created_date: '2025-12-10 02:59'
labels:
  - migration
  - python
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update Python source files in src/specify_cli/ with config loading logic, imports, command patterns, and event names. DEPENDS ON: task-422 test migration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Config file references updated: specflow_workflow.yml → specflow_workflow.yml
- [ ] #2 Schema file references updated: specflow_workflow.schema.json → specflow_workflow.schema.json
- [ ] #3 Command pattern regex updated: /specflow: → /specflow:
- [ ] #4 Event names updated: specflow.*.* → specflow.*.*
- [ ] #5 Import statements validated (no specflow module references)
- [ ] #6 All Python files pass linting: ruff check src/
<!-- AC:END -->
