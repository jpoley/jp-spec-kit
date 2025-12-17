# ADR-012: Migrate Docker Base Images from Debian Bullseye to Bookworm

## Status

Proposed

## Context

### Current State

The Flowspec development environment currently uses Debian 11 (Bullseye) base images:

- **Devcontainer**: `mcr.microsoft.com/devcontainers/python:3.11-bullseye`
- **Published Docker Image**: `mcr.microsoft.com/devcontainers/python:3.11-bullseye`

### Security Vulnerabilities in Bullseye

Debian 11 (Bullseye) entered Long Term Support (LTS) status in August 2024, meaning:

1. **Slower security patch cadence**: Security updates are provided only for critical vulnerabilities
2. **Known vulnerabilities**: Multiple CVEs affecting bullseye-based Python images:
   - **GHSA-r9hx-vwmv-q579**: setuptools vulnerability in Python package ecosystem
   - **CVE-2025-4330**: Marked "not-affected" in Bookworm because vulnerable code was never backported
   - Additional transitive dependencies with security issues

3. **Microsoft's patching policy**: Microsoft devcontainers only provides security patches for the latest in-support Debian versions. Bullseye receives minimal updates.

### Business Impact

**Risk of NOT migrating:**
- Exposure to known CVEs in production containers
- Slower remediation time for future vulnerabilities
- Compliance failures in security audits
- Increased attack surface for supply chain attacks

**Investment justification:**
- Migration cost: ~2-4 hours (update, test, validate)
- Risk reduction: Eliminates known CVEs, moves to active security support
- ROI: High - prevents potential security incidents, audit findings, and emergency patching

## Decision

**Migrate all Docker base images from Debian 11 (Bullseye) to Debian 12 (Bookworm).**

Specifically:
- Update `.devcontainer/Dockerfile` base image to `mcr.microsoft.com/devcontainers/python:3.11-bookworm`
- Update `.devcontainer/devcontainer.json` image to `mcr.microsoft.com/devcontainers/python:3.11-bookworm`

## Options Considered

### Option 1: Stay on Bullseye (REJECTED)

**Approach**: Continue using `python:3.11-bullseye` base images

**Pros**:
- No migration effort required
- Known stable environment
- No breaking change risk

**Cons**:
- **Critical security risk**: Slower security patches, known CVEs
- **LTS limitations**: Bullseye only receives critical updates
- **Compliance failures**: Security audits will flag outdated base images
- **Technical debt**: Eventually forced to migrate under pressure

**Verdict**: Unacceptable security risk. Deferred migration increases future emergency migration cost.

---

### Option 2: Migrate to Microsoft Devcontainers Bookworm (RECOMMENDED)

**Approach**: Use `mcr.microsoft.com/devcontainers/python:3.11-bookworm`

**Pros**:
- **Active security support**: Debian 12 is current stable, receives fast security patches
- **Microsoft maintained**: Regular updates, pre-configured for devcontainers
- **Minimal risk**: Microsoft images include developer tools (git, zsh, common-utils)
- **Drop-in replacement**: Designed as a direct upgrade path from bullseye images
- **VS Code integration**: Optimized for devcontainer workflows

**Cons**:
- Potential package version differences (e.g., libc, openssl)
- Requires testing all existing functionality
- Slightly larger image size (acceptable tradeoff)

**Verdict**: **RECOMMENDED**. Best balance of security, compatibility, and developer experience.

---

### Option 3: Migrate to Official Python Bookworm

**Approach**: Use `python:3.11-bookworm` (official Docker Hub image)

**Pros**:
- Canonical Python image from Docker official images
- Smaller base image (no devcontainer features)
- Active security support

**Cons**:
- **Missing devcontainer features**: No pre-configured git, zsh, common-utils
- **Additional setup required**: Manual installation of developer tools
- **Maintenance burden**: Need to replicate Microsoft's devcontainer features
- **Breaking change**: Requires rewriting `.devcontainer/Dockerfile`

**Verdict**: Not recommended. Adds maintenance overhead with no security benefit over Option 2.

---

### Option 4: Migrate to Slim Bookworm

**Approach**: Use `python:3.11-slim-bookworm` (minimal image)

**Pros**:
- Smallest image size (~50% reduction)
- Faster builds and pulls
- Reduced attack surface (fewer packages)
- Active security support

**Cons**:
- **Missing core tools**: No compilers, build essentials, git
- **Incompatible with devcontainer workflow**: Requires extensive customization
- **Breaking change for AI assistants**: Requires additional package installations
- **Developer experience regression**: Missing common utilities

**Verdict**: Not suitable for development containers. Better for production deployments.

---

## Selected Option: Option 2 (Microsoft Devcontainers Bookworm)

**Rationale**:
- Direct security upgrade with minimal risk
- Maintained by Microsoft for devcontainer use cases
- Preserves existing developer experience
- Drop-in replacement for bullseye images

## Implementation Plan

### Phase 1: Image Migration

**Files to modify**:

1. `.devcontainer/Dockerfile`:
   ```diff
   - FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye
   + FROM mcr.microsoft.com/devcontainers/python:3.11-bookworm
   ```

2. `.devcontainer/devcontainer.json`:
   ```diff
   - "image": "mcr.microsoft.com/devcontainers/python:3.11-bullseye",
   + "image": "mcr.microsoft.com/devcontainers/python:3.11-bookworm",
   ```

### Phase 2: Validation Testing

**Test categories**:

1. **Container build verification**:
   - Dockerfile builds successfully
   - Image size comparable to bullseye (~1.5GB expected)
   - No build errors or warnings

