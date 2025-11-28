---
id: task-088
title: Phase 0 - Task Context Loader for AC Validation

status: In Progress
assignee:
  - '@claude-agent-3'
created_date: '2025-11-28 15:56'
updated_date: '2025-11-28 18:14'
labels:
  - validate-enhancement
  - phase-0
  - backend
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the foundational task context loading capability for the enhanced /jpspec:validate command. This phase is responsible for loading a backlog task by ID, parsing its acceptance criteria into a structured format, and determining the validation approach (automated vs manual) for each AC based on naming conventions and task metadata.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Given a task ID, the loader retrieves task details via `backlog task <id> --plain` and parses all fields (title, description, status, ACs)
- [x] #2 Acceptance criteria are extracted into a structured list with index, text, and checked status for each AC
- [x] #3 The loader identifies related code files by searching for references in task description/notes (e.g., file paths, module names)
- [x] #4 The loader identifies related test files by matching patterns like `test_<feature>.py` or `<feature>.test.ts` based on task context
- [x] #5 For each AC, the loader determines validation approach: 'automated' (has matching test), 'manual' (requires human judgment), or 'hybrid'
- [x] #6 If no task ID is provided, the loader finds the current in-progress task via `backlog task list -s "In Progress" --plain`
- [x] #7 Returns a TaskContext object with: task_id, title, description, acceptance_criteria[], related_files[], validation_plan[]
- [x] #8 Handles error cases: task not found, no in-progress task, invalid task ID format
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create dataclasses for TaskContext and AcceptanceCriterion using Python dataclasses pattern from existing code
2. Implement load_task_context() to invoke backlog CLI and parse --plain output
3. Implement parse_acceptance_criteria() to extract AC list from markdown with regex patterns
4. Implement find_related_files() to search for file references in description/notes
5. Implement determine_validation_approach() based on test file existence
6. Add comprehensive error handling for all edge cases
7. Create tests following existing pytest patterns with fixtures
8. Run tests and linting to ensure quality
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented TaskContext loader with comprehensive AC parsing and validation approach determination.

Key features:
- TaskContext and AcceptanceCriterion dataclasses with all required fields
- load_task_context() integrates with backlog CLI via subprocess
- Parses task output including title, status, priority, labels, description, ACs, and notes
- Automatically discovers related code and test files from task description/notes
- Determines validation approach (automated/manual/hybrid) based on AC keywords and test availability
- Handles all error cases: task not found, no in-progress task, invalid ID format
- 45 comprehensive tests covering all functionality, edge cases, and integration
- All tests pass with 100% success rate
- Code formatted and linted with ruff
<!-- SECTION:NOTES:END -->
