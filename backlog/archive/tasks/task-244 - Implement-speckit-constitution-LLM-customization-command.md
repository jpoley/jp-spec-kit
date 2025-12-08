---
id: task-244
title: 'Implement /speckit:constitution LLM customization command'
status: Done
assignee:
  - '@kinsale'
created_date: '2025-12-03 02:40'
updated_date: '2025-12-04 22:40'
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
- [x] #1 Create .claude/commands/speckit/constitution.md slash command
- [x] #2 Command scans repo for: languages, frameworks, CI configs, test setup, linting tools
- [x] #3 Command detects existing patterns: security scanning, code review requirements, etc.
- [x] #4 Command customizes selected tier template with repo-specific findings
- [x] #5 Output includes NEEDS_VALIDATION markers on auto-generated sections
- [x] #6 Command outputs clear message: Constitution generated - please review and validate
- [x] #7 Supports --tier {light|medium|heavy} flag to override detection

- [x] #8 Command outputs validation checklist after generation
- [x] #9 Command supports --tier override flag
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented via PR #478 (merged).

- AC #1: `.claude/commands/speckit/constitution.md` slash command exists
- AC #2-3: Command scans repo for languages, frameworks, CI configs, test setup, linting, security tools
- AC #4: Customizes tier template with repo-specific findings
- AC #5: Output includes NEEDS_VALIDATION markers
- AC #6: Outputs clear message with validation checklist
- AC #7-9: Supports `--tier {light|medium|heavy}` flag with auto-detection fallback

Implementation at: `templates/commands/speckit/constitution.md` (667 lines)
<!-- SECTION:NOTES:END -->
