---
description: Prune local branches that have been merged and deleted on remote.
---

## User Input

```text
$ARGUMENTS
```

## Execution Instructions

This command safely prunes local Git branches that have been merged and deleted on remote. It helps keep your local repository clean by removing stale branches.

### Arguments

- No arguments or `--dry-run`: Preview branches to be deleted (default, safe mode)
- `--force` or `-f`: Actually delete the identified branches

### Protected Branches

The following branches are never deleted:
- `main`
- `master`
- `develop`
- The currently checked out branch

### Execution Steps

**Step 1: Validate Git Repository**

First, verify we're in a git repository with a remote configured:

```bash
# Check if in git repo
git rev-parse --git-dir > /dev/null 2>&1

# Check if remote exists
git remote -v
```

If not in a git repo or no remote configured, output an error message and stop.

**Step 2: Fetch from Remote with Prune**

Sync local tracking info with remote:

```bash
git fetch --prune --all
```

This updates remote tracking branches and removes references to branches deleted on remote.

**Step 3: Identify Branches to Prune**

Identify local branches that should be pruned:

1. **Gone branches**: Local branches whose upstream tracking branch no longer exists on remote:
```bash
git branch -vv | grep ': gone]' | awk '{print $1}'
```

2. **Merged branches**: Local branches fully merged into main/master (excluding protected branches):
```bash
git branch --merged main 2>/dev/null | grep -v -E '^\*|^\s*(main|master|develop)\s*$' | sed 's/^[ \t]*//'
```

**Step 4: Apply Safety Checks**

Before proceeding:
1. Get the current branch name: `git branch --show-current`
2. Filter out protected branches (main, master, develop)
3. Filter out the current branch
4. Deduplicate the list (a branch might be both "gone" and "merged")

**Step 5: Preview or Delete**

Parse `$ARGUMENTS` to determine mode:

- If `$ARGUMENTS` is empty, `--dry-run`, or doesn't contain `--force`/`-f`:
  - Output: "**DRY RUN** - The following branches would be deleted:"
  - List each branch with reason (gone/merged)
  - Output: "Run with `--force` to delete these branches."

- If `$ARGUMENTS` contains `--force` or `-f`:
  - For each branch to prune:
    ```bash
    git branch -D <branch-name>
    ```
  - Output success/failure for each branch

**Step 6: Output Summary**

Provide a clear summary:
- Number of branches deleted (or would be deleted in dry-run)
- Number of branches skipped with reasons
- Any errors encountered

### Example Output

**Dry Run Mode:**
```
Fetching from remote...
Done.

Analyzing local branches...

DRY RUN - The following branches would be deleted:

  - feature/old-feature (reason: upstream gone)
  - bugfix/fixed-issue (reason: merged into main)
  - experiment/test (reason: upstream gone)

Protected branches skipped:
  - main
  - develop

Summary: 3 branches would be pruned, 2 protected branches skipped.

Run with --force to delete these branches.
```

**Force Mode:**
```
Fetching from remote...
Done.

Pruning branches...

  Deleted: feature/old-feature (upstream gone)
  Deleted: bugfix/fixed-issue (merged into main)
  Deleted: experiment/test (upstream gone)

Summary: 3 branches pruned successfully.
```

**No Branches to Prune:**
```
Fetching from remote...
Done.

Analyzing local branches...

No branches to prune. Your local repository is clean!
```

### Error Handling

- **Not a git repository**: "Error: Not in a git repository. Please run this command from within a git project."
- **No remote configured**: "Error: No git remote configured. Please add a remote first."
- **Current branch would be pruned**: "Warning: Cannot delete the currently checked out branch '<branch>'. Switch to another branch first."
- **Branch deletion failed**: "Error: Failed to delete branch '<branch>': <error message>"

### Implementation Notes

Execute the git commands directly using the Bash tool. Process the output to build the lists of branches, apply safety filters, and format the output clearly for the user.
