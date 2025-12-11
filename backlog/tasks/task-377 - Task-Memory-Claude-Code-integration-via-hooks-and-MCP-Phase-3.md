---
id: task-377
title: 'Task Memory: Claude Code integration via hooks and MCP (Phase 3)'
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-09 15:56'
updated_date: '2025-12-11 08:20'
labels:
  - infrastructure
  - claude-code
  - mcp
  - phase-3
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented token-aware injection and E2E tests:

**Token-Aware Injection (AC#2)**:
- Added `estimate_tokens()` method using character-based approximation (1 token ≈ 4 chars)
- Implemented `truncate_memory_content()` with smart truncation strategy:
  * Always preserves header and metadata
  * Keeps Context section (recent context)
  * Truncates Notes section first (oldest content)
  * Reserves space for truncation notice to stay within limit
- Added `update_active_task_with_truncation()` for safe injection with token limits
- Creates `.truncated.md` files when content exceeds 2000 tokens, preserving originals

**E2E Tests (AC#6)**:
- Created comprehensive test suite in `tests/e2e/test_memory_claude_code_e2e.py`
- 23 E2E tests covering:
  * Session-start hook execution (4 tests)
  * Token-aware injection (8 tests)
  * @import injection flow (4 tests)
  * Hybrid approach (hooks + MCP) (3 tests)
  * Edge cases (4 tests)
- Also added 10 new unit tests in `tests/test_memory_injector.py`

**Files Modified**:
- `src/specify_cli/memory/injector.py` - Token counting and truncation methods
- `tests/e2e/test_memory_claude_code_e2e.py` - New E2E test suite (23 tests)
- `tests/test_memory_injector.py` - New unit tests (10 tests)

**Test Results**:
- All 23 E2E tests pass
- All 22 unit tests pass (12 existing + 10 new)
- Full test suite: 3134 passed, 17 skipped
- No linting issues (ruff check passed)

**Implementation Details**:
- Token estimation uses conservative 4 chars/token ratio
- Truncation preserves structure intelligently (header > context > decisions > notes)
- Original memory files never modified (truncated versions stored separately)
- Fail-safe: if truncation logic fails, hard truncates with notice
<!-- SECTION:NOTES:END -->
