# Galway CI/CD Pipeline Architecture

**Status**: Platform Design
**Owner**: Platform Engineer
**Last Updated**: 2025-12-04

## Executive Summary

This document defines the CI/CD pipeline architecture for all galway host tasks, targeting DORA Elite performance metrics while maintaining security, reliability, and developer experience excellence.

## DORA Elite Performance Targets

| Metric | Elite Target | Current Baseline | Galway Target |
|--------|-------------|------------------|---------------|
| **Deployment Frequency** | On-demand (multiple per day) | Per PR merge | Multiple per day |
| **Lead Time for Changes** | Less than 1 hour | ~30 minutes | < 15 minutes |
| **Change Failure Rate** | 0-15% | ~10% | < 5% |
| **Time to Restore Service** | Less than 1 hour | N/A (no prod yet) | < 30 minutes |

## Pipeline Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Developer Commit (with DCO)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Pre-commit Hooks                            │
│  • Format check (ruff format --check)                           │
│  • Lint (ruff check)                                            │
│  • Security scan (bandit, semgrep --fast)                       │
│  • Tests (pytest -x --ff)                                       │
│  • Commit message validation                                    │
│  Duration: < 30 seconds                                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        GitHub Actions CI                         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Lint Job   │  │   Test Job   │  │  Build Job   │          │
│  │  (parallel)  │  │  (parallel)  │  │  (parallel)  │          │
│  │              │  │              │  │              │          │
│  │ • ruff fmt   │  │ • pytest     │  │ • uv build   │          │
│  │ • ruff check │  │ • coverage   │  │ • SBOM gen   │          │
│  │ Duration:    │  │ Duration:    │  │ Duration:    │          │
│  │ ~1 min       │  │ ~2 min       │  │ ~1 min       │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┴─────────────────┘                   │
│                           │                                     │
│                           ▼                                     │
│              ┌─────────────────────────┐                        │
│              │    Security Job         │                        │
│              │                         │                        │
│              │ • Semgrep SAST          │                        │
│              │ • Bandit                │                        │
│              │ • pip-audit (deps)      │                        │
│              │ • SARIF upload          │                        │
│              │ Duration: ~2 min        │                        │
│              └────────────┬────────────┘                        │
│                           │                                     │
│                           ▼                                     │
│              ┌─────────────────────────┐                        │
│              │   Matrix Test Job       │                        │
│              │   (macOS/Ubuntu)        │                        │
│              │                         │                        │
│              │ • Python 3.11, 3.12     │                        │
│              │ • macOS-latest          │                        │
│              │ • ubuntu-latest         │                        │
│              │ Duration: ~3 min        │                        │
│              └────────────┬────────────┘                        │
│                           │                                     │
└───────────────────────────┼─────────────────────────────────────┘
                            │
                            ▼
               ┌─────────────────────────┐
               │    All Checks Pass      │
               │    Ready for Merge      │
               └─────────────┬───────────┘
                            │
                            ▼
               ┌─────────────────────────┐
               │   Release Workflow      │
               │   (on main merge)       │
               │                         │
               │ • Version bump          │
               │ • PyPI publish          │
               │ • GitHub Release        │
               │ • SBOM + Provenance     │
               │ Duration: ~2 min        │
               └─────────────────────────┘
```

## Pipeline Stages

### Stage 1: Pre-commit Validation (< 30 seconds)

**Purpose**: Shift-left quality gates, fail fast on developer machine

**Tools**:
- `ruff format --check .` - Format validation
- `ruff check .` - Linting
- `bandit -r src/ -ll` - Quick security scan
- `pytest tests/ -x --ff` - Fast-fail test execution

**Configuration**: `.pre-commit-config.yaml`

**Success Criteria**:
- All checks pass in < 30 seconds
- Developer gets immediate feedback
- Prevents broken commits from reaching CI

### Stage 2: Parallel Validation Jobs (1-2 minutes each)

**Lint Job**:
```yaml
lint:
  runs-on: ubuntu-latest
  steps:
    - checkout
    - setup Python 3.11
    - cache uv dependencies
    - uv sync (cached)
    - ruff format --check .
    - ruff check .
