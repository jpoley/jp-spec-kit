# PR Quality Checklist

This checklist ensures PRs pass CI and meet quality standards before submission.

## Pre-PR Verification Script

Run this before every PR:

Run the pre-PR check script before every PR:

```bash
./scripts/bash/pre-pr-check.sh
## Mandatory Checks

### 1. DCO Sign-off (Developer Certificate of Origin)

Every commit MUST include a DCO sign-off:

```bash
# Sign off a new commit
git commit -s -m "feat: add feature"

# Amend an existing commit to add sign-off
git commit --amend -s --no-edit

# Check if sign-off is present
git log -1 --format="%B" | grep -i "signed-off"
```

**Why it matters:** PRs without DCO are automatically rejected by CI.

### 2. Ruff Linting

```bash
# Check for lint errors
ruff check .

# Auto-fix lint errors
ruff check . --fix

# Check specific module
ruff check src/specify_cli/security/
```

**Common issues:**
- Unused imports
- Line too long (>88 chars)
- Missing type hints
- Undefined names

### 3. Ruff Formatting

```bash
# Check if files are formatted
ruff format --check .

# Auto-format files
ruff format .

# Check specific module
ruff format --check src/specify_cli/security/
```

**Why it matters:** Unformatted code fails CI.

### 4. Tests

```bash
# Run all tests
uv run pytest tests/ -q

# Run specific test module
uv run pytest tests/security/ -q

# Run with verbose output
uv run pytest tests/security/ -v

# Run with coverage
uv run pytest tests/ --cov=src/specify_cli
```

**Test requirements:**
- All tests must pass
- New code should have tests
- Aim for 80%+ coverage on new modules

## CI/CD Pipeline Checks

The CI pipeline runs these checks in order:

| Check | Command | Required |
|-------|---------|----------|
| DCO | `dco-check` | Yes |
| Lint | `ruff check .` | Yes |
| Format | `ruff format --check .` | Yes |
| Tests | `pytest tests/` | Yes |
| Type Check | `mypy src/` | Optional |

## Common PR Issues and Fixes

### Issue: Missing DCO Sign-off

**Error:** `DCO check failed`

**Fix:**
```bash
git commit --amend -s --no-edit
git push --force-with-lease
```

### Issue: Lint Errors

**Error:** `ruff check failed`

**Fix:**
```bash
ruff check . --fix
git add -A && git commit --amend --no-edit
git push --force-with-lease
```

### Issue: Format Errors

**Error:** `ruff format --check failed`

**Fix:**
```bash
ruff format .
git add -A && git commit --amend --no-edit
git push --force-with-lease
```

### Issue: Test Failures

**Error:** `pytest failed`

**Fix:**
1. Run tests locally: `uv run pytest tests/ -v`
2. Fix failing tests
3. Commit and push

## Pre-commit Hook Setup

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: Ruff Lint
        entry: ruff check --fix
        language: system
        types: [python]

      - id: ruff-format
        name: Ruff Format
        entry: ruff format
        language: system
        types: [python]

      - id: dco-check
        name: DCO Sign-off
        entry: bash -c 'git log -1 --format="%B" | grep -qi "signed-off-by"'
        language: system
        always_run: true
```

Install:
```bash
pre-commit install
```

## Quick Reference

```bash
# Full verification before PR
ruff check . && ruff format --check . && uv run pytest tests/ -q

# Fix all issues
ruff check . --fix && ruff format .

# Amend commit with sign-off
git commit --amend -s --no-edit

# Push amended commit
git push --force-with-lease
```

## Lessons Learned

From the galway security feature development:

1. **Always run verification locally before PR** - Don't rely on CI to catch issues
2. **Use `git commit -s`** - Make DCO sign-off automatic
3. **Run ruff before every commit** - Catch issues early
4. **Test in isolation** - Run just the module's tests first
5. **Check PR status after creation** - Don't assume CI will pass

## See Also

- [Contributing Guide](../../CONTRIBUTING.md)
