# CI/CD Security Integration Guide

Complete examples for integrating security scanning into your CI/CD pipelines.

## Overview

This guide shows how to integrate security scanners directly in CI/CD pipelines. For interactive security workflows in Claude Code sessions, use the `/jpspec:security` slash commands (see [Security Quickstart](./security-quickstart.md)).

**CI/CD Integration Strategy:**

1. **Pre-commit** - Fast scans before code is committed (local hooks)
2. **Pull Request** - Full scan with SARIF upload for code review
3. **Main Branch** - Comprehensive audit with reporting
4. **Scheduled** - Regular scans for new vulnerabilities

**Note**: `/jpspec:security` commands are designed for Claude Code sessions, not CI/CD automation. This guide uses scanner CLIs directly (Semgrep, Bandit, etc.) for pipeline integration.

## GitHub Actions

### Basic Security Scan

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6 AM

permissions:
  contents: read
  security-events: write

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install scanners
        run: |
          pip install semgrep bandit

      - name: Run security scan
        run: |
          semgrep --config=auto --sarif --output=results.sarif .
        continue-on-error: true

      - name: Upload SARIF to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif

      - name: Check for critical findings
        run: |
          specify security scan --fail-on critical
```

### Full Security Pipeline

```yaml
# .github/workflows/security-full.yml
name: Full Security Pipeline

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  security-events: write
  pull-requests: write

