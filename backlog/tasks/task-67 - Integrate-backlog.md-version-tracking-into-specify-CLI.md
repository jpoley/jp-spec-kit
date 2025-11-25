---
id: task-67
title: Integrate backlog.md version tracking into specify CLI
status: To Do
assignee: []
created_date: '2025-11-25 21:42'
labels:
  - P0
  - integration
  - backlog-md
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add backlog.md as a tracked dependency alongside spec-kit, enabling unified version management, auto-install during init, and synchronized upgrades.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Extend .spec-kit-compatibility.yml with backlog-md section (min/max/tested/recommended versions)
- [ ] #2 Add specify backlog install command that auto-detects pnpm/npm and installs validated version
- [ ] #3 Add specify backlog upgrade command (or integrate into existing specify upgrade)
- [ ] #4 During specify init, check for backlog.md and offer to install if missing
- [ ] #5 Add --backlog-version flag to specify init for version pinning
- [ ] #6 Update specify upgrade to check and sync backlog.md to validated version
- [ ] #7 Add backlog.md version to specify check output
<!-- AC:END -->
