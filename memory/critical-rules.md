# Critical Rules

## Pre-PR Validation (MANDATORY - NO EXCEPTIONS)

**BEFORE creating any PR, you MUST run and pass ALL THREE:**

```bash
# 1. Format check - MUST pass (no files needing reformatting)
uv run ruff format --check .

# 2. Lint check - MUST pass with zero errors
uv run ruff check .

# 3. Tests - MUST pass with zero failures
uv run pytest tests/ -x -q

# Run format first if needed, then verify:
uv run ruff format .  # Fix formatting
uv run ruff format --check . && uv run ruff check . && uv run pytest tests/ -x -q
```

**DO NOT create a PR if ANY check fails.** Fix issues first.

This is NON-NEGOTIABLE. PRs that fail CI waste time and create noise.

## No Direct Commits to Main (ABSOLUTE - NO EXCEPTIONS)

**NEVER commit directly to main.** All changes MUST go through a PR:

1. Create branch → 2. Make changes → 3. **Run lint + tests locally** → 4. Create PR → 5. CI passes → 6. Merge → 7. Mark task Done

Not for "urgent" fixes. Not for "small" changes. **NO EXCEPTIONS.**

See `memory/constitution.md` for full details.

## Branch Naming Convention (MANDATORY)

**ALL branches MUST include the machine hostname prefix:**

```bash
# Correct branch naming:
kinsale/task-083-quality-gates     # Machine name + task reference
galway/feature-auth-refactor       # Machine name + description
muckross/task-212-triage-engine    # Machine name + task reference

# WRONG - will be deleted:
task-083-quality-gates             # Missing hostname
feature/task-083                   # Wrong prefix pattern
feature-auth-refactor              # Missing hostname
```

**Why?** Branch names identify which machine/agent created the work. This enables:
- Parallel work across multiple machines
- Clear ownership and accountability
- Easy identification of work source

**Hostname is derived from the machine running Claude Code** (e.g., kinsale, galway, muckross).

## DCO Sign-off (Required)

All commits MUST include sign-off:

```bash
git commit -s -m "feat: description"
```

## Version Management

When modifying `src/specify_cli/__init__.py`:
1. Update version in `pyproject.toml`
2. Add entry to `CHANGELOG.md`
3. Follow semantic versioning

## Backlog.md Task Management

**NEVER edit task files directly** - Use `backlog task edit` CLI commands only.
Direct file editing breaks metadata sync, Git tracking, and relationships.

See: `backlog/CLAUDE.md` for detailed guidance.

## PR-Task Synchronization (Required)

When a PR completes a backlog task, update the task **before or with** PR creation:

```bash
# Mark ACs complete and set status with PR reference
backlog task edit <id> --check-ac 1 --check-ac 2 -s Done \
  --notes $'Completed via PR #<number>\n\nStatus: Pending CI verification'
```

**If PR fails CI**: Revert task to "In Progress" and uncheck incomplete ACs.
The backlog must always reflect reality.

## Git Worktrees for Parallel Work

Worktree name MUST match branch name:

```bash
git worktree add ../feature-auth feature-auth  # Correct
git worktree add ../work1 feature-auth         # Wrong
```

## Code Quality Standards

### Imports (PR #342)
All imports MUST be at module level, never inside functions/methods.

### Configuration Fields (PR #349)
Every configuration field MUST be used somewhere in the code. Before adding a config option, implement its functionality first or remove the field entirely.

### Output Formats (PR #349)
Output format methods MUST produce properly formatted content for their target format. No placeholder implementations that output raw/unconverted content.

### Variable Naming (PR #349)
Never use variable names that shadow imported modules (`html`, `json`, `re`, `os`, `sys`). Use descriptive names like `html_output`, `json_data`.

### Pattern Matching in Security Code (PR #342)
When writing heuristic classifiers:
1. Consider what ELSE could match the pattern (adversarial examples)
2. Add context requirements (same line, specific surrounding patterns)
3. Use negative patterns to exclude known false matches
4. NEVER return early on a single pattern - check for conflicting patterns

### Exception Handling (PR #342)
Exception handlers MUST:
1. Log the actual exception with context using `logger.warning()` or `logger.error()`
2. Include relevant data (truncated to reasonable size)
3. Return error details in user-facing messages when appropriate

### File Path Operations (PR #342)
For file-system operations:
1. Use absolute paths resolved from a known root
2. Find the actual git root, don't assume it's the file's parent
3. Use paths relative to git root for git commands

See: `memory/learnings/` for detailed examples from each PR.
