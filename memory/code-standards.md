# Code Standards

## API-Calling Functions (from PRs #579-583 learnings)

When writing code that calls external APIs (HTTP requests, etc.):

### 1. Exception Handling - Never Silently Swallow

```python
# ❌ BAD - Silent swallowing hides debugging information
except Exception:
    pass

# ✅ GOOD - Log all exceptions with context
except httpx.TimeoutException:
    logger.debug(f"Timeout fetching {url}")
except httpx.HTTPError as e:
    logger.debug(f"HTTP error fetching {url}: {e}")
except Exception as e:
    logger.debug(f"Unexpected error fetching {url}: {e}")
return None
```

### 2. Test Coverage - All Failure Modes

Every API function needs tests for:
- [ ] Success case
- [ ] Timeout case
- [ ] Network error case
- [ ] Invalid HTTP status code (4xx, 5xx)
- [ ] Missing expected fields in response
- [ ] Malformed response (JSON decode error)

Example JSON decode error test:
```python
def test_returns_none_on_invalid_json(self):
    """Returns None when response contains invalid JSON."""
    import json
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = json.JSONDecodeError("Invalid", "", 0)

    with patch("module.client.get", return_value=mock_response):
        result = function_under_test()
        assert result is None
```

### 3. Code Duplication - Extract Early

Before committing, check for repeated patterns. Extract into helpers:
```python
# ❌ BAD - Same pattern repeated 3 times in show_version_info()
if versions["available"] and versions["installed"] and compare_semver(...) < 0:
    status = "↑"

# ✅ GOOD - Extracted helper
def _has_upgrade(versions: dict) -> bool:
    return bool(
        versions.get("available")
        and versions.get("installed")
        and compare_semver(versions["installed"], versions["available"]) < 0
    )
```

### 4. Docstrings - Document Return Guarantees

```python
# ❌ INCOMPLETE - No return guarantee documented
"""Get version from API.
Returns:
    Version string or None
"""

# ✅ COMPLETE - Clear guarantees
"""Get version from compatibility matrix.

Checks multiple sources in priority order:
1. Current working directory's .spec-kit-compatibility.yml
2. Package's bundled compatibility matrix
3. Falls back to default known version "0.0.20"

Note:
    This function reads from the file system.

Returns:
    Version string (e.g., "0.0.20"), guaranteed to return a value
"""
```

## Python

- **Linter/Formatter**: Ruff (replaces Black, Flake8, isort)
- **Line length**: 88 characters
- **Type hints**: Required for public APIs
- **File paths**: Use `pathlib`

## File I/O (Critical)

- **Always use `encoding="utf-8"`** for all file operations:
  ```python
  # Reading
  with open(file_path, encoding="utf-8") as f:
      content = f.read()

  # Writing with pathlib
  path.write_text(content, encoding="utf-8")
  path.read_text(encoding="utf-8")
  ```
- **Always clean up temp files** with try-finally:
  ```python
  with tempfile.NamedTemporaryFile(delete=False) as f:
      temp_path = f.name
  try:
      # use temp file
  finally:
      Path(temp_path).unlink(missing_ok=True)
  ```

## Naming (Avoid Shadowing)

Never use Python built-in names as parameters or variables:
- **Bad**: `id`, `type`, `list`, `dict`, `input`, `filter`, `map`, `hash`
- **Good**: `finding_id`, `item_type`, `items`, `data`, `user_input`

## Defensive Programming

- **Clamp external inputs** to expected ranges:
  ```python
  confidence = float(data.get("confidence", 0.5))
  confidence = max(0.0, min(1.0, confidence))  # Clamp to [0.0, 1.0]
  ```
- **Explicit type conversions** for clarity:
  ```python
  # Good: explicit
  validate_path(str(finding.location.file))

  # Bad: implicit conversion
  validate_path(finding.location.file)  # Relies on __str__
  ```

## YAGNI (You Aren't Gonna Need It)

- Don't add config fields you don't use
- Remove dead code, don't comment it out
- If a feature isn't implemented, don't scaffold it

## Testing

- **Framework**: pytest
- **Coverage**: >80% on core functionality
- **Pattern**: Arrange-Act-Assert (AAA)
- **No shadowing** in test helpers either

## Commits

Follow conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`

## Consistency is Non-Negotiable

**If a standard applies, it applies EVERYWHERE:**
- Production code
- Test code
- Example code in docstrings
- Template examples (in "after" sections)

**Common failures (from PR #376/#377 learnings):**
- Fixed encoding in production but not tests
- Fixed some `write_text()` calls but not all
- Fixed code but not example templates

## Imports

- All imports at **module level** (top of file)
- Never inline imports inside functions:
  ```python
  # Bad
  def parse_response(data: str):
      import json  # Inline import
      return json.loads(data)

  # Good
  import json  # At module level

  def parse_response(data: str):
      return json.loads(data)
  ```

## Pre-PR Verification (Critical)

**Run these grep commands before every PR:**

```bash
# Find file I/O without encoding (should return nothing)
grep -rn "write_text\|read_text\|open(" src/ tests/ | grep -v "encoding=" | grep -v "\.pyc"

# Find shadowed built-ins
grep -rn "def.*\b(id|type|list|dict|input|filter|map|hash)\s*[=:]" src/ tests/

# Find inline imports
grep -rn "^\s*import " src/ | grep -v "^[^:]*:1:" | head -20
```

## Pre-PR Checklist

Before creating a PR, verify:
- [ ] `encoding="utf-8"` on ALL file operations (production AND tests)
- [ ] No Python built-in names shadowed
- [ ] All temp files cleaned up properly
- [ ] External inputs validated/clamped
- [ ] No unused config fields or dead code
- [ ] Explicit type conversions where needed
- [ ] All imports at module level
- [ ] Example templates show best practices
- [ ] Ran grep verification commands above

## Git & CI Compliance (Critical - from PR #381 learnings)

### Pre-Commit Checks (Run ALL of these)

```bash
# 1. Fetch and rebase onto latest main FIRST
git fetch origin main && git rebase origin/main

# 2. Format check (CI runs this - MUST pass)
uv run ruff format --check .

# 3. Lint check
uv run ruff check .

# 4. Tests
uv run pytest tests/ -x -q
```

**Common failure**: Running `ruff check .` but NOT `ruff format --check .` - these are DIFFERENT checks. CI runs both.

### DCO (Developer Certificate of Origin) Compliance

**ALWAYS use `-s` flag when committing:**
```bash
git commit -s -m "feat: your message"
```

**DCO Requirements:**
1. Commit must have `Signed-off-by: Name <email>` line
2. Sign-off email MUST match commit author email
3. Use `--author="Name <email>"` if author differs from git config

**Example of correct commit:**
```bash
git commit -s --author="Jason Poley <jason.poley@gmail.com>" -m "feat: add feature"
```

**Fixing DCO after the fact:**
```bash
# Get message and fix sign-off
git log -1 --format="%B" | sed 's/old-email/correct-email/' > /tmp/msg.txt
git commit --amend -F /tmp/msg.txt --author="Name <correct-email>"
```

### Why Rebasing Before PR Matters

Other PRs may introduce formatting issues or new files that affect CI checks:
- PR #378 added `security/fixer/generator.py` with formatting issues
- If you don't rebase, CI tests the merge result which includes those issues
- Your PR fails even though your code is fine

**Always rebase before pushing:**
```bash
git fetch origin main
git rebase origin/main
# Re-run all checks after rebase
uv run ruff format --check . && uv run ruff check . && uv run pytest tests/ -x -q
```
