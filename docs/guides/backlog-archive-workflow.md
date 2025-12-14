# Backlog Archive GitHub Actions Workflow Guide

This guide explains how to use the GitHub Actions workflow for automated backlog archiving.

## Overview

The `backlog-archive.yml` workflow provides three trigger modes for archiving tasks:

1. **Manual dispatch** - Run on demand via GitHub UI
2. **Scheduled** - Weekly automatic archiving (Sundays at midnight UTC)
3. **Commit keyword** - Trigger via commit message

## Workflow Location

`.github/workflows/backlog-archive.yml`

## Trigger Modes

### 1. Manual Dispatch (workflow_dispatch)

Run the workflow manually from GitHub Actions UI with customizable options.

**Steps:**
1. Go to repository → Actions → "Backlog Archive"
2. Click "Run workflow"
3. Select options:
   - **Mode**: `done` (default), `all`, or `date`
   - **Done by date**: Date filter (YYYY-MM-DD) when mode is `date`
   - **Dry run**: Preview only, no changes

**Example configurations:**

| Scenario | Mode | Done by date | Dry run |
|----------|------|--------------|---------|
| Archive completed tasks | done | (empty) | false |
| Preview before archiving | done | (empty) | true |
| Archive tasks before Dec 1 | date | 2025-12-01 | false |
| Archive everything (cleanup) | all | (empty) | false |

### 2. Scheduled (cron)

The workflow runs automatically every Sunday at midnight UTC.

**Schedule:** `0 0 * * 0` (weekly on Sundays)

**Behavior:**
- Archives Done tasks only (mode: done)
- Not a dry run (changes are committed)
- Commits as `github-actions[bot]`

### 3. Commit Keyword (push)

Trigger the workflow by including a keyword in your commit message.

**Keywords (case variations supported):**
- `archive-backlog`
- `Archive Backlog`
- `ARCHIVE-BACKLOG`

**Example:**
```bash
git commit -m "chore: cleanup sprint tasks archive-backlog"
git push
```

**Behavior:**
- Archives Done tasks only
- Runs on push to main branch
- Commits results automatically

## Workflow Steps

1. **Checkout repository** - Full history for accurate dates
2. **Setup Node.js** - Node.js 20 environment
3. **Install backlog CLI** - `npm install -g backlog.md`
4. **Determine parameters** - Based on trigger type
5. **Run archive script** - Execute `archive-tasks.sh`
6. **Commit and push** - If changes made and not dry-run
7. **Generate job summary** - Markdown summary in Actions UI

## Viewing Results

### Job Summary

After the workflow runs, view the summary in GitHub Actions:

1. Go to Actions → workflow run
2. Click on the job
3. Scroll to "Job Summary" section

The summary includes:
- Trigger source
- Archive mode
- Dry run status
- Archive output

### Commit History

Archive commits appear with format:
```
chore(backlog): archive tasks [<trigger source>]

Triggered by: <trigger source>
Mode: <done|all|date>
Status: <success|partial>
```

## Exit Code Handling

| Exit Code | Workflow Status | Meaning |
|-----------|-----------------|---------|
| 0 | Success | Tasks archived |
| 2 | Success | No tasks to archive (not an error) |
| 1, 3 | Failure | Error during archiving |

## Permissions

The workflow requires:
- `contents: write` - To commit archive changes

Uses `GITHUB_TOKEN` for authentication (automatically provided).

## Customization

### Change Schedule

Edit the cron expression in `.github/workflows/backlog-archive.yml`:

```yaml
schedule:
  - cron: '0 0 * * 0'  # Current: Sundays at midnight UTC
  # Examples:
  # - cron: '0 0 * * 5'  # Fridays at midnight
  # - cron: '0 0 1 * *'  # 1st of each month
  # - cron: '0 9 * * 1'  # Mondays at 9 AM UTC
```

### Change Default Mode

Edit the `inputs.mode.default` value:

```yaml
inputs:
  mode:
    default: 'done'  # Change to 'all' or 'date'
```

### Add Notification

Add a step after archiving to send notifications:

```yaml
- name: Notify on Slack
  if: steps.archive.outputs.has_changes == 'true'
  uses: slackapi/slack-github-action@v1
  with:
    channel-id: 'your-channel'
    slack-message: 'Backlog archived: ${{ steps.archive.outputs.message }}'
```

## Best Practices

1. **Use dry-run first**: Test manual dispatch with dry-run before production runs
2. **Monitor scheduled runs**: Check weekly workflow runs for failures
3. **Don't commit during archiving**: Avoid commits while workflow is running
4. **Review archive commits**: Periodically check what's being archived

## Troubleshooting

See [Backlog Archive Troubleshooting Runbook](../runbooks/backlog-archive-troubleshooting.md) for common issues.

### Quick Checks

**Workflow not triggering:**
- Check workflow is enabled (Actions → workflow → Enable)
- Verify branch is `main`
- Check commit keyword spelling

**Scheduled run didn't execute:**
- GitHub may delay or skip scheduled runs on inactive repos
- Check Actions → "Scheduled" filter for run history

**Commit keyword ignored:**
- Must be on `main` branch
- Check exact keyword match (case variations supported)

## Related Documentation

- [Backlog Archive User Guide](backlog-archive.md)
- [Backlog Archive Hook Guide](backlog-archive-hook.md)
- [Troubleshooting Runbook](../runbooks/backlog-archive-troubleshooting.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
