# Docker Hub CI/CD Platform Architecture

## Overview

This document describes the platform architecture for building, securing, and publishing the **AI Coding Agents Devcontainer** image to Docker Hub.

**Image**: `jpoley/specflow-agents`

**Purpose**: Pre-built, production-ready devcontainer for AI-assisted Spec-Driven Development with all AI coding CLIs pre-installed.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GitHub Actions                               │
│                                                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  Trigger Events                                                 │ │
│  │  - Push to main (latest tag)                                   │ │
│  │  - Semantic version tags (vX.Y.Z)                              │ │
│  │  - Pull requests (build only)                                  │ │
│  │  - Manual dispatch (custom tags)                               │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │   Build Job    │  │  Scan Jobs   │  │  Test Jobs   │            │
│  │                │  │              │  │              │            │
│  │ • Multi-arch   │  │ • Trivy      │  │ • Health     │            │
│  │ • amd64/arm64  │  │ • Snyk       │  │ • CLI check  │            │
│  │ • Layer cache  │  │ • Scout      │  │ • Python     │            │
│  │ • SBOM gen     │  │ • SARIF      │  │ • Multi-arch │            │
│  └────────────────┘  └──────────────┘  └──────────────┘            │
│           │                   │                  │                   │
│           └───────────────────┼──────────────────┘                   │
│                               ▼                                       │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    Security Gates                               │ │
│  │  - FAIL on HIGH/CRITICAL vulnerabilities (Trivy)               │ │
│  │  - Report on MEDIUM/LOW (Snyk)                                 │ │
│  │  - SBOM attestation                                            │ │
│  │  - SLSA provenance                                             │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                               │                                       │
│                               ▼ (Pass)                                │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    Push to Docker Hub                           │ │
│  │  - Tag: latest, vX.Y.Z, SHA-based                              │ │
│  │  - Platforms: linux/amd64, linux/arm64                         │ │
│  │  - Provenance: true                                            │ │
│  │  - SBOM: embedded                                              │ │
│  └────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Docker Hub Registry                          │
│                                                                       │
│  Image: jpoley/specflow-agents                        │
│  Tags: latest, vX.Y.Z, main-<SHA>                                   │
│  Platforms: linux/amd64, linux/arm64                                │
│  Metadata: SBOM, provenance, labels                                 │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         User Projects                                │
│                                                                       │
│  .devcontainer/devcontainer.json:                                   │
│  {                                                                   │
│    "image": "jpoley/specflow-agents:latest"          │
│  }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## CI/CD Pipeline Stages

### Stage 1: Build and Push (Job: `build`)

**Goal**: Build multi-platform Docker image with layer caching and SBOM generation.

**Steps**:
1. **Checkout code** - Fetch repository with full history
2. **Setup QEMU** - Enable multi-platform emulation (amd64, arm64)
3. **Setup Docker Buildx** - Advanced build engine with cache support
4. **Login to Docker Hub** - Authenticate (skip on PRs)
5. **Extract metadata** - Generate tags and labels
6. **Build and push** - Multi-platform build with:
   - Layer caching from GitHub Actions cache
   - SBOM generation (Syft)
   - SLSA provenance attestation
   - Push to Docker Hub (except PRs)

**Outputs**:
- `image_digest` - Unique SHA256 digest of the built image
- `image_tags` - List of tags applied to the image

**Performance Target**: < 5 minutes (DORA Elite)

**Optimizations**:
- GitHub Actions cache for Docker layers (`cache-from: type=gha`)
- Buildx parallel builds for multi-arch
- Layer ordering in Dockerfile (least to most frequently changed)

---

### Stage 2: Security Scanning - Trivy (Job: `scan-trivy`)

**Goal**: Detect HIGH and CRITICAL vulnerabilities in the image.

**Steps**:
1. **Pull image** - Fetch image by digest
2. **Run Trivy scan** - Scan for vulnerabilities
   - Severity: `HIGH,CRITICAL`
   - Exit code: `1` (fail on findings)
   - Output: SARIF format for GitHub Security
3. **Upload SARIF** - Publish to GitHub Security tab
4. **Generate report** - Table format for artifacts

**Security Gate**: **FAIL** if HIGH or CRITICAL vulnerabilities found.

**Example Trivy Findings**:
```
┌───────────────────┬────────────────┬──────────┬───────────────────┬───────────────┬────────────────────────────┐
│      Library      │ Vulnerability  │ Severity │ Installed Version │ Fixed Version │           Title            │
├───────────────────┼────────────────┼──────────┼───────────────────┼───────────────┼────────────────────────────┤
│ libssl1.1         │ CVE-2023-12345 │ HIGH     │ 1.1.1n-0          │ 1.1.1w-0      │ OpenSSL arbitrary code exec│
└───────────────────┴────────────────┴──────────┴───────────────────┴───────────────┴────────────────────────────┘
```

