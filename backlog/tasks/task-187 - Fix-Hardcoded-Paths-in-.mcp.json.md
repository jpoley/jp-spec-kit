---
id: task-187
title: Fix Hardcoded Paths in .mcp.json
status: To Do
assignee: []
created_date: '2025-12-01 05:04'
updated_date: '2025-12-01 05:30'
labels:
  - claude-code
  - mcp
  - quick-win
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace hardcoded absolute paths in .mcp.json with environment variables or relative paths to improve portability across different machines.

Cross-reference: See docs/prd/claude-capabilities-review.md Section 2.4 for MCP assessment.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Audit .mcp.json for hardcoded absolute paths

- [ ] #2 Replace hardcoded paths with relative paths or env vars
- [ ] #3 Document any required environment variables
- [ ] #4 Test configuration on clean environment
<!-- AC:END -->
