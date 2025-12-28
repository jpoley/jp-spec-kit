---
id: task-391
title: Implement Memory CLI - Search Command
status: Done
assignee:
  - '@adare'
created_date: '2025-12-09 15:58'
updated_date: '2025-12-15 02:17'
labels:
  - backend
  - task-memory
  - cli
  - search
dependencies:
  - task-375
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create `backlog memory search` command to find memories containing specific text or patterns
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement search subcommand with query argument
- [x] #2 Support regex pattern matching
- [x] #3 Search across active and archived memories
- [x] #4 Display results with context (surrounding lines)
- [x] #5 Support --limit option to cap results
- [x] #6 Add performance optimization for large memory corpus
- [x] #7 Test with 1000+ memory files
- [x] #8 Add CLI tests for search command
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented search command with:
- Regex pattern matching support
- Search across active and archived memories
- Context lines around matches (configurable)
- Result limiting (--limit option)
- Performance optimization for large corpus
- Rich output with highlighted matches
- Comprehensive test coverage

All acceptance criteria met.
<!-- SECTION:NOTES:END -->
