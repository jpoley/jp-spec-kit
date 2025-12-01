---
id: task-135
title: 'Implement /jpspec:prune-branch slash command'
status: Done
assignee:
  - '@claude'
created_date: '2025-11-28 17:25'
updated_date: '2025-11-28 17:26'
labels:
  - feature
  - git
  - developer-experience
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a slash command that safely prunes local branches that have been merged and deleted on remote. The command should fetch from remote, identify stale branches, and provide a safe dry-run preview before deletion.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 #1 Command fetches from remote with --prune flag to sync remote tracking info
- [x] #2 #2 Command identifies local branches whose upstream tracking branch is 'gone'
- [x] #3 #3 Command identifies local branches fully merged into main/master
- [x] #4 #4 By default (no args), shows dry-run preview of branches to be deleted without deleting
- [x] #5 #5 With --force or -f argument, actually deletes the identified branches
- [x] #6 #6 Never deletes the current branch - errors with helpful message if current branch would be pruned
- [x] #7 #7 Never deletes protected branches (main, master, develop)
- [x] #8 #8 Outputs clear summary showing: branches deleted, branches skipped with reasons
- [x] #9 #9 Handles edge cases gracefully: no branches to prune, not in git repo, no remote configured
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create slash command file at .claude/commands/jpspec/prune-branch.md
2. Implement git fetch --prune logic
3. Implement detection of gone/merged branches
4. Implement dry-run vs force mode logic
5. Add safety checks for protected branches
6. Add clear output formatting
7. Test with current repo state
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented /jpspec:prune-branch slash command that:

- Fetches from all remotes with --prune to sync tracking info
- Identifies branches with upstream "gone" status
- Identifies branches fully merged into main/master
- Provides safe dry-run preview by default
- Supports --force/-f flag for actual deletion
- Protects main, master, develop, and current branch
- Includes clear output formatting with reasons
- Handles edge cases (not in git repo, no remote, no branches to prune)

Tested git commands against current repo - found stale branch jpspec-backlog-integration-tasks-v2 that would be correctly identified for pruning.
<!-- SECTION:NOTES:END -->
