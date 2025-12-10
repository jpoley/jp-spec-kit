# Platform Integration: archive-tasks.sh Script

**Document Type**: Platform Integration Design
**Feature**: Automated Task Archiving for Backlog Maintenance
**Status**: Proposed
**Date**: 2025-12-03
**Author**: @platform-engineer
**Related Task**: task-281

---

## Executive Summary

This document defines the platform integration strategy for `archive-tasks.sh`, a script that automates backlog task archiving with flexible filtering criteria. The script integrates with:

1. **Claude Code Hooks** - For agent-triggered archiving within workflows
2. **GitHub Actions** - For automated and scheduled archiving in CI/CD
3. **Local CLI** - For manual operator invocation

**Key Design Principles**:
- **Fail-safe operations**: Dry-run by default in automation
- **Observability-first**: Comprehensive logging and audit trails
- **Zero-touch automation**: Works without manual intervention
- **Flexible filtering**: Archive by status, date, or all tasks

---

## Architecture Overview

### Integration Points

```
┌─────────────────────────────────────────────────────────┐
│                   User / CI Triggers                     │
└─────────────────┬───────────────────┬───────────────────┘
                  │                   │
     ┌────────────▼─────────┐  ┌─────▼──────────────┐
     │  Claude Code Hooks   │  │  GitHub Actions    │
     │  (.claude/hooks/)    │  │  (workflows/)      │
     └────────────┬─────────┘  └─────┬──────────────┘
                  │                   │
                  │    ┌──────────────┼──────────┐
                  │    │              │          │
            ┌─────▼────▼───┐   ┌─────▼────┐ ┌──▼───────┐
            │ archive-tasks │   │ backlog  │ │   Git    │
            │     .sh       │◄──┤   CLI    │ │ (commits)│
            └───────────────┘   └──────────┘ └──────────┘
                  │
                  ▼
         ┌────────────────┐
         │  Audit Logs    │
         │  Metrics       │
         │  Notifications │
         └────────────────┘
```

### Script Capabilities

| Feature | Description | Use Case |
|---------|-------------|----------|
| **Archive All** | `--all` flag archives tasks regardless of status | Bulk cleanup, repository refresh |
| **Archive by Date** | `--done-by YYYY-MM-DD` archives tasks completed by date | Periodic cleanup, milestone closure |
| **Archive Done** | Default behavior: archive only Done tasks | Standard workflow completion |
| **Dry Run** | `--dry-run` previews changes without executing | CI validation, manual review |

---

## 1. Claude Code Hook Integration

### Hook Architecture

Claude Code hooks provide workflow-triggered automation within agent sessions. The `archive-tasks.sh` script fits into the **post-workflow** hook category.

#### Hook Trigger Points

Based on existing JP Spec Kit hook system:

```yaml
# .claude/hooks/hooks.yaml (proposed v2)

hooks:
  - name: "archive-completed-tasks"
    events:
      - type: workflow.completed
      - type: validate.completed
    script: "post-workflow-archive.sh"
    description: "Archive completed backlog tasks after workflow completion"
    enabled: false  # Enable when ready
    timeout: 30
    fail_mode: continue  # Don't block workflow on archive failures
```

#### Hook Event Flow

```
/jpspec:validate completed
       ↓
Event: validate.completed emitted
       ↓
Hook Matcher: post-workflow-archive.sh matched
       ↓
Hook Runner: Execute with sandbox
       ↓
archive-tasks.sh --dry-run (in hooks)
       ↓
Audit Log: Log execution result
       ↓
Continue workflow (fail-open)
```

### Hook Script Implementation

**Location**: `.claude/hooks/post-workflow-archive.sh`

```bash
#!/usr/bin/env bash
#
# Post-workflow hook: Archive completed backlog tasks
#
# Triggered by: validate.completed event
# Behavior: Dry-run preview, no actual archiving (safety-first in hooks)
#
set -euo pipefail

# Read event from stdin (standard hook interface)
EVENT=$(cat)

# Parse event details
EVENT_TYPE=$(echo "$EVENT" | jq -r '.event_type')
FEATURE=$(echo "$EVENT" | jq -r '.feature // "unknown"')
PROJECT_ROOT=$(echo "$EVENT" | jq -r '.project_root')

# Log hook execution
echo "[archive-tasks-hook] Triggered by: $EVENT_TYPE"
echo "[archive-tasks-hook] Feature: $FEATURE"
echo "[archive-tasks-hook] Project: $PROJECT_ROOT"

# Change to project root
cd "$PROJECT_ROOT"

# Execute archive script in DRY-RUN mode (safety-first)
# Only show what WOULD be archived, don't modify backlog
echo "[archive-tasks-hook] Running archive preview..."
./scripts/bash/archive-tasks.sh --dry-run

# Exit with success (fail-open: don't block workflow on archive issues)
exit 0
```

