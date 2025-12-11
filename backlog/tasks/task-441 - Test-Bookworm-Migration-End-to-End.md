---
id: task-441
title: Test Bookworm Migration End-to-End
status: To Do
assignee: []
created_date: '2025-12-11 04:14'
labels:
  - qa
  - testing
  - docker
  - security
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Comprehensive testing of bookworm migration in both Docker and devcontainer environments
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 pytest test suite passes in bookworm container
- [ ] #2 AI CLI tools (claude-code, copilot, etc.) functional
- [ ] #3 MCP servers (backlog) operational - health checks pass
- [ ] #4 Build time comparable to bullseye baseline
- [ ] #5 Image size within 10% of bullseye (~1.5GB)
- [ ] #6 No regressions in developer workflow
- [ ] #7 VS Code debugger works
<!-- AC:END -->
