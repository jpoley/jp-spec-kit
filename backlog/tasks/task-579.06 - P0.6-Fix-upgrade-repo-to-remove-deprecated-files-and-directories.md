---
id: task-579.06
title: 'P0.6: Fix upgrade-repo to remove deprecated files and directories'
status: In Progress
assignee: []
created_date: '2026-01-06 17:20'
updated_date: '2026-01-06 18:49'
labels:
  - phase-0
  - upgrade-repo
  - cleanup
  - release-blocker
dependencies: []
parent_task_id: task-579
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The upgrade_repo command does NOT clean up deprecated files/directories in target repos.

Items that should be removed during upgrade:
- .specify/ directory (legacy, replaced by .flowspec/)
- _DEPRECATED_*.md command files
- Other deprecated artifacts

Changes needed:
1. Add cleanup step to upgrade_repo
2. Detect and offer to remove .specify/ directory
3. Remove _DEPRECATED_*.md files from .claude/commands/
4. Report what was cleaned up
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 upgrade_repo removes .specify/ directory if present
- [ ] #2 upgrade_repo removes _DEPRECATED_*.md files
- [ ] #3 Cleanup is reported to user
- [ ] #4 Backup created before removing files
- [ ] #5 Test: running upgrade-repo cleans up deprecated artifacts
<!-- AC:END -->
