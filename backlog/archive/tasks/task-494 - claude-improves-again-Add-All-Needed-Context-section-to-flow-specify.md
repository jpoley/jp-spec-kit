---
id: task-494
title: 'claude-improves-again: Add All Needed Context section to /flow:specify'
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-14 03:06'
updated_date: '2025-12-28 20:27'
labels:
  - context-engineering
  - commands
  - templates
  - claude-improves-again
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update the /flow:specify template to include a structured All Needed Context block that is easy to parse and reuse by other commands. This section lists code files, docs, examples, gotchas, and external APIs.

Source: docs/research/archon-inspired.md Task 7
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 /flow:specify template includes All Needed Context section
- [ ] #2 Section has Code Files, Docs/Specs, Examples, Gotchas/Prior Failures, External Systems subsections
- [ ] #3 Structure is machine-parseable by other flowspec commands
- [ ] #4 Documentation explains the purpose and format
<!-- AC:END -->