jobs:
  scan:
    name: Security Scan
    runs-on: ubuntu-latest
    outputs:
      findings-count: ${{ steps.scan.outputs.findings }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install tools
        run: pip install specify-cli semgrep

      - name: Run scan
        id: scan
        run: |
          specify security scan --format json --output scan-results.json
          FINDINGS=$(jq '.findings | length' scan-results.json)
          echo "findings=$FINDINGS" >> $GITHUB_OUTPUT

      - name: Upload scan results
        uses: actions/upload-artifact@v4
        with:
          name: scan-results
          path: scan-results.json

  triage:
    name: AI Triage
    runs-on: ubuntu-latest
    needs: scan
    if: needs.scan.outputs.findings-count > 0
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install tools
        run: pip install specify-cli

      - name: Download scan results
        uses: actions/download-artifact@v4
        with:
          name: scan-results

      - name: Run AI triage
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          specify security triage scan-results.json \
            --format json \
            --output triage-results.json

      - name: Upload triage results
        uses: actions/upload-artifact@v4
        with:
          name: triage-results
          path: triage-results.json

  report:
    name: Generate Report
    runs-on: ubuntu-latest
    needs: [scan, triage]
    if: always()
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install tools
        run: pip install specify-cli

      - name: Download artifacts
        uses: actions/download-artifact@v4

      - name: Generate audit report
        run: |
          specify security audit scan-results/scan-results.json \
            --format markdown \
            --output security-report.md \
            --owasp

      - name: Generate SARIF
        run: |
          specify security audit scan-results/scan-results.json \
            --format sarif \
            --output results.sarif

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif

      - name: Comment on PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('security-report.md', 'utf8');
            const summary = report.split('\n').slice(0, 50).join('\n');

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Security Scan Results\n\n${summary}\n\n<details><summary>Full Report</summary>\n\n${report}\n\n</details>`
            });
```

### Incremental Scan (PR Only)

```yaml
# .github/workflows/security-incremental.yml
name: Incremental Security Scan

on:
  pull_request:

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Get changed files
        id: changed
        run: |
          echo "files=$(git diff --name-only origin/${{ github.base_ref }}...HEAD | tr '\n' ' ')" >> $GITHUB_OUTPUT

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install tools
        run: pip install specify-cli semgrep

      - name: Scan changed files
        if: steps.changed.outputs.files != ''
        run: |
          specify security scan ${{ steps.changed.outputs.files }} \
            --fail-on high
```

## GitLab CI

### Basic Configuration

```yaml
# .gitlab-ci.yml
stages:
  - test
  - security
  - report

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.pip-cache"

.security-base:
  image: python:3.11
  before_script:
    - pip install specify-cli semgrep
  cache:
    paths:
      - .pip-cache/

security-scan:
  extends: .security-base
  stage: security
  script:
    - specify security scan --format json --output gl-sast-report.json
  artifacts:
    reports:
      sast: gl-sast-report.json
    paths:
      - gl-sast-report.json
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

security-triage:
  extends: .security-base
  stage: security
  needs: [security-scan]
  script:
    - specify security triage gl-sast-report.json --format json --output triage-report.json
  artifacts:
    paths:
      - triage-report.json
    expire_in: 1 week
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  when: manual

security-report:
  extends: .security-base
  stage: report
  needs: [security-scan]
  script:
    - specify security audit gl-sast-report.json --format markdown --output security-report.md
    - specify security audit gl-sast-report.json --format html --output security-report.html
  artifacts:
    paths:
      - security-report.md
      - security-report.html
    expire_in: 1 month
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

security-gate:
  extends: .security-base
  stage: security
  needs: [security-scan]
  script:
    - specify security scan --fail-on critical
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
```

### GitLab Security Dashboard Integration

```yaml
# .gitlab-ci.yml
include:
  - template: Security/SAST.gitlab-ci.yml

sast:
  variables:
    SAST_EXCLUDED_ANALYZERS: ""

jpspec-security:
  stage: test
  image: python:3.11
  script:
    - pip install specify-cli semgrep
    - specify security scan --format json --output gl-sast-report.json
  artifacts:
    reports:
      sast: gl-sast-report.json
```

## Jenkins

### Jenkinsfile

```groovy
// Jenkinsfile
pipeline {
    agent {
        docker {
            image 'python:3.11'
        }
    }

    environment {
        ANTHROPIC_API_KEY = credentials('anthropic-api-key')
    }

    stages {
        stage('Setup') {
            steps {
                sh 'pip install specify-cli semgrep'
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                    specify security scan \
                        --format json \
                        --output scan-results.json
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'scan-results.json'
                }
            }
        }

        stage('AI Triage') {
            when {
                expression {
                    def results = readJSON file: 'scan-results.json'
                    return results.findings.size() > 0
                }
            }
            steps {
                sh '''
                    specify security triage scan-results.json \
                        --format json \
                        --output triage-results.json
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'triage-results.json'
                }
            }
        }

        stage('Generate Report') {
            steps {
                sh '''
                    specify security audit scan-results.json \
                        --format html \
                        --output security-report.html \
                        --owasp
                '''
            }
            post {
                always {
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'security-report.html',
                        reportName: 'Security Report'
                    ])
                }
            }
        }

        stage('Security Gate') {
            steps {
                sh 'specify security scan --fail-on high'
            }
        }
    }

    post {
        failure {
            emailext(
                subject: "Security Scan Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Security vulnerabilities found. See: ${env.BUILD_URL}",
                recipientProviders: [developers()]
            )
        }
    }
}
```

### Jenkins Declarative with Matrix

```groovy
// Jenkinsfile with matrix builds
pipeline {
    agent none

    stages {
        stage('Security Matrix') {
            matrix {
                axes {
                    axis {
                        name 'SCANNER'
                        values 'semgrep', 'bandit'
                    }
                }
                agent {
                    docker { image 'python:3.11' }
                }
                stages {
                    stage('Scan') {
                        steps {
                            sh """
                                pip install specify-cli ${SCANNER}
                                specify security scan \
                                    --scanner ${SCANNER} \
                                    --format json \
                                    --output ${SCANNER}-results.json
                            """
                        }
                        post {
                            always {
                                archiveArtifacts artifacts: "${SCANNER}-results.json"
                            }
                        }
                    }
                }
            }
        }
    }
}
```

## Azure DevOps

### Azure Pipelines

```yaml
# azure-pipelines.yml
trigger:
  - main
  - develop

pr:
  - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.11'

stages:
  - stage: Security
    displayName: 'Security Scanning'
    jobs:
      - job: Scan
        displayName: 'Security Scan'
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(pythonVersion)'

          - script: |
              pip install specify-cli semgrep
            displayName: 'Install tools'

          - script: |
              specify security scan \
                --format json \
                --output $(Build.ArtifactStagingDirectory)/scan-results.json
            displayName: 'Run security scan'

          - task: PublishBuildArtifacts@1
            inputs:
              pathToPublish: '$(Build.ArtifactStagingDirectory)/scan-results.json'
              artifactName: 'SecurityResults'

          - script: |
              specify security scan --fail-on high
            displayName: 'Security gate'
            continueOnError: true

      - job: Report
        displayName: 'Generate Report'
        dependsOn: Scan
        steps:
          - task: DownloadBuildArtifacts@0
            inputs:
              artifactName: 'SecurityResults'

          - script: |
              pip install specify-cli
              specify security audit \
                $(System.ArtifactsDirectory)/SecurityResults/scan-results.json \
                --format html \
                --output $(Build.ArtifactStagingDirectory)/security-report.html
            displayName: 'Generate HTML report'

          - task: PublishBuildArtifacts@1
            inputs:
              pathToPublish: '$(Build.ArtifactStagingDirectory)/security-report.html'
              artifactName: 'SecurityReport'
```

## CircleCI

### CircleCI Configuration

```yaml
# .circleci/config.yml
version: 2.1

orbs:
  python: circleci/python@2.1

executors:
  security-executor:
    docker:
      - image: cimg/python:3.11

jobs:
  security-scan:
    executor: security-executor
    steps:
      - checkout
      - python/install-packages:
          pkg-manager: pip
          packages: specify-cli semgrep
      - run:
          name: Run security scan
          command: |
            specify security scan \
              --format json \
              --output scan-results.json
      - store_artifacts:
          path: scan-results.json
      - persist_to_workspace:
          root: .
          paths:
            - scan-results.json

  security-triage:
    executor: security-executor
    steps:
      - checkout
      - attach_workspace:
          at: .
      - python/install-packages:
          pkg-manager: pip
          packages: specify-cli
      - run:
          name: AI triage
          command: |
            specify security triage scan-results.json \
              --format json \
              --output triage-results.json
      - store_artifacts:
          path: triage-results.json

  security-report:
    executor: security-executor
    steps:
      - checkout
      - attach_workspace:
          at: .
      - python/install-packages:
          pkg-manager: pip
          packages: specify-cli
      - run:
          name: Generate report
          command: |
            specify security audit scan-results.json \
              --format html \
              --output security-report.html
      - store_artifacts:
          path: security-report.html

  security-gate:
    executor: security-executor
    steps:
      - checkout
      - python/install-packages:
          pkg-manager: pip
          packages: specify-cli semgrep
      - run:
          name: Security gate
          command: specify security scan --fail-on critical

workflows:
  security:
    jobs:
      - security-scan
      - security-triage:
          requires:
            - security-scan
      - security-report:
          requires:
            - security-scan
      - security-gate:
          requires:
            - security-scan
```

## Pre-commit Integration

### Basic Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: jpspec-security
        name: Security Scan
        entry: specify security scan --quick --fail-on critical
        language: python
        additional_dependencies: [specify-cli, semgrep]
        pass_filenames: false
        stages: [commit]
```

### Advanced Pre-commit with Multiple Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: jpspec-security-python
        name: Security Scan (Python)
        entry: specify security scan --scanner semgrep --quick --fail-on high
        language: python
        additional_dependencies: [specify-cli, semgrep]
        types: [python]
        pass_filenames: false

      - id: jpspec-security-bandit
        name: Bandit Security Check
        entry: bandit -r
        language: python
        additional_dependencies: [bandit]
        types: [python]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: detect-private-key
      - id: detect-aws-credentials
```

## Best Practices

### 1. Fail Fast, Report Always

```yaml
# Always upload results, even on failure
- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v3
  if: always()
  with:
    sarif_file: results.sarif
```

### 2. Cache Scanner Tools

```yaml
- name: Cache scanner tools
  uses: actions/cache@v4
  with:
    path: ~/.local/share/specify/tools
    key: security-tools-${{ runner.os }}
```

### 3. Use Secrets Properly

```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  SEMGREP_APP_TOKEN: ${{ secrets.SEMGREP_APP_TOKEN }}
```

### 4. Incremental Scans for PRs

```yaml
- name: Scan changed files only
  run: |
    git diff --name-only ${{ github.event.before }} ${{ github.sha }} | \
    xargs specify security scan
```

### 5. Scheduled Full Scans

```yaml
on:
  schedule:
    - cron: '0 6 * * 1'  # Weekly
```

## Troubleshooting

### Scanner Not Found in CI

```yaml
- name: Install scanner
  run: |
    pip install semgrep
    which semgrep  # Verify installation
```

### Permission Denied for SARIF Upload

Ensure workflow has correct permissions:

```yaml
permissions:
  security-events: write
```

### Timeouts on Large Codebases

```yaml
- name: Run scan with timeout
  timeout-minutes: 30
  run: specify security scan --timeout 1800
```

## Related Documentation

- [Security Quickstart](./security-quickstart.md)
- [Command Reference](../reference/jpspec-security-commands.md)
- [Custom Rules](./security-custom-rules.md)
