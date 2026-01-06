---
id: task-579.16
title: 'P4.1: Update documentation for command namespace changes'
status: To Do
assignee: []
created_date: '2026-01-06 17:21'
updated_date: '2026-01-06 18:52'
labels:
  - phase-4
  - documentation
dependencies: []
parent_task_id: task-579
priority: medium
ordinal: 89000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update all user documentation to reflect:
1. Removal of /spec:* commands (replaced by /flow:* commands)
2. Removal of /flow:operate (deployment is outer loop)
3. New agent naming conventions (dot notation, PascalCase)

Files to update:
- user-docs/guides/*.md
- docs/guides/*.md
- CLAUDE.md (already partially done)
- README.md

Also update any test references to /spec:* commands.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 User guides updated for /flow:* only workflow
- [ ] #2 /spec:* references removed from documentation
- [ ] #3 /flow:operate references removed from documentation
- [ ] #4 Agent naming conventions documented
- [ ] #5 Test references updated or removed
<!-- AC:END -->
