# Hook CI/CD Integration

## Overview

This document defines how Flowspec hooks integrate with continuous integration and continuous deployment (CI/CD) pipelines, enabling automated testing, deployment triggers, and workflow orchestration across development, staging, and production environments.

## Design Principles

1. **Pipeline-Agnostic**: Support GitHub Actions, GitLab CI, Jenkins, CircleCI, etc.
2. **Event-Driven**: CI/CD triggered by workflow events, not manual intervention
3. **Fail-Safe**: CI/CD failures don't break local development workflows
4. **Auditable**: All CI/CD triggers logged for compliance and debugging
5. **Idempotent**: Repeated event emissions don't cause duplicate deployments

## Integration Patterns

### Pattern 1: Local Hook → Remote CI Trigger

**Use Case**: After local implementation completes, trigger remote CI pipeline for integration tests.

```yaml
# .flowspec/hooks/hooks.yaml
hooks:
  - name: "trigger-ci-tests"
    description: "Trigger GitHub Actions integration tests after implementation"
    events:
      - type: "implement.completed"
    script: ".flowspec/hooks/trigger-ci.sh"
    timeout: 30
    env:
      GITHUB_TOKEN: "${GITHUB_FLOWSPEC}"
      WORKFLOW_FILE: "integration-tests.yml"
```

**Hook Script** (`.flowspec/hooks/trigger-ci.sh`):
```bash
#!/bin/bash
set -e

# Read event payload from stdin
EVENT=$(cat)
FEATURE=$(echo "$EVENT" | jq -r '.feature')
BRANCH=$(git branch --show-current)

# Trigger GitHub Actions workflow
gh workflow run "$WORKFLOW_FILE" \
  --ref "$BRANCH" \
  --field feature="$FEATURE" \
  --field trigger="flowspec-hook"

echo "✓ Triggered CI workflow: $WORKFLOW_FILE for feature $FEATURE"
```

**GitHub Actions Workflow** (`.github/workflows/integration-tests.yml`):
```yaml
name: Integration Tests

on:
  workflow_dispatch:
    inputs:
      feature:
        description: 'Feature name from flowspec'
        required: true
      trigger:
        description: 'Trigger source'
        required: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run integration tests
        run: |
          echo "Running integration tests for feature: ${{ inputs.feature }}"
          pytest tests/integration/ -v

      - name: Report status back to flowspec
        if: always()
        run: |
          # Post status to webhook or commit status
          echo "Tests completed with status: ${{ job.status }}"
```

### Pattern 2: CI/CD → Hook Execution

**Use Case**: CI pipeline emits events that trigger local hooks (e.g., deployment notification).

```yaml
# .github/workflows/deploy.yml
name: Deploy to Staging

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to staging
        run: ./scripts/deploy-staging.sh

      - name: Emit deployment event
        run: |
          # Emit event via webhook to developer machines
          curl -X POST https://webhook.example.com/events \
            -H "Content-Type: application/json" \
            -d '{
              "event_type": "deploy.completed",
              "environment": "staging",
              "commit": "${{ github.sha }}",
              "feature": "auto-extracted"
            }'
```

**Local Hook** (`.flowspec/hooks/hooks.yaml`):
```yaml
hooks:
  - name: "deployment-notification"
    description: "Notify when staging deployment completes"
    events:
      - type: "deploy.completed"
        filter:
          environment: "staging"
    command: |
      notify-send "Deployment Complete" "Staging environment updated"
```

### Pattern 3: Quality Gate Enforcement

**Use Case**: Block PR creation unless all quality gates pass (tests, coverage, linting).

```yaml
# .flowspec/hooks/hooks.yaml
hooks:
  - name: "quality-gate"
    description: "Enforce quality gates before PR creation"
    events:
      - type: "validate.completed"
    script: ".flowspec/hooks/quality-gate.sh"
    timeout: 600  # 10 minutes for full quality suite
    fail_mode: "stop"  # Block workflow if quality gate fails
```

**Hook Script** (`.flowspec/hooks/quality-gate.sh`):
```bash
#!/bin/bash
set -e

echo "Running quality gate checks..."

# 1. Run test suite
echo "→ Running tests..."
pytest tests/ -v --cov=src --cov-report=term-missing --cov-fail-under=85

# 2. Run linter
echo "→ Running linter..."
ruff check . --fix

# 3. Check acceptance criterion coverage
echo "→ Checking AC coverage..."
backlog task view "$TASK_ID" --plain | grep -q "- \[x\]" || {
  echo "❌ Incomplete acceptance criteria"
  exit 1
}

# 4. Trigger CI pipeline for integration tests
echo "→ Triggering CI integration tests..."
gh workflow run integration-tests.yml --ref "$(git branch --show-current)"

echo "✅ All quality gates passed"
```

