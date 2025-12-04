---
id: task-264
title: Migrate jpspec commands to templates
status: To Do
assignee: []
created_date: '2025-12-03 13:55'
labels:
  - infrastructure
  - migration
  - dogfood
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move enhanced jpspec commands from .claude/commands/jpspec/ to templates/commands/jpspec/ to eliminate content drift and establish single source of truth.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create templates/commands/jpspec/ directory
- [ ] #2 Copy all jpspec commands to templates (research, implement, validate, specify, plan, assess, operate)
- [ ] #3 Include _backlog-instructions.md in templates
- [ ] #4 Update specify dogfood to create jpspec symlinks
- [ ] #5 Verify symlinks work correctly
- [ ] #6 Remove old jpspec files from .claude/commands/
- [ ] #7 Update tests to verify jpspec template coverage
<!-- AC:END -->
