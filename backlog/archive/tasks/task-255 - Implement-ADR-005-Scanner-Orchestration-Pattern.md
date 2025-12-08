---
id: task-255
title: 'Implement ADR-005: Scanner Orchestration Pattern'
status: Done
assignee:
  - '@platform-engineer'
created_date: '2025-12-03 02:31'
updated_date: '2025-12-03 02:56'
labels:
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement pluggable scanner orchestrator with adapters for Semgrep, CodeQL, and Trivy. See docs/adr/ADR-005-scanner-orchestration-pattern.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define ScannerAdapter interface in src/specify_cli/security/adapters/base.py
- [x] #2 Implement ScannerOrchestrator in src/specify_cli/security/orchestrator.py
- [x] #3 Implement SemgrepAdapter (MVP scanner)
- [x] #4 Implement tool discovery chain (system → venv → download)
- [x] #5 Implement parallel scanner execution
- [x] #6 Implement fingerprint-based deduplication
- [x] #7 Unit tests with mocked scanner outputs
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Scanner orchestration pattern implemented successfully per ADR-005.

Implementation Components:
- ScannerAdapter interface (base.py) with abstract methods for name, version, is_available, scan, get_install_instructions
- ToolDiscovery class (discovery.py) implementing Chain of Responsibility for finding tools in system PATH → venv → cache
- SemgrepAdapter (semgrep.py) as reference implementation with JSON output parsing to UFFormat
- ScannerOrchestrator (orchestrator.py) with parallel execution via ThreadPoolExecutor and fingerprint-based deduplication

Key Features:
1. Tool discovery chain: System PATH → project venv → ~/.specify/tools cache
2. Parallel scanner execution with graceful degradation (one fails, others continue)
3. Fingerprint-based deduplication merges findings from multiple scanners
4. Comprehensive test coverage (30 tests, all passing)
5. Full type hints and docstrings on all public APIs

Test Results:
- All 30 tests passing
- Code quality checks passed (ruff)
- Mocked scanner outputs validate end-to-end flow

Files Created:
- src/specify_cli/security/adapters/__init__.py
- src/specify_cli/security/adapters/base.py (ScannerAdapter interface)
- src/specify_cli/security/adapters/discovery.py (ToolDiscovery)
- src/specify_cli/security/adapters/semgrep.py (SemgrepAdapter)
- src/specify_cli/security/orchestrator.py (ScannerOrchestrator)
- tests/test_scanner_orchestrator.py (30 comprehensive tests)

Next Steps:
- task-256: CLI commands for /jpspec:security scan
- Future: Add CodeQL and Trivy adapters
<!-- SECTION:NOTES:END -->