### Pattern 4: Deployment Pipeline Trigger

**Use Case**: After validation completes, automatically trigger deployment to staging.

```yaml
# .flowspec/hooks/hooks.yaml
hooks:
  - name: "trigger-deployment"
    description: "Trigger deployment pipeline after validation"
    events:
      - type: "validate.completed"
    script: ".flowspec/hooks/trigger-deploy.sh"
    timeout: 30
    env:
      DEPLOY_WEBHOOK_URL: "${DEPLOY_WEBHOOK_URL}"
      ENVIRONMENT: "staging"
```

**Hook Script** (`.flowspec/hooks/trigger-deploy.sh`):
```bash
#!/bin/bash
set -e

# Read event payload
EVENT=$(cat)
FEATURE=$(echo "$EVENT" | jq -r '.feature')
COMMIT=$(git rev-parse HEAD)
BRANCH=$(git branch --show-current)

# Trigger deployment via webhook
curl -X POST "$DEPLOY_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DEPLOY_TOKEN" \
  -d "{
    \"feature\": \"$FEATURE\",
    \"commit\": \"$COMMIT\",
    \"branch\": \"$BRANCH\",
    \"environment\": \"$ENVIRONMENT\",
    \"triggered_by\": \"flowspec-validate\"
  }"

echo "✓ Triggered deployment for feature $FEATURE to $ENVIRONMENT"
```

**Jenkins Pipeline** (receiving webhook):
```groovy
pipeline {
    agent any

    parameters {
        string(name: 'feature', description: 'Feature name')
        string(name: 'commit', description: 'Git commit SHA')
        string(name: 'environment', description: 'Target environment')
    }

    stages {
        stage('Deploy') {
            steps {
                script {
                    echo "Deploying feature ${params.feature} to ${params.environment}"
                    sh "./scripts/deploy.sh ${params.environment} ${params.commit}"
                }
            }
        }

        stage('Smoke Tests') {
            steps {
                sh "pytest tests/smoke/ --env ${params.environment}"
            }
        }

        stage('Notify') {
            steps {
                script {
                    // Post deployment status back to commit
                    sh """
                        curl -X POST https://api.github.com/repos/org/repo/statuses/${params.commit} \\
                          -H "Authorization: token \$GITHUB_TOKEN" \\
                          -d '{"state": "success", "description": "Deployed to ${params.environment}"}'
                    """
                }
            }
        }
    }
}
```

## CI/CD Platforms

### GitHub Actions

#### Triggering Workflows from Hooks

```bash
# .flowspec/hooks/trigger-github-workflow.sh
#!/bin/bash
set -e

EVENT=$(cat)
FEATURE=$(echo "$EVENT" | jq -r '.feature')

# Trigger workflow via GitHub CLI
gh workflow run integration-tests.yml \
  --ref "$(git branch --show-current)" \
  --field feature="$FEATURE" \
  --field event_type="$EVENT_TYPE"

# Alternative: Trigger via API
# curl -X POST \
#   -H "Authorization: token $GITHUB_TOKEN" \
#   -H "Accept: application/vnd.github.v3+json" \
#   https://api.github.com/repos/OWNER/REPO/actions/workflows/WORKFLOW_ID/dispatches \
#   -d "{\"ref\":\"main\",\"inputs\":{\"feature\":\"$FEATURE\"}}"
```

#### Receiving Events in GitHub Actions

```yaml
# .github/workflows/flowspec-integration.yml
name: Flowspec Integration

on:
  workflow_dispatch:
    inputs:
      feature:
        description: 'Feature name'
        required: true
      event_type:
        description: 'Event type (implement.completed, validate.completed, etc.)'
        required: true

jobs:
  handle-event:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Handle implement.completed
        if: inputs.event_type == 'implement.completed'
        run: |
          echo "Running integration tests for ${{ inputs.feature }}"
          pytest tests/integration/ -v

      - name: Handle validate.completed
        if: inputs.event_type == 'validate.completed'
        run: |
          echo "Triggering deployment for ${{ inputs.feature }}"
          ./scripts/deploy-staging.sh
```

### GitLab CI

#### Triggering Pipelines from Hooks

