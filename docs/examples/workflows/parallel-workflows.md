# Parallel Workflows Example

## Overview

This configuration enables parallel development tracks where frontend and backend teams can work independently and then integrate at a coordination point.

**Key Concept**: Split implementation into parallel tracks that converge at integration.

## Use Cases

- Multi-team organizations with separate frontend/backend teams
- Feature development with well-defined API contracts
- Microservice development (independent service development)
- A/B testing development (parallel feature variants)
- Mobile + web development (parallel platform implementations)

## Workflow Diagram

```
To Do
  ↓ /flow:assess
Assessed
  ↓ /flow:specify
Specified
  ↓ /flow:plan (defines API contract)
Planned
  ├─────────────────┬────────────────┐
  ↓                 ↓                ↓
Frontend Track    Backend Track    (parallel)
  ↓                 ↓
/flow:implement-frontend    /flow:implement-backend
  ↓                 ↓
Frontend In Progress    Backend In Progress
  ↓                 ↓
/flow:validate-frontend    /flow:validate-backend
  ↓                 ↓
Frontend Validated    Backend Validated
  └─────────────────┬────────────────┘
                    ↓ (both required)
            /flow:integrate
                    ↓
        Integration In Progress
                    ↓
      /flow:validate-integration
                    ↓
        Integration Validated
                    ↓
          /flow:operate
                    ↓
              Deployed
                    ↓
               Done
```

## Key Features

### 1. API Contract as Synchronization Point

The planning phase produces an API contract that both teams use:

```yaml
transitions:
  - name: "plan"
    from: "Specified"
    to: "Planned"
    output_artifacts:
      - type: "api_contract"
        path: "./docs/api/{feature}-api-contract.yaml"
        required: true
```

**Example API Contract** (`docs/api/user-auth-api-contract.yaml`):
```yaml
openapi: 3.0.0
info:
  title: User Authentication API
  version: 1.0.0

paths:
  /api/login:
    post:
      summary: Authenticate user
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                password:
                  type: string
      responses:
        200:
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
        401:
          description: Unauthorized
```

### 2. Independent Validation

Each track validates independently before integration:

**Frontend Validation**:
- Component testing
- Visual regression testing
- Accessibility testing
- Mocked backend integration tests

**Backend Validation**:
- API contract testing
- Integration testing (database, external services)
- Performance testing
- Security testing

### 3. Integration State

Requires **both tracks** to reach "Validated" state before proceeding:

```yaml
transitions:
  # Integration from either track requires the other track to be complete
  - name: "integrate"
    from: "Frontend Validated"
    to: "Integration In Progress"
    via: "integrate"
    description: "Frontend and backend integration started (requires Backend Validated)"

  - name: "integrate_from_backend"
    from: "Backend Validated"
    to: "Integration In Progress"
    via: "integrate"
    description: "Backend and frontend integration started (requires Frontend Validated)"
```

### 4. Rework Paths

If integration testing finds issues, can rework individual tracks:

```
Integration In Progress → Frontend In Progress (frontend issues)
Integration In Progress → Backend In Progress (backend issues)
```

## Usage

### 1. Setup

```bash
cp docs/examples/workflows/parallel-workflows.yml flowspec_workflow.yml
specify workflow validate
```

### 2. Create Feature with Clear API Contract

```bash
backlog task create "User authentication"
/flow:assess
/flow:specify

# Planning phase defines API contract
/flow:plan
# Creates docs/api/user-auth-api-contract.yaml
```

### 3. Split Team Assignments

**Frontend Team Task**:
```bash
backlog task create "User auth - frontend implementation" \
  --labels frontend \
  --assignee @frontend-team

# Frontend team works independently
/flow:implement-frontend
/flow:validate-frontend
```

**Backend Team Task**:
```bash
backlog task create "User auth - backend implementation" \
  --labels backend \
  --assignee @backend-team

# Backend team works independently
/flow:implement-backend
/flow:validate-backend
```

### 4. Integration

```bash
# Once both tracks reach "Validated" state
/flow:integrate

# Connects frontend to real backend
# Removes mocks
# Runs end-to-end tests

/flow:validate-integration
/flow:operate
```

## Coordination Points

### Point 1: API Contract Review

**When**: After `/flow:plan`

**Action**: Both teams review and approve API contract

**Checklist**:
- [ ] Request/response schemas defined
- [ ] Error codes documented
- [ ] Authentication requirements clear
- [ ] Rate limits specified
- [ ] Both teams agree on contract

### Point 2: Integration Readiness

**When**: Before `/flow:integrate`

**Action**: Verify both tracks are validated

**Checklist**:
- [ ] Frontend validated (all component tests pass)
- [ ] Backend validated (all API tests pass)
- [ ] API contract unchanged (or coordinated changes made)
- [ ] Integration environment ready
- [ ] Both teams available for issues

### Point 3: Deployment Readiness

**When**: After `/flow:validate-integration`

**Action**: Verify end-to-end system works

**Checklist**:
- [ ] End-to-end tests pass
- [ ] Performance meets requirements
- [ ] Security scan passed
- [ ] Both teams approve for deployment

## Team Workflows

### Frontend Team

