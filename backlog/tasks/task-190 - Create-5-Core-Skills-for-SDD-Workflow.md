---
id: task-190
title: Create 5 Core Skills for SDD Workflow
status: To Do
assignee: []
created_date: '2025-12-01 05:04'
updated_date: '2025-12-01 05:29'
labels:
  - claude-code
  - skills
  - sdd-workflow
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement 5 core Skills for SDD workflow automation: pm-planner, architect, qa-validator, security-reviewer, and sdd-methodology. Skills enable Claude to automatically invoke domain expertise based on task context.

Cross-reference: See docs/prd/claude-capabilities-review.md Section 2.3 for Skills gap analysis and docs/prd/workflow-engine-review.md for workflow context.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 pm-planner skill created with SKILL.md, task templates, and atomic task examples

- [ ] #2 architect skill created with ADR templates and architecture decision patterns
- [ ] #3 qa-validator skill created with test plan templates and QA checklists
- [ ] #4 security-reviewer skill created with SLSA requirements and security review checklists
- [ ] #5 sdd-methodology skill created with SDD workflow guidance and best practices
- [ ] #6 All skills have proper frontmatter (name, description) for automatic discovery
- [ ] #7 Skills documented in CLAUDE.md hooks section
<!-- AC:END -->
