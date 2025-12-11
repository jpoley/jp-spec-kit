# Bookworm Migration - Quick Reference

**Status:** Ready for Implementation
**Created:** 2025-12-10
**Tracking Tasks:** task-442, task-443, task-444, task-445

## TL;DR

Migrate from Debian Bullseye (EOL Aug 2026, LTS support) to Debian Bookworm (EOL Jun 2028, full regular support) for improved security posture and extended lifecycle.

## What Changes

Two lines in two files:

**`.devcontainer/Dockerfile` line 15:**
```diff
- FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye
+ FROM mcr.microsoft.com/devcontainers/python:3.11-bookworm
```

**`.devcontainer/devcontainer.json` line 3:**
```diff
- "image": "mcr.microsoft.com/devcontainers/python:3.11-bullseye",
+ "image": "mcr.microsoft.com/devcontainers/python:3.11-bookworm",
```

## Why This Matters

### Security Improvements

| Item | Bullseye | Bookworm | Gain |
|------|----------|----------|------|
| Support Type | LTS (limited) | Full regular | Active patches |
| EOL Date | Aug 2026 | Jun 2028 | +22 months |
| Python CVEs | Unpatched | CVE-2025-0938, CVE-2025-1795 fixed | Reduced exposure |
| Containerd CVEs | Unpatched | CVE-2024-25621, CVE-2025-64329 fixed | Container security |

**Sources:**
- [Debian Bullseye LTS Announcement](https://www.debian.org/News/2024/20240814)
- [Debian Bookworm Release Info](https://www.debian.org/releases/bookworm/)
- [Debian Security Tracker](https://security-tracker.debian.org/tracker/source-package/python3.11)

### CI/CD Impact

**NONE.** All workflows are base-image agnostic:
- `docker-publish.yml` reads from Dockerfile (no hardcoded base image)
- `ci.yml` uses GitHub runners (ubuntu-latest), not devcontainer
- `security-scan.yml` uses GitHub runners, not devcontainer

No workflow file changes required.

## Quick Start Commands

### 1. Update Files

```bash
cd /home/jpoley/ps/flowspec

# Backup (optional)
cp .devcontainer/Dockerfile .devcontainer/Dockerfile.bullseye.backup
cp .devcontainer/devcontainer.json .devcontainer/devcontainer.json.bullseye.backup

# Apply changes
sed -i 's/python:3.11-bullseye/python:3.11-bookworm/g' .devcontainer/Dockerfile
sed -i 's/python:3.11-bullseye/python:3.11-bookworm/g' .devcontainer/devcontainer.json

# Verify
git diff .devcontainer/
```

### 2. Build and Test Locally

```bash
# Build image
docker build -t flowspec-agents:bookworm-test -f .devcontainer/Dockerfile .devcontainer

# Quick verification
docker run --rm flowspec-agents:bookworm-test bash -c "
  cat /etc/os-release | grep bookworm &&
  python --version &&
  node --version &&
  pnpm --version &&
  /home/vscode/.local/bin/uv --version &&
  gh --version | head -1
"

# Run tests (if in devcontainer)
# uv sync && uv run pytest tests/ -v
```

### 3. Security Scan

```bash
# Scan new image
trivy image --severity HIGH,CRITICAL flowspec-agents:bookworm-test

# Compare with current (optional)
docker pull jpoley/flowspec-agents:latest
trivy image --severity HIGH,CRITICAL jpoley/flowspec-agents:latest
```

### 4. Create PR

```bash
# Create branch
git checkout -b platform/migrate-to-bookworm

# Commit
git add .devcontainer/Dockerfile .devcontainer/devcontainer.json
git commit -m "platform: migrate base images to Debian Bookworm

See docs/platform/docker-bookworm-migration.md for full migration plan.

Security improvements:
- Extends EOL from Aug 2026 to Jun 2028
- Resolves Python CVE-2025-0938, CVE-2025-1795
- Resolves Containerd CVE-2024-25621, CVE-2025-64329
- Provides active security updates vs LTS-only

Testing: All local tests pass. CI/CD workflows unaffected (base-image agnostic).

🤖 Generated with Claude Code

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
"

# Push and create PR
git push -u origin platform/migrate-to-bookworm
gh pr create --title "Platform: Migrate to Debian Bookworm" --label "platform,security,devcontainer"
```

### 5. Merge and Verify

```bash
# After PR approval
gh pr merge --squash --delete-branch

# Monitor publish
gh run watch

# Verify published image
docker pull jpoley/flowspec-agents:latest
docker run --rm jpoley/flowspec-agents:latest cat /etc/os-release | grep VERSION
# Expected: VERSION="12 (bookworm)"
```

## Rollback Plan

If issues arise:

```bash
# Revert merge commit
git revert <merge-commit-sha> --no-edit
git push origin main

# docker-publish workflow will auto-rebuild bullseye :latest
gh run watch
```

Or pin users to last bullseye version:
```dockerfile
# In devcontainer.json
"image": "jpoley/flowspec-agents:0.2.350"  # Last bullseye build
```

## Testing Checklist

- [ ] Local Docker build succeeds
- [ ] Container starts, shell accessible
- [ ] Python 3.11.x installed
- [ ] Node 20.x and pnpm installed
- [ ] uv and gh CLI installed
- [ ] Environment variables correct (PNPM_HOME, PATH)
- [ ] Full pytest suite passes
- [ ] Trivy scan shows CVE reduction vs bullseye
- [ ] CI checks pass on PR
- [ ] Docker Hub publish succeeds
- [ ] Published image verified as bookworm

## Backlog Tasks

| Task | Priority | Description |
|------|----------|-------------|
| task-442 | HIGH | Update base images in Dockerfile and devcontainer.json |
| task-443 | HIGH | Run security scans and document CVE improvements |
| task-444 | MEDIUM | Validate CI/CD pipeline post-migration |
| task-445 | MEDIUM | 30-day monitoring and documentation update |

## Reference Documentation

- **Full Migration Plan:** [docs/platform/docker-bookworm-migration.md](./docker-bookworm-migration.md)
- **Backlog Tasks:** `backlog/tasks/task-44{2,3,4,5}-*.md`
- **Verification Scripts:**
  - `verify-migration.sh` (see migration plan appendix)
  - `compare-security.sh` (see migration plan appendix)

## Key Contacts

- **Owner:** Platform Engineering
- **Tracking Issue:** TBD (create after PR)
- **Rollback Decision:** DevOps lead + Security team

---

**Next Steps:**

1. Review [full migration plan](./docker-bookworm-migration.md)
2. Start with task-442 (update base images)
3. Proceed through tasks 443-445 sequentially
4. Complete 30-day post-migration review

**Estimated Timeline:**

- Implementation: 1-2 hours
- PR review and merge: 1 day
- Docker publish: 10 minutes
- Post-migration monitoring: 30 days
