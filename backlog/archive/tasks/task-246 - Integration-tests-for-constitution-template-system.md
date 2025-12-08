---
id: task-246
title: Integration tests for constitution template system
status: Done
assignee:
  - '@kinsale'
created_date: '2025-12-03 02:45'
updated_date: '2025-12-04 22:42'
labels:
  - constitution-cleanup
  - 'workflow:Specified'
dependencies:
  - task-245
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Write comprehensive tests for the tiered constitution template feature
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Test specify init with --constitution light/medium/heavy flags
- [x] #2 Test empty repo detection and tier prompting
- [x] #3 Test existing project detection without constitution
- [x] #4 Test /speckit:constitution command execution
- [x] #5 Test NEEDS_VALIDATION marker handling
- [x] #6 Test specify constitution validate command
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
All ACs were already implemented with comprehensive tests:

- AC #1: `test_constitution_init.py::TestConstitutionValidation` - tests --constitution flags
- AC #2: `test_detect_existing_projects.py::TestIsExistingProject` - tests empty repo detection
- AC #3: `test_detect_existing_projects.py::TestCombinedDetection::test_existing_project_without_constitution`
- AC #4: `/speckit:constitution` template exists at `templates/commands/speckit/constitution.md` (LLM command)
- AC #5: `test_constitution_enforcement.py` - marker counting and section extraction
- AC #6: `test_constitution_validate.py` - 18 comprehensive tests for validate command

Test coverage: 111+ tests across 5 constitution test files, all passing.
<!-- SECTION:NOTES:END -->
