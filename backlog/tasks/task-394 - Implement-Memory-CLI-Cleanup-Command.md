---
id: task-394
title: Implement Memory CLI - Cleanup Command
status: Done
assignee:
  - '@adare'
created_date: '2025-12-09 15:58'
updated_date: '2025-12-15 02:18'
labels:
  - backend
  - task-memory
  - cli
  - cleanup
dependencies:
  - task-387
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create `backlog memory cleanup` command to manually trigger archival and deletion of old memories
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement cleanup subcommand with --archive-older-than and --delete-archived-older-than options
- [x] #2 Support time units (d=days, w=weeks, m=months)
- [x] #3 Add --dry-run flag to preview cleanup operations
- [x] #4 Display summary of files affected before/after
- [x] #5 Add interactive confirmation for destructive operations
- [x] #6 Test cleanup with various time ranges
- [x] #7 Add CLI tests for cleanup command
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented cleanup command with:
- --archive-older-than option (archive active memories by age)
- --delete-older-than option (delete archived memories by age)
- --dry-run/--execute modes (default: dry-run)
- Interactive confirmation for destructive operations
- Summary display before/after cleanup
- Age calculation in days
- Comprehensive test coverage

All acceptance criteria met.
<!-- SECTION:NOTES:END -->
