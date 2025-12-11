# Test Quality Standards

This document captures defensive coding patterns for test files and code examples, learned from fixing fragile tests and broken code examples in task-086, task-087, task-191a, task-191b, and task-191c.

## CRITICAL: Code Examples Must Be Complete and Runnable

**Every code example in documentation, agent definitions, and templates MUST be complete enough to run.** This means:

1. **ALL imports must be present** - no implicit imports
2. **No undefined references** - explain any dependencies with comments
3. **Use proper validators** - not weak regex patterns

### Why This Matters

Code examples are frequently copy-pasted by users and AI assistants. Incomplete examples:
- Fail immediately when run
- Waste time debugging missing imports
- Set a poor standard for the codebase
- Indicate the code was never actually tested

### Required Import Patterns

```python
# WRONG - Missing imports that would cause immediate failure
router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")  # Weak regex!

class UserResponse(BaseModel):
    created_at: datetime  # Where does datetime come from?

async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):  # AsyncSession? get_db?
    existing = await db.scalar(select(User).where(...))  # select? User?
```

```python
# CORRECT - Complete imports and documented dependencies
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db  # Your database dependency
from app.models import User  # Your SQLAlchemy User model

router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    """Request model for user creation."""

    email: EmailStr  # Robust email validation, not weak regex
    name: str = Field(..., min_length=1, max_length=100)


class UserResponse(BaseModel):
    """Response model for user data."""

    id: int
    email: str
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Create a new user."""
    # Check if email already exists
    existing = await db.scalar(select(User).where(User.email == user.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Create new user
    new_user = User(email=user.email, name=user.name)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
```

### Exception Handler Example

```python
# WRONG - Missing imports, undefined app, undefined UserNotFoundError
@app.exception_handler(UserNotFoundError)  # app? UserNotFoundError?
async def user_not_found_handler(request: Request, exc: UserNotFoundError):  # Request?
    return JSONResponse(status_code=404, content={"detail": str(exc)})  # JSONResponse?
```

```python
# CORRECT - Complete imports, defined exception class, defined app
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# Define custom exception with user_id attribute
class UserNotFoundError(Exception):
    """Raised when a user is not found in the database."""

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__(f"User {user_id} not found")


app = FastAPI()  # Your FastAPI application instance


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(
    request: Request, exc: UserNotFoundError
) -> JSONResponse:
    """Convert UserNotFoundError to HTTP 404 response."""
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc), "user_id": exc.user_id},
    )
```

### Test Example Imports

```python
# WRONG - Missing imports in test examples
@pytest.mark.asyncio
async def test_user_flow(client: AsyncClient):  # AsyncClient from where? client fixture?
    response = await client.post("/users/", json={...})  # json={...} is not valid!
```

```python
# CORRECT - Complete test imports with fixture documentation
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_user_flow(client: AsyncClient) -> None:
    """Test complete user creation and retrieval flow.

    Args:
        client: AsyncClient fixture (defined in conftest.py)
    """
    response = await client.post(
        "/users/",
        json={"email": "test@example.com", "name": "Test User"},
    )
    assert response.status_code == 201
    user_id = response.json()["id"]

    # Verify user was created
    response = await client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
```

### Checklist for Code Examples

- [ ] All imports are explicitly listed
- [ ] All type hints use imported types
- [ ] Undefined dependencies have explanatory comments
- [ ] Uses `EmailStr` not regex for email validation
- [ ] Test methods have `-> None` return type
- [ ] Test methods have docstrings
- [ ] The example could be copy-pasted and run (with appropriate model definitions)

## Required Helper Functions

Every test file that reads project files MUST include these helper functions:

### 1. Project Root Detection

```python
def get_project_root() -> Path:
    """Get the project root directory reliably.

    Returns:
        Path to the project root directory.
    """
    return Path(__file__).resolve().parent.parent
```

**Why**: Using relative paths like `Path(".claude/agents/...")` breaks depending on the working directory. Tests run from different directories (IDE, CI, command line) must work consistently.

**Wrong**:
```python
AGENT_DIR = ".claude/agents"  # Fragile!
return Path(AGENT_DIR) / filename
```

