---
id: task-448
title: Rename workflow schema and config files (flowspec → flowspec)
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-11 01:35'
updated_date: '2025-12-11 01:57'
labels:
  - backend
  - critical
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rename core schema files and root configuration from flowspec to flowspec. This is the critical first step that blocks all other rename tasks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 schemas/flowspec_workflow.schema.json → schemas/flowspec_workflow.schema.json
- [x] #2 memory/flowspec_workflow.yml → memory/flowspec_workflow.yml
- [x] #3 flowspec_workflow.yml → flowspec_workflow.yml (project root)
- [x] #4 src/specify_cli/workflow/config.py updated with new default paths
- [x] #5 Backward compatibility maintained (old filenames still work with deprecation warning)
- [x] #6 Config loading tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Rename flowspec_workflow.yml → flowspec_workflow.yml (root)
2. Rename schemas/flowspec_workflow.schema.json → schemas/flowspec_workflow.schema.json  
3. Rename memory/flowspec_workflow.yml → memory/flowspec_workflow.yml
4. Update src/specify_cli/workflow/config.py with new paths
5. Add backward compatibility layer for old filenames
6. Run config loading tests
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed via scripts/bash/rename-specflow-to-flowspec.sh

All 3066 tests pass.
Symlinks recreated and verified.
468 files changed.
<!-- SECTION:NOTES:END -->
