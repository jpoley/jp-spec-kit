---
id: task-503
title: 'claude-improves-again: Add loop metadata to flow commands'
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-14 03:07'
updated_date: '2025-12-28 22:15'
labels:
  - context-engineering
  - commands
  - claude-improves-again
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Annotate each .claude/commands/flow/ command file with loop metadata (inner/outer) to enable routing to appropriate agents/models and applying different safety rules per loop type.

Source: docs/research/archon-inspired.md Task 16
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Each flow command has loop: Inner or loop: Outer metadata
- [x] #2 /flow:specify marked as outer loop
- [x] #3 /flow:implement marked as inner loop
- [x] #4 /flow:validate documents which loop it spans
- [x] #5 Documentation explains loop routing implications
<!-- AC:END -->
