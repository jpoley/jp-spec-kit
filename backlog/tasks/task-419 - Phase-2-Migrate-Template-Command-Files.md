---
id: task-419
title: 'Phase 2: Migrate Template Command Files'
status: To Do
assignee: []
created_date: '2025-12-10 02:59'
labels:
  - migration
  - templates
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rename templates/commands/specflow/ directory to specflow/ and update all content: command declarations, include paths, references. DEPENDS ON: task-418 configuration migration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Directory templates/commands/specflow/ renamed to specflow/
- [ ] #2 All /specflow: commands updated to /specflow: in 31 template files
- [ ] #3 All include paths updated: {{INCLUDE:.claude/commands/specflow/...}} → specflow/
- [ ] #4 Command frontmatter updated in all templates
- [ ] #5 Validation checkpoint passes: all include paths resolve
- [ ] #6 No broken references in template files
<!-- AC:END -->
