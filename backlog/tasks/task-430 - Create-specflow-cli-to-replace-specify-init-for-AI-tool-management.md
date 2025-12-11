---
id: task-430
title: Create flowspec-cli to replace specify init for AI tool management
status: To Do
assignee: []
created_date: '2025-12-10 20:52'
labels:
  - cli
  - flowspec
  - enhancement
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a new `flowspec-cli` command that:
1. Replaces `specify init` for bootstrapping projects
2. Handles adding AI tools to existing projects (re-ask which tools)
3. Manages both AI tool setup AND constitution initialization
4. Removes the need for users to know about `specify init`

The goal is a single entry point:
- `flowspec init .` - Initialize current directory with AI tools + constitution
- `flowspec init my-project` - Create new project
- `flowspec init --add-ai copilot` - Add AI tool to existing project

This task comes AFTER task-428 (critical fix) and task-429 (ASCII logo).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 flowspec-cli init creates project with AI tool support
- [ ] #2 flowspec-cli init --add-ai adds AI tool to existing project
- [ ] #3 flowspec-cli init handles constitution setup
- [ ] #4 specify init still works but flowspec-cli is primary
- [ ] #5 Documentation updated to recommend flowspec-cli
<!-- AC:END -->
