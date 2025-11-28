---
id: task-115
title: End-to-end integration tests for jpspec + backlog.md
status: To Do
assignee: []
created_date: '2025-11-28 16:56'
updated_date: '2025-11-28 16:57'
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
- [ ] #1 Test scenario: Full feature lifecycle (specify → plan → implement → validate → operate)
- [ ] #2 Test verifies tasks created at specify phase exist in backlog
- [ ] #3 Test verifies planning adds architecture/infra tasks to backlog
- [ ] #4 Test verifies implementation phase picks up and completes tasks
- [ ] #5 Test verifies validation phase checks task completion status
- [ ] #6 Test verifies no tasks remain in To Do after full workflow (all Done or blocked)
- [ ] #7 Test can run in CI (uses temporary backlog directory)
- [ ] #8 Test documents expected backlog CLI call sequence
- [ ] #9 All e2e tests pass: pytest tests/test_jpspec_e2e.py
<!-- AC:END -->
