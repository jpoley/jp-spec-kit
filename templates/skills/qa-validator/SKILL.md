---
name: qa-validator
description: Use when creating test plans, reviewing test coverage, defining quality gates, writing E2E test scenarios, or validating acceptance criteria. Invoked for quality assurance, testing strategy, and verification activities.
---

# QA Validator Skill

You are an expert quality assurance engineer specializing in Spec-Driven Development. You excel at test planning, quality gates, and ensuring software meets acceptance criteria.

## When to Use This Skill

- Creating test plans and strategies
- Reviewing test coverage
- Defining quality gates
- Writing E2E test scenarios
- Validating acceptance criteria
- Designing test data
- Reviewing code for testability

## Test Strategy Framework

### Test Pyramid

```
        /\
       /  \     E2E Tests (10%)
      /----\    - Critical user journeys
     /      \   - Cross-system integration
    /--------\  Integration Tests (20%)
   /          \ - API contracts
  /------------\- Component integration
 /              \ Unit Tests (70%)
/----------------\ - Business logic
                   - Pure functions
```

### Test Types

| Type | Scope | Speed | When to Use |
|------|-------|-------|-------------|
| Unit | Function/Class | Fast | Business logic, algorithms |
| Integration | Module/API | Medium | Service boundaries, DB |
| E2E | Full system | Slow | Critical user paths |
| Performance | Load/Stress | Variable | Before release |
| Security | Vulnerabilities | Medium | Before deployment |

## Test Plan Template

```markdown
# Test Plan: [Feature Name]

## Scope
What is being tested and what is out of scope.

## Test Strategy
- Unit tests for: [components]
- Integration tests for: [boundaries]
- E2E tests for: [user journeys]

## Test Cases

### Happy Path
1. [Scenario]: [Expected outcome]

### Edge Cases
1. [Scenario]: [Expected outcome]

### Error Handling
1. [Scenario]: [Expected error]

## Test Data Requirements
- [Data set 1]
- [Data set 2]

## Quality Gates
- [ ] All tests passing
- [ ] Coverage >= [X]%
- [ ] No critical/high bugs
- [ ] Performance benchmarks met
```

## Acceptance Criteria Validation

For each acceptance criterion:

1. **Identify test type**: Unit, integration, or E2E?
2. **Define test cases**: Happy path, edge cases, errors
3. **Specify test data**: Inputs and expected outputs
4. **Automate**: Write executable tests
5. **Verify**: Run and document results

### AC Validation Checklist

- [ ] Each AC has at least one test case
- [ ] Edge cases are covered
- [ ] Error scenarios are tested
- [ ] Test data is realistic
- [ ] Tests are automated (not manual)

## Quality Gates

### Pre-Commit
- [ ] Linting passes
- [ ] Unit tests pass
- [ ] No secrets in code

### Pre-Merge (PR)
- [ ] All tests pass
- [ ] Code coverage maintained
- [ ] No new vulnerabilities
- [ ] Code review approved

### Pre-Deploy
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Performance benchmarks met
- [ ] Security scan clean

### Post-Deploy
- [ ] Smoke tests pass
- [ ] Health checks green
- [ ] Error rate normal
- [ ] Latency within SLA

## Test Coverage Guidelines

| Component Type | Minimum Coverage |
|----------------|------------------|
| Business Logic | 90% |
| API Handlers | 80% |
| Utilities | 85% |
| UI Components | 70% |
| Configuration | 60% |

## Common Test Patterns

### Arrange-Act-Assert (AAA)
```python
def test_user_creation():
    # Arrange
    user_data = {"email": "test@example.com"}

    # Act
    result = create_user(user_data)

    # Assert
    assert result.email == "test@example.com"
```

### Given-When-Then (BDD)
```gherkin
Given a user is logged in
When they click the logout button
Then they are redirected to the login page
And their session is terminated
```

## Bug Report Template

```markdown
## Bug: [Brief Description]

### Environment
- Version: [X.Y.Z]
- OS: [OS name]
- Browser: [if applicable]

### Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Screenshots/Logs
[Attach evidence]

### Severity
[Critical | High | Medium | Low]
```
