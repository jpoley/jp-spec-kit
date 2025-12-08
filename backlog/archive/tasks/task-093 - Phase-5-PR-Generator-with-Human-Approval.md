---
id: task-093
title: Phase 5 - PR Generator with Human Approval
status: Done
assignee: []
created_date: '2025-11-28 15:56'
updated_date: '2025-12-03 01:15'
labels:
  - validate-enhancement
  - phase-5
  - backend
  - pr-generation
dependencies:
  - task-092
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement the PR generation phase that creates a comprehensive pull request based on the completed task. The PR includes the task description, all acceptance criteria (verified), implementation notes, and validation results. Requires human approval before actual PR creation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Generates PR title from task title following pattern: 'feat(scope): task-title' or 'fix(scope): task-title'
- [ ] #2 Generates PR body with sections: Summary (from task desc), Acceptance Criteria (all checked), Test Plan, Implementation Notes
- [ ] #3 PR body includes validation results summary: tests passed, security scan status, quality gate status
- [ ] #4 Presents PR preview to user via formatted output before creation
- [ ] #5 Requests explicit human approval using AskUserQuestion with options: Create PR, Edit first, Skip PR
- [ ] #6 On approval, creates PR using `gh pr create --title "..." --body "..."`
- [ ] #7 Handles branch not pushed scenario: prompts to push first or auto-pushes with confirmation
- [ ] #8 Returns PR URL on successful creation; handles gh CLI errors gracefully
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation complete on main: src/specify_cli/workflow/pr_generator.py (12KB)
<!-- SECTION:NOTES:END -->
