---
id: task-437
title: Add Docker version tag publishing on release
status: To Do
assignee: []
created_date: '2025-12-11 03:54'
labels:
  - infrastructure
  - cicd
  - docker
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Docker images are only published with 'latest' and 'sha-xxx' tags. Version tags (v0.2.349, etc.) are not published when releases are created. This makes it impossible to pull specific versions of the flowspec-agents image.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Docker images are pushed with version tag (e.g., v0.2.349) when a release is created
- [ ] #2 Docker images are also tagged with semver patterns (e.g., 0.2)
- [ ] #3 Latest tag continues to work as before
- [ ] #4 Workflow triggers on both tag push and Dockerfile changes
<!-- AC:END -->