```

**Test Job**:
```yaml
test:
  runs-on: ubuntu-latest
  steps:
    - checkout
    - setup Python 3.11
    - cache uv dependencies
    - uv sync (cached)
    - pytest tests/ -v --cov --cov-report=term-missing
    - upload coverage to Codecov
```

**Build Job**:
```yaml
build:
  runs-on: ubuntu-latest
  steps:
    - checkout
    - setup Python 3.11
    - cache uv dependencies
    - uv build
    - generate SBOM (cyclonedx-py)
    - upload artifacts (dist/, SBOM)
```

**Key Optimization**: All three jobs run in parallel, reducing wall-clock time from 4 minutes sequential to 2 minutes parallel.

### Stage 3: Security Scanning (2 minutes)

**Reusable Workflow**: `.github/workflows/security-scan.yml`

**Scan Types**:
- **Incremental** (default for PRs): Only scan changed files
- **Full** (main branch): Complete codebase scan
- **Fast** (pre-commit): Changed files only, quick rules

**Tools**:
- **Semgrep**: SAST with OWASP rules
- **Bandit**: Python-specific security patterns
- **pip-audit**: Dependency vulnerability scanning

**Outputs**:
- SARIF results uploaded to GitHub Security tab
- PR comment with summary (critical/high/medium/low counts)
- Artifacts stored for 90 days

**Failure Policy**:
- Block on: Critical, High severity findings
- Warn on: Medium, Low severity findings

### Stage 4: Matrix Testing (3 minutes)

**Matrix Configuration**:
```yaml
matrix:
  os: [ubuntu-latest, macos-latest]
  python-version: ['3.11', '3.12']
```

**Purpose**:
- Validate cross-platform compatibility (Linux/macOS)
- Ensure Python version compatibility
- Catch platform-specific issues early

**Test Execution**:
- Full test suite on all matrix combinations
- Coverage reporting per combination
- Fail fast on first failure

### Stage 5: Release Automation (2 minutes)

**Triggers**:
- Merge to `main` branch
- Manual workflow dispatch with version bump type

**Steps**:
1. **Version Bump**: Update `pyproject.toml` version
2. **Build**: Create wheel and sdist distributions
3. **SBOM Generation**: CycloneDX SBOM with dependencies
4. **Provenance**: SLSA provenance attestation
5. **Publish**: Upload to PyPI (authenticated with API token)
6. **GitHub Release**: Create release with artifacts
7. **Tag**: Git tag with version number

**Artifacts**:
- `specify_cli-X.Y.Z-py3-none-any.whl`
- `specify_cli-X.Y.Z.tar.gz`
- `sbom.json` (CycloneDX format)
- `provenance.json` (SLSA attestation)

## Build Acceleration Strategies

### 1. Dependency Caching

**uv Cache**:
```yaml
- name: Cache uv dependencies
  uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: uv-${{ runner.os }}-${{ hashFiles('pyproject.toml') }}
    restore-keys: |
      uv-${{ runner.os }}-
```

**Impact**: Reduces dependency installation from 30s to 5s (83% reduction)

### 2. Parallel Job Execution

**Before** (sequential): 8 minutes total
```
lint (2m) → test (3m) → build (1m) → security (2m) = 8m
```

**After** (parallel): 3 minutes total
```
lint (2m) ─┐
test (3m) ─┼─→ security (2m) = 3m
build (1m)─┘
```

**Impact**: 62% reduction in wall-clock time

### 3. Incremental Security Scanning

**Full Scan** (main branch): ~2 minutes, scans entire codebase
**Incremental Scan** (PRs): ~30 seconds, scans only changed files

**Implementation**:
```bash
if [ "${{ github.event_name }}" == "pull_request" ]; then
  BASELINE="${{ github.event.pull_request.base.sha }}"
  specify security scan --incremental --baseline-commit=${BASELINE}
