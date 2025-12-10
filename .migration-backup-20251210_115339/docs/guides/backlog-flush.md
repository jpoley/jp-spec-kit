# Backlog Flush Guide

Archive completed tasks and generate summary reports to keep your backlog clean and maintain a historical record of work done.

## Overview

The **backlog flush** feature moves all tasks with status "Done" to an archive directory and generates a timestamped summary report. This helps:

- Keep your active backlog focused on current work
- Maintain a historical record of completed tasks
- Generate sprint/release summaries automatically
- Reduce clutter in your task board

## Ways to Flush Your Backlog

### 1. Manual CLI Execution (Recommended)

Run the flush script directly from your terminal:

```bash
# Preview what would be archived (no changes made)
./scripts/bash/flush-backlog.sh --dry-run

# Archive all Done tasks and generate summary
./scripts/bash/flush-backlog.sh

# Archive without generating a summary report
./scripts/bash/flush-backlog.sh --no-summary

# Archive and automatically commit changes to Git
./scripts/bash/flush-backlog.sh --auto-commit
```

**Windows users** can use the PowerShell equivalent:

```powershell
# Preview what would be archived
.\scripts\powershell\Flush-Backlog.ps1 -DryRun

# Archive all Done tasks
.\scripts\powershell\Flush-Backlog.ps1

# Archive without summary
.\scripts\powershell\Flush-Backlog.ps1 -NoSummary

# Archive and auto-commit
.\scripts\powershell\Flush-Backlog.ps1 -AutoCommit
```

### 2. Automated via GitHub Actions

Include `flush-backlog` in your commit message to trigger automatic archival:

```bash
git commit -m "feat: complete user authentication flush-backlog"
git push origin main
```

The workflow will:
1. Detect the `flush-backlog` keyword in the commit message
2. Run the flush script automatically
3. Commit and push the archived tasks and summary

**Note**: This only triggers on pushes to the `main` branch.

### 3. Using backlog.md CLI Directly

Archive individual tasks using the built-in CLI:

```bash
# Archive a single task by ID
backlog task archive 42

# View archived tasks
ls backlog/archive/tasks/
```

## Command Reference

### Bash Script Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Show what would be archived without making changes |
| `--no-summary` | Skip generating the flush summary report |
| `--auto-commit` | Automatically commit changes after flushing |
| `--help` | Display help information |

### PowerShell Script Options

| Option | Description |
|--------|-------------|
| `-DryRun` | Show what would be archived without making changes |
| `-NoSummary` | Skip generating the flush summary report |
| `-AutoCommit` | Automatically commit changes after flushing |
| `-Help` | Display help information |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - tasks archived |
| 1 | Validation error - backlog CLI not installed |
| 2 | No tasks to archive - no Done tasks found |
| 3 | Partial failure - some tasks failed to archive |

## Output Structure

### Archived Tasks

Archived tasks are moved to:
```
backlog/archive/tasks/task-{id} - {title}.md
```

The task files retain all their original content and metadata.

### Flush Summary

Each flush generates a timestamped summary at:
```
backlog/archive/flush-YYYY-MM-DD-HHMMSS.md
```

Example summary content:

```markdown
# Backlog Flush Summary

**Date:** 2025-11-26 12:34:10
**Archived Tasks:** 5
**Trigger Source:** manual

---

## Archived Tasks

### task-69: Implement-core-flush-backlog.sh-script

- **Priority:** high
- **Assignee:** None
- **Labels:** backend, script, bash
- **Acceptance Criteria:** 6/6 completed

### task-70: Implement-flush-summary-report-generation

- **Priority:** high
- **Assignee:** None
- **Labels:** backend, script, documentation
- **Acceptance Criteria:** 4/5 completed

---

## Statistics

### Total Archived
- **Count:** 5

### By Priority
- **High:** 3
- **Medium:** 1
- **Low:** 1

### Common Labels
- **backend:** 3
- **script:** 2
```

## Prerequisites

Before running the flush script, ensure:

1. **backlog.md CLI is installed**:
   ```bash
   npm install -g @backlog-md/cli
   # or
   pnpm add -g @backlog-md/cli
   ```

2. **You're in a project with backlog initialized**:
   ```bash
   # Check if backlog directory exists
   ls backlog/
   ```

3. **Tasks are marked as Done**:
   ```bash
   # View Done tasks
   backlog task list -s Done --plain
   ```

## Workflow Examples

### Sprint Cleanup

At the end of a sprint, archive all completed work:

```bash
# Review what will be archived
./scripts/bash/flush-backlog.sh --dry-run

# Archive and commit with a sprint marker
./scripts/bash/flush-backlog.sh --auto-commit
git tag sprint-23-complete
git push origin main --tags
```

### Release Documentation

Generate a summary of completed features for release notes:

```bash
# Flush and review the generated summary
./scripts/bash/flush-backlog.sh

# The summary at backlog/archive/flush-*.md can be used
# as a basis for release notes
```

### CI/CD Integration

Trigger automatic archival in your deployment pipeline:

```bash
# In your release script or CI config
git commit -m "release: v1.2.0 flush-backlog"
git push origin main
```

## Troubleshooting

### "backlog CLI not found"

Install the backlog.md CLI:
```bash
npm install -g @backlog-md/cli
```

### "No Done tasks to archive"

Verify you have tasks with status "Done":
```bash
backlog task list -s Done --plain
```

If tasks show as done on the board but aren't archiving, check the status field in the task file matches exactly "Done" (case-sensitive).

### "Permission denied" on script

Make the script executable:
```bash
chmod +x scripts/bash/flush-backlog.sh
```

### GitHub Actions not triggering

Ensure:
1. You're pushing to `main` branch (not a feature branch)
2. The commit message contains `flush-backlog` (case-insensitive)
3. The workflow file exists at `.github/workflows/backlog-flush.yml`

### Partial failures

If some tasks fail to archive (exit code 3):
1. Check the error output for specific task IDs
2. Verify those tasks exist and have status "Done"
3. Try archiving them individually: `backlog task archive {id}`

## Related Documentation

- [Backlog Quick Start](backlog-quickstart.md) - Getting started with backlog.md
- [Backlog User Guide](backlog-user-guide.md) - Complete task management guide
- [Backlog Troubleshooting](backlog-troubleshooting.md) - Common issues and solutions
