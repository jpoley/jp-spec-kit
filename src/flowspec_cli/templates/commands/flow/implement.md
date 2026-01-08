---
description: Execute implementation using specialized frontend and backend engineer agents with code review.
loop: inner
# Loop Classification: INNER LOOP
# This command is part of the inner loop (implementation/execution phase). It writes
# production code with fast iteration cycles (edit → run/tests → debug → repeat).
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command implements features using specialized engineering agents with integrated code review. **Engineers work exclusively from backlog tasks.**

**For /flow:implement**: Required input state is `workflow:Planned`. Output state will be `workflow:In Implementation`.

If the task doesn't have the required workflow state, inform the user:
- If task needs planning first: suggest running `/flow:plan`
- If task needs specification: suggest running `/flow:specify` first

**Proceed to Step 1 ONLY if workflow validation passes.**

### Step 1: Discover Backlog Tasks

**⚠️ CRITICAL: This command REQUIRES existing backlog tasks to work on.**

Discover tasks for implementation:

```bash
# Search for implementation tasks related to this feature
backlog search "$ARGUMENTS" --plain

# List available tasks to work on
backlog task list -s "To Do" --plain

# List any in-progress tasks for context
backlog task list -s "In Progress" --plain
```

**If no relevant tasks are found:**

```
⚠️ No backlog tasks found for: [FEATURE NAME]

This command requires existing backlog tasks with defined acceptance criteria.
Please run /flow:specify first to create implementation tasks, or create
tasks manually using:

  backlog task create "Implement [Feature]" --ac "Criterion 1" --ac "Criterion 2"

Then re-run /flow:implement
```

**If tasks ARE found, proceed to Step 2.**

### Step 2: Discover Related Specifications and ADRs

**⚠️ CRITICAL: Implementation MUST be informed by all relevant design documents.**

Before coding, discover ALL related PRDs, Functional Specs, Technical Specs, and ADRs:

```bash
# Search for PRDs related to this feature
ls -la docs/prd/ 2>/dev/null || echo "No PRDs found"
grep -rl "$ARGUMENTS" docs/prd/ 2>/dev/null || echo "No matching PRDs"

# Search for Functional and Technical Specs
ls -la docs/specs/ 2>/dev/null || echo "No specs found"
grep -rl "$ARGUMENTS" docs/specs/ 2>/dev/null || echo "No matching specs"

# Search for related ADRs (architecture decisions)
ls -la docs/adr/ 2>/dev/null || echo "No ADRs found"
grep -rl "$ARGUMENTS" docs/adr/ 2>/dev/null || echo "No matching ADRs"

# Search backlog task descriptions for spec/ADR references
backlog task list --plain 2>/dev/null | grep -i "prd\|spec\|adr"
```

**Read ALL discovered documents before implementation:**

The artifact progression is:
```
PRD -> Functional Spec -> Technical Spec -> ADR -> Implementation
```

| Document | What It Tells You |
|----------|-------------------|
| **PRD** | What the product must do and why the user cares |
| **Functional Spec** | What behaviors and capabilities are required |
| **Technical Spec** | How to build it (architecture, data, APIs) |
| **ADR** | Why we chose this technical path |

**If key documents are missing:**

```
⚠️ Missing design documents for: [FEATURE NAME]

Found:
- PRD: [[Y]/[N]]
- Functional Spec: [[Y]/[N]]
- Technical Spec: [[Y]/[N]]
- ADRs: [[Y]/[N]]

Recommendation:
- Run /flow:specify to create PRD and Functional Spec
- Run /flow:plan to create Technical Spec and ADRs
- Then re-run /flow:implement

Proceeding without specs may result in:
- Misaligned implementation
- Undefined edge cases
- Inconsistent architecture
- Undocumented decisions
```

**If documents ARE found, read them and proceed to Phase 0.**

### Checkpoint Reminder

> **💡 Safety Tip**: Claude creates checkpoints before each code change. If implementation doesn't work as expected, you can press `Esc Esc` to instantly undo changes, or use `/rewind` for interactive rollback. This is especially useful for:
> - Multi-file refactoring
> - Experimental approaches
> - Complex migrations

### Phase 0: Quality Gate (MANDATORY)

**⚠️ CRITICAL: Spec quality must pass before implementation begins.**

Before starting implementation, you MUST run the quality gate:

```bash
# Run quality gate on spec.md
flowspec gate

# Alternative: Override threshold if needed
flowspec gate --threshold 60

# Emergency bypass (NOT RECOMMENDED - use only with explicit user approval)
flowspec gate --force
```

**Quality Gate Exit Codes:**
- `0` = PASSED - Proceed to Phase 1
- `1` = FAILED - Spec quality below threshold
- `2` = ERROR - Missing spec.md or validation error

**If gate PASSES (exit code 0):**
```
✅ Quality gate passed
Proceeding with implementation...
```

**If gate FAILS (exit code 1):**
```
[X] Quality gate failed: Spec quality is X/100 (minimum: 70)

Recommendations:
  • Add missing section: ## Description
  • Add missing section: ## User Story
  • Reduce vague terms (currently: Y instances)
  • Add measurable acceptance criteria

Action Required:
1. Improve spec quality using recommendations
2. Re-run: flowspec quality docs/prd/<feature>-spec.md
3. When quality ≥70, re-run: /flow:implement

OR (not recommended without user approval):
  flowspec gate --force
```

**--force Bypass:**
- Only use with explicit user approval
- Warns that bypassing quality checks may lead to unclear requirements
- Logs the bypass decision

**Proceed to Phase 0.1 ONLY if quality gate passes or user explicitly approves --force bypass.**

### Phase 0.1: Rigor Rules Enforcement (MANDATORY)

**⚠️ CRITICAL: Branch naming and worktree conventions MUST be validated before implementation begins.**

These rules enforce consistency and enable automation across the team.

#### Validation: Branch Naming Convention

Branch names MUST follow the pattern: `{hostname}/task-{id}/{slug-description}`