fi
```

**Impact**: 75% reduction in security scan time for PRs

### 4. Test Execution Optimization

**Pytest Options**:
- `--ff` (fail-fast): Exit on first failure
- `--lf` (last-failed): Run previously failed tests first
- `--co` (collect-only): Validate test collection without execution

**Local CI Simulation** (task-085):
```bash
#!/bin/bash
# scripts/bash/local-ci.sh
set -e

echo "Running local CI simulation..."
uv run ruff format --check .
uv run ruff check .
uv run pytest tests/ -x --ff  # Fast-fail mode
uv build
echo "✅ Local CI passed"
```

**Impact**: Developers get CI feedback in < 1 minute locally

### 5. Predictive Test Selection

**Future Enhancement** (not yet implemented):
- Analyze code changes with AST parsing
- Determine affected modules and test coverage
- Run only tests that cover changed code
- Run full suite on main branch

**Expected Impact**: 50-70% reduction in test execution time

## CI/CD Integration Points

### Task-248: Security Scanning Pipeline

**Integration Points**:
1. Pre-commit hook with `semgrep --fast`
2. PR workflow with incremental scanning
3. Main branch with full scanning
4. Security tab integration via SARIF upload

**Configuration File**: `.github/workflows/security-scan.yml`

**Implementation**:
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly full scan
```

### Task-278: Command Structure Validation

**CI Check**:
```yaml
- name: Validate command structure
  run: |
    # Ensure all .claude/commands/*.md files follow naming convention
    for cmd in .claude/commands/*.md; do
      if [[ ! $(basename "$cmd") =~ ^[a-z-]+\.md$ ]]; then
        echo "❌ Invalid command name: $cmd"
        exit 1
      fi
    done

    # Validate YAML frontmatter
    uv run python scripts/validate-commands.py
```

**Implementation**: New CI job in `ci.yml`

### Task-168: macOS CI Matrix

**Matrix Configuration**:
```yaml
test:
  strategy:
    matrix:
      os: [ubuntu-latest, macos-14]  # macos-14 = M1 chip
      python-version: ['3.11', '3.12']
```

**macOS-Specific Tests**:
- Keyring integration (macOS Keychain)
- File path handling (case-sensitive vs case-insensitive)
- Readline/readchar behavior
- Terminal color support

### Task-085: Local CI Script

**Script**: `scripts/bash/local-ci.sh`

**Features**:
- Mimics exact GitHub Actions workflow
- Parallel execution with `&` and `wait`
- Exit on first failure
- Colored output for readability

**Usage**:
```bash
./scripts/bash/local-ci.sh
# Or
uv run local-ci
```

### Task-285: Stale Task Detection

**CI Job**:
```yaml
stale-check:
  runs-on: ubuntu-latest
  steps:
    - name: Check for stale Done tasks
      run: |
        STALE=$(uv run backlog task list -s Done --plain | \
                awk -F'|' '$5 ~ /Done/ && $6 ~ /[0-9]{4}-[0-9]{2}-[0-9]{2}/ {
                  cmd="date -d \""$6"\" +%s"
                  cmd | getline task_date
                  close(cmd)
                  now = systime()
                  days_old = (now - task_date) / 86400
                  if (days_old > 7) print $2
                }')

        if [ -n "$STALE" ]; then
          echo "⚠️ Stale Done tasks (>7 days): $STALE"
          echo "Run: ./scripts/bash/archive-tasks.sh"
        fi
```

### Task-282: Backlog Archive Workflow

**Scheduled Workflow**:
```yaml
name: Archive Done Tasks
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday
  workflow_dispatch:

jobs:
  archive:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Archive Done tasks
        run: |
          ./scripts/bash/archive-tasks.sh
          if [ -n "$(git status --porcelain)" ]; then
            git config user.name "github-actions[bot]"
            git config user.email "github-actions[bot]@users.noreply.github.com"
            git add backlog/
            git commit -m "chore(backlog): archive Done tasks [skip ci]"
            git push
          fi
```

