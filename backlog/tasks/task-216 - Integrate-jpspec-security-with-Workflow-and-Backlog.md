---
id: task-216
title: 'Integrate /jpspec:security with Workflow and Backlog'
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-12-03 01:58'
labels:
  - security
  - implement
  - workflow
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Wire /jpspec:security commands into jpspec_workflow.yml and add backlog.md task creation for findings.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add optional pre-commit hook integration
- [ ] #2 Implement --create-tasks flag to auto-create backlog tasks for findings
- [ ] #3 Task format includes severity, CWE, location, AI explanation
- [ ] #4 Document workflow integration options (validate extension, dedicated state)
- [ ] #5 CI/CD integration examples (GitHub Actions, GitLab CI)
- [ ] #6 SARIF output for GitHub Code Scanning
<!-- AC:END -->
