# SK-002: Worktree-based Feature Isolation

**Inspired by:** [spec-kitty](https://github.com/Priivacy-ai/spec-kitty) worktree strategy
**Priority:** P1 - High Impact
**Complexity:** Medium (estimated 1-2 weeks implementation)
**Dependencies:** None (uses native git features)

---

## 1. Problem Statement

Flowspec uses traditional branch-based development where developers switch branches to work on different features. This causes several problems:

**Current Pain Points:**
- Context switching requires `git checkout` or `git switch`
- Working directory changes when switching branches
- Can't easily work on multiple features simultaneously
- IDE state (open files, cursor positions) lost on branch switch
- AI agents lose context when branches change
- Merge conflicts during switch if uncommitted changes exist

**How Spec-Kitty Solves This:**
Spec-kitty creates git worktrees for each feature in `.worktrees/XXX-feature-name/`, allowing:
- Each feature has its own directory (isolated sandbox)
- No branch switching - just `cd` between directories
- Multiple AI agents can work on different features in parallel
- IDE can have multiple windows on different features
- Automatic cleanup after merge

---

## 2. Solution Overview

Add worktree-based feature isolation to flowspec's `/flow:specify` workflow. When a new feature specification is created, automatically create a git worktree for implementation.

### Key Design Decisions

#### Backlog.md Integration

**Backlog.md stays in the main repo as the single source of truth.**

Worktrees are about **git-level isolation** (code, tests, artifacts), not task management. The relationship is:

```
main-repo/
├── backlog/              # Source of truth for ALL tasks
│   └── tasks/
│       ├── task-42.md    # Feature A task
│       └── task-43.md    # Feature B task
├── .worktrees/
│   ├── 001-feature-a/    # Worktree for feature A
│   │   ├── src/          # Feature A code
│   │   ├── tests/        # Feature A tests
│   │   └── docs/prd/     # Feature A artifacts (symlink or copy)
│   └── 002-feature-b/    # Worktree for feature B
│       ├── src/          # Feature B code
│       └── ...
└── src/                  # Main branch code
```

**Task management workflow:**
1. Tasks created via `/flow:specify` go into `backlog/tasks/`
2. Developer `cd .worktrees/001-feature-a` to work on feature
3. Task status updates via `backlog task edit` (CLI works from any directory)
4. Dashboard reads from main repo's backlog (sees all tasks)

#### Worktree Lifecycle

```
/flow:specify "User authentication"
    │
    ├── 1. Create task in backlog/tasks/task-XX.md
    ├── 2. Create branch: 001-user-authentication
    ├── 3. Create worktree: .worktrees/001-user-authentication/
    ├── 4. Copy/symlink feature artifacts (spec, plan, ADRs)
    └── 5. Print: "cd .worktrees/001-user-authentication"

[Developer works in worktree]

/flow:merge (from worktree)
    │
    ├── 1. Verify all ACs complete in backlog
    ├── 2. Merge branch to main
    ├── 3. Push to remote
    ├── 4. Remove worktree
    ├── 5. Delete feature branch
    └── 6. Print: "Feature merged. You are now in main repo."
```

---

## 3. User Stories

### US-1: Automatic Worktree Creation
**As a** developer starting a new feature
**I want** a worktree created automatically during `/flow:specify`
**So that** I have an isolated workspace without manual setup

**Acceptance Criteria:**
- [ ] `/flow:specify` creates worktree in `.worktrees/{num}-{slug}/`
- [ ] Feature number auto-incremented (001, 002, 003...)
- [ ] Worktree on feature branch matching slug
- [ ] Clear instruction to `cd` into worktree printed
- [ ] Works with or without existing git history

### US-2: Work in Isolation
**As a** developer implementing a feature
**I want** my worktree isolated from other features
**So that** I can work without affecting other work-in-progress

**Acceptance Criteria:**
- [ ] Each worktree has its own working directory
- [ ] Changes in one worktree don't affect others
- [ ] Can run builds/tests independently per worktree
- [ ] IDE can open worktree as separate project

### US-3: Parallel Feature Development
**As a** team using multiple AI agents
**I want** multiple worktrees for different features
**So that** agents can work in parallel without conflicts

**Acceptance Criteria:**
- [ ] Multiple worktrees can exist simultaneously
- [ ] Each worktree tracks its own feature branch
- [ ] Dashboard shows all features across worktrees
- [ ] Backlog tasks accessible from any worktree

### US-4: Clean Merge and Cleanup
**As a** developer finishing a feature
**I want** automatic cleanup after merge
**So that** worktrees don't accumulate over time

**Acceptance Criteria:**
- [ ] `/flow:merge` command handles full lifecycle
- [ ] Worktree removed after successful merge
- [ ] Feature branch deleted after merge
- [ ] User returned to main repo root
- [ ] `--keep-worktree` flag to preserve if needed

### US-5: Backlog Access from Worktree
**As a** developer in a worktree
**I want** to update task status in the shared backlog
**So that** progress is tracked centrally

**Acceptance Criteria:**
- [ ] `backlog task edit` works from worktree directory
- [ ] Task changes reflect in main repo's backlog
- [ ] Dashboard updates show worktree task progress
- [ ] No duplicate tasks created

### US-6: Skip Worktree Option
**As a** developer preferring branch-based workflow
**I want** to opt out of worktree creation
**So that** I can use traditional branch switching

**Acceptance Criteria:**
- [ ] `--no-worktree` flag skips worktree creation
- [ ] Falls back to branch creation only
- [ ] Workflow continues normally without worktree
- [ ] User preference stored in config

---

## 4. Technical Design

### 4.1 Directory Structure

```
project-root/                      # Main repo (always on main branch)
├── .worktrees/                    # Worktree container (gitignored)
│   ├── 001-user-auth/             # Feature 1 worktree
│   │   ├── .git                   # Git worktree link file
│   │   ├── src/                   # Feature 1 source code
│   │   ├── tests/                 # Feature 1 tests
│   │   ├── docs/                  # Feature artifacts (symlink or copy)
│   │   │   └── prd/
│   │   │       └── user-auth.md   # This feature's PRD
│   │   └── backlog -> ../../backlog  # Symlink to shared backlog
│   │
│   └── 002-dashboard/             # Feature 2 worktree
│       ├── .git
│       ├── src/
│       ├── tests/
│       ├── docs/
│       └── backlog -> ../../backlog
│
├── backlog/                       # Shared task management (NOT in worktree)
│   ├── tasks/
│   │   ├── task-101.md            # Feature 1 tasks
│   │   ├── task-102.md
│   │   ├── task-103.md            # Feature 2 tasks
│   │   └── task-104.md
│   └── archive/
│
├── docs/                          # Main repo docs
│   ├── prd/                       # All PRDs (main copy)
│   └── adr/                       # All ADRs
│
├── src/                           # Main branch source
├── tests/                         # Main branch tests
├── flowspec_workflow.yml          # Workflow config
└── .gitignore                     # Includes .worktrees/
```

### 4.2 Git Worktree Commands

```bash
# Create worktree with new branch
git worktree add .worktrees/001-feature-name -b 001-feature-name

# List worktrees
git worktree list

# Remove worktree (after merge)
git worktree remove .worktrees/001-feature-name

# Prune stale worktrees
git worktree prune
```

### 4.3 Implementation: create_feature_worktree()

```python
# src/specify_cli/worktree/manager.py

from pathlib import Path
import subprocess
import re
from typing import Tuple, Optional

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug[:50]  # Limit length

def get_next_feature_number(project_dir: Path) -> int:
    """Get next feature number by scanning existing worktrees."""
    worktrees_dir = project_dir / ".worktrees"
    if not worktrees_dir.exists():
        return 1

    highest = 0
    for item in worktrees_dir.iterdir():
        if item.is_dir():
            match = re.match(r'^(\d+)-', item.name)
            if match:
                num = int(match.group(1))
                highest = max(highest, num)

    return highest + 1

def create_feature_worktree(
    project_dir: Path,
    feature_name: str,
    create_worktree: bool = True,
) -> Tuple[str, Optional[Path]]:
    """
    Create a feature branch and optional worktree.

    Returns:
        Tuple of (branch_name, worktree_path or None)
    """
    # Generate branch name
    feature_num = get_next_feature_number(project_dir)
    slug = slugify(feature_name)
    branch_name = f"{feature_num:03d}-{slug}"

    if not create_worktree:
        # Traditional branch-only mode
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=project_dir,
            check=True
        )
        return branch_name, None

    # Create worktree
    worktrees_dir = project_dir / ".worktrees"
    worktrees_dir.mkdir(exist_ok=True)

    worktree_path = worktrees_dir / branch_name

    # Check if worktree already exists
    if worktree_path.exists():
        # Reuse existing worktree
        return branch_name, worktree_path

    # Create new worktree with branch
    result = subprocess.run(
        ["git", "worktree", "add", str(worktree_path), "-b", branch_name],
        cwd=project_dir,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        # Fall back to branch-only if worktree fails
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=project_dir,
            check=True
        )
        return branch_name, None

    # Create backlog symlink in worktree
    backlog_link = worktree_path / "backlog"
    if not backlog_link.exists():
        backlog_source = project_dir / "backlog"
        if backlog_source.exists():
            backlog_link.symlink_to(backlog_source.resolve())

    return branch_name, worktree_path

def remove_feature_worktree(
    project_dir: Path,
    branch_name: str,
    delete_branch: bool = True
) -> bool:
    """
    Remove a feature worktree and optionally delete the branch.

    Returns:
        True if successful
    """
    worktree_path = project_dir / ".worktrees" / branch_name

    if worktree_path.exists():
        subprocess.run(
            ["git", "worktree", "remove", str(worktree_path)],
            cwd=project_dir,
            check=True
        )

    if delete_branch:
        subprocess.run(
            ["git", "branch", "-d", branch_name],
            cwd=project_dir,
            check=False  # May fail if not fully merged
        )

    return True
```

### 4.4 Integration with /flow:specify

Modify `/flow:specify` command to use worktree:

```python
# In specify command implementation

from ..worktree.manager import create_feature_worktree

def specify_command(feature_description: str, no_worktree: bool = False):
    project_dir = Path.cwd()

    # ... existing specify logic (create PRD, tasks) ...

    # Create worktree
    branch_name, worktree_path = create_feature_worktree(
        project_dir=project_dir,
        feature_name=feature_description,
        create_worktree=not no_worktree
    )

    if worktree_path:
        print(f"\n{'='*60}")
        print("NEXT STEP (REQUIRED):")
        print(f"  cd \"{worktree_path}\"")
        print("")
        print("Then continue with:")
        print("  /flow:plan")
        print(f"{'='*60}\n")
    else:
        print(f"\nCreated branch: {branch_name}")
        print("Continue with: /flow:plan")
```

### 4.5 Integration with /flow:merge

Create new `/flow:merge` command:

```markdown
---
description: Merge completed feature to main and cleanup worktree
---

# /flow:merge

Merge the current feature branch to main and cleanup resources.

## Prerequisites

- All acceptance criteria in backlog tasks must be complete
- Tests must pass
- Current directory must be in a feature worktree or branch

## Actions

1. **Verify completion**
   - Check all tasks for this feature have status "Done"
   - Verify no unchecked acceptance criteria

2. **Merge to main**
   - Switch to main branch
   - Pull latest changes
   - Merge feature branch (default: merge commit)
   - Push to remote (if --push specified)

3. **Cleanup**
   - Remove worktree directory
   - Delete feature branch
   - Return to main repo root

## Options

- `--strategy <merge|squash|rebase>` - Merge strategy (default: merge)
- `--push` - Push to remote after merge
- `--keep-worktree` - Don't remove worktree after merge
- `--keep-branch` - Don't delete feature branch
- `--dry-run` - Show what would happen without executing

## Usage

```bash
# From worktree: .worktrees/001-user-auth/
/flow:merge --push

# Squash commits
/flow:merge --strategy squash --push

# Keep worktree for reference
/flow:merge --keep-worktree --push
```
```

### 4.6 Backlog CLI from Worktree

The backlog CLI should work from any directory. It finds the project root by searching up for `backlog/` directory or `.git`:

```python
# In backlog CLI

def find_project_root() -> Path:
    """Find project root from current directory."""
    current = Path.cwd()

    while current != current.parent:
        # Check for backlog directory
        if (current / "backlog" / "tasks").exists():
            return current

        # Check for main git repo (not worktree .git file)
        git_path = current / ".git"
        if git_path.is_dir():  # Real .git directory, not worktree link
            return current

        # Follow worktree link to main repo
        if git_path.is_file():
            # This is a worktree, backlog is symlinked
            backlog_link = current / "backlog"
            if backlog_link.is_symlink():
                return backlog_link.resolve().parent

        current = current.parent

    raise RuntimeError("Could not find project root with backlog/")
```

---

## 5. User Experience Flow

### Creating a Feature

```
$ cd my-project

$ claude
> /flow:specify "Add user authentication with OAuth"

Creating feature specification...
- Branch: 001-add-user-authentication-with-oauth
- PRD: docs/prd/user-authentication.md
- Tasks: backlog/tasks/task-42.md, task-43.md, task-44.md

Worktree created at: .worktrees/001-add-user-authentication-with-oauth

============================================================
NEXT STEP (REQUIRED):
  cd ".worktrees/001-add-user-authentication-with-oauth"

Then continue with:
  /flow:plan
============================================================

$ cd .worktrees/001-add-user-authentication-with-oauth
$ claude
> /flow:plan
...
```

### Working in Parallel

```
# Terminal 1: Working on auth feature
$ cd .worktrees/001-user-auth
$ claude
> /flow:implement

# Terminal 2: Working on dashboard feature
$ cd .worktrees/002-dashboard
$ cursor
> /flow:implement

# Both update the shared backlog
$ backlog task edit task-42 --check-ac 1
$ backlog task edit task-45 -s "In Implementation"
```

### Merging a Feature

```
$ cd .worktrees/001-user-auth

$ claude
> /flow:merge --push

Verifying feature completion...
✓ All tasks complete (3/3)
✓ All acceptance criteria checked (8/8)

Merging to main...
✓ Switched to main branch
✓ Pulled latest changes
✓ Merged 001-add-user-authentication-with-oauth
✓ Pushed to origin

Cleaning up...
✓ Removed worktree
✓ Deleted feature branch

You are now in: /path/to/my-project (main branch)
```

---

## 6. Configuration

### User Preferences

Add to `.specify/config.yml`:

```yaml
worktree:
  enabled: true                    # Create worktrees by default
  directory: ".worktrees"          # Worktree container directory
  backlog_symlink: true            # Symlink backlog into worktrees
  cleanup_on_merge: true           # Remove worktree after merge
  delete_branch_on_merge: true     # Delete feature branch after merge
```

### .gitignore Addition

```gitignore
# Worktrees (created by flowspec, not tracked)
.worktrees/
```

---

## 7. Edge Cases & Error Handling

### Worktree Creation Fails
- Git version too old (< 2.5)
- Disk space issues
- Permission problems

**Mitigation:** Fall back to branch-only mode with warning.

### Uncommitted Changes During Merge
- User has uncommitted work in worktree

**Mitigation:** Block merge with clear error message.

### Worktree Already Exists
- Feature number collision

**Mitigation:** Reuse existing worktree with warning.

### Remote Branch Exists
- Branch pushed by another developer

**Mitigation:** Checkout existing branch, warn about potential conflicts.

---

## 8. Implementation Plan

### Phase 1: Core Worktree Manager (Week 1)
1. Create `src/specify_cli/worktree/` module
2. Implement `create_feature_worktree()`
3. Implement `remove_feature_worktree()`
4. Add feature numbering logic
5. Unit tests for worktree operations

### Phase 2: Command Integration (Week 1-2)
1. Modify `/flow:specify` to create worktrees
2. Create `/flow:merge` command
3. Add `--no-worktree` flag
4. Add backlog symlink creation
5. Integration tests

### Phase 3: Polish
1. Configuration support
2. Error handling and edge cases
3. Documentation updates
4. Update CLAUDE.md with worktree workflow

---

## 9. Success Metrics

| Metric | Target |
|--------|--------|
| Worktree creation time | < 2 seconds |
| Merge + cleanup time | < 5 seconds |
| No regressions in existing workflow | 100% |
| User adoption (opt-in initially) | Track via telemetry |

---

## 10. References

- [Git Worktree Documentation](https://git-scm.com/docs/git-worktree)
- [spec-kitty create-new-feature.sh](https://github.com/Priivacy-ai/spec-kitty/blob/main/scripts/bash/create-new-feature.sh)
- [spec-kitty merge-feature.sh](https://github.com/Priivacy-ai/spec-kitty/blob/main/scripts/bash/merge-feature.sh)