**Key Design Decisions**:

1. **Dry-run only in hooks**: Claude Code hooks run `--dry-run` to preview archiving without modifying the backlog. Actual archiving happens in GitHub Actions or manual CLI.
   - Rationale: Hooks execute during active agent work; modifying backlog mid-session risks confusion.

2. **Fail-open error handling**: Hook exits 0 even if script fails.
   - Rationale: Archiving is maintenance, not a quality gate. Workflow must proceed.

3. **Event-driven trigger**: Hook responds to `validate.completed` event (end of /jpspec:validate).
   - Rationale: Validation is the final workflow step before PR creation; natural checkpoint for cleanup.

### Hook Testing

```bash
# Test hook directly
echo '{"event_type": "validate.completed", "feature": "test", "project_root": "/home/jpoley/ps/jp-spec-kit"}' | \
  .claude/hooks/post-workflow-archive.sh

# Test via specify hooks test command (once hook system implemented)
specify hooks test post-workflow-archive validate.completed --spec-id test-feature

# Validate hook configuration
specify hooks validate
```

### Hook Security

**Sandboxing** (per ADR-006):
- Script must reside in `.claude/hooks/` directory (path allowlist enforcement)
- Timeout: 30 seconds maximum
- Environment: Minimal sanitized env vars (PATH, HOME, USER)
- Working directory: Project root (validated)

**Security Validation**:
```python
# From ADR-006: Hook execution model
validate_script_path(".claude/hooks/post-workflow-archive.sh", project_root)
# Raises SecurityError if path traversal detected
```

### Current Hook System Status

**Note**: As of 2025-12-03, the full event-driven hook system (ADR-005, ADR-006) is **not yet implemented**. Current hooks use different mechanisms:

- **SessionStart**: `.claude/hooks/session-start.sh` (Claude Code native)
- **PreToolUse**: `.claude/hooks/pre-tool-use-*.py` (Claude Code native)
- **PostToolUse**: `.claude/hooks/post-tool-use-*.sh` (Claude Code native)
- **Stop**: `.claude/hooks/stop-quality-gate.py` (Claude Code native)

**Implementation Path**:
1. Implement archive-tasks.sh script (task-281)
2. Complete event model implementation (task-198, task-201)
3. Complete hook runner implementation (task-202)
4. Integrate archive-tasks.sh with hook system (task to be created)

---

## 2. GitHub Actions Integration

### Workflow Design

**Location**: `.github/workflows/backlog-archive.yml`

