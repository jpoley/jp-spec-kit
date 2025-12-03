---
id: task-254
title: Build and Publish Security Scanner Docker Image
status: To Do
assignee: []
created_date: '2025-12-03 02:26'
labels:
  - infrastructure
  - containers
  - security
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create Docker image with Semgrep and specify-cli for air-gapped and highly controlled environments. Optimize for size (<200MB) and publish to GHCR.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create Dockerfile with Python 3.11, Semgrep, uv, specify-cli
- [ ] #2 Optimize image size (<200MB using slim base and multi-stage build)
- [ ] #3 Publish to GHCR (ghcr.io/yourusername/jpspeckit-security-scanner:version)
- [ ] #4 Add image usage to CI/CD pipeline as alternative scan method
- [ ] #5 Document usage for air-gapped environments in docs/platform/
- [ ] #6 Test image in isolated environment (no network access)
<!-- AC:END -->