```bash
# Validate branch naming (EXEC-002)
BRANCH=$(git branch --show-current 2>/dev/null)
if [ -z "$BRANCH" ]; then
  echo "[X] RIGOR VIOLATION (EXEC-002): Not on a git branch"
  echo "Fix: Create a branch following the pattern: hostname/task-NNN/slug-description"
  exit 1
fi

if ! echo "$BRANCH" | grep -Eq '^[a-z0-9-]+/task-[0-9]+/[a-z0-9-]+$'; then
  echo "[X] RIGOR VIOLATION (EXEC-002): Branch name must follow format: hostname/task-NNN/slug-description"
  echo "Current branch: $BRANCH"
  echo ""
  echo "Examples of valid branch names:"
  echo "  - macbook-pro/task-543/rigor-rules-integration"
  echo "  - desktop-alice/task-123/user-authentication"
  echo "  - laptop-bob/task-456/api-endpoints"
  echo ""
  echo "Fix: Create a new branch with compliant naming:"
  HOSTNAME=$(hostname -s | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9-]/-/g')
  # Extract task number if present in current branch, otherwise prompt user
  TASK_NUM=$(echo "$BRANCH" | grep -Eo 'task-[0-9]+' || echo "")
  if [ -z "$TASK_NUM" ]; then
    echo "  # First, identify your task ID from the backlog:"
    echo "  backlog task list --plain"
    echo "  # Then create branch with that task ID:"
    echo "  git checkout -b ${HOSTNAME}/task-<ID>/your-feature-slug"
  else
    echo "  git checkout -b ${HOSTNAME}/${TASK_NUM}/your-feature-slug"
  fi
  exit 1
fi

echo "✅ Branch naming validation passed: $BRANCH"
```

**Why this matters**:
- **Traceability**: Branch name instantly shows which task it implements
- **Conflict Prevention**: Hostname prefix prevents naming collisions in multi-developer teams
- **Automation**: Enables automated task-to-branch linking in CI/CD
- **Consistency**: Team-wide standard reduces cognitive overhead

#### Validation: Git Worktree

Implementation work MUST be done in a git worktree with matching task ID.

```bash
# Validate worktree usage (EXEC-001)
WORKTREE_DIR=$(git rev-parse --show-toplevel 2>/dev/null)
BRANCH=$(git branch --show-current 2>/dev/null)
# Use exact path matching to avoid substring false positives
IS_WORKTREE=$(git worktree list 2>/dev/null | awk '{print $1}' | grep -Fxq "$WORKTREE_DIR" && echo "yes" || echo "no")

if [ "$IS_WORKTREE" = "no" ]; then
  echo "[X] RIGOR VIOLATION (EXEC-001): Not in a git worktree"
  echo ""
  echo "Why worktrees matter:"
  echo "  - Enable parallel feature development"
  echo "  - No branch-switching overhead"
  echo "  - Isolate dependencies and state"
  echo ""
  echo "Fix: Create worktree matching your branch:"
  # BRANCH already defined at start of this code block
  WORKTREE_NAME=$(basename "$BRANCH")
  echo "  cd $(git rev-parse --show-toplevel)"
  echo "  git worktree add ../${WORKTREE_NAME} ${BRANCH}"
  echo "  cd ../${WORKTREE_NAME}"
  exit 1
fi

# Check worktree directory name contains task ID (best practice)
WORKTREE_NAME=$(basename "$WORKTREE_DIR")
TASK_ID=$(echo "$BRANCH" | grep -Eo 'task-[0-9]+' || echo "")

if [ -z "$TASK_ID" ]; then
  echo "⚠️  WARNING (EXEC-001): Branch does not contain task ID"
  echo "Worktree name should match task ID for clarity"
elif ! echo "$WORKTREE_NAME" | grep -q "$TASK_ID"; then
  echo "⚠️  WARNING (EXEC-001): Worktree name '$WORKTREE_NAME' does not contain task ID '$TASK_ID'"
  echo "Consider renaming worktree directory to match task ID"
else
  echo "✅ Worktree validation passed: $WORKTREE_NAME"
fi
```

**Why this matters**:
- **Parallel Development**: Work on multiple features without branch switching
- **State Isolation**: Each worktree has independent working directory and index
- **Dependency Isolation**: Different virtual environments per worktree
- **Reduced Context Switching**: No git checkout overhead

#### Validation: Backlog Task Linkage

```bash
# Validate backlog task exists (EXEC-004)
TASK_ID=$(echo "$BRANCH" | grep -Eo 'task-[0-9]+' || echo "")

if [ -z "$TASK_ID" ]; then
  echo "[X] RIGOR VIOLATION (EXEC-004): No task ID in branch name"
  echo "All implementation work must be linked to a backlog task"
  exit 1
fi

backlog task "$TASK_ID" --plain > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "[X] RIGOR VIOLATION (EXEC-004): Backlog task not found: $TASK_ID"
  echo ""
  echo "Fix: Create the backlog task first:"
  echo "  backlog task create 'Feature description' \\"
  echo "    --ac 'Acceptance criterion 1' \\"
  echo "    --ac 'Acceptance criterion 2' \\"
  echo "    -l 'backend' \\"
  echo "    --priority high"
  exit 1
fi

echo "✅ Backlog task validation passed: $TASK_ID"
```

**Why this matters**:
- **No Rogue Work**: All coding aligns with planned backlog
- **Prioritization**: Work is tracked and prioritized
- **Context Preservation**: Task contains acceptance criteria and context

**Proceed to Phase 0.5 ONLY if all rigor validations pass.**

### Phase 0.5: Load PRP Context (PRP-First Workflow)

**⚠️ CRITICAL: PRPs (Product Requirements Prompts) provide self-contained context for implementation.**

Before starting implementation, check for a PRP document for the active task:

