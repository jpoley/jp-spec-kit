---
id: task-551
title: Update critical-rules.md with rigor rules reference
status: To Do
assignee: []
created_date: '2025-12-17 16:42'
updated_date: '2025-12-17 17:07'
labels:
  - rigor
  - documentation
  - 'workflow:Planned'
dependencies:
  - task-541
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add reference to the new rigor rules system in the critical rules documentation. All Flowspec documentation must clearly state that rigor rules are mandatory for all users.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add section in critical-rules.md linking to _rigor-rules.md
- [ ] #2 Document enforcement modes (strict by default, warn, off)
- [ ] #3 Add examples of common violations and fix commands
- [ ] #4 Emphasize these rules apply to ALL Flowspec users, not just this project
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add rigor rules section to critical-rules.md
2. Reference _rigor-rules.md location
3. Summarize key blocking rules
4. Link to ADRs for rationale
<!-- SECTION:PLAN:END -->
