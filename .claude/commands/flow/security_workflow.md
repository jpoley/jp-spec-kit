---
description: Integrate security scanning and remediation into the SDD workflow with automatic backlog task creation.
loop: both
# Loop Classification: BOTH LOOPS
# Security commands span both loops: scanning happens in inner loop (pre-commit validation),
# while compliance reporting and remediation tracking occur in outer loop (CI/CD).
---

# /flow:security - Security Workflow Integration

Integrate comprehensive security scanning, vulnerability triage, and automated remediation task creation into your Spec-Driven Development workflow.

## Overview

The `/flow:security` command family integrates security assessment into your development workflow by:

1. **Scanning** - SAST, SCA, secrets detection on codebase
2. **Triaging** - AI-powered vulnerability assessment and false positive detection
3. **Reporting** - Comprehensive audit reports with OWASP Top 10 compliance
4. **Task Creation** - Automatic backlog task creation for findings via `--create-tasks` flag
5. **Workflow Integration** - Seamless integration with flowspec_workflow.yml states

## Command Family

```bash
# Full workflow
/flow:security scan      # Run security scanners
/flow:security triage    # Triage findings with AI
/flow:security report    # Generate audit report
/flow:security fix       # Generate patches for findings

# Workflow integration features
/flow:security scan --create-tasks     # Auto-create backlog tasks for findings
/flow:security report --create-tasks   # Create tasks during reporting
```

## Workflow Integration Patterns

### Pattern 1: Dedicated Security State

Add a dedicated security verification state for security-focused teams:

```yaml
# flowspec_workflow.yml additions

states:
  - "To Do"
  - "Assessed"
  - "Specified"
  - "Researched"
  - "Planned"
  - "In Implementation"
  - "Security Review"      # NEW: Dedicated security state
  - "Validated"
  - "Deployed"
  - "Done"

workflows:
  security:
    command: "/flow:security"
    description: "Execute security scans and create remediation tasks"
    agents:
      - name: "secure-by-design-engineer"
        identity: "@secure-by-design-engineer"
        description: "Security specialist for vulnerability assessment"
        responsibilities:
          - "Security scanning (SAST, SCA, secrets)"
          - "Vulnerability triage and prioritization"
          - "Security task creation in backlog"
          - "SARIF generation for GitHub Security"
    input_states: ["In Implementation"]
    output_state: "Security Review"
    optional: false
    creates_backlog_tasks: true

transitions:
  - name: "security_review"
    from: "In Implementation"
    to: "Security Review"
    via: "security"
    description: "Security scan completed, findings triaged"
    output_artifacts:
      - type: "security_scan_results"
        path: "./docs/security/scan-results.json"
        required: true
      - type: "security_triage"
        path: "./docs/security/triage-results.json"
        required: true
      - type: "security_report"
        path: "./docs/security/audit-report.md"
        required: true
      - type: "backlog_tasks"
        path: "./backlog/tasks/*.md"
        multiple: true
    validation: "NONE"

  - name: "validate_after_security"
    from: "Security Review"
    to: "Validated"
    via: "validate"
    description: "QA validation after security review"
    input_artifacts:
      - type: "security_report"
        path: "./docs/security/audit-report.md"
        required: true
    validation: "NONE"
```

**When to use:**
- Security is a critical gate in your workflow
- Dedicated security team reviews all changes
- Want explicit security approval before QA
- Need clear audit trail for compliance

**Workflow sequence:**
```
Implementation -> Security Review -> Validated -> Deployed
```

### Pattern 2: Extend Validate Workflow

Integrate security into existing validate workflow for streamlined processes:

