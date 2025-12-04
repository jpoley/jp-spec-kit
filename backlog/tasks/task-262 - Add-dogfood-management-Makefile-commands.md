---
id: task-262
title: Add dogfood management Makefile commands
status: To Do
assignee: []
created_date: '2025-12-03 13:54'
labels:
  - infrastructure
  - dx
  - dogfood
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Makefile targets for dogfood management. Provides consistent interface for validation, fixing, and status checking.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Makefile created with dogfood targets
- [ ] #2 make dogfood-validate: runs validation checks
- [ ] #3 make dogfood-fix: recreates all symlinks
- [ ] #4 make dogfood-status: shows current state
- [ ] #5 make test-dogfood: runs dogfood test suite
- [ ] #6 All targets work correctly and provide clear output
- [ ] #7 help target documents dogfood commands
<!-- AC:END -->
