# Git Workflow Rules

Rules for commits, branches, and PRs.

## No Direct Commits to Main

**NEVER commit directly to main.** All changes go through PRs:

1. Create branch
2. Make changes
3. Run lint + tests locally
4. Create PR
5. CI passes
6. Merge
7. Mark task Done

No exceptions for "urgent" or "small" changes.

## Branch Naming

Pattern: `{hostname}/task-{id}/{slug-description}`

Examples:
- `macbook-pro/task-541/rigor-rules-include`
- `desktop-alice/task-123/user-authentication`
- If your raw hostname is `Alice-MBP 01`, it will be sanitized to `alice-mbp-01`, so the branch would be `alice-mbp-01/task-123/add-feature`.

```bash
HOSTNAME=$(hostname -s | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')
git checkout -b "${HOSTNAME}/task-123/add-feature"
```

## Git Worktrees

Work in worktrees with matching branch names:

```bash
# Correct
git worktree add ../feature-auth feature-auth

# Wrong
git worktree add ../work1 feature-auth
```

## DCO Sign-off (Required)

All commits MUST include sign-off:

```bash
git commit -s -m "feat: description"
```

Sign-off email MUST match commit author email.

## Commit Messages

Follow conventional commits:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code restructuring
- `test:` - Tests
- `chore:` - Maintenance

## Pre-PR Validation (MANDATORY)

Before creating ANY PR, run and pass ALL THREE:

```bash
uv run ruff format --check .  # Format check
uv run ruff check .           # Lint check
uv run pytest tests/ -x -q    # Tests
```

**DO NOT create a PR if ANY check fails.**

## Rebase Before PR

```bash
git fetch origin main
git rebase origin/main
# Re-run checks after rebase
uv run ruff format --check . && uv run ruff check . && uv run pytest tests/ -x -q
```

## PR Iteration Naming

When addressing review feedback, create iteration branches:
- `original-branch-v2`
- `original-branch-v3`

## PR-Task Synchronization

When a PR completes a task, update before merging:

```bash
backlog task edit <task-id> --check-ac 1 --check-ac 2 -s Done \
  --notes $'Completed via PR #<number>\n\nStatus: Pending CI verification'
```

If PR fails CI, revert task to "In Progress".
