---
id: task-68
title: Enable jp-spec-kit to dogfood itself without circular dependency
status: To Do
assignee: []
created_date: '2025-11-25 21:57'
labels:
  - P0
  - dogfooding
  - developer-experience
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Allow jp-spec-kit to use its own /speckit.* and /jpspec:* commands during development without running specify init on itself (which would clobber source files). This enables true dogfooding of the spec-driven workflow.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create .jp-spec-kit-source marker file at repo root to identify this as the source repository
- [ ] #2 Update specify init to detect .jp-spec-kit-source and skip/warn instead of clobbering
- [ ] #3 Create .claude/commands/speckit/ directory with symlinks to templates/commands/*.md files
- [ ] #4 Verify all /speckit.* commands work in jp-spec-kit repo (analyze, checklist, clarify, constitution, implement, plan, specify, tasks)
- [ ] #5 Verify all /jpspec:* commands still work (implement, operate, plan, research, specify, validate)
- [ ] #6 Add specify dogfood command as alternative to manually creating symlinks (optional convenience)
- [ ] #7 Document dogfooding setup in CONTRIBUTING.md with platform-specific notes (Windows symlink requirements)
- [ ] #8 Test that specify upgrade also respects the .jp-spec-kit-source marker
- [ ] #9 Ensure symlinks are tracked in git (verify .gitattributes if needed)
<!-- AC:END -->
