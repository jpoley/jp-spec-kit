# Flowspec Hooks Quick Start

## Overview

Hooks allow you to run custom scripts when workflow events occur in your Flowspec project. This enables automation of tasks like running tests, updating documentation, quality gates, and integration with external tools.

## Getting Started

### 1. Initialize Your Project

When you run `flowspec init`, the hooks system is automatically set up:

```bash
flowspec init my-project --ai claude
cd my-project
```

This creates:
- `.specify/hooks/` directory
- `hooks.yaml` configuration with examples
- Example hook scripts (disabled by default)
- `README.md` with quick reference

### 2. Review Example Hooks

Open `.specify/hooks/hooks.yaml` to see the example hooks:

```yaml
hooks:
  - name: run-tests
    events:
      - type: implement.completed
    script: run-tests.sh
    description: Run test suite after implementation
    enabled: false  # Enable when ready
```

### 3. Enable and Customize a Hook

Edit `hooks.yaml` and set `enabled: true` for the hook you want to use:

```yaml
  - name: run-tests
    events:
      - type: implement.completed
    script: run-tests.sh
    description: Run test suite after implementation
    enabled: true  # ← Changed from false
```

Edit the corresponding script (e.g., `run-tests.sh`) to run your actual test command:

```bash
#!/bin/bash
set -e

echo "Running test suite..."

# Replace with your test command
pytest tests/
# npm test
# go test ./...

echo "Tests completed successfully"
```

### 4. Test Your Hook

Before enabling it in production, test the hook:

```bash
specify hooks test run-tests implement.completed
```

This executes the hook with a mock event and shows you the output.

### 5. Validate Configuration

Always validate your configuration after making changes:

```bash
specify hooks validate
```

This checks:
- YAML syntax
- Schema compliance
- Security constraints
- Script file existence
- Duplicate names

## Event Types Reference

### Specification Events
- `spec.created` - New feature specification created
- `spec.updated` - Feature specification modified

### Planning Events
- `plan.created` - Implementation plan created
- `plan.updated` - Implementation plan modified

### Task Events
- `task.created` - New task created
- `task.completed` - Task marked as done

### Implementation Events
- `implement.started` - Implementation phase started
- `implement.completed` - Implementation phase finished

### Validation Events
- `validate.started` - Validation phase started
- `validate.completed` - Validation phase finished

### Deployment Events
- `deploy.started` - Deployment started
- `deploy.completed` - Deployment finished

### Agent Events (Multi-Machine Observability)
- `agent.started` - Agent began working on a task
- `agent.progress` - Agent reports progress (percentage, status message)
- `agent.blocked` - Agent is waiting for something
- `agent.completed` - Agent finished task
- `agent.error` - Agent encountered error
- `agent.handoff` - Agent hands off to another agent/machine

## Common Use Cases

### 1. Run Tests After Implementation

```yaml
- name: run-tests
  events:
    - type: implement.completed
  script: run-tests.sh
  enabled: true
  timeout: 300  # 5 minutes
```

Script:
```bash
#!/bin/bash
set -e
pytest tests/ --cov=src --cov-report=html
```

### 2. Update Documentation on Spec Creation

```yaml
- name: update-docs
  events:
    - type: spec.created
  script: update-docs.sh
  enabled: true
```

Script:
```bash
#!/bin/bash
set -e
SPEC_ID=$(echo "$HOOK_EVENT" | jq -r '.feature')
echo "## Feature: $SPEC_ID" >> CHANGELOG.md
echo "Created: $(date)" >> CHANGELOG.md
```

### 3. Quality Gate Before Validation

```yaml
- name: quality-gate
  events:
    - type: validate.started
  script: quality-gate.sh
  enabled: true
  fail_mode: stop  # Block workflow if gate fails
  timeout: 120
```

Script:
```bash
#!/bin/bash
set -e

# Check code coverage
coverage report --fail-under=80

# Check code complexity
radon cc . -a -nb

# Security scan
bandit -r src/

echo "Quality gate passed"
```

### 4. Run Linter on Task Completion

```yaml
- name: lint-code
  events:
    - type: task.completed
  script: lint-code.sh
  enabled: true
```

Script:
```bash
#!/bin/bash
set -e
ruff check . --fix
ruff format .
```

### 5. Notify External System

```yaml
- name: notify-slack
  events:
    - type: deploy.completed
  script: notify-slack.sh
  enabled: true
```

