# CI/CD Integration Guide: /jpspec:security Commands

**Audience**: Platform Engineers, DevOps Engineers
**Last Updated**: 2025-12-02
**Related**: `jpspec-security-platform.md`

---

## Quick Start

### GitHub Actions (Recommended)

Add to `.github/workflows/pr-checks.yml`:

```yaml
name: PR Checks

on:
  pull_request:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for incremental scanning

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install JP Spec Kit
        run: |
          pip install uv
          uv tool install specify-cli

      - name: Run Security Scan
        run: |
          specify security scan \
            --incremental \
            --baseline-commit=${{ github.event.pull_request.base.sha }} \
            --fail-on critical,high \
            --format sarif \
            --output security-results.sarif

      - name: Upload SARIF to GitHub Security
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: security-results.sarif
```

---

## Integration Patterns

### 1. Pre-commit Hook (Local)

**Best for**: Fast feedback before commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: jpspec-security-scan
        name: Security Scan (Fast)
        entry: specify security scan --fast --changed-only --fail-on critical
        language: system
        stages: [commit]
        pass_filenames: false
```

**Install**:
```bash
pip install pre-commit
pre-commit install
```

**Performance**: <10 seconds for typical commit

---

### 2. Pull Request (CI)

**Best for**: Comprehensive scan before merge

```yaml
# .github/workflows/pr-security.yml
name: Security Scan

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  scan:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write  # For SARIF upload
      pull-requests: write     # For PR comments

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Cache Semgrep
        uses: actions/cache@v4
        with:
          path: ~/.local/bin/semgrep
          key: semgrep-${{ runner.os }}-1.50.0

      - name: Install Tools
        run: |
          pip install uv
          uv tool install specify-cli
          pip install semgrep==1.50.0

      - name: Run Security Scan
        id: scan
        run: |
          specify security scan \
            --incremental \
            --baseline-commit=${{ github.event.pull_request.base.sha }} \
            --fail-on critical,high \
            --format sarif \
            --output security-results.sarif \
            --ci-mode

          # Extract metrics for PR comment
          TOTAL=$(jq '.runs[0].results | length' security-results.sarif)
          CRITICAL=$(jq '[.runs[0].results[] | select(.level == "error")] | length' security-results.sarif)

          echo "total=${TOTAL}" >> $GITHUB_OUTPUT
          echo "critical=${CRITICAL}" >> $GITHUB_OUTPUT

      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: security-results.sarif
          category: jpspec-security

      - name: Comment PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const total = ${{ steps.scan.outputs.total }};
            const critical = ${{ steps.scan.outputs.critical }};

            const body = `## 🔒 Security Scan Results

            - **Total Findings**: ${total}
            - **Critical**: ${critical}

            ${critical > 0 ? '⚠️ **Critical vulnerabilities found!** Fix before merge.' : '✅ No critical issues.'}

            <details>
            <summary>How to fix</summary>

            \`\`\`bash
            # Triage findings
            specify security triage

            # Generate fixes
            specify security fix

            # Re-scan
            specify security scan
            \`\`\`
            </details>`;

            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });

      - name: Upload Artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-scan-results
          path: |
            security-results.sarif
            docs/security/*.md
            docs/security/*.json
          retention-days: 90
```

**Expected Duration**: 3-5 minutes for 100K LOC

---

### 3. Post-Merge (Audit)

**Best for**: Compliance reporting, trend tracking

```yaml
# .github/workflows/security-audit.yml
name: Security Audit

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday at 2 AM

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Tools
        run: |
          pip install uv
          uv tool install specify-cli

      - name: Full Security Scan
        run: |
          specify security scan --full --format json,sarif,markdown

      - name: Generate Audit Report
        run: specify security audit --format markdown,html

      - name: Upload to S3 (or artifact storage)
        run: |
          aws s3 cp docs/security/ s3://compliance-reports/security/ --recursive
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}

      - name: Notify Security Team
        if: contains(fromJson(steps.scan.outputs.summary), 'critical')
        uses: slackapi/slack-github-action@v1
        with:
          webhook: ${{ secrets.SLACK_SECURITY_WEBHOOK }}
          payload: |
            {
              "text": "🚨 Security Audit: Critical vulnerabilities found in main branch",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Security Audit Alert*\nCritical vulnerabilities detected in production code."
                  }
                }
              ]
            }
```

**Schedule**: Weekly or on every merge to main

---

## Performance Optimization

### Caching Strategy

**Cache Semgrep Binary**:
```yaml
- name: Cache Semgrep
  uses: actions/cache@v4
  with:
    path: ~/.local/bin/semgrep
    key: semgrep-${{ runner.os }}-1.50.0
    restore-keys: semgrep-${{ runner.os }}-
```

**Cache Scan Results** (for unchanged code):
```yaml
- name: Cache Scan Results
  uses: actions/cache@v4
  with:
    path: .jpspec/cache/security
    key: security-scan-${{ hashFiles('**/*.py', '**/*.ts', '**/*.go') }}
