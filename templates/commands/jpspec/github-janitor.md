---
description: Comprehensive git repository operations - health checks, branch management, worktree handling, cleanup, and more.
---

# /jpspec:github-janitor - Git Repository Operations

Comprehensive git repository maintenance and operations command with subcommands for all git-related tasks.

## User Input

```text
$ARGUMENTS
```

**Subcommands**:
- `status` - Repository health check (default if no subcommand)
- `prune` - Prune merged/stale branches and worktrees
- `worktree` - Manage git worktrees
- `sync` - Sync with remote repositories
- `branch` - Branch management operations
- `stash` - Stash management
- `check` - Pre-push validation checks

## Subcommand: status (default)

**Usage**: `/jpspec:github-janitor` or `/jpspec:github-janitor status`

Performs comprehensive repository health check.

### Execution Steps

**Step 1: Repository Validation**
```bash
# Verify git repository
git rev-parse --git-dir > /dev/null 2>&1 || { echo "Error: Not a git repository"; exit 1; }

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Repository: $(basename $(git rev-parse --show-toplevel))"
echo "Branch: $CURRENT_BRANCH"
```

**Step 2: Check Uncommitted Changes**
```bash
# Check for uncommitted changes
if git diff --quiet && git diff --cached --quiet; then
    echo "✓ No uncommitted changes"
else
    echo "⚠ Uncommitted changes detected"
    git status -s
fi
```

**Step 3: Check Unpushed Commits**
```bash
# Check for unpushed commits
UNPUSHED=$(git log @{u}.. --oneline 2>/dev/null | wc -l)
if [ "$UNPUSHED" -eq 0 ]; then
    echo "✓ No unpushed commits"
else
    echo "⚠ $UNPUSHED unpushed commit(s)"
    git log @{u}.. --oneline
fi
```

**Step 4: Check Rebase Status**
```bash
# Check for merge commits (should be rebased)
MERGE_COMMITS=$(git log --merges origin/main..HEAD --oneline 2>/dev/null | wc -l)
if [ "$MERGE_COMMITS" -eq 0 ]; then
    echo "✓ Branch properly rebased (no merge commits)"
else
    echo "⚠ $MERGE_COMMITS merge commit(s) found - consider rebasing"
fi
```

**Step 5: Branch Summary**
```bash
# Count branches
LOCAL_BRANCHES=$(git branch | wc -l)
MERGED_BRANCHES=$(git branch --merged main 2>/dev/null | grep -v -E '^\*|main|master|develop' | wc -l)
STALE_BRANCHES=$(git branch -vv | grep ': gone]' | wc -l)

echo ""
echo "Branches:"
echo "  Local: $LOCAL_BRANCHES"
echo "  Merged (prunable): $MERGED_BRANCHES"
echo "  Stale (upstream gone): $STALE_BRANCHES"
```

**Step 6: Worktree Summary**
```bash
# Count worktrees
WORKTREE_COUNT=$(git worktree list | wc -l)
ORPHANED=$(git worktree list --porcelain | grep -c 'prunable' || echo 0)

echo ""
echo "Worktrees:"
echo "  Active: $WORKTREE_COUNT"
echo "  Orphaned: $ORPHANED"
```

**Step 7: Generate Report**
```
GITHUB JANITOR STATUS
=====================

Repository: jp-spec-kit
Branch: feature/github-janitor
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

---

## Subcommand: prune

**Usage**: `/jpspec:github-janitor prune [--force]`

Prune merged branches and orphaned worktrees. Replaces the old `/jpspec:prune-branch` command.

### Arguments
- No arguments or `--dry-run`: Preview what would be deleted (default, safe mode)
- `--force` or `-f`: Actually delete the identified items
- `--branches-only`: Only prune branches, skip worktrees
- `--worktrees-only`: Only prune worktrees, skip branches

### Protected Branches
Never deleted: `main`, `master`, `develop`, current branch

### Execution Steps

**Step 1: Fetch and Sync**
```bash
echo "Fetching from remote..."
git fetch --prune --all
```

**Step 2: Identify Prunable Branches**
```bash
# Branches with gone upstream
GONE_BRANCHES=$(git branch -vv | grep ': gone]' | awk '{print $1}')

