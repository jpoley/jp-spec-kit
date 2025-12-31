---
id: task-471
title: 'claude-improves: Add CLAUDE.md scaffolding to flowspec init'
status: Done
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2025-12-31 22:05'
labels:
  - claude-improves
  - cli
  - specify-init
  - claude-md
  - phase-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enhance flowspec init to generate a project-specific CLAUDE.md file with essential sections (commands, environment, workflows) pre-populated based on detected tech stack.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 specify init creates root CLAUDE.md file
- [x] #2 CLAUDE.md includes project overview section
- [x] #3 Tech stack auto-detected from project files where possible
- [x] #4 Development commands section populated based on detected tooling
- [x] #5 @import statements for memory/*.md files included
- [x] #6 Template allows customization via prompts or flags
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Already implemented - CLAUDE.md generation with tech stack detection, @import statements, and --skip-claude-md flag was already in place.
<!-- SECTION:NOTES:END -->
