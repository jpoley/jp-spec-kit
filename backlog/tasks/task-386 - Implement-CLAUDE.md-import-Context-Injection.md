---
id: task-386
title: Implement CLAUDE.md @import Context Injection
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-09 15:57'
updated_date: '2025-12-11 08:21'
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
- [x] #2 Implement dynamic @import update in LifecycleManager
- [x] #3 Test @import with Claude Code (verify memory loads automatically)
- [x] #4 Handle no active task scenario gracefully
- [x] #5 Add section replacement logic with regex
- [x] #6 Test with multiple rapid state transitions
- [x] #7 Document @import mechanism in docs/reference/
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Integrated ContextInjector with LifecycleManager for @import directive management:

**Implementation Changes:**
- Refactored LifecycleManager to use ContextInjector for CLAUDE.md updates
- Added ContextInjector instance to LifecycleManager.__init__()
- Replaced manual @import management with delegation to ContextInjector
- Maintained backward compatibility with update_active_task_import() public API

**Testing:**
- All 120 lifecycle/injection/E2E tests pass
- Updated test expectations to use ../memory/task-XXX.md path format
- Verified integration with existing Claude Code E2E tests

**Documentation:**
- Created docs/reference/task-memory-import.md
- Documented @import mechanism, architecture, API, edge cases, and troubleshooting
- Added examples for both ContextInjector and LifecycleManager usage

**Files Changed:**
- src/specify_cli/memory/lifecycle.py (integrated ContextInjector)
- tests/test_memory_lifecycle.py (updated path format)
- tests/e2e/test_memory_lifecycle_e2e.py (updated path format)
- docs/reference/task-memory-import.md (new documentation)
<!-- SECTION:NOTES:END -->
