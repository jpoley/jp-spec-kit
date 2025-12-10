---
description: Execute tests and generate test coverage reports.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command provides guidance for running tests, analyzing coverage, and ensuring code quality through comprehensive testing.

### Test Pyramid Strategy

```
        /\
       /  \      E2E Tests (Few)
      /____\     - End-to-end user scenarios
     /      \    - Browser/API integration
    /        \   - Slow, expensive, brittle
   /__________\
  /            \ Integration Tests (Some)
 /              \ - Multiple units together
/________________\- Database, API, services
|                |
|                | Unit Tests (Many)
|  UNIT TESTS    | - Individual functions/classes
|________________| - Fast, isolated, deterministic
```

### Running Tests

**Python (pytest)**:
```bash
# Run all tests
pytest tests/

# Run specific file
pytest tests/test_users.py

# Run specific test
pytest tests/test_users.py::test_create_user

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run with verbose output
pytest tests/ -v

# Stop on first failure
pytest tests/ -x

# Run only failed tests from last run
pytest tests/ --lf

# Parallel execution
pytest tests/ -n auto
```

**TypeScript/JavaScript (Vitest)**:
```bash
# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run with coverage
npm test -- --coverage

# Run specific file
npm test -- users.test.ts

# Update snapshots
npm test -- --update
```

**Go**:
```bash
# Run all tests
go test ./...

# Run with coverage
go test ./... -cover

# Run specific test
go test -run TestCreateUser ./...

# Verbose output
go test -v ./...

# Coverage report
go test ./... -coverprofile=coverage.out
go tool cover -html=coverage.out
```

### Test Coverage Analysis

**Coverage Goals**:
- Overall: 80% minimum
- Critical paths: 95%+
- New code: 90%+
- Legacy code: Gradual improvement

**Coverage Report**:
```bash
# Python
pytest tests/ --cov=src --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html

# TypeScript
npm test -- --coverage
open coverage/index.html

# Go
go test ./... -coverprofile=coverage.out
go tool cover -html=coverage.out
```

**Analyze Coverage**:
- Identify untested paths
- Focus on high-risk areas
- Prioritize critical functionality
- Don't chase 100% blindly

### Test Quality Metrics

**Good Tests Are**:
1. **Fast**: Run in milliseconds
2. **Isolated**: No dependencies between tests
3. **Repeatable**: Same result every time
4. **Self-Checking**: Pass/fail automatically
5. **Timely**: Written with or before code

**Test Smells**:
- Slow tests (> 1 second for unit test)
- Flaky tests (random failures)
- Tests depending on order
- Tests with hardcoded data
- Tests with complex setup
- Tests testing multiple things

### Writing Effective Tests

**Unit Test Example (Python)**:
```python
import pytest
from src.users import create_user, UserValidationError

def test_create_user_success():
    """Test successful user creation."""
    user = create_user(email="test@example.com", name="Test User")

    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.id is not None
    assert user.created_at is not None

def test_create_user_invalid_email():
    """Test user creation fails with invalid email."""
    with pytest.raises(UserValidationError) as exc:
        create_user(email="invalid", name="Test User")

    assert "Invalid email format" in str(exc.value)

def test_create_user_duplicate_email(db_session):
    """Test user creation fails with duplicate email."""
    # Create first user
    create_user(email="test@example.com", name="User 1")

    # Attempt duplicate
    with pytest.raises(UserValidationError) as exc:
        create_user(email="test@example.com", name="User 2")

    assert "Email already exists" in str(exc.value)
```

**Integration Test Example (Python)**:
```python
import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_user_registration_flow():
    """Test complete user registration flow."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Register new user
        response = await client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "name": "New User",
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == 201
        user_id = response.json()["id"]

        # Verify user can login
        response = await client.post(
            "/auth/login",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == 200
        assert "token" in response.json()

        # Verify user profile accessible
        token = response.json()["token"]
        response = await client.get(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == "newuser@example.com"
```

**E2E Test Example (Playwright)**:
```typescript
import { test, expect } from '@playwright/test';

test('user can complete purchase flow', async ({ page }) => {
  // Navigate to product page
  await page.goto('/products/123');
  await expect(page.locator('h1')).toContainText('Product Name');

  // Add to cart
  await page.click('button:has-text("Add to Cart")');
  await expect(page.locator('.cart-count')).toHaveText('1');

  // Proceed to checkout
  await page.click('a:has-text("Cart")');
  await page.click('button:has-text("Checkout")');

  // Fill payment info
  await page.fill('#card-number', '4242424242424242');
  await page.fill('#expiry', '12/25');
  await page.fill('#cvv', '123');

  // Complete purchase
  await page.click('button:has-text("Complete Purchase")');

  // Verify success
  await expect(page.locator('.success-message')).toBeVisible();
  await expect(page.locator('.order-confirmation')).toContainText('Thank you');
});
```

### Test Organization

**Directory Structure**:
```
tests/
├── unit/                  # Unit tests
│   ├── test_users.py
│   ├── test_orders.py
│   └── test_utils.py
├── integration/           # Integration tests
│   ├── test_api.py
│   └── test_database.py
├── e2e/                   # End-to-end tests
│   ├── test_user_flows.py
│   └── test_checkout.py
├── fixtures/              # Test data
│   ├── users.json
│   └── orders.json
└── conftest.py           # Pytest configuration
```

### Test Data Management

**Fixtures (pytest)**:
```python
import pytest
from src.database import create_db, drop_db

@pytest.fixture
def db_session():
    """Provide clean database session for each test."""
    db = create_db()
    yield db
    drop_db(db)

@pytest.fixture
def sample_user():
    """Provide sample user data."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "age": 30
    }

@pytest.fixture
def authenticated_client(client, db_session):
    """Provide authenticated API client."""
    # Create user
    user = create_user(email="test@example.com", password="pass123")
    # Login
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "pass123"
    })
    token = response.json()["token"]
    # Return client with auth header
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

### Continuous Testing

**Pre-commit Hook**:
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running tests..."
pytest tests/ -x -q

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi

echo "Running linter..."
ruff check .

if [ $? -ne 0 ]; then
    echo "Linting failed. Commit aborted."
    exit 1
fi

echo "All checks passed!"
```

**CI Pipeline**:
```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Test Quality Checklist

Before marking testing complete:
- [ ] All critical paths have tests
- [ ] Coverage meets project minimum (typically 80%)
- [ ] Tests are fast (< 1s for unit tests)
- [ ] No flaky tests
- [ ] Tests are well-organized
- [ ] Test names clearly describe what they test
- [ ] Tests follow AAA pattern (Arrange, Act, Assert)
- [ ] Edge cases and error scenarios tested
- [ ] Integration tests for key flows
- [ ] E2E tests for critical user journeys

## Related Commands

- `/qa:verify` - Verify implementation meets requirements
- `/qa:review` - Code review and quality assessment
- `/dev:build` - Implementation
- `/sec:scan` - Security testing
