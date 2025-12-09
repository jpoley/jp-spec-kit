---
id: task-361
title: 'Design: Role Selection in Init/Reset Commands'
status: To Do
assignee: []
created_date: '2025-12-09 15:13'
updated_date: '2025-12-09 15:47'
labels:
  - infrastructure
  - commands
  - phase-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add role selection prompts to /speckit:init and /speckit:configure commands. Users select their primary role during project setup. DEPENDS ON: task-364 (schema must exist first).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Define role selection UX with 5 roles (PM, Dev, Sec, QA, All)
- [ ] #2 Determine configuration storage location (jpspec_workflow.yml + .vscode/settings.json)
- [ ] #3 Document role-to-command mappings
- [ ] #4 Specify multi-role support (primary + secondary roles)
- [ ] #5 Define team vs user mode configuration

- [ ] #6 Interactive prompt displays all 7 roles with icons
- [ ] #7 Selected role stored in specflow_workflow.yml
- [ ] #8 Non-interactive mode via --role flag
- [ ] #9 SPECFLOW_PRIMARY_ROLE env var override works
- [ ] #10 init.md template updated
- [ ] #11 reset.md renamed to configure.md
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
DEPENDS ON: task-364

1. Read role definitions from specflow_workflow.yml
2. Add interactive prompt showing all 7 roles with icons
3. Store selection in specflow_workflow.yml roles.primary field
4. Support --role flag for non-interactive mode
5. Support SPECFLOW_PRIMARY_ROLE env var override
6. Update init.md template
7. Rename reset.md to configure.md
<!-- SECTION:PLAN:END -->
