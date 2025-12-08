---
id: task-086
title: Spec-Light Mode for Medium Features
status: Done
assignee:
  - '@kinsale'
created_date: '2025-11-27 21:54'
updated_date: '2025-12-05 16:28'
labels:
  - jpspec
  - feature
  - ux
  - 'workflow:Specified'
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create simplified SDD workflow for medium-complexity features (after /jpspec:assess recommends it). Addresses Böckeler concern about 'a LOT of markdown files'. Creates spec-light.md (combined stories + AC), plan-light.md (high-level only), tasks.md (standard). Skips: /jpspec:research, /jpspec:analyze, detailed data models, API contracts. Still enforces: constitutional compliance, test-first. 40-50% faster workflow.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create spec-light.md template (combined user stories + AC)
- [x] #2 Create plan-light.md template (high-level approach only)
- [x] #3 Implement 'specify init --light' flag
- [x] #4 Skip research and analyze phases for light mode
- [x] #5 Maintain constitutional compliance requirement
- [x] #6 Simplified quality gates for light mode
- [x] #7 Document when to use light vs full mode
- [x] #8 Test workflow with medium-complexity features
<!-- AC:END -->
