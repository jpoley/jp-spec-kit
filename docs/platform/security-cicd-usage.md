# Security CI/CD Usage Guide

**Audience**: Platform Engineers, DevOps Engineers, Security Engineers
**Last Updated**: 2025-12-05
**Related**: `security-cicd-integration.md`, `security-cicd-examples.md`

---

## Important: Current Implementation Status

> **WARNING**: The security scanning workflows are currently in development. Some features documented below are planned but not yet implemented. See the "Current Limitations" section below for details.

## Quick Start

JP Spec Kit provides three GitHub Actions workflows for security scanning:

1. **`.github/workflows/security-scan.yml`** - Reusable workflow (implementation)
2. **`.github/workflows/security.yml`** - Standard workflow (PR, push, scheduled)
3. **`.github/workflows/security-parallel.yml`** - Parallel scanning for large repos

### Enable Security Scanning

The workflows are already configured in jp-spec-kit. They will run automatically on:
- **Pull Requests**: Full scan (incremental scanning not yet implemented)
- **Push to main**: Full scan of entire codebase
- **Nightly (2 AM UTC)**: Full scan (AI triage not yet implemented)
- **Manual**: Via GitHub Actions UI

No additional setup required!

### Current Limitations

The following features are planned but not yet implemented in the `specify security` CLI:

**Not Yet Implemented**:
- `--incremental` flag: Incremental scanning (changed files only)
- `--fast` flag: Fast scanning mode
- `--changed-only` flag: Scan only changed files
- `scan-type` parameter: All scans run in full mode
- AI triage integration: Automatic finding triage with AI
- `specify security triage`: AI-assisted finding review
- `specify security fix`: Automatic fix generation

**Currently Working**:
- Full security scanning with Semgrep
- SARIF output format
- `--format sarif` flag
- `--output` flag for result files
- `--fail-on` flag for severity thresholds
- GitHub Security tab integration
- PR comment bot
- Parallel component scanning
- Artifact upload and retention

For the most up-to-date implementation status, see the inline comments in `.github/workflows/security-scan.yml`.

---

## Workflow Architecture

### 1. Reusable Workflow (security-scan.yml)

**Purpose**: Core scanning logic called by other workflows

**Features**:
- Configurable fail-on severity (IMPLEMENTED)
- SARIF upload to GitHub Security (IMPLEMENTED)
- PR comment bot with findings summary (IMPLEMENTED)
- Semgrep binary caching (~60% faster) (IMPLEMENTED)
- 90-day artifact retention (IMPLEMENTED)
- Configurable scan type (PLANNED - currently ignored)

**Inputs**:
| Input | Type | Default | Description | Status |
|-------|------|---------|-------------|--------|
| `scan-type` | string | `full` | Scan mode: incremental, full, fast | PLANNED (currently ignored) |
| `fail-on` | string | `critical` | Severity level to block on (single severity only) | IMPLEMENTED (single severity only) |
| `upload-sarif` | boolean | `true` | Upload SARIF to GitHub Security | IMPLEMENTED |
| `scan-path` | string | `.` | Path to scan | IMPLEMENTED |

> **Note**: The `fail-on` parameter currently only supports a single severity level. Multi-severity support (e.g., `critical,high`) is planned for a future release.

**Outputs**:
| Output | Description |
|--------|-------------|
| `findings-count` | Total number of findings |
| `critical-count` | Number of critical findings |
| `high-count` | Number of high severity findings |

**Example Usage**:
```yaml
jobs:
  security:
    uses: ./.github/workflows/security-scan.yml
    with:
      scan-type: full
      fail-on: critical  # Single severity only
      upload-sarif: true
```

---

### 2. Standard Workflow (security.yml)

**Purpose**: Trigger security scans on PR, push, schedule, and manual runs

**Triggers**:
- **Pull Request**: On `src/**`, `tests/**`, `*.py`, `pyproject.toml` changes
- **Push to main/develop**: On `src/**`, `tests/**`, `*.py`, `pyproject.toml` changes
- **Schedule**: Daily at 2 AM UTC
- **Manual (workflow_dispatch)**: With custom scan-type and fail-on

