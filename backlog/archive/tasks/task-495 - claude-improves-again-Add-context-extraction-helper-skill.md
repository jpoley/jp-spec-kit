---
id: task-495
title: 'claude-improves-again: Add context extraction helper skill'
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-14 03:06'
updated_date: '2025-12-28 20:27'
labels:
  - context-engineering
  - skills
  - claude-improves-again
dependencies:
  - task-494
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a helper skill that parses the All Needed Context section from PRD files and returns structured data (JSON). This helper is used by /flow:implement, /flow:generate-prp, and /flow:validate.

Source: docs/research/archon-inspired.md Task 8
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Skill created at .claude/skills/context-extractor/SKILL.md
- [x] #2 Accepts path to a PRD file as input
- [x] #3 Parses All Needed Context section into structured JSON
- [x] #4 Returns code files, docs, examples, gotchas as structured data
- [x] #5 Can be invoked by other flow commands
<!-- AC:END -->
