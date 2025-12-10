---
id: task-271
title: Migrate specflow commands to templates
status: Done
assignee:
  - '@template-migrator'
created_date: '2025-12-03 14:01'
updated_date: '2025-12-04 01:24'
labels:
  - architecture
  - migration
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move enhanced specflow commands from .claude/commands/specflow/ to templates/commands/specflow/ to establish single source of truth
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create templates/commands/specflow/ directory
- [x] #2 Copy all 9 enhanced specflow commands to templates (implement, research, validate, plan, specify, operate, assess, prune-branch, _backlog-instructions)
- [x] #3 Verify file sizes match enhanced versions (implement.md ~20KB, not 3KB)
- [x] #4 Verify content is complete with backlog integration
- [x] #5 Update documentation referencing new locations
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Copied enhanced specflow commands from .claude to templates
<!-- SECTION:NOTES:END -->