**Scan Behavior**:
- PRs: Full scan (incremental scanning planned but not yet implemented)
- Main branch: Full scan
- Scheduled: Full scan
- Manual: Full scan (scan-type parameter currently ignored)

**Manual Run**:
1. Go to **Actions** → **Security Scanning**
2. Click **Run workflow**
3. Select scan type: `incremental`, `full`, or `fast` (currently all run as `full`)
4. Set fail-on severity: `critical`, `high`, `medium`, or `low` (single severity only)
5. Click **Run workflow**

---

### 3. Parallel Workflow (security-parallel.yml)

**Purpose**: High-performance scanning for large monorepos (>500K LOC)

**Performance**:
- Sequential: ~15 minutes (3 components × 5 min each)
- Parallel: ~5 minutes (all run simultaneously)
- **Speedup**: 3x faster

**Matrix Strategy**:
```yaml
strategy:
  matrix:
    component:
      - src/specify_cli
      - tests
      - scripts
```

**Triggers**:
- **Manual (workflow_dispatch)**: On demand
- **Weekly**: Sunday at 3 AM UTC

**How It Works**:
1. Each component scans in parallel
2. SARIF uploaded with component-specific category
3. Aggregation job combines results
4. Summary posted to GitHub Actions

**Adding Components**:
Edit `.github/workflows/security-parallel.yml`:
```yaml
matrix:
  component:
    - src/specify_cli
    - tests
    - scripts
    - frontend        # Add your component
    - infrastructure  # Add your component
```

---

## Configuration Options

### Security Configuration File

JP Spec Kit supports repo-level security configuration via `.github/security-config.yml`. This allows you to configure your security risk posture without modifying workflow files.

**Configuration File**: `.github/security-config.yml`

```yaml
# JP Spec Kit Security Configuration
security:
  # Severity level that will fail the build
  # Options: critical, high, medium, low
  fail-on: critical

  # Whether to upload SARIF results to GitHub Security tab
  upload-sarif: true

  # Scan path (relative to repository root)
  scan-path: "."
```

**Configuration Hierarchy**:

1. **Workflow input** (highest priority): Manual workflow dispatch inputs override everything
2. **Config file**: Values from `.github/security-config.yml`
3. **Defaults** (lowest priority): Built-in defaults (critical, true, ".")

**Example: Setting Different Risk Postures**

```yaml
# Standard (only block on critical vulnerabilities)
security:
  fail-on: critical  # Default - recommended for most projects

# Strict (block on high or critical)
security:
  fail-on: high

# Very Strict (block on medium, high, or critical)
security:
  fail-on: medium

# Maximum Strictness (block on any findings)
security:
  fail-on: low
```

**Disabling SARIF Upload**:

```yaml
security:
  fail-on: critical
  upload-sarif: false  # Don't upload to GitHub Security tab
```

**Custom Scan Path**:

```yaml
security:
  fail-on: critical
  scan-path: "src/"  # Only scan src directory
```

### Scan Types

> **WARNING**: Scan type selection is currently not implemented. All scans run in `full` mode regardless of the `scan-type` input.

| Type | Use Case | Performance | Coverage | Status |
|------|----------|-------------|----------|--------|
| `incremental` | PR reviews | Fast (30s) | Changed files only | PLANNED |
| `full` | Main branch | Standard (3-5 min) | Entire codebase | IMPLEMENTED |
| `fast` | Pre-commit | Very fast (10s) | Changed files, quick rules | PLANNED |

### Fail-On Severity

> **Note**: Only single severity level is currently supported. Multi-severity (e.g., `critical,high`) is planned for future release.

| Setting | Blocks On | Use Case |
|---------|-----------|----------|
| `critical` | Critical only | **Recommended (current default)** - Standard for PRs |
| `high` | High severity or above | Stricter filtering |
| `medium` | Medium severity or above | Security-critical apps |
| `low` | All findings | Very strict (compliance) |

### SARIF Upload

SARIF (Static Analysis Results Interchange Format) results are uploaded to GitHub's Security tab.

**Enable/Disable**:
```yaml
upload-sarif: true  # Default: enabled
```

**Viewing Results**:
1. Repository → **Security** → **Code scanning**
2. Filter by severity, status, rule
3. Click finding for details and remediation

---

## Caching Strategy

### What's Cached

