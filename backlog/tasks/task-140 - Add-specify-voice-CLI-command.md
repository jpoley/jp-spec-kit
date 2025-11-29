---
id: task-140
title: Add specify voice CLI command
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-11-28'
updated_date: '2025-11-29 00:28'
labels:
  - implement
  - voice
  - foundational
  - cli
  - phase2
dependencies:
  - task-139
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add 'specify voice' subcommand to src/specify_cli/cli.py that loads configuration, validates API keys, and launches voice bot. Initial implementation should validate config and print readiness status. Reference: docs/research/pipecat-voice-integration-summary.md Section 1.3 Initial Tasks
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Command `specify voice --help` displays usage information with --config option
- [x] #2 Command `specify voice --config path/to/config.json` loads and validates specified config file
- [x] #3 Missing API keys displays error listing which specific keys are missing
- [x] #4 Valid configuration displays "Voice assistant ready" status with provider names
- [x] #5 Exit code 0 on success, exit code 1 on configuration errors
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added specify voice CLI command with configuration loading and validation.

Changes:
- Added voice command to src/specify_cli/__init__.py
- Loads configuration from JSON file (--config option)
- Validates all required fields and API keys
- Displays clear error messages for missing API keys
- Shows readiness status with provider names
- Returns exit code 0 on success, 1 on errors
- Comprehensive help text with examples
- All code passes ruff linting and formatting

Command usage:
  specify voice --help
  specify voice --config /path/to/config.json
<!-- SECTION:NOTES:END -->
