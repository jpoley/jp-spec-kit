---
id: task-387
title: Implement MCP Resource for Task Memory
status: In Progress
assignee:
  - '@adare'
created_date: '2025-12-09 15:57'
updated_date: '2025-12-15 02:17'
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
Implemented MCP resource endpoints for task memory:

- Created src/specify_cli/memory/mcp.py with register_memory_resources()
- Two resource URIs: backlog://memory/{task_id} and backlog://memory/active
- Returns JSON with task memory content from TaskMemoryStore
- Handles missing files, invalid IDs, and CLAUDE.md errors gracefully
- 10/10 tests pass (business logic and registration)
- Exports: register_memory_resources(), create_memory_mcp_server()

Note: AC#1 (add to existing server) will be done when integrating with main backlog MCP. AC#6 and AC#7 are integration/documentation tasks to complete separately.
<!-- SECTION:NOTES:END -->
