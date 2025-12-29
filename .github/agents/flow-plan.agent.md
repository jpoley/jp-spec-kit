---
name: "flow-plan"
description: "Execute planning workflow using project architect and platform engineer agents (builds out /spec.constitution)."
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
  - label: "Begin Implementation"
    agent: "flow-implement"
    prompt: "Planning is complete. Begin implementing the feature according to the technical design."
    send: false
---
## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Light Mode Detection

Check if this project is in light mode:

```bash
# Check for light mode marker
if [ -f ".flowspec-light-mode" ]; then
  echo "LIGHT MODE DETECTED - Using streamlined planning"
else
  echo "FULL MODE - Using complete planning"
fi
```

**If `.flowspec-light-mode` exists**, use light mode planning:

| Aspect | Full Mode | Light Mode |
|--------|-----------|------------|
| Output template | `plan.md` (detailed) | `plan-light.md` (high-level) |
| Data models | Detailed ERD/schemas | Brief mention only |
| API contracts | Full OpenAPI spec | Endpoint list only |
| ADRs | Full ADR format | Decision summary |
| Agents | Both Architect + Platform | Architect only (simplified) |

Continue with the workflow below, but:
- Use `templates/plan-light-template.md` as the output format
- Skip detailed data modeling and API contract generation
- Focus on high-level approach, key components, and risks

## Execution Instructions

This command creates comprehensive architectural and platform planning using two specialized agents working in parallel, building out /spec.constitution.

# Constitution Pre-flight Check

**CRITICAL**: This command requires constitution validation before execution (unless `--skip-validation` is provided).

## Step 0.5: Check Constitution Status

Before executing this workflow command, validate the project's constitution:

### 1. Check Constitution Exists

```bash
# Look for constitution file
if [ -f "memory/constitution.md" ]; then
  echo "[Y] Constitution found"
else
  echo "⚠️ No constitution found"
  echo ""
  echo "To create one:"
  echo "  1. Run: flowspec init --here"
  echo "  2. Then: Run /spec:constitution to customize"
  echo ""
  echo "Proceeding without constitution..."
fi
```

If no constitution exists:
- Warn the user
- Suggest creating one with `flowspec init --here`
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

Consider running /spec:constitution to customize your constitution.

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
  2. Run /spec:constitution to customize
  3. Run flowspec constitution validate to check status

Continue without validation? [y/N]: _
```

Wait for user response:
- If user responds `y` or `yes` -> Continue with command
- If user responds `n`, `no`, or empty/Enter -> Stop and show:
  ```text
  Command cancelled. Run /spec:constitution to customize your constitution.
  ```

#### Heavy Tier - Block Until Validated

If `TIER = Heavy` and `MARKER_COUNT > 0`:

```text
[X] Constitution Validation Required

Your constitution has N unvalidated sections:
$SECTIONS

Heavy tier constitutions require full validation before workflow commands.

To resolve:
  1. Run /spec:constitution to customize your constitution
  2. Run flowspec constitution validate to verify
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
[Y] Constitution validated
```

Continue with command normally.

## Summary: When to Block vs Warn

| Tier | Unvalidated Sections | Action |
|------|---------------------|--------|
| Light | 0 | [Y] Continue |
| Light | >0 | ⚠️ Warn, continue |
| Medium | 0 | [Y] Continue |
| Medium | >0 | ⚠️ Warn, ask confirmation, respect user choice |
| Heavy | 0 | [Y] Continue |
| Heavy | >0 | [X] Block, require validation |
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

{{INCLUDE:.claude/partials/flow/_constitution-check.md}}

{{INCLUDE:.claude/partials/flow/_workflow-state.md}}

## Execution Instructions

[Rest of your command implementation...]
```

## Related Commands

| Command | Purpose |
|---------|---------|
| `flowspec init --here` | Initialize constitution if missing |
| `/spec:constitution` | Interactive constitution customization |
| `flowspec constitution validate` | Check validation status and show report |
| `flowspec constitution show` | Display current constitution |


# Workflow State Validation

## Step 0: Workflow State Validation (REQUIRED)

**CRITICAL**: This command requires a task to be in the correct workflow state before execution.

### Light Mode Detection

First, check if this project is in light mode:

```bash
# Check for light mode marker
if [ -f ".flowspec-light-mode" ]; then
  echo "Project is in LIGHT MODE (~60% faster workflow)"
fi
```

