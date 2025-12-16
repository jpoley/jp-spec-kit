# flowspec + Backlog.md Integration Guide

Complete guide to using `/flow` commands with backlog.md task management for end-to-end spec-driven development.

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Task Format for Flowspec Compatibility](#task-format-for-flowspec-compatibility)
- [Workflow State Transitions](#workflow-state-transitions)
- [Command Integration Reference](#command-integration-reference)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The `/flow` workflow system and backlog.md are deeply integrated to provide:

1. **State-Driven Commands**: Each `/flow` command validates task state before execution
2. **Automatic Task Discovery**: Commands search backlog for relevant tasks
3. **Progressive Task Creation**: Design commands create tasks; implementation commands consume them
4. **Acceptance Criteria Tracking**: Engineers check ACs as work progresses
5. **Full Traceability**: Requirements → Tasks → Implementation → Validation

### The Integration Flow

```
/flow:assess    →  Evaluate complexity (To Do → Assessed)
       ↓
/flow:specify   →  Create PRD + tasks (Assessed → Specified)
       ↓
/flow:research  →  Market validation (Specified → Researched)
       ↓
/flow:plan      →  Architecture design (Researched → Planned)
       ↓
/flow:implement →  Code development (Planned → In Implementation)
       ↓
/flow:validate  →  QA + security (In Implementation → Validated)
       ↓
/flow:operate   →  Deploy to production (Validated → Deployed)
```

## How It Works

### Design Commands Create Tasks

**Design commands** (`/flow:specify`, `/flow:research`, `/flow:plan`) create new tasks:

```bash
# /flow:specify creates implementation tasks
backlog task create "Implement user authentication" \
  -d "Core auth implementation per PRD section 4" \
  --ac "Implement OAuth2 flow" \
  --ac "Add JWT token validation" \
  --ac "Write unit tests" \
  -l backend,auth \
  --priority high

# /flow:plan creates architecture tasks
backlog task create "ADR: Authentication approach" \
  -d "Document OAuth2 vs SAML decision" \
  --ac "Document context and options" \
  --ac "Record decision and consequences" \
  -l architecture,adr \
  --priority high
```

### Implementation Commands Consume Tasks

**Implementation commands** (`/flow:implement`, `/flow:validate`, `/flow:operate`) work from existing tasks:

```bash
# Step 0: Discover existing tasks
backlog task list -s "To Do" --plain
backlog search "authentication" --plain

# Engineer workflow
backlog task edit task-42 -s "In Progress" -a @backend-engineer
# ... implement feature ...
backlog task edit task-42 --check-ac 1  # Mark AC complete
backlog task edit task-42 --check-ac 2
backlog task edit task-42 -s Done       # Only after ALL ACs checked
```

### State Validation

Before executing, each `/flowspec` command validates task state:

```bash
# This will ERROR if task is in wrong state
/flow:implement  # Requires task in "Planned" state

# Error message:
# Cannot run /flow:implement
#   Current state: "To Do"
#   Required states: Planned
# Suggestions:
#   - Run /flow:plan first
```

## Task Format for Flowspec Compatibility

### Required Fields

Tasks must include these fields for full `/flowspec` integration:

```markdown
---
id: task-042
title: Implement user authentication
status: To Do
priority: High
labels: [backend, auth, US1]
assignee: []
---

## Description

Implement user authentication system with OAuth2 support.

## Acceptance Criteria

- [ ] #1 Implement OAuth2 flow with Google provider
- [ ] #2 Add JWT token generation and validation
- [ ] #3 Write unit tests with 90% coverage
- [ ] #4 Add integration tests for auth flow
```

### Status Values

Use these exact status values for workflow compatibility:

| Status | Description | Used By |
|--------|-------------|---------|
| `To Do` | Created, not started | Initial state |
| `Assessed` | Complexity evaluated | After `/flow:assess` |
| `Specified` | PRD complete | After `/flow:specify` |
| `Researched` | Research validated | After `/flow:research` |
| `Planned` | Architecture designed | After `/flow:plan` |
| `In Progress` | Engineer working | During `/flow:implement` |
| `In Implementation` | Active coding | `/flow:implement` phase |
| `Validated` | QA + security passed | After `/flow:validate` |
| `Deployed` | In production | After `/flow:operate` |
| `Done` | All work complete | Final state |

### Labels for Traceability

Use labels to connect tasks to requirements:

```yaml
labels:
  # User story reference
  - US1      # Links to User Story 1 in PRD
  - US2      # Links to User Story 2

  # Task type
  - backend
  - frontend
  - architecture
  - infrastructure

  # Phase
  - setup
  - foundational
  - implementation
  - polish

  # Custom
  - blocking
  - parallelizable
```

### Acceptance Criteria Format

Write ACs in numbered checkbox format:

```markdown
## Acceptance Criteria

- [ ] #1 Users can register with email and password
- [ ] #2 Users can login with valid credentials
- [ ] #3 Invalid credentials return 401 error
- [ ] #4 Sessions expire after 15 minutes of inactivity
```

**Rules**:
- Minimum 2 ACs per task
- Each AC should be independently verifiable
- Use action verbs (implement, create, add, fix)
- Include measurable outcomes where possible

## Workflow State Transitions

### Valid Transitions

```
To Do ────────────────────────────────────────────────┐
   │                                                   │
   ↓ /flow:assess                                    │
Assessed                                               │
   │                                                   │
   ↓ /flow:specify                                   │
Specified ─────────────────────┐                      │
   │                           │                       │
   ↓ /flow:research          │ (skip research)       │
Researched                     │                       │
   │                           │                       │
   └───────────┬───────────────┘                       │
               ↓ /flow:plan                          │
           Planned                                     │
               │                                       │
               ↓ /flow:implement                     │
        In Implementation                              │
               │                                       │
               ↓ /flow:validate                      │
           Validated                                   │
               │                                       │
               ↓ /flow:operate                       │
           Deployed                                    │
               │                                       │
               ↓ Release Manager verification          │
             Done ←────────────────────────────────────┘
                    (simple tasks can go direct)
```

### Skipping Phases

Some phases can be skipped based on complexity:

```bash
# Simple tasks (8-12 complexity score)
To Do → Done  # Skip all /flowspec commands

# Medium tasks (13-20 complexity score)
To Do → Specified → Planned → In Implementation → Done

# Complex tasks (21-32 complexity score)
To Do → Assessed → Specified → Researched → Planned →
  In Implementation → Validated → Deployed → Done
```

## Command Integration Reference

### /flow:assess

**State Transition**: `To Do` → `Assessed`

**Backlog Operations**:
```bash
# Before: Task in To Do
backlog task list -s "To Do" --plain

# After: Task moved to Assessed with complexity labels
backlog task edit task-42 -s "Assessed" -l complexity-complex
```

### /flow:specify

**State Transition**: `Assessed` → `Specified`

**Backlog Operations**:
```bash
# Creates implementation tasks
backlog task create "T001: Implement login endpoint" \
  --ac "POST /auth/login returns JWT" \
  --ac "Invalid credentials return 401" \
  -l backend,US1

# Updates feature task
backlog task edit task-42 -s "Specified"
```

### /flow:research

**State Transition**: `Specified` → `Researched`

**Backlog Operations**:
```bash
# Creates research spike tasks
backlog task create "Research: OAuth providers comparison" \
  --ac "Compare Google, GitHub, Microsoft OAuth" \
  --ac "Document security considerations" \
  -l research

# Creates follow-up implementation tasks
backlog task create "Implement OAuth with recommended provider" \
  --dep task-research-42
```

### /flow:plan

**State Transition**: `Specified|Researched` → `Planned`

**Backlog Operations**:
```bash
# Creates architecture tasks
backlog task create "ADR: JWT vs session tokens" \
  --ac "Document decision rationale" \
  -l architecture,adr

# Creates infrastructure tasks
backlog task create "Setup CI/CD for auth service" \
  --ac "Configure build pipeline" \
  --ac "Add security scanning" \
  -l infrastructure,cicd
```

### /flow:implement

**State Transition**: `Planned` → `In Implementation`

**Backlog Operations**:
```bash
# Step 0: Discover tasks
backlog search "authentication" --plain
backlog task list -l backend --plain

# Engineer workflow
backlog task edit task-42 -s "In Progress" -a @backend-engineer
backlog task edit task-42 --plan $'1. Create auth endpoints\n2. Add JWT logic\n3. Write tests'
backlog task edit task-42 --check-ac 1
backlog task edit task-42 --check-ac 2
backlog task edit task-42 --notes $'Implemented with RS256 signing'

# Code reviewer validation
backlog task edit task-42 --uncheck-ac 2  # If AC not satisfied
backlog task edit task-42 --append-notes 'Review: Missing token expiration'
```

### /flow:validate

**State Transition**: `In Implementation` → `Validated`

**Backlog Operations**:
```bash
# QA validation
backlog task edit task-42 --check-ac 3  # Tests passing
backlog task edit task-42 --append-notes 'QA: All tests pass, 95% coverage'

# Security validation
backlog task edit task-42 --append-notes 'Security: No vulnerabilities found'

# Release Manager verification
backlog task 42 --plain  # Verify all ACs checked
backlog task edit task-42 -s "Validated"
```

### /flow:operate

**State Transition**: `Validated` → `Deployed`

**Backlog Operations**:
```bash
# Creates operational tasks
backlog task create "Runbook: Auth service high latency" \
  --ac "Document triage steps" \
  --ac "Add rollback procedure" \
  -l operations,runbook

# Marks feature as deployed
backlog task edit task-42 -s "Deployed"
```

## Best Practices

### 1. Always Start with Assessment

```bash
# Determine appropriate workflow depth
/flow:assess <feature description>

# Use result to choose path:
# Simple (8-12) → Implement directly
# Medium (13-20) → Spec-light mode
# Complex (21-32) → Full workflow
```

### 2. Verify Tasks Before Implementation

```bash
# WRONG: Jump straight to implement
/flow:implement User authentication  # ERROR: No tasks found

# RIGHT: Verify tasks exist
backlog task list --plain | grep -i "auth"
backlog search "authentication" --plain

# If no tasks, create them first
/flow:specify User authentication
```

### 3. Check ACs Progressively

```bash
# DON'T: Check all ACs at once at the end
backlog task edit task-42 --check-ac 1 --check-ac 2 --check-ac 3

# DO: Check as you complete each
# After implementing OAuth flow:
backlog task edit task-42 --check-ac 1

# After implementing JWT:
backlog task edit task-42 --check-ac 2

# After writing tests:
backlog task edit task-42 --check-ac 3
```

### 4. Add Implementation Notes

```bash
# Always document what was done
backlog task edit task-42 --notes $'Implementation summary:

- Used RS256 for JWT signing (more secure than HS256)
- Token expiration set to 15 minutes
- Refresh token rotation implemented per RFC 6749
- Added rate limiting (100 req/min per user)

Files changed:
- src/auth/jwt.ts
- src/auth/oauth.ts
- tests/auth/'
```

### 5. Code Reviewers Validate ACs

```bash
# Reviewer checks each AC
backlog task 42 --plain

# If AC marked complete but code doesn't satisfy:
backlog task edit task-42 --uncheck-ac 2
backlog task edit task-42 --append-notes 'Review: AC #2 missing token refresh logic'
```

### 6. Release Manager Verifies Definition of Done

Before marking any task as `Done`:
- [ ] All acceptance criteria checked (`[x]`)
- [ ] Implementation notes present
- [ ] Code review completed
- [ ] Tests passing
- [ ] No blocking issues

```bash
# Verify before marking Done
backlog task 42 --plain

# Only then mark complete
backlog task edit task-42 -s Done
```

## Troubleshooting

### "No backlog tasks found" Error

**Problem**: `/flow:implement` can't find tasks to work on.

**Cause**: No tasks created yet or wrong search terms.

**Solution**:
```bash
# 1. Check if tasks exist
backlog task list --plain

# 2. Search with different terms
backlog search "auth" --plain
backlog search "login" --plain

# 3. If no tasks, create them first
/flow:specify <feature description>

# 4. Verify tasks were created
backlog task list --plain | grep -i "<keyword>"
```

### "Cannot run /flow:X - wrong state" Error

**Problem**: Task not in expected state for command.

**Cause**: Running commands out of order.

**Solution**:
```bash
# Check current state
backlog task 42 --plain

# Follow workflow order:
# To Do → Assessed → Specified → Researched → Planned → ...

# If stuck in wrong state, manually fix:
backlog task edit task-42 -s "Planned"  # Requires appropriate AC completion
```

### Tasks Not Transitioning States

**Problem**: Commands complete but task status doesn't change.

**Cause**: Agent didn't call backlog CLI or CLI call failed.

**Solution**:
```bash
# 1. Check task status
backlog task 42 --plain

# 2. Manually update if needed
backlog task edit task-42 -s "Specified"

# 3. Verify agent context includes backlog CLI instructions
# Check .claude/commands/flow/*.md files
```

### Acceptance Criteria Not Checking

**Problem**: ACs remain unchecked despite work completion.

**Cause**: Engineer forgot to check ACs or CLI command failed.

**Solution**:
```bash
# Manually check ACs
backlog task edit task-42 --check-ac 1
backlog task edit task-42 --check-ac 2

# Verify
backlog task 42 --plain
# Should show [x] for checked ACs
```

### Code Reviewer Can't Uncheck ACs

**Problem**: Need to uncheck AC that shouldn't be marked complete.

**Solution**:
```bash
# Uncheck specific AC
backlog task edit task-42 --uncheck-ac 2

# Add note explaining why
backlog task edit task-42 --append-notes 'Unchecked AC #2: Missing error handling'
```

### Dependency Chain Issues

**Problem**: Tasks can't start because dependencies not complete.

**Diagnosis**:
```bash
# View task with dependencies
backlog task 42 --plain

# Check dependency status
backlog task <dep-id> --plain
```

**Solution**:
```bash
# Option 1: Complete blocking task first
backlog task edit <dep-id> -s "In Progress"
# ... complete work ...
backlog task edit <dep-id> -s Done

# Option 2: Remove dependency if not needed
# Edit task file directly to remove from dependencies list
```

### MCP Connection Issues

**Problem**: Claude Code can't manage tasks via MCP.

**Solution**:
```bash
# 1. Verify MCP server configured
claude mcp list

# 2. Re-add if missing
claude mcp add backlog --scope user -- backlog mcp start

# 3. Restart Claude Code

# 4. Test connection
# Ask Claude: "List all backlog tasks"
```

---

## Related Documentation

- **[Flowspec Workflow Guide](flowspec-workflow-guide.md)** - Complete workflow documentation
- **[Backlog User Guide](backlog-user-guide.md)** - Backlog.md standalone usage
- **[Backlog Quick Start](backlog-quickstart.md)** - Get started in 5 minutes
- **[Workflow State Mapping](workflow-state-mapping.md)** - State transition details
- **[Workflow Troubleshooting](workflow-troubleshooting.md)** - More troubleshooting tips

---

**Last Updated**: 2025-12-03
**Version**: 1.0