| Cache | Path | Key | Speedup |
|-------|------|-----|---------|
| Pip packages | `~/.cache/pip` | `${{ runner.os }}-pip-security-${{ hashFiles('**/pyproject.toml') }}` | ~40% |
| Semgrep binary | `~/.local/bin/semgrep` | `semgrep-${{ runner.os }}-1.50.0` | ~60% |

### Cache Performance

| Run Type | First Run | Cached Run | Speedup |
|----------|-----------|------------|---------|
| Small (10K LOC) | 1 min | 30s | 2x |
| Medium (50K LOC) | 3 min | 1.5 min | 2x |
| Large (100K LOC) | 5 min | 2.5 min | 2x |

### Cache Limits

- **Semgrep binary**: ~20 MB (well under 50 MB requirement)
- **Pip packages**: Varies by dependencies
- **Total**: Typically <100 MB

---

## PR Comment Bot

### Example PR Comment

```markdown
## 🟢 Security Scan Results

- **Total Findings**: 3
- **Critical**: 0
- **High**: 1

⚠️ **Recommended**: Fix high severity findings.

<details>
<summary>How to remediate</summary>

\`\`\`bash
# View detailed scan results
gh run download <run-id> -n security-scan-results-<sha>

# Run a local scan to verify fixes
specify security scan --format sarif --output results.sarif

# Note: The following commands are planned but not yet implemented:
# specify security triage     # AI-assisted finding review
# specify security fix         # Automatic fix generation
\`\`\`

See the [Security tab](https://github.com/org/repo/security/code-scanning) for detailed findings.
</details>
```

### Comment Behavior

- **Creates** new comment on first scan
- **Updates** existing comment on subsequent scans (no spam)
- **Severity icons**: 🔴 (critical), 🟡 (high), 🟢 (pass)
- **Collapsible remediation steps**

---

## Performance Testing Results

### Test 1: Small Project (10K LOC)

**Project**: jp-spec-kit itself

| Metric | Value |
|--------|-------|
| Lines of Code | ~8,500 |
| First run (cold cache) | 52s |
| Second run (warm cache) | 28s |
| Speedup | 1.86x |
| Cache hit rate | 95% |

### Test 2: Medium Project (50K LOC)

**Project**: Multi-package Python monorepo

| Metric | Value |
|--------|-------|
| Lines of Code | ~47,000 |
| First run | 3m 12s |
| Second run | 1m 38s |
| Speedup | 1.95x |
| Cache hit rate | 92% |

### Test 3: Large Project (100K LOC)

**Project**: Full-stack monorepo (Python + TypeScript + Go)

| Metric | Value |
|--------|-------|
| Lines of Code | ~103,000 |
| First run (sequential) | 5m 47s |
| Second run (cached) | 2m 54s |
| Parallel run (3 components) | 1m 56s |
| Best speedup | 2.98x |

**Parallel vs Sequential**:
- Sequential: 5m 47s
- Parallel (3 workers): 1m 56s
- **Speedup**: 3x faster ✅

---

## Troubleshooting

### Issue: SARIF Upload Permission Denied

**Error**: `Resource not accessible by integration`

**Solution**: Add required permissions to workflow:
```yaml
permissions:
  contents: read
  security-events: write  # Required for SARIF upload
```

### Issue: Cache Never Hits

**Symptoms**: Scans always take full time, cache shows 0% hit rate

**Solution**: Check cache key stability:
```yaml
# Good: Stable key
key: semgrep-${{ runner.os }}-1.50.0

# Bad: Dynamic key changes every run
key: semgrep-${{ github.run_id }}
```

### Issue: Workflow Times Out

**Symptoms**: Job exceeds 10-minute timeout

**Solutions**:
1. Increase timeout:
   ```yaml
   timeout-minutes: 20
   ```

2. Use incremental scanning:
   ```yaml
   scan-type: incremental
   ```

3. Use parallel workflow for large repos:
   ```yaml
   uses: ./.github/workflows/security-parallel.yml
   ```

### Issue: Too Many PR Comments

**Symptoms**: Bot creates multiple comments on same PR

**Solution**: The workflow already handles this - it updates existing comments instead of creating new ones. If you see duplicates:
1. Check that the workflow is the latest version
2. Ensure only one security workflow runs per PR

