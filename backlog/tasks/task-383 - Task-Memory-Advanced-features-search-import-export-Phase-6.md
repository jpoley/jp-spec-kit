---
id: task-383
title: 'Task Memory: Advanced features - search, import, export (Phase 6)'
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-09 15:57'
updated_date: '2025-12-11 08:52'
labels:
  - infrastructure
  - cli
  - feature
  - phase-6
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Power user features for Task Memory: search across memories, import from PRs, export to files, templates
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 backlog memory search finds content across all memories
- [x] #2 backlog memory import --from-pr imports PR description
- [x] #3 backlog memory export outputs to file
- [x] #4 Memory templates for different task types (feature, bugfix, research)
- [x] #5 Comprehensive user documentation
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Steel Thread Verified

Task Memory lifecycle is now working end-to-end:
1. Hook fixed - uses infer_old_status() to determine transitions
2. Memory created automatically on In Progress
3. @import directive added to CLAUDE.md
4. Memory archived on Done
5. Template simplified (no boilerplate comments)

AC#1 (search) was already implemented.
<!-- SECTION:NOTES:END -->
