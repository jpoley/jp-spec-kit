---
id: task-489
title: 'claude-improves-again: Add /flow:intake command'
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
Create a new Claude command that turns INITIAL docs into backlog tasks and task memory files. This command parses INITIAL documents and creates structured backlog entries with populated context.

Source: docs/research/archon-inspired.md Task 2
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Command file created at .claude/commands/flow/intake.md
- [x] #2 Command accepts path to INITIAL doc (defaults to docs/features/<slug>-initial.md)
- [x] #3 Parses FEATURE section to create backlog task title/description
- [x] #4 Creates task memory file at backlog/memory/<task-id>.md
- [x] #5 Populates memory with What/Why, Constraints, Examples, Docs, Gotchas
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Already implemented - command exists at .claude/commands/flow/intake.md with full INITIAL parsing and backlog integration.
<!-- SECTION:NOTES:END -->