```bash
# Extract task ID from arguments - handles both task IDs and feature descriptions
INPUT="${ARGUMENTS}"

# If no input provided, show active tasks and prompt
if [ -z "$INPUT" ]; then
  echo "⚠️ No task ID or feature description provided."
  echo "Searching for active 'In Progress' tasks..."
  backlog task list -s "In Progress" --plain | head -5
  echo ""
  echo "Please specify a task ID or feature description:"
  echo "  /flow:implement task-123"
  echo "  /flow:implement \"Add user authentication\""
  exit 1
fi

# Determine if input is already a task ID or needs resolution
if echo "$INPUT" | grep -Eq '^task-[0-9]+$'; then
  TASK_ID="$INPUT"
  echo "✅ Using task ID: $TASK_ID"
else
  # Treat input as a feature description - try to resolve via backlog search
  echo "🔍 '$INPUT' is not a task ID. Searching backlog for matching tasks..."
  RESOLVED_ID=$(backlog search "$INPUT" --plain 2>/dev/null | awk '/^task-[0-9]+/ {print $1; exit}')

  if [ -n "$RESOLVED_ID" ]; then
    TASK_ID="$RESOLVED_ID"
    echo "✅ Resolved feature description to: $TASK_ID"
  else
    echo "❌ Could not resolve a task ID from: \"$INPUT\""
    echo ""
    echo "Active tasks you can choose from:"
    backlog task list -s "In Progress" --plain | head -5
    echo ""
    echo "Please specify a valid task ID:"
    echo "  /flow:implement task-123"
    exit 1
  fi
fi

# Check for PRP file
PRP_PATH="docs/prp/${TASK_ID}.md"

if [ -f "$PRP_PATH" ]; then
  echo "✅ PRP found: $PRP_PATH"
  echo "Loading PRP as primary context..."
else
  echo "⚠️ No PRP found at: $PRP_PATH"
fi
```

**If PRP exists:**

```bash
# Read the PRP file
cat "$PRP_PATH"

# Confirm PRP loaded
echo ""
echo "✅ PRP loaded successfully"
echo ""
echo "The PRP contains:"
echo "  • Feature summary and acceptance criteria"
echo "  • Code files to review"
echo "  • Related documentation"
echo "  • Examples and known gotchas"
echo "  • Validation commands"
echo ""
echo "Proceeding to implementation with full context..."
```

**If PRP missing:**

```
⚠️ No PRP found for task: ${TASK_ID}

A PRP (Product Requirements Prompt) is a self-contained context bundle that includes:
  • All code files to read
  • Related documentation and specs
  • Examples demonstrating patterns
  • Known gotchas and pitfalls
  • Validation commands and success criteria

Without a PRP, you may be missing critical context.

Recommendation:
  1. Generate PRP first: /flow:generate-prp ${TASK_ID}
  2. Review the generated PRP: docs/prp/${TASK_ID}.md
  3. Then re-run: /flow:implement ${TASK_ID}

Continue without PRP? [y/N]
```

**Ask user to confirm if they want to proceed without PRP.** If user says no or doesn't respond, suggest running `/flow:generate-prp` first.

**PRP-First Workflow Benefits**:

| With PRP | Without PRP |
|----------|-------------|
| All context gathered upfront | Must discover context during implementation |
| Known gotchas highlighted | May miss edge cases |
| Clear validation commands | Unclear how to test |
| Focused implementation | May read irrelevant files |
| Faster onboarding for agents | More exploration needed |

**Proceed to Phase 1 ONLY after:**
- PRP is loaded (if available), OR
- User explicitly confirms proceeding without PRP

### Phase 1: Implementation (Parallel Execution)

**IMPORTANT**: Launch applicable engineer agents in parallel for maximum efficiency.

**⚠️ RIGOR RULE (EXEC-003)**: Log all significant decisions during implementation using:

```bash
./scripts/bash/rigor-decision-log.sh \
  --task $TASK_ID \
  --phase execution \
  --decision "What was decided" \
  --rationale "Why this choice" \
  --actor "@<agent-name>" \
  --alternatives "Alternative1,Alternative2"  # Optional
```

**When to log a decision**:
- **Technology choices**: Selected library, framework, or pattern
- **Architecture changes**: Changed data model, API design, or system structure
- **Trade-off resolutions**: Chose performance over simplicity, etc.
- **Deferred work**: Decided to defer optimization, feature, or refactor

**Examples**:
```bash
# Example 1: Library selection
./scripts/bash/rigor-decision-log.sh \
  --task task-543 \
  --phase execution \
  --decision "Use FastAPI for REST API" \
  --rationale "Better async support, OpenAPI generation" \
  --actor "@backend-engineer" \
  --alternatives "Flask,Django"

# Example 2: Architecture decision
./scripts/bash/rigor-decision-log.sh \
  --task task-543 \
  --phase execution \
  --decision "Split validation into separate phase" \
  --rationale "Clearer separation of concerns, easier to test" \
  --actor "@backend-engineer"

# Example 3: Deferred work
./scripts/bash/rigor-decision-log.sh \
  --task task-543 \
  --phase execution \
  --decision "Defer performance optimization to task-600" \
  --rationale "Current performance meets requirements, avoid premature optimization" \
  --actor "@backend-engineer" \
  --related "task-600"
```

#### Frontend Implementation (if UI/mobile components needed)

Use the Task tool to launch a **general-purpose** agent (Frontend Engineer context):

```
# AGENT CONTEXT: Senior Frontend Engineer

You are a Senior Frontend Engineer with deep expertise in React, React Native, modern web standards, and mobile development. You build user interfaces that are performant, accessible, maintainable, and delightful to use.

## Core Expertise
- **Modern React Development**: React 18+ with hooks, concurrent features, server components
- **Mobile Excellence**: React Native for native-quality mobile apps
- **Performance Optimization**: Fast load times, smooth interactions, efficient rendering
- **Accessibility First**: WCAG 2.1 AA compliance, inclusive interfaces
- **Type Safety**: TypeScript for error prevention and code quality

## Key Technologies
- **State Management**: Zustand, Jotai, TanStack Query, Context API
- **Styling**: Tailwind CSS, CSS Modules, Styled Components
- **Performance**: Code splitting, memoization, virtualization, Suspense
- **Testing**: Vitest, React Testing Library, Playwright

# TASK: Implement the frontend for: [USER INPUT FEATURE]

Context:
[If PRP loaded: The PRP document (docs/prp/${TASK_ID}.md) contains all context needed]
[Include architecture, PRD, design specs, API contracts from PRP or discovered docs]
[Include backlog task IDs discovered in Step 1]

## Backlog Task Management (REQUIRED)

**Your Agent Identity**: @frontend-engineer

Before coding, you MUST:
1. **Pick a task**: `backlog task <task-id> --plain` to review details
2. **Assign yourself**: `backlog task edit <task-id> -s "In Progress" -a @frontend-engineer`
3. **Add implementation plan**: `backlog task edit <task-id> --plan $'1. Step 1\n2. Step 2'`

During implementation:
- **Check ACs as you complete them**: `backlog task edit <task-id> --check-ac 1`
- **Check multiple ACs**: `backlog task edit <task-id> --check-ac 1 --check-ac 2`

After implementation:
- **Add implementation notes**: `backlog task edit <task-id> --notes $'Implemented X with Y pattern\n\nKey changes:\n- File A modified\n- File B created'`
- **Verify all ACs checked**: `backlog task <task-id> --plain` (all should show `[x]`)

Implementation Requirements:

1. **Component Development**
   - Build React/React Native components
   - Implement proper TypeScript types
   - Follow component composition patterns
   - Ensure accessibility (WCAG 2.1 AA)

2. **State Management**
   - Choose appropriate state solution (local, Context, Zustand, TanStack Query)
   - Implement efficient data fetching
   - Handle loading and error states

3. **Styling and Responsiveness**
   - Implement responsive design
   - Use design system/tokens
   - Ensure cross-browser/platform compatibility

4. **Performance Optimization**
   - Code splitting and lazy loading
   - Proper memoization
   - Optimized rendering

5. **Testing**
   - Unit tests for components
   - Integration tests for user flows
   - Accessibility tests

Deliver production-ready frontend code with tests.
```

