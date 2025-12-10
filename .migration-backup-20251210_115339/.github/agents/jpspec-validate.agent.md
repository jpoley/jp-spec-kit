---
name: "jpspec-validate"
description: "Execute validation and quality assurance using QA, security, documentation, and release management agents."
target: "chat"
tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Grep"
  - "Glob"
  - "Bash"
  - "mcp__backlog__*"
  - "mcp__serena__*"
  - "Skill"

handoffs:
  - label: "Deploy to Production"
    agent: "jpspec-operate"
    prompt: "Validation is complete. Deploy the feature to production and configure operations."
    send: false
---
# /jpspec:validate - Enhanced Phased Validation Workflow

Execute comprehensive validation workflow with task orchestration, automated testing, agent validation, AC verification, and PR generation.

## User Input

```text
$ARGUMENTS
```

**Expected Input**: Optional task ID (e.g., `task-094`). If not provided, command discovers the current in-progress task automatically.

# Constitution Pre-flight Check

**CRITICAL**: This command requires constitution validation before execution (unless `--skip-validation` is provided).

## Step 0.5: Check Constitution Status

Before executing this workflow command, validate the project's constitution:

### 1. Check Constitution Exists

```bash
# Look for constitution file
if [ -f "memory/constitution.md" ]; then
  echo "✓ Constitution found"
else
  echo "⚠️ No constitution found"
  echo ""
  echo "To create one:"
  echo "  1. Run: specify init --here"
  echo "  2. Then: Run /speckit:constitution to customize"
  echo ""
  echo "Proceeding without constitution..."
fi
```

If no constitution exists:
- Warn the user
- Suggest creating one with `specify init --here`
- Continue with command (constitution is recommended but not required)

### 2. If Constitution Exists, Check Validation Status

```bash
# Detect tier from TIER comment (default: Medium if not found)
TIER=$(grep -o "TIER: \(Light\|Medium\|Heavy\)" memory/constitution.md | cut -d' ' -f2)
TIER=${TIER:-Medium}  # Default to Medium if not found

# Count NEEDS_VALIDATION markers
MARKER_COUNT=$(grep -c "NEEDS_VALIDATION" memory/constitution.md || echo 0)

# Extract section names from NEEDS_VALIDATION markers
SECTIONS=$(grep "NEEDS_VALIDATION" memory/constitution.md | sed 's/.*NEEDS_VALIDATION: /  - /')

echo "Constitution tier: $TIER"
echo "Unvalidated sections: $MARKER_COUNT"
```

### 3. Apply Tier-Based Enforcement

#### Light Tier - Warn Only

If `TIER = Light` and `MARKER_COUNT > 0`:

```text
⚠️ Constitution has N unvalidated sections:
$SECTIONS

Consider running /speckit:constitution to customize your constitution.

Proceeding with command...
```

Then continue with the command.

#### Medium Tier - Warn and Confirm

If `TIER = Medium` and `MARKER_COUNT > 0`:

```text
⚠️ Constitution Validation Recommended

Your constitution has N unvalidated sections:
$SECTIONS

Medium tier projects should validate their constitution before workflow commands.

Options:
  1. Continue anyway (y/N)
  2. Run /speckit:constitution to customize
  3. Run specify constitution validate to check status

Continue without validation? [y/N]: _
```

Wait for user response:
- If user responds `y` or `yes` → Continue with command
- If user responds `n`, `no`, or empty/Enter → Stop and show:
  ```text
  Command cancelled. Run /speckit:constitution to customize your constitution.
  ```

#### Heavy Tier - Block Until Validated

If `TIER = Heavy` and `MARKER_COUNT > 0`:

```text
❌ Constitution Validation Required

Your constitution has N unvalidated sections:
$SECTIONS

Heavy tier constitutions require full validation before workflow commands.

To resolve:
  1. Run /speckit:constitution to customize your constitution
  2. Run specify constitution validate to verify
  3. Remove all NEEDS_VALIDATION markers

Or use --skip-validation to bypass (not recommended).

Command blocked until constitution is validated.
```

**DO NOT PROCEED** with the command. Exit and wait for user to resolve.

### 4. Skip Validation Flag

If the command was invoked with `--skip-validation`:

```bash
# Check for skip flag in arguments
if [[ "$ARGUMENTS" == *"--skip-validation"* ]]; then
  echo "⚠️ Skipping constitution validation (--skip-validation)"
  # Remove the flag from arguments and continue
  ARGUMENTS="${ARGUMENTS/--skip-validation/}"
fi
```

When skip flag is present:
- Log warning
- Skip all validation checks
- Continue with command
- Note: For emergency use only

### 5. Fully Validated Constitution

If `MARKER_COUNT = 0`:

```text
✓ Constitution validated
```

