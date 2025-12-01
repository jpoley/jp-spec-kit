---
id: task-192
title: Refactor CLAUDE.md to Use @import Syntax
status: To Do
assignee: []
created_date: '2025-12-01 05:05'
updated_date: '2025-12-01 05:31'
labels:
  - claude-code
  - documentation
  - refactoring
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refactor root CLAUDE.md to use @import syntax for modular organization. This reduces duplication and improves maintainability.

Cross-reference: See docs/prd/claude-capabilities-review.md Section 2.6 for CLAUDE.md assessment.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create memory/ directory for modular imports

- [ ] #2 Extract constitution principles to importable file
- [ ] #3 Extract coding standards to importable file
- [ ] #4 Root CLAUDE.md uses @import for major sections
- [ ] #5 All imports tested and loading correctly
<!-- AC:END -->