#### Backend Implementation (if API/services needed)

Use the Task tool to launch a **general-purpose** agent (Backend Engineer context):

```
# AGENT CONTEXT: Senior Backend Engineer

You are a Senior Backend Engineer with deep expertise in Go, TypeScript (Node.js), and Python. You build scalable, reliable, and maintainable backend systems including CLI tools, RESTful APIs, GraphQL services, and middleware.

## Core Expertise
- **API Development**: RESTful, GraphQL, gRPC services
- **CLI Tools**: Command-line interfaces and developer tools
- **Database Design**: Efficient data modeling and query optimization
- **System Architecture**: Scalable, resilient distributed systems
- **Performance**: High-throughput, low-latency services

## Language-Specific Expertise
- **Go**: Concurrency with goroutines, error handling, standard library
- **TypeScript/Node.js**: Async/await, event loop, modern ESM modules
- **Python**: Type hints, asyncio, modern dependency management

## Key Technologies
- **Go**: net/http, Gin, cobra (CLI), pgx (database)
- **TypeScript**: Express, Fastify, Prisma, Zod validation
- **Python**: FastAPI, SQLAlchemy, Pydantic, Click/Typer (CLI)

## Code Hygiene Requirements (MANDATORY)

Before completing ANY implementation, you MUST:

1. **Remove Unused Imports**
   - Run language-specific linter to detect unused imports
   - Delete ALL unused imports before completion
   - This is a blocking requirement - do not proceed with unused imports

2. **Language-Specific Linting**
   - **Python**: Run `ruff check --select F401,F841` (unused imports/variables)
   - **Go**: Run `go vet ./...` and check for unused imports
   - **TypeScript**: Run `tsc --noEmit` and check eslint rules

## Defensive Coding Requirements (MANDATORY)

1. **Input Validation at Boundaries**
   - Validate ALL function inputs at API/service boundaries
   - Never trust external data (API responses, file contents, env vars, user input)
   - Fail fast with clear error messages on invalid input

2. **Type Safety**
   - Use type hints/annotations on ALL public functions
   - Handle None/null/undefined explicitly - never assume values exist
   - Use union types for optional values, not implicit None

3. **Error Handling**
   - Handle all error cases explicitly
   - Provide meaningful error messages with context
   - Log errors with sufficient detail for debugging

## Language-Specific Rules

### Python (CRITICAL - Enforce Strictly)
- **Imports**: Run `ruff check --select F401` before completion
- **Types**: Type hints required on all public functions and methods
- **Validation**: Use Pydantic models or dataclasses for data validation
- **None Handling**: Use `Optional[T]` and explicit None checks
- **Example validation**:
  ```python
  from typing import Any, Dict

  def process_user(user_id: int, data: Dict[str, Any]) -> User:
      if not isinstance(user_id, int) or user_id <= 0:
          raise ValueError(f"Invalid user_id: {user_id}")
      if not data:
          raise ValueError("Data cannot be empty")
      # ... implementation
  ```

### Go
- **Imports**: Compiler enforces no unused imports (will not compile)
- **Errors**: Check ALL errors - never use `_` to ignore errors
- **Validation**: Validate struct fields, use constructor functions
- **Example validation**:
  ```go
  func NewUser(id int, name string) (*User, error) {
      if id <= 0 {
          return nil, fmt.Errorf("invalid id: %d", id)
      }
      if strings.TrimSpace(name) == "" {
          return nil, errors.New("name cannot be empty")
      }
      return &User{ID: id, Name: name}, nil
  }
  ```

### TypeScript
- **Imports**: Enable `noUnusedLocals` in tsconfig.json
- **Types**: Use strict mode, avoid `any` type
- **Validation**: Use Zod, io-ts, or similar for runtime validation
- **Example validation**:
  ```typescript
  const UserSchema = z.object({
    id: z.number().positive(),
    name: z.string().min(1),
  });

  function processUser(input: unknown): User {
    return UserSchema.parse(input); // Throws on invalid input
  }
  ```

# TASK: Implement the backend for: [USER INPUT FEATURE]

Context:
[If PRP loaded: The PRP document (docs/prp/${TASK_ID}.md) contains all context needed]
[Include architecture, PRD, API specs, data models from PRP or discovered docs]
[Include backlog task IDs discovered in Step 1]

## Backlog Task Management (REQUIRED)

**Your Agent Identity**: @backend-engineer

Before coding, you MUST:
1. **Pick a task**: `backlog task <task-id> --plain` to review details
2. **Assign yourself**: `backlog task edit <task-id> -s "In Progress" -a @backend-engineer`
3. **Add implementation plan**: `backlog task edit <task-id> --plan $'1. Step 1\n2. Step 2'`

During implementation:
- **Check ACs as you complete them**: `backlog task edit <task-id> --check-ac 1`
- **Check multiple ACs**: `backlog task edit <task-id> --check-ac 1 --check-ac 2`

After implementation:
- **Add implementation notes**: `backlog task edit <task-id> --notes $'Implemented X with Y pattern\n\nKey changes:\n- File A modified\n- File B created'`
- **Verify all ACs checked**: `backlog task <task-id> --plain` (all should show `[x]`)

Implementation Requirements:

1. **API Development** (choose applicable)
   - RESTful endpoints with proper HTTP methods
   - GraphQL schema and resolvers
   - gRPC services and protocol buffers
   - CLI commands and interfaces

2. **Business Logic**
   - Implement core feature logic
   - Input validation and sanitization
   - Error handling and logging
   - Transaction management

3. **Database Integration**
   - Data models and migrations
   - Efficient queries with proper indexing
   - Connection pooling
   - Data validation

4. **Security**
   - Authentication and authorization
   - Input validation
   - SQL/NoSQL injection prevention
   - Secure secret management

5. **Testing**
   - Unit tests for business logic
   - Integration tests for APIs
   - Database tests

Choose language: Go, TypeScript/Node.js, or Python based on architecture decisions.

## Pre-Completion Checklist (BLOCKING)

Before marking implementation complete, verify ALL items:

- [ ] **No unused imports** - Run linter, remove ALL unused imports
- [ ] **No unused variables** - Remove or use all declared variables
- [ ] **All inputs validated** - Boundary functions validate their inputs
- [ ] **Edge cases handled** - Empty values, None/null, invalid types
- [ ] **Types annotated** - All public functions have type hints/annotations
- [ ] **Errors handled** - All error paths have explicit handling
- [ ] **Tests pass** - All unit and integration tests pass
- [ ] **Linter passes** - No linting errors or warnings

⚠️ DO NOT proceed if any checklist item is incomplete.

Deliver production-ready backend code with tests.
```