```

**Expected Speedup**:
- First run (cold cache): 3-5 minutes
- Cached runs: 1-2 minutes (60% faster)

---

### Incremental Scanning

**How it works**:
```bash
# Only scan files changed since base commit
specify security scan \
  --incremental \
  --baseline-commit=${{ github.event.pull_request.base.sha }}
```

**Performance**:
- Full scan (100K LOC): 5 minutes
- Incremental (10 files changed): 30 seconds
- **Speedup**: 10x faster

---

### Parallel Scanning (Large Codebases)

For monorepos >500K LOC, split by component:

```yaml
jobs:
  security-scan:
    strategy:
      matrix:
        component:
          - backend-python
          - frontend-typescript
          - infrastructure-terraform
    steps:
      - name: Scan ${{ matrix.component }}
        run: |
          specify security scan \
            --path src/${{ matrix.component }} \
            --format sarif \
            --output results-${{ matrix.component }}.sarif

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results-${{ matrix.component }}.sarif
          category: ${{ matrix.component }}
```

**Performance**:
- Sequential: 15 minutes (3 components × 5 min each)
- Parallel: 5 minutes (all run simultaneously)
- **Speedup**: 3x faster

---

## Security Gates

### Severity-Based Blocking

**Block on Critical/High**:
```yaml
- name: Security Scan
  run: specify security scan --fail-on critical,high
```

**Warn on Medium**:
```yaml
- name: Security Scan
  run: |
    specify security scan --fail-on critical,high || EXIT_CODE=$?
    if [ $EXIT_CODE -eq 2 ]; then
      echo "⚠️ Medium severity issues found (non-blocking)"
      exit 0
    fi
    exit $EXIT_CODE
```

**Exit Codes**:
- `0`: No issues or low severity only
- `1`: Medium severity found
- `2`: High severity found
- `3`: Critical severity found

---

### Policy-Based Gates

Define policy in `.jpspec/security-policy.yml`:

```yaml
gates:
  pull_request:
    block_on: [critical, high]
    warn_on: [medium]
    audit_only: [low]

  main_branch:
    block_on: [critical]
    warn_on: [high, medium]
    audit_only: [low]
```

**Enforcement**:
```yaml
- name: Security Scan with Policy
  run: specify security scan --policy .jpspec/security-policy.yml
```

---

### Emergency Bypass

**Bypass via Commit Flag** (requires approval):
```bash
git commit --no-verify -m "fix: critical production bug [security-bypass]"
```

**Bypass via PR Label**:
```yaml
- name: Check Bypass Label
  id: bypass
  run: |
    LABELS=$(gh pr view ${{ github.event.pull_request.number }} --json labels -q '.labels[].name')
    if echo "$LABELS" | grep -q "security-scan-bypass"; then
      echo "bypass=true" >> $GITHUB_OUTPUT
    fi

- name: Security Scan
  if: steps.bypass.outputs.bypass != 'true'
  run: specify security scan --fail-on critical,high
