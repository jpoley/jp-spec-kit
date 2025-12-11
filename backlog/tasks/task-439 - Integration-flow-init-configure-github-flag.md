---
id: task-439
title: 'Integration: /flow:init --configure-github flag'
status: To Do
assignee: []
created_date: '2025-12-11 04:13'
labels:
  - cli
  - github
  - enhancement
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Integrate GitHub project setup features into /flow:init command with --configure-github flag. This would allow automatic generation of GitHub templates from templates/github/ during project initialization. Continuation of task-437.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add --configure-github flag to /flow:init command
- [ ] #2 Implement template copying from templates/github/ to .github/
- [ ] #3 Add variable substitution for {{REPO_NAME}}, {{OWNER}}, etc.
- [ ] #4 Support both greenfield and brownfield scenarios
- [ ] #5 Update CLI help text and documentation
<!-- AC:END -->