#### AI/ML Implementation (if ML components needed)

Use the Task tool to launch the **ai-ml-engineer** agent:

```
Implement AI/ML components for: [USER INPUT FEATURE]

Context:
[If PRP loaded: The PRP document (docs/prp/${TASK_ID}.md) contains all context needed]
[Include model requirements, data sources, performance targets from PRP or discovered docs]
[Include backlog task IDs discovered in Step 1]

## Backlog Task Management (REQUIRED)

**Your Agent Identity**: @ai-ml-engineer

Before coding, you MUST:
1. **Pick a task**: `backlog task <task-id> --plain` to review details
2. **Assign yourself**: `backlog task edit <task-id> -s "In Progress" -a @ai-ml-engineer`
3. **Add implementation plan**: `backlog task edit <task-id> --plan $'1. Step 1\n2. Step 2'`

During implementation:
- **Check ACs as you complete them**: `backlog task edit <task-id> --check-ac 1`
- **Check multiple ACs**: `backlog task edit <task-id> --check-ac 1 --check-ac 2`

After implementation:
- **Add implementation notes**: `backlog task edit <task-id> --notes $'Implemented X with Y pattern\n\nKey changes:\n- File A modified\n- File B created'`
- **Verify all ACs checked**: `backlog task <task-id> --plain` (all should show `[x]`)

Implementation Requirements:

1. **Model Development**
   - Training pipeline implementation
   - Feature engineering
   - Model evaluation and validation

2. **MLOps Infrastructure**
   - Experiment tracking (MLflow)
   - Model versioning
   - Training automation

3. **Model Deployment**
   - Inference service implementation
   - Model optimization (quantization, pruning)
   - Scalable serving architecture

4. **Monitoring**
   - Performance metrics
   - Data drift detection
   - Model quality tracking

Deliver production-ready ML system with monitoring.
```

### Phase 2: Code Review (Sequential after implementation)

#### Frontend Code Review

After frontend implementation, use the Task tool to launch a **general-purpose** agent (Frontend Code Reviewer context):

```
# AGENT CONTEXT: Principal Frontend Code Reviewer

You are a Principal Frontend Engineer conducting thorough code reviews for React and React Native applications. Your reviews focus on code quality, performance, accessibility, security, and maintainability.

## Review Focus Areas
1. **Functionality**: Correctness, edge cases, error handling, Hook rules
2. **Performance**: Re-renders, bundle size, code splitting, memoization, Web Vitals
3. **Accessibility**: WCAG 2.1 AA compliance, semantic HTML, keyboard navigation, ARIA
4. **Code Quality**: Readability, TypeScript types, component architecture
5. **Testing**: Coverage, test quality, integration tests
6. **Security**: XSS prevention, input validation, dependency vulnerabilities

## Review Philosophy
- Constructive and educational
- Explain the "why" behind suggestions
- Balance idealism with practical constraints
- Categorize feedback by severity

# TASK: Review the frontend implementation for: [USER INPUT FEATURE]

Code to review:
[PASTE FRONTEND CODE FROM PHASE 1]

## Backlog AC Verification (REQUIRED)

**Your Agent Identity**: @frontend-code-reviewer

Before approving code, you MUST:
1. **Review task ACs**: `backlog task <task-id> --plain`
2. **Verify AC completion matches code**: For each checked AC, confirm the code implements it
3. **Uncheck ACs if not satisfied**: `backlog task edit <task-id> --uncheck-ac <N>`
4. **Add review notes**: `backlog task edit <task-id> --append-notes $'Code Review:\n- Issue: ...\n- Suggestion: ...'`

**AC Verification Checklist**:
- [ ] Each checked AC has corresponding code changes
- [ ] Implementation notes accurately describe changes
- [ ] No undocumented functionality added
- [ ] Tests cover AC requirements

Conduct comprehensive review covering:

1. **Functionality**: Correctness, edge cases, error handling
2. **Performance**: Re-renders, bundle size, runtime performance
3. **Accessibility**: WCAG compliance, keyboard navigation, screen readers
4. **Code Quality**: Readability, maintainability, TypeScript types
5. **Testing**: Coverage, test quality
6. **Security**: XSS prevention, input validation

Provide categorized feedback:
- Critical (must fix before merge)
- High (should fix before merge)
- Medium (address soon)
- Low (nice to have)

Include specific, actionable suggestions.
```

