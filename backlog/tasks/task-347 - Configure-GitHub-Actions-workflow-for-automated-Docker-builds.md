---
id: task-347
title: Configure GitHub Actions workflow for automated Docker builds
status: To Do
assignee: []
created_date: '2025-12-09 01:03'
labels:
  - infrastructure
  - cicd
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Set up GitHub Actions workflow to automate Docker image building, scanning, and publishing.

**Implementation**:
1. Validate workflow YAML syntax:
   ```bash
   yamllint .github/workflows/docker-publish.yml
   ```

2. Test workflow on a feature branch first (will build but not push)

3. Verify job dependencies are correct:
   - build → scan-trivy, scan-snyk, test, sbom
   - All scans → scout
   - All jobs → metrics, rollback

4. Verify caching is configured:
   - `cache-from: type=gha`
   - `cache-to: type=gha,mode=max`

5. Test manual dispatch:
   ```bash
   gh workflow run docker-publish.yml -f tag=test
   ```

**Monitoring**:
- Check workflow run duration (target: < 5 minutes for build job)
- Verify artifacts are uploaded (trivy-scan-report, sbom, metrics.json, rollback-manifest.json)
- Check GitHub Security tab for SARIF uploads

**Failure Scenarios**:
- Workflow syntax errors
- Job timeouts (15 minutes max)
- Security scan failures
- Multi-platform build failures
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Workflow file passes YAML linting
- [ ] #2 Workflow triggers correctly on push to main, tag push, PR, and manual dispatch
- [ ] #3 Build job completes in < 5 minutes
- [ ] #4 All security scans complete successfully
- [ ] #5 Artifacts (scan reports, SBOM, metrics) are uploaded
- [ ] #6 Multi-platform build produces images for both amd64 and arm64
<!-- AC:END -->
