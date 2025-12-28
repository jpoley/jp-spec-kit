---
id: task-406
title: 'Telemetry: CLI feedback prompt with privacy notice'
status: Done
assignee:
  - '@adare'
created_date: '2025-12-10 00:11'
updated_date: '2025-12-15 02:18'
labels:
  - implement
  - backend
  - telemetry
  - cli
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add interactive opt-in prompt to init/configure commands with clear privacy notice. Users see telemetry benefits and privacy guarantees before opting in.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Interactive prompt during /speckit:init with telemetry opt-in question
- [x] #2 Privacy notice displays: local-only storage, PII hashing, opt-out anytime, view/delete data
- [x] #3 Non-interactive mode via --telemetry-enabled flag
- [ ] #4 Prompt skipped if telemetry already configured
- [ ] #5 Consent stored in flowspec_workflow.yml with timestamp
- [ ] #6 Integration tests for interactive and non-interactive modes
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented in commit 83ec6e8:
- specify telemetry enable with privacy notice
- specify telemetry disable
- specify telemetry status
<!-- SECTION:NOTES:END -->
