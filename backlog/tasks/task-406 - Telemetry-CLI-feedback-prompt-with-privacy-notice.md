---
id: task-406
title: 'Telemetry: CLI feedback prompt with privacy notice'
status: To Do
assignee:
  - '@pm-planner'
created_date: '2025-12-10 00:11'
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
- [ ] #1 Interactive prompt during /speckit:init with telemetry opt-in question
- [ ] #2 Privacy notice displays: local-only storage, PII hashing, opt-out anytime, view/delete data
- [ ] #3 Non-interactive mode via --telemetry-enabled flag
- [ ] #4 Prompt skipped if telemetry already configured
- [ ] #5 Consent stored in specflow_workflow.yml with timestamp
- [ ] #6 Integration tests for interactive and non-interactive modes
<!-- AC:END -->
