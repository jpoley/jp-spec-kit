---
id: task-287
title: Constitution Version Tracking
status: Done
assignee: []
created_date: '2025-12-04 16:10'
updated_date: '2025-12-04 22:45'
labels:
  - constitution-cleanup
dependencies:
  - task-244
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add version field to constitution and track changes over time for upgrades
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Constitution includes Version, Ratified Date, Last Amended fields
- [x] #2 specify constitution version shows current version
- [x] #3 specify upgrade detects outdated constitutions
- [x] #4 Upgrade flow prompts user: Constitution X.Y.Z available, you have A.B.C. Upgrade?
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Already implemented - `specify constitution version` command exists. Branch merged to main.
<!-- SECTION:NOTES:END -->
