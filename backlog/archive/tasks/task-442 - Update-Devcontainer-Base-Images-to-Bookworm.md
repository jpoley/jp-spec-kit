---
id: task-442
title: Update Devcontainer Base Images to Bookworm
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-11 04:16'
updated_date: '2025-12-19 19:09'
labels:
  - infrastructure
  - devcontainer
  - security
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update .devcontainer/Dockerfile and devcontainer.json from Debian Bullseye to Bookworm base images for improved security posture and extended support lifecycle (EOL: Jun 2028 vs Aug 2026)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update .devcontainer/Dockerfile line 15: python:3.11-bullseye → python:3.11-bookworm
- [x] #2 Update .devcontainer/devcontainer.json line 3: python:3.11-bullseye → python:3.11-bookworm
- [x] #3 Build Docker image locally and verify successful build
- [x] #4 Test container functionality (Python, Node, pnpm, uv, gh)
- [x] #5 Run full pytest suite in bookworm container - all tests pass
- [x] #6 Create PR with detailed commit message and migration plan link
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Superseded by PR #976 - Docker Hardened Images (DHI) migration. Dockerfile now uses dhi.io/python:3.13-alpine3.22-dev which is more secure than Bookworm.
<!-- SECTION:NOTES:END -->
