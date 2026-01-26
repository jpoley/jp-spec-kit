---
id: task-590
title: 'SPEC-008: Convert hooks to Node.js for cross-platform support'
status: To Do
assignee: []
created_date: '2026-01-24 15:36'
labels:
  - hooks
  - cross-platform
  - phase-3
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Rewrite hooks in Node.js for cross-platform support (Windows, macOS, Linux).

**Current State**: Bash-only hooks, limiting Windows compatibility.

**Target State**: Node.js hooks with shared utility library.

**New Structure**:
```
.claude/hooks/
├── lib/
│   ├── utils.js              # Cross-platform utilities
│   └── package-manager.js    # PM detection
├── session-start.js
├── session-end.js
├── pre-compact.js
├── suggest-compact.js
├── evaluate-session.js
└── format-python.js
```

**Shared Utilities**: getSessionsDir, ensureDir, findFiles

**Source**: docs/specs/flowspec-improvement-specs-v1.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All hooks work on Windows, macOS, Linux
- [ ] #2 Shared utility library for common operations
- [ ] #3 No bash dependencies in hook execution
- [ ] #4 Python hooks converted to Node.js or called via node
<!-- AC:END -->