---

### Stage 3: Security Scanning - Snyk (Job: `scan-snyk`)

**Goal**: Additional vulnerability scanning with Snyk's proprietary database.

**Steps**:
1. **Pull image** - Fetch image by digest
2. **Run Snyk scan** - Scan for vulnerabilities
   - Threshold: `high`
   - Continue on error (reporting only)
3. **Upload SARIF** - Publish to GitHub Security tab

**Security Gate**: **WARN** on findings (does not block)

**Why Snyk?**: Snyk has a different vulnerability database than Trivy, catching issues Trivy might miss.

---

### Stage 4: SBOM Generation (Job: `sbom`)

**Goal**: Generate Software Bill of Materials (SBOM) and attest to the image.

**Steps**:
1. **Pull image** - Fetch image by digest
2. **Generate SBOM with Syft** - Create SPDX-JSON SBOM
3. **Upload SBOM artifact** - Store for 90 days
4. **Attest SBOM** - Attach SBOM to image in registry

**SBOM Format**: SPDX 2.3 JSON

**Example SBOM Content**:
```json
{
  "spdxVersion": "SPDX-2.3",
  "packages": [
    {
      "name": "python",
      "versionInfo": "3.11.6",
      "licenseConcluded": "Python-2.0"
    },
    {
      "name": "node",
      "versionInfo": "20.10.0",
      "licenseConcluded": "MIT"
    }
  ]
}
```

**SLSA Compliance**: SBOM attestation supports SLSA Level 2.

---

### Stage 5: Image Testing (Job: `test`)

**Goal**: Verify image functionality on both platforms.

**Matrix Strategy**: `[linux/amd64, linux/arm64]`

**Tests**:
1. **Health check** - Run `/home/vscode/healthcheck.sh`
2. **CLI availability** - Verify `claude`, `backlog`, `uv`, `pnpm` are present
3. **Python environment** - Verify Python 3.11+ is available

**Pass Criteria**: All tests pass on both platforms.

---

### Stage 6: Docker Scout Analysis (Job: `scout`)

**Goal**: Analyze CVEs and SLSA compliance with Docker Scout.

**Steps**:
1. **Docker Scout CVEs** - Scan for vulnerabilities
2. **Upload SARIF** - Publish to GitHub Security tab

**Output**: Summary of CVEs by severity.

---

### Stage 7: Metrics Collection (Job: `metrics`)

**Goal**: Track image size, build time, and pipeline health over time.

**Metrics Collected**:
- Image size (MB)
- Build status (success/failure)
- Scan results (Trivy, Snyk, Scout)
- Git SHA and ref
- Build timestamp

**Metrics File** (`metrics.json`):
```json
{
  "workflow_run_id": "12345",
  "git_sha": "abc123",
  "image_size_mb": 1024,
  "build_status": "success",
  "trivy_status": "success",
  "build_date": "2025-12-08T10:00:00Z"
}
```

**Retention**: 90 days

**Observability**: These metrics can be ingested into Prometheus, Datadog, or similar systems.

---

### Stage 8: Rollback Preparation (Job: `rollback`)

**Goal**: Create a rollback manifest for easy reversion to previous image.

**Rollback Manifest** (`rollback-manifest.json`):
```json
{
  "current_digest": "sha256:abc123...",
  "current_tags": ["latest", "v1.2.3"],
  "rollback_command": "docker pull jpoley/specflow-agents@<PREVIOUS_DIGEST> && docker tag jpoley/specflow-agents@<PREVIOUS_DIGEST> jpoley/specflow-agents:latest && docker push jpoley/specflow-agents:latest"
}
```

**Retention**: 90 days

---

## Security Architecture

### Threat Model

**Threats**:
1. **Vulnerable dependencies** - CVEs in OS packages, Python packages, npm packages
2. **Supply chain attacks** - Malicious packages injected during build
3. **Secret leakage** - API keys, tokens, credentials in image
4. **Image tampering** - Unauthorized modifications to published image

**Mitigations**:

| Threat | Mitigation |
|--------|------------|
| Vulnerable dependencies | Trivy + Snyk scanning with FAIL on HIGH/CRITICAL |
| Supply chain attacks | SBOM generation + attestation, SLSA provenance |
| Secret leakage | No secrets in Dockerfile, secrets passed via env vars at runtime |
| Image tampering | Image digest verification, signed attestations |

### Security Scanning Strategy

**Multi-Layer Defense**:
1. **Trivy** - OSS scanner, FAIL on HIGH/CRITICAL
2. **Snyk** - Proprietary database, WARN on findings
3. **Docker Scout** - Docker-native CVE analysis

**SARIF Upload**: All scan results uploaded to GitHub Security tab for centralized tracking.

