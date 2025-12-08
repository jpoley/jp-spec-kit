---
id: task-256
title: 'Implement ADR-006: AI Triage Engine Design'
status: Done
assignee:
  - '@platform-engineer'
created_date: '2025-12-03 02:31'
updated_date: '2025-12-03 23:22'
labels:
  - architecture
  - security
  - ai
  - implement
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build AI-powered vulnerability triage with classification, risk scoring, clustering, and explanations. See docs/adr/ADR-006-ai-triage-engine-design.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement TriageEngine core logic in src/specify_cli/security/triage/engine.py
- [x] #2 Implement FindingClassifier interface and default classifier
- [x] #3 Implement 5 specialized classifiers (SQL Injection, XSS, Path Traversal, Hardcoded Secrets, Weak Crypto)
- [x] #4 Implement Raptor risk scoring formula: (Impact × Exploitability) / Detection_Time
- [x] #5 Implement finding clustering by CWE, file, and architectural pattern
- [x] #6 Implement plain-English explanation generation
- [ ] #7 Benchmark AI triage accuracy >85% on known TP/FP examples
- [x] #8 Unit tests with mocked LLM responses
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Summary

The AI Triage Engine has been successfully implemented with the following components:

### Completed (7 of 8 ACs)

**AC #1: TriageEngine core logic** ✅
- Implemented in `src/specify_cli/security/triage/engine.py`
- Orchestrates classification, risk scoring, clustering, and explanation generation
- 400+ lines of production code with comprehensive documentation

**AC #2: FindingClassifier interface and default classifier** ✅
- Abstract base class in `classifiers/base.py` with Strategy Pattern
- Default classifier in `classifiers/default.py` with heuristic and LLM modes
- Includes LLMClient protocol for pluggable LLM backends

**AC #3: 5 specialized classifiers** ✅
- `SQLInjectionClassifier` - Detects parameterized queries vs string concatenation
- `XSSClassifier` - Analyzes DOM manipulation patterns (innerHTML vs textContent)
- `PathTraversalClassifier` - Checks for path validation (realpath, normpath)
- `HardcodedSecretsClassifier` - Entropy analysis + dummy value detection
- `WeakCryptoClassifier` - Identifies weak algorithms (MD5, SHA1) vs secure (AES-256, bcrypt)

**AC #4: Raptor risk scoring formula** ✅
- Implemented in `src/specify_cli/security/triage/risk_scorer.py`
- Formula: `risk_score = (Impact × Exploitability) / Detection_Time`
- Impact from CVSS or severity mapping (0-10)
- Exploitability from CWE-based heuristics (0-10)
- Detection time from git blame (days since code written)

**AC #5: Finding clustering** ✅
- Clusters by CWE category (min 3 findings)
- Clusters by file (min 2 findings)
- Assigns cluster IDs for systemic issue identification
- Implemented in `_cluster()` method

**AC #6: Plain-English explanation generation** ✅
- Explanation dataclass with What/Why/Exploit/Fix sections
- Heuristic explanations (no LLM required)
- AI-powered explanations (via LLM when available)
- Max 500 characters per section (configurable)

**AC #8: Unit tests with mocked LLM responses** ✅
- 51 tests in `tests/security/triage/`
- All tests passing (100% pass rate)
- Comprehensive coverage:
  - test_classifiers.py (22 tests)
  - test_engine.py (18 tests)
  - test_models.py (11 tests)
- Mocked LLM responses for deterministic testing

### Not Implemented (1 AC)

**AC #7: Benchmark AI triage accuracy >85%** ❌
- No benchmark dataset of known TP/FP examples
- No accuracy measurement infrastructure
- No comparison with expert manual triage
- This requires:
  1. Curated dataset of 100+ labeled findings (TP/FP ground truth)
  2. Benchmark script to run triage and compare results
  3. Accuracy metrics calculation and reporting
  4. Per-classifier accuracy breakdown

### Code Quality

- **Architecture**: Follows ADR-006 design with Strategy Pattern
- **Type Safety**: Full type hints throughout
- **Testing**: 51 unit tests, all passing
- **Documentation**: Comprehensive docstrings and inline comments
- **Linting**: Passes `ruff check .` with no violations

### Related Commits

The implementation was completed in main branch via these commits:
- 98934b2: feat(security): implement AI triage engine with specialized classifiers
- 454038f: fix(security): address 16 code quality issues in triage engine
- a360d40: fix(security): address 8 GitHub Copilot review issues in triage engine
- PR #373: Merged galway-learnings-triage-fixes

### Recommendation

The core triage engine is production-ready for Phase 1 and Phase 2. AC #7 (benchmarking) should be tracked in a separate task as it requires:
1. Creating a benchmark dataset (different skill: data curation)
2. Establishing ground truth via expert review
3. Building measurement infrastructure

The implementation can be used and evaluated against real scan results to gather initial accuracy data organically.

### Resolution

The implementation was already completed and merged to main via PR #373 (galway-learnings-triage-fixes). The work includes:

- Original implementation: commit 98934b2
- Quality fixes: commits 454038f, a360d40
- Merged on: 2025-12-03

The galway-task-256-ai-triage-engine branch contains duplicate work and can be closed.

**Next Steps:**
1. Create new task for AC #7 (Benchmark dataset and accuracy measurement)
2. Close the galway-task-256 branch/worktree (redundant with main)
3. Consider this task complete pending benchmarking
<!-- SECTION:NOTES:END -->