Script:
```bash
#!/bin/bash
SPEC_ID=$(echo "$HOOK_EVENT" | jq -r '.feature')
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d "{\"text\":\"Deployment completed: $SPEC_ID\"}"
```

### 6. Multi-Machine Agent Progress Tracking

Track agent progress across multiple machines working on the same project:

```yaml
- name: aggregate-progress
  events:
    - pattern: "agent.*"  # Match all agent events
  script: aggregate-progress.sh
  enabled: true
```

Script:
```bash
#!/bin/bash
# Aggregate agent progress to a central summary file
set -e

EVENT_TYPE=$(echo "$HOOK_EVENT" | jq -r '.event_type')
AGENT_ID=$(echo "$HOOK_EVENT" | jq -r '.context.agent_id // "unknown"')
MACHINE=$(echo "$HOOK_EVENT" | jq -r '.context.machine // "unknown"')
TASK_ID=$(echo "$HOOK_EVENT" | jq -r '.context.task_id // "none"')
PROGRESS=$(echo "$HOOK_EVENT" | jq -r '.context.progress_percent // "n/a"')
MESSAGE=$(echo "$HOOK_EVENT" | jq -r '.context.status_message // ""')
TIMESTAMP=$(echo "$HOOK_EVENT" | jq -r '.timestamp')

# Append to progress summary with file locking for concurrent safety
SUMMARY_FILE=".specify/hooks/progress-summary.log"
LOCK_FILE="$SUMMARY_FILE.lock"
(
  flock -x 200
  echo "[$TIMESTAMP] $MACHINE: $EVENT_TYPE | $AGENT_ID | $TASK_ID | ${PROGRESS}% | $MESSAGE" >> "$SUMMARY_FILE"
  # Keep only last 100 entries
  tail -100 "$SUMMARY_FILE" > "$SUMMARY_FILE.tmp" && mv "$SUMMARY_FILE.tmp" "$SUMMARY_FILE"
) 200>"$LOCK_FILE"
```

Emitting agent progress events:
```bash
# When starting work on a task
specify hooks emit agent.started --task-id task-229 --spec-id agent-hooks

# Report progress periodically
specify hooks emit agent.progress --task-id task-229 --progress 50 --message "Implementing hooks"

# When handing off to another machine
specify hooks emit agent.handoff --task-id task-229 --agent-id claude-code@muckross --message "Planning complete, ready for implementation"

# When completing work
specify hooks emit agent.completed --task-id task-229 --message "All ACs verified"
```

Multi-machine coordination example:
```
muckross (planning)     → emit agent.completed --message "Planning done"
    ↓
central progress log    → stores event
    ↓
kinsale (implementing)  → emit agent.started --task-id task-229
    ↓
kinsale                 → emit agent.progress --progress 50
    ↓
galway (reviewing)      → reads progress log, sees kinsale at 50%
```

## Event Data Access

Hooks receive event data via the `HOOK_EVENT` environment variable as JSON:

```json
{
  "event_type": "implement.completed",
  "feature": "user-auth",
  "context": {
    "task_id": "task-123"
  },
  "project_root": "/path/to/project",
  "timestamp": "2025-12-02T10:30:00Z"
}
```

Parse it in your scripts:

```bash
#!/bin/bash
EVENT_TYPE=$(echo "$HOOK_EVENT" | jq -r '.event_type')
SPEC_ID=$(echo "$HOOK_EVENT" | jq -r '.feature // "unknown"')
TASK_ID=$(echo "$HOOK_EVENT" | jq -r '.context.task_id // "unknown"')

echo "Event: $EVENT_TYPE"
echo "Spec: $SPEC_ID"
echo "Task: $TASK_ID"
```

## CLI Commands

### List Configured Hooks

```bash
specify hooks list
```

Shows all hooks with their event types, scripts, and configuration.

### Emit Events Manually

```bash
# Emit a spec.created event
specify hooks emit spec.created --spec-id my-feature

# Emit a task.completed event
specify hooks emit task.completed --task-id task-123 --spec-id my-feature

# Dry run (show what would execute)
specify hooks emit implement.completed --spec-id auth --dry-run

# JSON output
specify hooks emit spec.created --spec-id test --json
```

### View Execution History

```bash
# Show last 10 executions
specify hooks audit

# Show last 20 executions
specify hooks audit --tail 20

# JSON output
specify hooks audit --json
```

### Test a Hook

```bash
# Test run-tests hook with implement.completed event
specify hooks test run-tests implement.completed

# Test with custom spec ID
specify hooks test quality-gate spec.created --spec-id my-feature
```