### SLSA Compliance

**Current Level**: SLSA Level 2

**Requirements Met**:
- Build service: GitHub Actions (trusted)
- Provenance: Embedded in image
- SBOM: Attached as attestation
- Immutable build: Digest-based image references

**Path to SLSA Level 3**:
- Sign provenance with Sigstore
- Use hermetic builds (isolated, no network access)
- Add build reproducibility verification

---

## Release Process

### Semantic Versioning

**Tag Format**: `vX.Y.Z` (e.g., `v1.2.3`)

**Versioning Strategy**:
- **MAJOR**: Breaking changes to image (e.g., upgrade Python 3.11 → 3.12)
- **MINOR**: New features (e.g., add new AI CLI)
- **PATCH**: Bug fixes, security patches

**Example**:
```bash
# Create a new release
git tag v1.2.3
git push origin v1.2.3

# GitHub Actions automatically builds and pushes:
# - jpoley/specflow-agents:v1.2.3
# - jpoley/specflow-agents:v1.2
# - jpoley/specflow-agents:v1
# - jpoley/specflow-agents:latest
```

### Manual Releases

**Use Case**: Testing, beta releases, emergency hotfixes

**Process**:
```bash
# Trigger workflow with custom tag
gh workflow run docker-publish.yml -f tag=beta
```

**Result**: Image tagged as `jpoley/specflow-agents:beta`

---

## Rollback Procedures

### Scenario: Critical Vulnerability Discovered in Latest Image

**Symptoms**:
- Trivy scan shows new CRITICAL CVE after push
- Security team requests immediate rollback

**Rollback Steps**:

1. **Identify previous good image**:
   ```bash
   # List recent image digests
   docker pull jpoley/specflow-agents:latest
   docker image history jpoley/specflow-agents:latest
   ```

2. **Re-tag previous digest as `latest`**:
   ```bash
   # Pull previous good image by digest
   docker pull jpoley/specflow-agents@sha256:abc123...

   # Re-tag as latest
   docker tag jpoley/specflow-agents@sha256:abc123... \
     jpoley/specflow-agents:latest

   # Push updated latest tag
   docker push jpoley/specflow-agents:latest
   ```

3. **Verify rollback**:
   ```bash
   # Users pulling latest now get the previous image
   docker pull jpoley/specflow-agents:latest
   docker image inspect jpoley/specflow-agents:latest --format='{{.RepoDigests}}'
   ```

4. **Create hotfix**:
   - Fix vulnerability in Dockerfile
   - Create new patch version tag (e.g., `v1.2.4`)
   - Push tag to trigger new build

**Automated Rollback**: Use the `rollback-manifest.json` artifact from the pipeline for digest references.

---

## Observability and Monitoring

### Build Metrics

**Tracked Metrics**:
- Build duration (target: < 5 minutes)
- Image size (MB) over time
- Vulnerability count (by severity)
- Build success rate
- Platform-specific test pass rate

**Storage**: GitHub Actions artifacts (90-day retention)

**Dashboarding**: Metrics can be ingested into:
- Prometheus + Grafana
- Datadog
- New Relic
- CloudWatch

**Example Prometheus Query**:
```promql
# Build duration trend
avg_over_time(docker_build_duration_seconds[7d])

# Image size growth
delta(docker_image_size_mb[30d])
```

### Docker Hub Pull Statistics

**Metrics Available** (via Docker Hub API):
- Pull count by tag
- Pull count by geography
- Pull count over time

**Example API Call**:
```bash
curl -s "https://hub.docker.com/v2/repositories/jpoley/specflow-agents/" | jq '.pull_count'
```

### GitHub Security Tab

**Centralized View**:
- All SARIF uploads (Trivy, Snyk, Scout)
- CVE tracking over time
- Dependency graph
- Dependabot alerts

**Access**: `https://github.com/jpoley/jp-spec-kit/security`

---

## DORA Elite Metrics Compliance

### Deployment Frequency

**Target**: Multiple deploys per day

**Current State**:
- Push to `main` → automatic build and deploy
- Tag push → automatic versioned release
- Manual dispatch → on-demand deployment

**Status**: ✅ Elite

### Lead Time for Changes

**Target**: < 1 hour

**Current State**:
- Commit to `main` → build triggers immediately
- Build duration: < 5 minutes (target)
- Total lead time: < 10 minutes

**Status**: ✅ Elite

### Change Failure Rate

**Target**: < 15%

**Mitigation**:
- Security gates (Trivy FAIL on HIGH/CRITICAL)
- Multi-platform testing
- Health checks before push
- Automated rollback capability

**Status**: 🟡 In Progress (need historical failure rate data)

### Mean Time to Recovery (MTTR)

**Target**: < 1 hour

**Rollback Capability**:
- Re-tag previous digest as `latest`: < 5 minutes
- Automated rollback manifest generation
- No code changes required for rollback

