---
id: task-509
title: Integrate Git Operations with Event Emission
status: To Do
assignee:
  - '@chamonix'
created_date: '2025-12-14 03:35'
updated_date: '2026-01-06 18:52'
labels:
  - agent-event-system
  - phase-2
  - architecture
  - scm
  - event-emission
dependencies: []
priority: high
ordinal: 43000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Emit git events on branch, commit, push, merge operations.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 git.commit event on every commit with sha message
- [ ] #2 git.branch_created and git.branch_deleted events
- [ ] #3 git.pushed event on push to remote
- [ ] #4 git.merged event on merge completion
- [ ] #5 Events include GPG signing info when available
<!-- AC:END -->