**Correct**:
```python
return get_project_root() / ".claude" / "agents" / filename
```

### 2. Safe File Reading

```python
def safe_read_file(file_path: Path) -> Optional[str]:
    """Safely read a file, returning None if it doesn't exist or can't be read.

    Args:
        file_path: Path to the file to read.

    Returns:
        File contents as string, or None if the file can't be read.
    """
    try:
        if file_path.exists() and file_path.is_file():
            return file_path.read_text(encoding="utf-8")
    except (OSError, IOError, PermissionError):
        pass
    return None
```

**Why**: Functions named "safe" should not raise exceptions. Return `Optional[str]` to allow graceful handling when files don't exist or can't be read.

**Wrong** (misleading name):
```python
def _read_file_safely(file_path: Path) -> str:
    if not file_path.exists():
        raise FileNotFoundError(...)  # NOT safe!
```

**Correct**: Return `None` instead of raising, let callers decide how to handle.

## Required Imports

Always import these types:

```python
from pathlib import Path
from typing import Dict, Optional

import pytest
```

## Constants at Module Level - NO MAGIC NUMBERS

Define ALL numeric values and patterns as module-level constants with explanatory comments:

```python
# WRONG - Magic numbers with unclear meaning
assert len(content) > 100
assert placeholder_count < 20
assert len(placeholders) >= 10
```

```python
# CORRECT - Named constants with explanation
# Minimum README length to ensure meaningful content (not just a title)
MIN_README_LENGTH = 100

# Minimum case study length - a real case study should be substantial
# (includes metrics, phases, feedback, recommendations, appendix)
MIN_CASE_STUDY_LENGTH = 2000

# Maximum placeholder count before content is considered mostly unfilled
# Template has ~30 placeholders, so 20 indicates mostly template
MAX_PLACEHOLDER_COUNT = 20

# Minimum placeholders expected in template for customization guidance
MIN_TEMPLATE_PLACEHOLDERS = 10

# Regex pattern to validate two-digit prefixed filenames (e.g., 01-name.md, 02-name.md)
CASE_STUDY_NAMING_PATTERN = re.compile(r"^\d{2}-[a-z0-9-]+$")
```

**Why This Matters**:
- Magic numbers make requirements unclear
- Future maintainers can't understand why `20` was chosen
- Constants document the reasoning and make changes easier

Also define expected values as module-level constants:

```python
# Constants
AGENT_NAME = "backend-engineer"
EXPECTED_COLOR = "green"
EXPECTED_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]
REQUIRED_FRONTMATTER_FIELDS = ["name", "description", "tools", "color"]
REQUIRED_CONTENT_SECTIONS = [
    "## Core Technologies",
    "## Implementation Standards",
]
```

## Shared Fixtures - Avoid Duplication

When multiple test classes need the same fixture, define it at module level:

```python
# WRONG - Same fixture duplicated in every test class
class TestStructure:
    @pytest.fixture
    def case_studies_dir(self) -> Path:
        return get_project_root() / "docs" / "case-studies"

class TestContent:
    @pytest.fixture
    def case_studies_dir(self) -> Path:  # Duplicated!
        return get_project_root() / "docs" / "case-studies"

class TestReadme:
    @pytest.fixture
    def case_studies_dir(self) -> Path:  # Duplicated again!
        return get_project_root() / "docs" / "case-studies"
```

```python
# CORRECT - Single shared fixture at module level
@pytest.fixture
def case_studies_dir() -> Path:
    """Get the case studies directory path.

    Returns:
        Path to docs/case-studies directory.
    """
    return get_project_root() / "docs" / "case-studies"


class TestStructure:
    def test_directory_exists(self, case_studies_dir: Path) -> None:
        # Uses shared fixture
        ...

class TestContent:
    def test_has_required_sections(self, case_studies_dir: Path) -> None:
        # Uses same shared fixture
        ...
```

## Type Hints

All functions and methods must have complete type hints:

```python
def test_method(self, fixture: Path) -> None:  # -> None required
    ...

def helper_function(content: str) -> Dict[str, str]:  # Return type required
    ...
```

## File Encoding

Always specify encoding when reading files:

```python
# Correct
file_path.read_text(encoding="utf-8")

# Wrong (relies on system default)
file_path.read_text()
```

