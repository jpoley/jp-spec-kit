---
description: Conduct code review with acceptance criteria verification.
loop: inner
# Loop Classification: INNER LOOP
# This command performs code review after implementation.
---

## User Input

```text
$ARGUMENTS
```

## Execution Instructions

This command conducts code review after implementation, verifying code quality and acceptance criteria completion.

### Prerequisites

Before running this command:
1. Implementation must be complete (`/flow:build`)
2. Code must be committed or staged for review

### Frontend Code Review

For UI/mobile code, launch frontend code reviewer:

**Agent Identity**: @frontend-code-reviewer

**Review Focus Areas**:
1. **Functionality**: Correctness, edge cases, error handling, Hook rules
2. **Performance**: Re-renders, bundle size, code splitting, memoization, Web Vitals
3. **Accessibility**: WCAG 2.1 AA compliance, semantic HTML, keyboard navigation
4. **Code Quality**: Readability, TypeScript types, component architecture
5. **Testing**: Coverage, test quality, integration tests
6. **Security**: XSS prevention, input validation, dependency vulnerabilities

**AC Verification (REQUIRED)**:
1. Review task ACs: `backlog task <task-id> --plain`
2. Verify each checked AC has corresponding code changes
3. Uncheck ACs if not satisfied: `backlog task edit <task-id> --uncheck-ac <N>`
4. Add review notes: `backlog task edit <task-id> --append-notes $'Code Review:\n- Issue: ...'`

### Backend Code Review

For API/services code, launch backend code reviewer:

**Agent Identity**: @backend-code-reviewer

**Review Focus Areas**:
1. **Security**: Authentication, authorization, injection prevention, secrets
2. **Performance**: Database optimization (N+1, indexes), scalability
3. **Code Quality**: Error handling, type safety, readability
4. **API Design**: RESTful patterns, versioning, error responses
5. **Database**: Schema design, migrations, query efficiency
6. **Testing**: Coverage, integration tests, edge cases

**Code Hygiene Checks (BLOCKING)**:

These MUST block merge if failed:
- **Unused imports**: Run `ruff check --select F401` (Python)
- **Unused variables**: Run `ruff check --select F841` (Python)
- **Missing input validation** on boundary functions
- **Missing type hints** on public Python functions
- **Ignored errors** in Go code

**AC Verification (REQUIRED)**:
1. Review task ACs: `backlog task <task-id> --plain`
2. Verify each checked AC has corresponding code changes
3. Uncheck ACs if not satisfied: `backlog task edit <task-id> --uncheck-ac <N>`
4. Add review notes: `backlog task edit <task-id> --append-notes $'Code Review:\n- Issue: ...'`

### Review Feedback Categories

Categorize all feedback by severity:

| Severity | Description | Action |
|----------|-------------|--------|
| **Critical** | Must fix before merge (unused imports, security issues) | BLOCKING |
| **High** | Should fix before merge | Strongly recommended |
| **Medium** | Address soon | Track for follow-up |
| **Low** | Nice to have | Optional improvement |

### Review Output

Provide structured review output:

```markdown
## Code Review Summary

### Critical Issues (BLOCKING)
- [ ] Issue 1: Description and fix suggestion

### High Priority
- [ ] Issue 2: Description and fix suggestion

### Medium Priority
- [ ] Issue 3: Description and suggestion

### Positive Observations
- Good pattern usage in X
- Clean separation of concerns in Y

### AC Verification
- [x] AC 1: Verified in file.ts
- [x] AC 2: Verified in api.py
- [ ] AC 3: NOT VERIFIED - missing implementation
```

### Iteration

After review:
1. **Address Critical issues** - Must fix before proceeding
2. **Address High issues** - Should fix before merge
3. **Re-review if significant changes** - Request another review pass

### Composability

This command can be invoked:
- Standalone: `/flow:review` for manual code review
- As part of `/flow:implement` orchestration
- Iteratively after addressing feedback
