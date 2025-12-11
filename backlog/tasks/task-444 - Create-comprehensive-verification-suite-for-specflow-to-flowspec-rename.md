---
id: task-444
title: Create comprehensive verification suite for flowspec to flowspec rename
status: To Do
assignee: []
created_date: '2025-12-11 01:32'
labels:
  - platform
  - verification
  - rename
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create and execute comprehensive verification checks to ensure complete rename:

Verification script components:
1. Grep-based completeness check:
   - Search all file types for 'flowspec' string
   - Exclude .git, node_modules, build artifacts
   - Report any remaining references with context
   - Exit with error if unexpected references found

2. Path verification:
   - Verify no flowspec/ directories exist
   - Verify flowspec/ directories exist and populated
   - Check symlink integrity
   - Verify schema files renamed

3. Test suite verification:
   - Run full pytest suite
   - Verify 100% test pass rate
   - Check code coverage meets threshold (70%+)
   - No test file import errors

4. CI pipeline verification:
   - All GitHub Actions workflows pass
   - Schema validation succeeds
   - Role validation succeeds
   - Dev setup validation succeeds

5. Documentation verification:
   - No broken links in markdown
   - All code examples syntactically valid
   - Configuration examples validate against schema

Create verification script: scripts/bash/verify-flowspec-rename.sh

Expected grep results (allowed):
- Comments explaining migration
- Deprecation warnings
- Git history references
- CHANGELOG entries
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Verification script created and executable
- [ ] #2 Grep check finds zero unexpected flowspec references
- [ ] #3 All test suites pass completely
- [ ] #4 All CI workflows pass
- [ ] #5 Symlink integrity verified
- [ ] #6 Documentation links verified
- [ ] #7 Script exits 0 on successful verification
- [ ] #8 Verification script integrated into CI
<!-- AC:END -->