Continue with command normally.

## Summary: When to Block vs Warn

| Tier | Unvalidated Sections | Action |
|------|---------------------|--------|
| Light | 0 | ✓ Continue |
| Light | >0 | ⚠️ Warn, continue |
| Medium | 0 | ✓ Continue |
| Medium | >0 | ⚠️ Warn, ask confirmation, respect user choice |
| Heavy | 0 | ✓ Continue |
| Heavy | >0 | ❌ Block, require validation |
| Any | >0 + `--skip-validation` | ⚠️ Warn, continue |

## Integration Example

```markdown
---
description: Your command description
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

{{INCLUDE:.claude/commands/jpspec/_constitution-check.md}}

{{INCLUDE:.claude/commands/jpspec/_workflow-state.md}}

## Execution Instructions

[Rest of your command implementation...]
```

## Related Commands

| Command | Purpose |
|---------|---------|
| `specify init --here` | Initialize constitution if missing |
| `/speckit:constitution` | Interactive constitution customization |
| `specify constitution validate` | Check validation status and show report |
| `specify constitution show` | Display current constitution |


# Workflow State Validation

## Step 0: Workflow State Validation (REQUIRED)

**CRITICAL**: This command requires a task to be in the correct workflow state before execution.

### Light Mode Detection

First, check if this project is in light mode:

```bash
# Check for light mode marker
if [ -f ".jpspec-light-mode" ]; then
  echo "Project is in LIGHT MODE (~60% faster workflow)"
fi
```

**Light Mode Behavior**:
- `/jpspec:research` → **SKIPPED** (inform user and suggest `/jpspec:plan` instead)
- `/jpspec:plan` → Uses `plan-light.md` template (high-level only)
- `/jpspec:specify` → Uses `spec-light.md` template (combined stories + AC)

If in light mode and the current command is `/jpspec:research`, inform the user:
```text
ℹ️ This project is in Light Mode

Light mode skips the research phase for faster iteration.
Current state: workflow:Specified

Suggestions:
  - Run /jpspec:plan to proceed directly to planning
  - To enable research, delete .jpspec-light-mode and use full mode
  - See docs/guides/when-to-use-light-mode.md for details
```

### 1. Get Current Task and State

```bash
# Find the task you're working on
# Option A: If task ID was provided in arguments, use that
# Option B: Look for task currently "In Progress"
backlog task list -s "In Progress" --plain

# Get task details and extract workflow state from labels
TASK_ID="<task-id>"  # Replace with actual task ID
backlog task "$TASK_ID" --plain
```

### 2. Check Workflow State

Extract the `workflow:*` label from the task. The state must match one of the **Required Input States** for this command:

| Command | Required Input States | Output State |
|---------|----------------------|--------------|
| /jpspec:assess | workflow:To Do, (no workflow label) | workflow:Assessed |
| /jpspec:specify | workflow:Assessed | workflow:Specified |
| /jpspec:research | workflow:Specified | workflow:Researched |
| /jpspec:plan | workflow:Specified, workflow:Researched | workflow:Planned |
| /jpspec:implement | workflow:Planned | workflow:In Implementation |
| /jpspec:validate | workflow:In Implementation | workflow:Validated |
| /jpspec:operate | workflow:Validated | workflow:Deployed |

### 3. Handle Invalid State

If the task's workflow state doesn't match the required input states:

```text
⚠️ Cannot run /jpspec:<command>

Current state: "<current-workflow-label>"
Required states: <list-of-valid-input-states>

Suggestions:
  - Valid workflows for current state: <list-valid-commands>
  - Use --skip-state-check to bypass (not recommended)
```

**DO NOT PROCEED** unless:
- The task is in a valid input state, OR
- User explicitly requests to skip the check

### 4. Update State After Completion

After successful workflow completion, update the task's workflow state:

```bash
# Remove old workflow label and add new one
# Replace <output-state> with the output state from the table above
backlog task edit "$TASK_ID" -l "workflow:<output-state>"
```

## Workflow State Labels Reference

Tasks use labels with the `workflow:` prefix to track their current workflow state:

- `workflow:Assessed` - SDD suitability evaluated (/jpspec:assess complete)
- `workflow:Specified` - Requirements captured (/jpspec:specify complete)
- `workflow:Researched` - Technical research completed (/jpspec:research complete)
- `workflow:Planned` - Architecture planned (/jpspec:plan complete)
- `workflow:In Implementation` - Code being written (/jpspec:implement in progress)
- `workflow:Validated` - QA and security validated (/jpspec:validate complete)
- `workflow:Deployed` - Released to production (/jpspec:operate complete)

## Programmatic State Checking

The state guard module can also be used programmatically:

