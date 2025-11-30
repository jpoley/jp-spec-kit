---
id: task-170
title: Standardize test mock data with MOCK identifiers
status: Done
assignee: []
created_date: '2025-11-30 19:17'
updated_date: '2025-11-30 19:17'
labels:
  - test
  - quality
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
All test fixtures must clearly identify mock data to prevent confusion with real backlog tasks. Task descriptions contain MOCK, integration tests use MOCK- prefixed IDs.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 conftest.py fixtures have MOCK in descriptions
- [x] #2 Task IDs use T001 format for parser compatibility
- [x] #3 Integration tests use MOCK- prefixed IDs
- [x] #4 All 907 tests pass
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed via commit 35f9915 on main (direct commit, no PR - urgent fix)
<!-- SECTION:NOTES:END -->
