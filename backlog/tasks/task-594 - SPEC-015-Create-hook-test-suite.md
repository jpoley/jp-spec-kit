---
id: task-594
title: 'SPEC-015: Create hook test suite'
status: To Do
assignee: []
created_date: '2026-01-24 15:36'
labels:
  - testing
  - hooks
  - phase-4
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add Node.js test suite for hooks to detect breaking changes.

**Problem**: Flowspec hooks aren't tested. Breaking changes go undetected.

**Solution**: Node.js test suite using node:test.

**New Structure**:
```
.claude/hooks/
├── tests/
│   ├── run-all.js
│   ├── lib/
│   │   ├── utils.test.js
│   │   └── package-manager.test.js
│   └── hooks/
│       ├── session-start.test.js
│       ├── suggest-compact.test.js
│       └── evaluate-session.test.js
```

**Run Command**: node .claude/hooks/tests/run-all.js

**Source**: docs/specs/flowspec-improvement-specs-v1.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Test suite for all hooks
- [ ] #2 Tests run with node tests/run-all.js
- [ ] #3 Coverage for edge cases
- [ ] #4 CI integration possible
<!-- AC:END -->