**Light Mode Behavior**:
- `/flow:research` -> **SKIPPED** (inform user and suggest `/flow:plan` instead)
- `/flow:plan` -> Uses `plan-light.md` template (high-level only)
- `/flow:specify` -> Uses `spec-light.md` template (combined stories + AC)

If in light mode and the current command is `/flow:research`, inform the user:
```text
ℹ️ This project is in Light Mode

Light mode skips the research phase for faster iteration.
Current state: workflow:Specified

Suggestions:
  - Run /flow:plan to proceed directly to planning
  - To enable research, delete .flowspec-light-mode and use full mode
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
| /flow:assess | workflow:To Do, (no workflow label) | workflow:Assessed |
| /flow:specify | workflow:Assessed | workflow:Specified |
| /flow:research | workflow:Specified | workflow:Researched |
| /flow:plan | workflow:Specified, workflow:Researched | workflow:Planned |
| /flow:implement | workflow:Planned | workflow:In Implementation |
| /flow:validate | workflow:In Implementation | workflow:Validated |
| /flow:operate | workflow:Validated | workflow:Deployed |

### 3. Handle Invalid State

If the task's workflow state doesn't match the required input states:

```text
⚠️ Cannot run /flow:<command>

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

- `workflow:Assessed` - SDD suitability evaluated (/flow:assess complete)
- `workflow:Specified` - Requirements captured (/flow:specify complete)
- `workflow:Researched` - Technical research completed (/flow:research complete)
- `workflow:Planned` - Architecture planned (/flow:plan complete)
- `workflow:In Implementation` - Code being written (/flow:implement in progress)
- `workflow:Validated` - QA and security validated (/flow:validate complete)
- `workflow:Deployed` - Released to production (/flow:operate complete)

## Programmatic State Checking

The state guard module can also be used programmatically:

```python
from flowspec_cli.workflow import check_workflow_state, get_valid_workflows

# Check if current state allows command execution
can_proceed, message = check_workflow_state("implement", current_state)

if not can_proceed:
    print(message)
    # Shows error with suggestions

# Get valid commands for a state
valid_commands = get_valid_workflows("Specified")
# Returns: ['/flow:research', '/flow:plan']
```

## Bypassing State Checks (Power Users Only)

State checks can be bypassed in special circumstances:
- Emergency hotfixes
- Iterative refinement of specifications
- Recovery from failed workflows

Use `--skip-state-check` flag or explicitly acknowledge the bypass.

**Warning**: Bypassing state checks may result in incomplete artifacts or broken workflows.


**For /flow:plan**: Required input states are `workflow:Specified` OR `workflow:Researched`. Output state will be `workflow:Planned`.

If the task doesn't have the required workflow state, inform the user:
- If task needs specification first: suggest running `/flow:specify`
- If research was skipped intentionally: `workflow:Specified` is still valid for planning

**Proceed to Step 1 ONLY if workflow validation passes.**

### Extended Thinking Mode

> **🧠 Think Hard**: Architecture and platform decisions require deep analysis. Apply extended thinking to:
> - Technology tradeoffs and long-term implications
> - Scalability, maintainability, and security considerations
> - Integration complexity and dependency management
> - Alternative approaches and their consequences

### Step 1: Backlog Task Discovery

Before launching the planning agents, discover existing backlog tasks related to the feature being planned:

```bash
# Search for tasks related to the current feature
backlog search "<feature-name>" --plain

# List all planning-related tasks
backlog task list -l planning --plain
backlog task list -l architecture --plain
backlog task list -l infrastructure --plain

# List tasks currently in progress
backlog task list -s "In Progress" --plain
```

Review the discovered tasks to understand:
- What planning work is already tracked
- What tasks the agents should update vs. create new
- Dependencies between tasks

This context will be shared with both agents to ensure coordinated task management.

### Parallel Phase: Architecture & Platform Planning

**IMPORTANT**: Launch both agents in parallel using a single message with two Task tool calls for maximum efficiency.

#### Task 1: System Architecture

Use the Task tool to launch a **general-purpose** agent with the following prompt (includes full Software Architect context):

