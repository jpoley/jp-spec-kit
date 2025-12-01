---
id: task-189
title: Create Stop Hook for Backlog Task Quality Gate
status: To Do
assignee: []
created_date: '2025-12-01 05:04'
updated_date: '2025-12-01 05:29'
labels:
  - claude-code
  - hooks
  - quality-gates
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement Stop hook to enforce backlog task quality gate before session ends. This aligns with JP Spec Kit's workflow validation approach (see workflow-engine-review.md) without requiring external database state.

Cross-reference: See docs/prd/claude-capabilities-review.md Section 2.1 for hooks gap analysis.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Stop hook script created at .claude/hooks/stop-quality-gate.py

- [ ] #2 Hook detects PR creation intent in conversation context
- [ ] #3 Hook checks for In Progress backlog tasks via CLI
- [ ] #4 Hook provides clear guidance message when tasks are incomplete
- [ ] #5 Hook configuration added to .claude/settings.json
<!-- AC:END -->
