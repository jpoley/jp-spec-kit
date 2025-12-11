---
id: task-437
title: Update GitHub workflow files to use flowspec instead of flowspec
status: To Do
assignee: []
created_date: '2025-12-11 01:32'
labels:
  - platform
  - ci-cd
  - rename
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update all GitHub Actions workflow files (.github/workflows/*.yml) to replace references to:
- flowspec_workflow.yml → flowspec_workflow.yml
- flowspec → flowspec in paths, comments, and documentation
- /flow: → /flow: in any command examples

Affected workflows:
- role-validation.yml (validates flowspec_workflow.yml)
- dev-setup-validation.yml (validates .claude/commands/flowspec/ structure)
- security-parallel.yml, security-scan.yml
- docker-publish.yml

Changes needed:
1. Update path references in workflow triggers
2. Update validation scripts to reference flowspec_workflow.yml
3. Update directory structure checks (flowspec → flowspec)
4. Update job names and descriptions
5. Update comments and documentation strings
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All workflow files reference flowspec_workflow.yml instead of flowspec_workflow.yml
- [ ] #2 dev-setup-validation checks for .claude/commands/flowspec/ directory
- [ ] #3 role-validation validates flowspec_workflow.yml schema
- [ ] #4 All workflows pass CI after rename
- [ ] #5 No references to 'flowspec' remain in workflow files except in comments explaining migration
<!-- AC:END -->
