---
id: task-213
title: Implement Automated Fix Generation and Patch Application
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-12-03 01:58'
labels:
  - security
  - implement
  - ai
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build AI-powered code patch generator for common vulnerability patterns. Enables /jpspec:security fix command.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Fix pattern library for SQL injection, XSS, path traversal, secrets, crypto
- [ ] #2 AI generates patches with before/after code and unified diff
- [ ] #3 Syntax validation of generated patches
- [ ] #4 Patch application workflow with confirmation
- [ ] #5 Fix quality >75% (correct or mostly correct)
- [ ] #6 Generate .patch files for each finding
<!-- AC:END -->
