# Acceptance Criteria Test Marking Guide

This guide explains how to mark tests with acceptance criteria references across different programming languages and testing frameworks.

## Overview

The AC test marking system ensures that every acceptance criterion in your PRD has corresponding runnable tests. This is enforced during workflow transitions from "In Implementation" to "Validated".

## Python (pytest)

### Marker Syntax

Use the `@pytest.mark.ac()` decorator:

```python
import pytest

@pytest.mark.ac("AC1: User can register with email and password")
def test_user_registration():
    """Test user registration with email."""
    # Test implementation
    pass

@pytest.mark.ac("AC2: Password must be at least 8 characters")
def test_password_minimum_length():
    """Test password validation."""
    # Test implementation
    pass
```

### Rules

1. **Marker format**: `@pytest.mark.ac("ACX: Description")`
2. **AC ID**: Must match the PRD exactly (e.g., "AC1", "AC2", "AC10")
3. **Description**: Full description from PRD (can be abbreviated if clear)
4. **One marker per test**: Each test function should mark one primary AC
5. **Multiple tests per AC**: Multiple tests can cover the same AC

### Examples

```python
# Single AC, single test
@pytest.mark.ac("AC3: Email verification required before login")
def test_email_verification_required():
    assert not can_login_without_verification()

# Same AC, multiple test cases
@pytest.mark.ac("AC4: Login fails with invalid credentials")
def test_login_with_wrong_password():
    assert login("user@example.com", "wrong") == LoginResult.FAILED

@pytest.mark.ac("AC4: Login fails with invalid credentials")
def test_login_with_nonexistent_email():
    assert login("nobody@example.com", "pass") == LoginResult.FAILED

# Parameterized tests
@pytest.mark.ac("AC5: Password validation rules")
@pytest.mark.parametrize("password,valid", [
    ("short", False),
    ("longenough", True),
    ("with spaces", False),
])
def test_password_validation(password, valid):
    assert validate_password(password) == valid
```

## TypeScript (Jest/Vitest)

### Marker Syntax

Use comment annotations `// @ac ACX: Description`:

```typescript
describe("User Authentication", () => {
  // @ac AC1: User can register with email and password
  it("should allow registration with valid email", () => {
    const result = registerUser("test@example.com", "password123");
    expect(result.success).toBe(true);
  });

  // @ac AC2: Password must be at least 8 characters
  it("should reject short passwords", () => {
    const result = registerUser("test@example.com", "short");
    expect(result.error).toBe("PASSWORD_TOO_SHORT");
  });
});
```

### Rules

1. **Comment format**: `// @ac ACX: Description`
2. **Placement**: Comment must appear immediately before the `it()` or `test()` block
3. **Case sensitivity**: AC ID must match exactly
4. **Whitespace**: Single space after `@ac` recommended

### Examples

```typescript
// Multiple tests for same AC
describe("Login Validation", () => {
  // @ac AC4: Login fails with invalid credentials
  test("login with wrong password fails", () => {
    expect(login("user@example.com", "wrong")).toEqual({
      success: false,
      error: "INVALID_CREDENTIALS",
    });
  });

  // @ac AC4: Login fails with invalid credentials
  test("login with unknown email fails", () => {
    expect(login("unknown@example.com", "pass")).toEqual({
      success: false,
      error: "INVALID_CREDENTIALS",
    });
  });
});

// Nested describe blocks
describe("Email Verification", () => {
  describe("before verification", () => {
    // @ac AC3: Email verification required before login
    it("should block login attempts", () => {
      expect(canLogin(unverifiedUser)).toBe(false);
    });
  });
});
```

## Go (testing package)

### Marker Syntax

Use comment annotations in test functions:

```go
package auth

import "testing"

func TestUserRegistration(t *testing.T) {
    // AC1: User can register with email and password
    t.Run("valid_registration", func(t *testing.T) {
        user, err := RegisterUser("test@example.com", "password123")
        if err != nil {
            t.Errorf("expected successful registration, got error: %v", err)
        }
    })
}

func TestPasswordValidation(t *testing.T) {
    // AC2: Password must be at least 8 characters
    t.Run("password_minimum_length", func(t *testing.T) {
        _, err := RegisterUser("test@example.com", "short")
        if err == nil {
            t.Error("expected password validation error")
        }
    })
}
```

### Rules

1. **Comment format**: `// ACX: Description`
2. **Placement**: Comment at the start of test function or subtest
3. **Subtests recommended**: Use `t.Run()` for organizing multiple cases per AC

### Examples

```go
// Multiple subtests for same AC
func TestLoginValidation(t *testing.T) {
    // AC4: Login fails with invalid credentials
    t.Run("wrong_password", func(t *testing.T) {
        result := Login("user@example.com", "wrong")
        if result.Success {
            t.Error("expected login to fail with wrong password")
        }
    })

    // AC4: Login fails with invalid credentials
    t.Run("unknown_email", func(t *testing.T) {
        result := Login("unknown@example.com", "pass")
        if result.Success {
            t.Error("expected login to fail with unknown email")
        }
    })
}

// Table-driven tests
func TestPasswordRules(t *testing.T) {
    // AC5: Password validation rules
    tests := []struct {
        name     string
        password string
        wantErr  bool
    }{
        {"too_short", "short", true},
        {"valid_length", "longenough", false},
        {"with_spaces", "has spaces", true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := ValidatePassword(tt.password)
            if (err != nil) != tt.wantErr {
                t.Errorf("ValidatePassword() error = %v, wantErr %v", err, tt.wantErr)
            }
        })
    }
}
```