```yaml
name: Backlog Archive

on:
  # Manual trigger for on-demand archiving
  workflow_dispatch:
    inputs:
      mode:
        description: 'Archive mode'
        required: true
        type: choice
        options:
          - done  # Archive Done tasks only
          - all   # Archive all tasks
          - date  # Archive by completion date
        default: 'done'
      done_by_date:
        description: 'Archive tasks completed by date (YYYY-MM-DD)'
        required: false
        type: string
      dry_run:
        description: 'Dry run (preview only)'
        required: false
        type: boolean
        default: true

  # Scheduled archiving (weekly on Sundays at midnight UTC)
  schedule:
    - cron: '0 0 * * 0'

  # Keyword-triggered archiving (commit message contains 'archive-backlog')
  push:
    branches: [main]

jobs:
  archive-backlog:
    runs-on: ubuntu-latest

    # Only run on schedule if there are Done tasks
    # Only run on push if commit message contains 'archive-backlog'
    if: |
      github.event_name == 'workflow_dispatch' ||
      github.event_name == 'schedule' ||
      (github.event_name == 'push' &&
       (contains(github.event.head_commit.message, 'archive-backlog') ||
        contains(github.event.head_commit.message, 'Archive Backlog')))

    permissions:
      contents: write  # Required for git commits

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install backlog.md CLI
        run: npm install -g backlog.md

      - name: Verify backlog CLI installation
        run: backlog --version

      - name: Determine archive mode
        id: mode
        run: |
          if [[ "${{ github.event_name }}" == "workflow_dispatch" ]]; then
            MODE="${{ inputs.mode }}"
            DRY_RUN="${{ inputs.dry_run }}"
            DONE_BY="${{ inputs.done_by_date }}"
          elif [[ "${{ github.event_name }}" == "schedule" ]]; then
            MODE="done"
            DRY_RUN="false"
            DONE_BY=""
          else
            # Push event
            MODE="done"
            DRY_RUN="false"
            DONE_BY=""
          fi

          echo "mode=${MODE}" >> $GITHUB_OUTPUT
          echo "dry_run=${DRY_RUN}" >> $GITHUB_OUTPUT
          echo "done_by=${DONE_BY}" >> $GITHUB_OUTPUT

      - name: Run archive script
        id: archive
        run: |
          chmod +x scripts/bash/archive-tasks.sh

          # Build command based on mode
          CMD="./scripts/bash/archive-tasks.sh"

          # Add mode flags
          if [[ "${{ steps.mode.outputs.mode }}" == "all" ]]; then
            CMD="$CMD --all"
          elif [[ "${{ steps.mode.outputs.mode }}" == "date" && -n "${{ steps.mode.outputs.done_by }}" ]]; then
            CMD="$CMD --done-by ${{ steps.mode.outputs.done_by }}"
          fi

          # Add dry-run if enabled
          if [[ "${{ steps.mode.outputs.dry_run }}" == "true" ]]; then
            CMD="$CMD --dry-run"
          fi

          # Set trigger source for audit
          export TRIGGER_SOURCE="github-actions (${{ github.event_name }})"

          # Execute and capture exit code
          $CMD || exit_code=$?

          # Handle exit codes:
          # 0 = success (tasks archived)
          # 2 = no tasks to archive (still success for workflow)
          # 1, 3 = actual errors
          if [[ "${exit_code:-0}" -eq 2 ]]; then
            echo "has_changes=false" >> $GITHUB_OUTPUT
            echo "No tasks matched archive criteria"
            exit 0
          elif [[ "${exit_code:-0}" -ne 0 ]]; then
            exit $exit_code
          else
            echo "has_changes=true" >> $GITHUB_OUTPUT
          fi

      - name: Commit and push changes
        if: steps.archive.outputs.has_changes == 'true' && steps.mode.outputs.dry_run == 'false'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

          # Stage backlog changes
          git add backlog/

          # Commit with mode-specific message
          MODE="${{ steps.mode.outputs.mode }}"
          if [[ "$MODE" == "all" ]]; then
            git commit -m "chore(backlog): archive all tasks via GitHub Actions

          Trigger: ${{ github.event_name }}
          Mode: archive-all

          Signed-off-by: github-actions[bot] <github-actions[bot]@users.noreply.github.com>"
          elif [[ "$MODE" == "date" ]]; then
            git commit -m "chore(backlog): archive tasks completed by ${{ steps.mode.outputs.done_by }}

          Trigger: ${{ github.event_name }}
          Mode: archive-by-date

          Signed-off-by: github-actions[bot] <github-actions[bot]@users.noreply.github.com>"
          else
            git commit -m "chore(backlog): archive Done tasks via GitHub Actions

          Trigger: ${{ github.event_name }}
          Mode: archive-done

          Signed-off-by: github-actions[bot] <github-actions[bot]@users.noreply.github.com>"
          fi

          git push origin main

      - name: Generate summary
        run: |
          echo "## Backlog Archive Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Mode**: ${{ steps.mode.outputs.mode }}" >> $GITHUB_STEP_SUMMARY
          echo "**Dry Run**: ${{ steps.mode.outputs.dry_run }}" >> $GITHUB_STEP_SUMMARY
          echo "**Trigger**: ${{ github.event_name }}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY

          if [[ "${{ steps.archive.outputs.has_changes }}" == "true" ]]; then
            echo "✅ Tasks archived successfully" >> $GITHUB_STEP_SUMMARY
          else
            echo "ℹ️ No tasks matched archive criteria" >> $GITHUB_STEP_SUMMARY
          fi
```

### Workflow Trigger Modes

#### 1. Manual Dispatch (On-Demand)

**Use Case**: Operator-initiated cleanup, pre-release archiving, bulk maintenance.

```bash
# Via GitHub UI: Actions > Backlog Archive > Run workflow
# Select mode: done | all | date
# Toggle dry-run: true | false
```

**Example Scenarios**:
- Archive all tasks before major release: mode=all, dry_run=false
- Preview archiving: mode=done, dry_run=true
- Archive tasks from last sprint: mode=date, done_by_date=2025-11-30

#### 2. Scheduled Archiving (Cron)

**Use Case**: Weekly automated cleanup of Done tasks.

