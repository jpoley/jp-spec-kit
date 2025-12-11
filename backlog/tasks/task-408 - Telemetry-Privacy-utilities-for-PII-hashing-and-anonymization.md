---
id: task-408
title: 'Telemetry: Privacy utilities for PII hashing and anonymization'
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-12-10 00:11'
labels:
  - implement
  - backend
  - telemetry
  - security
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create privacy utilities for hashing potentially identifying information. Ensures no PII is stored in telemetry without user consent.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 hash_pii() function using SHA-256 with project-specific salt
- [ ] #2 anonymize_path() function for sanitizing file paths (removes username, absolute paths)
- [ ] #3 anonymize_project_name() function for project identifiers
- [ ] #4 Salt generation and storage in .flowspec/telemetry.salt (gitignored)
- [ ] #5 Deterministic hashing - same input produces same hash within project
- [ ] #6 Unit tests for hash_pii, anonymize_path, anonymize_project_name, salt generation
<!-- AC:END -->
