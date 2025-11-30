---
id: task-170
title: Standardize test mock data with MOCK identifiers
status: Done
assignee:
  - '@claude'
created_date: '2025-11-30 19:20'
updated_date: '2025-11-30 19:24'
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed via PR #108

Status: Pending CI verification

Changes:
- conftest.py: All fixture descriptions contain MOCK
- test_jpspec_backlog_integration.py: Uses MOCK- prefixed IDs
- constitution.md: Added No Direct Commits to Main rule
- CLAUDE.md: Added direct commit prohibition
<!-- SECTION:NOTES:END -->
