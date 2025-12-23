---
id: task-480
title: 'claude-improves: Add flowspec init --complete option'
status: In Progress
assignee:
  - '@myself'
created_date: '2025-12-12 01:15'
updated_date: '2025-12-22 22:54'
labels:
  - claude-improves
  - cli
  - specify-init
  - feature
  - phase-2
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a --complete flag to flowspec init that deploys ALL templates in a single command, rather than requiring multiple init invocations for different components.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 --complete flag enables all optional features
- [ ] #2 Skills deployed to .claude/skills/
- [ ] #3 All hooks enabled in hooks.yaml
- [ ] #4 Full CI/CD template with lint, test, security jobs
- [ ] #5 Complete VSCode settings and extensions
- [ ] #6 MCP configuration created
- [ ] #7 Documentation explains --complete vs default behavior
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Wait for task-470 ACs #1-5 to complete\n2. Audit templates: CI/CD, VSCode, MCP config\n3. Implement --complete flag aggregation logic\n4. Override opt-out flags when --complete is set\n5. Create full CI/CD template (if missing)\n6. Create complete VSCode settings template\n7. Research and create MCP config template\n8. Write unit tests for --complete mode\n9. Create documentation comparing default vs --complete
<!-- SECTION:PLAN:END -->
