---
id: task-349
title: Implement SBOM generation and attestation
status: To Do
assignee: []
created_date: '2025-12-09 01:03'
labels:
  - infrastructure
  - cicd
  - security
  - compliance
dependencies: []
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Configure SBOM generation with Syft and attach attestations to published images for supply chain security.

**SBOM Requirements**:
- Format: SPDX 2.3 JSON
- Tool: Syft (Anchore)
- Attestation: GitHub Actions attestation

**Implementation**:
1. Test SBOM generation locally:
   ```bash
   docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
     anchore/syft:latest ai-coding-agents-test:local -o spdx-json > sbom.spdx.json
   ```

2. Validate SBOM format:
   ```bash
   jq '.spdxVersion' sbom.spdx.json  # Should be "SPDX-2.3"
   jq '.packages | length' sbom.spdx.json  # Should be > 0
   ```

3. Verify SBOM includes key components:
   - python (3.11.x)
   - node (20.x)
   - npm packages (@anthropic-ai/claude-code, backlog.md, etc.)
   - Debian packages

4. Test attestation attachment (requires Docker Hub push)

**SLSA Compliance**:
- SBOM attestation → SLSA Level 2
- Provenance attestation → SLSA Level 2
- Path to Level 3: Add Sigstore signing

**Retention**:
- SBOM artifacts: 90 days in GitHub Actions
- SBOM attestations: Permanent in Docker Hub
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 SBOM generated successfully in SPDX 2.3 JSON format
- [ ] #2 SBOM includes all major dependencies (Python, Node, npm packages, Debian packages)
- [ ] #3 SBOM uploaded as artifact with 90-day retention
- [ ] #4 SBOM attestation attached to published image
- [ ] #5 SBOM can be retrieved from Docker Hub: docker buildx imagetools inspect <image> --format '{{json .SBOM}}'
- [ ] #6 SBOM generation completes in < 2 minutes
<!-- AC:END -->
