# Code Standards

## Python Standards

- **Linter/Formatter**: Ruff (replaces Black, Flake8, isort)
- **Line length**: 88 characters
- **Type hints**: Required for public APIs
- **File paths**: Use `pathlib`
- **Imports**: All at module level (never inside functions)

## File I/O (Critical)

**Always use `encoding="utf-8"`** for all file operations:

```python
path.read_text(encoding="utf-8")
path.write_text(content, encoding="utf-8")
```

**Always clean up temp files** with try-finally.

## Naming (Avoid Shadowing)

Never use Python built-in names as parameters or variables:
- **Bad**: `id`, `type`, `list`, `dict`, `input`, `filter`, `map`, `hash`
- **Good**: `finding_id`, `item_type`, `items`, `data`, `user_input`

## Defensive Programming

- **Clamp external inputs** to expected ranges
- **Explicit type conversions** for clarity

## YAGNI (You Aren't Gonna Need It)

- Don't add config fields you don't use
- Remove dead code, don't comment it out
- If a feature isn't implemented, don't scaffold it

## API-Calling Functions

### Exception Handling - Never Silently Swallow

```python
# BAD
except Exception:
    pass

# GOOD - Log all exceptions with context
except httpx.TimeoutException:
    logger.debug(f"Timeout fetching {url}")
except httpx.HTTPError as e:
    logger.debug(f"HTTP error fetching {url}: {e}")
```

### Test Coverage - All Failure Modes

Every API function needs tests for:
- Success case
- Timeout case
- Network error case
- Invalid HTTP status code (4xx, 5xx)
- Missing expected fields in response
- Malformed response (JSON decode error)

## Pre-PR Verification

```bash
# Run before every PR:
uv run ruff format --check .
uv run ruff check .
uv run pytest tests/ -x -q
```

## Git & CI Compliance

### Pre-Commit Checks

```bash
git fetch origin main && git rebase origin/main
uv run ruff format --check .
uv run ruff check .
uv run pytest tests/ -x -q
```

**Common failure**: Running `ruff check .` but NOT `ruff format --check .` - these are DIFFERENT checks. CI runs both.

### DCO Compliance

**ALWAYS use `-s` flag when committing:**

```bash
git commit -s -m "feat: your message"
```

## Commits

Follow conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Consistency is Non-Negotiable

**If a standard applies, it applies EVERYWHERE:**
- Production code
- Test code
- Example code in docstrings
- Template examples
