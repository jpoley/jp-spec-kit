---
id: task-453
title: Rename test files and update test content (flowspec → flowspec)
status: To Do
assignee: []
created_date: '2025-12-11 01:36'
labels:
  - testing
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rename 14 test files from test_flowspec_* to test_flowspec_* and update all test assertions, imports, and fixtures. **Depends on: task-449 (Python source code)**
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All 14 test files renamed (test_flowspec_* → test_flowspec_*)
- [ ] #2 Test imports updated (no broken imports)
- [ ] #3 Test fixtures updated (flowspec_config instead of flowspec_config)
- [ ] #4 Test assertions updated (command names, config file paths)
- [ ] #5 All tests pass (100% success rate)
- [ ] #6 Test coverage ≥ baseline (85%)
- [ ] #7 No pytest warnings about renamed files
<!-- AC:END -->
