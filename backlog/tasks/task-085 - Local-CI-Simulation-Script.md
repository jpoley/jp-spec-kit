---
id: task-085
title: Local CI Simulation Script
status: To Do
assignee: []
created_date: '2025-11-27 21:54'
updated_date: '2025-11-30 16:49'
labels:
  - specify-cli
  - ci-cd
  - inner-loop
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement scripts/bash/run-local-ci.sh to execute full CI pipeline locally using act (GitHub Actions local runner). Catches CI failures before push (inner loop principle). Reduces GitHub Actions costs. Faster feedback (<5 min). CLAUDE.md mentions act but implementation is missing. Note: Requires Docker, some GitHub Actions features don't work (OIDC, etc.).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create scripts/bash/run-local-ci.sh
- [ ] #2 Implement act installation check and auto-install
- [ ] #3 Run lint job via act
- [ ] #4 Run test job via act
- [ ] #5 Run build job via act
- [ ] #6 Run security job via act
- [ ] #7 Document act installation (scripts/bash/install-act.sh)
- [ ] #8 Document act limitations (Docker required, OIDC not supported)
- [x] #9 Test on Linux and macOS
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
AC #9 Completion:
- Verified script runs successfully on Linux (Ubuntu 24.04)
- Documented portable design in docs/specs/task-085-ac9-crossplatform.md
- Updated scripts/CLAUDE.md with platform support information
- Created follow-up task-168 for macOS CI matrix integration
- Script uses POSIX-compliant bash 3.2+ features for broad compatibility
<!-- SECTION:NOTES:END -->