**Status**: ✅ Elite

---

## Cost Optimization

### Build Cost Reduction

**GitHub Actions Minutes**:
- Free tier: 2,000 minutes/month (public repos)
- Build duration: ~5 minutes
- Max builds/month: 400

**Docker Hub**:
- Free tier: 1 image, unlimited pulls for public images
- Cost: $0

**Optimizations**:
- Layer caching reduces build time by ~60%
- Multi-platform builds run in parallel
- Skip PR pushes to save minutes

### Image Size Optimization

**Current Size**: ~1.2 GB (estimated)

**Optimization Strategies**:
1. **Multi-stage builds** - Discard build dependencies
2. **Alpine base** - Smaller OS (trade-off: compatibility)
3. **Prune pnpm cache** - Remove unused packages
4. **Slim Node.js** - Use `node:20-slim` instead of full image

**Target**: < 1 GB

---

## User Documentation

### For Project Developers

**Quick Start**:
```json
{
  "name": "My AI Project",
  "image": "jpoley/specflow-agents:latest"
}
```

**Pin to Specific Version**:
```json
{
  "name": "My AI Project",
  "image": "jpoley/specflow-agents:v1.2.3"
}
```

**Pin to Digest (Immutable)**:
```json
{
  "name": "My AI Project",
  "image": "jpoley/specflow-agents@sha256:abc123..."
}
```

**Recommendation**: Use semantic version tags (`v1.2.3`) for production, `latest` for development.

---

## Future Enhancements

### Short-Term (Q1 2026)

- [ ] Add vulnerability trend tracking dashboard
- [ ] Implement Sigstore signing for SLSA Level 3
- [ ] Add Docker Hub rate limit monitoring
- [ ] Create automated changelog generation

### Medium-Term (Q2 2026)

- [ ] Implement hermetic builds for SLSA Level 4
- [ ] Add image size regression testing
- [ ] Create regional mirror registries (GHCR, ECR)
- [ ] Add performance benchmarking to test suite

### Long-Term (Q3+ 2026)

- [ ] Support for Windows containers
- [ ] Add GPU support for AI model training
- [ ] Create specialized variants (backend-only, frontend-only)
- [ ] Implement auto-patching for CVEs

---

## Troubleshooting

### Build Fails: "Layer Cache Miss"

**Symptom**: Build takes full 15 minutes instead of 5 minutes.

**Cause**: GitHub Actions cache evicted or Dockerfile layers changed.

**Solution**:
```bash
# Manually warm cache
gh workflow run docker-publish.yml -f tag=cache-warmup
```

### Security Scan Fails: "HIGH Vulnerability Detected"

**Symptom**: Trivy scan fails with HIGH severity CVE.

**Cause**: New CVE published for base image or dependency.

**Solution**:
1. Review Trivy report artifact
2. Update base image: `mcr.microsoft.com/devcontainers/python:3.11-bullseye`
3. Or upgrade affected package in Dockerfile
4. Re-run build

### Multi-Platform Build Fails on ARM64

**Symptom**: Build succeeds on amd64 but fails on arm64.

**Cause**: QEMU emulation issue or architecture-specific dependency.

**Solution**:
1. Check build logs for ARM64-specific errors
2. Test locally with `docker buildx build --platform linux/arm64`
3. Add architecture-specific workarounds in Dockerfile

---

## References

- [Docker Build with Buildx](https://docs.docker.com/build/building/multi-platform/)
- [GitHub Actions Cache](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [Trivy Vulnerability Scanner](https://aquasecurity.github.io/trivy/)
- [SLSA Framework](https://slsa.dev/)
- [SBOM with Syft](https://github.com/anchore/syft)
- [Docker Scout](https://docs.docker.com/scout/)

---

## Appendix: Dockerfile Layer Breakdown

```dockerfile
# Layer 1: Base OS + Python 3.11 (500 MB)
FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

# Layer 2: Node.js + pnpm (200 MB)
RUN install_node_pnpm

# Layer 3: GitHub CLI (50 MB)
RUN install_gh_cli

# Layer 4: uv + Python tools (100 MB)
RUN install_uv_ruff_pytest

# Layer 5: AI CLIs (300 MB)
RUN install_claude_copilot_codex_gemini_backlog

# Layer 6: Shell config (1 MB)
RUN configure_zshrc_bashrc

# Layer 7: MCP config (1 MB)
RUN configure_mcp_server

# Total: ~1.2 GB
```

**Caching Strategy**: Layers 1-3 rarely change, Layers 4-5 change occasionally, Layers 6-7 change frequently. This ordering maximizes cache hits.

---

**Document Version**: 1.0.0
**Last Updated**: 2025-12-08
**Maintained By**: Platform Engineering Team
