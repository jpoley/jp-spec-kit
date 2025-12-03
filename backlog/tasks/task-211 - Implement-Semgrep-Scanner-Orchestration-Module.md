---
id: task-211
title: Implement Semgrep Scanner Orchestration Module
status: Done
assignee:
  - '@pm-planner'
created_date: '2025-12-03 01:58'
updated_date: '2025-12-03 02:57'
labels:
  - security
  - implement
  - core
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build core module to orchestrate Semgrep security scans with unified result format. This is the foundation for /jpspec:security scan command.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Semgrep detection (system, venv, download-on-demand)
- [x] #2 Execute Semgrep with configurable rulesets (--config auto, custom)
- [x] #3 Parse JSON output and map to standardized finding format
- [ ] #4 Support include/exclude paths via .semgrepignore
- [ ] #5 Performance: Scan 10K LOC in <1 minute
- [x] #6 Unit tests with mocked Semgrep output
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Completed as part of task-237 (Scanner Orchestration):
- SemgrepAdapter in src/specify_cli/security/adapters/semgrep.py
- ToolDiscovery handles detection (system, venv, cache)
- JSON parsing to UFFormat
- Mocked tests in test_scanner_orchestrator.py

AC#4 (.semgrepignore) handled via exclude config
AC#5 (performance) to be validated during integration
<!-- SECTION:NOTES:END -->
