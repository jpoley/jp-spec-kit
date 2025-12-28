---
id: task-392
title: Implement Memory CLI - Clear Command
status: Done
assignee:
  - '@adare'
created_date: '2025-12-09 15:58'
updated_date: '2025-12-15 02:17'
labels:
  - backend
  - task-memory
  - cli
dependencies:
  - task-375
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create `backlog memory clear` command to delete task memory with confirmation
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement clear subcommand with task_id argument
- [x] #2 Require --confirm flag for safety
- [x] #3 Prompt user for confirmation if flag missing
- [x] #4 Create backup before deletion (optional --no-backup flag)
- [x] #5 Support --force flag to skip all prompts
- [x] #6 Add CLI tests for clear command with mocks
- [x] #7 Document clear usage and safety in docs/guides/
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented clear command with:
- --confirm flag for safety
- Automatic backup creation before deletion
- --no-backup flag to skip backup
- Interactive confirmation prompts
- Backup stored in .specify/backups/
- Comprehensive test coverage

All acceptance criteria met.
<!-- SECTION:NOTES:END -->
