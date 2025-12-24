# Security CI/CD Pipeline Setup Guide

This guide walks you through setting up automated security scanning in your CI/CD pipeline using GitHub Actions and Flowspec security commands.

## Overview

Flowspec provides reusable GitHub Actions workflows for security scanning that:

- Run automated security scans on every PR and scheduled intervals
- Upload SARIF results to GitHub Security tab for centralized vulnerability management
- Post PR comments with scan summaries and remediation guidance
- Cache scanning tools for faster execution
- Support parallel scanning for large codebases (3x speedup)
- Integrate with `/flow:security` commands for local development

## Quick Start

### 1. Copy Template Files

Copy the security scanning templates to your repository:

```bash
# Create workflows directory if it doesn't exist
mkdir -p .github/workflows

# Copy reusable security scan workflow
cp templates/github-actions/security-scan.yml .github/workflows/security-scan.yml

# Copy entry point workflow
cp templates/github-actions/security.yml .github/workflows/security.yml

# Copy security configuration
cp templates/github-actions/security-config.yml .github/security-config.yml
```

### 2. Customize Configuration

Edit `.github/security-config.yml` to match your project:

```yaml
security:
  # Severity level that causes scan to fail
  # Options: critical, high, medium, low
  fail-on: critical

  # Upload results to GitHub Security tab
  upload-sarif: true

  # Path to scan (relative to repo root)
  scan-path: "."
```

### 3. Replace Template Variables

In all workflow files that contain `{{PROJECT_NAME}}` (e.g., `security-scan.yml` and `security-parallel.yml`), replace it with your project name:

```bash
# Replace in all security workflow files
sed -i 's/{{PROJECT_NAME}}/my-project/g' .github/workflows/security-*.yml
```

### 4. Commit and Push

```bash
git add .github/
git commit -m "ci: add security scanning workflows"
git push
```

### 5. Verify Setup

The security scan will run automatically:

- On every pull request to `main`
- Weekly on Sunday at 2 AM UTC (configurable)
- Manually via workflow_dispatch

Check results in:
- **PR Comments**: Summary of findings
- **GitHub Actions**: Full scan logs
- **Security Tab**: Detailed vulnerability reports (requires SARIF upload)

## Workflow Architecture

### Standard Scanning (Default)

```
┌─────────────────────────────────────────────────────────┐
│                    security.yml                         │
│             (Entry Point Workflow)                      │
│                                                         │
│  Triggers:                                              │
│    - Pull requests to main                              │
│    - Weekly schedule (cron)                             │
│    - Manual dispatch                                    │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ calls
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                security-scan.yml                        │
│            (Reusable Workflow)                          │
│                                                         │
│  Steps:                                                 │
│    1. Checkout code                                     │
│    2. Cache Semgrep binary                              │
│    3. Install flowspec-cli                              │
│    4. Read security config                              │
│    5. Run: flowspec security scan                       │
│    6. Upload SARIF to GitHub Security                   │
│    7. Upload artifacts (reports)                        │
│    8. Comment PR with summary                           │
└─────────────────────────────────────────────────────────┘
```

### Parallel Scanning (Large Codebases)

For codebases >500K LOC, use parallel scanning:

```
┌─────────────────────────────────────────────────────────┐
│              security-parallel.yml                      │
│           (Manual Trigger Only)                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 │ matrix strategy
                 │
        ┌────────┴────────┬────────┬────────┐
        ▼                 ▼        ▼        ▼
   ┌─────────┐      ┌─────────┐  ...  ┌─────────┐
   │ Scan    │      │ Scan    │       │ Scan    │
   │ Backend │      │Frontend │       │ Tests   │
   └────┬────┘      └────┬────┘       └────┬────┘
        │                │                  │
        └────────┬───────┴──────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Aggregate       │
        │ Results         │
        └─────────────────┘
```

## Configuration Reference

### Security Configuration (`.github/security-config.yml`)

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `security.fail-on` | string | `critical` | Severity level that causes failure: `critical`, `high`, `medium`, `low` |
| `security.upload-sarif` | boolean | `true` | Upload SARIF to GitHub Security tab |
| `security.scan-path` | string | `.` | Path to scan (relative to repo root) |

### Workflow Inputs

Both workflows accept the following inputs via `workflow_dispatch`:

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `fail-on` | choice | (from config) | Override severity threshold |
| `scan-path` | string | `.` | Override scan path |
| `upload-sarif` | boolean | `true` | Override SARIF upload |

### Workflow Outputs

`security-scan.yml` provides outputs for downstream jobs:

| Output | Type | Description |
|--------|------|-------------|
| `findings-count` | number | Total number of findings |
| `critical-count` | number | Number of critical findings |
| `high-count` | number | Number of high severity findings |

## Advanced Usage

### Parallel Scanning for Large Codebases

For codebases >500K LOC, use parallel scanning for 3x speedup:

