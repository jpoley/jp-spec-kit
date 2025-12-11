# Docker Bookworm Migration Plan

**Status:** Planned
**Migration Date:** TBD
**Owner:** Platform Engineering
**Risk Level:** Low

## Executive Summary

This document outlines the migration strategy from Debian Bullseye to Debian Bookworm base images for the flowspec-agents development container. The migration addresses critical security vulnerabilities and extends our support lifecycle.

## Security Rationale

### Current State (Bullseye)

- **Release:** Debian 11 "Bullseye"
- **Current Support Status:** Long Term Support (LTS) phase since August 14, 2024
- **End of Life:** August 31, 2026
- **Security Posture:** Regular security updates transitioned to LTS team
- **Known Issues:**
  - CVE-2024-46901 (svn vulnerability)
  - CVE-2022-40897 (Python setuptools)
  - Additional CVEs accumulating during LTS phase

**Source:** [Debian Security Support for Bullseye](https://www.debian.org/News/2024/20240814)

### Target State (Bookworm)

- **Release:** Debian 12 "Bookworm"
- **Current Support Status:** Full regular support
- **Regular Support End:** June 10, 2026
- **End of Life (LTS End):** June 30, 2028
- **Security Posture:** Active regular security updates from main Debian team
- **Recent Security Fixes:**
  - CVE-2025-0938 (Python 3.11)
  - CVE-2025-1795 (Python 3.11)
  - CVE-2024-25621 (Containerd)
  - CVE-2025-64329 (Containerd)

**Source:** [Debian Bookworm Release Information](https://www.debian.org/releases/bookworm/)

### Security Improvement Summary

| Metric | Bullseye | Bookworm | Improvement |
|--------|----------|----------|-------------|
| Support Type | LTS | Full Regular | Active maintenance |
| Support Team | LTS Team | Main Security Team | Faster patches |
| EOL Date | Aug 2026 | Jun 2028 | +22 months |
| Package Updates | Conservative | Current | Latest stable |
| CVE Response Time | Slower (LTS) | Fast (regular) | Reduced exposure window |

**Additional References:**
- [Microsoft Dev Container Python Images](https://mcr.microsoft.com/en-us/product/devcontainers/python/about)
- [Debian Release Lifecycle](https://endoflife.date/debian)
- [Debian Security Tracker - Python 3.11](https://security-tracker.debian.org/tracker/source-package/python3.11)

## SLSA Compliance Implications

### Build Provenance (SLSA Level 2+)

The base image change impacts our SLSA compliance posture:

**Current:** `mcr.microsoft.com/devcontainers/python:3.11-bullseye`
- Provenance includes Bullseye package manifests
- Build reproducibility tied to Bullseye package versions

**Target:** `mcr.microsoft.com/devcontainers/python:3.11-bookworm`
- Updated provenance with Bookworm package manifests
- Improved reproducibility due to newer package ecosystem
- Better alignment with Microsoft's current support model

**Action Required:**
- Update SBOM generation after migration
- Verify provenance attestations reference correct base image
- Update security scanning baselines

### Supply Chain Security

Migration improves supply chain security through:
1. **Shorter vulnerability window:** Active security updates vs LTS-only
2. **Upstream alignment:** Microsoft recommends running `apt-get upgrade` for locked versions
3. **Dependency freshness:** Bookworm includes newer secure-by-default packages

## CI/CD Pipeline Impact

### Affected Workflows

#### 1. `.github/workflows/docker-publish.yml`

**Current Behavior:**
- Builds multi-platform images (linux/amd64, linux/arm64)
- Publishes to `jpoley/flowspec-agents` on Docker Hub
- Runs Trivy security scans post-publish
- Triggers on:
  - Release publication (creates version tags)
  - Dockerfile changes to main (updates :latest)
  - Manual workflow_dispatch

**Changes Required:** NONE

The workflow is base-image agnostic. It reads the Dockerfile and builds whatever base image is specified. No workflow file modifications needed.

**Verification Steps:**
1. Workflow will automatically detect Dockerfile change
2. Build time may vary (+/- 5-10% depending on package availability)
3. Trivy scan will run against new bookworm-based image
4. Compare scan results: `docker-publish` workflow artifacts

#### 2. `.github/workflows/ci.yml`

**Current Behavior:**
- Runs on `ubuntu-latest` GitHub runners (NOT in devcontainer)
- Uses `actions/setup-python@v5` with Python 3.11
- Jobs: lint, test, build, security

**Changes Required:** NONE

CI workflow does not use devcontainer images. It uses GitHub-hosted runners with Python installed via actions. Base image change has zero impact.

#### 3. `.github/workflows/security-scan.yml`

**Current Behavior:**
- Installs dependencies via `uv pip install --system .`
- Runs Semgrep security scanning
- Uploads SARIF results to GitHub Security tab

**Changes Required:** NONE

Security scanning runs on GitHub runners, not devcontainer. No changes needed.

### Docker Hub Publishing

**Publishing Strategy:**

The existing workflow handles version tagging automatically:

```yaml
tags: |
  type=raw,value=latest,enable={{is_default_branch}}
  type=semver,pattern={{version}}
  type=semver,pattern={{major}}.{{minor}}
  type=sha,prefix=sha-
  type=ref,event=branch
```

**After Migration:**

1. **On PR Merge to Main:**
   - Triggers `docker-publish.yml` (Dockerfile changed)
   - Builds bookworm-based image
   - Publishes to `jpoley/flowspec-agents:latest`
   - Tags: `latest`, `sha-<commit>`, `main`

2. **On Next Release (e.g., v0.2.351):**
   - Triggers `docker-publish.yml` (release published)
   - Builds bookworm-based image
   - Publishes to `jpoley/flowspec-agents:0.2.351`, `0.2`, `:latest`

**Backward Compatibility:**

Users pinned to `:latest` will automatically get bookworm after merge.
Users pinned to specific versions (e.g., `0.2.350`) will remain on bullseye.

**Action Required:**
- Update Docker Hub repository description to note bookworm migration date
- Consider tagging the last bullseye build: `docker tag jpoley/flowspec-agents:latest jpoley/flowspec-agents:bullseye-final`

### Build Time and Image Size Projections

**Expected Changes:**

| Metric | Current (Bullseye) | Projected (Bookworm) | Delta |
|--------|--------------------|----------------------|-------|
| Build Time (cold) | ~5-8 min | ~5-10 min | +0-2 min |
| Build Time (cached) | ~2-3 min | ~2-3 min | No change |
| Image Size (compressed) | ~400-500 MB | ~400-550 MB | +0-50 MB |
| Image Size (uncompressed) | ~1.2-1.5 GB | ~1.2-1.6 GB | +0-100 MB |

**Factors:**
- Bookworm packages may have slightly different sizes
- Additional security patches in bookworm may increase size marginally
- Build cache (GitHub Actions cache) remains effective

**Verification:**
```bash
# Compare image sizes
docker images jpoley/flowspec-agents --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
```

## Migration Implementation Plan

### Phase 1: Update Base Images

**Duration:** 5 minutes
**Risk:** Low

#### Files to Modify

**1. `.devcontainer/Dockerfile` (Line 15)**

```diff
- FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye
+ FROM mcr.microsoft.com/devcontainers/python:3.11-bookworm
```

**2. `.devcontainer/devcontainer.json` (Line 3)**

```diff
- "image": "mcr.microsoft.com/devcontainers/python:3.11-bullseye",
+ "image": "mcr.microsoft.com/devcontainers/python:3.11-bookworm",
```

**Execution:**

```bash
cd /home/jpoley/ps/flowspec

# Backup current files
cp .devcontainer/Dockerfile .devcontainer/Dockerfile.bullseye.backup
cp .devcontainer/devcontainer.json .devcontainer/devcontainer.json.bullseye.backup

# Apply changes (use sed or manual edit)
sed -i 's/python:3.11-bullseye/python:3.11-bookworm/g' .devcontainer/Dockerfile
sed -i 's/python:3.11-bullseye/python:3.11-bookworm/g' .devcontainer/devcontainer.json

# Verify changes
git diff .devcontainer/
```

### Phase 2: Local Validation

**Duration:** 20-30 minutes
**Risk:** Low

#### Step 1: Build Docker Image Locally

```bash
cd /home/jpoley/ps/flowspec

# Build the image
docker build -t flowspec-agents:bookworm-test -f .devcontainer/Dockerfile .devcontainer

# Verify build success
echo $?  # Should be 0
```

**Expected Output:**
- All installation steps complete successfully
- Verification step shows tool versions
- Final CMD sets to zsh

#### Step 2: Test Container Functionality

```bash
# Run container interactively
docker run -it --rm flowspec-agents:bookworm-test bash

# Inside container, verify:
# 1. Python version
python --version
# Expected: Python 3.11.x

# 2. Node.js and pnpm
node --version
pnpm --version
# Expected: Node 20.x, pnpm 9.x

# 3. uv package manager
/home/vscode/.local/bin/uv --version
# Expected: uv 0.x.x

# 4. GitHub CLI
gh --version
# Expected: gh version 2.x.x

# 5. Environment variables
echo $PNPM_HOME
echo $PATH
# Expected: Correct paths set

# 6. User context
whoami
# Expected: vscode

# Exit container
exit
```

#### Step 3: Run Full Test Suite

```bash
cd /home/jpoley/ps/flowspec

# Option A: Test in devcontainer (VS Code)
# 1. Reopen folder in container
# 2. Wait for container rebuild
# 3. Run: uv sync
# 4. Run: uv run pytest tests/ -v

# Option B: Test in standalone container
docker run -it --rm \
  -v "$PWD:/workspace" \
  -w /workspace \
  flowspec-agents:bookworm-test \
  bash -c "uv sync && uv run pytest tests/ -v"
```

**Success Criteria:**
- All tests pass
- No import errors
- No environment-related failures

#### Step 4: Verify Installed Tools

Create and run a comprehensive verification script:

```bash
cat > /tmp/verify-bookworm.sh << 'EOF'
#!/bin/bash
set -e

echo "=== Bookworm Migration Verification ==="
echo ""

echo "1. Base Image:"
cat /etc/os-release | grep VERSION=
echo ""

echo "2. Python:"
python --version
python -c "import sys; print(f'  Prefix: {sys.prefix}')"
echo ""

echo "3. Node.js and pnpm:"
node --version
pnpm --version
echo ""

echo "4. uv Package Manager:"
/home/vscode/.local/bin/uv --version
echo ""

echo "5. GitHub CLI:"
gh --version | head -1
echo ""

echo "6. Python Tools (via uv):"
/home/vscode/.local/bin/uv tool list
echo ""

echo "7. Environment:"
echo "  PNPM_HOME=$PNPM_HOME"
echo "  PATH=$PATH"
echo ""

echo "8. User Context:"
echo "  User: $(whoami)"
echo "  Home: $HOME"
echo ""

echo "=== All Checks Passed ==="
EOF

chmod +x /tmp/verify-bookworm.sh

# Run verification in container
docker run -it --rm flowspec-agents:bookworm-test /bin/bash -c "$(cat /tmp/verify-bookworm.sh)"
```

**Expected Output:**
```
=== Bookworm Migration Verification ===

1. Base Image:
VERSION="12 (bookworm)"

2. Python:
Python 3.11.x
  Prefix: /usr/local

3. Node.js and pnpm:
v20.x.x
9.x.x

4. uv Package Manager:
uv 0.x.x

5. GitHub CLI:
gh version 2.x.x

6. Python Tools (via uv):
ruff
pytest

7. Environment:
  PNPM_HOME=/home/vscode/.local/share/pnpm
  PATH=/home/vscode/.local/bin:/home/vscode/.local/share/pnpm:...

8. User Context:
  User: vscode
  Home: /home/vscode

=== All Checks Passed ===
```

### Phase 3: Security Validation

**Duration:** 10-15 minutes
**Risk:** Low

#### Step 1: Run Trivy Security Scan

```bash
# Install trivy if not available
# Ubuntu/Debian:
# wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
# echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
# sudo apt-get update && sudo apt-get install trivy

# Scan new bookworm image
trivy image --severity HIGH,CRITICAL flowspec-agents:bookworm-test > /tmp/trivy-bookworm.txt

# For comparison, scan current bullseye image (if available locally)
docker pull jpoley/flowspec-agents:latest  # Current bullseye image
trivy image --severity HIGH,CRITICAL jpoley/flowspec-agents:latest > /tmp/trivy-bullseye.txt

# Compare results
echo "=== Bullseye CVE Count ==="
grep "Total:" /tmp/trivy-bullseye.txt || echo "No summary found"

echo ""
echo "=== Bookworm CVE Count ==="
grep "Total:" /tmp/trivy-bookworm.txt || echo "No summary found"

# Detailed comparison
diff -u /tmp/trivy-bullseye.txt /tmp/trivy-bookworm.txt || echo "Differences found (expected)"
```

#### Step 2: Generate Security Report

```bash
cd /home/jpoley/ps/flowspec

# Run comprehensive security scan with JSON output
trivy image --format json --output docs/platform/bookworm-security-scan.json \
  flowspec-agents:bookworm-test

# Generate SARIF for GitHub Security tab
trivy image --format sarif --output docs/platform/bookworm-security-scan.sarif \
  flowspec-agents:bookworm-test

# Human-readable report
trivy image --severity HIGH,CRITICAL --format table \
  flowspec-agents:bookworm-test > docs/platform/bookworm-security-report.txt
```

#### Step 3: Document Security Posture Improvement

Create summary report:

```bash
cat > docs/platform/bookworm-security-summary.md << 'EOF'
# Bookworm Migration Security Summary

**Scan Date:** $(date -I)
**Image:** flowspec-agents:bookworm-test

## CVE Count Comparison

| Severity | Bullseye | Bookworm | Delta |
|----------|----------|----------|-------|
| CRITICAL | X        | Y        | -Z    |
| HIGH     | A        | B        | -C    |
| MEDIUM   | D        | E        | -F    |
| LOW      | G        | H        | -I    |

## Key Improvements

1. **OS Security Updates:** Bookworm includes latest Debian stable security patches
2. **Python 3.11 Patches:** CVE-2025-0938, CVE-2025-1795 fixed in bookworm
3. **Containerd Updates:** CVE-2024-25621, CVE-2025-64329 addressed
4. **Support Lifecycle:** Extended from Aug 2026 to Jun 2028 (EOL)

## Resolved CVEs

List of CVEs resolved by migrating to bookworm:
- CVE-XXXX-XXXX: Description
- CVE-YYYY-YYYY: Description

## Remaining CVEs

CVEs still present (if any):
- CVE-ZZZZ-ZZZZ: Description (mitigation: ...)

## Recommendation

**APPROVED FOR PRODUCTION**

The migration to Bookworm significantly improves our security posture with [X] fewer critical and [Y] fewer high-severity vulnerabilities. All functional tests passed.
EOF

# Fill in actual numbers after scans complete
```

### Phase 4: CI/CD Updates

**Duration:** 5 minutes
**Risk:** Low

#### Review Workflow Files

**No changes required** to workflow files. The workflows are base-image agnostic.

**Verification Checklist:**

```bash
cd /home/jpoley/ps/flowspec

# 1. Check docker-publish.yml references Dockerfile (not hardcoded base image)
grep -n "file: .devcontainer/Dockerfile" .github/workflows/docker-publish.yml
# Expected: Line 66 contains the Dockerfile reference

# 2. Verify CI uses GitHub runners, not devcontainer
grep -n "runs-on:" .github/workflows/ci.yml
# Expected: All jobs use ubuntu-latest

# 3. Confirm security-scan uses system Python
grep -n "uv pip install --system" .github/workflows/security-scan.yml
# Expected: Line 97 uses system install

echo "=== No workflow changes needed ==="
```

#### Update Docker Hub Repository Description (Manual)

After successful migration and Docker Hub publish:

1. Navigate to https://hub.docker.com/r/jpoley/flowspec-agents
2. Update "Full Description" to include:

```markdown
## Migration Notice

**As of [DATE]:** This image has migrated from Debian Bullseye to Debian Bookworm.

- **Current:** `mcr.microsoft.com/devcontainers/python:3.11-bookworm`
- **Previous:** `mcr.microsoft.com/devcontainers/python:3.11-bullseye` (archived as `:bullseye-final`)

The migration provides:
- Extended security support (EOL: June 2028 vs August 2026)
- Latest security patches for Python 3.11 and Debian packages
- Improved SLSA compliance posture

For users requiring Bullseye, use tag `:bullseye-final` (version 0.2.350 or earlier).
```

### Phase 5: Commit and Publish

**Duration:** 10 minutes
**Risk:** Low

#### Create Migration PR

```bash
cd /home/jpoley/ps/flowspec

# Stage changes
git add .devcontainer/Dockerfile .devcontainer/devcontainer.json

# Check status
git status

# Create feature branch
git checkout -b platform/migrate-to-bookworm

# Commit with detailed message
git commit -m "$(cat <<'EOF'
platform: migrate base images from Bullseye to Bookworm

BREAKING CHANGE: Development container base image updated from Debian
Bullseye to Bookworm for improved security posture and extended support.

Changes:
- Update .devcontainer/Dockerfile base image to 3.11-bookworm
- Update .devcontainer/devcontainer.json image to 3.11-bookworm

Security Improvements:
- Extends support lifecycle from Aug 2026 to Jun 2028
- Resolves CVE-2025-0938, CVE-2025-1795 (Python 3.11)
- Resolves CVE-2024-25621, CVE-2025-64329 (Containerd)
- Provides active security updates vs LTS-only support

Testing Completed:
- Local Docker build successful
- Full pytest suite passes
- Trivy security scan shows X fewer critical CVEs
- All dev tools verified (Python, Node, uv, gh)

CI/CD Impact:
- No workflow changes required (base-image agnostic)
- docker-publish.yml will auto-build bookworm image on merge
- Build time impact: +0-2 minutes (negligible)

Rollback Plan:
- Revert commits to restore bullseye base images
- Docker Hub retains previous :latest as :bullseye-final

References:
- Migration Plan: docs/platform/docker-bookworm-migration.md
- Security Report: docs/platform/bookworm-security-report.txt
- Debian Lifecycle: https://endoflife.date/debian

Resolves: #XXX (link to tracking issue)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"

# Push to remote
git push -u origin platform/migrate-to-bookworm

# Create PR
gh pr create \
  --title "Platform: Migrate to Debian Bookworm base images" \
  --body "$(cat <<'EOF'
## Summary

Migrates development container base images from Debian Bullseye to Bookworm to improve security posture and extend support lifecycle.

## Security Improvements

- **Extended EOL:** August 2026 → June 2028 (+22 months)
- **Support Type:** LTS → Full regular support
- **CVEs Resolved:**
  - Python 3.11: CVE-2025-0938, CVE-2025-1795
  - Containerd: CVE-2024-25621, CVE-2025-64329
- **Trivy Scan Results:** X fewer critical, Y fewer high severity issues

## Testing Checklist

- [x] Local Docker build successful
- [x] Container starts and shell accessible
- [x] All tools verified (Python 3.11, Node 20, pnpm, uv, gh)
- [x] Full pytest suite passes (X tests)
- [x] Trivy security scan completed
- [x] devcontainer.json rebuild tested in VS Code
- [ ] CI/CD pipeline passes on this PR

## CI/CD Impact

**No workflow changes required.** All workflows are base-image agnostic.

- `docker-publish.yml`: Will auto-build bookworm on merge
- `ci.yml`: Uses GitHub runners (no devcontainer dependency)
- `security-scan.yml`: Uses GitHub runners (no impact)

## Migration Plan

See: `docs/platform/docker-bookworm-migration.md`

## Rollback Plan

If issues arise post-merge:
1. Revert this PR's commits
2. Re-run `docker-publish` workflow to rebuild bullseye :latest
3. Investigate issues before retry

## References

- [Debian Bullseye LTS Announcement](https://www.debian.org/News/2024/20240814)
- [Debian Bookworm Release Info](https://www.debian.org/releases/bookworm/)
- [Microsoft DevContainer Python Images](https://mcr.microsoft.com/en-us/product/devcontainers/python/about)
- [Debian Security Tracker](https://security-tracker.debian.org/tracker/source-package/python3.11)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" \
  --base main \
  --label "platform,security,devcontainer"
```

#### Monitor CI/CD Pipeline

After PR creation:

```bash
# Watch PR checks
gh pr checks --watch

# Expected checks:
# - CI / lint (ubuntu-latest)
# - CI / test (ubuntu-latest)
# - CI / build (ubuntu-latest)
# - CI / security (ubuntu-latest)
# All should pass (no devcontainer dependency)
```

#### Merge and Verify Publish

After PR approval:

```bash
# Merge PR
gh pr merge --squash --delete-branch

# Monitor docker-publish workflow
gh run list --workflow=docker-publish.yml --limit 5

# Watch latest run
gh run watch

# Verify published image
docker pull jpoley/flowspec-agents:latest
docker run --rm jpoley/flowspec-agents:latest /bin/bash -c "cat /etc/os-release | grep VERSION="
# Expected output: VERSION="12 (bookworm)"
```

## Rollback Strategy

### Scenario 1: Issues Found During Local Testing

**Action:** Do not commit changes.

```bash
cd /home/jpoley/ps/flowspec

# Restore backup files
cp .devcontainer/Dockerfile.bullseye.backup .devcontainer/Dockerfile
cp .devcontainer/devcontainer.json.bullseye.backup .devcontainer/devcontainer.json

# Verify restoration
git diff .devcontainer/
# Should show no changes

# Clean up test image
docker rmi flowspec-agents:bookworm-test
```

### Scenario 2: Issues Found After PR Merge

**Action:** Immediate revert.

```bash
cd /home/jpoley/ps/flowspec

# Find the merge commit
git log --oneline --grep="Bookworm" -n 1
# Example output: abc1234 Platform: Migrate to Debian Bookworm base images

# Revert the merge commit
git revert <merge-commit-sha> --no-edit

# Push revert
git push origin main

# Monitor docker-publish workflow (will rebuild bullseye)
gh run watch
```

**Rebuild Timeline:**
- Revert push triggers `docker-publish.yml`
- Build time: 5-10 minutes
- New `:latest` will be bullseye-based
- Previous bookworm build remains as `:sha-<commit>`

### Scenario 3: Users Report Issues After Publish

**Action:** Communication and pinning guidance.

```bash
# 1. Investigate reported issue
#    - Collect error logs
#    - Reproduce in bookworm container
#    - Determine if bookworm-specific

# 2. If confirmed bookworm issue:
#    - Follow Scenario 2 (revert)
#    - Add GitHub issue detailing the problem
#    - Update migration plan with findings

# 3. Provide user workaround:
#    - Pin to last bullseye version: jpoley/flowspec-agents:0.2.350
#    - Or pin to tagged bullseye-final: jpoley/flowspec-agents:bullseye-final
```

### Rollback Decision Tree

```
Issue Detected?
  ├─ During local testing (Phase 2)
  │   └─ Do not commit. Restore backups. Root cause before retry.
  │
  ├─ During PR CI checks
  │   └─ Fix in PR or close PR. Do not merge.
  │
  ├─ After merge, before Docker publish completes
  │   └─ Cancel docker-publish workflow run. Revert immediately.
  │
  └─ After Docker publish completes
      ├─ Critical issue (breaks all users)
      │   └─ Revert immediately. Hotfix priority.
      │
      ├─ Moderate issue (breaks some users)
      │   └─ Evaluate: Can we patch forward? Or revert and fix?
      │
      └─ Minor issue (workaround available)
          └─ Document workaround. Fix in next release.
```

## Monitoring Plan

### Post-Migration Observability

#### Immediate Monitoring (First 24 hours)

**1. Docker Hub Metrics**

```bash
# Check pull count and stars
# Manual check: https://hub.docker.com/r/jpoley/flowspec-agents

# Look for sudden drop in pulls (indicator of breakage)
```

**2. GitHub Issues and Discussions**

```bash
# Monitor for user-reported issues
gh issue list --label "devcontainer,bookworm" --state open

# Check for mentions of bookworm in new issues
gh issue list --search "bookworm" --state open
```

**3. CI/CD Build Success Rate**

```bash
# Monitor docker-publish workflow
gh run list --workflow=docker-publish.yml --limit 10 --json status,conclusion

# Expect all "success" conclusions
```

**4. Security Scan Results**

```bash
# Check GitHub Security tab
# URL: https://github.com/jpoley/flowspec/security/code-scanning

# Expect reduction in findings vs pre-migration baseline
```

#### Ongoing Monitoring (First 30 days)

**1. User Feedback Channels**

Monitor:
- GitHub Issues: Tag bookworm-related issues
- PR Comments: Watch for devcontainer complaints
- Docker Hub Comments: Check for negative feedback

**2. Build Reliability**

Track:
- `docker-publish` workflow success rate (target: 100%)
- Build time trends (watch for degradation)
- Image size growth (should remain stable)

**3. Security Posture**

Monthly review:
- Trivy scan results trending
- New CVEs in bookworm vs bullseye
- Debian security announcements for bookworm

#### Success Metrics

Define success criteria for 30-day checkpoint:

| Metric | Target | Current |
|--------|--------|---------|
| CI/CD build success rate | 100% | TBD |
| User-reported issues | 0 critical, <3 minor | TBD |
| Docker pulls (weekly avg) | No significant drop | TBD |
| Critical CVEs | <5 (baseline from scan) | TBD |
| High CVEs | <20 (baseline from scan) | TBD |

### Monitoring Checklist

**Week 1:**
- [ ] Daily check: GitHub Issues for bookworm mentions
- [ ] Daily check: `docker-publish` workflow status
- [ ] Trivy scan review (automated in workflow)

**Week 2-4:**
- [ ] Weekly check: GitHub Issues and PR comments
- [ ] Weekly check: Docker Hub metrics
- [ ] Weekly Trivy scan comparison

**30-Day Review:**
- [ ] Compile metrics vs success criteria
- [ ] Generate summary report
- [ ] Decision: Keep bookworm or rollback

**Post-30-Day:**
- [ ] Close migration tracking issue
- [ ] Update Docker Hub description (if not done)
- [ ] Archive bullseye backups
- [ ] Document lessons learned

## Validation Checklist

Use this checklist during migration execution:

### Pre-Migration

- [ ] Backup current Dockerfile and devcontainer.json
- [ ] Review this migration plan
- [ ] Ensure Docker installed locally
- [ ] Ensure `trivy` installed for security scanning
- [ ] Check Git working tree is clean

### Phase 1: Update Base Images

- [ ] Update `.devcontainer/Dockerfile` line 15
- [ ] Update `.devcontainer/devcontainer.json` line 3
- [ ] Verify changes: `git diff .devcontainer/`

### Phase 2: Local Validation

- [ ] Build image: `docker build -t flowspec-agents:bookworm-test -f .devcontainer/Dockerfile .devcontainer`
- [ ] Verify build success (exit code 0)
- [ ] Run container interactively and test shell access
- [ ] Verify Python 3.11.x installed
- [ ] Verify Node 20.x and pnpm installed
- [ ] Verify uv package manager installed
- [ ] Verify gh CLI installed
- [ ] Check environment variables (PNPM_HOME, PATH)
- [ ] Run full pytest suite in container
- [ ] All tests pass

### Phase 3: Security Validation

- [ ] Run Trivy scan on bookworm image
- [ ] Run Trivy scan on current bullseye image (for comparison)
- [ ] Compare CVE counts (expect reduction)
- [ ] Generate security reports (JSON, SARIF, text)
- [ ] Document CVE improvements

### Phase 4: CI/CD Updates

- [ ] Verify `docker-publish.yml` references Dockerfile (not hardcoded image)
- [ ] Verify `ci.yml` uses GitHub runners (not devcontainer)
- [ ] Verify no hardcoded "bullseye" references in workflows
- [ ] Plan Docker Hub description update

### Phase 5: Commit and Publish

- [ ] Create feature branch: `platform/migrate-to-bookworm`
- [ ] Stage changes: `.devcontainer/Dockerfile`, `.devcontainer/devcontainer.json`
- [ ] Commit with detailed message
- [ ] Push branch to remote
- [ ] Create PR with comprehensive description
- [ ] All CI checks pass on PR
- [ ] PR reviewed and approved
- [ ] Merge PR to main
- [ ] Monitor `docker-publish` workflow
- [ ] Verify new image published to Docker Hub
- [ ] Pull and test published image
- [ ] Confirm `/etc/os-release` shows "bookworm"

### Post-Migration

- [ ] Update Docker Hub repository description
- [ ] Tag last bullseye build as `:bullseye-final` (optional)
- [ ] Monitor GitHub Issues for 24 hours
- [ ] Check security scan results in GitHub Security tab
- [ ] Create 30-day review calendar reminder
- [ ] Archive migration documentation

## Appendix: Testing Commands

### Quick Verification Script

Save as `verify-migration.sh`:

```bash
#!/bin/bash
set -euo pipefail

IMAGE="${1:-flowspec-agents:bookworm-test}"

echo "=== Verifying $IMAGE ==="

# Check if image exists
if ! docker image inspect "$IMAGE" &>/dev/null; then
  echo "ERROR: Image $IMAGE not found"
  exit 1
fi

# Run verification in container
docker run --rm "$IMAGE" bash -c '
set -e

echo "1. OS Version:"
cat /etc/os-release | grep "VERSION=" | grep -q "bookworm" && echo "  ✓ Bookworm detected" || (echo "  ✗ Not bookworm"; exit 1)

echo "2. Python:"
python --version | grep -q "3.11" && echo "  ✓ Python 3.11" || (echo "  ✗ Wrong Python version"; exit 1)

echo "3. Node.js:"
node --version | grep -q "v20" && echo "  ✓ Node 20" || (echo "  ✗ Wrong Node version"; exit 1)

echo "4. pnpm:"
pnpm --version >/dev/null && echo "  ✓ pnpm installed" || (echo "  ✗ pnpm not found"; exit 1)

echo "5. uv:"
/home/vscode/.local/bin/uv --version >/dev/null && echo "  ✓ uv installed" || (echo "  ✗ uv not found"; exit 1)

echo "6. GitHub CLI:"
gh --version >/dev/null && echo "  ✓ gh installed" || (echo "  ✗ gh not found"; exit 1)

echo "7. Environment:"
[ -n "$PNPM_HOME" ] && echo "  ✓ PNPM_HOME set" || (echo "  ✗ PNPM_HOME not set"; exit 1)

echo "8. User:"
[ "$(whoami)" = "vscode" ] && echo "  ✓ Running as vscode" || (echo "  ✗ Wrong user"; exit 1)

echo ""
echo "=== All checks passed ✓ ==="
'

echo ""
echo "Image $IMAGE is ready for use."
```

Usage:
```bash
chmod +x verify-migration.sh
./verify-migration.sh flowspec-agents:bookworm-test
./verify-migration.sh jpoley/flowspec-agents:latest  # After publish
```

### Security Comparison Script

Save as `compare-security.sh`:

```bash
#!/bin/bash
set -euo pipefail

BULLSEYE_IMAGE="${1:-jpoley/flowspec-agents:latest}"
BOOKWORM_IMAGE="${2:-flowspec-agents:bookworm-test}"

echo "=== Security Comparison ==="
echo "Bullseye: $BULLSEYE_IMAGE"
echo "Bookworm: $BOOKWORM_IMAGE"
echo ""

# Scan both images
trivy image --severity CRITICAL,HIGH --format json "$BULLSEYE_IMAGE" > /tmp/bullseye-scan.json
trivy image --severity CRITICAL,HIGH --format json "$BOOKWORM_IMAGE" > /tmp/bookworm-scan.json

# Extract counts
BULLSEYE_CRITICAL=$(jq '[.Results[].Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' /tmp/bullseye-scan.json)
BULLSEYE_HIGH=$(jq '[.Results[].Vulnerabilities[]? | select(.Severity == "HIGH")] | length' /tmp/bullseye-scan.json)

BOOKWORM_CRITICAL=$(jq '[.Results[].Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' /tmp/bookworm-scan.json)
BOOKWORM_HIGH=$(jq '[.Results[].Vulnerabilities[]? | select(.Severity == "HIGH")] | length' /tmp/bookworm-scan.json)

# Calculate deltas
CRITICAL_DELTA=$((BOOKWORM_CRITICAL - BULLSEYE_CRITICAL))
HIGH_DELTA=$((BOOKWORM_HIGH - BULLSEYE_HIGH))

# Display results
echo "| Severity | Bullseye | Bookworm | Delta |"
echo "|----------|----------|----------|-------|"
echo "| CRITICAL | $BULLSEYE_CRITICAL | $BOOKWORM_CRITICAL | $CRITICAL_DELTA |"
echo "| HIGH     | $BULLSEYE_HIGH | $BOOKWORM_HIGH | $HIGH_DELTA |"
echo ""

if [ "$CRITICAL_DELTA" -le 0 ] && [ "$HIGH_DELTA" -le 0 ]; then
  echo "✓ Security improved or equal"
  exit 0
else
  echo "✗ WARNING: More vulnerabilities in bookworm"
  exit 1
fi
```

Usage:
```bash
chmod +x compare-security.sh
./compare-security.sh
```

---

**Document Version:** 1.0
**Last Updated:** 2025-12-10
**Next Review:** Post-migration (30 days after merge)
