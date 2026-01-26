---
id: task-588
title: 'SPEC-004: Implement continuous learning skill'
status: To Do
assignee: []
created_date: '2026-01-24 15:36'
labels:
  - skills
  - learning
  - phase-3
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement continuous learning with automatic pattern extraction from sessions.

**Problem**: Flowspec doesn't extract reusable patterns from sessions. Each session starts from scratch.

**Solution**: Automatic pattern extraction at session end + manual /flow:learn command.

**Pattern Types**:
- error_resolution - How specific errors were resolved
- user_corrections - Patterns from user corrections
- workarounds - Solutions to framework/library quirks
- debugging_techniques - Effective debugging approaches
- project_specific - Project-specific conventions

**New Skill**: .claude/skills/continuous-learning/SKILL.md
**New Command**: /flow:learn

**Output Location**: .claude/skills/learned/[pattern-name].md

**Source**: docs/specs/flowspec-improvement-specs-v1.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Patterns extracted automatically at session end
- [ ] #2 Manual extraction via /flow:learn command
- [ ] #3 Learned skills loaded on session start
- [ ] #4 Skill files are human-readable and editable
<!-- AC:END -->
