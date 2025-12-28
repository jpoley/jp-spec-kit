---
id: task-544
title: 'Integrate rigor rules into /flow:validate'
status: Done
assignee: []
created_date: '2025-12-17 16:40'
updated_date: '2025-12-22 21:54'
labels:
  - rigor
  - validate
  - command
  - 'workflow:Planned'
dependencies:
  - task-541
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add rigor rules include to the validate command with rebase and CI checks. This command is the gateway to PR submission and must enforce all validation-phase rules.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add {{INCLUDE:_rigor-rules.md}} reference to validate.md template
- [ ] #2 Enforce rebase from main (zero merge conflicts) before PR creation
- [ ] #3 Verify all CI checks will pass before allowing PR suggestion
- [ ] #4 Add DCO sign-off verification step
- [ ] #5 Add Copilot comment handling guidance for iterative PRs (-v2, -v3)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add {{INCLUDE:_rigor-rules.md}} to validate.md template
2. Add rebase check (zero commits behind main)
3. Add CI pass verification step
4. Add DCO sign-off verification
5. Add Copilot comment handling guidance for -v2, -v3 branches
6. Test validation workflow
<!-- SECTION:PLAN:END -->
