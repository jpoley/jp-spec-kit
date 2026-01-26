---
id: task-581
title: 'SPEC-011: Slim CLAUDE.md to under 200 lines'
status: Done
assignee: []
created_date: '2026-01-24 15:35'
updated_date: '2026-01-24 17:07'
labels:
  - architecture
  - documentation
  - phase-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Reduce CLAUDE.md from ~800 lines to under 200 lines by moving details to rules and skills.

**Current State**: ~800 lines with many @imports
**Target State**: ~200 lines with essentials only

**Move to .claude/rules/**:
- critical-rules.md -> .claude/rules/critical.md
- code-standards.md -> .claude/rules/coding-style.md
- rigor-rules.md -> .claude/rules/rigor.md

**Source**: docs/specs/flowspec-improvement-specs-v1.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 CLAUDE.md under 200 lines
- [x] #2 No embedded code examples > 10 lines
- [x] #3 Rules moved to .claude/rules/
- [x] #4 @imports reduced to essential only
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed via PR #1156

Changes:
- CLAUDE.md reduced from ~800 to 180 lines
- Rules moved to .claude/rules/ (critical.md, coding-style.md, rigor.md)
- Removed verbose code examples and @imports
<!-- SECTION:NOTES:END -->
