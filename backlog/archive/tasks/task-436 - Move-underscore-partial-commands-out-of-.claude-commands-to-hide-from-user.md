---
id: task-436
title: Move underscore partial commands out of .claude/commands to hide from user
status: Done
assignee:
  - '@adare'
created_date: '2025-12-11 01:03'
updated_date: '2025-12-29 12:03'
labels:
  - bug
  - ux
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Internal partial commands (`_workflow-state`, `_constitution-check`, `_backlog-instructions`) show as visible slash commands. Move them outside `.claude/commands/` so they can still be used via `{{INCLUDE:...}}` but won't appear to users.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Underscore commands moved out of .claude/commands/
- [x] #2 Commands still work via INCLUDE directive
- [x] #3 Users don't see _* commands in slash command list
<!-- AC:END -->
