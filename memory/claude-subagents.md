# Claude Code Subagents

JP Spec Kit includes specialized subagents for parallel and isolated task execution. Subagents have their own context window and tool restrictions.

## How Subagents Work

Subagents are invoked using the Task tool with `subagent_type` parameter. Each subagent:
- Has an independent context window (preserves main context)
- Can be restricted to specific tools via `tools` frontmatter
- Runs in parallel with other subagents
- Returns results to the main agent

## Engineering Subagents

### 1. Frontend Engineer (`frontend-engineer`)

**Location**: `.claude/agents/frontend-engineer.md`

**Invoke when**:
- Creating React/Next.js components
- Implementing UI features
- Fixing browser/interaction bugs
- Writing frontend tests

**Tools**: `Read, Write, Edit, Glob, Grep, Bash`

**Expertise**:
- React 18+, Next.js 14+, TypeScript
- Tailwind CSS, CSS Modules
- Accessibility (WCAG AA)
- Vitest, React Testing Library, Playwright

### 2. Backend Engineer (`backend-engineer`)

**Location**: `.claude/agents/backend-engineer.md`

**Invoke when**:
- Creating API endpoints
- Database operations and optimization
- Business logic implementation
- Backend testing

**Tools**: `Read, Write, Edit, Glob, Grep, Bash`

**Expertise**:
- Python 3.11+, FastAPI, SQLAlchemy
- PostgreSQL, SQLite, migrations
- pytest, pytest-asyncio
- API security, validation

### 3. QA Engineer (`qa-engineer`)

**Location**: `.claude/agents/qa-engineer.md`

**Invoke when**:
- Writing test suites
- Improving test coverage
- Setting up test infrastructure
- E2E test implementation

**Tools**: `Read, Write, Edit, Glob, Grep, Bash`

**Expertise**:
- pytest, Vitest, Playwright
- Test pyramid strategy
- Coverage analysis
- CI/CD testing

### 4. Security Reviewer (`security-reviewer`)

**Location**: `.claude/agents/security-reviewer.md`

**Invoke when**:
- Security code review
- Vulnerability assessment
- SLSA compliance check
- Dependency audit

**Tools**: `Read, Glob, Grep, Bash` (read-only for security)

**Expertise**:
- OWASP Top 10
- SLSA compliance levels
- Threat modeling (STRIDE)
- Secure coding patterns

### 5. Project Manager (`project-manager-backlog`)

**Location**: `.claude/agents/project-manager-backlog.md`

**Invoke when**:
- Creating backlog tasks
- Breaking down features
- Task quality review
- Backlog management

**Tools**: All tools (default)

**Expertise**:
- Backlog.md CLI
- Atomic task creation
- Acceptance criteria
- Task breakdown strategies

## Using Subagents

### Invoke via Task Tool

```
Use the Task tool with subagent_type="frontend-engineer" to implement
the user profile component.
```

### Parallel Execution

Subagents can run in parallel for independent tasks:

```
1. Frontend: Implement UI components
2. Backend: Create API endpoints
3. QA: Write integration tests

All three can run simultaneously since they don't depend on each other.
```

### Tool Restrictions

Each subagent has appropriate tool restrictions:

| Subagent | Tools | Reason |
|----------|-------|--------|
| frontend-engineer | Read, Write, Edit, Glob, Grep, Bash | Full implementation access |
| backend-engineer | Read, Write, Edit, Glob, Grep, Bash | Full implementation access |
| qa-engineer | Read, Write, Edit, Glob, Grep, Bash | Test writing access |
| security-reviewer | Read, Glob, Grep, Bash | Read-only analysis |
| project-manager-backlog | All | Task management needs all tools |

## Subagent Best Practices

1. **Use for parallel work**: Launch multiple subagents for independent tasks
2. **Preserve main context**: Complex exploration should use subagents
3. **Match expertise**: Choose the right subagent for the task
4. **Review results**: Subagent output should be reviewed before integration
