---
id: task-103
title: Create workflow configuration troubleshooting guide
status: Done
assignee: []
created_date: '2025-11-28 15:58'
updated_date: '2025-12-03 01:16'
labels:
  - documentation
  - troubleshooting
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create comprehensive troubleshooting guide for common workflow configuration issues
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Troubleshooting guide created at docs/guides/workflow-troubleshooting.md
- [x] #2 Section: 'jpspec_workflow.yml not found' with solution
- [x] #3 Section: 'Configuration validation errors' with examples and fixes
- [x] #4 Section: 'State transition errors' with examples and solutions
- [x] #5 Section: 'Circular dependencies detected' explanation and fix
- [x] #6 Section: 'Unreachable states' explanation and fix
- [x] #7 Section: 'Agent not found' explanation and fix
- [x] #8 Section: 'Custom workflow not working' debugging steps
- [x] #9 Section: 'Rolling back configuration changes' instructions
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
AC #9 already complete - workflow-troubleshooting.md has:
- "Recovery and Rollback" section (line 570)
- "Rolling Back Configuration Changes" subsection (line 572)
- Complete step-by-step instructions for git restore, backups, emergency reset

docs/guides/workflow-troubleshooting.md complete (17KB) via PR #173
<!-- SECTION:NOTES:END -->
