---
id: task-585
title: 'SPEC-005: Implement strategic compaction suggestions'
status: To Do
assignee: []
created_date: '2026-01-24 15:35'
labels:
  - hooks
  - context-management
  - phase-2
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement strategic compaction suggestions at logical workflow boundaries instead of arbitrary points.

**Problem**: Context compaction happens mid-task, losing important context.

**Solution**: Suggest /compact at logical boundaries:
- After exploration, before execution
- After completing a milestone
- Before major context shifts

**Implementation**:
- Hook-based suggestion after configurable threshold (default: 50 edits)
- suggest-compact.js hook on PreToolUse for Edit|Write
- Suggestions every 25 edits after threshold

**Source**: docs/specs/flowspec-improvement-specs-v1.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Suggestions at configurable thresholds (default: 50)
- [ ] #2 State saved before compaction
- [ ] #3 Suggestions are non-blocking
- [ ] #4 Clear messaging about what will be preserved
<!-- AC:END -->
