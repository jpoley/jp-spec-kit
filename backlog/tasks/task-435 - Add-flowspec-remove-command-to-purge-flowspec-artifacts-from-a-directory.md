---
id: task-435
title: Add flowspec remove command to purge flowspec artifacts from a directory
status: To Do
assignee:
  - '@adare'
created_date: '2025-12-11 01:03'
updated_date: '2026-01-06 18:52'
labels:
  - feature
dependencies: []
priority: medium
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement a flowspec remove command that cleanly removes all flowspec-generated artifacts (.specify/, .claude/commands/, templates, etc.) from a project directory.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 specify remove command exists
- [ ] #2 Removes .specify/ directory
- [ ] #3 Removes .claude/commands/ directory
- [ ] #4 Preserves .github/workflows/
<!-- AC:END -->
