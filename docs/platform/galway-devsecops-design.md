# Galway DevSecOps Integration Design

**Status**: Platform Design
**Owner**: Platform Engineer
**Last Updated**: 2025-12-04

## Executive Summary

This document defines the DevSecOps architecture for all galway host tasks, implementing Shift-Left Security principles with automated scanning, policy-as-code enforcement, and comprehensive security observability.

## DevSecOps Philosophy

### The Three Ways of Security

```
┌──────────────────────────────────────────────────────────────┐
│                    Shift-Left Security                        │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Developer      Pre-commit      CI/CD         Production     │
│  Workstation    Hooks           Pipeline      Runtime        │
│      │              │                │              │         │
│      ▼              ▼                ▼              ▼         │
│  ┌────────┐    ┌─────────┐    ┌──────────┐   ┌──────────┐   │
│  │ Fast   │───▶│ Faster  │───▶│ Complete │──▶│ Monitor  │   │
│  │ Scan   │    │ Scan    │    │ Scan     │   │ & Audit  │   │
│  │        │    │         │    │          │   │          │   │
│  │ 10s    │    │ 30s     │    │ 2m       │   │ 24/7     │   │
│  └────────┘    └─────────┘    └──────────┘   └──────────┘   │
│      │              │                │              │         │
│      └──────────────┴────────────────┴──────────────┘         │
│                           │                                   │
│                           ▼                                   │
│              ┌─────────────────────────┐                      │
│              │  Security Feedback Loop │                      │
│              │  • Immediate alerts     │                      │
│              │  • Automated triage     │                      │
│              │  • Fix suggestions      │                      │
│              └─────────────────────────┘                      │
└──────────────────────────────────────────────────────────────┘
```

**Key Principles**:
1. **Shift-Left**: Find vulnerabilities early (developer machine > CI > production)
2. **Automate Everything**: No manual security gates
3. **Fail Fast**: Block on critical/high findings immediately
4. **Continuous Monitoring**: Security doesn't stop at deployment
5. **Developer-Friendly**: Security that enhances velocity, not hinders it

## Security Scanning Pipeline Architecture (task-248)

### Scanning Layers

**Layer 1: Developer Workstation** (Pre-commit)
```
Duration: < 10 seconds
Tools: Semgrep (fast rules), bandit (quick)
Scope: Changed files only
Feedback: Immediate (blocks commit)
```

**Layer 2: Pull Request** (CI - Incremental)
```
Duration: 30-60 seconds
Tools: Semgrep (incremental), bandit, pip-audit
Scope: Files changed in PR vs. base branch
Feedback: PR comment + GitHub Security tab
Action: Block merge on critical/high
```

**Layer 3: Main Branch** (CI - Full)
```
Duration: 2-3 minutes
Tools: Semgrep (full), bandit, pip-audit, SBOM generation
Scope: Entire codebase
Feedback: GitHub Security tab, Slack alert
Action: Create tracking issue for findings
```

**Layer 4: Production Runtime** (Continuous)
```
Duration: Continuous
Tools: pip-audit (scheduled), dependency monitoring
Scope: Deployed artifacts + dependencies
Feedback: Slack alert, GitHub issue
Action: Auto-create security patch PR
```

### Tool Selection and Configuration

**SAST (Static Application Security Testing)**

**Primary Tool: Semgrep**
```yaml
# .semgrep.yml
rules:
  - id: python-best-practices
    patterns:
      - pattern: eval(...)
    message: "Avoid eval() - potential code injection"
    severity: ERROR
    languages: [python]

  - id: hardcoded-secrets
    patterns:
      - pattern-regex: "(password|secret|token|api_key)\s*=\s*['\"][^'\"]+['\"]"
    message: "Hardcoded secret detected"
    severity: ERROR
    languages: [python]

  - id: sql-injection
    patterns:
      - pattern: cursor.execute($SQL, ...)
      - pattern-not: cursor.execute("...", ...)
    message: "Potential SQL injection"
    severity: ERROR
    languages: [python]

ruleset:
  - p/security-audit
  - p/owasp-top-ten
  - p/python
```

**Why Semgrep?**
- Fast: < 1 second per file
- Low false positive rate: ~10% vs. 30-50% for other tools
- Incremental scanning: Only changed files
- Custom rule support: Easy to add project-specific rules
- SARIF output: Native GitHub Security integration

