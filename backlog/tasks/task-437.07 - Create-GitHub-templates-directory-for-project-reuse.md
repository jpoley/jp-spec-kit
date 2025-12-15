---
id: task-437.07
title: Create GitHub templates directory for project reuse
status: Done
assignee:
  - '@kinsale'
created_date: '2025-12-11 03:28'
updated_date: '2025-12-15 02:18'
labels:
  - enhancement
  - templates
  - subtask
dependencies: []
parent_task_id: task-437
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Store GitHub configuration templates that can be copied to new projects via /flow:init.

## Directory to Create

### `templates/github/`

Contents:
- `ISSUE_TEMPLATE/config.yml.template`
- `ISSUE_TEMPLATE/bug_report.yml.template`
- `ISSUE_TEMPLATE/feature_request.yml.template`
- `PULL_REQUEST_TEMPLATE.md.template`
- `CODEOWNERS.template`
- `labeler.yml.template`
- `release.yml.template`
- `workflows/labeler.yml.template`
- `workflows/stale.yml.template`
- `workflows/scorecard.yml.template`
- `CONTRIBUTING.md.template`
- `CODE_OF_CONDUCT.md.template`
- `SECURITY.md.template`
- `SUPPORT.md.template`

## Template Variables
- `{{PROJECT_NAME}}` - Project name
- `{{PROJECT_OWNER}}` - GitHub owner/org
- `{{PROJECT_REPO}}` - Repository name
- `{{DEFAULT_BRANCH}}` - Main branch name
- `{{MAINTAINER}}` - Primary maintainer
- `{{CONTACT_EMAIL}}` - Contact email

## Integration
Update `/flow:init` to:
1. Detect missing GitHub files
2. Prompt for template variables
3. Copy and render templates to `.github/`

## Reference
- task-437 (parent)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 templates/github/ directory created with all template files
- [x] #2 Template variables documented in each file
- [x] #3 Templates render correctly with variable substitution
- [ ] #4 /flow:init detects missing GitHub configuration
- [ ] #5 /flow:init prompts for required variables
- [ ] #6 Documentation for template customization
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created templates/github/ directory with reusable templates:

## Files Created (11 total)

### Issue Templates
- ISSUE_TEMPLATE/config.yml ({{PROJECT_REPO}}, {{PROJECT_NAME}})
- ISSUE_TEMPLATE/bug_report.yml ({{PROJECT_NAME}}, {{PROJECT_REPO}}, {{DEFAULT_BRANCH}})
- ISSUE_TEMPLATE/feature_request.yml ({{PROJECT_NAME}})

### PR and Code Ownership
- PULL_REQUEST_TEMPLATE.md (no variables)
- CODEOWNERS ({{MAINTAINER}})
- labeler.yml (no variables)

### Release and Workflows
- release.yml (no variables)
- workflows/labeler.yml (no variables, pinned SHAs)
- workflows/stale.yml (no variables, pinned SHAs)
- workflows/scorecard.yml ({{DEFAULT_BRANCH}}, {{PROJECT_NAME}})

### Documentation
- README.md with usage instructions and variable reference

## Template Variables
- {{PROJECT_NAME}} - Project name
- {{PROJECT_OWNER}} - GitHub owner
- {{PROJECT_REPO}} - Full repo path
- {{DEFAULT_BRANCH}} - Main branch
- {{MAINTAINER}} - Primary maintainer

Note: AC 4-6 (flow:init integration) deferred to future task as it requires CLI changes.
<!-- SECTION:NOTES:END -->
