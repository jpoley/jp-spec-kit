---
id: task-492
title: 'claude-improves-again: Add /flow:generate-prp command'
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-14 03:06'
updated_date: '2025-12-19 18:56'
labels:
  - context-engineering
  - commands
  - claude-improves-again
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a command that generates PRP (Product Requirements Prompt) files by collecting PRD, docs, examples, learnings, and codebase snapshots into a single context bundle.

Source: docs/research/archon-inspired.md Task 5
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Command file created at .claude/commands/flow/generate-prp.md
- [x] #2 Collects PRD from /flow:specify for the active task
- [x] #3 Gathers docs/specs, examples, and learnings relevant to the task
- [x] #4 Generates bounded directory tree of relevant code paths
- [x] #5 Writes filled PRP to docs/prp/<task-id>.md
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Already implemented - command exists at .claude/commands/flow/generate-prp.md with full context gathering and PRP generation.
<!-- SECTION:NOTES:END -->
