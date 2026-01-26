# Critical Rules

## NEVER DELETE TESTS (ABSOLUTE - NO EXCEPTIONS)

**An AI agent MUST NEVER delete test files or test methods without EXPLICIT human instruction.**

This is NON-NEGOTIABLE. No exceptions. No rationalizations.

### What is NOT a valid reason to delete tests:
- "The code is deprecated" - NO
- "New tests replace them" - NO
- "It's a refactor" - NO
- "The tests are outdated" - NO
- "The tests are failing" - NO (fix them instead)
- "The commit message explains it" - NO

### The ONLY valid reason:
**Human explicitly says: "Delete these specific tests: [list]"**

### If you think tests should be deleted:
1. STOP
2. ASK the human: "I believe tests X, Y, Z may need removal because [reason]. Do you approve?"
3. WAIT for explicit "yes, delete them"
4. Only then proceed

### PR Requirements for ANY test deletion:
If human approves test deletion, the PR MUST:
1. Have **⚠️ TEST DELETION** in the PR title
2. List every deleted test file and method
3. Show before/after test counts
4. Explain why each deletion was human-approved

### Historical Example

In PR **#545** (commit `bd8642d`), an automated change deleted approximately **1,560 lines of tests** in a single shot. The deletion removed critical regression coverage, hid real defects that later escaped to users, and took significant human effort to diagnose and repair. This incident is **why** this rule exists and is **non-negotiable**.

---

## Pre-PR Validation (MANDATORY - NO EXCEPTIONS)

**BEFORE creating any PR, you MUST run and pass ALL THREE:**

```bash
uv run ruff format --check .  # Format check - MUST pass
uv run ruff check .           # Lint check - MUST pass with zero errors
uv run pytest tests/ -x -q    # Tests - MUST pass with zero failures
```

**DO NOT create a PR if ANY check fails.** Fix issues first.

---

## No Direct Commits to Main (ABSOLUTE - NO EXCEPTIONS)

**NEVER commit directly to main.** All changes MUST go through a PR:

1. Create branch -> 2. Make changes -> 3. **Run lint + tests locally** -> 4. Create PR -> 5. CI passes -> 6. Merge -> 7. Mark task Done

Not for "urgent" fixes. Not for "small" changes. **NO EXCEPTIONS.**

---

## DCO Sign-off (Required)

All commits MUST include sign-off:

```bash
git commit -s -m "feat: description"
```

---

## Backlog.md Task Management

**NEVER edit task files directly** - Use `backlog task edit` CLI commands only.
Direct file editing breaks metadata sync, Git tracking, and relationships.

---

## Task Memory - Durable Context (CRITICAL)

Task memory (`backlog/memory/task-XXX.md`) stores context that MUST survive:
- Context resets/compaction
- Session switches and machine changes
- Agent handoffs between workflow phases

### What MUST be in Task Memory

**"Critical Context" section (NEVER DELETE):**
1. **What**: Brief description of what we're building
2. **Why**: Business value, user need, or problem being solved
3. **Constraints**: Technical requirements, deadlines, dependencies
4. **AC Status**: Which acceptance criteria are complete/incomplete

**Key Decisions:**
- Architecture choices with rationale
- Trade-offs made and why
- Rejected approaches and why they failed

### When to Update Task Memory

- **Session start**: Read memory, update "Current State"
- **After decisions**: Record in "Key Decisions" immediately
- **Before session end**: Update "Current State" with what's done/next
- **After blocking issues**: Document in "Blocked/Open Questions"

---

## PR-Task Synchronization (Required)

When a PR completes a backlog task, update the task **before or with** PR creation:

```bash
backlog task edit <task-id> --check-ac 1 --check-ac 2 -s Done \
  --notes $'Completed via PR #<number>\n\nStatus: Pending CI verification'
```

**If PR fails CI**: Revert task to "In Progress" and uncheck incomplete ACs.

---

## Git Worktrees for Parallel Work

Worktree name MUST match branch name:

```bash
git worktree add ../feature-auth feature-auth  # Correct
git worktree add ../work1 feature-auth         # Wrong
```