```python
from specify_cli.workflow import check_workflow_state, get_valid_workflows

# Check if current state allows command execution
can_proceed, message = check_workflow_state("implement", current_state)

if not can_proceed:
    print(message)
    # Shows error with suggestions

# Get valid commands for a state
valid_commands = get_valid_workflows("Specified")
# Returns: ['/jpspec:research', '/jpspec:plan']
```

## Bypassing State Checks (Power Users Only)

State checks can be bypassed in special circumstances:
- Emergency hotfixes
- Iterative refinement of specifications
- Recovery from failed workflows

Use `--skip-state-check` flag or explicitly acknowledge the bypass.

**Warning**: Bypassing state checks may result in incomplete artifacts or broken workflows.


**For /jpspec:validate**: Required input state is `workflow:In Implementation`. Output state will be `workflow:Validated`.

If the task doesn't have the required workflow state, inform the user:
- If task needs implementation first: suggest running `/jpspec:implement`
- If validation is being re-run on deployed work: use `--skip-state-check` if appropriate

**Proceed to Phase 0 ONLY if workflow validation passes.**

### Extended Thinking Mode

> **🧠 Think Hard**: Security and quality validation require thorough analysis. Apply extended thinking to:
> - Attack vectors and vulnerability assessment
> - Data flow security and authentication boundaries
> - Test coverage gaps and edge cases
> - Compliance requirements and best practices

## Workflow Overview

This command orchestrates a phased validation workflow:

- **Phase 0: Task Discovery & Load** - Find/load target task
- **Phase 1: Automated Testing** - Run tests, linting, type checks
- **Phase 2: Agent Validation (Parallel)** - QA Guardian + Security Engineer
- **Phase 3: Documentation** - Technical Writer agent
- **Phase 4: AC Verification** - Verify all acceptance criteria
- **Phase 5: Task Completion** - Generate notes and mark Done
- **Phase 6: PR Generation** - Create pull request with approval

## Execution Instructions

Follow these phases sequentially. **Phase failures MUST halt the workflow** with clear error messages indicating which phase failed and why.

The command is **re-runnable** after fixing issues - it handles partial completion gracefully by checking task state at each phase.

---

### Phase 0: Task Discovery & Load

**Report progress**: Print "Phase 0: Discovering and loading task..."

#### Step 1: Determine Target Task ID

```bash
# If user provided task-id argument, use it
TASK_ID="$ARGUMENTS"

# Otherwise, discover in-progress task
if [ -z "$TASK_ID" ]; then
  # Find tasks in "In Progress" status
  backlog task list -s "In Progress" --plain
fi
```

**Task Selection Logic**:
- If user provided task ID: Use it directly
- If no argument: Find the single "In Progress" task
- If multiple "In Progress" tasks: Ask user which one to validate
- If no "In Progress" tasks: Error and halt

**Error Handling**:
- If task ID not found: "❌ Phase 0 Failed: Task {task-id} does not exist."
- If no in-progress tasks: "❌ Phase 0 Failed: No tasks in 'In Progress' status. Please specify a task ID."
- If multiple in-progress tasks: List them and ask user to specify which one

#### Step 2: Load Full Task Details

```bash
# Load complete task data
backlog task <task-id> --plain
```

**Parse critical fields**:
- Task ID
- Title
- Description
- Acceptance Criteria (list with checked status)
- Current Status
- Implementation Plan (if exists)
- Implementation Notes (if exists)

**Phase 0 Success**: Print task summary:
```
✅ Phase 0 Complete: Loaded task-094
   Title: Integration - Enhanced /jpspec:validate Command
   Status: In Progress
   ACs: 0/8 complete
```

---

### Phase 1: Automated Testing

**Report progress**: Print "Phase 1: Running automated tests, linting, and type checks..."

**Important**: Only run tests if code changes are involved. Skip for documentation-only tasks.

#### Step 1: Detect Project Type

```bash
# Check for test frameworks
if [ -f "pyproject.toml" ]; then
  # Python project
  echo "Detected Python project"
elif [ -f "package.json" ]; then
  # Node.js project
  echo "Detected Node.js project"
fi
```

#### Step 2: Run Test Suite

**For Python projects**:
```bash
# Run pytest with coverage
pytest tests/ -v --cov=src/specify_cli --cov-report=term-missing

# Run linting
ruff check . --output-format=concise

# Run type checks (if mypy configured)
if [ -f "pyproject.toml" ] && grep -q "mypy" pyproject.toml; then
  mypy src/
fi
```

**For Node.js projects**:
```bash
# Run tests
npm test  # or bun test, pnpm test

# Run linting
npm run lint  # or eslint .

# Run type checks
npm run typecheck  # or tsc --noEmit
```

#### Step 3: Evaluate Results

**Success criteria**:
- All tests pass (exit code 0)
- No critical linting errors
- Type checks pass (if applicable)

