---
id: task-439
title: Migrate Dockerfile to Bookworm
status: Done
assignee:
  - '@muckross'
created_date: '2025-12-11 04:14'
updated_date: '2025-12-15 02:18'
labels:
  - infrastructure
  - docker
  - security
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update .devcontainer/Dockerfile from bullseye to bookworm base image
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Base image updated to mcr.microsoft.com/devcontainers/python:3.11-bookworm
- [x] #2 All existing functionality preserved
- [x] #3 Image builds successfully
- [x] #4 Image size verified (comparable to current ~1.5GB)
- [ ] #5 No build errors or warnings
<!-- AC:END -->