**Secondary Tool: Bandit**
```yaml
# .bandit.yml
exclude_dirs:
  - /tests/
  - /scripts/

tests:
  - B201  # Flask debug mode
  - B301  # Pickle usage
  - B303  # Insecure MD5/SHA1
  - B304  # Insecure cipher modes
  - B305  # Insecure cipher usage
  - B306  # Insecure TempFile
  - B307  # eval() usage
  - B308  # mark_safe in templates
  - B320  # XML vulnerabilities
  - B601  # Shell injection
  - B602  # subprocess with shell=True
  - B608  # SQL injection

severity:
  - high
  - medium
```

**Why Bandit?**
- Python-specific: Deep understanding of Python security anti-patterns
- AST-based: Analyzes code structure, not just regex
- Configurable: Can exclude test code, allow safe patterns
- Well-documented: Clear explanations for findings

**Dependency Scanning: pip-audit**
```bash
# Scan for known vulnerabilities in dependencies
pip-audit --desc --format json --output vulnerabilities.json

# Fix mode (auto-upgrade vulnerable packages)
pip-audit --fix
```

**Why pip-audit?**
- Official PyPA tool: Maintained by Python Packaging Authority
- OSV database: Comprehensive vulnerability database
- Auto-fix: Can automatically upgrade vulnerable deps
- Transitive deps: Detects vulnerabilities in sub-dependencies

### Security Scanning Workflow

**Incremental Scan** (PR):
```yaml
name: Security Scan (Incremental)

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  security:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
      pull-requests: write

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for diff

      - name: Get changed files
        id: changed-files
        run: |
          BASE_SHA=${{ github.event.pull_request.base.sha }}
          HEAD_SHA=${{ github.event.pull_request.head.sha }}
          CHANGED=$(git diff --name-only $BASE_SHA..$HEAD_SHA | grep '\.py$' || true)
          echo "files=$CHANGED" >> $GITHUB_OUTPUT

      - name: Semgrep incremental scan
        if: steps.changed-files.outputs.files != ''
        run: |
          pip install semgrep
          semgrep scan \
            --config=auto \
            --sarif \
            --output semgrep.sarif \
            ${{ steps.changed-files.outputs.files }}

      - name: Bandit scan
        if: steps.changed-files.outputs.files != ''
        run: |
          pip install bandit
          bandit -r ${{ steps.changed-files.outputs.files }} \
            -f json -o bandit.json \
            -ll  # Low verbosity, low confidence threshold

      - name: pip-audit
        run: |
          pip install pip-audit
          pip-audit --format json --output deps.json

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: semgrep.sarif

      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            // Parse results and post summary
            const fs = require('fs');
            const semgrep = JSON.parse(fs.readFileSync('semgrep.sarif'));
            const bandit = JSON.parse(fs.readFileSync('bandit.json'));

            const critical = semgrep.runs[0].results.filter(r =>
              r.level === 'error' && r.properties.severity === 'CRITICAL'
            ).length;

            if (critical > 0) {
              github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: `🔴 **Security Alert**: ${critical} critical vulnerabilities detected. Merge blocked.`
              });
              core.setFailed('Critical security vulnerabilities detected');
            }
```

**Full Scan** (Main branch):
```yaml
name: Security Scan (Full)

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly full scan

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Semgrep full scan
        run: |
          pip install semgrep
          semgrep scan \
            --config=auto \
            --sarif \
            --output semgrep-full.sarif \
            --verbose

      - name: Bandit full scan
        run: |
          pip install bandit
          bandit -r src/ \
            -f json -o bandit-full.json

      - name: Generate SBOM
        run: |
          pip install cyclonedx-bom
          cyclonedx-py \
            --format json \
            --output sbom.json \
            --poetry  # Or --requirements requirements.txt

      - name: Upload SARIF + SBOM
        uses: actions/upload-artifact@v4
        with:
          name: security-artifacts
          path: |
            semgrep-full.sarif
            bandit-full.json
            sbom.json

      - name: Create tracking issue
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Security findings from ${new Date().toISOString().split('T')[0]}`,
              body: 'See security scan artifacts for details.',
              labels: ['security', 'automated']
            });
```

## Pre-commit Hook Configuration (task-251)

### Hook Installation

**Setup Script** (`scripts/bash/setup-pre-commit.sh`):
```bash
#!/bin/bash
set -e

echo "Installing pre-commit hooks..."

# Check if .git/hooks exists
if [ ! -d .git/hooks ]; then
    echo "Error: Not a git repository"
    exit 1
fi