### Task-296: Agent Updates Collector CI/CD

**If Rust Service Exists**:
```yaml
agent-updates-collector:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: dtolnay/rust-toolchain@stable
    - name: Cache Cargo
      uses: actions/cache@v4
      with:
        path: |
          ~/.cargo/registry
          ~/.cargo/git
          target/
        key: cargo-${{ runner.os }}-${{ hashFiles('**/Cargo.lock') }}
    - run: cargo build --release
    - run: cargo test
    - run: cargo clippy -- -D warnings
    - run: cargo audit
```

## GitHub Actions Workflow Templates

### Reusable Matrix Test Workflow

**File**: `.github/workflows/matrix-test.yml`

```yaml
name: Matrix Test (Reusable)

on:
  workflow_call:
    inputs:
      python-versions:
        type: string
        default: '["3.11", "3.12"]'
      os-matrix:
        type: string
        default: '["ubuntu-latest", "macos-14"]'

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: ${{ fromJSON(inputs.os-matrix) }}
        python-version: ${{ fromJSON(inputs.python-versions) }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/uv
          key: uv-${{ matrix.os }}-py${{ matrix.python-version }}-${{ hashFiles('pyproject.toml') }}

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        run: uv run pytest tests/ -v --cov

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          flags: ${{ matrix.os }}-py${{ matrix.python-version }}
```

### Reusable Security Scan Workflow

**File**: `.github/workflows/security-scan.yml` (already exists, see earlier)

### Reusable Build and Publish Workflow

**File**: `.github/workflows/build-publish.yml`

```yaml
name: Build and Publish (Reusable)

on:
  workflow_call:
    inputs:
      publish-pypi:
        type: boolean
        default: false
      generate-sbom:
        type: boolean
        default: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Build package
        run: uv build

      - name: Generate SBOM
        if: ${{ inputs.generate-sbom }}
        run: |
          pip install cyclonedx-bom
          cyclonedx-py -o sbom.json --format json

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: |
            dist/
            sbom.json

      - name: Publish to PyPI
        if: ${{ inputs.publish-pypi }}
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: |
          pip install twine
          twine upload dist/*
```

## Observability Integration

### Pipeline Metrics (Prometheus)

**Metrics to Track**:
```prometheus
# Pipeline execution duration
ci_pipeline_duration_seconds{job="lint|test|build|security|release"}

# Pipeline success/failure rate
ci_pipeline_status{job="...", status="success|failure"}

# Test execution metrics
ci_test_count{suite="unit|integration|e2e"}
ci_test_duration_seconds{suite="..."}
ci_test_failures{suite="..."}

# Security scan metrics
ci_security_findings{severity="critical|high|medium|low"}
ci_security_scan_duration_seconds

# DORA metrics
deployment_frequency_per_day
lead_time_for_changes_minutes
change_failure_rate_percent
time_to_restore_minutes
```

**Collection Method**: GitHub Actions workflow outputs + webhook to metrics collector

### Structured Logging

**All CI scripts use structured logging**:
```bash
log_info() {
  echo "{\"level\":\"info\",\"time\":\"$(date -Iseconds)\",\"msg\":\"$1\"}"
}

log_error() {
  echo "{\"level\":\"error\",\"time\":\"$(date -Iseconds)\",\"msg\":\"$1\"}" >&2
}
```

### Tracing Integration (task-136: claude-trace)

**GitHub Actions Integration**:
```yaml
- name: Setup tracing
  run: |
    echo "TRACE_ENABLED=true" >> $GITHUB_ENV
    echo "TRACE_ENDPOINT=https://trace.poley.dev/v1/traces" >> $GITHUB_ENV
    echo "TRACE_SERVICE_NAME=ci-pipeline" >> $GITHUB_ENV
    echo "TRACE_RUN_ID=${{ github.run_id }}" >> $GITHUB_ENV

- name: Run tests with tracing
  run: |
    uv run pytest tests/ --trace-enabled
```

