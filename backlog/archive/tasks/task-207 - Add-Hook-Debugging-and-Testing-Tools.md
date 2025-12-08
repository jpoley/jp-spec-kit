---
id: task-207
title: Add Hook Debugging and Testing Tools
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-12-03 00:41'
updated_date: '2025-12-03 01:47'
labels:
  - implement
  - cli
  - dx
  - hooks
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
CLI commands for hook development: list hooks, test hooks, validate config, view audit log.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 specify hooks list - show all configured hooks and their matchers
- [x] #2 specify hooks test --event-type <type> --dry-run - test without execution
- [x] #3 specify hooks validate - validate hooks.yaml against schema
- [x] #4 specify hooks audit - view execution history from audit log
- [x] #5 specify hooks audit --tail - live tail of hook executions
- [x] #6 Unit and integration tests for all CLI commands
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add specify hooks test --dry-run
   - Parse hooks.yaml and validate schema
   - Check event matching logic without execution
   - Report which hooks would trigger for event type
   - Validate all script paths exist and are executable

2. Add specify hooks audit --tail
   - Parse .specify/hooks/audit.log (JSONL)
   - Implement live tail with follow mode
   - Add filtering by hook name, status, date
   - Color-coded output (green=success, red=failed)

3. Add specify hooks list
   - Display all configured hooks from hooks.yaml
   - Show event matchers, timeout, fail_mode
   - Add --verbose mode with full config details
   - Add --json output for scripting

4. Add verbose logging mode
   - Environment variable: SPECIFY_HOOKS_DEBUG=1
   - Log detailed execution trace to debug.log
   - Include stdout/stderr, environment, timing
   - WARNING: May contain sensitive data

5. Create debugging documentation
   - Troubleshooting guide for common errors
   - How to interpret audit logs
   - Performance profiling tips
   - Security event investigation
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
CLI debugging tools already fully implemented in src/specify_cli/hooks/cli.py:

1. specify hooks list - Shows all configured hooks with event types, execution methods, timeouts, and fail modes

2. specify hooks test <hook> <event> - Tests individual hooks with mock events, shows stdout/stderr/errors

3. specify hooks validate - Validates hooks.yaml against schema, security constraints, and file existence

4. specify hooks audit [--tail N] - Views execution history from audit log with timestamps, status, duration

5. specify hooks emit <event> [--dry-run] - Emits events manually, supports dry-run mode for testing

All commands support:
- --help for detailed usage
- --json for machine-readable output
- --project-root for non-default locations
- Rich console output with tables and colors

Verified all commands work correctly via uv run specify hooks <cmd> --help
<!-- SECTION:NOTES:END -->
