---
id: task-444
title: Validate CI/CD Pipeline Post-Bookworm Migration
status: To Do
assignee: []
created_date: '2025-12-11 04:17'
labels:
  - cicd
  - infrastructure
  - docker
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ensure all GitHub Actions workflows function correctly after bookworm migration and verify Docker Hub publishing works as expected
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Review docker-publish.yml workflow file - confirm it references Dockerfile (not hardcoded base image)
- [ ] #2 Review ci.yml workflow - verify it uses GitHub runners (ubuntu-latest), not devcontainer
- [ ] #3 Review security-scan.yml workflow - confirm system Python install (no devcontainer dependency)
- [ ] #4 Create migration PR and verify all CI checks pass (lint, test, build, security)
- [ ] #5 Monitor docker-publish workflow execution after PR merge
- [ ] #6 Verify new image publishes to jpoley/flowspec-agents:latest with bookworm base
- [ ] #7 Pull published image and confirm /etc/os-release shows VERSION='12 (bookworm)'
<!-- AC:END -->
