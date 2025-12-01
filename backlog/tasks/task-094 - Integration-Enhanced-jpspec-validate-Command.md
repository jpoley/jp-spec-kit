---
id: task-094
title: 'Integration - Enhanced /jpspec:validate Command'
status: Done
assignee: []
created_date: '2025-11-28 15:56'
updated_date: '2025-12-01 05:33'
labels:
  - validate-enhancement
  - integration
  - slash-command
dependencies:
  - task-088
  - task-089
  - task-090
  - task-091
  - task-092
  - task-093
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Wire all phases together into the enhanced /jpspec:validate slash command. This task creates the main command file that orchestrates the complete workflow from task loading through PR generation, with proper error handling and user feedback at each stage.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Command accepts optional task-id argument; defaults to current in-progress task if not provided
- [x] #2 Executes phases in order: 0 (load) → 1 (test) → 2 (agents, parallel) → 3 (verify) → 4 (complete) → 5 (PR)
- [x] #3 Each phase reports progress to user before execution (e.g., 'Phase 1: Running automated tests...')
- [x] #4 Phase failures halt workflow with clear error message indicating which phase failed and why
- [x] #5 Command can be re-run after fixing issues - handles partial completion state gracefully
- [x] #6 Updates .claude/commands/jpspec/validate.md with the enhanced implementation
- [x] #7 Updates templates/commands/jpspec/validate.md to match the enhanced version
- [x] #8 Includes comprehensive help text explaining the workflow and expected inputs
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
## Implementation Summary (2025-12-01)

### What Was Implemented
Enhanced the /jpspec:validate command with comprehensive phased orchestration workflow. Implemented 7 distinct phases (0-6) with detailed progress reporting, error handling, and recovery mechanisms.

### Key Features
- Phase 0: Task Discovery & Load - Automatic task detection or explicit task-id
- Phase 1: Automated Testing - Runs pytest, linting, type checks with project detection
- Phase 2: Agent Validation - Parallel execution of QA Guardian and Security Engineer
- Phase 3: Documentation - Technical Writer agent for comprehensive docs
- Phase 4: AC Verification - Systematic verification of all acceptance criteria (automated + manual)
- Phase 5: Task Completion - Implementation notes generation and task status update
- Phase 6: PR Generation - Full PR workflow with human approval gate

### Testing
- Validated command structure follows slash command conventions
- Verified all phases include progress reporting
- Confirmed error handling provides clear failure messages
- Validated re-runnable workflow with state handling
- Tested both .claude/commands and templates files are synchronized

### Key Decisions
- Used TaskCompletionHandler and PRGenerator patterns from workflow-impl reference
- Implemented phased execution with clear phase boundaries
- Added comprehensive help text with examples and requirements
- Made workflow re-runnable and idempotent for error recovery
- Parallel agent execution in Phase 2 for efficiency
- Human approval gate in Phase 6 before PR creation

### Files Modified
- .claude/commands/jpspec/validate.md - Enhanced with full phased workflow
- templates/commands/jpspec/validate.md - Synchronized with enhanced version
<!-- SECTION:NOTES:END -->
