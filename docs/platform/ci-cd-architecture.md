# CI/CD Architecture - Local-First DevOps

**Date:** 2025-12-04
**Related Tasks:** task-085, task-168
**Related ADRs:** ADR-016-cicd-pipeline-design

---

## Overview

JP Spec Kit implements a **local-first CI/CD architecture** using **act** (GitHub Actions local runner) to shift testing left and achieve DORA Elite metrics.

### Key Principles

1. **Inner Loop Optimization** - Fast local feedback (<1 min)
2. **Environment Parity** - Local == CI (same Docker images)
3. **Fail Fast** - Catch issues before push
4. **Selective Execution** - Run only necessary jobs

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│ DEVELOPER WORKFLOW                                   │
│                                                      │
│  ┌────────────────────────────────────┐             │
│  │ Inner Loop (Local)                │             │
│  │                                    │             │
│  │  1. Make changes                  │             │
│  │  2. run-local-ci.sh               │             │
│  │     ├─ Lint (ruff)                │             │
│  │     ├─ Test (pytest)              │             │
│  │     ├─ Build (uv build)           │             │
│  │     └─ Security (semgrep)         │             │
│  │  3. Fix issues (<1 min feedback)  │             │
│  │  4. git push (pre-validated)      │             │
│  │                                    │             │
│  │  Performance: <1 minute            │             │
│  └────────────────┬───────────────────┘             │
│                   │                                  │
│                   │ git push                         │
│                   │                                  │
│  ┌────────────────▼───────────────────┐             │
│  │ Outer Loop (GitHub Actions)       │             │
│  │                                    │             │
│  │  1. Triggers on push/PR            │             │
│  │  2. Matrix (Linux, macOS, Win)     │             │
│  │  3. Full test suite                │             │
│  │  4. Security (Semgrep, CodeQL)     │             │
│  │  5. Publish artifacts              │             │
│  │                                    │             │
│  │  Performance: 8-12 minutes         │             │
│  └────────────────────────────────────┘             │
└──────────────────────────────────────────────────────┘
```

---

## run-local-ci.sh

**Location:** `scripts/bash/run-local-ci.sh`

**Usage:**
```bash
# Run default jobs (lint, test, build, security)
./scripts/bash/run-local-ci.sh

# Run specific jobs
./scripts/bash/run-local-ci.sh -j lint -j test

# List available jobs
./scripts/bash/run-local-ci.sh --list

# Install act if missing
./scripts/bash/run-local-ci.sh --install-act
```

**Features:**
- Auto-install act (binary download from GitHub releases)
- Dependency checking (Docker, act)
- Selective job execution
- Fail-fast on first error
- Cross-platform (Linux, macOS)

---

## GitHub Actions CI Matrix

**File:** `.github/workflows/ci.yml`

**Matrix:**
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest]
    python-version: ["3.11", "3.12"]
```

**Jobs:**
- **lint** - ruff check, ruff format, mypy
- **test** - pytest with coverage
- **build** - uv build, twine check
- **security** - Semgrep SAST

**Execution Time:**
- Linux: 5-7 minutes
- macOS: 6-8 minutes (slower runners)

---

## DORA Metrics Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Lead Time | 2-4 hours | <1 hour | 75% faster |
| Deploy Freq | 1/day | 5-10/day | 5-10x more |
| CFR | 25-30% | <15% | 50% reduction |
| MTTR | 2-4 hours | <1 hour | 75% faster |

**Explanation:**
- **Lead Time:** Local CI catches issues in <1 min (vs 5-10 min GitHub)
- **Deploy Freq:** Fast feedback encourages small, frequent commits
- **CFR:** Pre-validated commits fail less often
- **MTTR:** Fast local iteration for fixes

---

## act Limitations

### 1. OIDC Not Supported
- **Impact:** Can't authenticate with cloud providers
- **Workaround:** Skip cloud deployment jobs locally

### 2. GitHub Secrets Not Available
- **Impact:** `secrets.GITHUB_TOKEN` not accessible
- **Workaround:** Use `.secrets` file (add to .gitignore)

### 3. Some Actions Don't Work
- **Impact:** actions/cache, etc. may fail
- **Workaround:** Use `-j <job>` to skip problematic jobs

### 4. Docker Required
- **Impact:** act requires Docker daemon
- **Workaround:** Provide native script fallback

---

## Cross-Platform Testing

### Linux (Primary)
- CI Matrix: ubuntu-latest
- Local CI: act with ubuntu:act-latest
- Docker: Widely available

### macOS (task-168)
- CI Matrix: macos-latest
- Local CI: act with macOS runner (experimental)
- Docker: Docker Desktop required

### Windows (Future)
- CI Matrix: windows-latest (planned)
- Local CI: Limited act support
- Docker: WSL2 + Docker Desktop

---

## Cost Optimization

### Before Local CI
- 100 commits/month
- 30% fail first run (30 failures)
- 130 total CI runs × 5 min = 650 min
- Cost: $0 (within free tier)
- **Developer time wasted: 10.8 hours = $540**

### After Local CI
- 100 commits/month
- 30 failures caught locally
- 70 successful commits × 5 min = 350 min
- Cost: $0 (within free tier)
- **Developer time saved: 2 hours = $100/month**

---

## Implementation Phases

### Phase 1: Core Script (Week 1)
- Implement run-local-ci.sh
- Auto-install act
- Test on Linux

### Phase 2: CI Matrix (Week 2)
- Add macos-latest to matrix
- Verify cross-platform compatibility

### Phase 3: Documentation (Week 3)
- Update CLAUDE.md
- Troubleshooting guide
- act limitations documentation

---

## Success Criteria

- [ ] Lead time <1 hour (Elite)
- [ ] Deployment frequency >1/day (Elite)
- [ ] Change failure rate <15% (Elite)
- [ ] MTTR <1 hour (Elite)
- [ ] GitHub Actions usage reduced by 50%
- [ ] Developer NPS >40 ("Local CI is fast and reliable")
