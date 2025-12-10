---
id: task-422
title: 'Phase 5: Migrate Test Files'
status: To Do
assignee: []
created_date: '2025-12-10 02:59'
labels:
  - migration
  - testing
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rename 10 test files from test_specflow_*.py to test_specflow_*.py and update all test content: assertions, fixtures, docstrings, imports. DEPENDS ON: task-421 agent migration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All 10 test files renamed: test_specflow_*.py → test_specflow_*.py
- [ ] #2 Test imports updated: specflow_workflow → specflow_workflow
- [ ] #3 Command strings updated: /specflow: → /specflow:
- [ ] #4 Assertion patterns updated in all tests
- [ ] #5 Test discovery verified: pytest --collect-only shows all tests
- [ ] #6 Full test suite passes: pytest tests/ -v
<!-- AC:END -->
