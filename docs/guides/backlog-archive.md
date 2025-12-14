# Backlog Archive User Guide

This guide explains how to use the `archive-tasks.sh` script to archive completed backlog tasks.

## Overview

The `archive-tasks.sh` script moves completed tasks from `backlog/tasks/` to `backlog/archive/`, keeping your active backlog clean while preserving task history.

## Quick Start

```bash
# Preview what would be archived (dry run)
./scripts/bash/archive-tasks.sh --dry-run

# Archive all Done tasks
./scripts/bash/archive-tasks.sh

# Archive tasks completed before a specific date
./scripts/bash/archive-tasks.sh --done-by 2025-12-01
```

## Installation

The script is included in the flowspec repository. No additional installation required.

**Requirements:**
- Bash 4.0+
- `backlog.md` CLI installed (`npm i -g backlog.md`)
- Tasks directory at `backlog/tasks/`

## Command Reference

```bash
./scripts/bash/archive-tasks.sh [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Show what would be archived without making changes |
| `--all`, `-a` | Archive ALL tasks regardless of status |
| `--done-by DATE` | Archive Done tasks updated on or before DATE (YYYY-MM-DD) |
| `--help`, `-h` | Show help message |

### Filtering Modes

| Mode | Command | Behavior |
|------|---------|----------|
| Default | `archive-tasks.sh` | Archive tasks with status "Done" only |
| All | `archive-tasks.sh --all` | Archive ALL tasks regardless of status |
| Date filter | `archive-tasks.sh --done-by 2025-12-01` | Archive Done tasks updated on or before date |

**Note:** `--all` and `--done-by` are mutually exclusive.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success - tasks archived |
| 1 | Validation error (CLI missing, invalid args, invalid date) |
| 2 | No tasks to archive (informational, not an error) |
| 3 | Partial failure - some tasks failed to archive |

## Examples

### Preview Changes (Dry Run)

Always preview before archiving:

```bash
./scripts/bash/archive-tasks.sh --dry-run
```

Output:
```
=== Backlog Archive (Dry Run) ===
Mode: Done tasks only

[DRY RUN] Would archive: task-001 - Setup project structure
[DRY RUN] Would archive: task-002 - Add authentication

Summary:
  Tasks to archive: 2
  (Dry run - no changes made)
```

### Archive All Done Tasks

```bash
./scripts/bash/archive-tasks.sh
```

Output:
```
=== Backlog Archive ===
Mode: Done tasks only

Archived: task-001 - Setup project structure
Archived: task-002 - Add authentication

Summary:
  Tasks archived: 2
  Failed: 0
```

### Archive by Date

Archive tasks completed before December 1st, 2025:

```bash
./scripts/bash/archive-tasks.sh --done-by 2025-12-01
```

### Archive Everything (Sprint Cleanup)

**Warning:** This archives ALL tasks including in-progress work.

```bash
./scripts/bash/archive-tasks.sh --all --dry-run  # Preview first!
./scripts/bash/archive-tasks.sh --all
```

## Automation

### GitHub Actions Workflow

Archive tasks automatically via GitHub Actions. See [Backlog Archive Workflow Guide](backlog-archive-workflow.md).

### Pre-commit Hook

Optionally run archive checks before commits. See [Backlog Archive Hook Guide](backlog-archive-hook.md).

### Cron Job

Schedule regular archiving:

```bash
# Weekly archive (Sundays at midnight)
0 0 * * 0 /path/to/project/scripts/bash/archive-tasks.sh >> /var/log/backlog-archive.log 2>&1
```

## Archive Location

Archived tasks are moved to `backlog/archive/` with their original filenames preserved:

```
backlog/
├── tasks/           # Active tasks
│   └── task-003.md
└── archive/         # Archived tasks
    ├── task-001.md
    └── task-002.md
```

## Best Practices

1. **Always dry-run first**: Preview changes before archiving
2. **Archive regularly**: Keep the active backlog manageable (weekly or bi-weekly)
3. **Use date filtering**: Archive tasks from previous sprints/milestones
4. **Commit archive changes**: Track archive operations in version control
5. **Don't archive in-progress work**: Use default mode (Done tasks only)

## Troubleshooting

For common issues and solutions, see [Backlog Archive Troubleshooting Runbook](../runbooks/backlog-archive-troubleshooting.md).

### Quick Fixes

**"backlog CLI not found"**
```bash
npm i -g backlog.md
```

**"Invalid date format"**
```bash
# Use ISO 8601 format: YYYY-MM-DD
./scripts/bash/archive-tasks.sh --done-by 2025-12-01  # Correct
./scripts/bash/archive-tasks.sh --done-by 12/01/2025  # Wrong
```

**"No tasks to archive"**
- Check tasks have status "Done"
- Use `backlog task list -s Done` to verify

## Related Documentation

- [Backlog Quick Start](backlog-quickstart.md)
- [Backlog User Guide](backlog-user-guide.md)
- [Backlog Archive Workflow](backlog-archive-workflow.md)
- [Backlog Archive Hook](backlog-archive-hook.md)
- [Troubleshooting Runbook](../runbooks/backlog-archive-troubleshooting.md)
