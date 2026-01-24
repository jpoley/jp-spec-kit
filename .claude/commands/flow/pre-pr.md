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
[ -f "$DECISION_LOG" ] && [ $(wc -l < "$DECISION_LOG") -gt 0 ] || echo "[X] VALID-001: No decisions logged"
```

### Step 2: Lint and SAST (VALID-002)

```bash
[ -f "pyproject.toml" ] && uv run ruff check . || echo "[X] VALID-002: Lint failed"
[ -f "pyproject.toml" ] && command -v bandit >/dev/null && uv run bandit -r src/ -ll
```

### Step 3: Coding Standards (VALID-003)

```bash
[ -f "pyproject.toml" ] && uv run ruff check --select F401,F841 . || echo "[X] VALID-003: Unused imports/variables"
```

### Step 4: Tests and Formatting (VALID-007)

```bash
[ -f "pyproject.toml" ] && uv run pytest tests/ -x -q || echo "[X] VALID-007: Tests failed"
[ -f "pyproject.toml" ] && uv run ruff format --check . || echo "[X] VALID-007: Not formatted"
```

### Step 5: Rebase Status (VALID-004)

```bash
git fetch origin main 2>/dev/null
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo 0)
[ "$BEHIND" -gt 0 ] && echo "[X] VALID-004: $BEHIND commits behind main"
```

### Step 6: Acceptance Criteria (VALID-005)

```bash
TASK_ID=$(git branch --show-current | grep -Eo 'task-[0-9]+')
[ -n "$TASK_ID" ] && backlog task "$TASK_ID" --plain | grep -c "^\[ \]" | grep -q "^0$" || echo "[X] VALID-005: Incomplete ACs"
```

### Step 7: DCO Sign-off (PR-001)

```bash
for hash in $(git log origin/main..HEAD --format='%h'); do
  git log -1 --format='%B' "$hash" | grep -q "Signed-off-by:" || echo "[X] PR-001: $hash missing sign-off"
done
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
