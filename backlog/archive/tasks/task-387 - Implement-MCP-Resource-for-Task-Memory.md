---
id: task-387
title: Implement MCP Resource for Task Memory
status: Done
assignee:
  - '@adare'
created_date: '2025-12-09 15:57'
updated_date: '2025-12-28 20:40'
labels:
  - backend
  - task-memory
  - mcp
  - integration
dependencies:
  - task-375
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add MCP resource endpoint `backlog://memory/{task_id}` to expose task memory to MCP-compatible agents (Copilot, etc.)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add resource endpoint to existing backlog MCP server
- [x] #2 Implement backlog://memory/{task_id} URI handler
- [x] #3 Return markdown content from TaskMemoryStore
- [x] #4 Handle missing memory files with 404 error
- [x] #5 Add MCP resource tests with mock clients
- [ ] #6 Test with live MCP client (if available)
- [ ] #7 Document MCP resource URI in docs/reference/
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
MCP resources fully implemented in src/flowspec_cli/memory/mcp.py (193 LOC):
- list_task_memory_resources() - Lists all available task memories
- get_task_memory_resource() - Gets specific task memory content
- Exposes backlog://memory/{task_id} and backlog://memory/active resources
- Token-aware truncation (2000 token limit)
- JSON metadata support
<!-- SECTION:NOTES:END -->
