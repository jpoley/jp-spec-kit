---
id: task-260
title: Create dev-setup validation test suite
status: In Progress
assignee: []
created_date: '2025-12-03 13:54'
updated_date: '2025-12-04 01:40'
labels:
  - testing
  - infrastructure
  - dogfood
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Comprehensive pytest tests for dogfood/init equivalence. Validates single-source-of-truth architecture.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Test file created: tests/test_dogfood_validation.py
- [ ] #2 Test file created: tests/test_dogfood_init_equivalence.py
- [ ] #3 Tests verify .claude/commands contains only symlinks
- [ ] #4 Tests verify all symlinks resolve correctly
- [ ] #5 Tests verify dogfood-init command equivalence
- [ ] #6 Tests verify template coverage is complete
- [ ] #7 Tests pass with 100% success rate
<!-- AC:END -->
