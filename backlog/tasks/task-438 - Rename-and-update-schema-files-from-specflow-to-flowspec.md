---
id: task-438
title: Rename and update schema files from flowspec to flowspec
status: To Do
assignee: []
created_date: '2025-12-11 01:32'
labels:
  - platform
  - schema
  - rename
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rename and update JSON schema files and workflow configuration:

Files to rename:
- schemas/flowspec_workflow.schema.json → schemas/flowspec_workflow.schema.json
- memory/flowspec_workflow.schema.json → memory/flowspec_workflow.schema.json
- flowspec_workflow.yml → flowspec_workflow.yml
- memory/flowspec_workflow.yml → memory/flowspec_workflow.yml

Content updates in schema:
1. Update $id field from "flowspec_workflow" to "flowspec_workflow"
2. Update title from "Flowspec Workflow" to "FlowSpec Workflow"
3. Update description references
4. Update command pattern from "^/flow:" to "^/flow:"
5. Update all property descriptions
6. Update example values

Content updates in YAML files:
1. Update all /flow: commands to /flow:
2. Update workflow command references
3. Update descriptions and comments
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Schema files renamed to flowspec_workflow.schema.json
- [ ] #2 YAML config files renamed to flowspec_workflow.yml
- [ ] #3 Schema $id updated to flowspec_workflow
- [ ] #4 Command pattern changed to /flow:
- [ ] #5 Schema validation passes with new filenames
- [ ] #6 All example configs updated to use /flow: commands
<!-- AC:END -->
