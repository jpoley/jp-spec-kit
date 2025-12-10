---
id: task-420
title: 'Phase 3: Recreate Local Command Symlinks'
status: To Do
assignee: []
created_date: '2025-12-10 02:59'
labels:
  - migration
  - symlinks
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Delete .claude/commands/specflow/ directory and recreate as .claude/commands/specflow/ with 18 symlinks pointing to new template locations. DEPENDS ON: task-419 template migration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Directory .claude/commands/specflow/ deleted
- [ ] #2 Directory .claude/commands/specflow/ created
- [ ] #3 All 18 symlinks recreated pointing to templates/commands/specflow/
- [ ] #4 Symlink validation passes: no broken symlinks
- [ ] #5 All symlinked files accessible via .claude/commands/specflow/
<!-- AC:END -->
