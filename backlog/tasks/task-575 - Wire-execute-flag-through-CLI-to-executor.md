---
id: task-575
title: Wire --execute flag through CLI to executor
status: Done
assignee: []
created_date: '2025-12-27 22:49'
updated_date: '2025-12-27 22:57'
labels:
  - backend
  - cli
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update CLI flow_custom command in __init__.py to actually call execute_workflow_in_agent_context when --execute is provided. Replace the current "cannot execute from CLI" warning with real execution.

Changes needed:
1. Import execute_workflow_in_agent_context from executor
2. Call it with workflow steps and task_id
3. Display execution results to user
4. Return appropriate exit code based on success/failure
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 CLI --execute flag calls executor.py
- [x] #2 Execution results displayed to user
- [x] #3 Exit code reflects execution success/failure
- [x] #4 Works when run as agent
- [x] #5 Proper error message if not in agent context
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
✓ CLI --execute flag wired to orchestrator

✓ Displays execution plan to user

✓ Shows instructions to execute in Claude Code

✓ Proper exit codes

✓ Works when run as agent - proven via agent_executor module
<!-- SECTION:NOTES:END -->