**Error Handling**:
- If tests fail: "❌ Phase 1 Failed: {N} test(s) failed. Fix tests before continuing."
- If linting fails: "⚠️  Phase 1 Warning: Linting issues detected. Review before continuing."
- If type checks fail: "❌ Phase 1 Failed: Type check errors found."

**Phase 1 Success**: Print test summary:
```
✅ Phase 1 Complete: All automated checks passed
   Tests: 45 passed
   Coverage: 87%
   Linting: No issues
   Type checks: Passed
```

**Re-run handling**: If tests already passed in previous run, skip and print:
```
⏭️  Phase 1 Skipped: Tests already validated in previous run
```

---

### Phase 2: Agent Validation (Parallel Execution)

**Report progress**: Print "Phase 2: Launching QA Guardian and Security Engineer agents (parallel)..."

**IMPORTANT**: Launch QA and Security agents in parallel for efficiency using the Task tool.

#### Backlog Instructions Template

Each validator agent context below includes `{{BACKLOG_INSTRUCTIONS}}` which must be replaced with the content from `.claude/commands/jpspec/_backlog-instructions.md`. This ensures all agents have consistent backlog task management instructions.

**When executing this command, include the full content of `_backlog-instructions.md` in place of each `{{BACKLOG_INSTRUCTIONS}}` marker.**

#### Agent 1: Quality Guardian (QA Testing)

Use the Task tool to launch a **general-purpose** agent (Quality Guardian context):

```
# AGENT CONTEXT: Quality Guardian

You are the Quality Guardian, a vigilant protector of system integrity, user trust, and organizational reputation. You are the constructive skeptic who sees failure modes others miss, anticipates edge cases others ignore, and champions excellence as the minimum acceptable standard.

## Core Philosophy
- **Constructive Skepticism**: Question everything with intent to improve
- **Risk Intelligence**: See potential failures as opportunities for resilience
- **User-Centric**: Champion end user experience above all else
- **Long-Term Thinking**: Consider maintenance, evolution, technical debt from day one
- **Security-First**: Every feature is a potential vulnerability until proven otherwise

## Analysis Framework
1. **Failure Imagination Exercise**: List failure modes, assess impact/likelihood, plan detection/recovery
2. **Edge Case Exploration**: Test at zero, infinity, malformed input, extreme load, hostile users
3. **Three-Layer Critique**: Acknowledge value → Identify risk → Suggest mitigation
4. **Risk Classification**: Critical, High, Medium, Low

## Risk Dimensions

{{BACKLOG_INSTRUCTIONS}}
- Technical: Scalability, performance, reliability, concurrency
- Security: Vulnerabilities, attack surfaces, data exposure
- Business: Cost overruns, market timing, operational complexity
- User: Usability issues, adoption barriers, accessibility
- Operational: Maintenance burden, monitoring, debugging

# TASK: Conduct comprehensive quality validation for: [USER INPUT FEATURE]

Code and Artifacts:


Backlog Context:
[Include backlog task details from discovery phase if applicable]

Validation Requirements:

1. **Functional Testing & Acceptance Criteria Validation**
   - **Verify all backlog task acceptance criteria are met**
   - Cross-reference test results with AC requirements
   - **Mark ACs complete via backlog CLI as validation succeeds**
   - Test user workflows end-to-end
   - Validate edge cases and boundary conditions
   - Test error handling and recovery

2. **API and Contract Testing**
   - API endpoint testing (REST/GraphQL/gRPC)
   - Contract testing for API compatibility
   - Response validation
   - Error response testing

3. **Integration Testing**
   - Frontend-backend integration
   - Third-party service integration
   - Database integration
   - Message queue/event processing

4. **Performance Testing**
   - Load testing (expected traffic)
   - Stress testing (peak traffic)
   - Latency measurement (p50, p95, p99)
   - Resource utilization
   - Scalability validation

5. **Non-Functional Requirements**
   - Accessibility (WCAG 2.1 AA compliance)
   - Cross-browser/platform compatibility
   - Mobile responsiveness
   - Internationalization (if applicable)

6. **Risk Analysis**
   - Identify failure modes
   - Assess impact and likelihood
   - Validate monitoring and alerting
   - Verify rollback procedures

Deliver comprehensive test report with:
- Test results (passed/failed)
- Quality metrics
- Risk assessment
- Issues categorized by severity
- Recommendations for production readiness
```

**Phase 2 Success**: Print summary when both agents complete:
```
✅ Phase 2 Complete: Agent validation passed
   QA Guardian: 15 test scenarios validated
   Security Engineer: No critical vulnerabilities found
```

#### Agent 2: Security Engineer

Use the Task tool to launch a **general-purpose** agent (Secure-by-Design Engineer context):