#### Backend Code Review

After backend implementation, use the Task tool to launch a **general-purpose** agent (Backend Code Reviewer context):

```
# AGENT CONTEXT: Principal Backend Code Reviewer

You are a Principal Backend Engineer conducting thorough code reviews for Go, TypeScript (Node.js), and Python backend systems. Your reviews focus on code quality, security, performance, scalability, and maintainability.

## Review Focus Areas
1. **Security**: Authentication, authorization, injection prevention, data protection, secrets management
2. **Performance**: Database optimization (N+1 queries, indexes), scalability, resource management
3. **Code Quality**: Error handling, type safety, readability, maintainability
4. **API Design**: RESTful/GraphQL patterns, versioning, error responses
5. **Database**: Schema design, migrations, query efficiency, transactions
6. **Testing**: Coverage, integration tests, edge cases, error scenarios

## Security Priority
- SQL/NoSQL injection prevention
- Input validation and sanitization
- Proper authentication and authorization
- Secure secret management
- Dependency vulnerability scanning

## Code Hygiene Checks (CRITICAL - Must Block Merge if Failed)

### Unused Imports and Variables
- **BLOCK MERGE** if ANY unused imports exist
- **BLOCK MERGE** if ANY unused variables exist
- Run language-specific checks:
  - Python: `ruff check --select F401,F841`
  - Go: `go vet ./...` (compiler enforces)
  - TypeScript: `tsc --noEmit` with `noUnusedLocals`

### Defensive Coding Violations
- **BLOCK MERGE** if boundary functions lack input validation
- **BLOCK MERGE** if None/null not handled explicitly
- **BLOCK MERGE** if public functions lack type annotations (Python especially)
- Check for:
  - Functions accepting external data without validation
  - Missing type hints on public APIs
  - Implicit None handling (using value without checking)
  - Ignored errors (especially Go's `_` pattern)

# TASK: Review the backend implementation for: [USER INPUT FEATURE]

Code to review:
[PASTE BACKEND CODE FROM PHASE 1]

## Backlog AC Verification (REQUIRED)

**Your Agent Identity**: @backend-code-reviewer

Before approving code, you MUST:
1. **Review task ACs**: `backlog task <task-id> --plain`
2. **Verify AC completion matches code**: For each checked AC, confirm the code implements it
3. **Uncheck ACs if not satisfied**: `backlog task edit <task-id> --uncheck-ac <N>`
4. **Add review notes**: `backlog task edit <task-id> --append-notes $'Code Review:\n- Issue: ...\n- Suggestion: ...'`

**AC Verification Checklist**:
- [ ] Each checked AC has corresponding code changes
- [ ] Implementation notes accurately describe changes
- [ ] No undocumented functionality added
- [ ] Tests cover AC requirements
- [ ] Security requirements met

Conduct comprehensive review covering:

1. **Code Hygiene (BLOCKING)**:
   - Unused imports - MUST be zero
   - Unused variables - MUST be zero
   - Run: `ruff check --select F401,F841` (Python), `go vet` (Go), `tsc --noEmit` (TS)

2. **Defensive Coding (BLOCKING)**:
   - Input validation at boundaries - REQUIRED
   - Type annotations on public functions - REQUIRED
   - Explicit None/null handling - REQUIRED
   - No ignored errors - REQUIRED

3. **Security**: Authentication, authorization, injection prevention, secrets
4. **Performance**: Query optimization, scalability, resource management
5. **Code Quality**: Readability, error handling, type safety
6. **API Design**: RESTful/GraphQL patterns, error responses
7. **Database**: Schema design, migrations, query efficiency
8. **Testing**: Coverage, integration tests, edge cases

Provide categorized feedback:
- **Critical (BLOCK MERGE)**: Unused imports, missing validation, type safety violations
- High (fix before merge)
- Medium (address soon)
- Low (nice to have)

⚠️ ALWAYS flag as Critical:
- Any unused import or variable
- Missing input validation on boundary functions
- Missing type hints on public Python functions
- Ignored errors in Go code
- Missing runtime validation for external data

Include specific, actionable suggestions with examples.
```

### Phase 3: Iteration and Integration

1. **Address Review Feedback**
   - Fix critical and high-priority issues
   - Re-review if significant changes made

2. **Integration Testing**
   - Verify frontend-backend integration
   - Test complete user workflows
   - Validate API contracts

3. **Documentation**
   - Update API documentation
   - Add code comments for complex logic
   - Document configuration and deployment

### Phase 4: Pre-PR Validation (MANDATORY - NO EXCEPTIONS)

**⚠️ CRITICAL: Before creating any PR, you MUST run and pass ALL validation checks.**

This is a blocking gate enforced by rigor rules (VALID-001 through VALID-007). Do NOT create a PR until ALL checks pass.

#### Step 1: Verify Decision Logging (VALID-001 - BLOCKING)

All significant decisions MUST be logged before PR creation.

```bash
# Check decision log exists and has entries (VALID-001)
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")
DECISION_LOG="memory/decisions/${TASK_ID}.jsonl"

if [ ! -f "$DECISION_LOG" ]; then
  echo "[X] RIGOR VIOLATION (VALID-001): No decision log found: $DECISION_LOG"
  echo ""
  echo "You must log at least one decision. Examples of decisions to log:"
  echo "  - Technology choices (library, framework, pattern selection)"
  echo "  - Architecture changes"
  echo "  - Trade-off resolutions"
  echo "  - Deferred work decisions"
  echo ""
  echo "Fix: Log decisions using:"
  echo "  ./scripts/bash/rigor-decision-log.sh \\"
  echo "    --task ${TASK_ID} \\"
  echo "    --phase execution \\"
  echo "    --decision 'What was decided' \\"
  echo "    --rationale 'Why this choice' \\"
  echo "    --actor '@backend-engineer'"
  exit 1
fi

ENTRY_COUNT=$(wc -l < "$DECISION_LOG" 2>/dev/null || echo 0)
if [ "$ENTRY_COUNT" -eq 0 ]; then
  echo "[X] RIGOR VIOLATION (VALID-001): Decision log is empty"
  exit 1
fi

echo "✅ Decision traceability passed: $ENTRY_COUNT decisions logged"
```

