---
id: task-592
title: 'SPEC-010: Create /flow:checkpoint command'
status: To Do
assignee: []
created_date: '2026-01-24 15:36'
labels:
  - commands
  - workflow
  - phase-4
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add checkpoint command to create named save points and compare against them.

**Problem**: No way to create named save points and compare against them.

**Solution**: /flow:checkpoint command with create, verify, and list actions.

**Actions**:
- create [name]: Create checkpoint with git SHA
- verify [name]: Compare current state to checkpoint
- list: Show all checkpoints with status

**Checkpoint Log**: .flowspec/checkpoints.log
```
2025-01-24-10:30 | feature-start | abc123
```

**Comparison Output**:
```
CHECKPOINT COMPARISON: $NAME
============================
Files changed: X
Tests: +Y passed / -Z failed
Coverage: +X% / -Y%
Build: [PASS/FAIL]
```

**Source**: docs/specs/flowspec-improvement-specs-v1.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Named checkpoints with git SHA
- [ ] #2 Comparison reports changes since checkpoint
- [ ] #3 List all checkpoints with status
- [ ] #4 Clear old checkpoints (keep last 5)
<!-- AC:END -->
