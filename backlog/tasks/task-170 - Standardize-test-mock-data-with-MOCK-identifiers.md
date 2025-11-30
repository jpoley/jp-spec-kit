---
id: task-170
title: Standardize test mock data with MOCK identifiers
status: In Progress
assignee:
  - '@claude'
created_date: '2025-11-30 19:20'
updated_date: '2025-11-30 19:23'
labels:
  - test
  - quality
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
All test fixtures must clearly identify mock data to prevent confusion with real backlog tasks. Prevents test data from leaking into real backlog across branches.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 conftest.py fixtures have MOCK in descriptions
- [x] #2 Task IDs use T001 format for parser regex compatibility
- [x] #3 Integration tests use MOCK- prefixed IDs (MOCK-SIMPLE, etc.)
- [x] #4 All tests pass (907+)
- [x] #5 Constitution rule added: no direct commits to main
<!-- AC:END -->
