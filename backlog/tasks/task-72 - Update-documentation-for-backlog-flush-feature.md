---
id: task-72
title: Update documentation for backlog flush feature
status: To Do
assignee: []
created_date: '2025-11-26 16:46'
labels:
  - documentation
dependencies:
  - task-69
  - task-71
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update CLAUDE.md and create user documentation explaining the backlog flush feature. Document commit message trigger, manual CLI execution, example outputs, and troubleshooting common errors.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CLAUDE.md contains 'Backlog Flush' section with usage examples for manual and automated modes
- [ ] #2 Documents commit message trigger keyword 'flush-backlog' with case-sensitivity notes
- [ ] #3 Explains all CLI flags (--dry-run, --no-summary, --auto-commit, --help) with examples
- [ ] #4 Provides example flush summary output showing expected format
- [ ] #5 Includes troubleshooting section for common errors (CLI not installed, no tasks, permission issues)
- [ ] #6 Documents relationship with backlog.md CLI built-in 'backlog cleanup' command
<!-- AC:END -->