```
# AGENT CONTEXT: Secure-by-Design Engineer

You are a Secure-by-Design Engineer, an experienced security specialist focused on building security into the development lifecycle from the ground up. Security is not a feature to be added later, but a fundamental quality built into every aspect of the system from the beginning.

## Core Principles
- **Assume Breach**: Design as if systems will be compromised
- **Defense in Depth**: Multiple security layers
- **Principle of Least Privilege**: Minimum necessary access
- **Fail Securely**: Failures don't compromise security
- **Security by Default**: Secure out of the box

## Security Analysis Process
1. **Risk Assessment**: Identify assets, threats, business impact
2. **Threat Modeling**: Assets, threats, attack vectors
3. **Architecture Analysis**: Security weaknesses in design
4. **Code Review**: Vulnerability patterns (SQL injection, XSS, etc.)
5. **Access Control Review**: Authentication, authorization, privilege management
6. **Data Flow Analysis**: Sensitive information handling
7. **Dependency Security**: Third-party vulnerabilities
8. **Incident Response**: Monitoring and detection capabilities

## Severity Classification
- **Critical**: Authentication bypass, SQL injection, RCE
- **High**: XSS, privilege escalation, data exposure
- **Medium**: Information disclosure, DoS, weak crypto
- **Low**: Config issues, missing headers

{{BACKLOG_INSTRUCTIONS}}

# TASK: Conduct comprehensive security assessment for: [USER INPUT FEATURE]

Code and Infrastructure:
[Include implementation code, infrastructure configs, dependencies]

Backlog Context:
[Include backlog task details with security-related acceptance criteria]

Security Validation Requirements:

0. **Backlog Task Security Validation**
   - Validate security-related acceptance criteria
   - Cross-reference security tests with task ACs
   - Mark security ACs complete via backlog CLI as validations pass
   - Update task notes with security findings

1. **Code Security Review**
   - Authentication and authorization implementation
   - Input validation and sanitization
   - SQL/NoSQL injection prevention
   - XSS/CSRF prevention
   - Secure error handling (no sensitive data exposure)

2. **Dependency Security**
   - Scan for known vulnerabilities (CVEs)
   - Check dependency licenses
   - Validate supply chain security
   - Review SBOM (Software Bill of Materials)

3. **Infrastructure Security**
   - Secrets management validation
   - Network security configuration
   - Access controls and IAM
   - Encryption at rest and in transit
   - Container security (if applicable)

4. **Compliance**
   - GDPR compliance (if handling EU data)
   - SOC2 requirements
   - Industry-specific regulations
   - Data privacy requirements

5. **Threat Modeling**
   - Identify attack vectors
   - Assess exploitability
   - Validate security controls
   - Test defense in depth

6. **Penetration Testing** (for critical features)
   - Manual security testing
   - Automated vulnerability scanning
   - Authentication bypass attempts
   - Authorization escalation tests

Deliver comprehensive security report with:
- Security findings by severity (Critical/High/Medium/Low)
- Vulnerability details with remediation steps
- Compliance status
- Risk assessment
- Security gate approval status (Pass/Fail)
```

---

### Phase 3: Documentation

**Report progress**: Print "Phase 3: Launching Technical Writer agent for documentation..."

Use the Task tool to launch a **general-purpose** agent (Technical Writer context):

```
# AGENT CONTEXT: Senior Technical Writer

You are a Senior Technical Writer with deep expertise in creating clear, accurate, and audience-appropriate technical documentation. You transform complex technical concepts into accessible content that enables users, developers, and stakeholders to understand and effectively use software systems.

## Core Goals
- **Enable Users**: Help users accomplish their goals efficiently
- **Reduce Support**: Answer questions before they're asked
- **Build Trust**: Accurate, tested, up-to-date content
- **Scale Knowledge**: Transfer knowledge across teams and time
- **Support Different Audiences**: Technical and non-technical readers

## Documentation Types
- **API Documentation**: REST/GraphQL endpoints, parameters, examples, responses
- **User Guides**: Getting started, tutorials, how-to guides
- **Technical Documentation**: Architecture, components, configuration, deployment
- **Release Notes**: Features, breaking changes, migration guides
- **Operational Documentation**: Runbooks, monitoring, troubleshooting

## Quality Standards
- Clear structure and hierarchy
- Audience-appropriate language
- Tested, working examples
- Comprehensive but concise
- Searchable and navigable
- Accessible (alt text, headings, etc.)

{{BACKLOG_INSTRUCTIONS}}

# TASK: Create comprehensive documentation for: [USER INPUT FEATURE]

Context:
[Include feature description, implementation details, API specs, test results, security findings]

Backlog Context:
[Include backlog task details for documentation requirements]

## Documentation Task Management

Create backlog tasks for major documentation work:

```bash
# Example: Create documentation task
backlog task create "Documentation: API Reference for [Feature]" \
  -d "Complete API documentation for the feature" \
  --ac "API documentation complete" \
  --ac "Code examples provided and tested" \
  --ac "Error responses documented" \
  -l docs,api \
  --priority medium \
  -a @tech-writer