# Install pre-commit framework
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml <<'EOF'
repos:
  # Ruff - Fast Python linter
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  # Semgrep - Fast security scanner
  - repo: https://github.com/returntocorp/semgrep
    rev: v1.50.0
    hooks:
      - id: semgrep
        args:
          - --config=auto
          - --error
          - --skip-unknown-extensions
          - --metrics=off

  # Bandit - Python security linter
  - repo: https://github.com/PyCQA/bandit
    rev: '1.7.5'
    hooks:
      - id: bandit
        args: [-ll, -s, B101]  # Skip assert checks in tests

  # Secret detection
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  # Commit message validation
  - repo: https://github.com/compilerla/conventional-pre-commit
    rev: v3.0.0
    hooks:
      - id: conventional-pre-commit
        stages: [commit-msg]

  # File hygiene
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: detect-private-key

  # Python-specific checks
  - repo: https://github.com/pre-commit/pygrep-hooks
    rev: v1.10.0
    hooks:
      - id: python-check-blanket-noqa
      - id: python-no-eval
      - id: python-use-type-annotations

default_language_version:
  python: python3.11

fail_fast: false  # Run all hooks even if one fails
EOF

# Initialize pre-commit
pre-commit install
pre-commit install --hook-type commit-msg

# Create secrets baseline
detect-secrets scan > .secrets.baseline

echo "✅ Pre-commit hooks installed successfully"
echo "Run 'pre-commit run --all-files' to test"
```

### Hook Performance Optimization

**Parallel Execution**:
```yaml
# .pre-commit-config.yaml
default_stages: [commit]
fail_fast: false

# Enable parallel hook execution
default_install_hook_types: [pre-commit, commit-msg]
```

**Caching**:
```bash
# Pre-commit caches in ~/.cache/pre-commit
# Speed up by pre-populating
pre-commit install-hooks  # Install all hooks upfront
```

**Incremental Scanning**:
```yaml
# Only scan staged files
repos:
  - repo: https://github.com/returntocorp/semgrep
    hooks:
      - id: semgrep
        # Semgrep automatically runs on staged files only
        pass_filenames: true
```

**Expected Performance**:
- **Fast path** (no findings): 5-10 seconds
- **Slow path** (findings): 15-30 seconds

### Developer Experience

**Skip Hooks** (emergency escape hatch):
```bash
# Skip all hooks (use sparingly!)
git commit --no-verify -m "emergency fix"

# Skip specific hook
SKIP=semgrep git commit -m "skip semgrep this time"
```

**Update Hooks**:
```bash
# Update to latest versions
pre-commit autoupdate

# Run manually without committing
pre-commit run --all-files
```

## Security Policy as Code (task-252)

### Policy Definition

**Policy File** (`.security-policy.yml`):
```yaml
version: 1.0

# Severity thresholds
thresholds:
  block_on:
    - CRITICAL
    - HIGH
  warn_on:
    - MEDIUM
  ignore:
    - LOW

# Allowed exceptions (with justification)
exceptions:
  - rule_id: python-eval
    justification: "eval() used only in sandboxed REPL for plugin system"
    files:
      - src/specify_cli/plugin_runner.py
    expires: 2025-06-01  # Must be re-reviewed

  - rule_id: hardcoded-secret
    justification: "Test fixture, not real secret"
    files:
      - tests/fixtures/test_secrets.py
    expires: never

# Dependency policies
dependencies:
  auto_upgrade_security: true  # Auto-create PRs for security patches
  allowed_licenses:
    - MIT
    - Apache-2.0
    - BSD-3-Clause
    - BSD-2-Clause
  blocked_licenses:
    - GPL-3.0  # Copyleft incompatible with commercial use
    - AGPL-3.0

# SBOM requirements
sbom:
  required: true
  format: CycloneDX
  include_transitive: true

# Vulnerability disclosure
disclosure:
  security_email: security@peregrinesummit.com
  pgp_key_fingerprint: "1234 5678 90AB CDEF"
  security_txt: true  # Generate .well-known/security.txt
```

### Policy Enforcement

**Policy Validator** (`scripts/python/validate-security-policy.py`):
```python
#!/usr/bin/env python3
import json
import yaml
from datetime import datetime
from pathlib import Path

def load_policy():
    with open('.security-policy.yml') as f:
        return yaml.safe_load(f)

def load_scan_results(sarif_file: Path):
    with open(sarif_file) as f:
        return json.load(f)

