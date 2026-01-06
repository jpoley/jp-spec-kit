---
id: task-579.15
title: 'P2.3: Add MCP server health check to init/upgrade'
status: To Do
assignee: []
created_date: '2026-01-06 17:21'
updated_date: '2026-01-06 18:52'
labels:
  - phase-2
  - mcp
  - cli
  - quality
dependencies: []
parent_task_id: task-579
priority: medium
ordinal: 88000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add optional MCP server health check to flowspec init and upgrade-repo commands.

Purpose: Verify that configured MCP servers are available and working before completing init/upgrade.

Implementation:
1. Add --check-mcp flag to init and upgrade-repo
2. For each configured server, attempt to start and verify connectivity
3. Report which servers are available vs missing
4. Warn (don't fail) for missing recommended servers
5. Fail for missing required servers (with override flag)

This helps users identify MCP configuration issues early.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 --check-mcp flag added to init and upgrade-repo
- [ ] #2 Health check verifies MCP server availability
- [ ] #3 Clear reporting of available vs missing servers
- [ ] #4 Warnings for missing recommended servers
- [ ] #5 Appropriate error handling for missing required servers
<!-- AC:END -->