```bash
# Copy parallel scanning workflow
cp templates/github-actions/security-parallel.yml .github/workflows/security-parallel.yml

# Edit and customize the matrix strategy
```

Edit `.github/workflows/security-parallel.yml` and update the matrix:

```yaml
matrix:
  component:
    - src/backend       # Your backend code
    - src/frontend      # Your frontend code
    - tests             # Your test suite
    - infrastructure    # IaC code
    # Add more components as needed
```

**When to use parallel scanning:**

- Codebases >500K lines of code
- Monorepos with multiple components
- Projects requiring faster scan times

**Benefits:**

- 3x faster scanning via parallel execution
- Component-specific SARIF categories in Security tab
- Aggregated results for overall security posture

### Conditional Scanning (Only on Changes)

To scan only when code changes:

```yaml
on:
  pull_request:
    paths:
      - 'src/**'
      - 'tests/**'
      - '!docs/**'  # Exclude docs
```

### Multi-Environment Scanning

Scan different environments with different severity thresholds:

```yaml
jobs:
  scan-staging:
    uses: ./.github/workflows/security-scan.yml
    with:
      fail-on: high  # More lenient for staging

  scan-production:
    uses: ./.github/workflows/security-scan.yml
    with:
      fail-on: critical  # Strict for production
```

### Custom Scan Schedules

Adjust the cron schedule in `security.yml`:

```yaml
schedule:
  # Daily at 2 AM UTC
  - cron: '0 2 * * *'

  # Weekdays at 9 AM UTC
  - cron: '0 9 * * 1-5'

  # Every 6 hours
  - cron: '0 */6 * * *'
```

