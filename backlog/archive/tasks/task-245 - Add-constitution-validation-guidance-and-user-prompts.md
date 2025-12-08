---
id: task-245
title: Add constitution validation guidance and user prompts
status: Done
assignee:
  - '@kinsale'
created_date: '2025-12-03 02:43'
updated_date: '2025-12-04 22:39'
labels:
  - constitution-cleanup
  - 'workflow:Specified'
dependencies:
  - task-244
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ensure users are clearly informed when constitution needs validation and provide guidance
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add NEEDS_VALIDATION marker format documentation
- [x] #2 Create validation checklist output after constitution generation
- [x] #3 Add specify constitution validate command to check for unvalidated sections
- [x] #4 Warn user if they try to use /jpspec commands with unvalidated constitution
- [x] #5 Document constitution validation process in docs/guides/
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
All ACs were already implemented:

- AC #1: NEEDS_VALIDATION marker format documentation exists in `docs/guides/constitution-validation.md` (lines 30-42, 81-92)
- AC #2: Validation checklist output exists in `/speckit:constitution` command template (lines 475-567)
- AC #3: `specify constitution validate` CLI command exists with tests in `tests/test_constitution_validate.py`
- AC #4: jpspec commands include `_constitution-check.md` which warns on unvalidated constitutions with tier-based enforcement (light=warn, medium=confirm, heavy=block)
- AC #5: Comprehensive validation process guide at `docs/guides/constitution-validation.md`

No code changes required - marked as Done.
<!-- SECTION:NOTES:END -->
