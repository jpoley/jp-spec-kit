---
id: task-140
title: Add specify voice CLI command
status: Done
assignee:
  - '@backend-engineer'
created_date: '2025-11-28'
updated_date: '2025-11-29 01:05'
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
Added "specify voice" CLI command to launch voice assistant.

Implementation:
- Added voice() function to src/specify_cli/__init__.py
- Accepts --config/-c option for config file path
- Falls back to voice-config.json in current directory
- Loads and validates configuration using voice.config module
- Displays helpful error messages for missing config or API keys
- Shows configuration status on success with provider names
- Exit codes: 0 for success, 1 for errors

Verification:
- AC #1: specify voice --help displays usage with --config option ✓
- AC #2: specify voice --config path/to/config.json loads specified file ✓
- AC #3: Missing API keys displays specific error listing which keys needed ✓
- AC #4: Valid config displays "Voice assistant ready" with provider names ✓
- AC #5: Exit code 0 on success, 1 on errors ✓

Error handling:
- FileNotFoundError for missing config files
- ValueError for validation errors (missing fields, API keys)
- Generic Exception handler for unexpected errors
- All error paths provide helpful guidance
<!-- SECTION:NOTES:END -->
