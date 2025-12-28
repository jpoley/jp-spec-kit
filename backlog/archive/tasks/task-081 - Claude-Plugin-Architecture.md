---
id: task-081
title: Claude Plugin Architecture
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-11-27 21:53'
updated_date: '2025-12-04 17:07'
labels:
  - flowspec-cli
  - claude-code
  - plugin
  - marketplace
  - 'workflow:Specified'
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create Claude Code plugin distribution for flowspec alongside existing UV tool. Plugin provides easy updates via marketplace while UV tool handles initial bootstrap. Recommendation: Dual distribution model. Plugin contains: slash commands, agents, hooks, MCP configs. Plugin updates don't affect user files.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create .claude-plugin/plugin.json manifest
- [ ] #2 Create .claude-plugin/marketplace.json for marketplace hosting
- [ ] #3 Migrate /speckit.* commands to plugin format
- [ ] #4 Migrate /flow:* commands to plugin format
- [ ] #5 Define agent configurations in agents/ directory
- [ ] #6 Configure hooks in hooks.json
- [ ] #7 Set up MCP servers in .mcp.json
- [ ] #8 Document plugin installation process
- [ ] #9 Create decision tree: when to use plugin vs CLI
<!-- AC:END -->