def check_exceptions(finding, policy):
    """Check if finding matches an exception."""
    for exc in policy.get('exceptions', []):
        if finding['rule_id'] != exc['rule_id']:
            continue

        # Check file match
        if finding['file'] not in exc['files']:
            continue

        # Check expiration
        if exc.get('expires') != 'never':
            expires = datetime.fromisoformat(exc['expires'])
            if datetime.now() > expires:
                print(f"⚠️  Exception expired: {exc['rule_id']}")
                return False

        return True
    return False

def enforce_policy(sarif_file: Path):
    policy = load_policy()
    results = load_scan_results(sarif_file)

    blocked = []
    warnings = []

    for run in results['runs']:
        for result in run['results']:
            severity = result.get('properties', {}).get('severity', 'UNKNOWN')
            rule_id = result['ruleId']
            file_path = result['locations'][0]['physicalLocation']['artifactLocation']['uri']

            finding = {
                'rule_id': rule_id,
                'file': file_path,
                'severity': severity,
                'message': result['message']['text']
            }

            # Check exceptions
            if check_exceptions(finding, policy):
                continue

            # Apply thresholds
            if severity in policy['thresholds']['block_on']:
                blocked.append(finding)
            elif severity in policy['thresholds']['warn_on']:
                warnings.append(finding)

    # Report results
    if blocked:
        print(f"🔴 {len(blocked)} findings block merge:")
        for f in blocked:
            print(f"  - {f['rule_id']}: {f['message']} ({f['file']})")
        return 1

    if warnings:
        print(f"🟡 {len(warnings)} warnings (non-blocking):")
        for f in warnings:
            print(f"  - {f['rule_id']}: {f['message']} ({f['file']})")

    print("✅ Security policy check passed")
    return 0

if __name__ == '__main__':
    import sys
    exit(enforce_policy(Path(sys.argv[1])))
```

**CI Integration**:
```yaml
- name: Enforce security policy
  run: |
    python scripts/python/validate-security-policy.py semgrep.sarif
```

## DORA Metrics for Security (task-253)

### Security-Specific Metrics

**Mean Time to Detect (MTTD)**:
```prometheus
# Time from vulnerability disclosure to detection in our codebase
security_vulnerability_detection_time_seconds{severity, cve_id}

# Alert on slow detection
- alert: SlowVulnerabilityDetection
  expr: security_vulnerability_detection_time_seconds > 86400  # 1 day
  annotations:
    summary: "Vulnerability took > 24h to detect"
```

**Mean Time to Remediate (MTTR)**:
```prometheus
# Time from detection to fix merged
security_vulnerability_remediation_time_seconds{severity, cve_id}

# Target: Critical < 24h, High < 7 days
- alert: SlowSecurityRemediation
  expr: |
    security_vulnerability_remediation_time_seconds{severity="CRITICAL"} > 86400
  annotations:
    summary: "Critical vulnerability not fixed within 24h SLA"
```

**Security Debt**:
```prometheus
# Count of open security findings
security_findings_open{severity, age_bucket}

# Track trend over time
rate(security_findings_open[30d])
```

**Security Scan Coverage**:
```prometheus
# Percentage of codebase scanned
security_scan_coverage_percent

# Target: 100% of production code
- alert: LowSecurityCoverage
  expr: security_scan_coverage_percent < 95
```

### DORA Dashboard for Security

**Grafana Dashboard Panels**:

1. **Security Posture Overview**
   ```promql
   # Current open findings by severity
   sum(security_findings_open) by (severity)
   ```

2. **Detection Performance**
   ```promql
   # P50 and P95 detection time
   histogram_quantile(0.50, rate(security_vulnerability_detection_time_seconds_bucket[7d]))
   histogram_quantile(0.95, rate(security_vulnerability_detection_time_seconds_bucket[7d]))
   ```

3. **Remediation Performance**
   ```promql
   # Average time to fix by severity
   avg_over_time(security_vulnerability_remediation_time_seconds{severity="CRITICAL"}[30d]) / 3600  # Convert to hours
   ```

4. **Scan Frequency**
   ```promql
   # Scans per day
   sum(rate(security_scan_total[1d]))
   ```

5. **False Positive Rate**
   ```promql
   # Percentage of findings dismissed as false positives
   sum(security_false_positives_total) / sum(security_findings_total)
   ```

## Security Scanner Docker Image (task-254)

### Dockerfile

**Multi-stage Build** (`docker/Dockerfile.security-scanner`):
```dockerfile
# Stage 1: Build environment
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python security tools
RUN pip install --no-cache-dir --prefix=/build/install \
    semgrep==1.50.0 \
    bandit==1.7.5 \
    pip-audit==2.6.1 \
    cyclonedx-bom==4.0.0

