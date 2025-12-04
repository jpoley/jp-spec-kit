---
id: task-275
title: Update init command for subdirectory structure
status: Done
assignee:
  - '@cli-engineer'
created_date: '2025-12-03 14:01'
updated_date: '2025-12-03 14:19'
labels:
  - cli
  - init
  - implementation
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modify specify init to create subdirectory structure for commands instead of flat files
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Update command copying logic to use subdirectories (jpspec/, speckit/)
- [ ] #2 Ensure subdirectories are created before copying files
- [ ] #3 Copy _backlog-instructions.md partial along with commands
- [ ] #4 Test init creates correct subdirectory structure
- [ ] #5 Verify init output matches dogfood structure (files vs symlinks)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated create-release-packages.sh to generate subdirectory structure for commands. Init command extracts ZIPs as-is, so no changes needed there.
<!-- SECTION:NOTES:END -->
