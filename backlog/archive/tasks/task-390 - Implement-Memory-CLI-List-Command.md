---
id: task-390
title: Implement Memory CLI - List Command
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
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create `backlog memory list` command to show active and archived task memories
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement list subcommand with --archived flag
- [x] #2 Display task IDs with memory file sizes
- [x] #3 Sort by last modified time (newest first)
- [x] #4 Add color coding (green=active, yellow=archived)
- [x] #5 Support --plain output for scripting
- [x] #6 Test with various directory states (empty, 1000+ files)
- [x] #7 Add CLI tests for list command
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented list command with:
- Active and archived memory listing
- Rich table display with colors (green=active, yellow=archived)
- File size formatting (B, KB, MB)
- Sort by modified time (newest first)
- --plain output for scripting
- Comprehensive test coverage

All acceptance criteria met.
<!-- SECTION:NOTES:END -->