Use [crontab.guru](https://crontab.guru/) to generate cron expressions.

### Blocking vs Advisory Scans

**Advisory (Default)**: Scans run but don't block PRs

```yaml
continue-on-error: true  # Already set in template
```

**Blocking**: Scans must pass before PR merge

```yaml
continue-on-error: false  # Change in security-scan.yml
```

### Integration with Other Workflows

Use scan outputs in downstream jobs:

```yaml
jobs:
  security-scan:
    uses: ./.github/workflows/security-scan.yml

  deploy:
    needs: security-scan
    if: needs.security-scan.outputs.critical-count == 0
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: ./deploy.sh
```

## Viewing Results

### GitHub Security Tab

SARIF results appear in: **Repository → Security → Code scanning alerts**

Features:
- Vulnerability details with severity, CWE, OWASP categories
- Line-by-line code highlighting
- Remediation guidance
- Historical tracking (dismiss, reopen, fix)

### PR Comments

Automated PR comments include:
- Total findings count
- Critical and high severity counts
- Remediation instructions
- Links to detailed results

### Artifacts

Download detailed reports from Actions:

```bash
# Download latest scan results
gh run download --name security-scan-results-<SHA>

# View SARIF file
cat security-results.sarif | jq '.runs[0].results'
```

## Local Development Integration

Security scanning in CI/CD integrates with local `/flow:security` commands:

```bash
# Run scan locally (matches CI behavior)
flowspec security scan

# Triage findings with AI assistance
flowspec security triage

# Generate fix suggestions
flowspec security fix

# View scan report
cat docs/security/scan-report-*.md
```

## Troubleshooting

### Scan Fails with "flowspec not found"

**Cause**: flowspec-cli not installed

**Fix**: Ensure workflow includes pinned versions for supply chain security:

```yaml
- name: Install Flowspec
  run: |
    # Pin uv version for reproducibility
    pip install uv==0.5.11
    # Install flowspec-cli from PyPI with pinned version
    uv pip install --system flowspec-cli==0.1.0
```

⚠️ **Supply Chain Security Note**: Always pin package versions in CI/CD workflows.
Unpinned packages (`pip install uv` or `uv pip install flowspec-cli` without versions)
create a supply chain attack surface where a compromised package update could inject
malicious code into your pipeline. The workflow templates in `templates/github-actions/`
include proper version pinning - copy from templates rather than writing manually.

### SARIF Upload Fails

**Cause**: Missing security-events permission

**Fix**: Ensure workflow has:

```yaml
permissions:
  security-events: write
```

### PR Comment Bot Not Working

**Cause**: Missing pull-requests permission

**Fix**: Ensure workflow has:

```yaml
permissions:
  pull-requests: write
```

### Scan Times Out After 10 Minutes

**Cause**: Large codebase takes too long

**Fix**: Use parallel scanning workflow or increase timeout:

```yaml
timeout-minutes: 30  # Increase as needed
```

### Cache Not Working

**Cause**: Semgrep version mismatch

**Fix**: Update cache key to match installed version:

```yaml
- name: Cache Semgrep Binary
  uses: actions/cache@v4
  with:
    key: semgrep-${{ runner.os }}-1.50.0  # Match installed version
```

## Performance Optimization

### Caching Strategy

The workflow caches:
- Python dependencies (via actions/setup-python cache)
- Semgrep binary (via actions/cache)

**Cache invalidation:**
- Python deps: When requirements change
- Semgrep: When version changes

### Parallel Scanning Performance

**Standard scanning:**
- Single-threaded
- Scans entire codebase sequentially
- ~10-15 minutes for 500K LOC

**Parallel scanning:**
- Multi-threaded via matrix strategy
- Scans components in parallel
- ~3-5 minutes for 500K LOC (3x speedup)

**Trade-offs:**
- More GitHub Actions runner minutes consumed
- More complex SARIF category management
- Better for large codebases (>500K LOC)

## Security Considerations

### Secrets Management

**Never hardcode secrets in workflows**

Use GitHub Secrets for sensitive data:

```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}
```

### SARIF Upload Security

SARIF files may contain:
- Code snippets from your repository
- File paths and structure
- Vulnerability details

**Ensure:**
- SARIF upload is authorized for your organization
- Access to Security tab is properly restricted
- Artifact retention is configured appropriately

### Artifact Retention

Configure retention based on compliance needs:

```yaml
- name: Upload Scan Artifacts
  uses: actions/upload-artifact@v4
  with:
    retention-days: 90  # Adjust for compliance
```

### Pinned Tool Versions

Workflows pin tool versions for security:

```yaml
# Semgrep pinned to specific version
pip install semgrep==1.50.0

# yq binary with checksum verification
YQ_VERSION="v4.40.5"
YQ_CHECKSUM="4e9e5f4a574c6d7e04baa28f91e5b985ad7b22d4e4fd89e1f0d1ccb501e8ddf8"
```

**Update pinned versions regularly** to get security fixes.

## Best Practices

### Severity Threshold Guidelines

| Environment | Recommended `fail-on` |
|-------------|----------------------|
| Development | `medium` or advisory |
| Staging | `high` |
| Production | `critical` |

### Scan Frequency

| Trigger | Recommended |
|---------|-------------|
| Pull requests | Always |
| Main branch | On every push |
| Scheduled | Weekly minimum |
| Manual | As needed for audits |

### PR Workflow

1. Developer creates PR
2. Security scan runs automatically
3. Bot comments with summary
4. If critical findings:
   - Developer runs `flowspec security triage` locally
   - Developer runs `flowspec security fix` for suggestions
   - Developer fixes issues
   - Re-scan happens automatically on push
5. Reviewer checks Security tab for details
6. Merge when scan passes

## Migration Guide

### From CodeQL

Replace:

```yaml
- name: Initialize CodeQL
  uses: github/codeql-action/init@v3

- name: Analyze
  uses: github/codeql-action/analyze@v3
```

With:

```yaml
- uses: ./.github/workflows/security-scan.yml
```

**Benefits:**
- Unified scanning across languages (Semgrep > CodeQL coverage)
- Faster scans (Semgrep is faster than CodeQL)
- AI-assisted remediation via `/flow:security` commands

### From Snyk/Dependabot

Flowspec security scanning complements dependency scanning:

```yaml
jobs:
  security-sast:
    uses: ./.github/workflows/security-scan.yml  # SAST + SCA

  dependency-scan:
    uses: snyk/actions/node@master  # Keep for dependency insights
```

**Use both for defense-in-depth:**
- Flowspec: SAST (code vulnerabilities)
- Snyk/Dependabot: SCA (dependency vulnerabilities)

## Examples

### Example 1: Basic Setup (Small Project)

```yaml
# .github/workflows/security.yml
name: Security

on:
  pull_request:
  push:
    branches: [main]

jobs:
  scan:
    uses: ./.github/workflows/security-scan.yml
```

### Example 2: Multi-Environment (Medium Project)

```yaml
# .github/workflows/security.yml
name: Security

on:
  pull_request:
  push:
    branches: [main, develop]

jobs:
  scan-dev:
    if: github.ref == 'refs/heads/develop'
    uses: ./.github/workflows/security-scan.yml
    with:
      fail-on: high

  scan-prod:
    if: github.ref == 'refs/heads/main'
    uses: ./.github/workflows/security-scan.yml
    with:
      fail-on: critical
```

### Example 3: Monorepo with Parallel Scanning (Large Project)

```yaml
# .github/workflows/security-parallel.yml
name: Security (Parallel)

on:
  workflow_dispatch:

jobs:
  scan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        component: [backend, frontend, api, workers]
    steps:
      # ... (see template)
```

## Next Steps

- [Security Triage Guide](../reference/security-triage.md) - Triage findings with AI
- [Security Fix Guide](../reference/security-fix.md) - Apply automated fixes
- [Custom Security Rules](../guides/security-custom-rules.md) - Write custom Semgrep rules
- [Security Workflow Reference](../reference/security-workflow.md) - Full command reference

## Support

- [GitHub Discussions](https://github.com/jpoley/flowspec/discussions)
- [Report Issues](https://github.com/jpoley/flowspec/issues)
- [Security Policy](../../SECURITY.md)
