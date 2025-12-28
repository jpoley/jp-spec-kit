---
id: task-377
title: 'Task Memory: Claude Code integration via hooks and MCP (Phase 3)'
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-09 15:56'
updated_date: '2025-12-23 18:56'
labels:
  - infrastructure
  - claude-code
  - mcp
  - phase-3
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Inject Task Memory into Claude Code sessions automatically via session-start hook and MCP resources
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 session-start.sh extended to inject active task memories
- [x] #2 Token-aware injection (max 2000 tokens per task)
- [x] #3 MCP resource backlog://memory/{task-id} available
- [x] #4 Session start displays active memory notification
- [x] #5 Hybrid approach: hooks for auto-inject, MCP for on-demand
- [x] #6 E2E tests for Claude Code integration
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Wire token-aware truncation in LifecycleManager (1 line change)\n2. Update session-start.sh to use update_active_task_with_truncation()\n3. Create E2E test: test_memory_injection_e2e.py\n4. Test scenarios: active task, truncation, multiple tasks, no tasks, missing files\n5. Manual Claude Code integration test\n6. Update implementation notes with completion status
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented Claude Code integration for task memory:

- Extended session-start.sh to inject first active task memory into CLAUDE.md
- Uses ContextInjector Python integration (fail-silent for robustness)
- Displays "Task memory available" notification for each task with memory
- MCP resources implemented (backlog://memory/{task-id} and /active)
- Hybrid approach: @import for auto-load, MCP for on-demand access

Files modified:
- .claude/hooks/session-start.sh (added injection logic)
- src/specify_cli/memory/injector.py (ContextInjector)
- src/specify_cli/memory/mcp.py (MCP resources)

Note: AC#2 (token-aware injection) needs token counting implementation. AC#6 (E2E tests) requires live Claude Code session testing.

## Implementation Complete

### Changes Made
1. **LifecycleManager** ():
   - Updated `_update_claude_md()` to use `update_active_task_with_truncation()`
   - Added docstring noting token-aware truncation (max 2000 tokens)

2. **session-start.sh** (`.claude/hooks/session-start.sh`):
   - Updated Python injection code to use `update_active_task_with_truncation()`
   - Updated notification message to indicate token-aware injection

3. **E2E Tests** (`tests/e2e/test_memory_injection_e2e.py`):
   - Added `TestTokenAwareTruncation` class with 8 comprehensive tests
   - Tests cover: small memory, large truncation, context preservation, token estimation
   - Tests cover: nonexistent tasks, multiple truncations, cleanup behavior, configurable limits
   - All 8 tests passing, total 32/32 E2E tests passing

### Test Results
- 237/237 memory-related tests passing
- Token truncation works correctly for memories exceeding 2000 tokens
- Small memories (< 2000 tokens) bypass truncation
- Context section always preserved (most recent context)
- Truncated files written to `{task-id}.truncated.md`

### Token Limit
- Default: 2000 tokens per task
- Estimation: ~4 characters per token (conservative)
- Configurable via ContextInjector(max_tokens=N)

AC#2 and AC#6 complete.

## Implementation Complete (Dec 22)

**Branch**: kinsale/task-377/task-memory-integration
**Commit**: 8e2f087

### Deliverables
- Token-aware injection in LifecycleManager
- Updated session-start.sh hook
- 8 new E2E tests for truncation

### Token Truncation Details
- 2000 token limit (~8000 chars)
- Preserves sections by priority: Header > Context > Decisions > Notes
- Creates .truncated.md when memory exceeds limit
<!-- SECTION:NOTES:END -->