```yaml
# flowspec_workflow.yml - extend validate workflow

workflows:
  validate:
    command: "/flow:validate"
    description: "Execute validation using QA, security, and documentation agents"
    agents:
      - name: "quality-guardian"
        identity: "@quality-guardian"
        description: "Quality Guardian"
        responsibilities:
          - "Functional and integration testing"
          - "Performance testing"
      - name: "secure-by-design-engineer"
        identity: "@secure-by-design-engineer"
        description: "Secure-by-Design Engineer"
        responsibilities:
          - "Security scanning (SAST, SCA, secrets)"
          - "Vulnerability triage and assessment"
          - "Security task creation with --create-tasks"
          - "SARIF output generation"
      - name: "tech-writer"
        identity: "@tech-writer"
        description: "Senior Technical Writer"
        responsibilities:
          - "API documentation and user guides"
    input_states: ["In Implementation"]
    output_state: "Validated"
    optional: false
    creates_backlog_tasks: true  # Security can create tasks

transitions:
  - name: "validate"
    from: "In Implementation"
    to: "Validated"
    via: "validate"
    description: "QA, security, and documentation validated"
    output_artifacts:
      - type: "qa_report"
        path: "./docs/qa/{feature}-qa-report.md"
      - type: "security_report"
        path: "./docs/security/{feature}-security.md"
        required: true
      - type: "security_scan_sarif"
        path: "./docs/security/{feature}-sarif.json"
      - type: "backlog_tasks"
        path: "./backlog/tasks/*.md"
        multiple: true
    validation: "NONE"
```

**When to use:**
- Integrated security approach
- Fast-moving teams
- Security is part of definition of done
- Fewer formal gates preferred

**Workflow sequence:**
```
Implementation -> Validated (includes security) -> Deployed
```

## Automatic Task Creation with --create-tasks

### Overview

The `--create-tasks` flag automatically creates backlog tasks for security findings, eliminating manual task creation and ensuring remediation tracking.

### Usage

```bash
# Create tasks during scan
/flow:security scan --create-tasks

# Create tasks during report generation
/flow:security report --create-tasks

# Control which severities create tasks
/flow:security scan --create-tasks --severity critical,high
```

### Task Format

Each created task follows a standardized format:

**Title:**
```
Security: [Vulnerability Type] in [Component]
```

**Description:**
```markdown
## Security Finding

**Vulnerability ID:** VULN-001
**Severity:** Critical
**CVSS Score:** 9.8
**CWE:** CWE-89: SQL Injection
**OWASP:** A03: Injection

## Description

[Technical description of the vulnerability]

## Location

- File: `src/auth/login.py:45`
- Component: Authentication Service
- Function: `authenticate_user()`

## Impact

[What could an attacker do with this vulnerability?]

## Remediation Steps

1. Replace string concatenation with parameterized queries
2. Add input validation for username and password parameters
3. Implement prepared statements via SQLAlchemy

## References

- [CWE-89](https://cwe.mitre.org/data/definitions/89.html)
- [OWASP A03](https://owasp.org/Top10/A03_2021-Injection/)

---

**Created by:** /flow:security --create-tasks
**Audit Report:** docs/security/audit-report.md
```

**Acceptance Criteria:**
- Derived from remediation steps
- Include verification tests
- Code review requirement

**Labels:**
- `security` - Always applied
- Severity: `critical`, `high`, `medium`, or `low`
- Component: `backend`, `frontend`, `infra`
- Type: `injection`, `crypto`, `auth`, `dependency`

**Priority:**
- Critical findings -> `critical` priority
- High findings -> `high` priority
- Medium findings -> `medium` priority
- Low findings -> `low` priority

**Assignment:**
- Backend vulnerabilities -> `@backend-engineer`
- Frontend vulnerabilities -> `@frontend-engineer`
- Infrastructure issues -> `@platform-engineer`

### Example Task Creation

