---
id: task-445
title: Update example workflow configurations for flowspec rename
status: To Do
assignee: []
created_date: '2025-12-11 01:32'
labels:
  - documentation
  - examples
  - rename
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update all example workflow configurations in docs/examples/workflows/:

Files to update:
- docs/examples/workflows/custom-agents-workflow.yml
- docs/examples/workflows/minimal-workflow.yml
- docs/examples/workflows/parallel-workflows.yml
- docs/examples/workflows/security-audit-workflow.yml

Updates needed:
1. Update command references: /flow: → /flow:
2. Update schema references in comments
3. Update workflow names if they include 'flowspec'
4. Update agent configuration examples
5. Ensure examples validate against new flowspec_workflow.schema.json

Validation:
- Run schema validation on each example
- Test examples against real workflow validator
- Update any example documentation
- Verify examples in related guides still reference correct files
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All workflow examples use /flow: commands
- [ ] #2 Examples validate against flowspec_workflow.schema.json
- [ ] #3 Schema references in comments updated
- [ ] #4 Examples execute successfully in test environment
- [ ] #5 Related documentation updated to reference correct example files
<!-- AC:END -->
