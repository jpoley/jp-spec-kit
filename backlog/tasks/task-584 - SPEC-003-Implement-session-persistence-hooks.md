---
id: task-584
title: 'SPEC-003: Implement session persistence hooks'
status: To Do
assignee: []
created_date: '2026-01-24 15:35'
labels:
  - hooks
  - session-management
  - phase-2
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement session persistence hooks to prevent context loss when sessions end or compact.

**Problem**: All context lost on session end - what was being worked on, decisions made, files modified, open questions.

**Solution**: SessionStart/SessionEnd hooks that save and restore state.

**New Hooks**:
- session-start.js - Restores state and displays summary
- session-end.js - Saves current state
- pre-compact.js - Preserves state before compaction

**Session State File** (.flowspec/session-state.json):
```json
{
  "lastActivity": "2025-01-24T10:30:00Z",
  "activeTask": "task-543",
  "workingFiles": ["src/cli.py", "tests/test_cli.py"],
  "decisions": [{"what": "Use Click", "why": "Better composability"}],
  "openQuestions": ["How to handle config precedence?"],
  "checkpoint": "abc123"
}
```

**Source**: docs/specs/flowspec-improvement-specs-v1.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 State persists across session restarts
- [ ] #2 State preserved before context compaction
- [ ] #3 Clear summary displayed on session start
- [ ] #4 Node.js based for cross-platform support
<!-- AC:END -->