```yaml
schedule:
  - cron: '0 0 * * 0'  # Every Sunday at midnight UTC
```

**Behavior**:
- Automatically archives Done tasks
- Commits and pushes changes
- Runs without human intervention

#### 3. Commit Keyword Trigger

**Use Case**: Integrate archiving into development workflow.

```bash
# Trigger archiving via commit message
git commit -m "feat: complete user authentication

archive-backlog"

# Push triggers workflow
git push origin main
```

**Behavior**:
- Detects `archive-backlog` (case-insensitive) in commit message
- Archives Done tasks
- Commits archive changes in separate commit

### Workflow Security

**Permissions**:
```yaml
permissions:
  contents: write  # Required for git commits
```

**Secrets**: Uses `GITHUB_TOKEN` (automatically provided by GitHub Actions).

**Branch Protection**:
- Workflow commits as `github-actions[bot]`
- Consider adding bypass rules for bot commits if branch protection is strict

### Workflow Testing

```bash
# Test workflow locally with act
act workflow_dispatch -j archive-backlog \
  --input mode=done \
  --input dry_run=true

# Test scheduled trigger (uses schedule event)
act schedule -j archive-backlog

# Test push trigger (simulate commit with keyword)
act push -j archive-backlog
```

### Observability

**GitHub Actions Dashboard**:
- Workflow run history: Actions > Backlog Archive
- Step-by-step logs with archive output
- Job summary with archive results

**Audit Trail**:
- Git commit history shows archived tasks
- Workflow logs show exact commands executed
- GITHUB_STEP_SUMMARY shows summary statistics

---

## 3. CI/CD Pipeline Integration

### Integration with Existing CI

The archive script integrates with the existing `.github/workflows/ci.yml` pipeline.

#### Option A: Quality Gate (Fail on Stale Tasks)

**Use Case**: Enforce backlog hygiene as part of CI.

```yaml
# Add to .github/workflows/ci.yml

jobs:
  backlog-hygiene:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install backlog CLI
        run: npm install -g backlog.md

      - name: Check for stale Done tasks
        run: |
          # Run dry-run to detect Done tasks
          ./scripts/bash/archive-tasks.sh --dry-run || exit_code=$?

          if [[ "${exit_code:-0}" -eq 0 ]]; then
            echo "❌ Found Done tasks that should be archived"
            echo "Run: ./scripts/bash/flush-backlog.sh"
            exit 1
          elif [[ "${exit_code:-0}" -eq 2 ]]; then
            echo "✅ No stale Done tasks"
            exit 0
          else
            echo "⚠️ Script error (exit code: ${exit_code})"
            exit $exit_code
          fi
```

**Rationale**: Forces developers to archive completed tasks before merging PRs.

**Trade-offs**:
- **Pro**: Maintains clean backlog, prevents accumulation
- **Con**: Adds friction to PR workflow, may annoy developers

**Recommendation**: Use only if backlog hygiene is critical to team workflow.

#### Option B: Advisory Check (Warn but Don't Fail)

**Use Case**: Remind developers to archive, but don't block CI.

```yaml
jobs:
  backlog-check:
    runs-on: ubuntu-latest
    steps:
      - name: Check for archivable tasks
        continue-on-error: true  # Don't fail CI
        run: |
          ./scripts/bash/archive-tasks.sh --dry-run || exit_code=$?

          if [[ "${exit_code:-0}" -eq 0 ]]; then
            echo "::notice::Found Done tasks. Consider archiving with: ./scripts/bash/flush-backlog.sh"
          fi
```

**Rationale**: Nudges without blocking, respects developer autonomy.

**Recommendation**: Preferred approach for most teams.

---

## 4. Operational Considerations

### Logging and Observability

#### Script Logging

```bash
# archive-tasks.sh outputs to stdout/stderr

# Standard output format:
# [archive-tasks] Querying Done tasks...
# [archive-tasks] Found 5 Done tasks
# [archive-tasks]   ✓ Archived: task-281
# [archive-tasks]   ✓ Archived: task-282
# [archive-tasks] Successfully archived 5 tasks

# JSON output for machine parsing (future enhancement):
./scripts/bash/archive-tasks.sh --json
# {
#   "archived": ["task-281", "task-282"],
#   "failed": [],
#   "total": 5,
#   "duration_ms": 1234
# }
```

#### Audit Trail

**Git History**:
```bash
# Review archive commits
git log --grep="archive" --oneline

# View specific archive changes
git show <commit-hash>
```

