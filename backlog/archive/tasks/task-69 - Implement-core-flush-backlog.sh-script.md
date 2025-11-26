---
id: task-69
title: Implement core flush-backlog.sh script
status: Done
assignee: []
created_date: '2025-11-26 16:41'
updated_date: '2025-11-26 17:11'
labels:
  - backend
  - script
  - bash
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the main bash script that orchestrates Done task archival. The script queries tasks via backlog.md CLI, archives each Done task, and generates timestamped summary files. Must support dry-run mode, optional summary generation, and optional auto-commit.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Script accepts --dry-run, --no-summary, --auto-commit, and --help flags with correct behavior
- [x] #2 Validates backlog.md CLI is installed and exits with code 1 and clear error message if not
- [x] #3 Successfully queries Done tasks via 'backlog task list -s Done --plain' and parses task IDs
- [x] #4 Archives each Done task using 'backlog task archive <id>' with error handling for partial failures
- [x] #5 Dry-run mode displays tasks that would be archived without making any changes
- [x] #6 Exit codes follow specification: 0=success, 1=validation error, 2=no tasks, 3=partial failures
<!-- AC:END -->