**Trace Context Propagation**:
- GitHub Actions run ID → Trace ID
- Job name → Span name
- Step name → Child span
- Logs attached as span events

## Secret Management

### Required Secrets

| Secret | Purpose | Scope |
|--------|---------|-------|
| `PYPI_TOKEN` | PyPI package publishing | Repository |
| `GITHUB_TOKEN` | Auto-provided, PR comments, releases | Automatic |
| `CODECOV_TOKEN` | Coverage upload | Repository |
| `TRACE_API_KEY` | Observability tracing | Organization |

### Secret Rotation Policy

- **Frequency**: Every 90 days
- **Automation**: GitHub Actions scheduled workflow
- **Notification**: Slack alert 7 days before expiration

## Disaster Recovery

### Pipeline Failure Scenarios

**Scenario 1: GitHub Actions Outage**

**Mitigation**:
1. Local CI script execution: `./scripts/bash/local-ci.sh`
2. Manual merge with maintainer override
3. Post-merge validation on self-hosted runner

**Scenario 2: PyPI Publishing Failure**

**Mitigation**:
1. Artifacts saved as GitHub Release attachments
2. Manual publish with `twine upload dist/*`
3. Rollback procedure: `pip install specify-cli==<previous-version>`

**Scenario 3: Security Scanner False Positive Blocking Merge**

**Mitigation**:
1. Triage with `specify security triage`
2. Add exception in `.semgrep.yml` with justification
3. Override with maintainer approval + comment explaining false positive

### Rollback Procedures

**Rolling Back a Release**:
```bash
# 1. Identify last known good version
git log --oneline --decorate

# 2. Create rollback branch
git checkout -b rollback-to-v0.0.249 v0.0.249

# 3. Cherry-pick critical fixes if needed
git cherry-pick <commit-sha>

# 4. Trigger release workflow
git tag v0.0.251
git push origin v0.0.251

# 5. Yank broken version from PyPI
twine yank specify-cli 0.0.250 --reason "Critical bug, use 0.0.251"
```

## Success Metrics

### Pipeline Health

**Target SLOs**:
- **Availability**: 99.5% (CI pipeline always runnable)
- **Latency**: P95 < 5 minutes for PR validation
- **Error Rate**: < 2% false negatives (bugs that pass CI)

**Measurement**:
```bash
# Calculate P95 latency
gh run list --workflow=ci.yml --json durationMs \
  | jq '.[] | .durationMs' \
  | sort -n \
  | awk 'BEGIN {count=0} {times[count++]=$1} END {print times[int(count*0.95)]}'
```

### Developer Experience

**Target Metrics**:
- **Time to First Feedback**: < 30 seconds (pre-commit hooks)
- **Time to PR Approval**: < 15 minutes (full CI pipeline)
- **Context Switch Reduction**: Developers can keep working while CI runs

**Developer Survey Questions** (quarterly):
1. "How satisfied are you with CI/CD speed?" (1-5 scale)
2. "How often does CI block your work unnecessarily?" (rarely/sometimes/often)
3. "What would make the CI/CD pipeline more useful?"

### DORA Metrics Tracking