# Branches merged into main
MERGED_BRANCHES=$(git branch --merged main 2>/dev/null | grep -v -E '^\*|^\s*(main|master|develop)\s*$' | sed 's/^[ \t]*//')

# Combine and deduplicate
PRUNABLE_BRANCHES=$(echo -e "$GONE_BRANCHES\n$MERGED_BRANCHES" | sort -u | grep -v '^$')
```

**Step 3: Identify Orphaned Worktrees**
```bash
ORPHANED_WORKTREES=$(git worktree list --porcelain | grep -B2 'prunable' | grep 'worktree' | awk '{print $2}')
```

**Step 4: Apply Safety Filters**
```bash
CURRENT=$(git branch --show-current)
PROTECTED="main master develop $CURRENT"

# Filter out protected branches
for branch in $PRUNABLE_BRANCHES; do
    if ! echo "$PROTECTED" | grep -qw "$branch"; then
        SAFE_TO_DELETE="$SAFE_TO_DELETE $branch"
    fi
done
```

**Step 5: Execute or Preview**

Parse `$ARGUMENTS` to determine mode:

**Dry Run (default)**:
```
DRY RUN - The following would be cleaned:

Branches to prune (3):
  - feature/old-feature (upstream gone)
  - fix/completed-bug (merged into main)
  - experiment/test (upstream gone)

Worktrees to prune (1):
  - /home/user/project-old-worktree

Protected branches skipped:
  - main
  - develop

Run with --force to execute cleanup.
```

**Force Mode**:
```bash
# Delete branches
for branch in $SAFE_TO_DELETE; do
    git branch -D "$branch" && echo "Deleted: $branch"
done

# Prune worktrees
git worktree prune
```

**Step 6: Update State**
```python
from specify_cli.janitor import record_janitor_run, clear_pending_cleanup, write_audit_log

record_janitor_run(state_dir)
clear_pending_cleanup(state_dir)
write_audit_log(project_root, f"Pruned {count} branches")
```

---

## Subcommand: worktree

**Usage**: `/jpspec:github-janitor worktree <action> [args]`

Manage git worktrees for parallel development.

### Actions

#### list
```bash
# List all worktrees
git worktree list
```

#### add
```bash
# Create worktree for existing branch
git worktree add <path> <branch>

# Create worktree with new branch
git worktree add -b <new-branch> <path> <start-point>
```

**Example**:
```bash
# Create worktree for parallel feature development
git worktree add ../project-feature feature/new-feature

# Create new branch in worktree
git worktree add -b feature/experiment ../project-experiment main
```

#### remove
```bash
# Remove worktree
git worktree remove <path>

# Force remove (if dirty)
git worktree remove --force <path>
```

#### prune
```bash
# Prune orphaned worktrees
git worktree prune
```

---

## Subcommand: sync

**Usage**: `/jpspec:github-janitor sync [--rebase]`

Sync with remote repositories.

### Execution Steps

**Step 1: Fetch All Remotes**
```bash
git fetch --prune --all
```

**Step 2: Check Status**
```bash
# Commits behind
BEHIND=$(git rev-list HEAD..@{u} --count 2>/dev/null || echo 0)

# Commits ahead
AHEAD=$(git rev-list @{u}..HEAD --count 2>/dev/null || echo 0)

echo "Branch status: $AHEAD ahead, $BEHIND behind"
```

**Step 3: Sync (if --rebase)**
```bash
if [[ "$ARGUMENTS" == *"--rebase"* ]]; then
    git pull --rebase origin $(git branch --show-current)
fi
```

**Step 4: Report**
```
Remote Sync Complete
====================

Fetched from: origin
Branch: feature/github-janitor
Status: 0 ahead, 2 behind

To update: git pull --rebase origin feature/github-janitor
```

---

## Subcommand: branch

**Usage**: `/jpspec:github-janitor branch <action> [args]`

Branch management operations.

### Actions

#### list
```bash
# List with status
git branch -vv
```

#### create
```bash
# Create branch following naming convention
git checkout -b <type>/<task-id>-<description>

