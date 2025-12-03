---
id: task-215
title: 'Implement /jpspec:security CLI Commands'
status: Done
assignee:
  - '@pm-planner'
created_date: '2025-12-03 01:58'
updated_date: '2025-12-03 03:04'
labels:
  - 'workflow:Planned'
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build CLI interface for all four security subcommands (scan, triage, fix, audit) with argument parsing and workflow orchestration.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Implement /jpspec:security scan with --tool, --config, --fail-on flags
- [ ] #2 Implement /jpspec:security triage with --interactive, --min-severity flags
- [ ] #3 Implement /jpspec:security fix with --apply, --dry-run, --finding flags
- [ ] #4 Implement /jpspec:security audit with --format, --compliance flags
- [ ] #5 Exit codes: 0 (clean), 1 (findings), 2 (error)
- [ ] #6 Progress indicators for long-running scans
<!-- AC:END -->