#### Step 2: Run Lint Check (VALID-002 - BLOCKING)

```bash
# Python projects (VALID-002)
if [ -f "pyproject.toml" ]; then
  echo "Running lint check..."
  uv run ruff check .
  LINT_STATUS=$?

  if [ $LINT_STATUS -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-002): Lint check failed"
    echo "Fix: uv run ruff check --fix ."
    exit 1
  fi

  echo "✅ Lint check passed"
fi

# Go projects
if [ -f "go.mod" ]; then
  go vet ./...
  if [ $? -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-002): go vet failed"
    exit 1
  fi
fi

# TypeScript projects
if [ -f "package.json" ]; then
  npm run lint
  if [ $? -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-002): npm lint failed"
    exit 1
  fi
fi
```

**MUST pass with ZERO errors.** Fix all linting issues before proceeding.

#### Step 3: Run SAST Check (VALID-002 - BLOCKING)

```bash
# Python SAST check (VALID-002)
if [ -f "pyproject.toml" ]; then
  echo "Running SAST check..."
  if command -v bandit >/dev/null 2>&1; then
    uv run bandit -r src/ -ll
    if [ $? -ne 0 ]; then
      echo "[X] RIGOR VIOLATION (VALID-002): SAST check failed"
      echo "Review and fix security findings"
      exit 1
    fi
    echo "✅ SAST check passed"
  else
    echo "⚠️  WARNING: bandit not installed - skipping SAST"
  fi
fi
```

#### Step 4: Verify Coding Standards (VALID-003 - BLOCKING)

```bash
# Check for unused imports and variables (VALID-003)
if [ -f "pyproject.toml" ]; then
  echo "Checking coding standards compliance..."
  uv run ruff check --select F401,F841 .
  if [ $? -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-003): Unused imports or variables detected"
    echo "Fix: uv run ruff check --select F401,F841 --fix ."
    exit 1
  fi
  echo "✅ Coding standards check passed"
fi

# Go - compiler enforces
if [ -f "go.mod" ]; then
  go build ./...
  if [ $? -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-003): Build failed"
    exit 1
  fi
fi

# TypeScript
if [ -f "tsconfig.json" ]; then
  npx tsc --noEmit
  if [ $? -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-003): TypeScript check failed"
    exit 1
  fi
fi
```

**MUST have ZERO unused imports or variables.**

#### Step 5: Run Test Suite (VALID-007 - BLOCKING)

```bash
# Python projects (VALID-007)
if [ -f "pyproject.toml" ]; then
  echo "Running test suite..."
  uv run pytest tests/ -x -q
  TEST_STATUS=$?

  if [ $TEST_STATUS -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-007): Tests failed"
    echo "Fix failing tests before creating PR"
    exit 1
  fi

  echo "✅ Test suite passed"
fi

# Go projects
if [ -f "go.mod" ]; then
  go test ./...
  if [ $? -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-007): Tests failed"
    exit 1
  fi
fi

# TypeScript projects
if [ -f "package.json" ]; then
  npm test
  if [ $? -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-007): Tests failed"
    exit 1
  fi
fi
```

**MUST pass with ZERO failures.** Fix all failing tests before proceeding.

#### Step 6: Format Code (VALID-007 - BLOCKING)

```bash
# Python projects
if [ -f "pyproject.toml" ]; then
  echo "Checking code formatting..."
  uv run ruff format --check .
  FORMAT_STATUS=$?

  if [ $FORMAT_STATUS -ne 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-007): Code not formatted"
    echo "Fix: uv run ruff format ."
    exit 1
  fi

  echo "✅ Code formatting check passed"
fi

# Go projects
if [ -f "go.mod" ]; then
  UNFORMATTED_FILES="$(gofmt -l .)"
  if [ -n "$UNFORMATTED_FILES" ]; then
    echo "[X] RIGOR VIOLATION (VALID-007): Code not formatted"
    echo "The following files need formatting:"
    echo "$UNFORMATTED_FILES"
    echo "Fix: gofmt -w ."
    exit 1
  fi
fi

# TypeScript projects
if [ -f "package.json" ]; then
  if grep -q '"format:check"' package.json; then
    # Use format:check if available
    npm run format:check
    if [ $? -ne 0 ]; then
      echo "[X] RIGOR VIOLATION (VALID-007): Code not formatted"
      echo "Fix: npm run format"
      exit 1
    fi
  elif command -v prettier >/dev/null 2>&1; then
    # Fall back to prettier --check if available
    prettier --check . 2>/dev/null
    if [ $? -ne 0 ]; then
      echo "[X] RIGOR VIOLATION (VALID-007): Code not formatted"
      echo "Fix: prettier --write ."
      exit 1
    fi
  fi
fi
```

#### Step 7: Verify Rebase Status (VALID-004 - BLOCKING)

```bash
# Check branch is rebased from main (VALID-004)
echo "Checking rebase status..."
git fetch origin main 2>/dev/null
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo 0)

if [ "$BEHIND" -gt 0 ]; then
  echo "[X] RIGOR VIOLATION (VALID-004): Branch is $BEHIND commits behind main"
  echo ""
  echo "Fix: Rebase from main:"
  echo "  git fetch origin main"
  echo "  git rebase origin/main"
  echo "  # Resolve conflicts if any"
  echo "  git push --force-with-lease origin $(git branch --show-current)"
  exit 1
fi

echo "✅ Rebase status check passed"
```

#### Step 8: Verify Acceptance Criteria (VALID-005 - BLOCKING)

```bash
# Check all ACs are complete (VALID-005)
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")

if [ -n "$TASK_ID" ]; then
  echo "Verifying acceptance criteria..."
  INCOMPLETE=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep -c "^\[ \]" || echo 0)

  if [ "$INCOMPLETE" -gt 0 ]; then
    echo "[X] RIGOR VIOLATION (VALID-005): $INCOMPLETE incomplete acceptance criteria"
    backlog task "$TASK_ID" --plain | grep "^\[ \]"
    echo ""
    echo "Fix: Complete all ACs or document why they cannot be completed"
    echo "  backlog task edit ${TASK_ID} --check-ac <N>"
    exit 1
  fi

  echo "✅ All acceptance criteria met"
fi
```

