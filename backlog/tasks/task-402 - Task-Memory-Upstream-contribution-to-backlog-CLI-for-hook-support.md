---
id: task-402
title: 'Task Memory: Upstream contribution to backlog CLI for hook support'
status: To Do
assignee:
  - '@adare'
created_date: '2025-12-09 15:58'
updated_date: '2025-12-15 06:08'
labels:
  - upstream
  - contribution
  - infrastructure
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Contribute hook system to backlog.md CLI: emit events on task create/update/archive for extensibility
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Fork backlog.md repository
- [ ] #2 Implement hook system (post-task-create, post-task-update, post-task-archive)
- [ ] #3 Add --hook-dir config option
- [ ] #4 Hook execution with timeout (5s default)
- [ ] #5 Tests for hook system
- [ ] #6 Documentation for hook API
- [ ] #7 Submit PR to upstream backlog.md project
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Status Update (2025-12-15)

**Priority lowered**: Duplicate of task-204.03.

The Python shim (`src/specify_cli/backlog/shim.py`) and `bk` wrapper provide all needed event emission without requiring upstream changes to backlog.md.

Upstream contribution is optional enhancement, not required for Task Memory or other features.

**Consider consolidating with task-204.03** - same goal, different contexts.
<!-- SECTION:NOTES:END -->
