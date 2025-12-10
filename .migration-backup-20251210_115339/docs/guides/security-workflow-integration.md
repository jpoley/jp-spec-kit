# Security Workflow Integration Guide

This guide shows how to integrate `/jpspec:security` commands into your Spec-Driven Development workflow, including automatic task creation, CI/CD integration, and SARIF output for GitHub Security.

## Table of Contents

- [Overview](#overview)
- [Workflow Integration Patterns](#workflow-integration-patterns)
- [Automatic Task Creation](#automatic-task-creation)
- [CI/CD Integration](#cicd-integration)
- [Pre-Commit Hooks](#pre-commit-hooks)
- [SARIF Output](#sarif-output)
- [Best Practices](#best-practices)

## Overview

The `/jpspec:security` command family provides comprehensive security scanning and remediation tracking for your SDD workflow:

```bash
/jpspec:security scan      # Run SAST, SCA, secrets detection
/jpspec:security triage    # AI-powered vulnerability assessment
/jpspec:security report    # Generate audit reports
/jpspec:security fix       # Generate patches for findings
```

**Key Integration Features:**

1. **Workflow States** - Add security to your `jpspec_workflow.yml`
2. **Automatic Tasks** - Create backlog tasks with `--create-tasks` flag
3. **CI/CD Integration** - GitHub Actions, GitLab CI examples
4. **SARIF Output** - GitHub Security tab integration
5. **Pre-Commit Hooks** - Optional pre-commit scanning

## Workflow Integration Patterns

### Pattern 1: Dedicated Security State

**Best for:** Security-focused teams, compliance requirements, explicit security gates

Add a dedicated "Security Review" state to your workflow:

```yaml
# jpspec_workflow.yml

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
```

**Add security workflow:**

```yaml
workflows:
  security:
    command: "/jpspec:security"
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
```

**Add transitions:**

```yaml
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

**Workflow sequence:**

```
Implementation → /jpspec:security → Security Review → /jpspec:validate → Validated → Deployed
```

**When to use:**
- Security is a critical compliance requirement
- Dedicated security team reviews all changes
- Need explicit security approval gate
- Clear audit trail required

### Pattern 2: Extend Validate Workflow

**Best for:** Fast-moving teams, integrated security approach, fewer formal gates

Extend the existing validate workflow to include security:

```yaml
# jpspec_workflow.yml

workflows:
  validate:
    command: "/jpspec:validate"
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
```

**Update transition artifacts:**

```yaml
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

**Workflow sequence:**

```
Implementation → /jpspec:validate (includes security) → Validated → Deployed
```

**When to use:**
- Integrated security is part of definition of done
- Fast iteration velocity preferred
- Security team embedded with development
- Streamlined process desired

## Automatic Task Creation

### Overview

The `--create-tasks` flag automatically creates backlog tasks for security findings, eliminating manual work and ensuring remediation tracking.

### Basic Usage

```bash
# Create tasks during scan
/jpspec:security scan --create-tasks

# Create tasks during report generation
/jpspec:security report --create-tasks

# Control which severities create tasks
/jpspec:security scan --create-tasks --severity critical,high
```

### Task Format

Each security finding becomes a structured backlog task:

**Title Format:**
```
Security: [Vulnerability Type] in [Component]
```

**Examples:**
- `Security: SQL Injection in login endpoint`
- `Security: XSS vulnerability in admin panel`
- `Security: Outdated dependency (lodash) with known CVEs`

**Description Format:**

```markdown
## Security Finding

**Vulnerability ID:** VULN-001
**Severity:** Critical
**CVSS Score:** 9.8
**CWE:** CWE-89: SQL Injection
**OWASP:** A03: Injection

## Description

The login endpoint uses string concatenation to build SQL queries, allowing
attackers to inject arbitrary SQL code and bypass authentication.

## Location

- File: `src/auth/login.py:45`
- Component: Authentication Service
- Function: `authenticate_user()`

## Impact

An attacker could:
- Bypass authentication completely
- Extract all user credentials from database
- Modify or delete database contents
- Execute arbitrary commands on database server

## Remediation Steps

1. Replace string concatenation with parameterized queries
2. Add input validation for username and password parameters
3. Implement prepared statements via SQLAlchemy
4. Add security test to verify SQL injection is prevented

## References

- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)
- [OWASP A03: Injection](https://owasp.org/Top10/A03_2021-Injection/)

---

**Created by:** /jpspec:security --create-tasks
**Audit Report:** docs/security/audit-report.md
```

**Acceptance Criteria** (derived from remediation steps):
- [ ] Parameterized queries implemented using SQLAlchemy
- [ ] Input validation added for username and password
- [ ] Prepared statements used for all database queries
- [ ] Security test added to test suite
- [ ] Code review completed by @backend-code-reviewer

**Labels:**
- `security` (always)
- `critical` (severity)
- `backend` (component)
- `injection` (vulnerability type)

**Priority:** `critical` (mapped from severity)

**Assignee:** `@backend-engineer` (based on component)

### Severity Filtering

Control which findings create tasks:

```bash
# Only critical and high (recommended for most teams)
/jpspec:security scan --create-tasks --severity critical,high

# All severities (may create noise)
/jpspec:security scan --create-tasks --severity critical,high,medium,low

# Critical only (for very high-velocity teams)
/jpspec:security scan --create-tasks --severity critical
```

### Priority Mapping

| Security Severity | Backlog Priority | Timeline |
|-------------------|------------------|----------|
| Critical | critical | Fix immediately |
| High | high | Fix within 7 days |
| Medium | medium | Fix within 30 days |
| Low | low | Fix within 90 days |

### Example: Created Task

```bash
# Task automatically created by --create-tasks
$ backlog task list --plain

task-301 | Security: SQL Injection in login endpoint | @backend-engineer | Critical | To Do
```

```bash
# View task details
$ backlog task task-301

Task: task-301
Title: Security: SQL Injection in login endpoint
Status: To Do
Priority: critical
Assignee: @backend-engineer
Labels: security, critical, backend, injection

Acceptance Criteria:
- [ ] Parameterized queries implemented using SQLAlchemy
- [ ] Input validation added for username and password
- [ ] Prepared statements used for all database queries
- [ ] Security test added to test suite
- [ ] Code review completed by @backend-code-reviewer

Description:
[Full description as shown above]
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/security-scan.yml`:

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
      pull-requests: write    # For PR comments

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install jp-spec-kit
        run: |
          pip install uv
          uv sync
          uv tool install .

      - name: Run security scan
        run: |
          specify security scan --format sarif --output security-results.sarif

      - name: Upload SARIF to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: security-results.sarif
        if: always()

      - name: Triage findings
        run: |
          specify security triage --input security-results.sarif

      - name: Generate report and create tasks
        if: github.event_name == 'pull_request'
        run: |
          specify security report --create-tasks --severity critical,high

      - name: Block on critical findings
        run: |
          CRITICAL_COUNT=$(jq '[.findings[] | select(.severity == "critical")] | length' docs/security/triage-results.json)
          if [ "$CRITICAL_COUNT" -gt 0 ]; then
            echo "❌ Found $CRITICAL_COUNT critical vulnerabilities - blocking merge"
            exit 1
          fi
          echo "✅ No critical vulnerabilities found"

      - name: Comment on PR
        if: github.event_name == 'pull_request' && always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('docs/security/audit-report.md', 'utf8');

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Security Scan Results\n\n${report}`
            });
```

**Key Features:**
- Runs on every PR and main branch push
- Uploads SARIF to GitHub Security tab
- Creates backlog tasks for critical/high findings
- Blocks PR merge on critical vulnerabilities
- Comments security report on PR

### GitLab CI

Create `.gitlab-ci.yml` or add to existing file:

```yaml
stages:
  - test

security-scan:
  stage: test
  image: python:3.11

  before_script:
    - pip install uv
    - uv sync
    - uv tool install .

  script:
    # Run scan and generate SARIF
    - specify security scan --format sarif --output gl-sast-report.json

    # Triage findings
    - specify security triage --input gl-sast-report.json

    # Generate report and create tasks
    - specify security report --create-tasks --severity critical,high

    # Check for critical findings
    - |
      CRITICAL_COUNT=$(jq '[.findings[] | select(.severity == "critical")] | length' docs/security/triage-results.json)
      if [ "$CRITICAL_COUNT" -gt 0 ]; then
        echo "❌ Found $CRITICAL_COUNT critical vulnerabilities"
        exit 1
      fi

  artifacts:
    reports:
      sast: gl-sast-report.json
    paths:
      - docs/security/
    expire_in: 1 week

  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
```

**Key Features:**
- GitLab SAST report integration
- Blocks merge on critical findings
- Creates backlog tasks automatically
- Archives security reports as artifacts

### Jenkins Pipeline

```groovy
pipeline {
    agent any

    stages {
        stage('Security Scan') {
            steps {
                sh 'specify security scan --format sarif --output security-results.sarif'
            }
        }

        stage('Triage') {
            steps {
                sh 'specify security triage --input security-results.sarif'
            }
        }

        stage('Report & Tasks') {
            steps {
                sh 'specify security report --create-tasks --severity critical,high'
            }
        }

        stage('Gate') {
            steps {
                script {
                    def criticalCount = sh(
                        script: "jq '[.findings[] | select(.severity == \"critical\")] | length' docs/security/triage-results.json",
                        returnStdout: true
                    ).trim()

                    if (criticalCount.toInteger() > 0) {
                        error("Found ${criticalCount} critical vulnerabilities")
                    }
                }
            }
        }
    }

    post {
        always {
            publishHTML([
                reportDir: 'docs/security',
                reportFiles: 'audit-report.html',
                reportName: 'Security Report'
            ])
        }
    }
}
```

## Pre-Commit Hooks

### Overview

Pre-commit hooks run security scans on staged files before commit, catching issues early in the development cycle.

**Important:** Pre-commit hooks are **optional** - teams choose whether to enable them.

### Enable Pre-Commit Scanning

```bash
# Initialize hooks configuration
specify hooks init

# Enable pre-commit security scanning
specify hooks enable pre-commit-security
```

### Configuration

Create `.specify/hooks/hooks.yaml`:

```yaml
version: "1.0"

hooks:
  pre-commit:
    - name: "security-scan-staged"
      description: "Scan staged files for security issues"
      script: "scripts/security/pre-commit-scan.sh"

      # Failure behavior
      on_failure: "warn"    # Warn but allow commit (recommended)
      # on_failure: "block" # Block commit on findings (strict mode)

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

### Pre-Commit Script

Create `scripts/security/pre-commit-scan.sh`:

```bash
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
specify security scan --staged-only --output docs/security/pre-commit-scan.json

# Check for critical findings
CRITICAL_COUNT=$(jq '[.findings[] | select(.severity == "critical")] | length' docs/security/pre-commit-scan.json)
HIGH_COUNT=$(jq '[.findings[] | select(.severity == "high")] | length' docs/security/pre-commit-scan.json)

if [ "$CRITICAL_COUNT" -gt 0 ]; then
  echo "❌ Found $CRITICAL_COUNT critical security issues in staged files"
  echo "   Run 'specify security triage' to review findings"
  exit 1
fi

if [ "$HIGH_COUNT" -gt 0 ]; then
  echo "⚠️  Found $HIGH_COUNT high security issues in staged files"
  echo "   Consider fixing before committing"
  # Warn but don't block (change exit 0 to exit 1 to block)
  exit 0
fi

echo "✅ No critical security issues found in staged files"
exit 0
```

Make script executable:

```bash
chmod +x scripts/security/pre-commit-scan.sh
```

### Configuration Options

| Option | Values | Description |
|--------|--------|-------------|
| `on_failure` | `warn`, `block` | Warn (allow commit) or block (prevent commit) |
| `block_on` | `critical`, `high`, `medium`, `low` | Severities that block commit |
| `create_tasks` | `true`, `false` | Auto-create backlog tasks for findings |
| `task_severity` | List of severities | Which severities create tasks |

### Recommended Configurations

**Balanced (Recommended):**
```yaml
on_failure: "warn"
block_on: [critical]
create_tasks: true
task_severity: [critical, high]
```
- Blocks only critical findings
- Warns on high/medium/low
- Creates tasks for critical and high

**Strict:**
```yaml
on_failure: "block"
block_on: [critical, high]
create_tasks: true
task_severity: [critical, high, medium]
```
- Blocks critical and high findings
- Creates tasks for all significant findings

**Permissive:**
```yaml
on_failure: "warn"
block_on: []
create_tasks: true
task_severity: [critical]
```
- Never blocks commits
- Creates tasks only for critical findings
- Relies on CI/CD for enforcement

## SARIF Output

### What is SARIF?

SARIF (Static Analysis Results Interchange Format) is a standard JSON format for static analysis tool output. GitHub Code Scanning uses SARIF to display security findings.

### Generate SARIF

```bash
# Generate SARIF during scan
specify security scan --format sarif --output security-results.sarif

# Upload to GitHub (via GitHub Actions)
- name: Upload SARIF to GitHub Security
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: security-results.sarif
```

### SARIF Format

```json
{
  "version": "2.1.0",
  "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "JP Spec Kit Security Scanner",
          "version": "1.0.0",
          "informationUri": "https://github.com/jpoley/jp-spec-kit",
          "rules": [
            {
              "id": "CWE-89",
              "name": "SQL Injection",
              "shortDescription": {
                "text": "SQL Injection vulnerability"
              },
              "fullDescription": {
                "text": "The application uses string concatenation to build SQL queries."
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
                  "startColumn": 10
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

### GitHub Security Tab Integration

When SARIF is uploaded to GitHub:

1. **Security Tab** - View all findings in repository Security tab
2. **Code Annotations** - Vulnerabilities appear inline in PRs
3. **Alerts** - GitHub creates security alerts
4. **Trend Analysis** - Track security posture over time
5. **Notifications** - Email/Slack on new vulnerabilities

### Viewing Security Findings

**In GitHub:**
1. Go to repository **Security** tab
2. Click **Code scanning alerts**
3. View findings by severity, tool, branch
4. Click finding to see code location and remediation

**In Pull Requests:**
1. Findings appear as annotations on changed lines
2. Click annotation to see full details
3. Dismiss false positives with reason
4. Track remediation in PR comments

## Best Practices

### Workflow Integration

1. **Choose the Right Pattern**
   - Dedicated state for security-focused teams
   - Extend validate for integrated teams
   - Consider compliance requirements

2. **Gate Appropriately**
   - Block critical/high in production branches
   - Warn on medium/low to maintain velocity
   - Allow overrides with approval for hotfixes

3. **Automate Task Creation**
   - Use `--create-tasks` for consistency
   - Filter by severity to avoid noise
   - Map severity to priority correctly

4. **Track Remediation**
   - Use backlog tasks to track fixes
   - Re-scan after fixes to verify
   - Close tasks when verified

### CI/CD Integration

1. **Run on Every PR** - Catch issues before merge
2. **Upload SARIF** - Integrate with GitHub Security
3. **Comment on PRs** - Surface findings in code review
4. **Block Critical** - Prevent merging vulnerable code
5. **Track Metrics** - Monitor trends over time

### Pre-Commit Hooks

1. **Optional by Design** - Let teams choose
2. **Fast Scans Only** - Only scan staged files
3. **Warn, Don't Block** - Use `on_failure: warn` for most teams
4. **Critical Only** - Block only on critical findings
5. **Clear Feedback** - Show what's wrong and how to fix

### Task Management

1. **Be Specific** - Clear titles and descriptions
2. **Actionable ACs** - Verifiable acceptance criteria
3. **Appropriate Priority** - Map severity correctly
4. **Assign Correctly** - Route to right team/engineer
5. **Track Progress** - Update as work proceeds

## Troubleshooting

### Tasks Not Being Created

```bash
# Verify --create-tasks flag is set
specify security scan --create-tasks --severity critical,high

# Check triage results exist
ls -l docs/security/triage-results.json

# Verify backlog is accessible
backlog task list --plain

# Check for errors in scan output
specify security scan --verbose --create-tasks
```

### SARIF Upload Fails

```bash
# Validate SARIF format
jq . security-results.sarif

# Check GitHub Actions permissions
# Ensure workflow has:
permissions:
  security-events: write

# Verify file exists
ls -l security-results.sarif
```

### Pre-Commit Hook Not Running

```bash
# Verify hook is installed
ls -l .git/hooks/pre-commit

# Check script is executable
chmod +x scripts/security/pre-commit-scan.sh

# Test manually
bash scripts/security/pre-commit-scan.sh

# Check hook configuration
cat .specify/hooks/hooks.yaml
```

### GitHub Security Tab Empty

```bash
# Verify SARIF was uploaded
# Check GitHub Actions logs for upload step

# Ensure correct branch
# Code scanning only shows alerts for default branch and PRs

# Check file format
# Must be valid SARIF 2.1.0 format
```

## Next Steps

- [CI/CD Integration Examples](../platform/security-cicd-examples.md) - Complete CI/CD configurations
- [SARIF Output Guide](../../templates/docs/security/sarif-output-guide.md) - SARIF format specification
- `/jpspec:security scan --help` - Security scan command reference
- [Security Commands Documentation](../reference/security-commands.md) - Complete command reference

## See Also

- [Workflow Architecture](workflow-architecture.md)
- [Workflow State Mapping](workflow-state-mapping.md)
- [Security Reporter Skill](../../.claude/skills/security-reporter/SKILL.md)
- [Security Workflow Skill](../../.claude/skills/security-workflow/SKILL.md)
