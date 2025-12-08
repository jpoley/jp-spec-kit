---
id: task-115
title: End-to-end integration tests for jpspec + backlog.md
status: Done
assignee: []
created_date: '2025-11-28 16:56'
updated_date: '2025-12-04 01:25'
labels:
  - jpspec
  - backlog-integration
  - testing
  - e2e
  - P1
dependencies:
  - task-109
  - task-110
  - task-111
  - task-112
  - task-113
  - task-114
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create comprehensive end-to-end tests that verify the complete jpspec workflow uses backlog.md correctly from specification through deployment.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Test scenario: Full feature lifecycle (specify → plan → implement → validate → operate)
- [x] #2 Test verifies tasks created at specify phase exist in backlog
- [x] #3 Test verifies planning adds architecture/infra tasks to backlog
- [x] #4 Test verifies implementation phase picks up and completes tasks
- [x] #5 Test verifies validation phase checks task completion status
- [x] #6 Test verifies no tasks remain in To Do after full workflow (all Done or blocked)
- [x] #7 Test can run in CI (uses temporary backlog directory)
- [x] #8 Test documents expected backlog CLI call sequence
- [x] #9 All e2e tests pass: pytest tests/test_jpspec_e2e.py
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
E2E tests implemented in tests/test_jpspec_e2e.py

All 13 tests pass covering:
- Full feature lifecycle (assess → specify → plan → implement → validate → operate)
- Task creation at specify phase
- Architecture task additions at plan phase
- Implementation phase task pickup
- Validation phase completion checks
- All tasks Done after workflow
- CI compatible (uses tmp_path fixtures)
- Documented CLI call sequence in test docstrings
<!-- SECTION:NOTES:END -->
