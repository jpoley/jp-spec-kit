---
id: task-579.02
title: 'P0.2: Remove ALL broken {{INCLUDE:}} directives from templates'
status: Done
assignee: []
created_date: '2026-01-06 17:19'
updated_date: '2026-01-06 19:10'
labels:
  - phase-0
  - cleanup
  - templates
  - release-blocker
dependencies: []
parent_task_id: task-579
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove non-functional {{INCLUDE:}} directives from all command templates. Per PR #1125, {{INCLUDE:}} syntax does NOT work in Claude command files - only @import works in CLAUDE.md files.

Affected files (28 total) include:
- templates/commands/flow/*.md (6 files with broken includes)
- templates/commands/arch/*.md (2 files)
- .claude/commands/flow/*.md (deployed versions)

The directives reference non-existent partials:
- .claude/partials/flow/_constitution-check.md
- .claude/partials/flow/_workflow-state.md
- .claude/partials/flow/_rigor-rules.md

Options:
1. Remove directives entirely
2. Inline content from flowspec partials into templates
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 grep -r '{{INCLUDE:' templates/ returns ZERO matches
- [x] #2 grep -r '{{INCLUDE:' .claude/commands/ returns ZERO matches
- [x] #3 All command files are functional without missing partial references
- [x] #4 Content inlined where necessary for command functionality
<!-- AC:END -->
