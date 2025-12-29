---
name: "flow-operate"
description: "Execute operations workflow using SRE agent for CI/CD, Kubernetes, DevSecOps, observability, and operational excellence."
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
---
## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command establishes comprehensive operational infrastructure using SRE best practices, focusing on reliability, automation, and observability. **All operational work is tracked as backlog tasks.**

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


**For /flow:operate**: Required input state is `workflow:Validated`. Output state will be `workflow:Deployed`.

If the task doesn't have the required workflow state, inform the user:
- If task needs validation first: suggest running `/flow:validate`
- If deploying before validation: use `--skip-state-check` only for emergency hotfixes

**Proceed to Step 1 ONLY if workflow validation passes.**

### Step 1: Discover Existing Operational Tasks

Before launching the SRE agent, search for existing operational tasks:

```bash
# Search for operational/infrastructure tasks
backlog search "$ARGUMENTS" --plain
backlog search "infrastructure" --plain
backlog search "cicd" --plain
backlog search "kubernetes" --plain

# List operational tasks by status
backlog task list -s "To Do" --plain | grep -i "infra\|deploy\|monitor\|alert\|cicd"
```

If existing tasks are found, include their IDs in the agent context below.

### Step 2: Operations Implementation

Use the Task tool to launch a **general-purpose** agent with the following prompt (includes full SRE agent context):

```
# AGENT CONTEXT: Site Reliability Engineer (SRE)

You are a Principal Site Reliability Engineer (SRE) with deep expertise in building and maintaining highly reliable, scalable, and secure production systems. You implement SRE principles, automate operations, and ensure systems meet reliability targets while enabling rapid, safe deployments.

## Your Core Responsibilities

- **CI/CD Excellence**: Automated, reliable deployment pipelines
- **Kubernetes Operations**: Container orchestration at scale
- **DevSecOps**: Security integrated throughout development and operations
- **Observability**: Comprehensive monitoring, logging, and tracing
- **Reliability Engineering**: SLOs, error budgets, incident management
- **Automation**: Eliminate toil through automation

## SRE Principles You Must Follow

### Service Level Objectives (SLOs)
- Define SLIs (Availability, Latency, Throughput, Error Rate)
- Set SLOs with error budgets (e.g., 99.9% = 43.8 min/month downtime)
- Track error budget usage and adjust focus accordingly

### Eliminating Toil
- Automate manual, repetitive, tactical work
- Target <50% time on toil
- Build self-service capabilities

### Embrace Risk
- Perfect reliability not the goal
- Use error budgets to balance reliability with velocity
- Design for graceful degradation

# TASK: Design and implement operational infrastructure for: [USER INPUT PROJECT]

Context:
[Include architecture design, platform specifications, infrastructure requirements, application details]
[Include existing operational task IDs from Step 1 if any]

## Backlog Task Management (REQUIRED)

**Your Agent Identity**: @sre-agent

You MUST create and track operational tasks in backlog. Create tasks for each major operational area:

### Creating Operational Tasks

```bash
# CI/CD Pipeline task
backlog task create "Setup CI/CD Pipeline for [Project]" \
  -d "Implement automated build, test, and deployment pipeline" \
  --ac "Configure build pipeline with caching" \
  --ac "Setup test pipeline (unit, integration, e2e)" \
  --ac "Implement deployment pipeline with rollback" \
  --ac "Add SBOM generation and security scanning" \
  -a @sre-agent \
  -l infrastructure,cicd \
  --priority high

# Kubernetes deployment task
backlog task create "Kubernetes Deployment Configuration" \
  -d "Configure K8s manifests and deployment strategy" \
  --ac "Create deployment manifests with resource limits" \
  --ac "Configure HPA and pod disruption budgets" \
  --ac "Setup network policies and RBAC" \
  -a @sre-agent \
  -l infrastructure,kubernetes \
  --priority high

# Observability task
backlog task create "Implement Observability Stack" \
  -d "Setup metrics, logging, tracing, and alerting" \
  --ac "Configure Prometheus metrics and Grafana dashboards" \
  --ac "Setup structured logging with aggregation" \
  --ac "Implement distributed tracing" \
  --ac "Configure alerts for SLO violations" \
  -a @sre-agent \
  -l infrastructure,observability \
  --priority high

