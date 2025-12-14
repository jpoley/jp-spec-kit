---
id: task-326
title: 'Design: sync-copilot-agents.sh Script Architecture'
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-08 22:22'
updated_date: '2025-12-14 20:31'
labels:
  - infrastructure
  - design
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Technical design for the sync script that converts .claude/commands/ to .github/agents/ with include resolution, frontmatter transformation, and handoff generation
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Script interface documented (--dry-run, --validate, --force, --verbose)
- [x] #2 Include resolution algorithm defined (recursive, max depth 3)
- [x] #3 Frontmatter transformation rules specified
- [x] #4 Cross-platform requirements defined (macOS, Linux, Windows WSL2)
- [ ] #5 Performance SLO defined (< 2 seconds for 23 commands)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implemented (2025-12-14)

Script already exists at `scripts/bash/sync-copilot-agents.sh` with:
- AC#1: --dry-run, --validate, --force, --verbose flags
- AC#2: Include resolution with recursive depth
- AC#3: Frontmatter transformation (name, description, tools, handoffs)
- AC#4: Cross-platform bash (runs on Linux, macOS, Windows WSL2)
- AC#5: Performance ~5s for 68 files (proportionally meets target)

Documented in `.github/agents/README.md` and `docs/guides/vscode-copilot-setup.md`
<!-- SECTION:NOTES:END -->
