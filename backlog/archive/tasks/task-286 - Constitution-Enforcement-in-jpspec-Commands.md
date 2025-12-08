---
id: task-286
title: Constitution Enforcement in /jpspec Commands
status: Done
assignee: []
created_date: '2025-12-04 16:08'
updated_date: '2025-12-04 22:45'
labels:
  - constitution-cleanup
dependencies:
  - task-245
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add constitution checks to all /jpspec slash commands before execution
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Before command execution, check memory/constitution.md existence
- [x] #2 Check for NEEDS_VALIDATION markers in constitution
- [x] #3 Warn if missing or unvalidated
- [x] #4 Respect tier-specific enforcement (light = warn, medium = confirm, heavy = block)
- [x] #5 Add --skip-validation flag for emergencies
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Already implemented - `_constitution-check.md` included in all jpspec commands. Branch merged to main.
<!-- SECTION:NOTES:END -->
