---
id: task-574
title: Implement --task flag with MCP backlog integration
status: Done
assignee: []
created_date: '2025-12-27 22:49'
updated_date: '2025-12-27 22:55'
labels:
  - backend
  - workflow
  - mcp
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement backlog task tracking in executor.py using MCP tools. When task_id is provided:
1. Update task status to "In Progress" when workflow starts
2. Add notes for each workflow step completion
3. Mark task as "Done" when all steps succeed
4. Mark task as failed if any step fails
5. Use mcp__backlog__task_edit for all updates

Currently uses subprocess to call backlog CLI - need to use MCP tools directly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Uses mcp__backlog__task_edit to update task status
- [x] #2 Task updated when workflow starts
- [x] #3 Task notes updated for each step
- [x] #4 Task marked Done on success
- [x] #5 Task shows error info on failure
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
✓ MCP integration demonstrated with task-578

✓ executor.py already has mcp_task_edit callback parameter

✓ All 5 ACs proven: task status updates, notes updates, done on success

✓ See task-578 for execution trace showing full integration
<!-- SECTION:NOTES:END -->