```

As you complete documentation sections, mark corresponding ACs:
```bash
backlog task edit <id> --check-ac 1  # API documentation complete
```

Documentation Deliverables:

1. **API Documentation** (if API changes)
   - Endpoint documentation
   - Request/response examples
   - Authentication requirements
   - Error codes and messages
   - Rate limiting and quotas

2. **User Documentation**
   - Feature overview and benefits
   - Getting started guide
   - Step-by-step tutorials
   - Screenshots/diagrams
   - Troubleshooting guide

3. **Technical Documentation**
   - Architecture overview
   - Component documentation
   - Configuration options
   - Deployment instructions
   - Monitoring and alerting setup

4. **Release Notes**
   - Feature summary
   - Breaking changes (if any)
   - Migration guide (if needed)
   - Known limitations
   - Bug fixes

5. **Internal Documentation**
   - Code comments for complex logic
   - Runbooks for operations
   - Incident response procedures
   - Rollback procedures

Ensure all documentation is:
- Accurate and up-to-date
- Clear and audience-appropriate
- Well-formatted with proper structure
- Accessible (alt text, headings, etc.)
- Ready for publication
```

**Phase 3 Success**: Print summary:
```
✅ Phase 3 Complete: Documentation updated
   Files updated: 3
   Sections added: User Guide, API Reference
```

---

### Phase 4: Acceptance Criteria Verification

**Report progress**: Print "Phase 4: Verifying acceptance criteria completion..."

This phase systematically verifies all task acceptance criteria are met.

#### Step 1: Load Current Task State

```bash
# Reload task to get latest AC status
backlog task <task-id> --plain
```

#### Step 2: Parse Acceptance Criteria

Extract the list of acceptance criteria with their checked status:
```json
{
  "acceptanceCriteria": [
    {"text": "Command accepts optional task-id argument", "checked": false},
    {"text": "Executes phases in order", "checked": false},
    ...
  ]
}
```

#### Step 3: Verify Each AC

For each unchecked acceptance criterion:

**Automated ACs** (can be verified by test results):
- Check if corresponding tests passed in Phase 1
- If tests passed, mark AC complete: `backlog task edit <task-id> --check-ac N`

**Manual ACs** (require human verification):
- Present AC to user
- Show relevant evidence (test output, code changes, agent reports)
- Ask user: "Has this acceptance criterion been met? [y/N]"
- If yes, mark complete: `backlog task edit <task-id> --check-ac N`
- If no, halt and report which AC failed

#### Step 4: Verify 100% Completion

After verification loop:
```bash
# Reload task to confirm all ACs checked
backlog task <task-id> --plain
```

**Success criteria**: All ACs must have `"checked": true`

**Error Handling**:
- If any AC unchecked: "❌ Phase 4 Failed: {N} acceptance criteria not yet verified. Cannot proceed to completion."
- List unchecked ACs by index and text

**Phase 4 Success**: Print summary:
```
✅ Phase 4 Complete: All acceptance criteria verified
   Total ACs: 8
   Verified: 8
   Status: 100% complete
```

---

### Phase 5: Task Completion

**Report progress**: Print "Phase 5: Generating implementation notes and marking task complete..."

#### Step 1: Generate Implementation Summary

Create comprehensive implementation notes based on:
- What was implemented (from task description and changes)
- How it was tested (from Phase 1 test results)
- Key decisions made (from agent reports)
- Validation results (from Phases 2-3)

**Example implementation notes format**:
```markdown
## Implementation Summary (2025-12-01 15:30:00)

### What Was Implemented
Enhanced the /jpspec:validate command with phased orchestration workflow.
Implemented 7 distinct phases with progress reporting and error handling.

### Testing
- All unit tests passing (45/45)
- Integration tests passing (12/12)
- Linting: No issues
- Type checks: Passed

### Key Decisions
- Used TaskCompletionHandler pattern for AC verification
- Implemented re-runnable workflow with state checks
- Added progress reporting at each phase
- Parallel agent execution in Phase 2 for efficiency

### Validation Results
- QA Guardian: 15 scenarios validated, all passed
- Security Engineer: No critical vulnerabilities
- Documentation: Updated 2 command files
```

#### Step 2: Add Implementation Notes

```bash
backlog task edit <task-id> --notes $'<implementation-summary>'
```

#### Step 3: Mark Task as Done

**Important**: Only mark Done if task status is currently "In Progress"

