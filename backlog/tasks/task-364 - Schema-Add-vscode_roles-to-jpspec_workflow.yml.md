---
id: task-364
title: 'Schema: Add vscode_roles to jpspec_workflow.yml'
status: To Do
assignee: []
created_date: '2025-12-09 15:14'
updated_date: '2025-12-09 15:46'
labels:
  - infrastructure
  - schema
  - phase-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create specflow_workflow.yml schema with role definitions. This is the foundation - all other tasks depend on this schema existing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 5 roles defined (pm, dev, sec, qa, all) with descriptions
- [ ] #2 Agent mappings complete for each role
- [ ] #3 Visibility settings (primary_only, hide_others, show_speckit)
- [ ] #4 Schema validation updated to include vscode_roles section
- [ ] #5 Default role configuration (default_role: all)

- [ ] #6 Rename jpspec_workflow.yml to specflow_workflow.yml
- [ ] #7 Add roles section with all 7 roles (pm, arch, dev, sec, qa, ops, all)
- [ ] #8 Each role has: display_name, icon, commands array, agents array
- [ ] #9 Add version 2.0 header
- [ ] #10 Create JSON schema for validation
- [ ] #11 Update specify workflow validate command
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create specflow_workflow.yml template in templates/
2. Define role schema with all 7 roles (pm, arch, dev, sec, qa, ops, all)
3. Map commands to roles per ADR-role-based-command-namespaces.md
4. Map agents to roles per ADR
5. Create JSON schema for validation
6. Update CLI to use new filename
7. Add migration from old jpspec_workflow.yml
<!-- SECTION:PLAN:END -->
