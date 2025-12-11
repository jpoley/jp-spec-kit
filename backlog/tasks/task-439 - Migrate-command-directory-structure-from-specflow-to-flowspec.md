---
id: task-439
title: Migrate command directory structure from flowspec to flowspec
status: To Do
assignee: []
created_date: '2025-12-11 01:32'
labels:
  - platform
  - symlinks
  - rename
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Migrate command directory structure and update symlinks:

Directory structure changes:
- .claude/commands/flowspec/ → .claude/commands/flowspec/
- templates/commands/flowspec/ → templates/commands/flowspec/

Symlink migration strategy:
1. Delete all symlinks in .claude/commands/flowspec/
2. Create new directory .claude/commands/flowspec/
3. Recreate symlinks pointing to templates/commands/flowspec/
4. Verify symlink integrity

Files affected (17 symlinks):
- assess.md, implement.md, init.md, operate.md
- plan.md, research.md, reset.md, specify.md, validate.md
- security_fix.md, security_report.md, security_triage.md
- security_web.md, security_workflow.md
- _backlog-instructions.md, _constitution-check.md, _workflow-state.md

Command template files (17 files in templates/commands/flowspec/):
- All .md files need directory rename only (content updated separately)
- Verify no absolute paths break after rename
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Directory templates/commands/flowspec/ exists with all command files
- [ ] #2 Directory .claude/commands/flowspec/ contains recreated symlinks
- [ ] #3 All symlinks resolve correctly to templates/commands/flowspec/
- [ ] #4 Old flowspec directories removed
- [ ] #5 dev-setup validation passes with new structure
- [ ] #6 No broken symlinks detected
<!-- AC:END -->
