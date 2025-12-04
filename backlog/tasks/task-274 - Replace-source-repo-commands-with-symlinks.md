---
id: task-274
title: Replace source repo commands with symlinks
status: Done
assignee:
  - '@cli-engineer'
created_date: '2025-12-03 14:01'
updated_date: '2025-12-03 14:17'
labels:
  - architecture
  - migration
  - implementation
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Delete direct files in .claude/commands/ and replace with symlinks created by dogfood
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Backup current .claude/commands/jpspec/ files (git commit before deletion)
- [ ] #2 Delete all .claude/commands/jpspec/*.md files
- [ ] #3 Run specify dogfood --force to create symlinks
- [ ] #4 Verify all .claude/commands/**/*.md are symlinks (none are regular files)
- [ ] #5 Test Claude Code reads commands via symlinks successfully
- [ ] #6 Commit symlink replacement to git
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Replaced all command files with symlinks to templates subdirectories. jpspec: 8 commands, speckit: 8 commands
<!-- SECTION:NOTES:END -->
