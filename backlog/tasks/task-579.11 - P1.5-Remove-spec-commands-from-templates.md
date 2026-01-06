---
id: task-579.11
title: 'P1.5: Remove /spec:* commands from templates'
status: To Do
assignee: []
created_date: '2026-01-06 17:20'
updated_date: '2026-01-06 18:52'
labels:
  - phase-1
  - cleanup
  - commands
  - release-blocker
dependencies: []
parent_task_id: task-579
priority: high
ordinal: 84000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove /spec:* namespace commands from templates per user requirement: "NOT having specify commands, only having specific flow commands"

Files to remove from templates/commands/spec/:
- analyze.md
- checklist.md
- clarify.md
- configure.md
- constitution.md
- implement.md
- init.md
- plan.md
- specify.md
- tasks.md

Decision: Remove entirely from templates (deployed to projects). Flowspec internal .claude/commands/spec/ can remain for flowspec development if needed.

Also update:
- .claude/commands/flow/init.md (remove /spec:* references)
- .claude/commands/flow/reset.md (remove /spec:* references)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 templates/commands/spec/ directory deleted or archived
- [ ] #2 flowspec init does NOT create /spec:* commands in target repos
- [ ] #3 flow/init.md and flow/reset.md updated to remove /spec:* references
- [ ] #4 Test: new projects have no /spec:* commands
<!-- AC:END -->
