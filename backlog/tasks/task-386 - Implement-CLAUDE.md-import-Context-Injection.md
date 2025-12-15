---
id: task-386
title: Implement CLAUDE.md @import Context Injection
status: In Progress
assignee:
  - '@adare'
created_date: '2025-12-09 15:57'
updated_date: '2025-12-15 02:17'
labels:
  - backend
  - task-memory
  - claude-code
  - integration
dependencies:
  - task-377
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update backlog/CLAUDE.md to dynamically include active task memory via @import directive for Claude Code
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add Active Task Context section to backlog/CLAUDE.md
- [ ] #2 Implement dynamic @import update in LifecycleManager
- [ ] #3 Test @import with Claude Code (verify memory loads automatically)
- [x] #4 Handle no active task scenario gracefully
- [x] #5 Add section replacement logic with regex
- [x] #6 Test with multiple rapid state transitions
- [ ] #7 Document @import mechanism in docs/reference/
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented ContextInjector with full @import management:

- Created src/specify_cli/memory/injector.py with ContextInjector class
- Supports update_active_task(), clear_active_task(), get_active_task_id()
- Handles Active Task Context section in CLAUDE.md with regex replacement
- Gracefully handles missing CLAUDE.md, no active task, and rapid transitions
- 12/12 tests pass covering all scenarios
- Session-start hook updated to inject first active task memory

Note: AC#2 refers to LifecycleManager which doesn't exist yet - integration will happen when task lifecycle management is implemented. AC#3 and AC#7 are manual/documentation tasks to complete separately.
<!-- SECTION:NOTES:END -->
