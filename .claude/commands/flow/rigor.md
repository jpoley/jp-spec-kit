---
description: Validate rigor rules (branch naming, worktree, backlog linkage) before implementation.
loop: inner
# Loop Classification: INNER LOOP
# This command enforces consistency conventions for implementation work.
---

## User Input

```text
$ARGUMENTS
```

## Execution Instructions

This command validates rigor rules that enforce consistency and enable automation across the team. All validations must pass before implementation can begin.

### Validation 1: Branch Naming Convention (EXEC-002)

Branch names MUST follow the pattern: `{hostname}/task-{id}/{slug-description}`

```bash
BRANCH=$(git branch --show-current 2>/dev/null)
if [ -z "$BRANCH" ]; then
  echo "[X] RIGOR VIOLATION (EXEC-002): Not on a git branch"
  echo "Fix: Create a branch following the pattern: hostname/task-NNN/slug-description"
  exit 1
fi

if ! echo "$BRANCH" | grep -Eq '^[a-z0-9-]+/task-[0-9]+/[a-z0-9-]+$'; then
  echo "[X] RIGOR VIOLATION (EXEC-002): Branch name must follow format: hostname/task-NNN/slug-description"
  echo "Current branch: $BRANCH"
  echo ""
  echo "Examples of valid branch names:"
  echo "  - macbook-pro/task-543/rigor-rules-integration"
  echo "  - desktop-alice/task-123/user-authentication"
  echo ""
  HOSTNAME=$(hostname -s | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')
  TASK_NUM=$(echo "$BRANCH" | grep -Eo 'task-[0-9]+' || echo "")
  if [ -z "$TASK_NUM" ]; then
    echo "Fix: git checkout -b ${HOSTNAME}/task-<ID>/your-feature-slug"
  else
    echo "Fix: git checkout -b ${HOSTNAME}/${TASK_NUM}/your-feature-slug"
  fi
  exit 1
fi

echo "[OK] Branch naming validation passed: $BRANCH"
```

**Why this matters**:
- **Traceability**: Branch name instantly shows which task it implements
- **Conflict Prevention**: Hostname prefix prevents naming collisions
- **Automation**: Enables automated task-to-branch linking in CI/CD

### Validation 2: Git Worktree (EXEC-001)

Implementation work MUST be done in a git worktree with matching task ID.

```bash
WORKTREE_DIR=$(git rev-parse --show-toplevel 2>/dev/null)
BRANCH=$(git branch --show-current 2>/dev/null)
GIT_DIR=$(git rev-parse --git-dir 2>/dev/null || echo "")
case "$GIT_DIR" in
  */.git/worktrees/*) IS_WORKTREE="yes" ;;
  *) IS_WORKTREE="no" ;;
esac

if [ "$IS_WORKTREE" = "no" ]; then
  echo "[X] RIGOR VIOLATION (EXEC-001): Not in a git worktree"
  echo ""
  echo "Why worktrees matter:"
  echo "  - Enable parallel feature development"
  echo "  - No branch-switching overhead"
  echo "  - Isolate dependencies and state"
  echo ""
  WORKTREE_NAME=$(basename "$BRANCH")
  echo "Fix: Create worktree:"
  echo "  cd $(git rev-parse --show-toplevel)"
  echo "  git worktree add ../${WORKTREE_NAME} ${BRANCH}"
  exit 1
fi

# Check worktree directory name contains task ID (best practice)
WORKTREE_NAME=$(basename "$WORKTREE_DIR")
TASK_ID=$(echo "$BRANCH" | grep -Eo 'task-[0-9]+' || echo "")

if [ -z "$TASK_ID" ]; then
  echo "[!] WARNING (EXEC-001): Branch does not contain task ID"
elif ! echo "$WORKTREE_NAME" | grep -q "$TASK_ID"; then
  echo "[!] WARNING (EXEC-001): Worktree name '$WORKTREE_NAME' does not contain task ID '$TASK_ID'"
else
  echo "[OK] Worktree validation passed: $WORKTREE_NAME"
fi
```

**Why this matters**:
- **Parallel Development**: Work on multiple features without branch switching
- **State Isolation**: Each worktree has independent working directory and index

### Validation 3: Backlog Task Linkage (EXEC-004)

```bash
TASK_ID=$(echo "$BRANCH" | grep -Eo 'task-[0-9]+' || echo "")

if [ -z "$TASK_ID" ]; then
  echo "[X] RIGOR VIOLATION (EXEC-004): No task ID in branch name"
  echo "All implementation work must be linked to a backlog task"
  exit 1
fi

backlog task "$TASK_ID" --plain > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "[X] RIGOR VIOLATION (EXEC-004): Backlog task not found: $TASK_ID"
  echo ""
  echo "Fix: Create the backlog task first:"
  echo "  backlog task create 'Feature description' --ac 'AC 1' --ac 'AC 2'"
  exit 1
fi

echo "[OK] Backlog task validation passed: $TASK_ID"
```

**Why this matters**:
- **No Rogue Work**: All coding aligns with planned backlog
- **Prioritization**: Work is tracked and prioritized
- **Context Preservation**: Task contains acceptance criteria and context

### Output Summary

Report validation results using the derived variables:

```bash
WORKTREE_NAME=$(basename "$WORKTREE_DIR")

echo "Rigor Rules Validation"
echo "======================"
echo "[OK] Branch naming (EXEC-002): $BRANCH"
echo "[OK] Git worktree (EXEC-001): $WORKTREE_NAME"
echo "[OK] Backlog linkage (EXEC-004): $TASK_ID"
echo ""
echo "All rigor validations passed. Ready to proceed."
```

### Composability

This command can be invoked:
- Standalone: `/flow:rigor` for manual validation
- As part of `/flow:implement` orchestration
- In pre-commit hooks for enforcement
