---
description: Execute validation and quality assurance using QA, security, documentation, and release management agents.
loop: both
# Loop Classification: BOTH LOOPS (BRIDGE)
# This command spans both inner and outer loops. It performs inner loop quality checks
# (testing, code review) while preparing artifacts for outer loop deployment (release
# management, documentation). It bridges the transition from development to deployment.
---

# /flow:validate - Enhanced Phased Validation Workflow

Execute comprehensive validation workflow with task orchestration, automated testing, agent validation, AC verification, and PR generation.

## User Input

```text
$ARGUMENTS
```

**Expected Input**: Optional task ID (e.g., `task-094`). If not provided, command discovers the current in-progress task automatically.

**For /flow:validate**: Required input state is `workflow:In Implementation`. Output state will be `workflow:Validated`.

If the task doesn't have the required workflow state, inform the user:
- If task needs implementation first: suggest running `/flow:implement`
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
- **Phase 0.5: Feature Validation Plan Extraction** - Extract and execute FVP from PRD/PRP
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
- If task ID not found: "[X] Phase 0 Failed: Task {task-id} does not exist."
- If no in-progress tasks: "[X] Phase 0 Failed: No tasks in 'In Progress' status. Please specify a task ID."
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
   Title: Integration - Enhanced /flow:validate Command
   Status: In Progress
   ACs: 0/8 complete
```

---

### Phase 0.5: Feature Validation Plan Extraction

**Report progress**: Print "Phase 0.5: Extracting Feature Validation Plan from PRD/PRP..."

This phase locates the task's PRD or PRP file and extracts the Feature Validation Plan section to get feature-specific validation commands.

#### Step 1: Locate PRD or PRP File

Search for PRD/PRP files related to the current task using this priority order:

```bash
# Extract task ID number
TASK_NUM=$(echo "$TASK_ID" | grep -oE '[0-9]+')

# Initialize SPEC_FILE variable
SPEC_FILE=""

# Priority 1: Task-specific PRP with "task-" prefix
PRP_FILE_PRIMARY="docs/prp/task-${TASK_NUM}.md"

# Priority 2: Task-specific PRP without prefix
PRP_FILE_ALT="docs/prp/${TASK_ID}.md"

# Search with priority order
if [ -f "$PRP_FILE_PRIMARY" ]; then
  SPEC_FILE="$PRP_FILE_PRIMARY"
  echo "✅ Found PRP: $SPEC_FILE"

elif [ -f "$PRP_FILE_ALT" ]; then
  SPEC_FILE="$PRP_FILE_ALT"
  echo "✅ Found PRP (alternate format): $SPEC_FILE"

else
  # Priority 3: PRD files that mention this task
  # First, search for the numeric task reference pattern (safe - TASK_NUM is digits only)
  PRD_FILE=$(find docs/prd/ -name "*.md" -type f -print0 2>/dev/null \
    | xargs -0 grep -l -E "task-${TASK_NUM}\b" 2>/dev/null \
    | head -n 1 || true)

  # If not found, search for TASK_ID as a literal string (use -F to avoid injection)
  if [ -z "$PRD_FILE" ] && [ -n "$TASK_ID" ]; then
    PRD_FILE=$(find docs/prd/ -name "*.md" -type f -print0 2>/dev/null \
      | xargs -0 grep -l -F -- "$TASK_ID" 2>/dev/null \
      | head -n 1 || true)
  fi

  if [ -n "$PRD_FILE" ]; then
    SPEC_FILE="$PRD_FILE"
    echo "✅ Found PRD referencing task: $SPEC_FILE"
  else
    echo "ℹ️ No PRP/PRD file found for ${TASK_ID}; skipping Feature Validation Plan extraction."
  fi
