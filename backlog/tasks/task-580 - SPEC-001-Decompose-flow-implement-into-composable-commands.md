---
id: task-580
title: 'SPEC-001: Decompose /flow:implement into composable commands'
status: To Do
assignee: []
created_date: '2026-01-24 15:35'
labels:
  - architecture
  - refactoring
  - phase-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Decompose the monolithic /flow:implement command (1,419 lines) into focused, composable units.

**Current State**: Single command doing 8 things across 7 phases
**Target State**: 5 composable commands, each <200 lines

**New Commands to Create**:
- /flow:gate - Quality gate validation (~50 lines)
- /flow:rigor - Rigor rule enforcement (~100 lines)
- /flow:build - Parallel implementation orchestration (~100 lines)
- /flow:review - Code review with AC verification (~100 lines)
- /flow:pre-pr - Pre-PR validation checklist (~100 lines)

**Source**: docs/specs/flowspec-improvement-specs-v1.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 No single command exceeds 200 lines
- [ ] #2 Each command has ONE clear responsibility
- [ ] #3 Commands are composable via orchestration
- [ ] #4 Backward compatibility: /flow:implement still works
- [ ] #5 /flow:implement becomes orchestrator only (~50 lines)
<!-- AC:END -->