**Automated Collection**:
```yaml
# .github/workflows/dora-metrics.yml
name: DORA Metrics Collection

on:
  push:
    branches: [main]
  pull_request:
    types: [closed]

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - name: Calculate deployment frequency
        run: |
          # Count deployments in last 24 hours
          DEPLOYS=$(gh run list --workflow=release.yml \
                    --created "$(date -d '24 hours ago' -Iseconds)" \
                    --json conclusion | jq '[.[] | select(.conclusion=="success")] | length')
          echo "deployments_per_day=$DEPLOYS"

      - name: Calculate lead time
        run: |
          # Time from first commit to merge
          PR_NUM=${{ github.event.pull_request.number }}
          FIRST_COMMIT=$(gh pr view $PR_NUM --json commits \
                         | jq -r '.commits[0].committedDate')
          MERGED_AT=$(gh pr view $PR_NUM --json mergedAt \
                      | jq -r '.mergedAt')
          LEAD_TIME=$(( ($(date -d "$MERGED_AT" +%s) - $(date -d "$FIRST_COMMIT" +%s)) / 60 ))
          echo "lead_time_minutes=$LEAD_TIME"

      - name: Send to metrics backend
        run: |
          curl -X POST https://metrics.poley.dev/dora \
            -H "Content-Type: application/json" \
            -d "{\"deployment_frequency\":$DEPLOYS,\"lead_time\":$LEAD_TIME}"
```

## Future Enhancements

### Phase 2: Advanced Optimizations

1. **Build Cache Warming**: Pre-populate caches before developer workday
2. **Predictive Test Selection**: AI-driven test case selection based on code changes
3. **Dynamic Resource Allocation**: Scale GitHub Actions runners based on load
4. **Canary Releases**: Gradual rollout with automatic rollback on errors

### Phase 3: Self-Hosted Runners

**When to Consider**:
- Pipeline wait time > 2 minutes due to GitHub Actions queue
- Security compliance requires on-prem execution
- Cost > $500/month for GitHub Actions minutes

**Architecture**:
```
┌─────────────────────────────────────────┐
│   GitHub Actions Controller             │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│   Kubernetes Cluster (netcon)           │
│                                         │
│   ┌─────────────────────────────────┐   │
│   │  Actions Runner Controller      │   │
│   │  (ARC by GitHub)                │   │
│   └─────────┬───────────────────────┘   │
│             │                           │
│             ▼                           │
│   ┌─────────────────┐                   │
│   │ Runner Pods     │ (auto-scale)      │
│   │ - ubuntu-runner │                   │
│   │ - macos-runner  │                   │
│   └─────────────────┘                   │
└─────────────────────────────────────────┘
```

## Appendix A: CI/CD Command Reference

```bash
# Local CI simulation
./scripts/bash/local-ci.sh

# Run specific CI job locally
act -j lint
act -j test

# Trigger manual release
gh workflow run release.yml -f version_bump=minor

# View CI logs
gh run list --workflow=ci.yml
gh run view <run-id> --log

# Debug failed CI job
gh run view <run-id> --log-failed

# Re-run failed jobs
gh run rerun <run-id> --failed

# Cancel running workflow
gh run cancel <run-id>

# View DORA metrics
gh api /repos/:owner/:repo/actions/runs \
  | jq '.workflow_runs[] | {name: .name, duration: .run_started_at, conclusion: .conclusion}'
```

## Appendix B: Related Tasks

| Task ID | Title | Integration Point |
|---------|-------|-------------------|
| task-248 | Security Scanning Pipeline | Stage 3: Security job |
| task-278 | Command Structure Validation | Stage 2: Lint job |
| task-168 | macOS CI Matrix | Stage 4: Matrix test job |
| task-085 | Local CI Script | Developer workflow |
| task-285 | Stale Task Detection | New CI job |
| task-282 | Archive Workflow | Scheduled workflow |
| task-251 | Pre-commit Hooks | Stage 1: Pre-commit |
| task-252 | Security Policy as Code | Security scan config |
| task-253 | DORA Metrics | Metrics collection |
| task-254 | Security Scanner Docker | Container build job |

## Appendix C: References

- [DORA Metrics Research](https://dora.dev/)
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/learn-github-actions/best-practices-for-workflows)
- [SLSA Framework](https://slsa.dev/)
- [Google SRE Book: CI/CD](https://sre.google/sre-book/release-engineering/)
- [Accelerate (Book)](https://itrevolution.com/product/accelerate/)