```bash
# .flowspec/hooks/trigger-gitlab-pipeline.sh
#!/bin/bash
set -e

EVENT=$(cat)
FEATURE=$(echo "$EVENT" | jq -r '.feature')

# Trigger GitLab pipeline via API
curl -X POST \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  "https://gitlab.com/api/v4/projects/$PROJECT_ID/trigger/pipeline" \
  -F "token=$PIPELINE_TRIGGER_TOKEN" \
  -F "ref=main" \
  -F "variables[FEATURE]=$FEATURE" \
  -F "variables[EVENT_TYPE]=$EVENT_TYPE"

echo "✓ Triggered GitLab pipeline for feature $FEATURE"
```

#### Receiving Events in GitLab CI

```yaml
# .gitlab-ci.yml
workflow:
  rules:
    - if: $EVENT_TYPE == "implement.completed"
    - if: $EVENT_TYPE == "validate.completed"

variables:
  FEATURE: ${FEATURE}

stages:
  - test
  - deploy

integration-tests:
  stage: test
  rules:
    - if: $EVENT_TYPE == "implement.completed"
  script:
    - echo "Running integration tests for $FEATURE"
    - pytest tests/integration/ -v

deploy-staging:
  stage: deploy
  rules:
    - if: $EVENT_TYPE == "validate.completed"
  script:
    - echo "Deploying $FEATURE to staging"
    - ./scripts/deploy-staging.sh
```

### Jenkins

#### Triggering Jobs from Hooks

```bash
# .flowspec/hooks/trigger-jenkins-job.sh
#!/bin/bash
set -e

EVENT=$(cat)
FEATURE=$(echo "$EVENT" | jq -r '.feature')

# Trigger Jenkins job via API
curl -X POST \
  -u "$JENKINS_USER:$JENKINS_API_TOKEN" \
  "$JENKINS_URL/job/$JOB_NAME/buildWithParameters" \
  --data-urlencode "FEATURE=$FEATURE" \
  --data-urlencode "EVENT_TYPE=$EVENT_TYPE" \
  --data-urlencode "COMMIT=$(git rev-parse HEAD)"

echo "✓ Triggered Jenkins job: $JOB_NAME for feature $FEATURE"
```

#### Receiving Events in Jenkins

```groovy
// Jenkinsfile
pipeline {
    agent any

    parameters {
        string(name: 'FEATURE', description: 'Feature name from flowspec')
        string(name: 'EVENT_TYPE', description: 'Event type')
        string(name: 'COMMIT', description: 'Git commit SHA')
    }

    stages {
        stage('Handle Event') {
            steps {
                script {
                    switch(params.EVENT_TYPE) {
                        case 'implement.completed':
                            sh 'pytest tests/integration/ -v'
                            break
                        case 'validate.completed':
                            sh './scripts/deploy-staging.sh'
                            break
                        default:
                            echo "Unknown event type: ${params.EVENT_TYPE}"
                    }
                }
            }
        }
    }

    post {
        always {
            // Report status back to commit
            script {
                def status = currentBuild.result ?: 'SUCCESS'
                sh """
                    curl -X POST https://api.github.com/repos/org/repo/statuses/${params.COMMIT} \\
                      -H "Authorization: token \$GITHUB_TOKEN" \\
                      -d '{"state": "${status.toLowerCase()}", "description": "Jenkins: ${params.EVENT_TYPE}"}'
                """
            }
        }
    }
}
```

### CircleCI

#### Triggering Pipelines from Hooks

```bash
# .flowspec/hooks/trigger-circleci-pipeline.sh
#!/bin/bash
set -e

EVENT=$(cat)
FEATURE=$(echo "$EVENT" | jq -r '.feature')

# Trigger CircleCI pipeline via API
curl -X POST \
  -H "Circle-Token: $CIRCLECI_TOKEN" \
  -H "Content-Type: application/json" \
  "https://circleci.com/api/v2/project/gh/$ORG/$REPO/pipeline" \
  -d "{
    \"branch\": \"$(git branch --show-current)\",
    \"parameters\": {
      \"feature\": \"$FEATURE\",
      \"event_type\": \"$EVENT_TYPE\"
    }
  }"

echo "✓ Triggered CircleCI pipeline for feature $FEATURE"
```

#### Receiving Events in CircleCI

