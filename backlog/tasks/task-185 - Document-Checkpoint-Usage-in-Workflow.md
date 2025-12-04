---
id: task-185
title: Document Checkpoint Usage in Workflow
status: Done
assignee: []
created_date: '2025-12-01 05:04'
updated_date: '2025-12-04 01:25'
labels:
  - claude-code
  - documentation
  - quick-win
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add checkpoint usage documentation to CLAUDE.md and relevant slash commands. Checkpoints provide safety for experimental changes without Git overhead.

Cross-reference: See docs/prd/claude-capabilities-review.md Section 2.10 for checkpoint assessment.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Checkpoint usage section added to CLAUDE.md

- [x] #2 Best practices documented (when to use, Esc Esc shortcut, /rewind command)
- [x] #3 /jpspec:implement command includes checkpoint reminder for risky changes
- [x] #4 Examples provided for refactoring and experimental features
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Checkpoint documentation complete in memory/claude-checkpoints.md

Documents:
- How checkpoints work (automatic creation, instant rewind)
- When to use checkpoints (experimental refactoring, multi-file changes)
- Quick reference (Esc Esc, /rewind, restore options)
- Best practices (mental checkpoints, checkpoint + git)
- Example workflows (experimental refactoring, proof of concept)
- Integration with SDD workflow (/jpspec:implement reminder)

Included via @import in CLAUDE.md
Checkpoint reminder added to templates/commands/jpspec/implement.md
<!-- SECTION:NOTES:END -->
