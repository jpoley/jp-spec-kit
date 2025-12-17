---
id: task-549
title: 'Add /flow:freeze command for task suspension'
status: To Do
assignee: []
created_date: '2025-12-17 16:41'
updated_date: '2025-12-17 17:07'
labels:
  - rigor
  - freeze
  - command
  - new-feature
  - 'workflow:Planned'
dependencies:
  - task-541
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a new command to properly freeze work with context preservation. All Flowspec users must be able to pause work safely without losing context. This is mandatory per rigor rules.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create templates/commands/flow/freeze.md with freeze workflow
- [ ] #2 Update task memory with key facts on freeze (mandatory)
- [ ] #3 Validate code is in working state before freeze (tests must pass)
- [ ] #4 Push to remote with facts documented (mandatory)
- [ ] #5 Add symlink in .claude/commands/flow/freeze.md
- [ ] #6 Document freeze command in CLAUDE.md slash commands section
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create templates/commands/flow/freeze.md
2. Add task memory update requirement
3. Add working state validation (tests pass)
4. Add remote push with facts
5. Create symlink in .claude/commands/flow/
6. Update CLAUDE.md slash commands section
7. Test freeze/resume workflow
<!-- SECTION:PLAN:END -->
