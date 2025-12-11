# Security CI/CD Integration Guide

This guide explains how to use Flowspec's security scanning in your CI/CD pipelines.

## Overview

Flowspec provides GitHub Actions workflows for automated security scanning:

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| `security.yml` | Main security scan | PRs, scheduled, manual |
| `security-scan.yml` | Reusable workflow | Called by other workflows |
| `security-parallel.yml` | Parallel scanning | Manual, scheduled |

## Quick Start

### 1. Enable Security Scanning

Security scanning is automatically enabled for pull requests to `main`. No configuration required.

### 2. View Results

- **PR Comments**: Scan results are posted as PR comments
- **Security Tab**: Findings appear in GitHub's Security > Code scanning alerts
- **Artifacts**: Full SARIF results available as workflow artifacts

### 3. Configure (Optional)

Create `.github/security-config.yml` to customize behavior:

```yaml
security:
  fail-on: critical    # critical, high, medium, or low
  upload-sarif: true   # Upload to GitHub Security tab
  scan-path: "."       # Path to scan
```

## Configuration Reference

### Security Config File

Location: `.github/security-config.yml`

| Setting | Default | Description |
|---------|---------|-------------|
| `fail-on` | `critical` | Severity level that triggers failure |
| `upload-sarif` | `true` | Upload results to GitHub Security |
| `scan-path` | `.` | Directory to scan |

**Note**: Only single severity is currently supported for `fail-on`. Multi-severity support (e.g., `critical,high`) is planned.

### Workflow Inputs

When triggering manually via `workflow_dispatch`:

| Input | Description |
|-------|-------------|
| `fail-on` | Override severity threshold |

## Workflows

### security.yml (Main Workflow)

Triggers on:
- Pull requests to `main`
- Weekly schedule (Sunday 2 AM UTC)
- Manual dispatch

```yaml
# Example: Call from another workflow
jobs:
  security:
    uses: ./.github/workflows/security-scan.yml
    with:
      fail-on: critical
      upload-sarif: true
```

### security-scan.yml (Reusable)

The core scanning workflow. Called by `security.yml`.

**Inputs:**

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `scan-type` | string | `full` | Scan type (reserved for future use) |
| `fail-on` | string | `critical` | Severity to fail on |
| `upload-sarif` | boolean | `true` | Upload SARIF to GitHub |
| `scan-path` | string | `.` | Path to scan |

**Outputs:**

| Output | Description |
|--------|-------------|
| `findings-count` | Total number of findings |
| `critical-count` | Number of critical findings |
| `high-count` | Number of high findings |

### security-parallel.yml (Large Repos)

For repositories >500K LOC, use parallel scanning:

```yaml
# Scans components in parallel:
# - src/specify_cli
# - tests
# - scripts
```

Triggers:
- Manual dispatch
- Weekly schedule (Sunday 3 AM UTC)

## Advisory Mode

Security scanning runs in **advisory mode** by default:

- Scans do **not** block PR merges
- Results are informational
- Use findings to prioritize security work

This allows teams to adopt security scanning gradually without blocking development.

## Remediation Workflow

When findings are reported:

```bash
# 1. Download scan results
gh run download <run-id> -n security-scan-results-<sha>

# 2. Triage with AI assistance
specify security triage

# 3. Generate fix suggestions
specify security fix

# 4. Apply fixes and re-scan
specify security scan
```

## Current Limitations

1. **Single Severity Only**: The `--fail-on` flag accepts one severity level
2. **Full Scans Only**: Incremental scanning (`--incremental`) is not yet implemented
3. **Advisory Mode**: Scans don't block PRs (by design)

## Troubleshooting

### Scan Not Running

1. Check workflow file exists: `.github/workflows/security.yml`
2. Verify branch protection allows workflow runs
3. Check Actions permissions in repository settings

### No Findings Shown

1. Verify `upload-sarif: true` is set
2. Check Security tab permissions
3. Review workflow logs for errors

### SARIF Upload Fails

1. Ensure `security-events: write` permission is set
2. Check GitHub Advanced Security is enabled (for private repos)
3. Verify SARIF file was generated

## Security Considerations

### Dependency Pinning

All external tools are pinned to specific versions:
- Semgrep: `1.50.0`
- yq: `v4.40.5` (with SHA-256 checksum verification)

### Token Permissions

Workflows use minimal permissions:
- `contents: read` - Read repository code
- `security-events: write` - Upload SARIF
- `pull-requests: write` - Post PR comments

### Shell Injection Prevention

All workflows use environment variables for GitHub context:
- Inputs passed via `env:` blocks
- No direct `${{ }}` interpolation in `run:` scripts

## Integration Examples

### With Branch Protection

```yaml
# Require security scan to pass before merge
# Settings > Branches > Branch protection rules
# Add "Security Scan / scan" as required check
```

### With Dependabot

Security scans run automatically on Dependabot PRs, helping identify security issues in dependency updates.

### With Release Workflow

```yaml
# Run security scan before release
jobs:
  security:
    uses: ./.github/workflows/security-scan.yml
    with:
      fail-on: high  # Stricter threshold for releases

  release:
    needs: security
    if: needs.security.outputs.critical-count == 0
    # ... release steps
```

## Related Documentation

- [Security Commands Reference](../reference/flowspec-security-commands.md)