2. **Python environment**:
   - Python 3.11 functional
   - `uv` package manager works
   - Virtual environments activate correctly
   - `pytest` test suite passes

3. **Developer tools**:
   - Node.js 20 + pnpm installed and functional
   - GitHub CLI (`gh`) works
   - Git operations function correctly
   - zsh shell configured properly

4. **AI assistant CLIs**:
   - Claude Code functional
   - GitHub Copilot CLI functional
   - Other AI assistants (codex, gemini) work if installed

5. **MCP servers**:
   - backlog.md MCP server operational
   - MCP server health checks pass (`./scripts/bash/check-mcp-servers.sh`)

6. **VS Code integration**:
   - Devcontainer opens successfully
   - Extensions load correctly
   - Python debugger works
   - Terminal integration functional

### Phase 3: Rollback Strategy

If critical issues emerge:

1. **Immediate rollback**:
   ```bash
   git revert <migration-commit>
   git push
   ```

2. **Rebuild containers**:
   ```bash
   docker system prune -a  # Clear cached bookworm layers
   # Rebuild devcontainer from bullseye base
   ```

3. **Document issues**:
   - Create task for bookworm-specific bugs
   - Update ADR with "Rejected" status and rationale
   - Schedule future migration attempt

### Phase 4: Documentation Updates

Update references in:
- `.devcontainer/Dockerfile` comments
- `docs/guides/dev-environment-setup.md` (if exists)
- Release notes for next version

## Risk Assessment

### Breaking Change Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Package version incompatibilities | Medium | Medium | Comprehensive testing before merge |
| Python package build failures | Low | High | Test all uv installs in bookworm |
| Node.js ecosystem issues | Low | Medium | Verify pnpm installs succeed |
| AI assistant CLI breakage | Low | High | Test all AI CLIs before merging |
| MCP server failures | Low | Critical | Run MCP health checks |

### Security Improvements

| Improvement | Severity Addressed | Impact |
|-------------|-------------------|--------|
| Eliminate CVE-2025-4330 | Medium | Bookworm not affected |
| Faster security patches | High | Active Debian stable support |
| Remove setuptools GHSA-r9hx-vwmv-q579 | Medium | Fixed in bookworm Python packages |
| Reduce future CVE exposure | High | Current stable = priority patches |

## Testing Strategy

### Automated Testing

```bash
# 1. Build Dockerfile
docker build -f .devcontainer/Dockerfile -t flowspec-bookworm:test .

# 2. Run test suite in container
docker run --rm flowspec-bookworm:test pytest tests/

# 3. Verify Python tools
docker run --rm flowspec-bookworm:test uv --version
docker run --rm flowspec-bookworm:test python --version

# 4. Check installed packages
docker run --rm flowspec-bookworm:test pnpm --version
docker run --rm flowspec-bookworm:test gh --version
```

### Manual Testing

```bash
# 1. Open devcontainer in VS Code
# 2. Verify Python environment
python --version  # Should be 3.11.x
uv --version
pytest --version

# 3. Test package installation
uv pip install requests
python -c "import requests; print(requests.__version__)"

# 4. Test AI assistant CLIs
claude --version
copilot --version

# 5. Test MCP servers
./scripts/bash/check-mcp-servers.sh

# 6. Run full test suite
pytest tests/
```

### Success Criteria

- [ ] Dockerfile builds without errors
- [ ] Image size within 10% of bullseye image (~1.5GB)
- [ ] All pytest tests pass
- [ ] AI assistant CLIs functional
- [ ] MCP servers operational
- [ ] VS Code devcontainer opens successfully
- [ ] No regressions in developer workflow

## Consequences

### Positive

- **Enhanced security posture**: Eliminates known CVEs, receives active security patches
- **Compliance readiness**: Moves to current stable Debian release
- **Reduced technical debt**: Proactive migration vs. emergency response
- **Future-proofing**: Debian 12 supported until ~2028 (5 years LTS)

### Negative

- **Testing overhead**: Requires comprehensive validation before merge
- **Potential package differences**: Minor version bumps in system libraries
- **One-time migration cost**: ~2-4 hours total effort

### Neutral

- **Image size**: Comparable to bullseye (~1.5GB)
- **Developer experience**: Should be transparent to users
- **Performance**: No significant performance differences expected

## Success Metrics

**Post-migration validation**:
- [ ] Zero CVEs reported in Docker image scans (trivy, grype)
- [ ] All CI/CD pipelines pass with bookworm images
- [ ] No developer-reported issues within 2 weeks
- [ ] MCP server health checks pass consistently

## References

- [Debian Releases: Bullseye LTS Status](https://www.debian.org/releases/bullseye/)
- [Debian Releases: Bookworm (current stable)](https://www.debian.org/releases/bookworm/)
- [Microsoft Devcontainers Python Images](https://github.com/devcontainers/images/tree/main/src/python)
- [GHSA-r9hx-vwmv-q579: setuptools vulnerability](https://github.com/advisories/GHSA-r9hx-vwmv-q579)
- [CVE-2025-4330: Not affected in Bookworm](https://security-tracker.debian.org/tracker/CVE-2025-4330)

## Related Tasks

- task-xxx: Migrate Dockerfile to Bookworm
- task-xxx: Migrate devcontainer.json to Bookworm
- task-xxx: Test Bookworm Migration End-to-End
- task-xxx: ADR: Docker Base Image Migration to Bookworm

## Approval

**Security Review**: Required before implementation
**Architecture Review**: Required (this ADR)
**Implementation Owner**: TBD

---

**Next Steps**:
1. Review and approve this ADR
2. Create implementation tasks in backlog
3. Execute migration in test environment
4. Validate all functionality
5. Merge to main branch
6. Monitor for issues
