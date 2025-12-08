# GitHub Janitor Guide

The GitHub Janitor is a comprehensive git repository operations tool that handles all git-related maintenance tasks. It replaces the old `/jpspec:prune-branch` command and adds many more capabilities.

## Quick Start

```bash
# Check repository health (default)
/jpspec:github-janitor

# Preview what would be cleaned
/jpspec:github-janitor prune

# Actually clean up
/jpspec:github-janitor prune --force

# Pre-push validation
/jpspec:github-janitor check
```

## Migration from prune-branch

If you were using `/jpspec:prune-branch`, here's how to migrate:

| Old Command | New Command |
|-------------|-------------|
| `/jpspec:prune-branch` | `/jpspec:github-janitor prune` |
| `/jpspec:prune-branch --force` | `/jpspec:github-janitor prune --force` |
| `/jpspec:prune-branch --dry-run` | `/jpspec:github-janitor prune` |

## Subcommands

### status (default)

Performs a comprehensive repository health check.

```bash
/jpspec:github-janitor
# or
/jpspec:github-janitor status
```

**Output**:
```
GITHUB JANITOR STATUS
=====================

Repository: jp-spec-kit
Branch: feature/my-feature
Status: Clean ✓

Health Checks:
  ✓ No uncommitted changes
  ✓ No unpushed commits
  ✓ Branch properly rebased
  ✓ Git configuration valid

Branches:
  Local: 5
  Merged (prunable): 2
  Stale (upstream gone): 1

Worktrees:
  Active: 1
  Orphaned: 0

Recommendations:
  - Run `/jpspec:github-janitor prune` to clean up 3 branches
```

### prune

Prune merged branches and orphaned worktrees.

```bash
# Preview (safe mode, default)
/jpspec:github-janitor prune

# Execute cleanup
/jpspec:github-janitor prune --force

# Only prune branches
/jpspec:github-janitor prune --branches-only

# Only prune worktrees
/jpspec:github-janitor prune --worktrees-only
```

**Protected branches** (never deleted):
- `main`
- `master`
- `develop`
- The currently checked out branch

### worktree

Manage git worktrees for parallel development.

```bash
# List worktrees
/jpspec:github-janitor worktree list

# Create worktree for existing branch
/jpspec:github-janitor worktree add ../project-feature feature/my-feature

# Create worktree with new branch
/jpspec:github-janitor worktree add -b feature/new ../project-new main

# Remove worktree
/jpspec:github-janitor worktree remove ../project-feature

# Prune orphaned worktrees
/jpspec:github-janitor worktree prune
```

**Use Case**: Working on multiple features simultaneously without switching branches.

### sync

Sync with remote repositories.

```bash
# Fetch and show status
/jpspec:github-janitor sync

# Fetch and rebase
/jpspec:github-janitor sync --rebase
```

**Output**:
```
Remote Sync Complete
====================

Fetched from: origin
Branch: feature/my-feature
Status: 0 ahead, 2 behind

To update: git pull --rebase origin feature/my-feature
```

### branch

Branch management operations.

```bash
# List branches with status
/jpspec:github-janitor branch list

# Create branch from task (follows naming convention)
/jpspec:github-janitor branch create feature/task-123-my-feature

# Rename branch
/jpspec:github-janitor branch rename old-name new-name

# Delete branch (safe)
/jpspec:github-janitor branch delete my-branch

# Force delete (unmerged)
/jpspec:github-janitor branch delete --force my-branch
```

**Naming Convention**: `<type>/<task-id>-<description>`

Types: `feature`, `fix`, `docs`, `refactor`, `test`, `chore`

### stash

Stash management.

```bash
# List stashes
/jpspec:github-janitor stash list

# Save current changes
/jpspec:github-janitor stash save "WIP: my changes"

# Save including untracked files
/jpspec:github-janitor stash save -u "WIP: with untracked"

# Apply most recent stash
/jpspec:github-janitor stash apply

# Drop specific stash
/jpspec:github-janitor stash drop 0
```

### check

Pre-push validation checks.

```bash
/jpspec:github-janitor check
```

**Validates**:
1. Branch is rebased on main (no merge commits)
2. Lint passes (if configured in push-rules.md)
3. Tests pass (if configured in push-rules.md)
4. Branch naming matches convention

**Output**:
```
PRE-PUSH VALIDATION
===================

✓ Branch rebased on main (no merge commits)
✓ Lint passed
✓ Tests passed
✓ Branch naming valid

Ready to push!
```

## Integration with /jpspec:validate

The github-janitor runs automatically as **Phase 7** in `/jpspec:validate`:

1. Phases 0-6 complete (testing, validation, PR creation)
2. **Phase 7**: GitHub Janitor
   - Performs repository health check
   - Identifies cleanup candidates
   - Updates state files
   - Reports findings (dry-run by default)

## Session Warnings

When you start a Claude Code session, the session-start hook checks for pending cleanup:

```
Environment Warnings:
  ⚠ Repository cleanup pending: 2 branch(es) to prune
  ⚠   Run '/jpspec:github-janitor prune' to clean up
```

This warning clears after running `/jpspec:github-janitor prune --force`.

## State Files

GitHub Janitor maintains state in `.specify/state/`:

| File | Purpose |
|------|---------|
| `janitor-last-run` | ISO timestamp of last successful run |
| `pending-cleanup.json` | Items identified for cleanup |

These files are automatically added to `.gitignore` during `specify init`.

## Configuration

Configure janitor behavior in `push-rules.md`:

```yaml
janitor_settings:
  run_after_validation: true      # Run in Phase 7 of validate
  prune_merged_branches: true     # Auto-prune merged branches
  clean_stale_worktrees: true     # Auto-clean orphaned worktrees
  protected_branches:
    - main
    - master
    - develop
```

## Safety Principles

1. **Protected branches are NEVER deleted** (main, master, develop)
2. **Current branch is NEVER deleted**
3. **Dry-run is the default** - must use `--force` for destructive actions
4. **All operations are logged** to `.specify/audit.log`
5. **Force push to main/master requires explicit confirmation**

## Audit Logging

All janitor operations are logged:

```
[2025-12-07T21:30:00Z] JANITOR: Pruned 3 branches, cleaned 1 worktree
[2025-12-07T21:30:00Z] JANITOR: Branches: feature/old, fix/done, experiment/test
```

View the audit log:
```bash
cat .specify/audit.log
```

## Troubleshooting

### "Not a git repository"

You're not in a git repository. Run from project root or initialize with `git init`.

### "No remote configured"

Remote-dependent operations will be skipped. Add a remote:
```bash
git remote add origin <url>
```

### "Branch deletion failed"

The branch may have unmerged changes. Use `--force` if you're sure:
```bash
/jpspec:github-janitor prune --force
```

### Worktree locked

Another process is using the worktree. Check running processes or force remove:
```bash
/jpspec:github-janitor worktree remove --force <path>
```

## See Also

- [Push Rules Configuration](push-rules-configuration.md)
- [Workflow State Mapping](workflow-state-mapping.md)
- `/jpspec:validate` - Validation workflow with Phase 7 janitor
