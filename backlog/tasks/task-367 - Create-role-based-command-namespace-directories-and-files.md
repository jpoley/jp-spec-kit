---
id: task-367
title: Create role-based command namespace directories and files
status: To Do
assignee: []
created_date: '2025-12-09 15:47'
updated_date: '2025-12-09 15:47'
labels:
  - infrastructure
  - commands
  - phase-2
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the new command directory structure with role-based namespaces. DEPENDS ON: task-364 (schema), task-361 (init/configure). This creates the actual command files.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create directories: .claude/commands/{pm,arch,dev,sec,qa,ops}/
- [ ] #2 Create PM commands: assess.md, define.md, discover.md
- [ ] #3 Create Arch commands: design.md, decide.md, model.md
- [ ] #4 Create Dev commands: build.md, debug.md, refactor.md, cleanup.md
- [ ] #5 Create Sec commands: scan.md, triage.md, fix.md, audit.md, report.md
- [ ] #6 Create QA commands: test.md, verify.md, review.md
- [ ] #7 Create Ops commands: deploy.md, monitor.md, respond.md, scale.md
- [ ] #8 Update speckit commands: init.md, configure.md (renamed from reset)
- [ ] #9 Create backwards-compatible aliases in flowspec/ namespace
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
DEPENDS ON: task-364, task-361

1. Create namespace directories under .claude/commands/
2. Create PM commands (assess, define, discover) - migrate from flowspec:assess, flowspec:specify, flowspec:research
3. Create Arch commands (design, decide, model) - migrate from flowspec:plan
4. Create Dev commands (build, debug, refactor, cleanup) - migrate from flowspec:implement
5. Create Sec commands (scan, triage, fix, audit, report) - migrate from flowspec:security_*
6. Create QA commands (test, verify, review) - migrate from flowspec:validate
7. Create Ops commands (deploy, monitor, respond, scale) - migrate from flowspec:operate
8. Update speckit/ with init.md, configure.md
9. Create alias files in flowspec/ that redirect to new commands
10. Update templates/commands/ with same structure
<!-- SECTION:PLAN:END -->
