---
id: task-339
title: Create GitHub Actions Workflow for Docker Hub Publishing
status: To Do
assignee: []
created_date: '2025-12-09 01:01'
labels:
  - infrastructure
  - devcontainer
  - ci-cd
dependencies:
  - task-338
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Automated CI/CD pipeline to build, scan, and publish devcontainer images to Docker Hub.

File location: `.github/workflows/docker-hub-publish.yml`

Workflow triggers:
- Push to main → Build and push `edge` tag
- Git tags `v*.*.*` → Build and push semver tags
- Pull requests → Build only (no push)
- Weekly schedule (Mondays 6 AM UTC) → Rebuild for security updates

Build matrix for 4 variants, multi-platform (amd64, arm64), semantic versioning tags, security scanning with Trivy, SBOM generation, GitHub Security integration.

Depends on: task-338 (Dockerfile.hub)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Workflow builds all 4 variants in matrix (runtime, minimal, python, node)
- [ ] #2 Multi-platform builds working (linux/amd64, linux/arm64) using QEMU and buildx
- [ ] #3 Semantic versioning tags automatically generated from git tags
- [ ] #4 Trivy security scan runs on all images and blocks publish on HIGH/CRITICAL vulnerabilities
- [ ] #5 SBOM generated in SPDX format and attached to GitHub releases
- [ ] #6 Docker Hub README auto-updated on releases using peter-evans/dockerhub-description
- [ ] #7 Weekly rebuild scheduled (cron: 0 6 * * 1) for security updates
- [ ] #8 Build caching configured (cache-from/cache-to type=gha) for faster builds
<!-- AC:END -->
