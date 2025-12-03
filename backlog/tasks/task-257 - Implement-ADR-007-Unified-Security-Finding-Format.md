---
id: task-257
title: 'Implement ADR-007: Unified Security Finding Format'
status: Done
assignee:
  - '@platform-engineer'
created_date: '2025-12-03 02:31'
updated_date: '2025-12-03 02:47'
labels:
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Define canonical data model for security findings with SARIF compatibility. See docs/adr/ADR-007-unified-security-finding-format.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define Finding and Location dataclasses in src/specify_cli/security/models.py
- [x] #2 Implement fingerprinting for deduplication
- [x] #3 Implement finding merging (when multiple scanners find same issue)
- [x] #4 Implement JSON serialization (to_dict/from_dict)
- [x] #5 Implement SARIFExporter for SARIF 2.1.0 export
- [x] #6 Implement MarkdownExporter for human-readable reports
- [x] #7 Validate SARIF export against official schema
- [x] #8 Unit tests for all export formats
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented Unified Finding Format (UFFormat) per ADR-007:

## Implementation Summary

### Core Data Model
- Created `src/specify_cli/security/models.py` with Finding, Location, Severity, and Confidence classes
- Implemented fingerprinting using SHA256 hash of file + line range + CWE/title
- Implemented finding merging with severity escalation and confidence boosting
- Full JSON serialization with to_dict/from_dict methods

### Export Formats
- **SARIFExporter**: SARIF 2.1.0 compliant export for GitHub Code Scanning integration
  - Groups findings by scanner (one run per tool)
  - Includes tool metadata, rules, and results
  - Maps severity levels to SARIF levels (error/warning/note)
- **MarkdownExporter**: Human-readable reports with severity grouping and emojis
- **JSONExporter**: Simple JSON export with pretty/compact formatting options

### Testing
- Created `tests/test_security_models.py` with 27 tests covering:
  - Location and Finding dataclass creation
  - Fingerprinting consistency and uniqueness
  - Finding merging logic
  - JSON serialization roundtrip
  - SARIF conversion
  - All export formats
- Created `tests/test_sarif_validation.py` with 9 tests validating:
  - SARIF 2.1.0 document structure
  - Required fields per specification
  - Valid SARIF level values
  - Multi-scanner support

### Code Quality
- All 36 tests pass
- Ruff linting: All checks passed
- Type hints on all public APIs
- Comprehensive docstrings with examples
- No unused imports or code

## Files Created

```
src/specify_cli/security/
├── __init__.py           # Module exports
├── models.py             # Core Finding/Location models
└── exporters/
    ├── __init__.py       # Exporter exports
    ├── base.py           # BaseExporter abstract class
    ├── json.py           # JSONExporter
    ├── sarif.py          # SARIFExporter (SARIF 2.1.0)
    └── markdown.py       # MarkdownExporter

tests/
├── test_security_models.py      # Core model tests (27 tests)
└── test_sarif_validation.py     # SARIF spec validation (9 tests)
```

## Next Steps

The UFFormat is now ready for integration with scanner adapters. Future work:
1. Create scanner adapters (Semgrep, CodeQL, Trivy) that convert scanner output to UFFormat
2. Implement triage engine that operates on UFFormat findings
3. Create MCP server endpoints that serve UFFormat findings
4. Add CLI commands for security scanning workflows
<!-- SECTION:NOTES:END -->
