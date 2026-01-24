# Agent Delegation Rules

Rules for when and how to use subagents.

## Available Agents

| Agent | Location | Expertise |
|-------|----------|-----------|
| backend-engineer | `.claude/agents/backend-engineer.md` | Python, APIs, databases |
| frontend-engineer | `.claude/agents/frontend-engineer.md` | React, TypeScript, UI |
| qa-engineer | `.claude/agents/qa-engineer.md` | Testing, coverage, E2E |
| security-reviewer | `.claude/agents/security-reviewer.md` | OWASP, SLSA, scanning |

## When to Delegate

**Use subagents when**:
- Task requires specialized domain expertise
- Work can be parallelized (frontend + backend)
- Security review is needed (security-reviewer)
- Test coverage needs assessment (qa-engineer)

**Don't delegate when**:
- Simple, single-domain task
- Quick fix or small change
- Overhead exceeds benefit

## Agent Selection by Task Labels

Tasks labeled `backend` -> backend-engineer
Tasks labeled `frontend` -> frontend-engineer
All implementation tasks -> qa-engineer (for tests)
All implementation tasks -> security-reviewer (read-only review)

## Parallel Execution

When tasks can be parallelized:

```bash
backlog task edit <task-id> -l "parallel-work:frontend,backend"
```

Frontend and backend engineers can work simultaneously on separate worktrees.

## Security Reviewer Constraints

Security reviewer has **read-only** access:
- Analyzes and reports findings
- Does NOT make code changes
- Findings must be addressed by implementation agents

## Agent Workflow Integration

Agents are invoked during `/flow:implement`:

1. Orchestrator reads task labels
2. Assigns appropriate agents
3. Agents work in parallel where possible
4. Results aggregated for review

## Context Handoff

When delegating to agents:
- Include task ID and acceptance criteria
- Reference relevant PRDs and specs
- Specify expected outputs
- Set clear boundaries

## Quality Gates

All agent work must pass:
- Code review by another agent or human
- Security review (automated or manual)
- Test coverage requirements
- Lint and format checks