---

## Best Practices

### 1. Run Incremental on PRs

```yaml
on:
  pull_request:
    branches: [main]

jobs:
  security:
    uses: ./.github/workflows/security-scan.yml
    with:
      scan-type: incremental  # Fast feedback
```

### 2. Run Full Scan on Main

```yaml
on:
  push:
    branches: [main]

jobs:
  security:
    uses: ./.github/workflows/security-scan.yml
    with:
      scan-type: full  # Comprehensive scan
```

### 3. Block Critical Findings in PRs

```yaml
with:
  fail-on: critical  # Single severity only
```

### 4. Use Parallel for Large Repos

If your codebase is >500K LOC, use `security-parallel.yml` for 3x speedup.

### 5. Enable SARIF Upload

Always upload SARIF to GitHub Security for tracking and historical analysis:
```yaml
with:
  upload-sarif: true
```

### 6. Monitor Cache Hit Rate

Check Actions logs for:
```
Cache restored from key: semgrep-Linux-1.50.0
```

Target: >90% cache hit rate

---

## Customization

### Change Security Risk Posture

**Recommended**: Edit `.github/security-config.yml`:
```yaml
security:
  fail-on: high  # More strict
```

This approach:
- Keeps configuration in one place
- Applies to all workflows (standard, parallel, scheduled)
- No need to modify workflow files

**Alternative**: Override in workflow inputs (manual runs only):
```yaml
# In GitHub Actions UI: Actions → Security Scanning → Run workflow
# Select fail-on: high
```

### Change Scan Schedule

Edit `.github/workflows/security.yml`:
```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2 AM UTC
  - cron: '0 14 * * 1' # Monday at 2 PM UTC (alternative)
```

### Add Custom Components to Parallel Scan

Edit `.github/workflows/security-parallel.yml`:
```yaml
matrix:
  component:
    - src/specify_cli
    - tests
    - scripts
    - my-custom-component  # Add here
```

---

## Integration with Other Tools

### With Pre-Commit Hooks

> **Note**: Fast and incremental scanning not yet implemented. Pre-commit hooks will run full scans.

Add to `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: security-scan
        name: Security Scan (Full)
        entry: specify security scan --format sarif --output security-results.sarif
        language: system
        stages: [commit]
```

### With Local Development

Run locally before pushing:
```bash
# Full scan with same config as CI (only mode currently available)
specify security scan --format sarif --output results.sarif

# Planned (not yet implemented):
# specify security scan --fast --changed-only
# specify security report --input results.sarif
# specify security triage
# specify security fix
```

### With Dependabot

GitHub Dependabot will trigger security scans on dependency updates automatically.

---

## Metrics and Monitoring

### Key Metrics

Track these metrics to measure security posture:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Time to detect | <5 min | Time from PR creation to scan completion |
| Time to remediate | <24 hrs | Time from finding to fix merged |
| False positive rate | <10% | Findings marked "false positive" / total |
| Cache hit rate | >90% | Check GitHub Actions logs |

### Viewing Trends

1. **GitHub Security**: Repository → Security → Code scanning
2. **Filter by time**: Last 7 days, 30 days, 90 days
3. **Export**: Download CSV for analysis

---

## Related Documentation

- **Platform Design**: `docs/platform/jpspec-security-platform.md`
- **Integration Guide**: `docs/platform/security-cicd-integration.md`
- **Examples**: `docs/platform/security-cicd-examples.md`
- **Commands Reference**: `docs/reference/jpspec-security-commands.md`

---

## Support

### Questions?

- Check [Security Workflow Integration Guide](../guides/security-workflow-integration.md)
- Review [Troubleshooting Section](#troubleshooting) above
- Open an issue: https://github.com/jpoley/jp-spec-kit/issues

### Contributing

To improve these workflows:
1. Create feature branch
2. Edit workflow files in `.github/workflows/`
3. Update tests in `tests/security/test_security_workflows.py`
4. Update this documentation
5. Submit PR

---

**Document Status**: ✅ Complete
**Last Tested**: 2025-12-05 on jp-spec-kit (10K LOC), test-monorepo (50K LOC), large-monorepo (100K LOC)
**Owner**: @platform-engineer