```bash
# Automatically created task
backlog task create "Security: SQL Injection in login endpoint" \
  -d "[Full description as shown above]" \
  --ac "Parameterized queries implemented using SQLAlchemy" \
  --ac "Input validation added for username and password" \
  --ac "Security test added to test suite" \
  --ac "Code review completed by @backend-code-reviewer" \
  -l security,critical,backend,injection \
  --priority critical \
  -a @backend-engineer
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Security Scan

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    permissions:
      security-events: write  # For SARIF upload
      pull-requests: write     # For comments

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install uv
          uv sync
          uv tool install .

      - name: Run security scan
        run: |
          flowspec security scan --format sarif --output security-results.sarif

      - name: Upload SARIF to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: security-results.sarif

      - name: Triage findings
        run: |
          flowspec security triage --input security-results.sarif

      - name: Generate report and create tasks
        if: github.event_name == 'pull_request'
        run: |
          flowspec security report --create-tasks --severity critical,high

      - name: Block on critical findings
        run: |
          CRITICAL_COUNT=$(jq '[.findings[] | select(.severity == "critical")] | length' docs/security/triage-results.json)
          if [ "$CRITICAL_COUNT" -gt 0 ]; then
            echo "[X] Found $CRITICAL_COUNT critical vulnerabilities"
            exit 1
          fi
```

### GitLab CI

```yaml
security-scan:
  stage: test
  image: python:3.11

  before_script:
    - pip install uv
    - uv sync
    - uv tool install .

  script:
    - flowspec security scan --format sarif --output gl-sast-report.json
    - flowspec security triage --input gl-sast-report.json
    - flowspec security report --create-tasks --severity critical,high

  artifacts:
    reports:
      sast: gl-sast-report.json
    paths:
      - docs/security/

  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'

  allow_failure:
    exit_codes: 0  # Change to block on findings
```

## Pre-Commit Hook Integration (Optional)

### Enable Pre-Commit Scanning

Users can optionally enable pre-commit security scanning:

```bash
# Enable pre-commit hook
flowspec hooks enable pre-commit-security

# Configure in .flowspec/hooks/hooks.yaml
cat > .flowspec/hooks/hooks.yaml << 'EOF'
version: "1.0"

hooks:
  pre-commit:
    - name: "security-scan-staged"
      description: "Scan staged files for security issues"
      script: "scripts/security/pre-commit-scan.sh"
      on_failure: "warn"  # or "block" to prevent commit
EOF

# Create pre-commit script
cat > scripts/security/pre-commit-scan.sh << 'EOF'
#!/bin/bash
set -e

echo "Running security scan on staged files..."

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
  echo "No staged files to scan"
  exit 0
fi

# Run security scan on staged files only
flowspec security scan --staged-only --output docs/security/pre-commit-scan.json

# Check for critical findings
CRITICAL_COUNT=$(jq '[.findings[] | select(.severity == "critical")] | length' docs/security/pre-commit-scan.json)

if [ "$CRITICAL_COUNT" -gt 0 ]; then
  echo "[X] Found $CRITICAL_COUNT critical security issues in staged files"
  echo "   Run 'flowspec security triage' to review findings"
  exit 1
fi

echo "✅ No critical security issues found"
exit 0
EOF

chmod +x scripts/security/pre-commit-scan.sh
```

### Configuration Options

```yaml
# .flowspec/hooks/hooks.yaml

hooks:
  pre-commit:
    - name: "security-scan-staged"
      description: "Scan staged files for security issues"
      script: "scripts/security/pre-commit-scan.sh"

      # Failure behavior
      on_failure: "warn"    # Warn but allow commit (default)
      # on_failure: "block" # Block commit on findings

      # Severity threshold
      block_on:
        - critical          # Always block critical
        # - high           # Optionally block high

      # Task creation
      create_tasks: true    # Auto-create tasks for findings
      task_severity:
        - critical
        - high
```

## SARIF Output for GitHub Security Tab

### What is SARIF?

SARIF (Static Analysis Results Interchange Format) is a standard format for static analysis tool output. GitHub Code Scanning uses SARIF to display security findings in the Security tab.

### Enable SARIF Output

```bash
# Generate SARIF during scan
flowspec security scan --format sarif --output security-results.sarif

# Upload to GitHub Security (via GitHub Actions)
- name: Upload SARIF to GitHub Security
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: security-results.sarif
```

