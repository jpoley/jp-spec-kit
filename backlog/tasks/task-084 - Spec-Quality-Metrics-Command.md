---
id: task-084
title: Spec Quality Metrics Command
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-11-27 21:54'
updated_date: '2025-12-04 17:07'
labels:
  - specify-cli
  - feature
  - quality
  - 'workflow:Specified'
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add 'specify quality' command for automated spec assessment. Measures: Completeness (required sections present), Clarity (vague terms, passive voice, measurable criteria), Traceability (requirements → plan → tasks linkage), Constitutional compliance, Ambiguity markers. Output: Score 0-100 with recommendations. Reduces subjective review time by 50%+.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Design quality scoring algorithm with dimensions
- [ ] #2 Implement completeness assessment (required sections)
- [ ] #3 Implement clarity assessment (vague terms, specificity)
- [ ] #4 Implement traceability assessment (story → plan → task)
- [ ] #5 Implement constitutional compliance check
- [ ] #6 Implement ambiguity marker detection
- [ ] #7 Create rich output format (table with scores + recommendations)
- [ ] #8 Add customizable thresholds via .specify/quality-config.json
- [x] #9 Integrate with pre-implementation gates
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
AC #9: Implemented specify gate command with exit codes 0/1/2. Integrated into /jpspec:implement as Phase 0 (mandatory quality gate before implementation).
<!-- SECTION:NOTES:END -->
