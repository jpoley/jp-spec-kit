---
id: task-499
title: 'claude-improves-again: Add /flow:map-codebase command'
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-14 03:06'
updated_date: '2025-12-28 20:27'
labels:
  - context-engineering
  - commands
  - claude-improves-again
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a helper command that generates bounded directory tree listings for specified code paths. The output can be embedded in PRPs or saved as feature maps.

Source: docs/research/archon-inspired.md Task 12
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Command file created at .claude/commands/flow/map-codebase.md
- [ ] #2 Accepts one or more paths of interest as arguments
- [ ] #3 Runs bounded directory tree listing (limited depth)
- [ ] #4 Can write to PRP CODEBASE SNAPSHOT section
- [ ] #5 Can write to docs/feature-maps/<task-id>.md as standalone
<!-- AC:END -->
