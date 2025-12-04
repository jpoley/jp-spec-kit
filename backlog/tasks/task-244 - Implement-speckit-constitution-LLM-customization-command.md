---
id: task-244
title: 'Implement /speckit:constitution LLM customization command'
status: To Do
assignee:
  - '@kinsale'
created_date: '2025-12-03 02:40'
updated_date: '2025-12-04 17:07'
labels:
  - constitution-cleanup
  - 'workflow:Specified'
dependencies:
  - task-241
  - task-243
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create slash command that analyzes repo and customizes constitution template with repo-specific details
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create .claude/commands/speckit/constitution.md slash command
- [ ] #2 Command scans repo for: languages, frameworks, CI configs, test setup, linting tools
- [ ] #3 Command detects existing patterns: security scanning, code review requirements, etc.
- [ ] #4 Command customizes selected tier template with repo-specific findings
- [ ] #5 Output includes NEEDS_VALIDATION markers on auto-generated sections
- [ ] #6 Command outputs clear message: Constitution generated - please review and validate
- [ ] #7 Supports --tier {light|medium|heavy} flag to override detection

- [ ] #8 Command outputs validation checklist after generation
- [ ] #9 Command supports --tier override flag
<!-- AC:END -->
