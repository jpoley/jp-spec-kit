---
id: task-471
title: 'claude-improves: Add CLAUDE.md scaffolding to flowspec init'
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2025-12-22 21:54'
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
- [ ] #1 specify init creates root CLAUDE.md file
- [ ] #2 CLAUDE.md includes project overview section
- [ ] #3 Tech stack auto-detected from project files where possible
- [ ] #4 Development commands section populated based on detected tooling
- [ ] #5 @import statements for memory/*.md files included
- [ ] #6 Template allows customization via prompts or flags
<!-- AC:END -->
