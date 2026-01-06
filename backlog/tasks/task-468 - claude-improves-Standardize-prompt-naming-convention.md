---
id: task-468
title: 'claude-improves: Standardize prompt naming convention'
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2026-01-06 18:52'
labels:
  - claude-improves
  - source-repo
  - prompts
  - naming
  - phase-2
dependencies: []
priority: high
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GitHub prompts use mixed naming conventions:
- jpspec.* (current)
- specflow.* (legacy)
- speckit.* (current)

This inconsistency causes confusion. Need to standardize on one naming convention or document the mapping clearly.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document the naming convention strategy (standardize vs coexist)
- [ ] #2 If standardizing: migrate all prompts to consistent naming
- [ ] #3 If coexisting: document the mapping in CLAUDE.md
- [ ] #4 Update any references to old naming convention
- [ ] #5 Add validation to CI to prevent naming drift
<!-- AC:END -->