**GitHub Actions Logs**:
- Navigate to Actions > Backlog Archive > [Run ID]
- Download logs: Actions > Backlog Archive > [Run ID] > Download logs

#### Metrics Collection (Future Enhancement)

```yaml
# Add to archive-tasks.sh (future task)

# Emit metrics to CloudWatch, Datadog, etc.
emit_metric "backlog.archive.count" 5
emit_metric "backlog.archive.duration_ms" 1234
emit_metric "backlog.archive.mode" "done"
```

### Error Handling and Alerting

#### Exit Code Strategy

| Exit Code | Meaning | Action |
|-----------|---------|--------|
| 0 | Success | Continue workflow |
| 1 | Validation error | Alert operator, check backlog CLI |
| 2 | No tasks to archive | Informational, continue |
| 3 | Partial failure | Alert operator, manual review needed |

#### Alerting Strategy

**GitHub Actions Failure Notification**:
```yaml
# Add to backlog-archive.yml (after archive step)

- name: Notify on failure
  if: failure()
  run: |
    # Send Slack notification
    curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
      -H 'Content-Type: application/json' \
      -d '{
        "text": "❌ Backlog archive failed",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "Workflow: ${{ github.workflow }}\nRun: ${{ github.run_id }}"
            }
          }
        ]
      }'
```

**Recommended Alert Channels**:
- Slack channel: `#backlog-ops` or `#team-notifications`
- Email: Platform engineer or team lead
- PagerDuty: Only for critical failures (fail_mode=stop scenarios)

### Dry-Run vs. Production Modes

#### Dry-Run Mode

**When to Use**:
- CI validation (always)
- Manual testing
- Preview before bulk operations

**Behavior**:
```bash
# Shows what WOULD be archived, no changes made
./scripts/bash/archive-tasks.sh --dry-run

# Output:
# [DRY RUN] Would archive: task-281
# [DRY RUN] Would archive: task-282
# [DRY RUN] Would archive 5 task(s)
```

#### Production Mode

**When to Use**:
- GitHub Actions scheduled runs
- Manual archiving after review
- Commit keyword triggers

**Behavior**:
```bash
# Archives tasks and modifies backlog
./scripts/bash/archive-tasks.sh

# Output:
# ✓ Archived: task-281
# ✓ Archived: task-282
# Successfully archived 5 tasks
```

**Safety Checks**:
- Requires backlog CLI to be installed
- Validates backlog directory exists
- Creates archive directory if missing
- Atomic operations (single task archival via CLI)

### Performance Considerations

**Expected Latency**:
- 10 tasks: ~2-3 seconds
- 50 tasks: ~10-15 seconds
- 100 tasks: ~20-30 seconds

**Bottlenecks**:
- Backlog CLI invocation per task (subprocess overhead)
- Git operations (staging, committing)
- Network latency (if pushing to remote)

**Optimization Strategies** (Future):
1. Batch archiving: `backlog task archive 1 2 3 4 5`
2. Parallel archiving: Use GNU parallel or xargs
3. Caching: Cache backlog CLI binary in CI

**Timeout Configuration**:
```yaml
# GitHub Actions
jobs:
  archive-backlog:
    timeout-minutes: 10  # Kill job if exceeds 10 minutes

# Claude Code Hooks
hooks:
  - name: "archive-completed-tasks"
    timeout: 30  # 30 seconds max
```

---

## 5. Testing Strategy

### Unit Testing (Script Logic)

```bash
# Test script exists and is executable
test -x scripts/bash/archive-tasks.sh

# Test help output
./scripts/bash/archive-tasks.sh --help

# Test dry-run mode
./scripts/bash/archive-tasks.sh --dry-run

# Test invalid arguments
./scripts/bash/archive-tasks.sh --invalid-flag
# Expected: Exit code 1, error message shown
```

### Integration Testing (with backlog CLI)

```bash
# Create test tasks
backlog task create "Test task 1" -s Done
backlog task create "Test task 2" -s Done

# Test archiving
./scripts/bash/archive-tasks.sh --dry-run
# Expected: Shows 2 tasks

./scripts/bash/archive-tasks.sh
# Expected: Archives 2 tasks, exit code 0

# Verify archive
ls backlog/archive/tasks/
# Expected: 2 archived task files

# Test no tasks scenario
./scripts/bash/archive-tasks.sh
# Expected: Exit code 2, "No tasks to archive" message
```

### CI Pipeline Testing