```yaml
# .circleci/config.yml
version: 2.1

parameters:
  feature:
    type: string
    default: ""
  event_type:
    type: string
    default: ""

jobs:
  integration-tests:
    docker:
      - image: python:3.11
    steps:
      - checkout
      - run:
          name: Run integration tests
          command: |
            echo "Feature: << pipeline.parameters.feature >>"
            pytest tests/integration/ -v

  deploy-staging:
    docker:
      - image: python:3.11
    steps:
      - checkout
      - run:
          name: Deploy to staging
          command: ./scripts/deploy-staging.sh

workflows:
  flowspec-events:
    when:
      or:
        - equal: [ "implement.completed", << pipeline.parameters.event_type >> ]
        - equal: [ "validate.completed", << pipeline.parameters.event_type >> ]

    jobs:
      - integration-tests:
          filters:
            branches:
              only: /.*/
          when:
            equal: [ "implement.completed", << pipeline.parameters.event_type >> ]

      - deploy-staging:
          filters:
            branches:
              only: /main/
          when:
            equal: [ "validate.completed", << pipeline.parameters.event_type >> ]
```

## Example Workflows

### Workflow 1: Automated Testing Pipeline

**Goal**: After implementation completes locally, trigger remote integration tests.

```yaml
# .flowspec/hooks/hooks.yaml
hooks:
  - name: "run-local-tests"
    description: "Run local unit tests immediately"
    events:
      - type: "implement.completed"
    script: ".flowspec/hooks/run-local-tests.sh"
    timeout: 300
    fail_mode: "stop"

  - name: "trigger-integration-tests"
    description: "Trigger remote integration tests in CI"
    events:
      - type: "implement.completed"
    script: ".flowspec/hooks/trigger-ci.sh"
    timeout: 30
```

**Flow**:
1. Developer runs `/flow:implement authentication`
2. Event `implement.completed` emitted
3. Hook `run-local-tests` executes: `pytest tests/unit/ -v`
4. If local tests pass, hook `trigger-integration-tests` triggers GitHub Actions
5. GitHub Actions runs full integration test suite
6. Results posted back to commit as status check

### Workflow 2: Deployment Pipeline

**Goal**: After validation completes, deploy to staging automatically.

```yaml
# .flowspec/hooks/hooks.yaml
hooks:
  - name: "validate-quality-gates"
    description: "Run all quality checks before deployment"
    events:
      - type: "validate.completed"
    script: ".flowspec/hooks/quality-gate.sh"
    timeout: 600
    fail_mode: "stop"

  - name: "deploy-to-staging"
    description: "Trigger staging deployment"
    events:
      - type: "validate.completed"
    script: ".flowspec/hooks/deploy-staging.sh"
    timeout: 30
```

**Flow**:
1. Developer runs `/flow:validate authentication`
2. Event `validate.completed` emitted
3. Hook `validate-quality-gates` runs: tests, lint, coverage checks
4. If all gates pass, hook `deploy-to-staging` triggers Jenkins deployment job
5. Jenkins deploys to staging environment
6. Smoke tests run automatically
7. Slack notification sent to team

### Workflow 3: PR Creation Automation

**Goal**: Automatically create PR when all tasks complete.

```yaml
# .flowspec/hooks/hooks.yaml
hooks:
  - name: "auto-create-pr"
    description: "Create PR when all tasks complete"
    events:
      - type: "task.completed"
    script: ".flowspec/hooks/create-pr.sh"
    timeout: 60
```

**Hook Script** (`.flowspec/hooks/create-pr.sh`):
```bash
#!/bin/bash
set -e

# Check if all tasks for this feature are complete
INCOMPLETE=$(backlog task list -s "In Progress" --plain | wc -l)

if [ "$INCOMPLETE" -gt 0 ]; then
  echo "⏳ Still $INCOMPLETE tasks in progress, skipping PR creation"
  exit 0
fi

# All tasks complete - create PR
FEATURE=$(git branch --show-current)
BASE_BRANCH="main"

gh pr create \
  --title "feat: $(echo $FEATURE | tr '-' ' ')" \
  --body "$(cat <<EOF
## Summary
$(backlog task list -s Done --plain | head -10)

## Test Plan
- [x] Unit tests pass
- [x] Integration tests pass
- [x] All acceptance criteria complete

Generated with [Flowspec](https://github.com/jpoley/flowspec)
EOF
)" \
  --base "$BASE_BRANCH" \
  --head "$FEATURE"

echo "✅ PR created for feature: $FEATURE"
```

## Security Considerations

### Secret Management

**DO NOT** hardcode secrets in hooks.yaml or hook scripts.

**Best Practices**:
1. Use environment variables: `${GITHUB_TOKEN}`
2. Store in `.env` file (gitignored)
3. Use secret management tools: 1Password, AWS Secrets Manager
4. Rotate tokens regularly