```bash
# Check current status first
backlog task <task-id> --plain

# If status is "In Progress", mark Done
if [ "$status" == "In Progress" ]; then
  backlog task edit <task-id> -s Done
fi
```

**Re-run handling**: If task already "Done", skip this step:
```
⏭️  Phase 5 Skipped: Task already marked Done
```

**Phase 5 Success**: Print summary:
```
✅ Phase 5 Complete: Task marked as Done
   Task ID: task-094
   Final Status: Done
   Implementation notes: Added
```

---

### Phase 6: Pull Request Generation

**Report progress**: Print "Phase 6: Generating pull request with human approval..."

This phase creates a well-formatted pull request using the PRGenerator pattern.

#### Step 0: Pre-PR Validation Gate (MANDATORY - NO EXCEPTIONS)

**⚠️ CRITICAL: Before creating any PR, ALL validation checks MUST pass.**

This is a blocking gate. Do NOT proceed to PR creation until ALL checks pass.

```bash
# 1. Run lint check - MUST pass with ZERO errors
uv run ruff check .

# 2. Run test suite - MUST pass with ZERO failures
uv run pytest tests/ -x -q

# 3. Check for unused imports/variables
uv run ruff check --select F401,F841 .
```

**Validation Checklist (ALL REQUIRED)**:

- [ ] `ruff check .` passes with zero errors
- [ ] `pytest tests/ -x -q` passes with zero failures
- [ ] No unused imports (`ruff check --select F401`)
- [ ] No unused variables (`ruff check --select F841`)
- [ ] Code is formatted (`ruff format .`)

**If ANY check fails**:
```
❌ Pre-PR Gate Failed: Validation checks must pass before PR creation.

Failures:
- [List failed checks]

Fix all issues and re-run /jpspec:validate
```

**⚠️ DO NOT proceed to Step 1 if ANY validation check fails.**

PRs that fail CI:
- Waste reviewer time
- Create noise in the repository
- Demonstrate lack of due diligence
- Will be closed without review

#### Step 1: Check Branch Status

```bash
# Verify current branch is pushed to remote
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null
```

**If branch not pushed**:
```
⚠️  Warning: Current branch is not pushed to remote.
Please push your branch first:
  git push -u origin $(git branch --show-current)

❌ Phase 6 Failed: Branch not pushed to remote
```

Halt and wait for user to push branch.

#### Step 2: Generate PR Title

Use conventional commit format derived from task title:
```
# Task title: "Integration - Enhanced /jpspec:validate Command"
# PR title: "feat: enhanced /jpspec:validate command"
```

**PR Type Detection**:
- If task has label "feature": `feat:`
- If task has label "fix" or "bug": `fix:`
- If task has label "docs": `docs:`
- If task has label "refactor": `refactor:`
- Default: `feat:`

#### Step 3: Generate PR Body

Create comprehensive PR body with sections:

```markdown
## Summary
Completes task: task-094

[Implementation notes from Phase 5]

## Acceptance Criteria

1. [x] Command accepts optional task-id argument; defaults to current in-progress task if not provided
2. [x] Executes phases in order: 0 (load) → 1 (test) → 2 (agents, parallel) → 3 (docs) → 4 (verify) → 5 (complete) → 6 (PR)
3. [x] Each phase reports progress to user before execution
4. [x] Phase failures halt workflow with clear error message
5. [x] Command can be re-run after fixing issues
6. [x] Updates .claude/commands/jpspec/validate.md
7. [x] Updates templates/commands/jpspec/validate.md
8. [x] Includes comprehensive help text

## Test Plan

- ✅ Unit tests: 45 passed
- ✅ Integration tests: 12 passed
- ✅ Linting: No issues
- ✅ Type checks: Passed
- ✅ Manual testing: Validated all phases execute correctly

## Validation Results

- **QA Guardian**: 15 scenarios validated, all passed
- **Security Engineer**: No critical vulnerabilities found
- **Documentation**: Command files updated and validated
```

#### Step 4: Present PR Preview

Display formatted PR preview to user:
```
================================================================================
PR PREVIEW
================================================================================

Title: feat: enhanced /jpspec:validate command

Body:
--------------------------------------------------------------------------------
[Full PR body as shown above]
--------------------------------------------------------------------------------
```

#### Step 5: Request Human Approval

**Critical**: Must get explicit approval before creating PR.

```
Create this pull request? [y/N]:
```

- If user enters `y` or `yes`: Proceed to Step 6
- If user enters anything else: Cancel PR creation

**If cancelled**:
```
❌ Phase 6 Cancelled: PR creation cancelled by user

Next steps:
- Review PR preview above
- Make any needed changes
- Re-run /jpspec:validate to try again
```

Exit gracefully without error.