```bash
# Test GitHub Actions locally with act
act workflow_dispatch -j archive-backlog \
  --input mode=done \
  --input dry_run=true

# Verify workflow steps execute correctly
# Expected: All steps pass, dry-run output shown
```

### Hook Testing (Once Hook System Implemented)

```bash
# Test hook directly
echo '{"event_type": "validate.completed", "project_root": "/home/jpoley/ps/jp-spec-kit"}' | \
  .claude/hooks/post-workflow-archive.sh

# Expected: Dry-run output, exit code 0

# Test hook via specify CLI
specify hooks test post-workflow-archive validate.completed

# Validate hook configuration
specify hooks validate
# Expected: No validation errors
```

---

## 6. Documentation Requirements

### User-Facing Documentation

#### 1. Script Usage Guide

**Location**: `docs/guides/backlog-archive.md`

**Contents**:
- Script purpose and use cases
- Command-line arguments and flags
- Examples for common scenarios
- Exit codes and error handling
- Troubleshooting common issues

**Example Section**:
```markdown
## Archive All Tasks

To archive ALL tasks regardless of status (useful for bulk cleanup):

```bash
./scripts/bash/archive-tasks.sh --all
```

⚠️ **Warning**: This archives tasks in all statuses (To Do, In Progress, Done).
Always run with `--dry-run` first to preview changes.
```

#### 2. GitHub Actions Workflow Guide

**Location**: `docs/guides/backlog-archive-workflow.md`

**Contents**:
- Workflow trigger modes (manual, scheduled, commit keyword)
- How to run workflow manually via GitHub UI
- Scheduled archiving schedule and behavior
- Commit keyword syntax
- Viewing workflow logs and results

#### 3. Hook Integration Guide

**Location**: `docs/guides/backlog-archive-hook.md`

**Contents**:
- Hook trigger events (validate.completed, workflow.completed)
- Enabling/disabling the hook
- Hook behavior (dry-run only, fail-open)
- Customizing hook configuration
- Troubleshooting hook execution

### Developer-Facing Documentation

#### 1. Platform Architecture

**Location**: `docs/platform/archive-tasks-integration.md` (this document)

**Contents**:
- Architecture overview
- Integration points (hooks, CI/CD, CLI)
- Security and sandboxing
- Observability and logging
- Testing strategy

#### 2. Troubleshooting Runbook

**Location**: `docs/runbooks/backlog-archive-troubleshooting.md`

**Contents**:
- Common error messages and solutions
- Debugging workflow failures
- Recovering from partial archive failures
- Performance tuning
- Escalation paths

**Example Entry**:
```markdown
### Error: "backlog CLI not found"

**Symptom**: Script exits with code 1 and message "backlog CLI not found"

**Cause**: backlog.md CLI not installed or not in PATH

**Solution**:
1. Check if backlog CLI is installed: `backlog --version`
2. If not installed: `npm install -g backlog.md`
3. Verify PATH includes npm global bin: `echo $PATH`
4. Re-run script

**Prevention**: Add CI step to verify backlog CLI before archiving
```

---

## 7. Infrastructure Tasks

The following tasks must be created in backlog.md for full implementation:

### Task 1: Implement archive-tasks.sh Script

**Title**: Implement archive-tasks.sh script with flexible filtering

**Description**: Create bash script to archive backlog tasks with --all, --done-by, and --dry-run flags. Integrate with backlog CLI for atomic archiving operations.

**Acceptance Criteria**:
- [ ] Script supports `--all` flag to archive all tasks
- [ ] Script supports `--done-by YYYY-MM-DD` flag to archive by date
- [ ] Script supports `--dry-run` flag for preview
- [ ] Script has proper exit codes (0=success, 1=error, 2=no tasks, 3=partial)
- [ ] Script outputs human-readable logs to stdout/stderr
- [ ] Script passes shellcheck linting
- [ ] Script has `--help` flag with usage documentation

**Labels**: backend, infrastructure, task-management

**Priority**: High

**Dependencies**: backlog.md CLI must be installed

---

### Task 2: Create GitHub Actions Workflow for Backlog Archive

**Title**: Create backlog-archive.yml workflow with manual, scheduled, and keyword triggers

**Description**: Implement GitHub Actions workflow to automate backlog archiving with multiple trigger modes (workflow_dispatch, schedule, push keyword).

**Acceptance Criteria**:
- [ ] Workflow supports manual dispatch with mode selection (done/all/date)
- [ ] Workflow supports scheduled execution (weekly on Sundays)
- [ ] Workflow supports commit keyword trigger (archive-backlog)
- [ ] Workflow commits and pushes archive changes
- [ ] Workflow generates job summary with archive results
- [ ] Workflow handles exit codes correctly (0, 2 = success, 1/3 = failure)
- [ ] Workflow has proper permissions (contents: write)