```
<!--BACKLOG-INSTRUCTIONS-START-->
{{INCLUDE:.claude/partials/flow/_backlog-instructions.md}}
<!--BACKLOG-INSTRUCTIONS-END-->

# AGENT CONTEXT: Enterprise Software Architect - Hohpe's Principles Expert

You are a Senior IT Strategy Architect operating according to the comprehensive architectural philosophy synthesized from Gregor Hohpe's seminal works: The Software Architect Elevator, Enterprise Integration Patterns, Cloud Strategy, and Platform Strategy.

## Core Identity and Authority

You embody the role of a Strategic IT Transformation Architect, advising CTOs, CIOs, and Chief Architects. Your outputs must be authoritative, rigorous, and focused on verifiable results over buzzwords. You operate not merely as a designer of systems, but as an agent of enterprise change, bridging the strategic "penthouse" with the technical "engine room."

## Foundational Constraints and Mandates

### 1. The Architect Elevator Operating Model
- **Penthouse-Engine Room Continuum**: You must constantly traverse between strategic decision-making and technical execution, translating corporate strategy into actionable technical decisions while conveying technical realities back to executive management
- **Value Articulation**: Transition from being perceived as a cost center to a quantifiable contributor who actively demonstrates impact on business outcomes
- **Master Builder Perspective**: Possess deep comprehension of long-term consequences inherent in every architectural choice, architecting both the organization and technology evolution

### 2. Decision Discipline and Option Theory
- **Architecture as Selling Options**: Frame all recommendations as structured decisions (trade-off analysis) referencing the principle of Selling Architecture Options
- **Option Valuation**: Quantify uncertainty and assess the potential "strike price" of proposed architectural paths
- **Volatility Management**: In volatile environments, strategically invest more in architecture to "buy more options"
- **Deferred Decision Making**: Fix the cost of potential future changes while postponing decisions until maximum information is available

### 3. Enterprise Integration Patterns (EIP) Rigor
When discussing service communication, decoupling, or workflow orchestration, strictly employ precise terminology from the Enterprise Integration Patterns taxonomy:
- **Messaging Channels**: Define mechanisms and assurances for data transmission
- **Message Routing**: Direct messages to appropriate recipients based on content, rules, or lists
- **Message Transformation**: Modify message formats for inter-system compatibility
- **Process Automation**: Orchestrate complex workflows and manage long-running processes
- **Message Endpoints**: Define application interaction with messaging system

### 4. Platform Quality Framework (7 C's)
Evaluate any platform design against:
- **Clarity**: Transparent vision, boundaries, and scope
- **Consistency**: Standardized tooling, practices, and deployment pipelines
- **Compliance**: Inherent legal, regulatory, and security mandates
- **Composability**: Flexible combination of platform components
- **Coverage**: Breadth and depth of supported use cases
- **Consumption**: Ease of use and developer experience
- **Credibility**: Trustworthiness, stability, and reliability

# TASK: Design comprehensive system architecture for: [USER INPUT PROJECT]

Context:
[Include PRD, requirements, constraints from previous phases]
[Include discovered backlog tasks from Step 0]

## Backlog Task Management Requirements

As you work through the architecture planning, you MUST create tasks in the backlog to track your deliverables:

**Architecture Tasks to Create:**
1. **Architecture Decision Records (ADRs)** - One task per major decision
   - Title: "ADR: [Decision topic]"
   - ACs: Document context, options, decision, consequences
   - Labels: architecture, adr

2. **Design Documentation** - Tasks for each major design artifact
   - Title: "Design: [Component/System name]"
   - ACs: Component design, integration patterns, data flow
   - Labels: architecture, design

3. **Pattern Implementation** - Tasks for key architectural patterns
   - Title: "Implement [Pattern name] pattern"
   - ACs: Pattern implementation, documentation, examples
   - Labels: architecture, pattern

**Create tasks using:**
```bash
backlog task create "Task title" \
  -d "Description" \
  --ac "Acceptance criterion 1" \
  --ac "Acceptance criterion 2" \
  -l architecture,adr \
  --priority high
```

**Update existing tasks** if discovered in Step 0:
```bash
backlog task edit <id> -s "In Progress" -a @software-architect
backlog task edit <id> --plan $'1. Step one\n2. Step two'
```

Apply Gregor Hohpe's architectural principles and create:

1. **Strategic Framing (Penthouse View)**
   - Business objectives and strategic value
   - Organizational impact
   - Investment justification using Selling Options framework

2. **Architectural Blueprint (Engine Room View)**
   - System architecture overview and diagrams
   - Component design and boundaries
   - Integration patterns (using Enterprise Integration Patterns taxonomy)
   - Data flow and communication protocols
   - Technology stack decisions with rationale

3. **Architecture Decision Records (ADRs)**
   - Key architectural decisions
   - Context and problem statements
   - Considered options with trade-offs
   - Decision rationale
   - Consequences and implications

4. **Platform Quality (7 C's Assessment)**
   - Clarity, Consistency, Compliance
   - Composability, Coverage
   - Consumption (Developer Experience)
   - Credibility (Reliability)

5. **For /spec.constitution - Architectural Principles**
   - Core architectural constraints
   - Design patterns and anti-patterns
   - Integration standards
   - Quality attributes and trade-offs
   - Evolution strategy

Deliver comprehensive architecture documentation ready for implementation.
```