#### Step 6: Create PR Using gh CLI

```bash
gh pr create --title "<pr-title>" --body "<pr-body>"
```

**Error Handling**:
- If `gh` not found: "❌ Phase 6 Failed: GitHub CLI not installed. Install from https://cli.github.com/"
- If `gh pr create` fails: Display gh error message and halt
- If PR already exists for branch: Display existing PR URL

#### Step 7: Extract PR URL

Parse PR URL from `gh` output and display to user.

**Phase 6 Success**: Print summary:
```
✅ Phase 6 Complete: Pull request created successfully

PR URL: https://github.com/owner/repo/pull/123
Task: task-094 (Done)

Workflow complete! 🎉
```

---

## Workflow Complete

After all phases complete successfully, display final summary:

```
================================================================================
VALIDATION WORKFLOW COMPLETE
================================================================================

Task: task-094 - Integration - Enhanced /jpspec:validate Command
Status: Done ✅

Phase Summary:
✅ Phase 0: Task loaded successfully
✅ Phase 1: All automated tests passed
✅ Phase 2: Agent validation passed (QA + Security)
✅ Phase 3: Documentation updated
✅ Phase 4: All acceptance criteria verified (8/8)
✅ Phase 5: Task marked Done with implementation notes
✅ Phase 6: Pull request created

Pull Request: https://github.com/owner/repo/pull/123

Next steps:
1. Wait for CI/CD pipeline to complete
2. Request code review if needed
3. Merge PR once approved and all checks pass
4. Delete feature branch after merge
================================================================================
```

---

## Error Recovery

If any phase fails, the workflow halts with a clear error message. To recover:

1. **Review the error message** - Identifies which phase failed and why
2. **Fix the issue** - Address the root cause (failing tests, unchecked ACs, etc.)
3. **Re-run the command** - Execute `/jpspec:validate <task-id>` again
4. **Resume from where it left off** - Workflow is idempotent and handles partial completion

**Example error recovery**:
```bash
# Phase 1 failed due to test failures
❌ Phase 1 Failed: 3 test(s) failed. Fix tests before continuing.

# Developer fixes tests
# Re-run validate command
/jpspec:validate task-094

# Workflow detects tests now pass and continues from Phase 2
```

---

## Help Text

**Command**: `/jpspec:validate [task-id]`

**Purpose**: Execute comprehensive validation workflow with task orchestration, automated testing, agent validation, AC verification, and PR generation.

**Arguments**:
- `task-id` (optional): Specific task ID to validate (e.g., `task-094`)
- If not provided: Automatically discovers the single "In Progress" task

**Workflow Phases**:
1. **Phase 0: Task Discovery & Load** - Find and load target task
2. **Phase 1: Automated Testing** - Run tests, linting, type checks
3. **Phase 2: Agent Validation** - Launch QA Guardian and Security Engineer (parallel)
4. **Phase 3: Documentation** - Launch Technical Writer agent
5. **Phase 4: AC Verification** - Verify all acceptance criteria met
6. **Phase 5: Task Completion** - Generate notes and mark task Done
7. **Phase 6: PR Generation** - Create pull request with human approval

**Examples**:

```bash
# Validate specific task
/jpspec:validate task-094

# Auto-discover in-progress task
/jpspec:validate
```

**Features**:
- ✅ Phased execution with progress reporting
- ✅ Phase failures halt workflow with clear error messages
- ✅ Re-runnable after fixing issues (handles partial completion)
- ✅ Automated test execution and validation
- ✅ Parallel agent execution for efficiency
- ✅ Systematic AC verification (automated + manual)
- ✅ Comprehensive implementation notes generation
- ✅ PR generation with human approval gate

**Requirements**:
- Task must be in "In Progress" status
- Tests must pass before proceeding
- All acceptance criteria must be verified
- Branch must be pushed to remote before PR creation
- GitHub CLI (`gh`) must be installed for PR creation

**Error Recovery**:
If a phase fails, fix the issue and re-run the command. The workflow will resume from where it left off.

**See Also**:
- `/jpspec:implement` - Implementation workflow
- `/jpspec:plan` - Planning workflow
- `backlog task` - Task management commands

## Post-Completion: Emit Workflow Event

After successfully completing this command (all validation phases passed, PR created), emit the workflow event:

```bash
specify hooks emit validate.completed \
  --spec-id "$FEATURE_ID" \
  --task-id "$TASK_ID" \
  -f docs/qa/$FEATURE_ID-qa-report.md \
  -f docs/security/$FEATURE_ID-security-report.md
```

Replace `$FEATURE_ID` with the feature name/identifier and `$TASK_ID` with the backlog task ID if available.

This triggers any configured hooks in `.specify/hooks/hooks.yaml` (e.g., notifications, deployment triggers).
