---
id: task-579.17
title: 'P4.2: Archive build-docs with /spec:* and /flow:operate references'
status: To Do
assignee: []
created_date: '2026-01-06 17:21'
updated_date: '2026-01-06 18:52'
labels:
  - phase-4
  - documentation
  - cleanup
dependencies: []
parent_task_id: task-579
priority: low
ordinal: 90000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Archive or update build documentation that references deprecated commands.

Build-docs with /flow:operate references:
- build-docs/research/ (3 files)
- build-docs/adr/ (9 files)
- build-docs/architecture/ (3 files)
- build-docs/evaluations/ (2 files)
- build-docs/platform/ (3 files)
- build-docs/diagrams/ (1 file)
- build-docs/audit/ (1 file)

Options:
1. Move to build-docs/archive/ with deprecation notice
2. Update to reflect current workflow (if still relevant)
3. Add deprecation header to files
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Build-docs archived or updated
- [ ] #2 Deprecation notices added where appropriate
- [ ] #3 Active docs don't reference deprecated commands
<!-- AC:END -->
