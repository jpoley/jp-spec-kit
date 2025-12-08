---
id: task-289
title: Memory Bank Integration for Repo Facts
status: Done
assignee: []
created_date: '2025-12-04 16:12'
updated_date: '2025-12-04 22:45'
labels:
  - constitution-cleanup
dependencies:
  - task-244
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Store detected repo facts in memory/repo-facts.md for LLM context across all commands
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 /speckit:constitution writes findings to memory/repo-facts.md
- [x] #2 Format: YAML frontmatter + markdown sections
- [x] #3 Facts include: languages, frameworks, linting tools, CI/CD, test setup, security tools
- [x] #4 LLM agents can reference repo-facts.md for context in other commands
- [x] #5 specify init and specify upgrade update repo-facts.md
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Already implemented - `/speckit:constitution` writes to `memory/repo-facts.md`. Branch merged to main.
<!-- SECTION:NOTES:END -->
