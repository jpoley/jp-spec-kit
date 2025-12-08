---
id: task-096
title: Update /jpspec commands to check workflow constraints
status: Done
assignee: []
created_date: '2025-11-28 15:58'
updated_date: '2025-12-02 23:42'
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
- [x] #1 All /jpspec command implementations updated to load WorkflowConfig
- [x] #2 Each command validates that task is in allowed input_state before execution
- [x] #3 Commands provide clear error messages when state check fails
- [x] #4 Commands update task state to output_state after successful execution
- [x] #5 Error messages suggest valid workflows for current state
- [x] #6 Commands work with both backlog.md and future task systems
- [x] #7 No breaking changes to existing /jpspec command interfaces
- [x] #8 All 6 commands (specify, research, plan, implement, validate, operate) implement checks
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed via PR #229 (merged)

Implementation:
- Added WorkflowStateGuard module (src/specify_cli/workflow/state_guard.py)
- Updated all 7 /jpspec commands with workflow validation
- 50 comprehensive tests
- Resolved conflicts with enhanced validate.md phased workflow
<!-- SECTION:NOTES:END -->
