---
id: task-437.02
title: Create Pull Request Template for flowspec
status: Done
assignee:
  - '@adare'
created_date: '2025-12-11 03:28'
updated_date: '2025-12-15 02:18'
labels:
  - infrastructure
  - github
  - subtask
dependencies: []
parent_task_id: task-437
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a comprehensive PR template that guides both humans and AI agents.

## File to Create

### `.github/PULL_REQUEST_TEMPLATE.md`

Sections:
1. **Description** - What/Why
2. **Related Issues** - Closes/Fixes/Resolves #
3. **Type of Change** - Checkboxes (bug fix, feature, breaking, docs, refactor, tests, config, perf, style, deps, CI/CD)
4. **Conventional Commit Format** - Guidance on PR title format
5. **Testing Checklist** - Tests added, existing pass, manual testing, coverage
6. **Documentation Checklist** - README, docs, comments, API docs, CONTRIBUTING
7. **Security Checklist** - No secrets, input validation, security implications, dependency scan, auth review, error messages
8. **Breaking Changes** - Yes/No with description
9. **Final Checklist** - Code style, self-review, comments, no warnings, tests, PR title format

## Key Insight
This template works for both human contributors AND AI coding agents (like Claude Code) that can read and automatically fill PR templates.

## Reference
- task-437 (parent)
- https://github.com/vfarcic/dot-ai/.github/PULL_REQUEST_TEMPLATE.md
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 PR template includes all 9 sections from design
- [x] #2 Conventional commit format guidance included
- [x] #3 Security checklist covers OWASP basics
- [x] #4 Template renders correctly in GitHub PR UI
- [x] #5 AI agents can parse and fill template automatically
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created comprehensive PR template:

.github/PULL_REQUEST_TEMPLATE.md
- 9 sections: Description, Related Issues, Type of Change, Conventional Commit Format, Testing Checklist, Documentation Checklist, Security Checklist, Breaking Changes, Final Checklist
- Conventional commit format guidance with examples
- Security checklist covers OWASP basics (secrets, input validation, auth, error messages)
- AI Agent Notes section for programmatic filling
- Works for both humans and AI agents (Claude Code)
<!-- SECTION:NOTES:END -->
