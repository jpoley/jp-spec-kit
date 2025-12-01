---
id: task-191
title: Create 4 Engineering Subagents
status: To Do
assignee: []
created_date: '2025-12-01 05:04'
updated_date: '2025-12-01 05:29'
labels:
  - claude-code
  - subagents
  - sdd-workflow
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement 4 engineering subagents for specialized implementation work: frontend-engineer, backend-engineer, qa-engineer, and security-reviewer. These complement the existing pm-planner subagent.

Cross-reference: See docs/prd/claude-capabilities-review.md Section 2.7 for subagent gap analysis.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 frontend-engineer subagent created with React/Next.js/UI expertise

- [ ] #2 backend-engineer subagent created with API/database/Python expertise
- [ ] #3 qa-engineer subagent created with testing/coverage/E2E expertise
- [ ] #4 security-reviewer subagent created with SLSA/vulnerability assessment expertise
- [ ] #5 All subagents have appropriate tool restrictions in frontmatter
- [ ] #6 Subagents documented in CLAUDE.md
<!-- AC:END -->
