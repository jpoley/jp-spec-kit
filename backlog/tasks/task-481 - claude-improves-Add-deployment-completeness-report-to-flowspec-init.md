---
id: task-481
title: 'claude-improves: Add deployment completeness report to flowspec init'
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2026-01-06 18:52'
labels:
  - claude-improves
  - cli
  - specify-init
  - ux
  - phase-2
dependencies: []
priority: high
ordinal: 33000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After flowspec init completes, display a summary showing what was deployed, what was skipped, and what manual steps remain.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Init outputs summary table of deployed components
- [ ] #2 Shows skills: deployed vs available
- [ ] #3 Shows hooks: enabled vs disabled
- [ ] #4 Shows templates: created vs skipped
- [ ] #5 Provides suggestions for --complete or individual flags
- [ ] #6 Summary includes next steps for user
- [ ] #7 Add --quiet flag to suppress report
<!-- AC:END -->
