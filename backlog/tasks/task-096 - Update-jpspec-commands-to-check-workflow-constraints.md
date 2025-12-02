---
id: task-096
title: Update /jpspec commands to check workflow constraints
status: To Do
assignee: []
created_date: '2025-11-28 15:58'
labels:
  - implementation
  - integration
  - jpspec-commands
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update all /jpspec command implementations to enforce workflow state constraints from configuration
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All /jpspec command implementations updated to load WorkflowConfig
- [ ] #2 Each command validates that task is in allowed input_state before execution
- [ ] #3 Commands provide clear error messages when state check fails
- [ ] #4 Commands update task state to output_state after successful execution
- [ ] #5 Error messages suggest valid workflows for current state
- [ ] #6 Commands work with both backlog.md and future task systems
- [ ] #7 No breaking changes to existing /jpspec command interfaces
- [ ] #8 All 6 commands (specify, research, plan, implement, validate, operate) implement checks
<!-- AC:END -->