fi
```

**File Search Priority**:
1. Task-specific PRP: `docs/prp/task-{task-num}.md`
2. Task-specific PRP (alternate): `docs/prp/{task-id}.md`
3. PRD files mentioning the task in docs/prd/
4. No file found (skip this phase gracefully)

#### Step 2: Extract Feature Validation Plan Section

If a spec file is found (`$SPEC_FILE` is not empty), extract the "Feature Validation Plan" or "VALIDATION LOOP" section:

```bash
# Only proceed if we found a spec file
if [ -n "$SPEC_FILE" ]; then
  # Extract the Feature Validation Plan section using awk
  # Uses flag-based approach to avoid including next section header
  # Note: awk ERE supports | alternation without escaping
  FVP_SECTION=$(awk '
    /^## Feature Validation Plan/ || /^## VALIDATION LOOP/ { in_section=1; print; next }
    /^## / && in_section { exit }
    in_section { print }
  ' "$SPEC_FILE")

  if [ -z "$FVP_SECTION" ]; then
    echo "ℹ️ No Feature Validation Plan section found in: $SPEC_FILE"
  else
    echo "✅ Found Feature Validation Plan section"
  fi
fi
```

**Expected Section Structure** (from PRD or PRP):

```markdown
## Feature Validation Plan

### Commands
pytest tests/path/to/feature/ -v
ruff check src/path/to/feature/

### Expected Success
All tests pass, no linting errors

### Known Failure Modes
Test may fail if database not initialized
```

#### Step 3: Parse Validation Commands

Extract the commands from the "Commands" subsection.

> **Important**: Commands should be listed directly without code block wrappers (no triple backticks).
> The parser looks for lines starting with command names (pytest, ruff, etc.) and will NOT
> correctly extract commands wrapped in markdown code blocks.
>
> **Correct format:**
> ```
> ### Commands
> pytest tests/feature/ -v
> ruff check src/feature/
> ```
>
> **Incorrect format** (commands inside code blocks will be filtered out during parsing):
> ```
> ### Commands
> ```bash
> pytest tests/feature/ -v
> ```
> ```

```bash
# Check if FVP_SECTION was extracted before parsing
if [ -z "$FVP_SECTION" ]; then
  echo "ℹ️ Feature Validation Plan section is missing or empty; skipping command extraction."
  VALIDATION_COMMANDS=""
else
  # Extract commands from the Commands subsection
  # Looks for lines after "### Commands" until the next "###" header or section end
  # Pattern matches:
  #   - Lines starting with non-whitespace, non-hash chars (direct commands)
  #   - Indented non-comment lines with actual content (strips leading whitespace)
  # Filters out:
  #   - Code block markers via /^```([[:alnum:]_+-]+)?[[:space:]]*$/ which matches fences with optional language and trailing whitespace
  #   - Code blocks are supported but not recommended; this logic defensively skips fenced blocks
  VALIDATION_COMMANDS=$(echo "$FVP_SECTION" | awk '
    BEGIN { in_cmds=0; in_code_block=0 }
    /^### Commands/ { in_cmds=1; next }
    /^###/ && in_cmds { exit }
    /^## / && in_cmds { exit }
    in_cmds && /^```([[:alnum:]_+-]+)?[[:space:]]*$/ { in_code_block = !in_code_block; next }  # Toggle on fence lines (``` with optional language and whitespace)
    in_cmds && in_code_block { next }  # Skip all lines inside fenced code blocks
    in_cmds && /^[^#[:space:]]/ { print }
    in_cmds && /^[[:space:]]+[^#[:space:]]/ { gsub(/^[[:space:]]+/, ""); if (NF > 0) print }
  ')

  if [ -z "$VALIDATION_COMMANDS" ]; then
    echo "ℹ️ No validation commands found in Feature Validation Plan"
  fi
fi
```

Store the extracted commands for immediate execution in Phase 0.5 (Feature Validation Plan execution before Phase 1).

#### Step 4: Display Validation Commands to User

Present the feature-specific validation commands to the user:

```
📋 Feature Validation Plan found in: docs/prp/task-094.md

Validation Commands:
--------------------------------------------------------------------------------
pytest tests/flowspec_cli/test_validate_command.py -v
pytest tests/integration/test_validate_workflow.py -v
ruff check src/flowspec_cli/commands/validate.py
flowspec validate --help
--------------------------------------------------------------------------------

Do you want to:
1. Run these commands automatically (with safety validation)
2. Print commands for manual execution
3. Skip and use default test suite

Choice [1/2/3]:
```

#### Step 5: Execute or Print Commands

Based on user choice:

**Option 1: Run automatically (with safety validation)**

> **Security requirement**: Commands from PRD/PRP markdown files must be validated before execution.

```bash
# Allowlist of safe command patterns (customize per project)
# Patterns are anchored at both start and end for security
# Note: ( .*)? allows optional space and arguments (tolerant of trailing whitespace)
# Security assumption: npm run/test assumes package.json scripts are trusted.
#   The allowlist validates command format but not the script content itself.
SAFE_PATTERNS=(
  "^pytest( .*)?$"
  "^ruff( .*)?$"
  "^mypy( .*)?$"
  "^flowspec( .*)?$"
  "^npm test( .*)?$"
  "^npm run (@[a-z0-9_-]+/)?[A-Za-z_][A-Za-z0-9:._-]*( .*)?$"
  "^cargo test( .*)?$"
  "^go test( .*)?$"
)

# Dangerous shell metacharacters that should not appear in commands
# These could allow command injection even if prefix matches
# Includes: semicolon, pipe, ampersand, dollar, backtick, backslash,
#           parentheses, braces, angle brackets, quotes, whitespace controls
# Note: '$' is intentionally included to block variable expansion. This also
#       blocks otherwise-safe commands containing literal $ (e.g., grep patterns).
# Note: In ANSI-C quoting ($'...'), '\\\\' represents two backslashes in the
#       string literal, which the regex engine interprets as a single escaped
#       backslash matching a literal '\' character.
# Note: Single and double quotes are blocked to prevent shell interpretation attacks
#       when commands are executed via bash -c.
#
# Design trade-off: Security over flexibility. Blocking these characters prevents
# command injection but also blocks some legitimate use cases. Workarounds:
#   - Backslash in test filters (pytest -k "test\d+"): Use pytest markers or
#     literal character classes like [0-9] instead of \d
#   - Dollar sign in grep patterns: Run grep manually or use Option 2 (print commands)
#   - Quoted arguments (pytest -k "name"): Run manually or use Option 2
#   - Commands with shell features: Use Option 2 to print and run manually
DANGEROUS_CHARS=$'[;|&$`\\\\(){}\'\"<>\t\n\r\v\f]'

# Validate each command against allowlist
validate_command() {
  local cmd="$1"

  # First check for dangerous shell metacharacters
  if [[ "$cmd" =~ $DANGEROUS_CHARS ]]; then
    echo "⚠️ Security: Command contains shell metacharacters: $cmd"
    return 1  # Reject commands with potentially dangerous chars
  fi

  # Check for path traversal attempts (e.g., pytest ../../etc/passwd)
  # Pattern requires "/" or boundary adjacent to ".." to catch actual path traversal:
  #   - Matches: /../, /.. at end or before space, ../ at start or after space
  #   - Does NOT match: test..py, 1..10, file...name (consecutive dots without /)
  # Limitation: Does not catch URL-encoded (%2e%2e) or UTF-8 encoded traversal.
  #   Such attacks are mitigated by the allowlist and DANGEROUS_CHARS checks.
  if [[ "$cmd" =~ (^|[[:space:]])\.\.(/|[[:space:]]|$) || "$cmd" =~ /\.\.(/|[[:space:]]|$) ]]; then
    echo "⚠️ Security: Command contains path traversal (..): $cmd"
    return 1  # Reject commands with path traversal
  fi

  # Then check against allowlist patterns
  for pattern in "${SAFE_PATTERNS[@]}"; do
    if [[ "$cmd" =~ $pattern ]]; then
      return 0  # Safe
    fi
  done
  return 1  # Not in allowlist
}

# Process commands with validation
# Use here-string (<<<) instead of pipe to avoid subshell variable scope issues.
# This allows overall_status to be modified inside the loop and checked after.
overall_status=0
while IFS= read -r cmd; do
  if [ -n "$cmd" ]; then
    if validate_command "$cmd"; then
      echo "✅ Validated: $cmd"
      # Execute the validated command via bash -c for proper argument handling.
      # Safety relies on validate_command/DANGEROUS_CHARS blocking injection.
      #
      # Limitation: File paths with spaces are not supported because quotes are
      # rejected by the security validation (DANGEROUS_CHARS). Commands with paths
      # that contain spaces will fail validation, even if quoted.
      # Best practice: Avoid spaces in test file paths entirely (e.g., rename files).
      bash -c "$cmd"
      exit_code=$?
      if [ "$exit_code" -eq 0 ]; then
        echo "✅ Command succeeded: $cmd"
      else
        echo "❌ Command failed with exit code $exit_code: $cmd"
        overall_status=1
      fi
    else
      # Security-first: Unknown commands fail the workflow rather than being silently skipped.
      # This ensures all FVP commands are explicitly validated before execution.
      # To fix: Add the command pattern to SAFE_PATTERNS, or use Option 2 (manual).
      echo "⚠️ Command not in allowlist, rejecting: $cmd"
      echo "   Add to SAFE_PATTERNS if this is a legitimate test command"
      overall_status=1
    fi
  fi
done <<< "$VALIDATION_COMMANDS"

# Check overall status and halt if any command failed or was rejected
if [ "$overall_status" -ne 0 ]; then
  echo "❌ One or more validation commands failed or were rejected. Halting before Phase 1."
  exit 1
fi
```

- Validate commands against allowlist before execution
- Execute each validated command sequentially
- Capture output and exit codes
- Report success/failure for each command
- Continue to Phase 1 only if all commands pass

**Option 2: Print for manual execution**
- Display commands with copy-paste friendly format
- Print "Expected Success" criteria if available
- Print "Known Failure Modes" if available
- Pause and wait for user confirmation before Phase 1

**Option 3: Skip**
- Proceed directly to Phase 1 with standard test suite

#### Step 6: Store Validation Results

If commands were run automatically, store results for Phase 5 task notes:

```bash
# Store validation results in temporary file or variable
VALIDATION_RESULTS="Feature Validation Plan Results:
Command 1: pytest tests/feature/ -v → PASSED (15 tests)
Command 2: ruff check src/feature/ → PASSED (0 errors)
Command 3: Custom validation → PASSED
"
```

These results will be included in implementation notes during Phase 5.

**Error Handling**:
- If PRD/PRP file not found: Print info message and skip to Phase 1
  ```
  ℹ️ Phase 0.5 Skipped: No PRD/PRP file found for task-094
     Continuing with standard test suite...
  ```
- If Feature Validation Plan section not found: Skip to Phase 1
  ```
  ℹ️ Phase 0.5 Skipped: No Feature Validation Plan in PRD/PRP
     Continuing with standard test suite...
  ```
- If any validation command fails: Halt workflow
  ```
  [X] Phase 0.5 Failed: Validation command failed
  Command: pytest tests/feature/ -v
  Exit Code: 1
  Output: [test output]

  Workflow halted. Fix the failing tests and re-run /flow:validate
  ```

**Phase 0.5 Success**: Print summary:
```
✅ Phase 0.5 Complete: Feature validation commands executed
   Source: docs/prp/task-094.md
   Commands run: 3
   All validations: PASSED
```

**Re-run handling**: If feature validation already passed in previous run, skip and print:
```
⏭️  Phase 0.5 Skipped: Feature validation already completed
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
pytest tests/ -v --cov=src/flowspec_cli --cov-report=term-missing

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
- If tests fail: "[X] Phase 1 Failed: {N} test(s) failed. Fix tests before continuing."
- If linting fails: "⚠️  Phase 1 Warning: Linting issues detected. Review before continuing."
- If type checks fail: "[X] Phase 1 Failed: Type check errors found."

#### Step 4: Document Skipped Tests

**IMPORTANT**: If any tests are skipped, document them for the PR body.

```bash
# Capture skipped tests with reasons
pytest tests/ -v 2>&1 | grep -E "SKIPPED" > /tmp/skipped_tests.txt
```

For each skipped test, categorize and document the reason:
- **Benchmark tests**: Require full dataset or extended runtime
- **Performance tests**: Require specific environment or resources
- **Integration tests**: Require external services (databases, APIs, web servers)
- **E2E tests**: Require full environment setup
- **Platform-specific tests**: Require specific OS or architecture
- **Flaky tests**: Known intermittent failures (should reference issue if exists)

Store this information for Phase 6 PR generation.

**Phase 1 Success**: Print test summary:
```
✅ Phase 1 Complete: All automated checks passed
   Tests: 45 passed, 17 skipped
   Coverage: 87%
   Linting: No issues
   Type checks: Passed
   Skipped tests: Documented for PR
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

Each validator agent context below includes `{{BACKLOG_INSTRUCTIONS}}` which must be replaced with the content from `.claude/partials/flow/_backlog-instructions.md`. This ensures all agents have consistent backlog task management instructions.

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
3. **Three-Layer Critique**: Acknowledge value -> Identify risk -> Suggest mitigation
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
- If any AC unchecked: "[X] Phase 4 Failed: {N} acceptance criteria not yet verified. Cannot proceed to completion."
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
- How it was tested (from Phase 0.5 FVP + Phase 1 test results)
- Key decisions made (from agent reports)
- Validation results (from Phases 2-3)

**Example implementation notes format**:
```markdown
## Implementation Summary (2025-12-01 15:30:00)

### What Was Implemented
Enhanced the /flow:validate command with phased orchestration workflow.
Implemented 8 distinct phases (Phase 0 through Phase 6, including Phase 0.5) with progress reporting and error handling.

### Feature Validation Plan Results
[Include results from Phase 0.5 if Feature Validation Plan was found and executed]

Source: docs/prp/task-094.md

Commands executed:
- pytest tests/flowspec_cli/test_validate_command.py -v → PASSED (15 tests)
- ruff check src/flowspec_cli/commands/validate.py → PASSED (0 errors)
- flowspec validate --help → PASSED (help text verified)

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

**Important**: If Phase 0.5 extracted and ran Feature Validation Plan commands, include those results in the "Feature Validation Plan Results" section. This provides traceable evidence that feature-specific validations were performed.

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
# CI Pre-flight Validation (RIGOR: VALID-007)
echo "Running CI pre-flight validation..."
echo ""

# 1. Format check - MUST pass with ZERO errors
echo "1. Format check..."
uv run ruff format --check .
FORMAT_STATUS=$?
if [ $FORMAT_STATUS -ne 0 ]; then
  echo "[X] Format check failed"
  echo "Fix: uv run ruff format ."
else
  echo "[Y] Format check passed"
fi

# 2. Lint check - MUST pass with ZERO errors
echo ""
echo "2. Lint check..."
uv run ruff check .
LINT_STATUS=$?
if [ $LINT_STATUS -ne 0 ]; then
  echo "[X] Lint check failed"
  echo "Fix: uv run ruff check --fix ."
else
  echo "[Y] Lint check passed"
fi

# 3. Test suite - MUST pass with ZERO failures
echo ""
echo "3. Test suite..."
uv run pytest tests/ -x -q
TEST_STATUS=$?
if [ $TEST_STATUS -ne 0 ]; then
  echo "[X] Tests failed"
  echo "Fix: uv run pytest tests/ -v (see detailed output)"
else
  echo "[Y] Tests passed"
fi

# 4. Unused imports/variables check
echo ""
echo "4. Unused imports/variables..."
uv run ruff check --select F401,F841 .
UNUSED_STATUS=$?
if [ $UNUSED_STATUS -ne 0 ]; then
  echo "[X] Unused imports/variables detected"
  echo "Fix: uv run ruff check --select F401,F841 --fix ."
else
  echo "[Y] No unused imports/variables"
fi

# 5. Type check (if mypy configured)
echo ""
echo "5. Type check..."
if [ -f "pyproject.toml" ] && grep -q "mypy" pyproject.toml 2>/dev/null; then
  uv run mypy src/ 2>/dev/null
  TYPE_STATUS=$?
  if [ $TYPE_STATUS -ne 0 ]; then
    echo "[X] Type check failed"
    echo "Fix: Review mypy errors and add type hints"
  else
    echo "[Y] Type check passed"
  fi
else
  echo "⏭️  Type check skipped (mypy not configured)"
  TYPE_STATUS=0
fi

# Evaluate overall status
echo ""
if [ $FORMAT_STATUS -ne 0 ] || [ $LINT_STATUS -ne 0 ] || [ $TEST_STATUS -ne 0 ] || [ $UNUSED_STATUS -ne 0 ] || [ $TYPE_STATUS -ne 0 ]; then
  echo "[X] Pre-PR Gate Failed: CI checks must pass before PR creation"
  echo ""
  echo "Failed checks:"
  [ $FORMAT_STATUS -ne 0 ] && echo "  - Format check"
  [ $LINT_STATUS -ne 0 ] && echo "  - Lint check"
  [ $TEST_STATUS -ne 0 ] && echo "  - Test suite"
  [ $UNUSED_STATUS -ne 0 ] && echo "  - Unused imports/variables"
  [ $TYPE_STATUS -ne 0 ] && echo "  - Type check"
  echo ""
  echo "Fix all issues and re-run /flow:validate"
  exit 1
fi

echo "[Y] All CI checks passed"
```

**Validation Checklist (ALL REQUIRED)**:

- [ ] `ruff format --check .` passes with zero errors
- [ ] `ruff check .` passes with zero errors
- [ ] `pytest tests/ -x -q` passes with zero failures
- [ ] No unused imports (`ruff check --select F401`)
- [ ] No unused variables (`ruff check --select F841`)
- [ ] Type check passes (if mypy configured)

**If ANY check fails**:
```
[X] Pre-PR Gate Failed: Validation checks must pass before PR creation.

Failures:
- [List failed checks]

Fix all issues and re-run /flow:validate
```

**⚠️ DO NOT proceed to Step 0.5 if ANY validation check fails.**

PRs that fail CI:
- Waste reviewer time
- Create noise in the repository
- Demonstrate lack of due diligence
- Will be closed without review

#### Step 0.5: Rebase Enforcement (RIGOR: VALID-004)

**MANDATORY**: Branch MUST be rebased from main with zero commits behind before PR creation.

```bash
# Check if branch is behind main
git fetch origin main 2>/dev/null
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")

# Validate BEHIND is numeric before comparison (POSIX-compliant)
if ! echo "$BEHIND" | grep -Eq '^[0-9]+$'; then
  echo "[!] Warning: Could not determine commits behind main (origin/main may not exist)"
  BEHIND=0
fi

if [ "$BEHIND" -gt 0 ]; then
  echo "[X] RIGOR VIOLATION (VALID-004): Branch is $BEHIND commits behind main"
  echo "Fix: git fetch origin main && git rebase origin/main"
  echo ""
  echo "After rebasing:"
  echo "  1. Resolve any conflicts"
  echo "  2. Run tests: uv run pytest tests/ -x"
  echo "  3. Push: git push --force-with-lease origin \$(git branch --show-current)"
  exit 1
fi

echo "[Y] Branch is up-to-date with main (zero commits behind)"
```

**This is BLOCKING** - do not proceed to Step 1 if branch is behind main.

#### Step 0.6: DCO Sign-off Verification (RIGOR: PR-001)

**MANDATORY**: All commits MUST have DCO (Developer Certificate of Origin) sign-off.

```bash
# Check all commits in branch for DCO sign-off
echo "Checking DCO sign-off for all commits..."

# POSIX-compliant iteration over commit hashes (avoids bash-specific process substitution)
UNSIGNED_COMMITS=""
for hash in $(git log origin/main..HEAD --format='%h' 2>/dev/null); do
  # Check for Signed-off-by anywhere in commit body
  if ! git log -1 --format='%B' "$hash" 2>/dev/null | grep -q "Signed-off-by:"; then
    MSG=$(git log -1 --format='%s' "$hash" 2>/dev/null)
    UNSIGNED_COMMITS="$UNSIGNED_COMMITS
$hash $MSG"
  fi
done

# Count unsigned commits (count non-empty lines)
if [ -n "$UNSIGNED_COMMITS" ]; then
  UNSIGNED_COUNT=$(printf '%s\n' "$UNSIGNED_COMMITS" | grep -c .)
  echo "[X] RIGOR VIOLATION (PR-001): $UNSIGNED_COUNT commits missing DCO sign-off"
  echo ""
  echo "Unsigned commits:"
  printf '%s\n' "$UNSIGNED_COMMITS" | while read -r line; do
    [ -n "$line" ] && echo "  $line"
  done
  echo ""
  echo "Fix: Add sign-off to all commits:"
  echo "  git rebase origin/main --exec 'git commit --amend --no-edit -s'"
  echo "  git push --force-with-lease origin \$(git branch --show-current)"
  exit 1
fi

echo "[Y] All commits have DCO sign-off"
```

**DCO Certification**: By signing off, you certify that you wrote the code or otherwise have the right to submit it under the project's license.

**This is BLOCKING** - do not proceed to Step 1 if any commits lack DCO sign-off.

#### Step 1: Check Branch Status and Merge Conflicts

```bash
# Verify current branch is pushed to remote
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null

# Check for merge conflicts with main/master
git fetch origin main
git merge-tree $(git merge-base HEAD origin/main) HEAD origin/main | grep -q "^<<<<<<<" && echo "CONFLICTS"
```

**If branch not pushed**:
```
⚠️  Warning: Current branch is not pushed to remote.
Please push your branch first:
  git push -u origin "$(git branch --show-current)"

[X] Phase 6 Failed: Branch not pushed to remote
```

**If merge conflicts exist** (MANDATORY - NO EXCEPTIONS):
```
[X] Phase 6 Failed: Merge conflicts detected with main branch.

You MUST resolve conflicts before creating a PR:
  git fetch origin main
  git rebase origin/main
  # Resolve any conflicts
  git push --force-with-lease

DO NOT submit PRs with merge conflicts.
```

Halt and wait for user to resolve conflicts and rebase.

#### Step 2: Generate PR Title

Use conventional commit format derived from task title:
```
# Task title: "Integration - Enhanced /flow:validate Command"
# PR title: "feat: enhanced /flow:validate command"
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
2. [x] Executes phases in order: 0 (load) -> 1 (test) -> 2 (agents, parallel) -> 3 (docs) -> 4 (verify) -> 5 (complete) -> 6 (PR)
3. [x] Each phase reports progress to user before execution
4. [x] Phase failures halt workflow with clear error message
5. [x] Command can be re-run after fixing issues
6. [x] Updates .claude/commands/flow/validate.md
7. [x] Updates templates/commands/flowspec/validate.md
8. [x] Includes comprehensive help text

## Test Plan

- ✅ Unit tests: 45 passed
- ✅ Integration tests: 12 passed
- ✅ Linting: No issues
- ✅ Type checks: Passed
- ✅ Manual testing: Validated all phases execute correctly

## Skipped Tests

**REQUIRED**: If any tests were skipped during validation, document them here with explanations.

<details>
<summary>N skipped tests - click to expand</summary>

**[Category] tests** (reason):
- `test_file.py::TestClass::test_name` - [specific reason]

</details>

**Note**: All skipped tests are pre-existing and unrelated to this PR. [Or explain if any are related]

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

Title: feat: enhanced /flow:validate command

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
[X] Phase 6 Cancelled: PR creation cancelled by user

Next steps:
- Review PR preview above
- Make any needed changes
- Re-run /flow:validate to try again
```

Exit gracefully without error.

#### Step 6: Create PR Using gh CLI

```bash
gh pr create --title "<pr-title>" --body "<pr-body>"
```

**Error Handling**:
- If `gh` not found: "[X] Phase 6 Failed: GitHub CLI not installed. Install from https://cli.github.com/"
- If `gh pr create` fails: Display gh error message and halt
- If PR already exists for branch: Display existing PR URL

#### Step 7: Extract PR URL

Parse PR URL from `gh` output and display to user.

**Phase 6 Success**: Print summary:
```
✅ Phase 6 Complete: Pull request created successfully

PR URL: https://github.com/owner/repo/pull/123
Task: task-094 (Done)

Next: Monitor for Copilot review comments (see Phase 6.5 for iteration guidance)
```

---

### Phase 6.5: Copilot Comment Resolution (Post-PR Iteration)

**Report progress**: Print "Phase 6.5: Monitoring for Copilot review comments..."

**IMPORTANT**: This phase is executed AFTER PR creation when GitHub Copilot provides review comments.

#### When to Execute Phase 6.5

Execute this phase when:
- PR has been created successfully
- GitHub Copilot has posted review comments on the PR
- Comments suggest code improvements, security issues, or best practice violations

#### Step 1: Review Copilot Comments

```bash
# View Copilot comments on the PR
gh pr view <pr-number> --comments

# Or view in browser
gh pr view <pr-number> --web
```

**Evaluation criteria**:
- Is the suggestion valid and improves code quality?
- Does it address a real issue (security, performance, maintainability)?
- Is it aligned with project coding standards?

#### Step 2: Decide on Action

**If ALL Copilot comments are invalid/not applicable**:
- Add a comment explaining why suggestions are not being applied
- Proceed to request human review
- No iteration needed

**If ANY Copilot comments are valid**:
- Proceed to Step 3 to create iteration branch

#### Step 3: Create Iteration Branch

**RIGOR: PR-003 - Version Iteration Naming**

```bash
# Determine current iteration version
CURRENT_BRANCH=$(git branch --show-current)

# Calculate next version using portable extraction (works in bash 3.2+)
# Extract version number using sed for better portability
# Use [0-9][0-9]* to require at least one digit (not [0-9]* which matches zero)
VERSION=$(printf '%s\n' "$CURRENT_BRANCH" | sed -n 's/.*-v\([0-9][0-9]*\)$/\1/p')

if [ -n "$VERSION" ]; then
  # Already an iteration branch (e.g., hostname/task-123/feature-v2)
  NEXT_VERSION=$((VERSION + 1))
  BASE_BRANCH=$(printf '%s\n' "$CURRENT_BRANCH" | sed 's/-v[0-9][0-9]*$//')
  ITERATION_BRANCH="${BASE_BRANCH}-v${NEXT_VERSION}"
else
  # First iteration (e.g., hostname/task-123/feature -> hostname/task-123/feature-v2)
  ITERATION_BRANCH="${CURRENT_BRANCH}-v2"
fi

# Create iteration branch
git checkout -b "$ITERATION_BRANCH"
echo "Created iteration branch: $ITERATION_BRANCH"
```

**Branch naming pattern**:
- Original: `hostname/task-NNN/feature-slug`
- First iteration: `hostname/task-NNN/feature-slug-v2`
- Second iteration: `hostname/task-NNN/feature-slug-v3`
- Nth iteration: `hostname/task-NNN/feature-slug-v{N+1}`

#### Step 4: Apply Fixes

Address each valid Copilot comment:

1. **Make code changes** to resolve the issue
2. **Add tests** if new logic introduced
3. **Update documentation** if behavior changed
4. **Verify locally** with CI pre-flight checks:

```bash
# Run full validation suite (all commands must pass)
if uv run ruff format . && uv run ruff check --fix . && uv run pytest tests/ -x -q; then
  echo "[Y] Fixes validated locally"
else
  echo "[X] Fixes introduced new issues - resolve before pushing"
fi
```

#### Step 5: Commit and Push Iteration

```bash
# Stage all changes
git add .

# Commit with DCO sign-off
git commit -s -m "fix: address Copilot feedback from PR #<old-pr-number>

- Fix 1: Description
- Fix 2: Description
- Fix 3: Description

Resolves Copilot comments: <comment-links>"

# Push iteration branch
git push -u origin "$ITERATION_BRANCH"
```

#### Step 6: Create New PR and Close Old PR

**RIGOR: PR-002 - Copilot Comments Resolution**

```bash
# Get old PR number
OLD_PR=$(gh pr view --json number -q '.number' 2>/dev/null)

# Create new PR with iteration branch
gh pr create \
  --title "feat: <feature-description> (v2)" \
  --body "$(cat <<'EOF'
## Summary
Supersedes PR #<old-pr-number> with Copilot feedback addressed.

## Changes from Previous PR
- Addressed Copilot comment: <summary of fix 1>
- Addressed Copilot comment: <summary of fix 2>
- Addressed Copilot comment: <summary of fix 3>

## Previous PR
See #<old-pr-number> for original context and acceptance criteria.

## Test Plan
- ✅ All tests passing
- ✅ Copilot suggestions implemented
- ✅ CI pre-flight checks passed

<Include full test plan from original PR>
EOF
)"

# Close old PR with reference to new one
NEW_PR=$(gh pr view --json number -q '.number' 2>/dev/null)
gh pr close "$OLD_PR" --comment "Superseded by PR #${NEW_PR} with Copilot feedback addressed"

echo "Old PR #${OLD_PR} closed, new PR #${NEW_PR} created"
```

#### Step 7: Iterate Until Zero Copilot Comments

**Repeat Phase 6.5 until**:
- Zero unresolved Copilot comments remain, OR
- All remaining comments are documented as "will not fix" with rationale

**Maximum iterations**: If exceeding 5 iterations, escalate to human review to discuss whether Copilot suggestions are appropriate.

#### Phase 6.5 Success

```
✅ Phase 6.5 Complete: Copilot feedback addressed

Iteration: v3
PR URL: https://github.com/owner/repo/pull/125
Previous PRs: #123 (v1, closed), #124 (v2, closed)
Unresolved Copilot comments: 0

Ready for human review!
```

---

## Workflow Complete

After all phases complete successfully, display final summary:

```
================================================================================
VALIDATION WORKFLOW COMPLETE
================================================================================

Task: task-094 - Integration - Enhanced /flow:validate Command
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
5. Task is complete (status: Done)
================================================================================
```

---

## Error Recovery

If any phase fails, the workflow halts with a clear error message. To recover:

1. **Review the error message** - Identifies which phase failed and why
2. **Fix the issue** - Address the root cause (failing tests, unchecked ACs, etc.)
3. **Re-run the command** - Execute `/flow:validate <task-id>` again
4. **Resume from where it left off** - Workflow is idempotent and handles partial completion

**Example error recovery**:
```bash
# Phase 1 failed due to test failures
[X] Phase 1 Failed: 3 test(s) failed. Fix tests before continuing.

# Developer fixes tests
# Re-run validate command
/flow:validate task-094

# Workflow detects tests now pass and continues from Phase 2
```

---

## Help Text

**Command**: `/flow:validate [task-id]`

**Purpose**: Execute comprehensive validation workflow with task orchestration, automated testing, agent validation, AC verification, and PR generation.

**Arguments**:
- `task-id` (optional): Specific task ID to validate (e.g., `task-094`)
- If not provided: Automatically discovers the single "In Progress" task

**Workflow Phases**:
1. **Phase 0: Task Discovery & Load** - Find and load target task
2. **Phase 0.5: Feature Validation Plan Extraction** - Extract and execute feature-specific validation from PRD/PRP
3. **Phase 1: Automated Testing** - Run tests, linting, type checks
4. **Phase 2: Agent Validation** - Launch QA Guardian and Security Engineer (parallel)
5. **Phase 3: Documentation** - Launch Technical Writer agent
6. **Phase 4: AC Verification** - Verify all acceptance criteria met
7. **Phase 5: Task Completion** - Generate notes and mark task Done
8. **Phase 6: PR Generation** - Create pull request with human approval

**Examples**:

```bash
# Validate specific task
/flow:validate task-094

# Auto-discover in-progress task
/flow:validate
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
- **No merge conflicts with main branch** (rebase and resolve before PR creation)
- GitHub CLI (`gh`) must be installed for PR creation
- **Skipped tests must be documented in PR body with explanations** (category and reason for each)

**Error Recovery**:
If a phase fails, fix the issue and re-run the command. The workflow will resume from where it left off.

**See Also**:
- `/flow:implement` - Implementation workflow
- `/flow:plan` - Planning workflow
- `backlog task` - Task management commands

## Post-Completion: Emit Workflow Event

After successfully completing this command (all validation phases passed, PR created), emit the workflow event:

```bash
flowspec hooks emit validate.completed \
  --spec-id "$FEATURE_ID" \
  --task-id "$TASK_ID" \
  -f docs/qa/$FEATURE_ID-qa-report.md \
  -f docs/security/$FEATURE_ID-security-report.md
```

Replace `$FEATURE_ID` with the feature name/identifier and `$TASK_ID` with the backlog task ID if available.

This triggers any configured hooks in `.flowspec/hooks/hooks.yaml` (e.g., notifications, deployment triggers).

## Telemetry: Track Agent Invocations

After validation completes, track the agents that were invoked for analytics (if telemetry is enabled):

```bash
# Track each agent that was invoked during this command (silently, will be no-op if disabled)

# Track the command execution with user's role
flowspec telemetry track-role "$CURRENT_ROLE" --command /flow:validate -q

# QA Guardian agent was invoked in Phase 2:
flowspec telemetry track-agent quality-guardian --command /flow:validate -q

# Security Engineer agent was invoked in Phase 2:
flowspec telemetry track-agent secure-by-design-engineer --command /flow:validate -q

# Technical Writer agent was invoked in Phase 3:
flowspec telemetry track-agent technical-writer --command /flow:validate -q
```

Replace `$CURRENT_ROLE` with the user's current role (dev, pm, qa, etc.).

This enables workflow analytics for understanding agent usage patterns. The tracking is:
- **Opt-in only**: Only recorded if user has enabled telemetry via `flowspec telemetry enable`
- **Privacy-first**: Project names are hashed, no PII collected
- **Fail-safe**: Commands will not fail if telemetry is unavailable