### Validate Configuration

```bash
# Validate default hooks.yaml
specify hooks validate

# Validate specific config file
specify hooks validate -f .specify/hooks/custom.yaml
```

## Configuration Options

### Global Defaults

```yaml
defaults:
  timeout: 30        # Default timeout in seconds
  fail_mode: continue  # continue or stop
```

### Hook Configuration

```yaml
- name: my-hook
  events:
    - type: spec.created  # Event type to match
    # OR
    - pattern: "spec.*"   # Regex pattern

  # Execution method (choose one)
  script: my-script.sh     # Script in .specify/hooks/
  # OR
  command: "npm test"      # Inline command

  description: "Hook description"
  enabled: true            # Enable/disable hook
  timeout: 60              # Override default timeout
  fail_mode: stop          # stop or continue

  env:                     # Additional environment variables
    DEBUG: "true"
    LOG_LEVEL: "info"
```

## Fail Modes

### `continue` (default)
- Hook failures are logged but don't stop the workflow
- Useful for non-critical tasks (notifications, logging, etc.)

### `stop`
- Hook failures block the workflow
- Use for quality gates and critical checks

Example:
```yaml
- name: quality-gate
  events:
    - type: validate.started
  script: quality-gate.sh
  fail_mode: stop  # Workflow stops if this fails
```

## Security

### Sandboxing
- Scripts must be in `.specify/hooks/` directory
- Cannot execute scripts outside this directory
- Timeout enforced (default: 30s, max: 600s)

### Audit Logging
- All hook executions are logged to `.specify/hooks/audit.log`
- Includes timestamp, success/failure, duration, exit code
- View with `specify hooks audit`

### Best Practices
1. **Keep scripts in version control** - Track changes to hooks
2. **Test before enabling** - Use `specify hooks test`
3. **Set appropriate timeouts** - Prevent hung processes
4. **Use fail_mode wisely** - Only use `stop` for critical gates
5. **Validate environment variables** - Don't assume they exist
6. **Handle errors gracefully** - Use `set -e` in bash scripts

## Troubleshooting

### Hook not executing
1. Check `enabled: true` in hooks.yaml
2. Verify event type matches
3. Check script is executable: `chmod +x .specify/hooks/my-script.sh`
4. Validate config: `specify hooks validate`

### Hook failing
1. Test manually: `specify hooks test my-hook implement.completed`
2. Check audit log: `specify hooks audit --tail 20`
3. Review error messages in output
4. Verify script permissions and dependencies

### Timeout errors
1. Increase timeout in hooks.yaml
2. Optimize script performance
3. Move long-running tasks to background jobs

### Event not firing
1. Verify you're emitting the event: `specify hooks emit <event-type> --dry-run`
2. Check event type spelling
3. Review hooks.yaml event matchers

## Examples by Language

### Python Projects
```yaml
- name: run-tests
  events:
    - type: implement.completed
  script: run-tests.sh
  enabled: true
```

```bash
#!/bin/bash
set -e
pytest tests/ --cov=src --cov-report=html
ruff check . --fix
ruff format .
```

### JavaScript/Node.js Projects
```yaml
- name: run-tests
  events:
    - type: implement.completed
  script: run-tests.sh
  enabled: true
```

```bash
#!/bin/bash
set -e
npm test
npm run lint
npm run build
```

### Go Projects
```yaml
- name: run-tests
  events:
    - type: implement.completed
  script: run-tests.sh
  enabled: true
```

```bash
#!/bin/bash
set -e
go test ./...
go vet ./...
golangci-lint run
```

## Next Steps

1. **Enable your first hook** - Start with a simple test hook
2. **Test it thoroughly** - Use `specify hooks test`
3. **Monitor execution** - Check `specify hooks audit`
4. **Customize for your workflow** - Add project-specific hooks
5. **Share with team** - Commit hooks to version control

## Additional Resources

- [Hooks Configuration Reference](../reference/hooks-api.md) - Full configuration options
- [Event Types Reference](../reference/hooks-events.md) - Complete event catalog
- [Hook Examples Library](../examples/hooks/) - Real-world examples
- [Security Best Practices](../guides/hooks-security.md) - Secure hook development

## Getting Help

- Validate your config: `specify hooks validate`
- Test hooks individually: `specify hooks test <hook-name> <event-type>`
- View execution history: `specify hooks audit`
- Check GitHub issues: https://github.com/jpoley/flowspec/issues
