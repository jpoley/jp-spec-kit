---
id: task-418
title: 'Phase 1: Migrate Configuration Files'
status: To Do
assignee: []
created_date: '2025-12-10 02:58'
labels:
  - migration
  - configuration
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rename and update workflow configuration files: specflow_workflow.yml, specflow_workflow.schema.json. Update schema $id field to match new filename. DEPENDS ON: task-417 script completion.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 memory/specflow_workflow.schema.json renamed to specflow_workflow.schema.json
- [ ] #2 Schema $id field updated to specflow_workflow.schema.json
- [ ] #3 memory/specflow_workflow.yml renamed to specflow_workflow.yml
- [ ] #4 Root specflow_workflow.yml renamed to specflow_workflow.yml
- [ ] #5 Command patterns in schema updated to /specflow:
- [ ] #6 Workflow validation passes: specify workflow validate
<!-- AC:END -->