```bash
# 1. Get assigned to frontend track
backlog task view task-frontend-123

# 2. Implement using API contract
/flow:implement-frontend
# - Use docs/api/{feature}-api-contract.yaml
# - Mock backend responses
# - Focus on UI/UX

# 3. Validate independently
/flow:validate-frontend
# - Component tests
# - Visual regression tests
# - Accessibility tests

# 4. Ready for integration
# (Wait for backend team to reach "Backend Validated")

# 5. Integration (coordinated)
/flow:integrate
# - Connect to real backend
# - Remove mocks

# 6. E2E validation
/flow:validate-integration
```

### Backend Team

```bash
# 1. Get assigned to backend track
backlog task view task-backend-123

# 2. Implement API contract
/flow:implement-backend
# - Implement docs/api/{feature}-api-contract.yaml exactly
# - Focus on business logic
# - Add database schema

# 3. Validate independently
/flow:validate-backend
# - API contract tests
# - Integration tests
# - Security tests

# 4. Ready for integration
# (Wait for frontend team to reach "Frontend Validated")

# 5. Integration (coordinated)
/flow:integrate
# - Verify contract implementation

# 6. E2E validation
/flow:validate-integration
```

## Advanced Patterns

### Pattern 1: Three-Way Parallelization

Add mobile development track:

```yaml
states:
  # ... existing states
  - "Mobile In Progress"
  - "Mobile Validated"

workflows:
  implement-mobile:
    # ... similar to implement-frontend

transitions:
  - name: "integrate"
    from: "Mobile Validated"
    to: "Integration In Progress"
    requires_states: ["Frontend Validated", "Backend Validated", "Mobile Validated"]
```

### Pattern 2: Microservices Parallelization

Multiple backend services developed in parallel:

```yaml
states:
  - "Auth Service In Progress"
  - "Auth Service Validated"
  - "User Service In Progress"
  - "User Service Validated"
  - "Payment Service In Progress"
  - "Payment Service Validated"

# Integration requires all services validated
```

### Pattern 3: A/B Testing Variants

Develop two feature variants in parallel:

```yaml
states:
  - "Variant A In Progress"
  - "Variant A Validated"
  - "Variant B In Progress"
  - "Variant B Validated"

# Deploy both variants with feature flag
```

## Troubleshooting

### Issue 1: API Contract Divergence

**Problem**: Frontend and backend implement different API contracts

**Prevention**:
- Lock API contract file during implementation
- Use contract testing (Pact, Spring Cloud Contract)
- Review changes together before implementing

**Detection**:
```bash
# Compare implemented API to contract
diff docs/api/{feature}-api-contract.yaml \
     src/backend/openapi-generated.yaml
```

**Resolution**:
```bash
# Coordinate change with both teams
# Update contract
vim docs/api/{feature}-api-contract.yaml

# Both teams update implementation
/flow:implement-frontend  # Frontend updates
/flow:implement-backend   # Backend updates
```

### Issue 2: Integration Blocked on One Track

**Problem**: Frontend validated, backend still in progress

**Options**:

**Option 1: Wait** (Recommended):
```bash
# Frontend team helps with backend
# Or works on next feature
```

**Option 2: Backend Rework**:
```bash
# If backend has fundamental issues
backlog task edit task-backend-123 -s "Backend In Progress" \
  --notes "Rework needed: API performance issues"
```

**Option 3: Temporary Mock**:
```bash
# Deploy frontend with mock backend (not recommended for production)
```

### Issue 3: Integration Test Failures

**Problem**: E2E tests fail during integration

**Diagnose**:
```bash
# Check which component is failing
# Frontend issue?
/flow:implement-frontend  # Fix and re-validate

# Backend issue?
/flow:implement-backend  # Fix and re-validate

# Both?
# Coordinate fix between teams
```

## Benefits

1. **Faster Development**: Teams work in parallel, no blocking
2. **Clear Contracts**: API contract prevents integration issues
3. **Independent Testing**: Each track validates separately
4. **Better Coordination**: Explicit integration points
5. **Flexibility**: Teams can move at different speeds

## Trade-offs

| Benefit | Trade-off |
|---------|-----------|
| Parallel work reduces time | More coordination overhead |
| Independent validation catches issues early | Integration testing still needed |
| Clear API contracts prevent issues | Contract changes affect both teams |
| Teams can specialize | Integration knowledge still required |

## Best Practices

1. **Define API Contract Early** - In planning phase, before implementation
2. **Lock Contract During Implementation** - Changes require coordination
3. **Use Contract Testing** - Verify both sides implement same contract
4. **Communicate at Integration Points** - Don't integrate silently
5. **Keep Tracks Synchronized** - Don't let one track lag too far behind
6. **Mock Realistically** - Frontend mocks should match backend behavior
7. **Test Contracts Continuously** - Backend contract tests run on every commit

## Comparison to Linear Workflow

| Aspect | Linear Workflow | Parallel Workflow |
|--------|----------------|-------------------|
| **Development Time** | Longer (sequential) | Shorter (parallel) |
| **Coordination Overhead** | Low | Medium |
| **Integration Risk** | Low | Medium |
| **Team Specialization** | Less important | Critical |
| **Contract Clarity** | Nice-to-have | Required |
| **Best For** | Small teams, simple features | Large teams, complex features |

## Related Examples

- [Minimal Workflow](./minimal-workflow.md) - Simple linear workflow
- [Custom Agents Workflow](./custom-agents-workflow.md) - Custom agent definitions
- [Security Audit Workflow](./security-audit-workflow.md) - Enhanced security validation
