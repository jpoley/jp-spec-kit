---
id: task-437.01
title: Create Issue Templates for flowspec
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
Create structured GitHub issue templates following the vfarcic/dot-ai pattern.

## Files to Create

### `.github/ISSUE_TEMPLATE/config.yml`
- `blank_issues_enabled: no` to force template usage
- Contact links for: GitHub Discussions, Documentation, Support, Security reporting

### `.github/ISSUE_TEMPLATE/bug_report.yml`
- Markdown intro with pre-submission checklist
- Bug description (required)
- Steps to reproduce (required)
- Expected behavior (required)
- Actual behavior (required)
- Environment section: Python version, OS, flowspec-cli version
- Logs textarea with shell rendering
- Final checklist checkboxes

### `.github/ISSUE_TEMPLATE/feature_request.yml`
- Problem statement focus (not wish lists)
- Use case description
- Priority dropdown
- Willing to contribute checkbox
- Related to backlog task field

## Reference
- task-437 (parent)
- https://github.com/vfarcic/dot-ai/.github/ISSUE_TEMPLATE/
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 config.yml disables blank issues and provides contact links
- [x] #2 bug_report.yml has all required fields with proper validation
- [x] #3 feature_request.yml focuses on problem statements with priority dropdown
- [x] #4 Templates follow GitHub issue forms YAML schema
- [x] #5 Labels auto-assigned on issue creation (bug, needs-triage, enhancement)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created 3 issue template files:

1. .github/ISSUE_TEMPLATE/config.yml
   - blank_issues_enabled: false
   - Contact links: Discussions, Docs, Security

2. .github/ISSUE_TEMPLATE/bug_report.yml
   - All required fields with validation
   - Environment section (Python, OS, version)
   - Follows GitHub issue forms YAML schema
   - Auto-labels: bug, needs-triage

3. .github/ISSUE_TEMPLATE/feature_request.yml
   - Problem statement focus
   - Priority dropdown
   - Contribution checkboxes
   - Auto-labels: enhancement, needs-triage
<!-- SECTION:NOTES:END -->