## Checking Coverage

### Manual Check

```bash
# Check coverage for current feature
specify ac-coverage --check

# Check specific feature
specify ac-coverage --feature user-auth --check

# Generate report without validation
specify ac-coverage --output coverage.json

# Allow partial coverage (exceptional cases)
specify ac-coverage --check --allow-partial-coverage
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# GitHub Actions
- name: Check AC Coverage
  run: specify ac-coverage --check

# GitLab CI
ac-coverage:
  script:
    - specify ac-coverage --check
```

### Coverage Report Format

The `ac-coverage.json` manifest contains:

```json
{
  "feature": "user-authentication",
  "prd_path": "./docs/prd/user-authentication.md",
  "generated_at": "2025-11-30T20:30:00Z",
  "acceptance_criteria": [
    {
      "id": "AC1",
      "description": "User can register with email and password",
      "user_story": "US1",
      "tests": [
        "tests/test_auth.py::test_user_registration"
      ],
      "status": "covered"
    },
    {
      "id": "AC2",
      "description": "Password minimum 8 characters",
      "user_story": "US1",
      "tests": [],
      "status": "uncovered"
    }
  ],
  "summary": {
    "total_acs": 6,
    "covered": 5,
    "uncovered": 1,
    "coverage_percent": 83.3
  }
}
```

## Best Practices

### 1. Mark Tests During Implementation

Add AC markers as you write tests, not after:

```python
# Good - Mark immediately
@pytest.mark.ac("AC1: Feature description")
def test_new_feature():
    pass

# Bad - Written test without marker (will fail coverage check)
def test_new_feature():
    pass
```

### 2. One Primary AC Per Test

Each test should verify one primary acceptance criterion:

```python
# Good - Single AC focus
@pytest.mark.ac("AC1: User registration")
def test_user_registration():
    assert register_user("test@example.com", "pass123")

# Acceptable - Helper test for same AC
@pytest.mark.ac("AC1: User registration")
def test_registration_duplicate_email_rejected():
    assert not register_user("existing@example.com", "pass123")

# Bad - Testing multiple unrelated ACs
def test_everything():
    assert register_user(...)  # AC1
    assert login(...)          # AC4
    assert change_password(...)  # AC7
```

### 3. Match AC IDs Exactly

```python
# Good - Exact match
@pytest.mark.ac("AC1: Description")

# Bad - Wrong ID
@pytest.mark.ac("AC01: Description")  # Should be AC1
@pytest.mark.ac("ac1: Description")   # Wrong case
```

### 4. Use Descriptive Test Names

```python
# Good - Clear test purpose
@pytest.mark.ac("AC3: Email verification required")
def test_login_blocked_without_email_verification():
    pass

# Acceptable
@pytest.mark.ac("AC3: Email verification required")
def test_email_verification_required():
    pass

# Bad - Unclear purpose
@pytest.mark.ac("AC3: Email verification required")
def test_ac3():
    pass
```

### 5. Document Exceptional Cases

If you need `--allow-partial-coverage`:

```bash
# Create .ac-coverage-exception file
echo "AC10: Performance optimization - benchmarking not yet automated" > .ac-coverage-exception

# Document in PR
specify ac-coverage --check --allow-partial-coverage
```

## Troubleshooting

### "AC not found in tests"

```
Error: AC3 is uncovered
  AC3: Email verification required before login
```

**Solution**: Add marker to your test:

```python
@pytest.mark.ac("AC3: Email verification required before login")
def test_email_verification():
    pass
```

### "Test not detected"

If your test has the marker but isn't detected:

1. **Check test file naming**: Must match `test_*.py`, `*_test.py`, `*.test.ts`, `*_test.go`
2. **Check test directory**: Default is `./tests/`, use `--test-dirs` to specify others
3. **Check marker syntax**: Must be exact format for your language

### "Duplicate AC markers"

Multiple tests can mark the same AC (this is fine):

```python
@pytest.mark.ac("AC4: Login validation")
def test_wrong_password():
    pass

@pytest.mark.ac("AC4: Login validation")
def test_wrong_email():
    pass
```

Both tests will be listed in the coverage report.

## Migration Guide

### Adding AC Coverage to Existing Project

1. **Add markers to existing tests**:
   ```bash
   # Review PRD
   cat docs/prd/feature.md

   # Mark tests one AC at a time
   # Edit tests/test_auth.py and add markers
   ```

2. **Check coverage incrementally**:
   ```bash
   specify ac-coverage
   # Review uncovered ACs
   # Add tests for uncovered ACs
   ```

3. **Enforce in CI once complete**:
   ```yaml
   - name: AC Coverage Check
     run: specify ac-coverage --check
   ```

### Handling Legacy Tests

For tests written before AC tracking:

```python
# Option 1: Map existing test to AC
@pytest.mark.ac("AC1: User registration")  # Added
def test_user_can_register():  # Existing test
    pass

# Option 2: Write new AC-focused test
@pytest.mark.ac("AC1: User registration")
def test_ac1_user_registration():  # New test
    test_user_can_register()  # Calls existing
```

## Summary

- **Python**: `@pytest.mark.ac("ACX: Description")`
- **TypeScript**: `// @ac ACX: Description`
- **Go**: `// ACX: Description`
- **Check coverage**: `specify ac-coverage --check`
- **100% coverage required** for workflow transitions
- **One AC per test** (multiple tests per AC is fine)
- **Mark during implementation**, not after