# Stage 2: Runtime image
FROM python:3.11-slim

LABEL org.opencontainers.image.title="JP Spec Kit Security Scanner"
LABEL org.opencontainers.image.description="Comprehensive security scanning for Python projects"
LABEL org.opencontainers.image.version="0.0.250"
LABEL org.opencontainers.image.authors="jpoley@peregrinesummit.com"

WORKDIR /scan

# Copy installed tools from builder
COPY --from=builder /build/install /usr/local

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    jq \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 scanner && \
    chown -R scanner:scanner /scan

USER scanner

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD semgrep --version && bandit --version

# Default command: run all scans
COPY --chown=scanner:scanner scripts/security/scan-all.sh /usr/local/bin/
ENTRYPOINT ["/usr/local/bin/scan-all.sh"]
```

### Scan Entrypoint Script

**Script** (`scripts/security/scan-all.sh`):
```bash
#!/bin/bash
set -euo pipefail

# Configuration
SCAN_PATH=${SCAN_PATH:-/scan}
OUTPUT_DIR=${OUTPUT_DIR:-/scan/results}
SCAN_TYPE=${SCAN_TYPE:-full}  # full | incremental | fast

mkdir -p "$OUTPUT_DIR"

log() {
    echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"level\":\"INFO\",\"message\":\"$1\"}"
}

log "Starting security scan (type: $SCAN_TYPE)"

# Semgrep scan
log "Running Semgrep..."
semgrep scan \
    --config=auto \
    --sarif \
    --output "$OUTPUT_DIR/semgrep.sarif" \
    --metrics=off \
    "$SCAN_PATH"

# Bandit scan
log "Running Bandit..."
bandit -r "$SCAN_PATH" \
    -f json \
    -o "$OUTPUT_DIR/bandit.json" \
    -ll || true  # Don't fail on findings

# pip-audit (if requirements.txt exists)
if [ -f "$SCAN_PATH/requirements.txt" ] || [ -f "$SCAN_PATH/pyproject.toml" ]; then
    log "Running pip-audit..."
    pip-audit \
        --desc \
        --format json \
        --output "$OUTPUT_DIR/dependencies.json" \
        || true
fi

# Generate SBOM
log "Generating SBOM..."
if [ -f "$SCAN_PATH/pyproject.toml" ]; then
    cyclonedx-py \
        --format json \
        --output "$OUTPUT_DIR/sbom.json" \
        --poetry
fi

# Consolidate results
log "Consolidating results..."
cat > "$OUTPUT_DIR/summary.json" <<EOF
{
  "scan_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "scan_type": "$SCAN_TYPE",
  "scan_path": "$SCAN_PATH",
  "results": {
    "semgrep": "$(jq '.runs[0].results | length' "$OUTPUT_DIR/semgrep.sarif" || echo 0)",
    "bandit": "$(jq '.results | length' "$OUTPUT_DIR/bandit.json" || echo 0)",
    "dependencies": "$(jq '.vulnerabilities | length' "$OUTPUT_DIR/dependencies.json" || echo 0)"
  }
}
EOF

log "Scan complete. Results in $OUTPUT_DIR"
cat "$OUTPUT_DIR/summary.json"
```

### Usage

**Docker Build**:
```bash
docker build -t jp-spec-kit-security:latest -f docker/Dockerfile.security-scanner .

# Tag for registry
docker tag jp-spec-kit-security:latest ghcr.io/jpoley/jp-spec-kit-security:0.0.250
docker push ghcr.io/jpoley/jp-spec-kit-security:0.0.250
```

**Docker Run**:
```bash
# Scan current directory
docker run --rm \
  -v $(pwd):/scan:ro \
  -v $(pwd)/results:/scan/results:rw \
  jp-spec-kit-security:latest

# Incremental scan
docker run --rm \
  -e SCAN_TYPE=incremental \
  -v $(pwd):/scan:ro \
  -v $(pwd)/results:/scan/results:rw \
  jp-spec-kit-security:latest

# CI usage
docker run --rm \
  -v $(pwd):/scan:ro \
  -v $(pwd)/results:/scan/results:rw \
  ghcr.io/jpoley/jp-spec-kit-security:0.0.250
```

**GitHub Actions Integration**:
```yaml
- name: Run security scan in container
  run: |
    docker run --rm \
      -v ${{ github.workspace }}:/scan:ro \
      -v ${{ github.workspace }}/results:/scan/results:rw \
      ghcr.io/jpoley/jp-spec-kit-security:0.0.250

