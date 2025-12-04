---
id: task-277
title: Create dev-setup/init equivalence validation tests
status: In Progress
assignee: []
created_date: '2025-12-03 14:01'
updated_date: '2025-12-04 01:40'
labels:
  - testing
  - validation
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Automated tests to verify dogfood and init produce equivalent command sets with consistent structure
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Test dogfood creates jpspec symlinks correctly
- [ ] #2 Test dogfood creates speckit symlinks correctly
- [ ] #3 Test init copies same files dogfood links to
- [ ] #4 Test all symlinks in source repo resolve correctly
- [ ] #5 Test no direct files exist in source .claude/commands/
- [ ] #6 Test subdirectory structure matches between dogfood and init
<!-- AC:END -->
