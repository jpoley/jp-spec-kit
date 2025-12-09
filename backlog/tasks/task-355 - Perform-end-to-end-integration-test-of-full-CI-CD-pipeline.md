---
id: task-355
title: Perform end-to-end integration test of full CI/CD pipeline
status: To Do
assignee: []
created_date: '2025-12-09 01:03'
labels:
  - infrastructure
  - cicd
  - testing
  - integration
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Execute a complete end-to-end test of the CI/CD pipeline from code commit to published image, verifying all stages work correctly.

**Test Scenario**: Publish a new version of the devcontainer image.

**Test Steps**:

1. **Create feature branch**:
   ```bash
   git checkout -b test/cicd-e2e
   ```

2. **Make trivial change to Dockerfile**:
   ```dockerfile
   # Add comment or label for testing
   LABEL test.version="e2e-test"
   ```

3. **Commit and push**:
   ```bash
   git commit -am "test: E2E pipeline test"
   git push origin test/cicd-e2e
   ```

4. **Verify PR build**:
   - Workflow triggers on PR
   - Build job completes successfully
   - Image NOT pushed (PR builds don't push)
   - Security scans run
   - Tests pass

5. **Merge to main**:
   ```bash
   gh pr create --title "Test E2E pipeline" --body "E2E test"
   gh pr merge --squash
   ```

6. **Verify main build**:
   - Workflow triggers on merge
   - Build job pushes image with tags: `latest`, `main-<SHA>`
   - Security scans pass (Trivy, Snyk, Scout)
   - SBOM generated and attached
   - Tests pass on both platforms
   - Metrics collected
   - Rollback manifest created

7. **Verify published image**:
   ```bash
   docker pull jpoley/specflow-agents:latest
   docker run --rm jpoley/specflow-agents:latest /home/vscode/healthcheck.sh
   ```

8. **Test semantic versioning**:
   ```bash
   git tag v1.0.0-test
   git push origin v1.0.0-test
   ```
   Verify tags: `v1.0.0-test`, `v1.0-test`, `v1-test`, `latest`

9. **Test rollback**:
   - Identify previous digest
   - Execute rollback script
   - Verify `latest` tag reverted

10. **Verify artifacts**:
    - Download `trivy-scan-report`
    - Download `sbom.spdx.json`
    - Download `metrics.json`
    - Download `rollback-manifest.json`

11. **Verify GitHub Security tab**:
    - SARIF results visible
    - Vulnerability alerts (if any)

12. **Test manual dispatch**:
    ```bash
    gh workflow run docker-publish.yml -f tag=e2e-manual
    ```
    Verify image tagged as `e2e-manual`

**Acceptance Criteria**:
- All workflow jobs complete successfully
- Image published to Docker Hub with correct tags
- Security scans pass or report expected findings
- SBOM attached to image
- Tests pass on both platforms
- Artifacts uploaded and downloadable
- Rollback procedure works
- Total pipeline duration < 15 minutes

**Cleanup**:
- Delete test tags from Docker Hub
- Delete test branches
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 PR build completes successfully without pushing image
- [ ] #2 Main build completes and pushes image with correct tags
- [ ] #3 All security scans (Trivy, Snyk, Scout) complete successfully
- [ ] #4 SBOM generated and attached to published image
- [ ] #5 Tests pass on both linux/amd64 and linux/arm64
- [ ] #6 All artifacts (scan reports, SBOM, metrics, rollback manifest) uploaded
- [ ] #7 Published image pulls and runs successfully
- [ ] #8 Semantic version tagging works correctly
- [ ] #9 Rollback procedure successfully reverts to previous image
- [ ] #10 Total pipeline duration < 15 minutes
- [ ] #11 GitHub Security tab shows SARIF uploads
<!-- AC:END -->