- name: Upload results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results/semgrep.sarif
```

## Tool Dependency Management (task-249)

### Dependency Pinning Strategy

**Pin Exact Versions**:
```requirements
# requirements-security.txt
semgrep==1.50.0
bandit==1.7.5
pip-audit==2.6.1
cyclonedx-bom==4.0.0
detect-secrets==1.4.0
```

**Why Exact Pins?**
- **Reproducibility**: Same scan results across environments
- **Security**: Prevent supply chain attacks via malicious updates
- **Stability**: Avoid breaking changes in tools

### Dependency Update Automation

**Dependabot Configuration** (`.github/dependabot.yml`):
```yaml
version: 2
updates:
  # Security tools
  - package-ecosystem: "pip"
    directory: "/requirements"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "security-tools"
    groups:
      security-tools:
        patterns:
          - "semgrep"
          - "bandit"
          - "pip-audit"
          - "cyclonedx-bom"
```

**Automated Testing of Updates**:
```yaml
# .github/workflows/test-security-tool-updates.yml
name: Test Security Tool Updates

on:
  pull_request:
    paths:
      - 'requirements-security.txt'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install updated tools
        run: pip install -r requirements-security.txt

      - name: Run test scan
        run: |
          # Scan known vulnerable code
          semgrep scan tests/fixtures/vulnerable-code.py --config=auto

          # Ensure findings are detected
          if [ $(semgrep scan tests/fixtures/vulnerable-code.py --json | jq '.results | length') -eq 0 ]; then
            echo "❌ Test scan found no vulnerabilities (expected some)"
            exit 1
          fi

      - name: Compare results with baseline
        run: |
          # Ensure new version doesn't reduce detection
          python scripts/compare-scan-results.py \
            baseline-results.json \
            new-results.json
```

## Security Observability (task-250)

Detailed observability design is in `galway-observability-design.md`, but key security-specific integrations:

**Metrics**:
```prometheus
security_scan_duration_seconds{tool, scan_type}
security_findings_total{severity, tool, category}
security_false_positive_rate{tool}
security_mttr_seconds{severity}
```

**Logs**:
```json
{
  "level": "WARNING",
  "message": "Security finding detected",
  "context": {
    "rule_id": "python-eval",
    "severity": "HIGH",
    "file": "src/plugin_runner.py",
    "line": 42,
    "recommendation": "Use ast.literal_eval() instead"
  }
}
```

**Traces**:
- Span: `security_scan`
  - Child span: `semgrep_scan`
  - Child span: `bandit_scan`
  - Child span: `dependency_scan`
  - Child span: `upload_sarif`

## Success Metrics

**Security Posture**:
- **Critical/High findings**: 0 in production
- **Mean Time to Detect**: < 4 hours for new CVEs
- **Mean Time to Remediate**: < 24 hours for critical, < 7 days for high

**Developer Experience**:
- **Pre-commit hook time**: < 10 seconds P95
- **False positive rate**: < 10%
- **Scan frequency**: Every commit (incremental), daily (full)

**CI/CD Integration**:
- **Scan success rate**: > 99% (no tool failures)
- **Scan duration**: < 2 minutes for PR, < 5 minutes for full

## Related Tasks

| Task ID | Title | Integration Point |
|---------|-------|-------------------|
| task-248 | Security Scanning Pipeline | Core pipeline architecture |
| task-251 | Pre-commit Hooks | Developer workflow integration |
| task-252 | Security Policy as Code | Policy enforcement |
| task-253 | DORA Metrics | Security metrics tracking |
| task-254 | Security Scanner Docker | Containerized scanning |
| task-249 | Tool Dependency Management | Dependency pinning |
| task-250 | Security Observability | Metrics, logs, traces |

## Appendix: Security Tool Comparison

| Tool | Type | Speed | Accuracy | Output | Best For |
|------|------|-------|----------|--------|----------|
| Semgrep | SAST | Fast | High | SARIF | Pre-commit, CI |
| Bandit | SAST | Fast | Medium | JSON | Python-specific |
| pip-audit | SCA | Fast | High | JSON | Dependencies |
| Snyk | SCA | Medium | High | JSON | Dependencies + license |
| CodeQL | SAST | Slow | Very High | SARIF | Deep analysis |
| Trivy | Container | Fast | High | JSON | Container images |

**Recommendation**: Semgrep + Bandit + pip-audit for fast, comprehensive coverage.
