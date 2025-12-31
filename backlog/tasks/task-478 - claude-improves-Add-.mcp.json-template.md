---
id: task-478
title: 'claude-improves: Add .mcp.json template'
status: Done
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2025-12-31 22:05'
labels:
  - claude-improves
  - templates
  - mcp
  - configuration
  - phase-2
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
No .mcp.json configuration is created during `specify init`. Projects using MCP servers need this configuration file.

Should provide a template with common MCP server configurations.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 .mcp.json template created with common server stubs
- [x] #2 Template includes backlog MCP server configuration
- [ ] #3 Documentation comments explain each server option
- [ ] #4 specify init prompts for MCP configuration (optional)
- [ ] #5 Template is JSON5 compatible for comments
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented generate_mcp_json() function that creates .mcp.json during flowspec init with backlog and flowspec-security MCP servers. Tech-stack aware (adds Python-specific servers for Python projects).
<!-- SECTION:NOTES:END -->
