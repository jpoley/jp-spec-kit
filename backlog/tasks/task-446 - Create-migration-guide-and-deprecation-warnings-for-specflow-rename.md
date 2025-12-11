---
id: task-446
title: Create migration guide and deprecation warnings for flowspec rename
status: To Do
assignee: []
created_date: '2025-12-11 01:32'
labels:
  - documentation
  - deprecation
  - rename
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create comprehensive migration guide and implement deprecation warnings:

Migration guide (docs/guides/migration-flowspec-to-flowspec.md):
1. Overview: Why the rename happened
2. Quick migration checklist
3. File renames required
4. Command updates: /flow: → /flow:
5. Configuration updates
6. Breaking changes summary
7. Rollback procedure if needed
8. FAQ and troubleshooting

Deprecation implementation:
1. Update generate-deprecated-aliases.sh:
   - Add /flow: → /flow: mappings
   - Generate deprecation stub files
   
2. Create deprecation warning system:
   - Detect old /flow: usage
   - Display migration warning
   - Provide correct /flow: command
   - Set removal date (12 months from release)

CHANGELOG entry:
- Add BREAKING CHANGE section
- Document all renamed files
- Command mapping table
- Migration steps
- Version compatibility notes

Release notes template:
- Highlight major rename
- Link to migration guide
- Provide support contact
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Migration guide created and comprehensive
- [ ] #2 Deprecation warnings implemented for /flow: commands
- [ ] #3 generate-deprecated-aliases.sh includes flowspec mappings
- [ ] #4 CHANGELOG.md updated with breaking change section
- [ ] #5 Release notes template created
- [ ] #6 FAQ addresses common migration issues
- [ ] #7 Rollback procedure documented and tested
<!-- AC:END -->
