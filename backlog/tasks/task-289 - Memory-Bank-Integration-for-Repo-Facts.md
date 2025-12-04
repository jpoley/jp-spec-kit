---
id: task-289
title: Memory Bank Integration for Repo Facts
status: In Progress
assignee:
  - '@galway'
created_date: '2025-12-04 16:12'
updated_date: '2025-12-04 17:22'
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
- [ ] #1 /speckit:constitution writes findings to memory/repo-facts.md
- [ ] #2 Format: YAML frontmatter + markdown sections
- [ ] #3 Facts include: languages, frameworks, linting tools, CI/CD, test setup, security tools
- [ ] #4 LLM agents can reference repo-facts.md for context in other commands
- [ ] #5 specify init and specify upgrade update repo-facts.md
<!-- AC:END -->