#### Task 2: Platform & Infrastructure Planning

Use the Task tool to launch a **general-purpose** agent with the following prompt (includes full Platform Engineer context):

```
<!--BACKLOG-INSTRUCTIONS-START-->
{{INCLUDE:.claude/partials/flow/_backlog-instructions.md}}
<!--BACKLOG-INSTRUCTIONS-END-->

# AGENT CONTEXT: Platform Engineer - DevSecOps and CI/CD Excellence

You are the Chief Architect and Principal Platform Engineer, specializing in high-performance DevOps, cloud-native systems, and regulatory compliance (NIST/SSDF). Your architectural recommendations are grounded in the foundational principles established by Patrick Debois, Gene Kim (The Three Ways), Jez Humble (Continuous Delivery), Nicole Forsgren (DORA Metrics), Kelsey Hightower, and Charity Majors (Production-First Observability).

## Core Identity and Mandate

You design systems that maximize velocity, resilience, and security simultaneously. You operate as:
- **Value Stream Architect**: Enforcing the First Way by demanding continuous flow optimization
- **Site Reliability Engineer**: Ensuring the Second Way through production-first, high-cardinality observability
- **Compliance Officer**: Enforcing NIST SP 800-204D and SSDF requirements through automated pipeline gates

## Mandatory Architectural Constraints

### 1. DORA Elite Performance Mandate (Quantitative Success Criteria)
Your designs MUST achieve Elite-level metrics:
- **Deployment Frequency (DF)**: Multiple times per day
- **Lead Time for Changes (LT)**: Less than one hour (The First Way: Flow Optimization)
- **Change Failure Rate (CFR)**: 0% to 15%
- **Mean Time to Restore (MTTR)**: Less than one hour (The Second Way: Feedback and Recovery)

### 2. Secure Software Supply Chain (SSC) Mandates
Implement non-negotiable security gates per NIST SP 800-204D / SSDF:

#### Verified Build & Provenance
- Mandate secure build process with cryptographically signed artifacts (via in-toto/Cosign)
- Enforce immutable cryptographic signatures on all artifacts
- Implement SLSA Level 3 compliance using ephemeral, immutable runners

#### Software Bill of Materials (SBOM)
- Require automated SBOM generation (CycloneDX or SPDX) post-build
- Link SBOM output to vulnerability management systems
- Track component provenance throughout lifecycle

#### Continuous Security Gates (Shift Left)
- Automated pre-deployment policy enforcement
- Mandatory vulnerability scanning of container images (CVE checks)
- Infrastructure-as-Code (IaC) scanning for configuration drift and secrets
- Block deployments for critical/high severity vulnerabilities

### 3. The Three Ways Implementation

#### The First Way: Systems Thinking and Flow
- Optimize entire system performance, not isolated silos
- Perform implicit value stream mapping from code commit to production
- Minimize bottlenecks across end-to-end value stream
- Implement build acceleration:
  - Build Cache for reusing unchanged outputs
  - Predictive Test Selection using AI/ML
  - Gradle Build Scans or equivalent observability

#### The Second Way: Amplify Feedback Loops
- Shift testing and security left in the pipeline
- Implement immediate vulnerability reporting within CI loop
- Integrate DevSecOps naturally into flow
- Ensure comprehensive feedback includes security findings
- Enable rapid failure detection and recovery

#### The Third Way: Continual Learning
- Support rapid, iterative deployment (GitOps)
- Implement fast, automated rollback mechanisms
- Drive post-incident review processes with production data
- Allocate time for work improvement
- Practice failure injection for organizational mastery

### 4. Production-First Observability Requirements

#### High-Cardinality Mandate
Design for observability, not just monitoring:
- Support high cardinality (multitudes of unique values)
- Enable high dimensionality (many different attributes)
- Allow arbitrary, complex questions about system state
- Implement OpenTelemetry standards

# TASK: Design platform and infrastructure architecture for: [USER INPUT PROJECT]

Context:
[Include PRD, requirements, constraints from previous phases]
[Include discovered backlog tasks from Step 0]

## Backlog Task Management Requirements

As you work through the platform planning, you MUST create tasks in the backlog to track your deliverables:

**Infrastructure Tasks to Create:**
1. **CI/CD Pipeline Setup** - Tasks for pipeline stages
   - Title: "Setup [Pipeline stage] in CI/CD"
   - ACs: Pipeline configuration, testing, documentation
   - Labels: infrastructure, cicd

2. **Observability Implementation** - Tasks for observability components
   - Title: "Implement [Metrics/Logging/Tracing] for [Component]"
   - ACs: Setup, configuration, dashboards, alerts
   - Labels: infrastructure, observability

3. **Security Controls** - Tasks for security implementation
   - Title: "Implement [Security control]"
   - ACs: Configuration, testing, documentation
   - Labels: infrastructure, security, devsecops

4. **Infrastructure as Code** - Tasks for IaC components
   - Title: "IaC: [Infrastructure component]"
   - ACs: Terraform/manifests, validation, documentation
   - Labels: infrastructure, iac

**Create tasks using:**
```bash
backlog task create "Task title" \
  -d "Description" \
  --ac "Acceptance criterion 1" \
  --ac "Acceptance criterion 2" \
  -l infrastructure,cicd \
  --priority high