#### Step 9: Verify Task Status (VALID-006 - BLOCKING)

```bash
# Verify task status is current (VALID-006)
# Extract TASK_ID from branch (each code block is independent in markdown)
TASK_ID=$(git branch --show-current 2>/dev/null | grep -Eo 'task-[0-9]+' || echo "")

if [ -n "$TASK_ID" ]; then
  echo "Verifying task status..."
  # Extract full status (handles multi-word statuses like "In Progress")
  STATUS=$(backlog task "$TASK_ID" --plain 2>/dev/null | grep "Status:" | head -1 | sed 's/^Status:[[:space:]]*//')

  if [ "$STATUS" != "In Progress" ]; then
    echo "⚠️  WARNING (VALID-006): Task status may be stale: $STATUS"
    echo "Update task status before PR:"
    echo "  backlog task edit ${TASK_ID} -s 'In Progress'"
  else
    echo "✅ Task status current"
  fi
fi
```

#### Validation Checklist (ALL REQUIRED)

Before creating the PR, verify ALL of these:

- [ ] **VALID-001**: Decision log exists with entries
- [ ] **VALID-002**: Lint check passes (`ruff check .`)
- [ ] **VALID-002**: SAST check passes (if bandit installed)
- [ ] **VALID-003**: No unused imports (`ruff check --select F401`)
- [ ] **VALID-003**: No unused variables (`ruff check --select F841`)
- [ ] **VALID-007**: Test suite passes (`pytest tests/ -x -q`)
- [ ] **VALID-007**: Code is formatted (`ruff format --check .`)
- [ ] **VALID-004**: Branch rebased from main (zero commits behind)
- [ ] **VALID-005**: All acceptance criteria are marked complete
- [ ] **VALID-006**: Task status reflects current state
- [ ] **PR-001**: All commits have DCO sign-off

**⚠️ DO NOT proceed to create a PR if ANY checklist item is incomplete.**

PRs that fail CI:
- Waste reviewer time
- Create noise in the repository
- Demonstrate lack of due diligence
- Will be closed without review

#### Step 10: Verify DCO Sign-off (PR-001 - BLOCKING)

```bash
# Check all commits have DCO sign-off (PR-001)
echo "Checking DCO sign-off..."
# POSIX-compliant iteration over commit hashes (avoids bash-specific process substitution)
UNSIGNED_COMMITS=""
for hash in $(git log origin/main..HEAD --format='%h' 2>/dev/null); do
  if ! git log -1 --format='%B' "$hash" 2>/dev/null | grep -q "Signed-off-by:"; then
    UNSIGNED_COMMITS="$UNSIGNED_COMMITS $hash"
  fi
done
UNSIGNED_COUNT=$(echo "$UNSIGNED_COMMITS" | wc -w)

if [ "$UNSIGNED_COUNT" -gt 0 ]; then
  echo "[X] RIGOR VIOLATION (PR-001): $UNSIGNED_COUNT commits missing DCO sign-off"
  echo ""
  echo "Fix: Add sign-off to all commits:"
  echo "  git rebase origin/main --exec 'git commit --amend --no-edit -s'"
  echo "  git push --force-with-lease origin $(git branch --show-current)"
  exit 1
fi

echo "✅ DCO sign-off check passed"
```

#### Step 11: Create PR (Only After All Checks Pass)

Once all validation passes:

```bash
# Commit changes with DCO sign-off
git add .
git commit -s -m "feat(scope): description"

# Push and create PR
git push origin <branch-name>
gh pr create --title "feat: description" --body "..."
```

### Deliverables (ALL THREE REQUIRED)

Implementation is **code + documents + tests**. All three are mandatory deliverables.

#### 1. Production Code
- Fully implemented, reviewed source code
- All acceptance criteria satisfied
- Code review feedback addressed
- Pre-PR validation passing (lint, format, tests)

#### 2. Key Documents
- Updated/created API documentation
- Code comments for complex logic
- Configuration and deployment docs
- Any new ADRs for implementation decisions

#### 3. Complete Tests
- Unit tests for all new functions/methods
- Integration tests for API endpoints
- Edge case coverage (empty inputs, errors, boundaries)
- Test coverage meeting project minimum (typically 80%)

**Implementation is NOT complete until all three are delivered.**

| Deliverable | Verification |
|-------------|--------------|
| Code | PR passes CI, code review approved |
| Documents | API docs updated, comments added |
| Tests | `pytest`/`go test`/`npm test` passes, coverage met |

## Post-Completion: Emit Workflow Event

After successfully completing this command (implementation done, reviews passed, pre-PR validation complete), emit the workflow event:

```bash
flowspec hooks emit implement.completed \
  --spec-id "$FEATURE_ID" \
  --task-id "$TASK_ID" \
  -f src/$FEATURE_ID/
```

Replace `$FEATURE_ID` with the feature name/identifier and `$TASK_ID` with the backlog task ID if available.

This triggers any configured hooks in `.flowspec/hooks/hooks.yaml` (e.g., running tests, quality gates, notifications).

## Telemetry: Track Agent Invocations

After implementation completes, track the agents that were invoked for analytics (if telemetry is enabled):

```bash
# Track each agent that was invoked during this command (silently, will be no-op if disabled)

# Track the command execution
flowspec telemetry track-role "$CURRENT_ROLE" --command /flow:implement -q

# If frontend work was done:
flowspec telemetry track-agent frontend-engineer --command /flow:implement -q

# If backend work was done:
flowspec telemetry track-agent backend-engineer --command /flow:implement -q

# If AI/ML work was done:
flowspec telemetry track-agent ai-ml-engineer --command /flow:implement -q

# If code reviews were performed:
flowspec telemetry track-agent frontend-code-reviewer --command /flow:implement -q
flowspec telemetry track-agent backend-code-reviewer --command /flow:implement -q
```

Replace `$CURRENT_ROLE` with the user's current role (dev, pm, qa, etc.).

This enables workflow analytics for understanding agent usage patterns. The tracking is:
- **Opt-in only**: Only recorded if user has enabled telemetry via `flowspec telemetry enable`
- **Privacy-first**: Project names are hashed, no PII collected
- **Fail-safe**: Commands will not fail if telemetry is unavailable
