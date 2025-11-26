---
id: task-72
title: Update documentation for backlog flush feature
status: Done
assignee:
  - '@claude'
created_date: '2025-11-26 16:46'
updated_date: '2025-11-26 17:02'
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
- [x] #1 CLAUDE.md contains 'Backlog Flush' section with usage examples for manual and automated modes
- [x] #2 Documents commit message trigger keyword 'flush-backlog' with case-sensitivity notes
- [x] #3 Explains all CLI flags (--dry-run, --no-summary, --auto-commit, --help) with examples
- [x] #4 Provides example flush summary output showing expected format
- [x] #5 Includes troubleshooting section for common errors (CLI not installed, no tasks, permission issues)
- [x] #6 Documents relationship with backlog.md CLI built-in 'backlog cleanup' command
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added comprehensive "Backlog Flush" section to CLAUDE.md covering:

- Manual execution with all CLI flags (--dry-run, --no-summary, --auto-commit, --help)
- Automated GitHub Actions integration via commit message trigger (flush-backlog, case-insensitive)
- Flush summary format with example showing timestamped output structure
- Exit codes table explaining all return values (0, 1, 2, 3)
- Troubleshooting section for common errors (CLI not installed, no backlog dir, no tasks, permissions)
- Comparison table between flush-backlog.sh and backlog cleanup command

Section placed after "Backlog.md Integration" section for logical flow. All acceptance criteria satisfied with clear examples and comprehensive documentation.
<!-- SECTION:NOTES:END -->
