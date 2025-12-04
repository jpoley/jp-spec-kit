---
id: task-271
title: Migrate jpspec commands to templates
status: Done
assignee:
  - '@template-migrator'
created_date: '2025-12-03 14:01'
updated_date: '2025-12-03 14:14'
labels:
  - architecture
  - migration
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move enhanced jpspec commands from .claude/commands/jpspec/ to templates/commands/jpspec/ to establish single source of truth
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create templates/commands/jpspec/ directory
- [ ] #2 Copy all 9 enhanced jpspec commands to templates (implement, research, validate, plan, specify, operate, assess, prune-branch, _backlog-instructions)
- [ ] #3 Verify file sizes match enhanced versions (implement.md ~20KB, not 3KB)
- [ ] #4 Verify content is complete with backlog integration
- [ ] #5 Update documentation referencing new locations
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Copied enhanced jpspec commands from .claude to templates
<!-- SECTION:NOTES:END -->
