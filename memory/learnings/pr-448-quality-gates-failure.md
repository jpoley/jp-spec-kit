# Lessons Learned: PR #448 Quality Gates Failure

## Summary

PR #448 (task-083 pre-implementation quality gates) failed CI lint check and had code quality issues identified by Copilot review.

## Root Causes

### 1. Lint Failure - File Not Formatted
- **Issue**: `.claude/hooks/pre-implement.py` failed `ruff format --check .`
- **Root Cause**: Local validation may have passed but file was modified after check
- **Fix**: Always run format/check immediately before git commit

### 2. Unused Constant
- **Issue**: `EXIT_ERROR = 2` defined but never used
- **Root Cause**: Defensive coding adding constants "just in case"
- **Fix**: Only define what you use; remove dead code before commit

### 3. Unused Variable
- **Issue**: `gap = threshold - score` calculated but never used
- **Root Cause**: Leftover from refactoring or incomplete implementation
- **Fix**: Review all variables are actually used; delete unused ones

### 4. Suboptimal Regex
- **Issue**: `r"^[\\s]*[-*]\\s+"` could be simplified to `r"^\\s*[-*]\\s+"`
- **Root Cause**: Unnecessary character class wrapper around single character
- **Fix**: Review regex patterns for simplification opportunities

## Prevention Checklist

Before every PR:

```bash
# 1. Format all changed files
uv run ruff format .

# 2. Verify format check passes
uv run ruff format --check .

# 3. Run lint check
uv run ruff check .

# 4. Run tests
uv run pytest tests/ -x -q

# 5. Review for dead code
# - Unused imports
# - Unused variables
# - Unused constants
# - Unused functions

# 6. Only then commit and push
git add . && git commit -s -m "..."
```

## Code Quality Rules

1. **No dead code**: Every constant, variable, import, and function must be used
2. **Simplify regex**: Use simplest pattern that works; avoid redundant character classes
3. **Complete implementations**: Don't leave variables calculated but unused
4. **Run full validation chain**: format → lint → tests → commit

## Key Takeaway

**Trust but verify**: Don't assume local checks pass in CI. The validation chain must be:
1. `ruff format .` (fix)
2. `ruff format --check .` (verify)
3. `ruff check .` (lint)
4. `pytest tests/ -x -q` (test)

Only after ALL pass should you commit.
