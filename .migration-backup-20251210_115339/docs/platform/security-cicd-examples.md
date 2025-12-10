# Security CI/CD Integration Examples

Complete, production-ready CI/CD configurations for integrating `/jpspec:security` commands into your development workflow.

## Table of Contents

- [GitHub Actions](#github-actions)
- [GitLab CI](#gitlab-ci)
- [Jenkins](#jenkins)
- [CircleCI](#circleci)
- [Pre-Commit Hooks](#pre-commit-hooks)
- [SARIF Upload Configuration](#sarif-upload-configuration)

## GitHub Actions

### Complete Security Workflow

Create `.github/workflows/security-scan.yml`:

```yaml
name: Security Scan

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main, develop]
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'

permissions:
  contents: read
  security-events: write
  pull-requests: write

jobs:
  security-scan:
    name: Security Analysis
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for better analysis

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install jp-spec-kit
        run: |
          pip install uv
          uv sync
          uv tool install .

      - name: Cache security scan results
        uses: actions/cache@v4
        with:
          path: |
            docs/security/
            .security-cache/
          key: security-scan-${{ github.sha }}
          restore-keys: |
            security-scan-

      - name: Run security scan
        id: scan
        run: |
          specify security scan \
            --format sarif \
            --output security-results.sarif \
            --cache .security-cache
        continue-on-error: true

      - name: Upload SARIF to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: security-results.sarif
          category: jp-spec-kit-security
        if: always()

      - name: Triage findings with AI
        id: triage
        run: |
          specify security triage \
            --input security-results.sarif \
            --output docs/security/triage-results.json \
            --false-positive-detection \
            --context docs/prd/

      - name: Generate audit report
        run: |
          specify security report \
            --input docs/security/triage-results.json \
            --output docs/security/audit-report.md \
            --format markdown

      - name: Create backlog tasks for findings
        if: github.event_name == 'pull_request'
        run: |
          specify security report \
            --create-tasks \
            --severity critical,high \
            --assignee-mapping .github/security-assignees.yml

      - name: Check security gate
        id: gate
        run: |
          # Count critical and high severity findings
          CRITICAL=$(jq '[.findings[] | select(.severity == "critical")] | length' docs/security/triage-results.json)
          HIGH=$(jq '[.findings[] | select(.severity == "high")] | length' docs/security/triage-results.json)
          MEDIUM=$(jq '[.findings[] | select(.severity == "medium")] | length' docs/security/triage-results.json)

          echo "critical=$CRITICAL" >> $GITHUB_OUTPUT
          echo "high=$HIGH" >> $GITHUB_OUTPUT
          echo "medium=$MEDIUM" >> $GITHUB_OUTPUT

          # Fail if critical findings exist
          if [ "$CRITICAL" -gt 0 ]; then
            echo "::error::Found $CRITICAL critical security vulnerabilities"
            exit 1
          fi

          # Warn if high findings exist
          if [ "$HIGH" -gt 0 ]; then
            echo "::warning::Found $HIGH high severity security vulnerabilities"
          fi

          echo "✅ Security gate passed"

      - name: Generate security badge
        run: |
          # Create badge for README
          if [ "${{ steps.gate.outputs.critical }}" -gt 0 ]; then
            BADGE="![Security](https://img.shields.io/badge/security-at%20risk-red)"
          elif [ "${{ steps.gate.outputs.high }}" -gt 0 ]; then
            BADGE="![Security](https://img.shields.io/badge/security-needs%20attention-yellow)"
          else
            BADGE="![Security](https://img.shields.io/badge/security-passing-green)"
          fi
          echo "$BADGE" > docs/security/badge.txt

      - name: Upload security artifacts
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: |
            docs/security/
            security-results.sarif
          retention-days: 90
        if: always()

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');

            // Read audit report
            let report = '';
            try {
              report = fs.readFileSync('docs/security/audit-report.md', 'utf8');
            } catch (err) {
              console.error('Could not read audit report:', err);
              return;
            }

            // Truncate if too long (GitHub comment limit)
            const maxLength = 60000;
            if (report.length > maxLength) {
              report = report.substring(0, maxLength) + '\n\n... (truncated)';
            }

            // Create or update comment
            const { data: comments } = await github.rest.issues.listComments({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
            });

            const botComment = comments.find(comment =>
              comment.user.login === 'github-actions[bot]' &&
              comment.body.includes('## Security Scan Results')
            );

            const commentBody = `## Security Scan Results

            **Findings Summary:**
            - Critical: ${{ steps.gate.outputs.critical }}
            - High: ${{ steps.gate.outputs.high }}
            - Medium: ${{ steps.gate.outputs.medium }}

            <details>
            <summary>View Full Report</summary>

            ${report}

            </details>

            ---
            *Generated by [JP Spec Kit](https://github.com/jpoley/jp-spec-kit) Security Scanner*
            `;

            if (botComment) {
              await github.rest.issues.updateComment({
                comment_id: botComment.id,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: commentBody,
              });
            } else {
              await github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: commentBody,
              });
            }

      - name: Update security dashboard
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: |
          # Generate historical trend data
          specify security metrics \
            --output docs/security/metrics.json \
            --history 30d

      - name: Notify security team
        if: steps.gate.outputs.critical > 0
        uses: actions/github-script@v7
        with:
          script: |
            // Create GitHub issue for critical findings
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 Critical Security Vulnerabilities Detected',
              body: `Critical security vulnerabilities were detected in commit ${context.sha}.

              **Critical Findings:** ${{ steps.gate.outputs.critical }}
              **High Findings:** ${{ steps.gate.outputs.high }}

              Please review the security report: https://github.com/${context.repo.owner}/${context.repo.repo}/security/code-scanning

              **Action Required:** Address critical findings immediately.`,
              labels: ['security', 'critical', 'needs-triage'],
              assignees: ['security-team'],  // Replace with your team
            });
```

### Assignee Mapping Configuration

Create `.github/security-assignees.yml`:

```yaml
# Map vulnerability types to GitHub users/teams

backend:
  assignee: "@backend-team"
  users:
    - backend-engineer-1
    - backend-engineer-2

frontend:
  assignee: "@frontend-team"
  users:
    - frontend-engineer-1
    - frontend-engineer-2

infrastructure:
  assignee: "@platform-team"
  users:
    - platform-engineer-1
    - devops-engineer-1

security:
  assignee: "@security-team"
  users:
    - security-engineer-1

# Vulnerability type routing
vulnerability_types:
  sql-injection: "@backend-team"
  xss: "@frontend-team"
  auth-bypass: "@backend-team"
  crypto-failure: "@security-team"
  dependency: "@platform-team"
```

## GitLab CI

### Complete Security Pipeline

Create `.gitlab-ci.yml` or add to existing file:

```yaml
stages:
  - security
  - report
  - notify

variables:
  SECURITY_SCAN_IMAGE: "python:3.11"
  SARIF_OUTPUT: "gl-sast-report.json"

# Cache security scan results
cache:
  key: "${CI_COMMIT_REF_SLUG}-security"
  paths:
    - .security-cache/
    - docs/security/

security:scan:
  stage: security
  image: $SECURITY_SCAN_IMAGE
  timeout: 30 minutes

  before_script:
    - pip install uv
    - uv sync
    - uv tool install .

  script:
    # Run security scan
    - specify security scan
        --format sarif
        --output $SARIF_OUTPUT
        --cache .security-cache

    # Triage findings
    - specify security triage
        --input $SARIF_OUTPUT
        --output docs/security/triage-results.json
        --false-positive-detection

    # Generate report
    - specify security report
        --input docs/security/triage-results.json
        --output docs/security/audit-report.md

  artifacts:
    reports:
      sast: $SARIF_OUTPUT
    paths:
      - docs/security/
      - $SARIF_OUTPUT
    expire_in: 30 days
    when: always

  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - if: '$CI_PIPELINE_SOURCE == "schedule"'

security:gate:
  stage: security
  image: $SECURITY_SCAN_IMAGE
  needs: ["security:scan"]

  script:
    # Check findings
    - |
      CRITICAL=$(jq '[.findings[] | select(.severity == "critical")] | length' docs/security/triage-results.json)
      HIGH=$(jq '[.findings[] | select(.severity == "high")] | length' docs/security/triage-results.json)

      echo "Critical findings: $CRITICAL"
      echo "High findings: $HIGH"

      # Block on critical
      if [ "$CRITICAL" -gt 0 ]; then
        echo "❌ Found $CRITICAL critical vulnerabilities - blocking pipeline"
        exit 1
      fi

      # Warn on high
      if [ "$HIGH" -gt 0 ]; then
        echo "⚠️ Found $HIGH high severity vulnerabilities"
      fi

      echo "✅ Security gate passed"

  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'

security:tasks:
  stage: report
  image: $SECURITY_SCAN_IMAGE
  needs: ["security:scan"]

  before_script:
    - pip install uv
    - uv tool install .

  script:
    # Create backlog tasks for critical/high findings
    - specify security report
        --create-tasks
        --severity critical,high

  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

security:notify:
  stage: notify
  image: curlimages/curl:latest
  needs: ["security:gate"]

  script:
    # Notify Slack on critical findings
    - |
      CRITICAL=$(jq '[.findings[] | select(.severity == "critical")] | length' docs/security/triage-results.json)
      if [ "$CRITICAL" -gt 0 ]; then
        curl -X POST "$SLACK_WEBHOOK_URL" \
          -H 'Content-Type: application/json' \
          -d "{
            \"text\": \"🚨 Critical security vulnerabilities detected in $CI_PROJECT_NAME\",
            \"blocks\": [
              {
                \"type\": \"section\",
                \"text\": {
                  \"type\": \"mrkdwn\",
                  \"text\": \"*Critical Findings:* $CRITICAL\\n*Pipeline:* $CI_PIPELINE_URL\"
                }
              }
            ]
          }"
      fi

  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
      when: always
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
      when: always

security:metrics:
  stage: report
  image: $SECURITY_SCAN_IMAGE
  needs: ["security:scan"]

  before_script:
    - pip install uv
    - uv tool install .

  script:
    # Generate security metrics
    - specify security metrics
        --output docs/security/metrics.json
        --history 30d

    # Create trend visualization
    - specify security visualize
        --input docs/security/metrics.json
        --output docs/security/trends.html

  artifacts:
    paths:
      - docs/security/metrics.json
      - docs/security/trends.html
    expire_in: 90 days

  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
```

### GitLab Security Dashboard Integration

GitLab automatically displays SARIF results in the Security Dashboard when using the `sast` report type.

## Jenkins

### Declarative Pipeline

Create `Jenkinsfile`:

```groovy
pipeline {
    agent {
        docker {
            image 'python:3.11'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }

    triggers {
        // Run daily at 2 AM
        cron('0 2 * * *')
    }

    stages {
        stage('Setup') {
            steps {
                sh '''
                    pip install uv
                    uv sync
                    uv tool install .
                '''
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    specify security scan \
                        --format sarif \
                        --output security-results.sarif \
                        --cache .security-cache
                '''
            }
        }

        stage('Triage Findings') {
            steps {
                sh '''
                    specify security triage \
                        --input security-results.sarif \
                        --output docs/security/triage-results.json \
                        --false-positive-detection
                '''
            }
        }

        stage('Generate Report') {
            steps {
                sh '''
                    specify security report \
                        --input docs/security/triage-results.json \
                        --output docs/security/audit-report.md \
                        --format markdown,html
                '''
            }
        }

        stage('Create Tasks') {
            when {
                changeRequest()
            }
            steps {
                sh '''
                    specify security report \
                        --create-tasks \
                        --severity critical,high
                '''
            }
        }

        stage('Security Gate') {
            steps {
                script {
                    def criticalCount = sh(
                        script: '''
                            jq '[.findings[] | select(.severity == "critical")] | length' \
                                docs/security/triage-results.json
                        ''',
                        returnStdout: true
                    ).trim()

                    def highCount = sh(
                        script: '''
                            jq '[.findings[] | select(.severity == "high")] | length' \
                                docs/security/triage-results.json
                        ''',
                        returnStdout: true
                    ).trim()

                    echo "Critical findings: ${criticalCount}"
                    echo "High findings: ${highCount}"

                    if (criticalCount.toInteger() > 0) {
                        error("Found ${criticalCount} critical vulnerabilities")
                    }

                    if (highCount.toInteger() > 5) {
                        unstable("Found ${highCount} high severity vulnerabilities")
                    }
                }
            }
        }
    }

    post {
        always {
            // Publish HTML reports
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'docs/security',
                reportFiles: 'audit-report.html',
                reportName: 'Security Report'
            ])

            // Archive artifacts
            archiveArtifacts artifacts: 'docs/security/**/*', fingerprint: true
        }

        failure {
            // Send email notification
            emailext(
                subject: "Security Scan Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: """
                    Security scan failed for ${env.JOB_NAME}.

                    Build URL: ${env.BUILD_URL}
                    Security Report: ${env.BUILD_URL}Security_Report/

                    Please review the security findings immediately.
                """,
                to: 'security-team@example.com',
                attachLog: true
            )
        }

        success {
            // Update security dashboard
            sh '''
                specify security metrics \
                    --output docs/security/metrics.json \
                    --history 30d
            '''
        }
    }
}
```

## CircleCI

### Complete Configuration

Create `.circleci/config.yml`:

```yaml
version: 2.1

orbs:
  python: circleci/python@2.1.1

executors:
  python-executor:
    docker:
      - image: cimg/python:3.11
    resource_class: medium
    working_directory: ~/project

commands:
  install-jpspec:
    steps:
      - run:
          name: Install JP Spec Kit
          command: |
            pip install uv
            uv sync
            uv tool install .

  run-security-scan:
    steps:
      - run:
          name: Run Security Scan
          command: |
            specify security scan \
              --format sarif \
              --output security-results.sarif \
              --cache .security-cache

  triage-findings:
    steps:
      - run:
          name: Triage Findings
          command: |
            specify security triage \
              --input security-results.sarif \
              --output docs/security/triage-results.json \
              --false-positive-detection

  generate-report:
    steps:
      - run:
          name: Generate Security Report
          command: |
            specify security report \
              --input docs/security/triage-results.json \
              --output docs/security/audit-report.md

  security-gate:
    steps:
      - run:
          name: Security Gate Check
          command: |
            CRITICAL=$(jq '[.findings[] | select(.severity == "critical")] | length' \
              docs/security/triage-results.json)

            if [ "$CRITICAL" -gt 0 ]; then
              echo "❌ Found $CRITICAL critical vulnerabilities"
              exit 1
            fi

            echo "✅ Security gate passed"

jobs:
  security-scan:
    executor: python-executor
    steps:
      - checkout
      - install-jpspec
      - restore_cache:
          keys:
            - security-cache-{{ .Branch }}-{{ checksum "pyproject.toml" }}
            - security-cache-{{ .Branch }}-
            - security-cache-
      - run-security-scan
      - triage-findings
      - generate-report
      - save_cache:
          key: security-cache-{{ .Branch }}-{{ checksum "pyproject.toml" }}
          paths:
            - .security-cache
            - docs/security
      - store_artifacts:
          path: docs/security
          destination: security-reports
      - store_test_results:
          path: security-results.sarif
      - persist_to_workspace:
          root: .
          paths:
            - docs/security

  security-gate:
    executor: python-executor
    steps:
      - checkout
      - attach_workspace:
          at: .
      - security-gate

  create-tasks:
    executor: python-executor
    steps:
      - checkout
      - attach_workspace:
          at: .
      - install-jpspec
      - run:
          name: Create Backlog Tasks
          command: |
            specify security report \
              --create-tasks \
              --severity critical,high

workflows:
  security-workflow:
    jobs:
      - security-scan:
          filters:
            branches:
              only:
                - main
                - develop
      - security-gate:
          requires:
            - security-scan
      - create-tasks:
          requires:
            - security-scan
          filters:
            branches:
              only:
                - develop

  nightly-security-scan:
    triggers:
      - schedule:
          cron: "0 2 * * *"  # 2 AM daily
          filters:
            branches:
              only:
                - main
    jobs:
      - security-scan
      - security-gate:
          requires:
            - security-scan
```

## Pre-Commit Hooks

### Git Pre-Commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Security scan pre-commit hook
# Run security scans on staged files before commit

set -e

echo "🔒 Running security pre-commit checks..."

# Check if jp-spec-kit is installed
if ! command -v specify &> /dev/null; then
    echo "⚠️  jp-spec-kit not found, skipping security scan"
    exit 0
fi

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    echo "No staged files to scan"
    exit 0
fi

# Run security scan on staged files only
echo "Scanning ${STAGED_FILES[@]}"

specify security scan \
    --staged-only \
    --output .git/pre-commit-scan.json \
    --no-cache

# Check for critical findings
CRITICAL_COUNT=$(jq '[.findings[] | select(.severity == "critical")] | length' \
    .git/pre-commit-scan.json 2>/dev/null || echo "0")

if [ "$CRITICAL_COUNT" -gt 0 ]; then
    echo "❌ Found $CRITICAL_COUNT critical security issues in staged files"
    echo ""
    echo "Critical findings:"
    jq -r '.findings[] | select(.severity == "critical") |
        "  - \(.title) (\(.location.file):\(.location.line))"' \
        .git/pre-commit-scan.json
    echo ""
    echo "Run 'specify security triage' to review findings"
    echo "To bypass this check (not recommended): git commit --no-verify"
    exit 1
fi

# Check for high findings (warn only)
HIGH_COUNT=$(jq '[.findings[] | select(.severity == "high")] | length' \
    .git/pre-commit-scan.json 2>/dev/null || echo "0")

if [ "$HIGH_COUNT" -gt 0 ]; then
    echo "⚠️  Found $HIGH_COUNT high security issues in staged files"
    echo "Consider fixing before committing"
fi

echo "✅ Pre-commit security checks passed"
exit 0
```

Make executable:

```bash
chmod +x .git/hooks/pre-commit
```

### Pre-Push Hook

Create `.git/hooks/pre-push`:

```bash
#!/bin/bash
# Security scan pre-push hook
# Run full security scan before push

set -e

echo "🔒 Running security pre-push checks..."

# Check if jp-spec-kit is installed
if ! command -v specify &> /dev/null; then
    echo "⚠️  jp-spec-kit not found, skipping security scan"
    exit 0
fi

# Run full security scan
specify security scan \
    --format json \
    --output .git/pre-push-scan.json

# Check for critical and high findings
CRITICAL_COUNT=$(jq '[.findings[] | select(.severity == "critical")] | length' \
    .git/pre-push-scan.json)
HIGH_COUNT=$(jq '[.findings[] | select(.severity == "high")] | length' \
    .git/pre-push-scan.json)

if [ "$CRITICAL_COUNT" -gt 0 ]; then
    echo "❌ Found $CRITICAL_COUNT critical security vulnerabilities"
    echo "Cannot push code with critical vulnerabilities"
    exit 1
fi

if [ "$HIGH_COUNT" -gt 3 ]; then
    echo "⚠️  Found $HIGH_COUNT high severity vulnerabilities"
    echo "Consider addressing high severity issues before pushing"
    read -p "Continue with push? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ Pre-push security checks passed"
exit 0
```

Make executable:

```bash
chmod +x .git/hooks/pre-push
```

## SARIF Upload Configuration

### GitHub Code Scanning

Ensure your GitHub Actions workflow has:

```yaml
permissions:
  security-events: write  # Required for SARIF upload

steps:
  - name: Upload SARIF to GitHub Security
    uses: github/codeql-action/upload-sarif@v3
    with:
      sarif_file: security-results.sarif
      category: jp-spec-kit-security
      wait-for-processing: true
    if: always()  # Upload even if scan fails
```

### GitLab SAST

GitLab automatically processes SARIF files in the `sast` artifact report:

```yaml
artifacts:
  reports:
    sast: gl-sast-report.json
```

### Azure DevOps

```yaml
- task: PublishSecurityAnalysisLogs@3
  inputs:
    artifactName: 'CodeAnalysisLogs'
    allTools: false
    toolLogsNotFoundAction: 'Standard'
```

## Environment Variables

### Required Variables

Set these in your CI/CD environment:

```bash
# GitHub
GITHUB_TOKEN           # For SARIF upload and API access

# GitLab
CI_JOB_TOKEN          # Automatically provided

# Slack notifications (optional)
SLACK_WEBHOOK_URL     # For security alerts

# Email notifications (optional)
SECURITY_EMAIL        # Email for critical findings
```

### Optional Variables

```bash
# Scan configuration
SECURITY_SCAN_TIMEOUT=1800        # Scan timeout in seconds
SECURITY_CACHE_DIR=.security-cache # Cache directory
SECURITY_SEVERITY_FILTER=critical,high  # Severity filter

# Task creation
CREATE_TASKS=true                 # Auto-create backlog tasks
TASK_SEVERITY=critical,high       # Task creation severity threshold
```

## Best Practices

1. **Run on Every PR** - Catch issues before merge
2. **Block Critical** - Never allow critical vulnerabilities to merge
3. **Warn on High** - Surface but don't necessarily block
4. **Cache Results** - Speed up scans with caching
5. **Upload SARIF** - Integrate with platform security features
6. **Create Tasks** - Automate remediation tracking
7. **Notify Teams** - Alert on critical findings
8. **Track Metrics** - Monitor security posture trends
9. **Regular Scans** - Run scheduled scans on main branch
10. **Clear Feedback** - Provide actionable information in failures

## See Also

- [Security Workflow Integration Guide](../guides/security-workflow-integration.md)
- [SARIF Output Guide](../../templates/docs/security/sarif-output-guide.md)
- [Security Commands Reference](../reference/security-commands.md)
