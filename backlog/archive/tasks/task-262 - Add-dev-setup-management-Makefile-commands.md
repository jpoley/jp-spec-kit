---
id: task-262
title: Add dev-setup management Makefile commands
status: Done
assignee: []
created_date: '2025-12-03 13:54'
updated_date: '2025-12-04 01:34'
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
- [x] #1 Makefile created with dogfood targets
- [x] #2 make dogfood-validate: runs validation checks
- [x] #3 make dogfood-fix: recreates all symlinks
- [x] #4 make dogfood-status: shows current state
- [x] #5 make test-dogfood: runs dogfood test suite
- [x] #6 All targets work correctly and provide clear output
- [x] #7 help target documents dogfood commands
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Makefile targets implemented with dev- prefix (instead of dogfood- for discretion):
- make dev-validate
- make dev-fix
- make dev-status
- make test-dev

All targets work correctly and documented in Makefile help.
<!-- SECTION:NOTES:END -->
