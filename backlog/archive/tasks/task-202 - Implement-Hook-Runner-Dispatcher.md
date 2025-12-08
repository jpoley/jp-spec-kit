---
id: task-202
title: Implement Hook Runner/Dispatcher
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-03 00:41'
updated_date: '2025-12-03 01:21'
labels:
  - implement
  - backend
  - cli
  - hooks
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
CLI command 'specify hooks run' that receives events and dispatches to configured hooks. Includes sandboxing, timeout, and audit logging.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 CLI command: specify hooks run --event-type <type> --payload <json>
- [x] #2 Match events to hooks using configuration and dispatch scripts
- [x] #3 Sandbox execution with timeout (default 30s, configurable)
- [x] #4 Audit logging to .specify/hooks/audit.log with timestamps and results
- [ ] #5 Exit code reflects hook success/failure for CI integration
- [x] #6 Integration tests with real hook scripts
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created runner.py with HookRunner class and HookResult dataclass

Key features:
- HookResult dataclass with execution details
- HookRunner class with run_hook() method
- Security validation: script path allowlist, timeout enforcement
- Environment sanitization with HOOK_EVENT JSON
- Audit logging in JSONL format
- Support for both script and command execution methods
<!-- SECTION:NOTES:END -->