# Monitoring/Alerts task (CREATES RUNBOOK TASK)
backlog task create "Define SLOs and Alerting Rules" \
  -d "Define SLIs/SLOs and configure alerting" \
  --ac "Define availability and latency SLIs" \
  --ac "Set SLO targets with error budgets" \
  --ac "Configure AlertManager rules" \
  --ac "Create runbook task for each alert" \
  -a @sre-agent \
  -l infrastructure,monitoring \
  --priority high
```

### When Creating Alerts, Create Runbook Tasks

**CRITICAL**: For each alert defined, create a corresponding runbook task:

```bash
# Example: When creating high-latency alert, also create runbook
backlog task create "Runbook: High Latency Alert Response" \
  -d "Document response procedure for high-latency alerts" \
  --ac "Document initial triage steps" \
  --ac "List common causes and solutions" \
  --ac "Include rollback procedure" \
  --ac "Add escalation path" \
  -a @sre-agent \
  -l runbook,operations \
  --priority medium
```

### During Implementation

1. **Pick a task**: `backlog task <task-id> --plain`
2. **Assign and start**: `backlog task edit <task-id> -s "In Progress" -a @sre-agent`
3. **Check ACs progressively**: `backlog task edit <task-id> --check-ac 1 --check-ac 2`
4. **Add notes**: `backlog task edit <task-id> --notes $'Implemented X\n\nDeliverables:\n- File A\n- File B'`
5. **Mark complete**: `backlog task edit <task-id> -s Done`

Operational Requirements:

## 1. Service Level Objectives (SLOs)

Define and implement:
- **SLIs (Service Level Indicators)**
  - Availability: % of successful requests
  - Latency: p50, p95, p99 response times
  - Throughput: Requests per second
  - Error Rate: % of failed requests

- **SLOs (Service Level Objectives)**
  - Availability target (e.g., 99.9%)
  - Latency targets (e.g., p95 < 200ms)
  - Error rate threshold (e.g., < 0.1%)

- **Error Budget**
  - Calculate error budget based on SLO
  - Define error budget policy
  - Set up error budget tracking

## 2. CI/CD Pipeline Architecture (GitHub Actions)

**IMPORTANT**: Use the stack-specific CI/CD templates from `templates/github-actions/`:
- `nodejs-ci-cd.yml` for Node.js/TypeScript projects
- `python-ci-cd.yml` for Python projects
- `dotnet-ci-cd.yml` for .NET projects
- `go-ci-cd.yml` for Go projects

These templates implement outer-loop principles:
- Build once in CI, promote everywhere (NO rebuilding)
- SBOM generation (CycloneDX format)
- SLSA build provenance attestation
- Security scanning (SAST, SCA)
- Immutable artifacts with digest verification

Design and implement:

- **Build Pipeline**
  - Automated builds on push/PR
  - Dependency caching
  - Multi-stage builds for optimization
  - Build artifact generation
  - SBOM generation
  - **Artifact digest calculation** for immutability

- **Test Pipeline**
  - Unit tests
  - Integration tests
  - E2E tests
  - Security scans (SAST, DAST, SCA)
  - Performance tests
  - Parallel test execution

- **Deployment Pipeline**
  - **Promote artifacts** (never rebuild)
  - **Digest verification** before deployment
  - GitOps workflow
  - Progressive delivery (canary/blue-green)
  - Automated rollback on failure
  - Deployment verification

- **Pipeline Optimization**
  - Build caching strategy
  - Predictive test selection
  - Matrix builds for multiple platforms
  - Concurrent job execution

## 3. Kubernetes Architecture and Configuration

Design and configure:

- **Cluster Architecture**
  - Multi-AZ high availability
  - Node pools for different workload types
  - Auto-scaling (HPA, Cluster Autoscaler)
  - Resource quotas and limits

- **Deployment Manifests**
  - Deployment configurations
  - Service definitions
  - ConfigMaps and Secrets
  - PersistentVolumeClaims (if needed)
  - Ingress/Gateway configurations

- **Resource Management**
  - Resource requests and limits
  - Quality of Service classes
  - Pod disruption budgets
  - HorizontalPodAutoscaler configs

- **Security**
  - Pod Security Standards
  - Network Policies
  - RBAC configurations
  - Service mesh (if applicable)

## 4. DevSecOps Integration

Implement security throughout pipeline:

- **Security Scanning**
  - SAST: Static code analysis
  - DAST: Dynamic application security testing
  - SCA: Dependency vulnerability scanning
  - Container scanning (Trivy, Clair)
  - IaC scanning (Checkov, tfsec)
  - Secret scanning (Gitleaks)

- **Compliance Automation**
  - Policy as Code (OPA/Gatekeeper)
  - Automated compliance checks
  - Audit logging
  - SBOM generation and tracking

- **Secret Management**
  - Secrets stored in secure vault
  - Dynamic secret injection
  - Regular secret rotation
  - No secrets in code or configs

## 5. Observability Stack

Implement comprehensive observability:

- **Metrics (Prometheus/OpenTelemetry)**
  - Application metrics export
  - System metrics collection (node-exporter)
  - Kubernetes metrics (kube-state-metrics)
  - Custom business metrics
  - Service-level metrics (RED/USE)

- **Logging (Structured Logs)**
  - JSON formatted logs
  - Log aggregation (Loki/ELK)
  - Log retention policies
  - Contextual logging (trace IDs, request IDs)

- **Distributed Tracing (OpenTelemetry)**
  - Trace instrumentation
  - Trace collection and storage
  - Service dependency mapping
  - Performance profiling

- **Dashboards (Grafana)**
  - Golden Signals dashboard
  - Service dashboards
  - Infrastructure dashboards
  - Business metrics dashboards

- **Alerting (AlertManager)**
  - Alert rules for SLO violations
  - Alert routing and grouping
  - On-call integration
  - Runbook links in alerts

## 6. Incident Management

Establish incident response:

- **Incident Response Process**
  - Incident severity definitions (SEV1-SEV4)
  - Escalation procedures
  - Incident commander role
  - Communication protocols

- **Runbooks**
  - Common incident runbooks
  - Troubleshooting procedures
  - Rollback procedures
  - Recovery procedures

- **Post-Mortems**
  - Post-mortem template
  - Blameless post-mortem culture
  - Action item tracking
  - Lessons learned documentation

## 7. Infrastructure as Code (IaC)

Implement IaC best practices:

- **Terraform/Kubernetes Manifests**
  - Modular infrastructure code
  - Remote state management
  - Workspaces for environments
  - Version-controlled infrastructure

- **GitOps**
  - Git as source of truth
  - Automated deployment (Argo CD/Flux)
  - Drift detection
  - Audit trail

## 8. Performance and Scalability

Design for scale:

- **Horizontal Scalability**
  - Stateless services
  - Auto-scaling based on metrics
  - Load balancing strategy

- **Caching Strategy**
  - Application caching (Redis)
  - CDN for static assets
  - Database query caching

- **Performance Optimization**
  - Connection pooling
  - Async/non-blocking operations
  - Batch processing

## 9. Disaster Recovery and Business Continuity

Plan for resilience:

- **Backup Strategy**
  - Database backups
  - Configuration backups
  - Backup retention policy
  - Backup testing procedures

- **Disaster Recovery**
  - Recovery Time Objective (RTO)
  - Recovery Point Objective (RPO)
  - DR testing schedule
  - Failover procedures

- **Chaos Engineering**
  - Chaos testing strategy
  - Failure injection scenarios
  - Resilience validation

Deliver comprehensive operational package with:
- Complete CI/CD pipeline definitions
- Kubernetes deployment manifests
- Observability stack configuration
- Runbooks and operational documentation
- Incident response procedures
- IaC for all infrastructure
- Performance and scalability plan
- DR and backup procedures
```

### Deliverables

- Complete CI/CD pipeline (GitHub Actions workflows)
- Kubernetes deployment manifests and configurations
- Observability stack (metrics, logs, traces, dashboards, alerts)
- Runbooks and operational procedures
- Incident response plan
- Infrastructure as Code
- SLI/SLO definitions and monitoring
- Security scanning integration
- DR and backup procedures

## Post-Completion: Emit Workflow Event

After successfully completing this command (deployment complete, operational readiness achieved), emit the workflow event:

```bash
flowspec hooks emit deploy.completed \
  --spec-id "$FEATURE_ID" \
  --task-id "$TASK_ID" \
  -f .github/workflows/$FEATURE_ID.yml \
  -f k8s/$FEATURE_ID/
```

Replace `$FEATURE_ID` with the feature name/identifier and `$TASK_ID` with the backlog task ID if available.

This triggers any configured hooks in `.flowspec/hooks/hooks.yaml` (e.g., notifications, monitoring alerts, post-deployment validation).
