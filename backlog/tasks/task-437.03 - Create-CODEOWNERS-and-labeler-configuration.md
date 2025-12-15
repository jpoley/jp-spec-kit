---
id: task-437.03
title: Create CODEOWNERS and labeler configuration
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
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Set up automatic code ownership and PR labeling.

## Files to Create

### `.github/CODEOWNERS`
- Default owner: `* @jpoley`
- Path-specific:
  - `/docs/` - docs ownership
  - `/.github/` - CI/CD ownership  
  - `/src/` - core code ownership
  - `/templates/` - template ownership
  - `/tests/` - test ownership

### `.github/labeler.yml`
Label mappings:
- `documentation`: docs/**, *.md, README*
- `source`: src/**
- `tests`: tests/**, **/*.test.*, **/*.spec.*
- `ci-cd`: .github/workflows/**, .github/actions/**, Dockerfile*
- `infrastructure`: k8s/**, kubernetes/**, manifests/**
- `dependencies`: pyproject.toml, requirements*.txt, uv.lock
- `config`: *.config.*, *.yaml, *.yml, *.toml
- `templates`: templates/**

### `.github/workflows/labeler.yml`
GitHub Action workflow to apply labels on PR.

## Reference
- task-437 (parent)
- https://github.com/vfarcic/dot-ai/.github/CODEOWNERS
- https://github.com/vfarcic/dot-ai/.github/labeler.yml
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 CODEOWNERS file with default and path-specific owners
- [x] #2 labeler.yml maps all relevant file paths to labels
- [x] #3 Labeler workflow triggers on pull_request events
- [x] #4 Labels automatically applied when PR created/updated
- [x] #5 Action version pinned with full commit SHA
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created CODEOWNERS and labeler configuration:

1. .github/CODEOWNERS
   - Default owner: @jpoley
   - Path-specific: docs, src, templates, tests, .github, memory, scripts
   - Config files: pyproject.toml, uv.lock

2. .github/labeler.yml
   - 13 label mappings: documentation, source, tests, ci-cd, infrastructure, dependencies, config, templates, scripts, github, memory, backlog, claude
   - Uses v5 labeler syntax (changed-files)

3. .github/workflows/labeler.yml
   - Triggers on PR opened, synchronize, reopened
   - Actions pinned with full SHA:
     - checkout@b4ffde65f46336ab88eb53be808477a3936bae11 (v4.1.1)
     - labeler@8558fd74291d67161a8a78ce36a881fa63b766a9 (v5.0.0)
   - Minimal permissions: contents read, pull-requests write
   - persist-credentials: false for security
<!-- SECTION:NOTES:END -->
