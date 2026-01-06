---
id: task-550
title: Add workflow status tracking to all commands
status: To Do
assignee: []
created_date: '2025-12-17 16:42'
updated_date: '2026-01-06 18:52'
labels:
  - rigor
  - workflow
  - tracking
  - 'workflow:Planned'
dependencies:
  - task-541
priority: medium
ordinal: 78000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ensure each workflow step emits clear 'next step' guidance and tracks current flow status. Flowspec users must always know where they are and what's next. This is mandatory per rigor rules.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add workflow status output at end of each /flow:* command
- [ ] #2 Track current phase in task labels (workflow:Phase) consistently
- [ ] #3 Emit next step suggestions based on current state in all commands
- [ ] #4 Update task memory with workflow progress on each phase transition
- [ ] #5 Agent must always track and report current flow status and what's next
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add workflow status output template to _rigor-rules.md
2. Update all /flow:* commands with status emission
3. Track current phase in task labels consistently
4. Add next step suggestions based on current state
5. Update task memory with workflow progress
6. Test end-to-end workflow tracking
<!-- SECTION:PLAN:END -->