# Types: feature, fix, docs, refactor, test, chore
```

**Example from task**:
```bash
# For task-305 "Implement Janitor Warning System"
git checkout -b feature/task-305-janitor-warning
```

#### rename
```bash
# Rename branch
git branch -m <old-name> <new-name>

# Update remote
git push origin :<old-name> <new-name>
git push origin -u <new-name>
```

#### delete
```bash
# Delete local branch (safe - only if merged)
git branch -d <branch>

# Force delete (unmerged)
git branch -D <branch>

# Delete remote branch
git push origin --delete <branch>
```

---

## Subcommand: stash

**Usage**: `/jpspec:github-janitor stash <action> [args]`

Stash management.

### Actions

#### list
```bash
git stash list
```

#### save
```bash
# Stash with message
git stash push -m "<message>"

# Include untracked files
git stash push -u -m "<message>"
```

#### apply
```bash
# Apply most recent
git stash pop

# Apply specific
git stash apply stash@{n}
```

#### drop
```bash
# Drop specific stash
git stash drop stash@{n}

# Clear all (use with caution!)
git stash clear
```

---

## Subcommand: check

**Usage**: `/jpspec:github-janitor check`

Pre-push validation checks. Validates branch is ready for push.

### Execution Steps

**Step 1: Check Rebase Status**
```python
from specify_cli.hooks.rebase_checker import check_rebase_status, format_rebase_error

result = check_rebase_status("main")
if not result.is_rebased:
    print(format_rebase_error(result))
    print("\nFix: git rebase -i main")
    exit(1)
```

**Step 2: Load Push Rules**
```python
from specify_cli.push_rules import load_push_rules

config = load_push_rules(Path("push-rules.md"))
```

**Step 3: Run Lint (if configured)**
```bash
if [ "$LINT_REQUIRED" = "true" ]; then
    echo "Running lint..."
    eval "$LINT_COMMAND"
fi
```

**Step 4: Run Tests (if configured)**
```bash
if [ "$TEST_REQUIRED" = "true" ]; then
    echo "Running tests..."
    eval "$TEST_COMMAND"
fi
```

**Step 5: Check Branch Naming**
```bash
BRANCH=$(git branch --show-current)
PATTERN="^(feature|fix|docs|refactor|test|chore)/[a-z0-9-]+$"

if ! echo "$BRANCH" | grep -qE "$PATTERN"; then
    echo "⚠ Branch name doesn't match convention: $PATTERN"
fi
```

**Step 6: Report**
```
PRE-PUSH VALIDATION
===================

✓ Branch rebased on main (no merge commits)
✓ Lint passed
✓ Tests passed
✓ Branch naming valid

Ready to push!
```

---

## Help Text

**Command**: `/jpspec:github-janitor [subcommand] [args]`

**Purpose**: Comprehensive git repository operations - replaces `/jpspec:prune-branch` and adds many more capabilities.

**Subcommands**:

| Subcommand | Description |
|------------|-------------|
| `status` | Repository health check (default) |
| `prune` | Prune merged branches and worktrees |
| `worktree` | Manage git worktrees |
| `sync` | Sync with remote repositories |
| `branch` | Branch management operations |
| `stash` | Stash management |
| `check` | Pre-push validation checks |

**Examples**:

```bash
# Health check (default)
/jpspec:github-janitor

# Preview what would be pruned
/jpspec:github-janitor prune

# Actually prune
/jpspec:github-janitor prune --force

# Create worktree for parallel development
/jpspec:github-janitor worktree add ../project-feature feature/my-feature

# Pre-push checks
/jpspec:github-janitor check

# Sync with remote
/jpspec:github-janitor sync --rebase
```

**Migration from /jpspec:prune-branch**:
- `/jpspec:prune-branch` → `/jpspec:github-janitor prune`
- `/jpspec:prune-branch --force` → `/jpspec:github-janitor prune --force`

**See Also**:
- `.claude/agents/github-janitor.md` - Agent documentation
- `docs/guides/github-janitor.md` - User guide
- `push-rules.md` - Push rules configuration
