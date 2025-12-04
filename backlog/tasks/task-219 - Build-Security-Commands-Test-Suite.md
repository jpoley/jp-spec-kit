---
id: task-219
title: Build Security Commands Test Suite
status: To Do
assignee:
  - '@muckross'
created_date: '2025-12-03 01:58'
updated_date: '2025-12-04 16:32'
labels:
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create comprehensive test suite for security module with unit, integration, and snapshot tests.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Unit tests for scanner.py with mocked Semgrep output
- [ ] #2 Integration tests on sample vulnerable projects
- [ ] #3 AI triage accuracy tests on benchmark dataset
- [ ] #4 Fix generation quality tests (syntax validation)
- [ ] #5 Snapshot tests for report format stability
- [ ] #6 Test coverage >85% for security/ module
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Build Security Commands Test Suite

### Overview
Create comprehensive test suite covering unit tests, integration tests, AI triage accuracy tests, and snapshot tests.

### Step-by-Step Implementation

#### Step 1: Unit Tests for Scanner Module (3 hours)
**File**: `tests/security/test_scanner.py`

Test coverage:
- Semgrep execution with mocked output
- Result parsing (JSON, SARIF)
- Error handling (tool not found, network failures)
- Finding data model validation
- Severity mapping

#### Step 2: Integration Tests on Sample Projects (3 hours)
**Files**: `tests/security/fixtures/vulnerable_*` + `tests/security/test_integration.py`

Create sample vulnerable projects:
- SQL injection (Python)
- XSS (JavaScript)
- Path traversal (Go)
- Hardcoded secrets (any language)

Test full workflow: scan → triage → fix

#### Step 3: AI Triage Accuracy Tests (3 hours)
**File**: `tests/security/test_triage_accuracy.py`

1. Create benchmark dataset (50 findings with expert labels)
2. Run AI triage on benchmark
3. Calculate accuracy metrics (precision, recall, F1)
4. Assert accuracy >85%
5. Track accuracy over time

#### Step 4: Fix Generation Quality Tests (2 hours)
**File**: `tests/security/test_fix_generation.py`

Test fixes:
- Are syntactically valid (parse with AST)
- Actually fix the vulnerability (re-scan shows no finding)
- Don't break existing functionality (run project tests)

#### Step 5: Snapshot Tests for Report Formats (1 hour)
**File**: `tests/security/test_snapshots.py`

Use pytest-snapshot:
- Markdown report format stability
- JSON output format stability
- SARIF output format stability

####Step 6: Achieve >85% Coverage (2 hours)
Run coverage report, add tests for uncovered code paths

### Dependencies
- Security commands implemented
- Test fixtures prepared

### Estimated Effort
**Total**: 14 hours (1.75 days)
<!-- SECTION:PLAN:END -->
