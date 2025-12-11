---
id: task-456
title: End-to-end integration testing and validation (flowspec rename)
status: To Do
assignee: []
created_date: '2025-12-11 01:36'
labels:
  - testing
  - qa
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Comprehensive E2E testing of renamed commands across all workflows. Final validation before merge. **Depends on: task-453 (test files), task-454 (documentation)**
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All /flow: commands execute successfully
- [ ] #2 Workflow state transitions work correctly (Assess → Specify → Plan → Implement → Validate → Deploy)
- [ ] #3 Backlog integration works (task creation, state updates)
- [ ] #4 MCP server integration works (tessl mcp start)
- [ ] #5 No references to 'flowspec' in active code (except historical docs)
- [ ] #6 Linting passes (ruff check . --fix)
- [ ] #7 All tests pass (pytest tests/ -v)
- [ ] #8 Coverage maintained (≥85%)
- [ ] #9 CLI help text shows correct command names
- [ ] #10 Deprecation warnings work (Phase 1)
<!-- AC:END -->
