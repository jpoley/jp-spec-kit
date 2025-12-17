# Rigor Rules Quick Reference Card

**Print this and keep it handy while working on tasks**

## Branch Naming (MANDATORY)

```bash
# Format: hostname/task-NNN/slug-description
git checkout -b $(hostname -s | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]//g')/task-542/your-feature

# Examples:
# macbook-pro/task-542/decision-logging
# build-server/task-100/api-refactor
```

## Pre-PR Validation (MANDATORY - RUN BEFORE EVERY PR)

```bash
./scripts/bash/rigor-pre-pr-validation.sh
```

**If any check fails, FIX IT. No bypassing allowed.**

## Decision Logging

```bash
./scripts/bash/rigor-decision-log.sh \
  --task task-542 \
  --phase execution \
  --decision "Use React Query for data fetching" \
  --rationale "Built-in caching reduces boilerplate" \
  --actor "@frontend-engineer"
```

**Log when you:**
- Choose a library or framework
- Make an architecture decision
- Select a data structure
- Make a performance trade-off
- Implement a security pattern

## Rebase Before PR

```bash
git fetch origin main
git rebase origin/main
git push --force-with-lease
```

## DCO Sign-off

```bash
# Every commit needs sign-off
git commit -s -m "feat: your change"

# Fix missing sign-offs
git rebase -i origin/main --exec 'git commit --amend --no-edit -s'
```

## Freeze Task (Context Switch)

```bash
# Save and suspend work
/flow:freeze --reason "Blocked by API access"

# Resume later
git checkout branch-name
cat backlog/memory/task-542.md
/flow:implement
```

## Query Decisions

```bash
# All decisions for a task
jq '.' memory/decisions/task-542.jsonl

# Find specific decision
jq 'select(.decision | contains("PostgreSQL"))' memory/decisions/task-*.jsonl

# Timeline of all decisions
jq -s 'sort_by(.timestamp)' memory/decisions/task-*.jsonl
```

## Workflow Status Template

```
[Y] Phase: {PHASE} complete
    Current state: workflow:{STATE}
    Next step: {COMMAND}

    Progress:
    ✅ Setup phase
    ✅ Execution phase
    ⬜ Validation phase (NEXT)
    ⬜ PR phase (pending)

    Decisions logged: {COUNT}
```

## Common Fixes

### Invalid Branch Name
```bash
git branch -m old-name $(hostname -s)/task-542/slug
```

### Branch Behind Main
```bash
git rebase origin/main
git push --force-with-lease
```

### Invalid Decision Log JSON
```bash
jq empty memory/decisions/task-542.jsonl  # Find error
# Fix manually, then validate again
```

### Pre-PR Validation Fails
```bash
# Format
uv run ruff format .

# Lint
uv run ruff check . --fix

# Tests
uv run pytest tests/ -v

# Re-run validation
./scripts/bash/rigor-pre-pr-validation.sh
```

## Phases

1. **Setup**: Branch, constitution, task memory
2. **Execution**: Code, tests, decisions
3. **Freeze**: (optional) Suspend with context
4. **Validation**: Pre-PR checks
5. **PR**: Create, CI, review, merge

## Key Rules

1. Branch name MUST follow format
2. ALL commits MUST have DCO sign-off
3. Branch MUST be rebased before PR
4. Pre-PR validation MUST pass (no bypassing)
5. Critical decisions MUST be logged to JSONL

## Help

```bash
# Validate branch
./scripts/bash/rigor-branch-validation.sh

# Check rebase status
./scripts/bash/rigor-rebase-check.sh

# Full pre-PR check
./scripts/bash/rigor-pre-pr-validation.sh

# Log decision
./scripts/bash/rigor-decision-log.sh --help
```

## DORA Elite Targets

- **Deploy**: >1/day
- **Lead Time**: <1 day
- **Failures**: <5%
- **Restore**: <1 hour

Rigor rules help us hit these targets by preventing failures before they reach CI.

---

**Full docs**: `build-docs/platform/rigor-rules-infrastructure.md`