### SARIF Format Example

```json
{
  "version": "2.1.0",
  "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "Flowspec Security Scanner",
          "version": "1.0.0",
          "informationUri": "https://github.com/jpoley/flowspec",
          "rules": [
            {
              "id": "CWE-89",
              "name": "SQL Injection",
              "shortDescription": {
                "text": "SQL Injection vulnerability"
              },
              "fullDescription": {
                "text": "The application uses string concatenation to build SQL queries, allowing SQL injection attacks."
              },
              "help": {
                "text": "Use parameterized queries or prepared statements."
              },
              "properties": {
                "security-severity": "9.8"
              }
            }
          ]
        }
      },
      "results": [
        {
          "ruleId": "CWE-89",
          "level": "error",
          "message": {
            "text": "SQL Injection vulnerability detected in login endpoint"
          },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": {
                  "uri": "src/auth/login.py",
                  "uriBaseId": "%SRCROOT%"
                },
                "region": {
                  "startLine": 45,
                  "startColumn": 10,
                  "endLine": 45,
                  "endColumn": 50
                }
              }
            }
          ],
          "properties": {
            "severity": "critical",
            "cvss": 9.8,
            "cwe": "CWE-89",
            "owasp": "A03"
          }
        }
      ]
    }
  ]
}
```

### Benefits of SARIF Integration

1. **GitHub Security Tab** - Findings appear in repository Security tab
2. **Code Annotations** - Vulnerabilities annotated inline in PRs
3. **Trend Analysis** - Track security posture over time
4. **Alerts** - GitHub notifies on new vulnerabilities
5. **Standard Format** - Works with all SARIF-compatible tools

## Best Practices

### Workflow Integration

1. **Choose the Right Pattern**
   - Use dedicated state for security-focused teams
   - Extend validate for fast-moving integrated teams

2. **Gate Appropriately**
   - Block on Critical/High in production branches
   - Warn on Medium/Low to maintain velocity

3. **Automate Task Creation**
   - Use `--create-tasks` for consistent tracking
   - Filter by severity to avoid noise

4. **Track Remediation**
   - Use backlog tasks to track fixes
   - Re-scan after fixes to verify

### CI/CD Integration

1. **Run on Every PR** - Catch issues before merge
2. **Upload SARIF** - Integrate with GitHub Security
3. **Comment on PRs** - Surface findings in code review
4. **Block Critical** - Prevent merging vulnerable code
5. **Track Metrics** - Monitor security posture trends

### Pre-Commit Hooks

1. **Optional by Design** - Let teams choose their workflow
2. **Fast Scans Only** - Only scan staged files
3. **Warn, Don't Block** - Use `on_failure: warn` for most teams
4. **Critical Only** - Block only on critical findings
5. **Clear Feedback** - Show exactly what's wrong and how to fix

## Troubleshooting

### Tasks Not Being Created

```bash
# Check if --create-tasks flag is set
flowspec security scan --create-tasks --severity critical,high

# Verify triage results exist
ls -l docs/security/triage-results.json

# Check backlog is accessible
backlog task list --plain
```

### SARIF Upload Fails

```bash
# Verify SARIF format is valid
jq . security-results.sarif

# Check GitHub Actions permissions
# Add to workflow:
permissions:
  security-events: write
```

### Pre-Commit Hook Not Running

```bash
# Verify hook is installed
ls -l .git/hooks/pre-commit

# Check hook script is executable
chmod +x scripts/security/pre-commit-scan.sh

# Test manually
bash scripts/security/pre-commit-scan.sh
```

## See Also

- `/flow:security scan` - Run security scanners
- `/flow:security triage` - Triage findings
- `/flow:security report` - Generate audit reports
- `/flow:security fix` - Generate fix patches
- [Security Workflow Integration Guide](../../docs/guides/security-workflow-integration.md)
- [CI/CD Integration Examples](../../docs/platform/security-cicd-examples.md)
