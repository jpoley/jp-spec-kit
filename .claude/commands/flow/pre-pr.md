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
    if ! uv run bandit -r src/ -ll; then
      echo "[X] VALID-002: SAST (bandit) failed"
      exit 1
    fi
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
backlog_output=$(backlog task "$TASK_ID" --plain)
if [ $? -ne 0 ]; then
  echo "[X] VALID-005: Failed to fetch task $TASK_ID from backlog"
  exit 1
fi
total_acs=$(printf '%s\n' "$backlog_output" | grep -c "^\[[ xX]\]")
if [ "$total_acs" -eq 0 ]; then
  echo "[X] VALID-005: No acceptance criteria found for task $TASK_ID"
  exit 1
fi
unchecked_acs=$(printf '%s\n' "$backlog_output" | grep -c "^\[ \]")
if [ "$unchecked_acs" -ne 0 ]; then
  echo "[X] VALID-005: Incomplete ACs ($unchecked_acs of $total_acs unchecked)"
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

After all validations pass, display a summary:

```bash
echo "Pre-PR Validation"
echo "================="
echo "[OK] VALID-001: Decision log exists"
echo "[OK] VALID-002: Lint and SAST pass"
echo "[OK] VALID-003: No unused imports/variables"
echo "[OK] VALID-007: Tests pass, code formatted"
echo "[OK] VALID-004: Branch rebased from main"
echo "[OK] VALID-005: All ACs complete ($total_acs/$total_acs)"
echo "[OK] PR-001: All commits DCO signed"
echo ""
echo "All pre-PR validations passed. Ready to create PR."
```

### If All Checks Pass

```bash
git add . && git commit -s -m "feat(scope): description"
git push origin <branch-name>
gh pr create --title "feat: description" --body "..."
```

### Composability

Invoke standalone (`/flow:pre-pr`), via `/flow:implement`, or in CI pipelines.
