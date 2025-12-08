---
id: task-259
title: Create dev-setup validation GitHub Action
status: Done
assignee: []
created_date: '2025-12-03 13:54'
updated_date: '2025-12-04 02:42'
labels:
  - infrastructure
  - cicd
  - dogfood
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GitHub Actions workflow to validate dogfood consistency on every PR. Ensures .claude/commands/ only contains symlinks and prevents content drift.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Workflow file created at .github/workflows/dogfood-validation.yml
- [x] #2 Validates no non-symlink .md files exist in .claude/commands/
- [x] #3 Validates all symlinks resolve to existing templates
- [x] #4 Runs dogfood command and verifies output structure
- [x] #5 Executes test suite (test_dogfood_*.py)
- [x] #6 Provides clear error messages on failure
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation completed in PR #397:
https://github.com/jpoley/jp-spec-kit/pull/397

Created .github/workflows/dev-setup-validation.yml with:

1. Symlink structure validation (bash commands)
   - R1: All .md files must be symlinks
   - R2: All symlinks must resolve
   - R3: All symlinks point to templates/commands/
   - R7: Subdirectory structure validation

2. dev-setup command execution and verification
   - Runs: uv run specify dev-setup --force
   - Verifies jpspec/ and speckit/ directories created
   - Counts and verifies symlinks were created

3. Test suite execution
   - Runs: uv run pytest tests/test_dev_setup_*.py -v
   - Full validation of all rules

4. Clear error messages
   - Each validation step has descriptive output
   - Failures provide fix instructions: "uv run specify dev-setup --force"

Note: Implemented as "dev-setup-validation.yml" (not "dogfood-validation.yml")
to match the actual command name and test file naming convention.
The tests are test_dev_setup_*.py (not test_dogfood_*.py).
<!-- SECTION:NOTES:END -->
