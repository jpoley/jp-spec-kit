---
id: task-294
title: Constitution Enforcement Integration Tests
status: To Do
assignee: []
created_date: '2025-12-04 16:22'
updated_date: '2025-12-04 16:31'
labels:
  - constitution-cleanup
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Verify /flowspec commands enforce constitution checks correctly by tier
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Test light tier: /flow:specify warns but proceeds
- [ ] #2 Test medium tier: /flow:specify prompts for confirmation
- [ ] #3 Test heavy tier: /flow:specify blocks execution
- [ ] #4 Test --skip-validation flag bypasses checks
- [ ] #5 Test unvalidated constitution triggers validation warning
<!-- AC:END -->
