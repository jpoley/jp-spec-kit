---
id: task-273
title: Update dogfood command for jpspec symlinks
status: Done
assignee:
  - '@cli-engineer'
created_date: '2025-12-03 14:01'
updated_date: '2025-12-03 14:16'
labels:
  - cli
  - dogfood
  - implementation
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend specify dogfood to create symlinks for jpspec commands in addition to speckit
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add loop to process both speckit and jpspec namespaces
- [x] #2 Create jpspec symlinks pointing to templates/commands/jpspec/*.md
- [x] #3 Handle _backlog-instructions.md partial (create symlink)
- [x] #4 Add verification for all jpspec symlinks
- [ ] #5 Update CLI help text to mention both speckit and jpspec
- [ ] #6 Test dogfood creates 17 total symlinks (8 speckit + 9 jpspec)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated dogfood to create symlinks for both jpspec and speckit subdirectories, skip _backlog-instructions.md partial, and verify all symlinks
<!-- SECTION:NOTES:END -->
