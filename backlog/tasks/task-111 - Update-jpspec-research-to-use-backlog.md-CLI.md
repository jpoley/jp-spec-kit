---
id: task-111
title: 'Update /jpspec:research to use backlog.md CLI'
status: Done
assignee:
  - '@claude-agent'
created_date: '2025-11-28 16:56'
updated_date: '2025-11-29 05:16'
labels:
  - jpspec
  - backlog-integration
  - research
  - P1
dependencies:
  - task-107
  - task-108
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modify the research.md command to integrate backlog.md task management. Researcher and Business Validator agents must create research tasks and document findings in backlog.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Command discovers existing research-related backlog tasks
- [x] #2 Both agents receive shared backlog instructions from _backlog-instructions.md
- [x] #3 Researcher creates research spike tasks in backlog
- [x] #4 Business Validator creates validation tasks in backlog
- [x] #5 Agents add research findings as implementation notes to tasks
- [x] #6 Test: Run /jpspec:research and verify research tasks created with findings
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented /jpspec:research backlog.md integration.

## Changes

### research.md Updates
- Added {{INCLUDE:.claude/commands/jpspec/_backlog-instructions.md}} directive to both Phase 1 (Researcher) and Phase 2 (Business Validator) agent prompts
- Used <!--BACKLOG-INSTRUCTIONS-START--> and <!--BACKLOG-INSTRUCTIONS-END--> markers consistent with plan.md pattern
- Maintains existing specialized research/validation task creation instructions alongside shared instructions

### Test Coverage (AC#6)
- Added TestSharedBacklogInstructions test class with 5 new tests:
  - test_backlog_instructions_file_exists
  - test_researcher_includes_shared_backlog_instructions
  - test_business_validator_includes_shared_backlog_instructions
  - test_both_agents_have_include_before_context
  - test_shared_instructions_include_count

## Verification
- All 37 tests in test_jpspec_research_backlog.py pass
- Ruff check passes on modified files

## Pre-existing Functionality Verified
- AC#1: Pre-execution search discovers research tasks (lines 19-26 of research.md)
- AC#3: Researcher creates research spike tasks with proper format (lines 86-95)
- AC#4: Business Validator creates validation tasks with proper format (lines 227-238)
- AC#5: Both agents add findings as implementation notes (lines 117-148, 260-305)
<!-- SECTION:NOTES:END -->