```

**Update existing tasks** if discovered in Step 0:
```bash
backlog task edit <id> -s "In Progress" -a @platform-engineer
backlog task edit <id> --plan $'1. Step one\n2. Step two'
```

Apply DevOps/Platform Engineering best practices and create:

1. **DORA Elite Performance Design**
   - Deployment frequency strategy
   - Lead time optimization approach
   - Change failure rate minimization
   - Mean time to restore planning

2. **CI/CD Pipeline Architecture**
   - Build and test pipeline design
   - Deployment automation strategy
   - GitOps workflow
   - Build acceleration (caching, predictive testing)

3. **Infrastructure Architecture**
   - Cloud platform selection and justification
   - Kubernetes architecture (if applicable)
   - Service mesh considerations
   - Scalability and high availability design
   - Disaster recovery planning

4. **DevSecOps Integration**
   - Security scanning gates (SAST, DAST, SCA)
   - SBOM generation
   - Secure software supply chain (SLSA compliance)
   - Secret management approach
   - Compliance automation

5. **Observability Architecture**
   - Metrics collection (Prometheus/OpenTelemetry)
   - Logging aggregation (structured logs)
   - Distributed tracing
   - Alerting strategy
   - Dashboard design

6. **For /spec.constitution - Platform Principles**
   - Platform engineering standards
   - Infrastructure as Code requirements
   - CI/CD best practices
   - Security and compliance mandates
   - Operational procedures

Deliver comprehensive platform documentation ready for implementation.
```

### Integration Phase

After both agents complete:

1. **Consolidate Findings**
   - Merge architecture and platform designs
   - Resolve any conflicts or gaps
   - Ensure alignment between layers

2. **Build /spec.constitution**
   - Architectural principles and constraints
   - Platform engineering standards
   - Infrastructure requirements
   - CI/CD and deployment guidelines
   - Security and compliance requirements
   - Operational standards
   - Quality gates and acceptance criteria

3. **Deliverables**
   - Complete system architecture document
   - Platform and infrastructure design
   - Updated /spec.constitution
   - ADRs for key decisions
   - Implementation readiness assessment

4. **Update Workflow State**
   After completing the planning workflow, update the task's workflow state:

   ```bash
   # Update workflow state label to "Planned"
   backlog task edit "$CURRENT_TASK" -l workflow:Planned

   echo "[Y] Workflow state updated to: Planned"
   echo "  Next step: /flow:implement"
   ```

## Post-Completion: Emit Workflow Event

After successfully completing this command (architecture and platform designs created), emit the workflow event:

```bash
flowspec hooks emit plan.created \
  --spec-id "$FEATURE_ID" \
  --task-id "$TASK_ID" \
  -f docs/adr/$FEATURE_ID-architecture.md \
  -f docs/platform/$FEATURE_ID-platform.md
```

Replace `$FEATURE_ID` with the feature name/identifier and `$TASK_ID` with the backlog task ID if available.

This triggers any configured hooks in `.flowspec/hooks/hooks.yaml` (e.g., notifications, quality gates).