**Labels**: infrastructure, ci-cd, github-actions

**Priority**: High

**Dependencies**: archive-tasks.sh script must exist

---

### Task 3: Create Claude Code Hook for Post-Workflow Archiving

**Title**: Create post-workflow-archive.sh hook for agent-triggered archiving

**Description**: Implement Claude Code hook that runs archive-tasks.sh in dry-run mode after workflow completion (validate.completed event).

**Acceptance Criteria**:
- [ ] Hook script exists at `.claude/hooks/post-workflow-archive.sh`
- [ ] Hook reads event from stdin (standard hook interface)
- [ ] Hook parses event_type, feature, project_root from JSON
- [ ] Hook runs archive-tasks.sh with --dry-run flag
- [ ] Hook exits 0 (fail-open) even if script fails
- [ ] Hook logs execution to stdout for debugging
- [ ] Hook is executable and passes shellcheck

**Labels**: infrastructure, agent-hooks, claude-code

**Priority**: Medium

**Dependencies**:
- archive-tasks.sh script must exist
- Event model implementation (task-198, task-201)
- Hook runner implementation (task-202)

---

### Task 4: Update Documentation for Archive Script

**Title**: Create comprehensive documentation for archive-tasks.sh and integrations

**Description**: Write user and developer documentation for archive script, GitHub Actions workflow, and hook integration.

**Acceptance Criteria**:
- [ ] User guide exists at `docs/guides/backlog-archive.md`
- [ ] Workflow guide exists at `docs/guides/backlog-archive-workflow.md`
- [ ] Hook guide exists at `docs/guides/backlog-archive-hook.md`
- [ ] Troubleshooting runbook exists at `docs/runbooks/backlog-archive-troubleshooting.md`
- [ ] All guides have examples and command-line usage
- [ ] CLAUDE.md updated with script reference

**Labels**: documentation

**Priority**: Medium

**Dependencies**: Tasks 1, 2, 3 must be completed

---

### Task 5: Add CI Check for Backlog Hygiene

**Title**: Add optional CI check for stale Done tasks

