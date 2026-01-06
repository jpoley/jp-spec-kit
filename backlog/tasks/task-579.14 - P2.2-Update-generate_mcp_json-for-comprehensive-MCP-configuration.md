---
id: task-579.14
title: 'P2.2: Update generate_mcp_json() for comprehensive MCP configuration'
status: To Do
assignee: []
created_date: '2026-01-06 17:21'
updated_date: '2026-01-06 18:52'
labels:
  - phase-2
  - mcp
  - cli
dependencies:
  - task-579.03
parent_task_id: task-579
priority: high
ordinal: 87000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update the generate_mcp_json() function to create comprehensive MCP configuration with required servers.

Current implementation (lines 2450-2501):
- Only adds backlog and flowspec-security
- Skips if .mcp.json already exists

Changes needed:
1. Add required MCP servers by default: backlog, github, serena
2. Add tech-stack aware recommendations (playwright for frontend, trivy/semgrep for security)
3. Support merging with existing .mcp.json (add missing servers)
4. Add --mcp-minimal flag for minimal config
5. Add prompts for optional servers during init

This function is called by flowspec init and should also be called by upgrade-repo (task-579.03).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 generate_mcp_json() adds required servers (backlog, github, serena)
- [ ] #2 Tech-stack detection adds appropriate optional servers
- [ ] #3 Existing .mcp.json is merged (not overwritten)
- [ ] #4 --mcp-minimal flag available for minimal config
- [ ] #5 Test: flowspec init creates comprehensive .mcp.json
<!-- AC:END -->
