# Security Rules

Rules for secure coding practices. These apply to all code in the project.

## No Hardcoded Secrets

Never commit:
- API keys, tokens, passwords
- Database connection strings with credentials
- Private keys or certificates
- Environment-specific secrets

Use environment variables or secret managers instead.

## Input Validation

- Validate all external inputs at boundaries
- Use Pydantic models for request validation
- Never trust user input

```python
# Good: Use typed validators
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr  # Robust validation, not regex
    name: str = Field(..., min_length=1, max_length=100)

# Bad: Weak regex patterns (e.g., allows 'user@domain..com' and accepts invalid/overly short TLDs)
email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
```

## Injection Prevention

- Use parameterized queries for databases
- Never string-interpolate SQL, shell commands, or templates
- Escape output appropriately for context (HTML, JSON, shell)

```python
# Good: Parameterized query
await db.scalar(select(User).where(User.email == email))

# Bad: String interpolation
await db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

## Pattern Matching in Security Code

When writing heuristic classifiers or security scanners:
1. Consider adversarial examples - what else could match?
2. Add context requirements (same line, surrounding patterns)
3. Use negative patterns to exclude known false matches
4. Never return early on a single pattern

## Exception Handling

- Log exceptions with context using `logger.warning()` or `logger.error()`
- Include relevant data (truncated to reasonable size)
- Never silently swallow exceptions

```python
# Good: Log all exceptions with context
except httpx.TimeoutException:
    logger.debug(f"Timeout fetching {url}")
except Exception as e:
    logger.debug(f"Unexpected error: {e}")
return None

# Bad: Silent swallowing
except Exception:
    pass
```

## File Path Operations

- Use absolute paths resolved from a known root
- Find the actual git root, don't assume paths
- Validate paths before operations

## Sensitive Data Logging

Never log:
- Passwords or tokens
- Personal identifiable information (PII)
- Full request/response bodies with sensitive fields

Truncate or redact sensitive fields before logging.
