---
id: task-586
title: 'SPEC-009: Create standalone /flow:verify command'
status: To Do
assignee: []
created_date: '2026-01-24 15:35'
labels:
  - commands
  - verification
  - phase-2
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extract verification logic from /flow:implement into a standalone reusable command.

**Problem**: Verification is buried in 200+ lines within /flow:implement.

**Solution**: Standalone /flow:verify command with quick and full modes.

**Verification Phases**:
1. Build Verification
2. Type Check (pyright/tsc)
3. Lint Check (ruff/eslint)
4. Test Suite with coverage
5. Security Scan
6. Diff Review

**Output Format**:
```
VERIFICATION REPORT
==================
Build:     [PASS/FAIL]
Types:     [PASS/FAIL] (X errors)
Lint:      [PASS/FAIL] (X warnings)
Tests:     [PASS/FAIL] (X/Y passed, Z% coverage)
Security:  [PASS/FAIL] (X issues)
Overall:   [READY/NOT READY] for PR
```

**Source**: docs/specs/flowspec-improvement-specs-v1.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Standalone command not embedded in implement
- [ ] #2 Quick mode (build + lint + tests only)
- [ ] #3 Full mode (all 6 phases)
- [ ] #4 Clear pass/fail report
<!-- AC:END -->