## Assertion Messages

Include meaningful assertion messages that help diagnose failures:

```python
# Good
assert agent_path.exists(), f"Agent file not found at {agent_path}"
assert frontmatter.get("name") == AGENT_NAME, (
    f"Agent name should be '{AGENT_NAME}', got '{frontmatter.get('name')}'"
)

# Bad (no context on failure)
assert agent_path.exists()
assert frontmatter.get("name") == AGENT_NAME
```

## Fixture Patterns

Use consistent fixture patterns for shared test data:

```python
@pytest.fixture
def agent_path(self) -> Path:
    """Get path to the agent file."""
    return get_project_root() / ".claude" / "agents" / "agent-name.md"

@pytest.fixture
def agent_content(self, agent_path: Path) -> str:
    """Return content of the agent file."""
    content = safe_read_file(agent_path)
    if content is None:
        pytest.skip(f"Agent file not found: {agent_path}")
    return content
```

## Test Organization

Group related tests into classes with clear docstrings:

```python
class TestAgentFile:
    """Test the agent file exists and is valid."""

class TestFrontmatter:
    """Test the YAML frontmatter of the agent."""

class TestTools:
    """Test the tools configuration for the agent."""

class TestContent:
    """Test the content of the agent."""
```

## Use Regex for Structural Assertions, Not Simple String Matching

When testing that content has specific patterns (like conditionals, function definitions), use regex instead of simple string matching:

```python
# WRONG - Weak assertion that doesn't validate structure
assert ".flowspec-light-mode" in content, "Missing light mode marker check"
# This passes even if the string is in a comment or random text!
```

```python
# CORRECT - Regex validates actual conditional structure
import re

# Pattern matches: if [ -f ".flowspec-light-mode" ] or similar conditional
light_mode_conditional = re.search(
    r'if\s+\[.*\.flowspec-light-mode.*\]', content
)
assert light_mode_conditional is not None, (
    "Missing conditional check for .flowspec-light-mode "
    "(expected: if [ -f \".flowspec-light-mode\" ])"
)
```

**Why This Matters**:
- Simple string matching can pass when the pattern is in a comment or example
- Regex ensures the actual structural pattern exists
- Better error messages when the assertion fails

## Bash Code Examples Must Be Complete

Bash code examples should include both the if and else branches to show the complete logic:

```bash
# WRONG - Incomplete bash example missing else clause
if [ -f ".flowspec-light-mode" ]; then
  echo "LIGHT MODE DETECTED"
fi
# What happens when NOT in light mode? Unclear!
```

```bash
# CORRECT - Complete bash example with both branches
if [ -f ".flowspec-light-mode" ]; then
  echo "LIGHT MODE DETECTED"
  # Stop here - research is skipped in light mode
else
  echo "FULL MODE - Proceeding with research"
  # Continue with standard research workflow
fi
```

**Why**: Complete examples prevent users from missing important logic paths.

## Except Clauses Must Have Explanatory Comments

Empty `except` blocks or those that just `pass` must explain why:

```python
# WRONG - Silent suppression without explanation
try:
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
except (OSError, IOError, PermissionError):
    pass  # Why are we suppressing? Unclear!
return None
```

```python
# CORRECT - Comment explains the intent
try:
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
except (OSError, IOError, PermissionError):
    # Suppress file read errors; function returns None if file can't be read
    pass
return None
```

## Checklist for New Test Files

- [ ] `get_project_root()` helper function included
- [ ] `safe_read_file()` returns `Optional[str]`, not raises
- [ ] `Optional` imported from typing
- [ ] All paths use project root detection
- [ ] `encoding="utf-8"` on all file reads
- [ ] `-> None` on all test methods
- [ ] Constants defined at module level (no magic numbers)
- [ ] Meaningful assertion messages
- [ ] Test classes with descriptive docstrings
- [ ] Empty except clauses have explanatory comments
- [ ] Use regex for structural assertions (not simple string matching)

## Checklist for Code Examples in Documentation

