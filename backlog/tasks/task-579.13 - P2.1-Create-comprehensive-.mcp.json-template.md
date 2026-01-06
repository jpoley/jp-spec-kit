---
id: task-579.13
title: 'P2.1: Create comprehensive .mcp.json template'
status: To Do
assignee: []
created_date: '2026-01-06 17:21'
updated_date: '2026-01-06 18:52'
labels:
  - phase-2
  - mcp
  - templates
dependencies: []
parent_task_id: task-579
priority: high
ordinal: 86000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a comprehensive .mcp.json template that includes all required and recommended MCP servers for flowspec projects.

Current generate_mcp_json() only adds:
- backlog (always)
- flowspec-security (Python projects only)

Template should include:

REQUIRED (Core Functionality):
- backlog: Task management (all workflows)
- github: PR/Issue/Code operations (/flow:submit-n-watch-pr)
- serena: Code understanding & edits (/flow:implement, /flow:validate)

RECOMMENDED (Enhanced Features):
- playwright-test: Browser automation for E2E tests
- trivy: Security scanning (/sec:* commands)
- semgrep: SAST code scanning (/sec:* commands)

OPTIONAL (UI Development):
- shadcn-ui: Component library
- chrome-devtools: Browser inspection

Location: templates/.mcp.json (new file)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 templates/.mcp.json created with comprehensive config
- [ ] #2 Config includes required servers (backlog, github, serena)
- [ ] #3 Config includes recommended servers (playwright-test, trivy, semgrep)
- [ ] #4 Config documented with comments explaining each server
- [ ] #5 Test: template is valid JSON and servers are correctly configured
<!-- AC:END -->
