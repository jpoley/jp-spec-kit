# Python FastAPI Project Constitution Example

This example shows a customized constitution for a Python FastAPI project.

## Before: Template

```markdown
## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]
<!-- SECTION:TECH_STACK:END -->
```

## After: Customized

```markdown
## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
- **Primary Language**: Python 3.11+
- **Framework**: FastAPI 0.100+
- **Package Manager**: uv
- **Database**: PostgreSQL with SQLAlchemy
- **Async Runtime**: uvicorn
<!-- SECTION:TECH_STACK:END -->

## Quality Standards
<!-- SECTION:QUALITY:BEGIN -->
- Test coverage minimum: 80%
- All endpoints must have OpenAPI documentation
- Type hints required on all public functions
- Pydantic models for all request/response schemas
- Async/await for all I/O operations
<!-- SECTION:QUALITY:END -->

## Testing
<!-- SECTION:TESTING:BEGIN -->
- Framework: pytest with pytest-asyncio
- Fixtures: conftest.py for shared fixtures
- Coverage: pytest-cov with 80% threshold
- Integration tests for all API endpoints
- Test database: SQLite for fast test execution
<!-- SECTION:TESTING:END -->

## Code Quality
<!-- SECTION:CODE_QUALITY:BEGIN -->
- Linter: ruff (replaces flake8, isort, black)
- Formatter: ruff format
- Type checker: mypy (strict mode)
- Pre-commit hooks enforced
- Security: bandit + safety scans
<!-- SECTION:CODE_QUALITY:END -->

## CI/CD
<!-- SECTION:CICD:BEGIN -->
- Platform: GitHub Actions
- Workflows: test.yml, release.yml
- Deploy: Docker containers to Kubernetes
- SLSA Level 2 compliance
- Container scanning with Trivy
<!-- SECTION:CICD:END -->

## API Standards
<!-- SECTION:API:BEGIN -->
- All endpoints return consistent error responses
- Use HTTP status codes correctly
- Implement pagination for list endpoints
- Rate limiting on public endpoints
- Request/response logging with correlation IDs
<!-- SECTION:API:END -->

## Security
<!-- SECTION:SECURITY:BEGIN -->
- Never log sensitive data (passwords, tokens, PII)
- Use parameterized queries (prevent SQL injection)
- Validate and sanitize all inputs
- Hash passwords with bcrypt/argon2
- Implement CORS with explicit origins
- Security headers (HSTS, CSP, X-Frame-Options)
<!-- SECTION:SECURITY:END -->
```

## repo-facts.md Generated

```yaml
---
detected_at: "2025-12-04T10:30:00"
languages:
  - Python
frameworks:
  - FastAPI
  - SQLAlchemy
  - Pydantic
package_manager: uv
ci_cd: GitHub Actions
test_framework: pytest
linter: ruff
formatter: ruff
type_checker: mypy
security_tools:
  - bandit
  - safety
deployment: Docker + Kubernetes
---
```

## Key Customization Points

1. **Technology Stack**: Specific Python version, FastAPI, uv package manager
2. **Quality Standards**: 80% coverage, type hints, Pydantic schemas
3. **Testing**: pytest-asyncio for async tests, SQLite test database
4. **Code Quality**: Ruff for linting/formatting (modern Python tooling)
5. **Security**: Explicit security requirements for API endpoints
6. **API Standards**: Custom section for API-specific requirements

## Usage

```bash
# After running /speckit:constitution
specify constitution validate

# Apply customizations from this example
# Edit .specify/memory/constitution.md
# Replace template sections with customized versions
```