- [ ] All imports are explicitly listed at top
- [ ] No undefined type hints (datetime, AsyncSession, etc.)
- [ ] Dependencies explained with comments (get_db, User model)
- [ ] Uses proper validators (EmailStr, not regex for email)
- [ ] Could be copy-pasted and would run
- [ ] Bash examples include both if and else branches when applicable

## Documentation Quality Standards

### Avoid Exact Percentages in Summary Tables

Exact percentages in overview/summary tables cause maintenance toil. Every time underlying metrics change, the summary must be updated.

```markdown
<!-- WRONG - Exact percentages cause toil -->
| Case Study | Domain | Metrics | Status |
|------------|--------|---------|--------|
| Workflow Hook System | DevTools | 40% rework reduction | Complete |
| Constitution Templates | CLI | 35% faster implementation | Complete |
```

```markdown
<!-- CORRECT - Qualitative descriptions -->
| Case Study | Domain | Key Outcome | Status |
|------------|--------|-------------|--------|
| Workflow Hook System | DevTools | Significant rework reduction | Complete |
| Constitution Templates | CLI | Faster implementation | Complete |
```

**Why**: When the case study is updated with new metrics, only that case study needs to change - not the summary table in README.

### Completed Documentation Should Only Have Completed Tasks

Case studies or project documentation marked "Complete" should NOT include:
- Tasks marked "In Progress"
- Tasks marked "Planned"
- Tasks with no time spent

```markdown
<!-- WRONG - Incomplete tasks in "completed" case study -->
### Task List
| Task ID | Title | Status | Time |
|---------|-------|--------|------|
| task-255 | Scanner Orchestration | Done | 2h |
| task-256 | AI Triage Engine | In Progress | 4h |  <!-- BAD! -->
| task-258 | Security MCP Server | Planned | - |  <!-- BAD! -->
```

```markdown
<!-- CORRECT - Only completed tasks, with note about future work -->
### Task List
| Task ID | Title | Status | Time |
|---------|-------|--------|------|
| task-255 | Scanner Orchestration | Done | 2h |
| task-257 | Unified Finding Format | Done | 2h |

*Note: Additional tasks (AI Triage Engine, Security MCP Server) are planned for future iterations.*
```

## NEVER CLAIM CODE WORKS WITHOUT TESTING

The root cause of these issues is claiming code is complete without actually running it. This is unacceptable.

### Verification Requirements

1. **For test files**: Actually run `pytest` and verify tests pass
2. **For code examples**: Verify imports exist and types are correct
3. **For lint**: Actually run `ruff check` AND `ruff format --check` (both must pass!)
4. **For the full suite**: Run the complete test suite before claiming "done"

### Pre-Commit Checklist (MANDATORY)

Before EVERY commit, run these commands:

```bash
# 1. Run lint check
uv run ruff check .

# 2. Run format check (NOT just ruff check - they are different!)
uv run ruff format --check .

# 3. If format check fails, fix it:
uv run ruff format .

# 4. Run tests
uv run pytest tests/

# 5. Commit with DCO sign-off (required for CI)
git commit -s -m "commit message"
```

**CRITICAL**: `ruff check` and `ruff format --check` are DIFFERENT commands:
- `ruff check` - finds code quality issues (unused imports, etc.)
- `ruff format --check` - finds formatting issues (line length, spacing, etc.)

Both must pass for CI to succeed. Running only one is NOT sufficient.

### What "Testing Passed" Means

- NOT: "I think it would pass"
- NOT: "It looks correct"
- NOT: "The structure is right"
- YES: "I ran `pytest` and saw all tests pass"
- YES: "I ran `ruff check` and there were no errors"

### Common Mistakes to Avoid

- "All 28 tests pass" (without running them)
- "Lint passes" (ran `ruff check` but not `ruff format --check`)
- "This would work" (without verifying imports exist)
- Forgetting DCO sign-off (`git commit -s` required)

If you say tests pass, you MUST have run them. Period.

### CI Failures and Their Causes

| CI Check | Command | Common Failure Cause |
|----------|---------|---------------------|
| lint | `ruff check` | Unused imports, undefined names |
| lint | `ruff format --check` | Line too long, spacing issues |
| DCO | n/a | Missing `-s` flag on commit |
| test | `pytest` | Actual test failures |
| build | `uv build` | Syntax errors, missing deps |
