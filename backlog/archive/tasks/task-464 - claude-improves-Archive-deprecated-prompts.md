---
id: task-464
title: 'claude-improves: Archive deprecated prompts'
status: Done
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2025-12-15 01:49'
labels:
  - claude-improves
  - source-repo
  - prompts
  - cleanup
  - phase-1
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
13 deprecated prompts exist in .github/prompts/ that should be archived or removed:
- specflow._DEPRECATED_*.prompt.md (13 files)

These clutter the prompts directory and may cause confusion.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create .github/prompts/archive/ directory
- [x] #2 Move all *DEPRECATED* files to archive directory
- [x] #3 Verify no deprecated files remain in main prompts directory
- [x] #4 Update any documentation referencing these prompts
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Archived 13 deprecated prompts to .github/prompts/archive/

Files moved:
- specflow._DEPRECATED_assess.prompt.md
- specflow._DEPRECATED_implement.prompt.md
- specflow._DEPRECATED_operate.prompt.md
- specflow._DEPRECATED_plan.prompt.md
- specflow._DEPRECATED_prune-branch.prompt.md
- specflow._DEPRECATED_research.prompt.md
- specflow._DEPRECATED_security_fix.prompt.md
- specflow._DEPRECATED_security_report.prompt.md
- specflow._DEPRECATED_security_triage.prompt.md
- specflow._DEPRECATED_security_web.prompt.md
- specflow._DEPRECATED_security_workflow.prompt.md
- specflow._DEPRECATED_specify.prompt.md
- specflow._DEPRECATED_validate.prompt.md

No documentation updates needed - docs/research/claude-repair.md already documents this cleanup as a recommended fix.

Task completed - PR #801 merged 2025-12-12. All acceptance criteria met.
<!-- SECTION:NOTES:END -->