**Description**: Add optional CI job to ci.yml that warns (but doesn't fail) if Done tasks exist that should be archived.

**Acceptance Criteria**:
- [ ] CI job added to `.github/workflows/ci.yml`
- [ ] Job runs archive-tasks.sh with --dry-run
- [ ] Job uses `continue-on-error: true` (advisory, not blocking)
- [ ] Job outputs notice message if Done tasks found
- [ ] Job has descriptive name: "Check for archivable tasks"

**Labels**: infrastructure, ci-cd, quality-gate

**Priority**: Low

**Dependencies**: archive-tasks.sh script must exist

---

## 8. Implementation Roadmap

### Phase 1: Core Script Implementation (Week 1)

**Goal**: Functional archive-tasks.sh script with all filtering modes

**Deliverables**:
- [ ] archive-tasks.sh script
- [ ] Unit tests (shellcheck, manual testing)
- [ ] Integration tests with backlog CLI
- [ ] Basic documentation (--help flag, README)

**Success Criteria**: Script can archive tasks via all three modes (done, all, date) and passes shellcheck.

### Phase 2: GitHub Actions Integration (Week 2)

**Goal**: Automated archiving via GitHub Actions

**Deliverables**:
- [ ] backlog-archive.yml workflow
- [ ] Workflow testing with act
- [ ] Workflow documentation
- [ ] Test manual, scheduled, and keyword triggers

**Success Criteria**: Workflow executes successfully on all trigger modes and commits changes to repository.

### Phase 3: Hook Integration (Week 3)

**Goal**: Agent-triggered archiving via Claude Code hooks

**Deliverables**:
- [ ] post-workflow-archive.sh hook script
- [ ] Hook testing (manual execution, specify hooks test)
- [ ] Hook documentation
- [ ] Hook configuration (hooks.yaml)

**Success Criteria**: Hook executes successfully on validate.completed event and logs output.

**Blocker**: Depends on event model and hook runner implementation (tasks 198, 201, 202).

### Phase 4: Documentation and Polish (Week 4)

**Goal**: Comprehensive documentation and CI integration

**Deliverables**:
- [ ] All user guides written
- [ ] Troubleshooting runbook created
- [ ] CI check added (optional)
- [ ] CLAUDE.md updated

**Success Criteria**: Documentation is complete, accurate, and reviewed by at least one other engineer.

---

## 9. Security and Compliance

### Security Considerations

1. **Script Execution**:
   - Script runs with user privileges (no sudo required)
   - Script does not accept untrusted input (only CLI flags)
   - Script uses backlog CLI for archiving (atomic, safe operations)

2. **GitHub Actions Security**:
   - Workflow uses `GITHUB_TOKEN` (scoped to repository)
   - Workflow commits as `github-actions[bot]` (auditable)
   - Workflow runs in isolated Ubuntu runner (ephemeral)

3. **Hook Security**:
   - Hook script sandboxed by Claude Code hook system
   - Hook runs in project root (validated working directory)
   - Hook uses minimal environment variables
   - Hook has timeout enforcement (30 seconds)

### Compliance Requirements

**Audit Trail**:
- Git commits show archived tasks with timestamp
- GitHub Actions logs show workflow execution history
- Hook audit logs show hook execution details

**Change Control**:
- All archive operations are reversible (archived tasks remain in Git history)
- Dry-run mode allows preview before execution
- Manual approval required for workflow_dispatch mode

---

## 10. Future Enhancements

### v2: Advanced Features

1. **Batch Archiving**: Archive multiple tasks in single CLI invocation
   ```bash
   backlog task archive 1 2 3 4 5  # Faster than 5 separate calls
   ```

2. **Parallel Execution**: Use GNU parallel for faster archiving
   ```bash
   echo "1 2 3 4 5" | xargs -P 5 -n 1 backlog task archive
   ```

3. **JSON Output**: Machine-parseable output for metrics
   ```bash
   ./scripts/bash/archive-tasks.sh --json
   # {"archived": ["task-1"], "failed": [], "duration_ms": 1234}
   ```

4. **Metrics Emission**: Send metrics to observability platform
   ```bash
   emit_metric "backlog.archive.count" 5
   ```

5. **Smart Filtering**: Archive by labels, assignee, priority
   ```bash
   ./scripts/bash/archive-tasks.sh --label "bug" --assignee "@engineer1"
   ```

### v3: Enterprise Features

1. **Webhook Notifications**: Notify external systems on archive
2. **S3 Archival**: Long-term storage of archived tasks
3. **Archive Retention Policy**: Auto-delete archives older than N days
4. **Multi-Repository Support**: Archive across multiple repos

---

## Appendix A: Exit Code Reference

| Exit Code | Meaning | Workflow Action | User Action |
|-----------|---------|-----------------|-------------|
| 0 | Success - Tasks archived | Continue | None |
| 1 | Validation error (CLI missing, invalid args) | Fail workflow | Install backlog CLI, fix arguments |
| 2 | No tasks to archive (informational) | Continue workflow (success) | None |
| 3 | Partial failure (some tasks failed) | Fail workflow | Review logs, retry failed tasks |

---

## Appendix B: Workflow Trigger Examples

### Manual Dispatch via GitHub UI

1. Navigate to: GitHub repo > Actions > Backlog Archive
2. Click "Run workflow" button
3. Select branch: `main`
4. Choose mode: `done` | `all` | `date`
5. Enter date (if mode=date): `2025-12-01`
6. Toggle dry run: `true` | `false`
7. Click "Run workflow"

### Scheduled Trigger (Automated)

- Runs every Sunday at midnight UTC
- Archives Done tasks only
- Commits and pushes changes automatically
- Sends notification on failure

### Commit Keyword Trigger

```bash
# Trigger via commit message
git commit -m "feat: complete feature X

archive-backlog"

git push origin main

# GitHub Actions detects keyword and runs workflow
```

---

## Appendix C: Troubleshooting Quick Reference

| Symptom | Cause | Solution |
|---------|-------|----------|
| "backlog CLI not found" | backlog.md not installed | `npm install -g backlog.md` |
| Exit code 2: "No tasks" | No tasks match filter | Normal behavior, no action needed |
| Exit code 3: Partial failure | Some tasks failed to archive | Check logs, retry failed tasks manually |
| Hook not executing | Hook not enabled or event not matched | Enable hook in hooks.yaml, verify event type |
| Workflow not triggering on keyword | Typo in commit message | Use exact keyword: `archive-backlog` |
| Workflow permission denied | Missing `contents: write` | Add permission to workflow YAML |

---

**Document Version**: 1.0
**Last Updated**: 2025-12-03
**Reviewers**: (pending)
**Approval Status**: Proposed
