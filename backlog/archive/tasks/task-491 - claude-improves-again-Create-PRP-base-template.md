---
id: task-491
title: 'claude-improves-again: Create PRP base template'
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-14 03:06'
updated_date: '2025-12-19 18:56'
labels:
  - context-engineering
  - templates
  - claude-improves-again
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a Product Requirements Prompt (PRP) template that acts as a single, self-contained context packet for each feature. This includes ALL NEEDED CONTEXT, CODEBASE SNAPSHOT, and VALIDATION LOOP sections.

Source: docs/research/archon-inspired.md Task 4
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Template created at templates/docs/prp/prp-base-flowspec.md
- [x] #2 ALL NEEDED CONTEXT section with Code Files, Docs/Specs, Examples, Known Gotchas, Related Tasks subsections
- [x] #3 CODEBASE SNAPSHOT section for bounded directory tree
- [x] #4 VALIDATION LOOP section with Commands, Expected Success, Known Failure Modes
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Already implemented - template exists at templates/docs/prp/prp-base-flowspec.md with ALL NEEDED CONTEXT, CODEBASE SNAPSHOT, and VALIDATION LOOP sections.
<!-- SECTION:NOTES:END -->
