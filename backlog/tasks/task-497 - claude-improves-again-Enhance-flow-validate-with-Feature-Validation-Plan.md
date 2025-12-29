---
id: task-497
title: 'claude-improves-again: Enhance /flow:validate with Feature Validation Plan'
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-14 03:06'
updated_date: '2025-12-28 22:15'
labels:
  - context-engineering
  - commands
  - claude-improves-again
dependencies:
  - task-496
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update /flow:validate to extract and execute the Feature Validation Plan from PRD/PRP files. The command should run validation commands and update task notes with results.

Source: docs/research/archon-inspired.md Task 10
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 /flow:validate locates PRD or PRP for active task
- [x] #2 Extracts Feature Validation Plan section using context helper
- [x] #3 Runs validation commands or prints them for manual execution
- [x] #4 Updates backlog task notes with validation results
- [x] #5 Updates task memory with Current State and Latest validation run
<!-- AC:END -->
