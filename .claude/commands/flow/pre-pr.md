---
description: Run pre-PR validation checklist before creating pull request.
loop: inner
# Loop Classification: INNER LOOP
# This command validates all requirements before PR creation.
---

## User Input

```text
$ARGUMENTS
```

## Execution Instructions

Run all validation checks before creating a PR. All checks must pass - this is a blocking gate.

### Step 1: Decision Logging (VALID-001)

```bash
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")
DECISION_LOG="memory/decisions/${TASK_ID}.jsonl"
if [ ! -f "$DECISION_LOG" ] || [ "$(wc -l < "$DECISION_LOG")" -le 0 ]; then
  echo "[X] VALID-001: No decisions logged"
  exit 1
fi
```

### Step 2: Lint and SAST (VALID-002)

```bash
if [ -f "pyproject.toml" ]; then
  if ! uv run ruff check .; then
    echo "[X] VALID-002: Lint failed"
    exit 1
  fi
  if command -v bandit >/dev/null; then
    uv run bandit -r src/ -ll
  fi
fi
```

### Step 3: Coding Standards (VALID-003)

```bash
if [ -f "pyproject.toml" ]; then
  if ! uv run ruff check --select F401,F841 .; then
    echo "[X] VALID-003: Unused imports/variables"
    exit 1
  fi
fi
```

### Step 4: Tests and Formatting (VALID-007)

```bash
if [ -f "pyproject.toml" ]; then
  if ! uv run pytest tests/ -x -q; then
    echo "[X] VALID-007: Tests failed"
    exit 1
  fi

  if ! uv run ruff format --check .; then
    echo "[X] VALID-007: Not formatted"
    exit 1
  fi
fi
```

### Step 5: Rebase Status (VALID-004)

```bash
git fetch origin main 2>/dev/null
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo 0)
if [ "$BEHIND" -gt 0 ]; then
  echo "[X] VALID-004: $BEHIND commits behind main"
  exit 1
fi
```

### Step 6: Acceptance Criteria (VALID-005)

```bash
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+')
if [ -z "$TASK_ID" ]; then
  echo "[X] VALID-005: Incomplete ACs (no task ID found on branch name)"
  exit 1
fi
if ! backlog task "$TASK_ID" --plain | grep -c "^\[ \]" | grep -q "^0$"; then
  echo "[X] VALID-005: Incomplete ACs"
  exit 1
fi
```

### Step 7: DCO Sign-off (PR-001)

```bash
dco_fail=0
for hash in $(git log origin/main..HEAD --format='%h'); do
  if ! git log -1 --format='%B' "$hash" | grep -q "Signed-off-by:"; then
    echo "[X] PR-001: $hash missing sign-off"
    dco_fail=1
  fi
done

if [ "$dco_fail" -ne 0 ]; then
  exit 1
fi
```

### Validation Summary

```
Pre-PR Validation
=================
[ ] VALID-001: Decision log exists
[ ] VALID-002: Lint and SAST pass
[ ] VALID-003: No unused imports/variables
[ ] VALID-007: Tests pass, code formatted
[ ] VALID-004: Branch rebased from main
[ ] VALID-005: All ACs complete
[ ] PR-001: All commits DCO signed
```

### If All Checks Pass

```bash
git add . && git commit -s -m "feat(scope): description"
git push origin <branch-name>
gh pr create --title "feat: description" --body "..."
```

### Composability

Invoke standalone (`/flow:pre-pr`), via `/flow:implement`, or in CI pipelines.