```

**Audit Trail**:
- All bypasses logged to `docs/security/bypass-log.md`
- Security team notified via Slack/email
- Monthly review required

---

## SARIF Upload to GitHub Security

**Enable GitHub Code Scanning**:

1. Navigate to repository **Settings** → **Code security and analysis**
2. Enable **Code scanning**
3. Add SARIF upload step to workflow:

```yaml
- name: Upload SARIF to GitHub Security
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: security-results.sarif
    category: jpspec-security  # Group results by tool
```

**Benefits**:
- Findings appear in **Security** tab
- PR annotations for new vulnerabilities
- Track remediation over time

**Viewing Results**:
- Repository → **Security** → **Code scanning**
- Filter by severity, tool, status

---

## Artifact Retention

**Upload Scan Results**:
```yaml
- name: Upload Security Artifacts
  uses: actions/upload-artifact@v4
  with:
    name: security-scan-${{ github.sha }}
    path: |
      security-results.sarif
      docs/security/*.md
      docs/security/*.json
    retention-days: 90  # Compliance requirement
```

**Download Artifacts**:
```bash
# Via GitHub CLI
gh run download <run-id> -n security-scan-results

# Via web UI
Actions → Workflow Run → Artifacts
```

---

## Multi-Platform Support

### GitLab CI

```yaml
# .gitlab-ci.yml
security-scan:
  stage: test
  image: python:3.11-slim
  before_script:
    - pip install uv
    - uv tool install specify-cli
  script:
    - specify security scan --fail-on critical,high --format json,sarif
  artifacts:
    reports:
      sast: security-results.sarif
    paths:
      - docs/security/
    expire_in: 90 days
  cache:
    paths:
      - ~/.local/bin/semgrep
```

---

### Jenkins

```groovy
// Jenkinsfile
pipeline {
    agent any

    stages {
        stage('Security Scan') {
            steps {
                sh '''
                    pip install uv
                    uv tool install specify-cli
                    specify security scan --fail-on critical,high --format sarif
                '''
            }
        }

        stage('Upload Results') {
            steps {
                archiveArtifacts artifacts: 'security-results.sarif', fingerprint: true
                publishHTML([
                    reportDir: 'docs/security',
                    reportFiles: '*.html',
                    reportName: 'Security Scan Report'
                ])
            }
        }
    }

    post {
        always {
            recordIssues(tools: [sarif(pattern: 'security-results.sarif')])
        }
    }
}
```

---

### CircleCI

```yaml
# .circleci/config.yml
version: 2.1

jobs:
  security-scan:
    docker:
      - image: python:3.11-slim
    steps:
      - checkout

      - restore_cache:
          keys:
            - semgrep-{{ arch }}-1.50.0

      - run:
          name: Install Tools
          command: |
            pip install uv
            uv tool install specify-cli

      - run:
          name: Run Security Scan
          command: |
            specify security scan --fail-on critical,high --format sarif

      - save_cache:
          key: semgrep-{{ arch }}-1.50.0
          paths:
            - ~/.local/bin/semgrep

      - store_artifacts:
          path: security-results.sarif
          destination: security-scan

      - store_artifacts:
          path: docs/security
          destination: security-reports

workflows:
  version: 2
  build-and-scan:
    jobs:
      - security-scan
```

---

## Monitoring and Alerting

### Prometheus Metrics

**Expose metrics endpoint**:
```yaml
- name: Publish Metrics
  run: |
    # Push metrics to Prometheus Pushgateway
    specify security scan --metrics-push http://pushgateway:9091
```

**Key Metrics**:
- `jpspec_security_scan_duration_seconds` - Scan performance
- `jpspec_security_findings_total` - Findings by severity
- `jpspec_security_gate_blocks_total` - Pipeline blocks

---

### Slack Notifications

```yaml
- name: Notify Slack on Failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook: ${{ secrets.SLACK_SECURITY_WEBHOOK }}
    payload: |
      {
        "text": "🚨 Security scan failed in ${{ github.repository }}",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "*PR*: ${{ github.event.pull_request.html_url }}\n*Author*: ${{ github.actor }}"
            }
          }
        ]
      }
```

---

### Email Reports

```yaml
- name: Send Weekly Security Report
  if: github.event.schedule
  run: |
    specify security audit --format html > report.html

    # Send via SendGrid/AWS SES
    python scripts/send-email.py \
      --to security-team@example.com \
      --subject "Weekly Security Report" \
      --html report.html
```

---

## Troubleshooting

### Common Issues

#### 1. Scan Timeout

**Symptom**: Pipeline exceeds 10-minute timeout

**Solution**:
```yaml
# Increase timeout
- name: Security Scan
  timeout-minutes: 20  # Default is 10
  run: specify security scan

# Or use incremental scanning
- name: Security Scan
  run: specify security scan --incremental
```

---

#### 2. Semgrep Download Fails

**Symptom**: "Failed to install Semgrep"

**Solution**:
```yaml
# Pre-install Semgrep
- name: Install Semgrep
  run: pip install semgrep==1.50.0

# Or use Docker
- name: Run Semgrep via Docker
  run: |
    docker run --rm -v $(pwd):/src returntocorp/semgrep:latest \
      semgrep scan --config auto --json --output results.json /src
```

---

#### 3. SARIF Upload Permission Denied

**Symptom**: "Resource not accessible by integration"

**Solution**:
```yaml
jobs:
  security-scan:
    permissions:
      contents: read
      security-events: write  # Required for SARIF upload
```

---

#### 4. Cache Miss (Slow Scans)

**Symptom**: Cache never hits, scans always slow

**Solution**:
```yaml
# Check cache key
- name: Cache Semgrep
  uses: actions/cache@v4
  with:
    path: ~/.local/bin/semgrep
    key: semgrep-${{ runner.os }}-1.50.0  # Must be stable
    restore-keys: semgrep-${{ runner.os }}-  # Fallback
```

---

## Best Practices

### 1. Run Scans Early and Often

- ✅ Pre-commit hooks for instant feedback
- ✅ PR checks to prevent vulnerable code merges
- ✅ Scheduled scans to catch new vulnerabilities

### 2. Use Incremental Scanning

- ✅ Faster feedback (10x speedup)
- ✅ Lower CI minute consumption
- ✅ Full scans only on main branch

### 3. Cache Aggressively

- ✅ Cache tool binaries (Semgrep)
- ✅ Cache scan results (unchanged code)
- ✅ Use stable cache keys

### 4. Separate Blocking vs. Auditing

- ✅ Block critical/high in PRs
- ✅ Audit medium/low in post-merge
- ✅ Emergency bypass with approval

### 5. Track Metrics

- ✅ DORA metrics (lead time, MTTR)
- ✅ Security posture (findings over time)
- ✅ False positive rate

---

## Example Projects

### 1. JP Spec Kit (Python)

**Workflow**: `.github/workflows/security.yml`
```yaml
on: [pull_request, push]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install uv && uv tool install specify-cli
      - run: specify security scan --fail-on critical,high
```

---

### 2. React App (TypeScript)

**Workflow**: `.github/workflows/security.yml`
```yaml
on: [pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm install -g specify-cli
      - run: specify security scan --path src --fail-on critical,high
```

---

### 3. Monorepo (Multi-language)

**Workflow**: Parallel scanning by component
```yaml
jobs:
  security:
    strategy:
      matrix:
        component: [backend, frontend, infrastructure]
    steps:
      - run: specify security scan --path ${{ matrix.component }}
```

---

## References

- **Platform Design**: `docs/platform/jpspec-security-platform.md`
- **PRD**: `docs/prd/jpspec-security-commands.md`
- **GitHub Actions Docs**: https://docs.github.com/en/actions
- **SARIF Spec**: https://docs.oasis-open.org/sarif/sarif/v2.1.0/

---

**Document Status**: ✅ Complete
**Next Steps**: Implement CI/CD pipeline (task-XXX)
**Owner**: @platform-engineer
