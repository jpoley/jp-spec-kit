# Testing Rules

Rules for test quality and coverage.

## Framework and Coverage

- **Framework**: pytest
- **Coverage target**: >80% on core functionality
- **Pattern**: Arrange-Act-Assert (AAA)

## Never Delete Tests

**ABSOLUTE - NO EXCEPTIONS**

AI agents MUST NEVER delete test files or test methods without EXPLICIT human instruction.

### NOT valid reasons to delete:
- "The code is deprecated"
- "New tests replace them"
- "It's a refactor"
- "The tests are outdated"
- "The tests are failing" (fix them instead)

### The ONLY valid reason:
Human explicitly says: "Delete these specific tests: [list]"

### If you think tests should be deleted:
1. STOP
2. ASK: "I believe tests X, Y, Z may need removal because [reason]. Do you approve?"
3. WAIT for explicit "yes, delete them"

## API Function Test Coverage

Every API function needs tests for:
- Success case
- Timeout case
- Network error case
- Invalid HTTP status (4xx, 5xx)
- Missing expected fields
- Malformed response (JSON decode error)

## Project Root Detection

Every test that reads files MUST include:

```python
# Requires: from pathlib import Path
def get_project_root() -> Path:
    """Get the project root directory reliably."""
    return Path(__file__).resolve().parent.parent
```

Never use relative paths like `Path(".claude/agents/...")`.

## Safe File Reading

```python
# Requires: from pathlib import Path; from typing import Optional
def safe_read_file(file_path: Path) -> Optional[str]:
    """Safely read file, returning None on missing/error."""
    try:
        if file_path.exists() and file_path.is_file():
            return file_path.read_text(encoding="utf-8")
    except (OSError, IOError, PermissionError):
        pass
    return None
```

## Constants (No Magic Numbers)

Define ALL numeric values at module level:

```python
# Good
MIN_README_LENGTH = 100  # Ensures meaningful content
MAX_PLACEHOLDER_COUNT = 20  # Template has ~30 placeholders

# Bad
assert len(content) > 100
```

## Type Hints and Assertions

- All test methods require `-> None` return type
- Include meaningful assertion messages: `assert path.exists(), f"Not found: {path}"`

## Pre-Commit Verification

Run all three before committing:
- `uv run ruff check .` - Lint
- `uv run ruff format --check .` - Format
- `uv run pytest tests/ -x -q` - Tests