**Example** (`.flowspec/hooks/.env`):
```bash
# CI/CD Tokens (NEVER commit this file)
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
JENKINS_API_TOKEN=xxxxxxxxxxxx
DEPLOY_WEBHOOK_URL=https://deploy.example.com/webhook
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
```

**Load in hook script**:
```bash
#!/bin/bash
set -e

# Load environment variables from .env
if [ -f .flowspec/hooks/.env ]; then
  source .flowspec/hooks/.env
fi

# Use token
gh workflow run integration-tests.yml --ref "$(git branch --show-current)"
```

### Network Security

- **HTTPS Only**: All webhook URLs must use HTTPS
- **Authentication**: Always include authentication headers
- **Timeouts**: Set reasonable timeouts (30s for webhooks)
- **Retries**: Implement exponential backoff for failed requests

### Audit Logging

All CI/CD triggers must be logged:

```json
{
  "timestamp": "2025-12-02T15:30:45.123Z",
  "event_type": "cicd.triggered",
  "hook_name": "trigger-deployment",
  "target": {
    "platform": "github-actions",
    "workflow": "integration-tests.yml",
    "ref": "feature/authentication"
  },
  "status": "success",
  "response": {
    "run_id": "12345678",
    "run_url": "https://github.com/org/repo/actions/runs/12345678"
  }
}
```

## Performance Optimization

### Webhook Retry Strategy

```python
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def trigger_webhook(url: str, payload: dict, headers: dict) -> requests.Response:
    """
    Trigger webhook with exponential backoff retry

    Args:
        url: Webhook URL
        payload: JSON payload
        headers: HTTP headers (including auth)

    Returns:
        Response object

    Raises:
        requests.RequestException: If all retries fail
    """
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response
```

### Parallel Hook Execution

For independent CI/CD triggers (e.g., trigger tests + notify Slack):

```yaml
hooks:
  - name: "trigger-tests"
    events:
      - type: "implement.completed"
    script: ".flowspec/hooks/trigger-tests.sh"
    parallel: true  # v2 feature

  - name: "notify-team"
    events:
      - type: "implement.completed"
    script: ".flowspec/hooks/notify-slack.sh"
    parallel: true  # v2 feature
```

## Monitoring and Alerting

### CI/CD Health Metrics

Track:
- **Trigger Success Rate**: % of webhooks that return 2xx
- **Trigger Latency**: Time from event → webhook response
- **Pipeline Completion Rate**: % of triggered pipelines that complete successfully
- **Pipeline Duration**: Time from trigger → completion

### Example Dashboard (Grafana)

```promql
# Webhook trigger success rate
sum(rate(hooks_cicd_triggers_total{status="success"}[5m])) /
sum(rate(hooks_cicd_triggers_total[5m]))

# Average webhook latency
histogram_quantile(0.95, hooks_cicd_trigger_duration_seconds_bucket)

# Failed triggers in last hour
count(hooks_cicd_triggers_total{status="failed"}[1h])
```

## Troubleshooting

### Common Issues

#### 1. Webhook Timeout

**Symptom**: Hook reports "timeout" after 30s
**Cause**: CI platform slow to respond
**Solution**: Increase timeout or use async webhook (v2)

```yaml
hooks:
  - name: "trigger-slow-pipeline"
    timeout: 60  # Increase from 30s default
```

#### 2. Authentication Failure

**Symptom**: Hook reports "401 Unauthorized"
**Cause**: Invalid or expired token
**Solution**: Rotate token and update `.env`

```bash
# Test token manually
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/user
```

#### 3. Duplicate Triggers

**Symptom**: Multiple pipelines triggered for single event
**Cause**: Event emitted multiple times
**Solution**: Implement idempotency key

```bash
# Generate idempotency key from event ID
IDEMPOTENCY_KEY=$(echo "$EVENT" | jq -r '.event_id')

curl -X POST "$WEBHOOK_URL" \
  -H "Idempotency-Key: $IDEMPOTENCY_KEY" \
  -d "$PAYLOAD"
```

## References

- [GitHub Actions Workflow Dispatch](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_dispatch)
- [GitLab CI Trigger API](https://docs.gitlab.com/ee/ci/triggers/)
- [Jenkins Remote API](https://www.jenkins.io/doc/book/using/remote-access-api/)
- [CircleCI Pipeline API](https://circleci.com/docs/api/v2/)
- [Webhook Security Best Practices](https://webhooks.fyi/security/introduction)
