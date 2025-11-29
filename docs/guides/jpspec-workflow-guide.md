# JP Spec Kit /jpspec Workflow Guide

Comprehensive guide to using the /jpspec command orchestration system for specification-driven development with AI-powered agents.

## Table of Contents

- [Executive Summary](#executive-summary)
- [Overview](#overview)
- [The Seven /jpspec Commands](#the-seven-jpspec-commands)
- [Specialized Agents](#specialized-agents)
- [Workflow Patterns](#workflow-patterns)
- [Use Case Examples](#use-case-examples)
- [Integration with Backlog Tasks](#integration-with-backlog-tasks)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Advanced Topics](#advanced-topics)
  - [Customizing the Workflow](#customizing-the-workflow)
  - [MCP Integration](#mcp-integration)
  - [Integration with CI/CD](#integration-with-cicd)
  - [Metrics and Analytics](#metrics-and-analytics)
- [Diagram: /jpspec Workflow](#diagram-jpspec-workflow)
- [References](#references)

## Executive Summary

### What is the /jpspec Workflow System?

The /jpspec workflow system is JP Spec Kit's **AI-powered command orchestration layer** that coordinates specialized agents through the complete software development lifecycle. It transforms specification-driven development from a manual process into an automated, traceable workflow.

**Value Proposition**:
- **Reduce Planning Time**: Automated PRD generation, architecture design, and task breakdown (50-70% time savings)
- **Improve Quality**: Specialized agents ensure comprehensive coverage (research, security, QA, operations)
- **Enable Traceability**: Every decision, task, and artifact tracked in backlog.md
- **Scale Team Productivity**: Parallel agent execution maximizes throughput
- **Maintain Consistency**: Proven patterns embedded in agent contexts (SVPG, DORA, SRE, DevSecOps)

### The Seven Commands

```
/jpspec:assess    → Evaluate feature complexity (Simple/Medium/Complex)
/jpspec:specify   → Create comprehensive Product Requirements Document (PRD)
/jpspec:research  → Market research + business validation
/jpspec:plan      → Architecture + platform design (parallel agents)
/jpspec:implement → Frontend + backend implementation with code review
/jpspec:validate  → QA testing + security + docs + release readiness
/jpspec:operate   → CI/CD pipelines + Kubernetes + observability
```

### When to Use /jpspec

**Use Full Workflow For**:
- Complex features (21-32 complexity score from `/jpspec:assess`)
- Multi-team coordination requirements
- High business impact or compliance needs
- Architectural changes requiring ADRs
- Features with significant technical uncertainty

**Use Spec-Light Mode For**:
- Medium features (13-20 complexity score)
- Single-team features with moderate complexity
- Well-understood technical approaches
- Features with some integration complexity

**Skip Workflow For**:
- Simple features (8-12 complexity score)
- Bug fixes with clear solutions
- Configuration changes
- Minor UI tweaks
- Documentation-only updates

See [/jpspec:assess](#jpspecassess) for detailed complexity assessment.

## Overview

### Architecture

The /jpspec system orchestrates specialized AI agents through seven distinct phases, managing the transition from high-level requirements to production-ready systems:

```mermaid
graph TB
    A[User Requirements] --> B[/jpspec:assess]
    B --> C{Complexity?}
    C -->|Complex| D[/jpspec:specify]
    C -->|Medium| D
    C -->|Simple| SKIP[Direct Implementation]

    D --> E[/jpspec:research]
    E --> F[/jpspec:plan]
    F --> G[/jpspec:implement]
    G --> H[/jpspec:validate]
    H --> I[/jpspec:operate]
    I --> J[Production Deployment]

    D -.-> BL[Backlog Tasks Created]
    E -.-> BL
    F -.-> BL
    G --> BL
    H --> BL
    I --> BL

    BL --> TRACK[Task Tracking & Progress]

    style D fill:#e1f5ff
    style E fill:#e1f5ff
    style F fill:#e1f5ff
    style G fill:#fff4e1
    style H fill:#fff4e1
    style I fill:#e8f5e9
```

### Design Workflow vs. Implementation Workflow

The /jpspec commands are divided into two categories:

**Design Commands** (Create Implementation Tasks):
- `/jpspec:specify` - Creates implementation tasks in backlog.md (section 6 of PRD)
- `/jpspec:research` - Creates follow-up implementation tasks based on findings
- `/jpspec:plan` - Creates architecture and infrastructure tasks

**Implementation Commands** (Execute Existing Tasks):
- `/jpspec:implement` - Requires existing tasks with acceptance criteria
- `/jpspec:validate` - Validates task completion and marks tasks Done
- `/jpspec:operate` - Implements operational infrastructure from backlog tasks

**Critical Rule**: Design commands produce tasks; implementation commands consume them. Never run `/jpspec:implement` without first running `/jpspec:specify` to create implementation tasks.

### Execution Patterns

Commands execute agents in two patterns:

**Sequential Execution**:
- `/jpspec:research`: Researcher → Business Validator (validator uses researcher output)
- `/jpspec:validate`: QA + Security (parallel) → Tech Writer → Release Manager

**Parallel Execution**:
- `/jpspec:plan`: Software Architect + Platform Engineer (independent work, then consolidated)
- `/jpspec:implement`: Frontend Engineer + Backend Engineer (when both needed)

Sequential patterns ensure data dependencies; parallel patterns maximize throughput.

## The Seven /jpspec Commands

### /jpspec:assess

**Purpose**: Evaluate feature complexity to determine appropriate workflow depth.

**When to Use**:
- Before starting any new feature
- When unsure if full SDD workflow is necessary
- During project planning to estimate effort
- To calibrate team understanding of complexity

**Execution Pattern**: Interactive questionnaire (8 questions)

**Agents Invoked**: None (direct user interaction)

**Inputs**:
- Feature description
- User responses to 8 assessment questions

**Outputs**:
- Complexity score (8-32 points)
- Complexity classification (Simple/Medium/Complex)
- Workflow recommendation (Skip SDD / Spec-Light / Full SDD)
- Specific next steps

**Assessment Dimensions**:
1. Scope and Size (LOC, modules affected)
2. Integration and Dependencies (external APIs, data complexity)
3. Team and Process (team size, cross-functional needs)
4. Risk and Uncertainty (technical unknowns, business impact)

**Example Usage**:
```bash
/jpspec:assess Add user authentication with OAuth2
```

**Decision Matrix**:
- **8-12 points**: Simple → Skip SDD, implement directly
- **13-20 points**: Medium → Spec-Light mode (specify + implement only)
- **21-32 points**: Complex → Full SDD workflow (all 7 commands)

**Reference**: See `.claude/commands/jpspec/assess.md` for complete assessment framework.

---

### /jpspec:specify

**Purpose**: Create comprehensive Product Requirements Document (PRD) using SVPG Product Operating Model principles.

**When to Use**:
- Starting a new feature (after `/jpspec:assess` recommends Medium or Complex)
- When user stories need formalization
- When cross-functional alignment is required
- When clear acceptance criteria are needed for implementation

**Execution Pattern**: Sequential (single agent)

**Agents Invoked**:
- **Product Requirements Manager** (@pm-planner)
  - Expertise: SVPG principles, DVF+V risk framework, outcome-driven development
  - Philosophy: Fall in love with the problem, not the solution

**Inputs**:
- User-provided feature description
- Business context or research findings (if available)
- Existing backlog tasks related to the feature (discovered via search)

**Outputs**:
1. **Comprehensive PRD** with 10 sections:
   - Executive Summary (problem, solution, metrics, business value)
   - User Stories and Use Cases
   - DVF+V Risk Assessment (Desirability, Usability, Feasibility, Viability)
   - Functional Requirements
   - Non-Functional Requirements (performance, security, accessibility)
   - **Task Breakdown (backlog tasks created via CLI)**
   - Discovery and Validation Plan
   - Acceptance Criteria and Testing
   - Dependencies and Constraints
   - Success Metrics (outcome-focused, North Star metric)

2. **Backlog Tasks** - Created in section 6, including:
   - Task IDs from backlog CLI
   - Dependencies between tasks
   - Priority ordering (high/medium/low)
   - Complexity labels (size-s, size-m, size-l, size-xl)
   - Acceptance criteria (minimum 2 per task)

**Critical Requirement**: The PM Planner agent **MUST** create implementation tasks using `backlog task create` during PRD development. Failure to create tasks means the specification is incomplete.

**Example Usage**:
```bash
/jpspec:specify Build a user dashboard with activity timeline and notifications
```

**Verification After Completion**:
```bash
# Verify tasks were created
backlog task list --plain | grep -i "dashboard"
```

**Reference**: See `.claude/commands/jpspec/specify.md` for complete agent context.

---

### /jpspec:research

**Purpose**: Conduct comprehensive market research and business validation to de-risk feature investments.

**When to Use**:
- After specification is complete
- When market validation is needed
- When competitive landscape is unclear
- When business viability is uncertain
- For high-investment features requiring validation

**Execution Pattern**: Sequential (two agents)

**Agents Invoked**:
1. **Senior Research Analyst** (@researcher)
   - Expertise: Market intelligence, competitive analysis, technical feasibility, trend forecasting
   - Methodology: Multi-source verification, credible citations, quantitative analysis

2. **Senior Business Analyst** (@business-validator)
   - Expertise: Business viability, opportunity validation, financial analysis, strategic risk
   - Framework: TAM/SAM/SOM analysis, unit economics, risk assessment

**Inputs**:
- Feature specification from `/jpspec:specify`
- Research topic or focus areas
- Existing research tasks (discovered via backlog search)

**Phase 1 Outputs** (Research):
- Executive Summary (key findings with confidence levels)
- Market Analysis (TAM/SAM/SOM, growth trends, customer segments)
- Competitive Landscape (key competitors, strengths/weaknesses, positioning)
- Technical Feasibility (available technologies, complexity, risks)
- Industry Trends (emerging patterns, best practices, future outlook)
- Sources and References (credible, recent citations)

**Phase 2 Outputs** (Business Validation):
- Executive Assessment (Go/No-Go/Proceed with Caution)
- Opportunity Score (1-10 across 4 dimensions: Market, Financial, Operational, Strategic)
- Market Opportunity Assessment (realistic TAM/SAM/SOM estimates)
- Financial Viability Analysis (revenue model, unit economics, profitability path)
- Operational Feasibility (resource requirements, capability gaps)
- Strategic Fit Analysis (organizational alignment)
- Risk Register (probability, impact, mitigation strategies)
- Critical Assumptions (what must be true, validation methods)

**Critical Requirement**: Research agents **MUST** create follow-up implementation tasks based on findings. Research without actionable tasks provides no value.

**Example Usage**:
```bash
/jpspec:research OAuth2 authentication providers for enterprise SaaS
```

**Backlog Integration**:
- Creates research spike task with ACs
- Documents findings in task implementation notes
- Creates follow-up implementation tasks based on recommendations
- Links research task to implementation tasks

**Reference**: See `.claude/commands/jpspec/research.md` for complete agent contexts.

---

### /jpspec:plan

**Purpose**: Create comprehensive architectural and platform design using parallel specialized agents.

**When to Use**:
- After specification (and optionally research) is complete
- When architectural decisions are needed
- When platform/infrastructure design is required
- Before implementation to establish technical foundation
- When ADRs (Architecture Decision Records) are needed

**Execution Pattern**: Parallel (two agents working simultaneously)

**Agents Invoked**:
1. **Enterprise Software Architect** (@software-architect)
   - Expertise: Gregor Hohpe's principles, Enterprise Integration Patterns, Architect Elevator
   - Philosophy: Traverse penthouse-to-engine-room, architecture as selling options
   - Framework: 7 C's Platform Quality (Clarity, Consistency, Compliance, Composability, Coverage, Consumption, Credibility)

2. **Platform Engineer** (@platform-engineer)
   - Expertise: DevSecOps, DORA metrics, NIST/SSDF compliance, SRE principles
   - Philosophy: Elite DORA performance, secure by design, production-first observability
   - Framework: The Three Ways (Flow, Feedback, Continuous Learning)

**Inputs**:
- PRD from `/jpspec:specify`
- Requirements and constraints
- Existing backlog tasks (architecture/infrastructure tasks discovered via search)

**Agent 1 Outputs** (Software Architect):
1. Strategic Framing (business objectives, investment justification using Options framework)
2. Architectural Blueprint (system overview, component design, integration patterns using EIP taxonomy)
3. Architecture Decision Records (ADRs) - Key decisions with context, options, consequences
4. Platform Quality Assessment (7 C's evaluation)
5. Architectural Principles for /speckit.constitution

**Agent 2 Outputs** (Platform Engineer):
1. DORA Elite Performance Design (deployment frequency, lead time, CFR, MTTR strategies)
2. CI/CD Pipeline Architecture (build, test, deployment automation, GitOps)
3. Infrastructure Architecture (cloud platform, Kubernetes, service mesh, HA, DR)
4. DevSecOps Integration (SAST/DAST/SCA, SBOM, SLSA compliance, secret management)
5. Observability Architecture (Prometheus/OpenTelemetry, logging, tracing, alerting)
6. Platform Principles for /speckit.constitution

**Integration Phase**:
After both agents complete, consolidate findings into:
- Complete system architecture document
- Platform and infrastructure design
- Updated /speckit.constitution (architectural + platform principles)
- ADRs for key decisions
- Implementation readiness assessment

**Critical Requirement**: Both agents **MUST** create backlog tasks for their deliverables (ADRs, design docs, pattern implementations, infrastructure setup).

**Example Usage**:
```bash
/jpspec:plan Multi-tenant SaaS application with microservices architecture
```

**Backlog Integration**:
- Creates architecture tasks (ADRs, design docs, patterns)
- Creates infrastructure tasks (CI/CD, observability, security, IaC)
- Updates existing planning tasks (discovered in Step 0)
- All tasks assigned to respective agents

**Reference**: See `.claude/commands/jpspec/plan.md` for complete agent contexts.

---

### /jpspec:implement

**Purpose**: Execute implementation using specialized engineering agents with integrated code review.

**When to Use**:
- After planning is complete (and tasks are created in backlog)
- **ONLY when implementation tasks exist with defined acceptance criteria**
- When ready for actual code development
- Never without first running `/jpspec:specify` to create tasks

**Execution Pattern**: Parallel engineers (Phase 1) → Sequential code review (Phase 2)

**Critical Prerequisite**: This command **REQUIRES** existing backlog tasks. It will error if no relevant tasks are found. Run `/jpspec:specify` first to create implementation tasks.

**Agents Invoked**:

**Phase 1 - Implementation (Parallel)**:
1. **Senior Frontend Engineer** (@frontend-engineer)
   - Expertise: React 18+, React Native, TypeScript, performance optimization, accessibility (WCAG 2.1 AA)
   - Technologies: Zustand, Tailwind CSS, Vitest, React Testing Library, Playwright
   - Focus: Component development, state management, responsive design, performance, testing

2. **Senior Backend Engineer** (@backend-engineer)
   - Expertise: Go, TypeScript/Node.js, Python, RESTful/GraphQL/gRPC APIs, CLI tools
   - Technologies: Go (net/http, Gin, cobra), TypeScript (Express, Fastify, Prisma), Python (FastAPI, SQLAlchemy)
   - **Mandatory Code Hygiene**: Remove ALL unused imports/variables before completion (blocking requirement)
   - **Defensive Coding**: Input validation at boundaries, type safety, explicit error handling

3. **AI/ML Engineer** (@ai-ml-engineer) - Optional
   - Expertise: Model training, MLOps, inference optimization, monitoring
   - Technologies: MLflow, model versioning, deployment pipelines
   - Focus: Training pipelines, feature engineering, model serving, drift detection

**Phase 2 - Code Review (Sequential)**:
4. **Principal Frontend Code Reviewer** (@frontend-code-reviewer)
   - Review Areas: Functionality, performance (Web Vitals), accessibility (WCAG), code quality, testing, security (XSS)
   - Validates: AC completion in backlog tasks, unchecks ACs if not satisfied

5. **Principal Backend Code Reviewer** (@backend-code-reviewer)
   - Review Areas: Security (auth, injection prevention), performance (N+1 queries), code quality, API design, database, testing
   - **Critical Blocks**: Unused imports/variables (MUST be zero), missing input validation, missing type annotations
   - Validates: AC completion in backlog tasks, unchecks ACs if not satisfied

**Inputs**:
- Architecture and PRD
- **Backlog task IDs** (discovered in Step 0)
- API contracts and data models

**Outputs**:
- Production-ready code (frontend and/or backend)
- Comprehensive test suites (unit, integration)
- Code review reports with categorized feedback (Critical/High/Medium/Low)
- Updated backlog tasks with implementation notes and checked ACs

**Backlog Task Workflow** (for each engineer):
1. **Pick a task**: `backlog task <task-id> --plain`
2. **Assign and start**: `backlog task edit <task-id> -s "In Progress" -a @backend-engineer`
3. **Add implementation plan**: `backlog task edit <task-id> --plan $'1. Step 1\n2. Step 2'`
4. **Check ACs progressively**: `backlog task edit <task-id> --check-ac 1 --check-ac 2`
5. **Add notes**: `backlog task edit <task-id> --notes $'Implementation summary...'`
6. **Reviewers validate**: Verify ACs are truly complete, uncheck if not satisfied

**Backend Pre-Completion Checklist** (BLOCKING):
- [ ] No unused imports - Run linter, remove ALL unused imports
- [ ] No unused variables - Remove or use all declared variables
- [ ] All inputs validated - Boundary functions validate their inputs
- [ ] Edge cases handled - Empty values, None/null, invalid types
- [ ] Types annotated - All public functions have type hints/annotations
- [ ] Errors handled - All error paths have explicit handling
- [ ] Tests pass - All unit and integration tests pass
- [ ] Linter passes - No linting errors or warnings

**Example Usage**:
```bash
# First verify tasks exist
backlog task list -s "To Do" --plain

# Then run implementation
/jpspec:implement User authentication and authorization system
```

**Error Handling**:
If no tasks are found:
```
⚠️ No backlog tasks found for: [FEATURE NAME]

This command requires existing backlog tasks with defined acceptance criteria.
Please run /jpspec:specify first to create implementation tasks.
```

**Reference**: See `.claude/commands/jpspec/implement.md` for complete agent contexts.

---

### /jpspec:validate

**Purpose**: Execute comprehensive quality assurance, security validation, documentation, and release readiness assessment.

**When to Use**:
- After implementation is complete
- Before production deployment
- When quality gates are required
- For production-readiness validation
- When security assessment is needed

**Execution Pattern**: QA + Security (parallel Phase 1) → Tech Writer (Phase 2) → Release Manager (Phase 3)

**Agents Invoked**:

**Phase 1 - Testing & Security (Parallel)**:
1. **Quality Guardian** (@quality-guardian)
   - Philosophy: Constructive skepticism, see failure modes others miss
   - Framework: Failure Imagination Exercise, Edge Case Exploration, Three-Layer Critique
   - Focus: Functional testing, API/contract testing, integration testing, performance testing, accessibility (WCAG 2.1 AA)
   - **Validates backlog task ACs**: Marks ACs complete as validation succeeds

2. **Secure-by-Design Engineer** (@secure-by-design-engineer)
   - Philosophy: Assume breach, defense in depth, principle of least privilege
   - Framework: Risk assessment, threat modeling, severity classification (Critical/High/Medium/Low)
   - Focus: Code security (auth, injection prevention, XSS/CSRF), dependency scanning, infrastructure security, compliance (GDPR, SOC2)
   - **Validates security ACs**: Updates task notes with security findings

**Phase 2 - Documentation (Sequential)**:
3. **Senior Technical Writer** (@tech-writer)
   - Expertise: API docs, user guides, technical docs, release notes, runbooks
   - Standards: Clear structure, tested examples, accessibility
   - Deliverables: API reference, user documentation, technical docs, release notes, runbooks
   - **Creates documentation tasks**: Tracks doc work in backlog

**Phase 3 - Release Management (Sequential, Human Approval Gate)**:
4. **Senior Release Manager** (@release-manager)
   - Expertise: Release coordination, quality validation, risk management, deployment orchestration
   - Framework: Pre-release validation checklist, release types (major/minor/patch/hotfix), deployment strategies
   - **Critical Responsibility**: Verify Definition of Done for ALL backlog tasks before approving release
   - **Human Approval Required**: ALL production releases require explicit human approval

**Inputs**:
- Implemented code
- Test results
- Backlog task details for validation context

**Phase 1 Outputs** (QA + Security):
- Comprehensive test report (functional, integration, performance, accessibility)
- Quality metrics and risk assessment
- Security assessment report (findings by severity, vulnerability details, compliance status)
- Issues categorized by severity
- Recommendations for production readiness

**Phase 2 Outputs** (Documentation):
- API documentation (endpoints, examples, authentication, errors)
- User documentation (overview, getting started, tutorials, troubleshooting)
- Technical documentation (architecture, configuration, deployment, monitoring)
- Release notes (features, breaking changes, migration guide, known limitations)
- Internal documentation (code comments, runbooks, incident response)

**Phase 3 Outputs** (Release Management):
- Pre-release validation checklist (all items checked)
- Release readiness assessment (go/no-go recommendation)
- Deployment plan (strategy, window, stakeholders, rollback)
- Risk assessment (deployment risks, user impact, rollback complexity)
- **Human Approval Checkpoint**: Clear go/no-go with supporting evidence
- Post-approval deployment coordination

**Definition of Done Verification** (Release Manager):
Before approving ANY release:
1. ✅ All acceptance criteria checked - Every task AC marked complete
2. ✅ Implementation notes added - Each task has implementation summary
3. ✅ Tests passing - Verify test results for each task
4. ✅ Code reviewed - Confirm review completion

**Example Usage**:
```bash
# Discover tasks ready for validation
backlog task list -s "In Progress" --plain
backlog task list -s "Done" --plain

# Run validation
/jpspec:validate User authentication feature
```

**Release Types and Approval**:
- **Major (x.0.0)**: Breaking changes - Executive sign-off required
- **Minor (x.y.0)**: New features - Product owner approval required
- **Patch (x.y.z)**: Bug fixes - Engineering lead approval required
- **Hotfix**: Critical fixes - On-call lead + stakeholder approval required

**Reference**: See `.claude/commands/jpspec/validate.md` for complete agent contexts.

---

### /jpspec:operate

**Purpose**: Establish comprehensive operational infrastructure using SRE best practices.

**When to Use**:
- After validation is complete
- When CI/CD pipelines are needed
- When Kubernetes deployment is required
- When observability infrastructure is needed
- For production deployment preparation
- When operational automation is required

**Execution Pattern**: Sequential (single agent)

**Agents Invoked**:
1. **Principal Site Reliability Engineer** (@sre-agent)
   - Expertise: CI/CD excellence, Kubernetes operations, DevSecOps, observability, reliability engineering
   - Principles: SLOs/error budgets, eliminate toil, embrace risk, automation-first
   - Framework: DORA metrics, NIST/SSDF compliance, production-first observability

**Inputs**:
- Architecture design
- Platform specifications
- Infrastructure requirements
- Application details
- Existing operational tasks (discovered via backlog search)

**Outputs**:

1. **Service Level Objectives (SLOs)**
   - SLIs defined (availability, latency, throughput, error rate)
   - SLO targets set (e.g., 99.9% availability)
   - Error budget calculated and tracked

2. **CI/CD Pipeline Architecture (GitHub Actions)**
   - **Uses stack-specific templates** from `templates/github-actions/`:
     - `nodejs-ci-cd.yml` for Node.js/TypeScript
     - `python-ci-cd.yml` for Python
     - `go-ci-cd.yml` for Go
     - `dotnet-ci-cd.yml` for .NET
   - Build pipeline (caching, multi-stage builds, SBOM generation, digest calculation)
   - Test pipeline (unit, integration, e2e, security scans, parallel execution)
   - Deployment pipeline (promote artifacts with digest verification, GitOps, progressive delivery, automated rollback)

3. **Kubernetes Architecture**
   - Cluster architecture (multi-AZ HA, node pools, auto-scaling, resource quotas)
   - Deployment manifests (deployments, services, ConfigMaps, Secrets, Ingress)
   - Resource management (requests/limits, QoS, PDBs, HPA)
   - Security (Pod Security Standards, Network Policies, RBAC, service mesh)

4. **DevSecOps Integration**
   - Security scanning (SAST, DAST, SCA, container scanning, IaC scanning, secret scanning)
   - Compliance automation (Policy as Code, automated checks, audit logging, SBOM)
   - Secret management (secure vault, dynamic injection, rotation, no secrets in code)

5. **Observability Stack**
   - Metrics (Prometheus/OpenTelemetry, system metrics, custom business metrics, RED/USE)
   - Logging (structured JSON logs, aggregation, retention policies, contextual logging)
   - Distributed tracing (OpenTelemetry instrumentation, service dependency mapping)
   - Dashboards (Grafana for Golden Signals, service dashboards, infrastructure dashboards)
   - Alerting (AlertManager for SLO violations, routing/grouping, on-call integration, runbook links)

6. **Incident Management**
   - Incident response process (severity definitions, escalation, incident commander role)
   - **Runbooks** (common incidents, troubleshooting, rollback, recovery)
   - Post-mortems (template, blameless culture, action tracking)

7. **Infrastructure as Code**
   - Terraform/K8s manifests (modular code, remote state, workspaces, version control)
   - GitOps (Git as source of truth, automated deployment, drift detection, audit trail)

8. **Performance and Scalability**
   - Horizontal scalability (stateless services, auto-scaling, load balancing)
   - Caching strategy (Redis, CDN, database query caching)
   - Performance optimization (connection pooling, async operations, batch processing)

9. **Disaster Recovery**
   - Backup strategy (database backups, config backups, retention policy, testing)
   - DR planning (RTO/RPO, testing schedule, failover procedures)
   - Chaos engineering (testing strategy, failure injection, resilience validation)

**Critical Requirement: Runbook Tasks**

When creating alerts, the SRE agent **MUST** create corresponding runbook tasks:

```bash
# Example: For each alert, create a runbook task
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

**Example Usage**:
```bash
# Discover existing operational tasks
backlog search "infrastructure" --plain
backlog search "cicd" --plain

# Run operations workflow
/jpspec:operate E-commerce platform with microservices
```

**Backlog Integration**:
Creates operational tasks for:
- CI/CD pipeline setup (build, test, deployment with SBOM and security scanning)
- Kubernetes deployment configuration
- Observability stack implementation
- SLO and alerting rules definition
- **Runbook creation** (one task per alert type)
- IaC implementation
- DR and backup procedures

**Outer Loop Principles**:
- Build once in CI, promote everywhere (NO rebuilding for different environments)
- Immutable artifacts with digest verification
- SLSA build provenance attestation
- SBOM generation (CycloneDX format)
- Security scanning integrated into pipeline

**Reference**: See `.claude/commands/jpspec/operate.md` for complete agent context.

---

## Specialized Agents

The /jpspec system coordinates 15 specialized agents across the development lifecycle. Each agent brings domain expertise, proven frameworks, and best practices to their area of responsibility.

### Agent Classification

Agents are organized into two loops based on the **Agent Loop Classification** framework:

**Inner Loop Agents** (Iterate on code and specifications):
- Product Requirements Manager
- Researcher
- Business Validator
- Software Architect
- Platform Engineer
- Frontend Engineer
- Backend Engineer
- AI/ML Engineer
- Frontend Code Reviewer
- Backend Code Reviewer
- Quality Guardian
- Secure-by-Design Engineer
- Technical Writer

**Outer Loop Agents** (Operate production systems):
- SRE Agent
- Release Manager

### Agent Details

#### Product Requirements Manager (@pm-planner)
**Role**: Creates comprehensive Product Requirements Documents (PRDs)

**Expertise**:
- SVPG Product Operating Model (Inspired, Empowered, Transformed)
- DVF+V Risk Framework (Desirability, Usability, Feasibility, Viability)
- Outcome-driven development
- Product discovery techniques

**Philosophy**:
- Empowered product teams over feature factories
- Fall in love with the problem, not the solution
- Focus on outcomes (customer behavior change) over outputs (features)
- Validate risks early and cheaply

**Invoked By**: `/jpspec:specify`

**Responsibilities**:
- Create 10-section PRD (executive summary, user stories, DVF+V assessment, requirements, success metrics)
- **Create implementation tasks in backlog.md** (section 6 of PRD)
- Define North Star metric and outcome-focused KPIs
- Document discovery and validation plan
- Establish clear acceptance criteria

---

#### Senior Research Analyst (@researcher)
**Role**: Conducts comprehensive market and technical research

**Expertise**:
- Market intelligence and competitive analysis
- Technical feasibility assessment
- Industry trend forecasting
- Multi-source intelligence gathering

**Methodology**:
- Multi-source verification (validate claims with independent sources)
- Recency prioritization (use recent information, note older sources)
- Credibility assessment (evaluate source authority and bias)
- Quantification (use specific numbers and metrics)

**Invoked By**: `/jpspec:research` (Phase 1)

**Responsibilities**:
- Market analysis (TAM/SAM/SOM, growth trends, customer segments)
- Competitive landscape (key competitors, strengths/weaknesses)
- Technical feasibility (technologies, complexity, risks)
- Industry trends (emerging patterns, best practices)
- Sourced recommendations with confidence levels

---

#### Senior Business Analyst (@business-validator)
**Role**: Validates business viability and strategic fit

**Expertise**:
- Financial viability assessment
- Market validation
- Operational feasibility
- Strategic alignment
- Risk assessment

**Framework**:
- Market Opportunity Assessment (TAM/SAM/SOM)
- Financial Viability (revenue model, cost structure, unit economics)
- Risk Analysis (market, execution, financial risks)
- Go/No-Go/Proceed-with-Caution recommendations

**Invoked By**: `/jpspec:research` (Phase 2, after Researcher)

**Responsibilities**:
- Business validation report with opportunity score (1-10)
- Financial projections (base, upside, downside scenarios)
- Risk register with mitigation strategies
- Critical assumptions identification
- Strategic recommendations
- **Create follow-up implementation tasks** based on validation

---

#### Enterprise Software Architect (@software-architect)
**Role**: Designs system architecture and integration patterns

**Expertise**:
- Gregor Hohpe's architectural philosophy (Architect Elevator, Enterprise Integration Patterns)
- Architecture as selling options (option theory)
- Platform quality framework (7 C's)
- Master builder perspective

**Framework**:
- **Architect Elevator**: Traverse penthouse (strategy) to engine room (implementation)
- **Option Theory**: Quantify uncertainty, defer decisions until maximum information
- **Enterprise Integration Patterns**: Precise terminology for messaging, routing, transformation
- **7 C's Platform Quality**: Clarity, Consistency, Compliance, Composability, Coverage, Consumption, Credibility

**Invoked By**: `/jpspec:plan` (parallel with Platform Engineer)

**Responsibilities**:
- Strategic framing (business objectives, investment justification)
- Architectural blueprint (component design, integration patterns using EIP)
- Architecture Decision Records (ADRs) with options analysis
- Platform quality assessment (7 C's)
- Architectural principles for /speckit.constitution
- **Create architecture tasks in backlog** (ADRs, design docs, pattern implementations)

---

#### Platform Engineer (@platform-engineer)
**Role**: Designs platform and infrastructure architecture

**Expertise**:
- DevSecOps and CI/CD excellence
- DORA metrics (Deployment Frequency, Lead Time, CFR, MTTR)
- NIST SP 800-204D and SSDF compliance
- SRE principles (The Three Ways: Flow, Feedback, Continuous Learning)

**Mandates**:
- **DORA Elite Performance**: Multiple deployments/day, <1hr lead time, <15% CFR, <1hr MTTR
- **Secure Software Supply Chain**: SLSA Level 3, SBOM generation, cryptographic signatures
- **Production-First Observability**: High-cardinality metrics, OpenTelemetry standards

**Invoked By**: `/jpspec:plan` (parallel with Software Architect)

**Responsibilities**:
- DORA elite performance design
- CI/CD pipeline architecture (build acceleration, GitOps, automated rollback)
- Infrastructure architecture (cloud platform, Kubernetes, service mesh, HA/DR)
- DevSecOps integration (SAST/DAST/SCA, SBOM, secret management)
- Observability architecture (metrics, logging, tracing, alerting)
- Platform principles for /speckit.constitution
- **Create infrastructure tasks in backlog** (CI/CD, observability, security, IaC)

---

#### Senior Frontend Engineer (@frontend-engineer)
**Role**: Implements user interfaces for web and mobile

**Expertise**:
- Modern React development (React 18+ with hooks, concurrent features, server components)
- React Native for mobile apps
- Performance optimization (fast load times, smooth interactions)
- Accessibility (WCAG 2.1 AA compliance)
- TypeScript for type safety

**Technologies**:
- State management: Zustand, Jotai, TanStack Query, Context API
- Styling: Tailwind CSS, CSS Modules, Styled Components
- Testing: Vitest, React Testing Library, Playwright
- Performance: Code splitting, memoization, virtualization, Suspense

**Invoked By**: `/jpspec:implement` (parallel with Backend Engineer)

**Responsibilities**:
- Component development (React/React Native, TypeScript, composition patterns)
- State management (appropriate solution for use case)
- Styling and responsiveness (design system, cross-browser/platform)
- Performance optimization (code splitting, memoization)
- Testing (unit, integration, accessibility tests)
- **Work from backlog tasks**: Pick task, assign self, check ACs progressively

---

#### Senior Backend Engineer (@backend-engineer)
**Role**: Implements server-side logic, APIs, and CLI tools

**Expertise**:
- Multi-language: Go, TypeScript/Node.js, Python
- API development (RESTful, GraphQL, gRPC)
- CLI tools and developer tooling
- Database design and optimization
- System architecture (scalable, resilient distributed systems)

**Technologies**:
- Go: net/http, Gin, cobra (CLI), pgx (database)
- TypeScript: Express, Fastify, Prisma, Zod validation
- Python: FastAPI, SQLAlchemy, Pydantic, Click/Typer (CLI)

**Mandatory Requirements**:
1. **Code Hygiene (BLOCKING)**:
   - Remove ALL unused imports before completion
   - Remove ALL unused variables
   - Run language-specific linter (Python: `ruff check --select F401,F841`, Go: `go vet`, TS: `tsc --noEmit`)

2. **Defensive Coding (BLOCKING)**:
   - Validate ALL function inputs at API/service boundaries
   - Never trust external data (API responses, file contents, env vars, user input)
   - Type hints/annotations on ALL public functions
   - Handle None/null/undefined explicitly
   - Explicit error handling (no ignored errors)

**Invoked By**: `/jpspec:implement` (parallel with Frontend Engineer)

**Responsibilities**:
- API development (REST/GraphQL/gRPC endpoints, CLI commands)
- Business logic (implementation, validation, error handling, transactions)
- Database integration (models, migrations, efficient queries, validation)
- Security (auth/authz, input validation, injection prevention, secret management)
- Testing (unit, integration, database tests)
- **Pre-completion checklist**: Verify no unused imports/variables, all inputs validated, types annotated, errors handled
- **Work from backlog tasks**: Pick task, assign self, check ACs progressively

---

#### AI/ML Engineer (@ai-ml-engineer)
**Role**: Implements AI/ML models and infrastructure

**Expertise**:
- Model training and evaluation
- MLOps infrastructure
- Model deployment and optimization
- Monitoring and drift detection

**Technologies**:
- MLflow for experiment tracking
- Model versioning systems
- Inference optimization (quantization, pruning)
- Performance and drift monitoring

**Invoked By**: `/jpspec:implement` (optional, when ML components needed)

**Responsibilities**:
- Model development (training pipelines, feature engineering, evaluation)
- MLOps infrastructure (experiment tracking, versioning, automation)
- Model deployment (inference service, optimization, scalable serving)
- Monitoring (performance metrics, data drift, model quality)
- **Work from backlog tasks**: Pick task, assign self, check ACs progressively

---

#### Principal Frontend Code Reviewer (@frontend-code-reviewer)
**Role**: Reviews frontend code for quality, performance, and accessibility

**Review Focus**:
- Functionality (correctness, edge cases, error handling, Hook rules)
- Performance (re-renders, bundle size, code splitting, memoization, Web Vitals)
- Accessibility (WCAG 2.1 AA compliance, semantic HTML, keyboard navigation, ARIA)
- Code quality (readability, TypeScript types, component architecture)
- Testing (coverage, test quality, integration tests)
- Security (XSS prevention, input validation, dependency vulnerabilities)

**Philosophy**:
- Constructive and educational
- Explain the "why" behind suggestions
- Balance idealism with practical constraints
- Categorize feedback by severity (Critical/High/Medium/Low)

**Invoked By**: `/jpspec:implement` (after Frontend Engineer)

**Responsibilities**:
- Comprehensive code review across 6 dimensions
- **Validate backlog AC completion**: Verify each checked AC has corresponding code
- **Uncheck ACs if not satisfied**: `backlog task edit <id> --uncheck-ac <N>`
- Add review notes to backlog task
- Categorized feedback with actionable suggestions

---

#### Principal Backend Code Reviewer (@backend-code-reviewer)
**Role**: Reviews backend code for security, performance, and quality

**Review Focus**:
- **Code Hygiene (CRITICAL - BLOCKS MERGE)**:
  - Unused imports - MUST be zero (run `ruff check --select F401` for Python)
  - Unused variables - MUST be zero
  - No exceptions allowed
- **Defensive Coding (CRITICAL - BLOCKS MERGE)**:
  - Input validation at boundaries - REQUIRED
  - Type annotations on public functions - REQUIRED (especially Python)
  - Explicit None/null handling - REQUIRED
  - No ignored errors - REQUIRED (especially Go's `_` pattern)
- Security (auth/authz, injection prevention, secrets management)
- Performance (database optimization, N+1 queries, scalability)
- Code quality (readability, error handling, type safety)
- API design (RESTful/GraphQL patterns, versioning, error responses)
- Database (schema design, migrations, query efficiency)
- Testing (coverage, integration tests, edge cases)

**Philosophy**:
- Security and code hygiene are non-negotiable
- Block merge for any unused import/variable
- Constructive feedback with examples
- Always explain rationale

**Invoked By**: `/jpspec:implement` (after Backend Engineer)

**Responsibilities**:
- Comprehensive code review with mandatory hygiene checks
- **BLOCK MERGE if**: Any unused import/variable, missing validation, missing type annotations, ignored errors
- **Validate backlog AC completion**: Verify each checked AC has corresponding code
- **Uncheck ACs if not satisfied**: `backlog task edit <id> --uncheck-ac <N>`
- Categorized feedback (Critical blocks merge, High/Medium/Low)
- Add review notes to backlog task with specific examples

---

#### Quality Guardian (@quality-guardian)
**Role**: Protects system integrity through comprehensive testing

**Philosophy**:
- Constructive skepticism (question everything with intent to improve)
- Risk intelligence (see failures as opportunities for resilience)
- User-centric (champion end user experience)
- Long-term thinking (consider maintenance, evolution, technical debt)
- Security-first (every feature is a potential vulnerability)

**Framework**:
- Failure Imagination Exercise (list failure modes, assess impact/likelihood, plan detection/recovery)
- Edge Case Exploration (test at zero, infinity, malformed input, extreme load, hostile users)
- Three-Layer Critique (acknowledge value → identify risk → suggest mitigation)
- Risk Classification (Critical/High/Medium/Low)

**Invoked By**: `/jpspec:validate` (parallel with Secure-by-Design Engineer)

**Responsibilities**:
- Functional testing and **backlog AC validation** (mark ACs complete as validation succeeds)
- API and contract testing (endpoints, responses, errors)
- Integration testing (frontend-backend, third-party services, database)
- Performance testing (load, stress, latency p50/p95/p99, resource utilization)
- Non-functional requirements (accessibility WCAG 2.1 AA, cross-browser, mobile, i18n)
- Risk analysis (failure modes, impact/likelihood, monitoring, rollback)
- Comprehensive test report with quality metrics and recommendations

---

#### Secure-by-Design Engineer (@secure-by-design-engineer)
**Role**: Ensures security throughout the development lifecycle

**Philosophy**:
- Assume breach (design as if systems will be compromised)
- Defense in depth (multiple security layers)
- Principle of least privilege (minimum necessary access)
- Fail securely (failures don't compromise security)
- Security by default (secure out of the box)

**Framework**:
- Risk assessment (identify assets, threats, business impact)
- Threat modeling (assets, threats, attack vectors)
- Architecture analysis (security weaknesses in design)
- Severity classification (Critical: auth bypass, SQL injection, RCE; High: XSS, privilege escalation)

**Invoked By**: `/jpspec:validate` (parallel with Quality Guardian)

**Responsibilities**:
- Code security review (auth/authz, input validation, injection prevention, XSS/CSRF, error handling)
- Dependency security (CVE scanning, license checks, supply chain security, SBOM review)
- Infrastructure security (secrets management, network security, access controls, encryption, container security)
- Compliance (GDPR, SOC2, industry-specific regulations, data privacy)
- Threat modeling (attack vectors, exploitability, security controls, defense in depth)
- Penetration testing (manual security testing, automated scanning, auth bypass attempts, authorization escalation)
- **Validate security ACs in backlog tasks**: Update task notes with security findings
- Security report with findings by severity and remediation steps

---

#### Senior Technical Writer (@tech-writer)
**Role**: Creates clear, accurate technical documentation

**Expertise**:
- API documentation (REST/GraphQL endpoints, parameters, examples)
- User guides (getting started, tutorials, how-to guides)
- Technical documentation (architecture, components, configuration, deployment)
- Release notes (features, breaking changes, migration guides)
- Operational documentation (runbooks, monitoring, troubleshooting)

**Quality Standards**:
- Clear structure and hierarchy
- Audience-appropriate language
- Tested, working examples
- Comprehensive but concise
- Searchable and navigable
- Accessible (alt text, headings)

**Invoked By**: `/jpspec:validate` (after QA + Security)

**Responsibilities**:
- API documentation (endpoints, request/response examples, auth, error codes, rate limiting)
- User documentation (feature overview, getting started, tutorials, screenshots/diagrams, troubleshooting)
- Technical documentation (architecture, components, configuration, deployment, monitoring)
- Release notes (feature summary, breaking changes, migration guide, limitations, bug fixes)
- Internal documentation (code comments, runbooks, incident response, rollback)
- **Create documentation tasks in backlog**: Track major doc work
- Ensure all docs are accurate, clear, well-formatted, and accessible

---

#### Senior Release Manager (@release-manager)
**Role**: Orchestrates safe, reliable software releases with human approval gates

**Expertise**:
- Release coordination across teams
- Quality validation (ensuring production standards)
- Risk management and mitigation
- Deployment orchestration
- Rollback planning

**Framework**:
- Pre-release validation checklist (build, tests, reviews, security, performance, docs, monitoring, rollback)
- Release types (Major/Minor/Patch/Hotfix - all require human approval)
- Deployment strategy (canary, blue-green, feature flags, staged rollout)

**Critical Responsibility**:
**ALL production releases require explicit human approval** - No exceptions.

**Invoked By**: `/jpspec:validate` (after Tech Writer, final gate)

**Responsibilities**:
- **Definition of Done verification** (all ACs checked, implementation notes added, tests passing, code reviewed)
- Pre-release validation (review all quality gates, verify critical/high issues resolved, check coverage/security/docs)
- Release planning (determine release type, plan deployment strategy, schedule window, identify stakeholders, prepare rollback)
- Risk assessment (deployment risks, user impact, rollback complexity, monitoring readiness)
- Release checklist verification (CI/CD passing, reviews complete, no critical issues, performance met, docs updated, monitoring configured)
- **Human approval request** with release summary, quality metrics, security status, risk assessment, deployment plan
- Post-approval coordination (deployment execution, monitoring, validation, documentation)
- **Mark backlog tasks as Done** only after ALL Definition of Done criteria verified

---

#### Principal Site Reliability Engineer (@sre-agent)
**Role**: Establishes operational infrastructure and reliability practices

**Expertise**:
- CI/CD excellence (automated, reliable pipelines)
- Kubernetes operations (container orchestration at scale)
- DevSecOps (security integrated throughout operations)
- Observability (comprehensive monitoring, logging, tracing)
- Reliability engineering (SLOs, error budgets, incident management)

**SRE Principles**:
- Service Level Objectives (define SLIs, set SLOs with error budgets, track usage)
- Eliminating Toil (automate manual work, target <50% time on toil, build self-service)
- Embrace Risk (perfect reliability not the goal, use error budgets to balance reliability with velocity)

**Invoked By**: `/jpspec:operate`

**Responsibilities**:
- SLO definition (SLIs for availability/latency/throughput/error rate, SLO targets, error budgets)
- CI/CD pipeline (use stack-specific templates, build/test/deploy automation, SBOM generation, digest verification)
- Kubernetes architecture (multi-AZ HA, node pools, auto-scaling, deployment manifests, resource management, security)
- DevSecOps (SAST/DAST/SCA, SBOM, SLSA compliance, secret management, compliance automation)
- Observability stack (Prometheus/OpenTelemetry metrics, structured logging, distributed tracing, Grafana dashboards, AlertManager)
- Incident management (incident response process, **runbooks**, post-mortems)
- Infrastructure as Code (Terraform/K8s manifests, GitOps, drift detection)
- Performance and scalability (horizontal scaling, caching, optimization)
- Disaster recovery (backup strategy, DR planning, chaos engineering)
- **Create operational tasks in backlog** (CI/CD, K8s, observability, security, IaC)
- **Create runbook tasks** for each alert type

---

## Workflow Patterns

### Sequential vs. Parallel Execution

The /jpspec system uses two execution patterns based on agent dependencies and optimization goals:

#### Sequential Execution

**When Used**:
- Output of one agent feeds into another
- Later agent needs complete context from earlier agent
- Decision gates between phases

**Examples**:
1. **`/jpspec:research`**:
   ```
   Researcher → Business Validator
   ```
   - Researcher gathers market intelligence, competitive analysis, technical feasibility
   - Business Validator uses research findings to assess viability and provide Go/No-Go recommendation
   - Sequential because validator needs complete research context

2. **`/jpspec:validate`**:
   ```
   (QA + Security in parallel) → Tech Writer → Release Manager
   ```
   - Phase 1: QA and Security run in parallel (independent validation)
   - Phase 2: Tech Writer waits for validation results to document findings
   - Phase 3: Release Manager waits for all validation and docs to assess readiness
   - Sequential phases because each depends on previous completion

**Rationale**:
- Ensures data dependencies are met
- Provides clear decision points
- Allows earlier agent output to inform later agent work
- Enables quality gates (validation → documentation → approval)

---

#### Parallel Execution

**When Used**:
- Agents work independently on separate areas
- No data dependencies between agents
- Maximize throughput and minimize wall-clock time

**Examples**:
1. **`/jpspec:plan`**:
   ```
   Software Architect ∥ Platform Engineer
   (parallel execution, then consolidated)
   ```
   - Software Architect: System architecture, component design, ADRs, integration patterns
   - Platform Engineer: CI/CD, infrastructure, DevSecOps, observability
   - Parallel because they work on different layers (application vs. platform)
   - Consolidated after both complete to ensure alignment and resolve conflicts

2. **`/jpspec:implement`**:
   ```
   Frontend Engineer ∥ Backend Engineer ∥ AI/ML Engineer (optional)
   (parallel implementation, then sequential code review)
   ```
   - Frontend: UI components, state management, styling, frontend tests
   - Backend: APIs, business logic, database, backend tests
   - AI/ML: Model training, MLOps, inference, monitoring (if needed)
   - Parallel because they work on different codebases with defined contracts (API specs)
   - Code review is sequential after implementation completes

3. **`/jpspec:validate` Phase 1**:
   ```
   Quality Guardian ∥ Secure-by-Design Engineer
   (parallel validation, then results feed into Tech Writer)
   ```
   - QA: Functional, integration, performance, accessibility testing
   - Security: Code review, dependency scanning, infrastructure security, compliance
   - Parallel because they validate different aspects independently
   - Results consolidated before documentation phase

**Rationale**:
- Maximize developer velocity (reduce wall-clock time)
- Enable specialization (each agent focuses on their domain)
- Prevent bottlenecks (no waiting for sequential completion)
- Optimize resource utilization (agents can run concurrently)

**Design Principle**: Use parallel execution when agents are independent; use sequential when later agents need earlier context.

---

### Design→Implement Workflow

The /jpspec system enforces a critical separation between design (task creation) and implementation (task execution):

**Design Commands** (Produce Tasks):
- `/jpspec:specify` - PM Planner creates implementation tasks in PRD section 6
- `/jpspec:research` - Research and Business Validator create follow-up tasks
- `/jpspec:plan` - Architect and Platform Engineer create architecture/infrastructure tasks

**Implementation Commands** (Consume Tasks):
- `/jpspec:implement` - Engineers pick tasks from backlog and implement
- `/jpspec:validate` - Validators verify task completion
- `/jpspec:operate` - SRE implements operational tasks

**Critical Rule**: Never run `/jpspec:implement` without first running `/jpspec:specify` to create implementation tasks.

**Verification Pattern**:
```bash
# After design command, verify tasks were created
backlog task list --plain | grep -i "<feature-keyword>"

# If no tasks found, design command is incomplete
# If tasks exist, ready for implementation
```

**Why This Matters**:
- Ensures all implementation work is tracked
- Provides clear acceptance criteria before coding starts
- Enables progress tracking and estimation
- Prevents scope creep (only implement what's in tasks)
- Maintains traceability from requirements to implementation

---

### Backlog Task State Transitions

Tasks flow through states as /jpspec commands execute:

```
To Do → Specified → Researched → Planned → In Implementation → Validated → Deployed → Done
         (specify)  (research)   (plan)   (implement)        (validate)  (operate)
```

**State Semantics**:
- **To Do**: Task created, no work started
- **Specified**: PRD complete, implementation tasks created
- **Researched**: Market research and business validation complete
- **Planned**: Architecture and platform design complete
- **In Implementation**: Engineers actively coding
- **Validated**: QA, security, and docs complete
- **Deployed**: Operational infrastructure deployed
- **Done**: All work complete, all ACs checked

**Valid Transitions**:
- `/jpspec:specify` can run on "To Do" tasks → moves to "Specified"
- `/jpspec:research` can run on "Specified" tasks → moves to "Researched"
- `/jpspec:plan` can run on "Researched" (or "Specified") tasks → moves to "Planned"
- `/jpspec:implement` can run on "Planned" tasks → moves to "In Implementation"
- `/jpspec:validate` can run on "In Implementation" tasks → moves to "Validated"
- `/jpspec:operate` can run on "Validated" tasks → moves to "Deployed"
- Release Manager marks tasks as "Done" after Definition of Done verified

**Invalid Transitions** (will error):
- Running `/jpspec:implement` on "To Do" task (must run `/jpspec:specify` first)
- Running `/jpspec:validate` on "Planned" task (must run `/jpspec:implement` first)
- Skipping required phases breaks traceability

---

## Use Case Examples

### Use Case 1: Simple Bug Fix (Skip Workflow)

**Scenario**: Button alignment issue on login page (CSS fix, 20 lines of code).

**Complexity Assessment** (`/jpspec:assess`):
- Q1: LOC? A (20 lines CSS)
- Q2: Modules? A (1 component)
- Q3: Integrations? A (None)
- Q4: Data? A (No persistence)
- Q5: Team? A (Solo)
- Q6: Cross-functional? A (Engineering only)
- Q7: Technical? A (Well-known)
- Q8: Business impact? A (Low)

**Total Score**: 8/32 (Simple)

**Recommendation**: Skip SDD, implement directly

**Workflow**:
```bash
# Create simple task in backlog
backlog task create "Fix button alignment on login page" \
  -d "Align submit button to center of form" \
  --ac "Button centered on all screen sizes" \
  --ac "Visual regression test added" \
  -l bugfix,frontend \
  --priority medium

# Implement directly (no /jpspec commands needed)
# Mark task Done when complete
```

**Why Skip Workflow**:
- Problem and solution are well-understood
- No coordination required
- Minimal risk
- Specification overhead would slow delivery

---

### Use Case 2: New API Endpoint (Spec-Light Mode)

**Scenario**: Add user preferences API endpoint (200 lines, database changes, 2 developers).

**Complexity Assessment** (`/jpspec:assess`):
- Q1: LOC? B (200 lines)
- Q2: Modules? B (API + DB + Client)
- Q3: Integrations? B (Database + Cache)
- Q4: Data? C (New tables + migrations)
- Q5: Team? B (2 developers)
- Q6: Cross-functional? A (Engineering only)
- Q7: Technical? A (Standard REST API)
- Q8: Business impact? B (User experience)

**Total Score**: 15/32 (Medium)

**Recommendation**: Spec-Light Mode

**Workflow**:
```bash
# 1. Create lightweight specification
/jpspec:specify User preferences API endpoint

# Agent creates PRD with:
# - Problem statement and user stories
# - API contract definition
# - Database schema changes
# - Acceptance criteria
# - Implementation tasks in backlog

# 2. Skip research (well-understood technical approach)

# 3. Skip full planning (standard architecture)

# 4. Implement directly
/jpspec:implement User preferences API

# Engineers work from backlog tasks created by /jpspec:specify

# 5. Standard code review and merge
```

**Why Spec-Light**:
- Captures key decisions without excessive documentation
- Enables team alignment (2 developers need coordination)
- Database changes require planning
- Standard patterns don't require full architecture phase
- Low business risk allows skipping validation phase

---

### Use Case 3: Payment Integration (Full SDD Workflow)

**Scenario**: Integrate Stripe payment processing (1000+ lines, 4-5 developers, revenue-critical, PCI compliance).

**Complexity Assessment** (`/jpspec:assess`):
- Q1: LOC? C (1000+ lines)
- Q2: Modules? C (Payment service, UI, webhooks, admin)
- Q3: Integrations? C (Stripe, database, email, analytics)
- Q4: Data? D (Complex transactions, PCI compliance)
- Q5: Team? C (4-5 developers)
- Q6: Cross-functional? D (Eng, Product, Legal, Security)
- Q7: Technical? C (Multiple spikes needed)
- Q8: Business impact? D (Revenue-critical, PCI compliance)

**Total Score**: 27/32 (Complex)

**Recommendation**: Full SDD Workflow

**Workflow**:
```bash
# 1. Assess complexity
/jpspec:assess Stripe payment integration
# Output: Complex (27/32) → Recommend Full SDD

# 2. Create comprehensive specification
/jpspec:specify Stripe payment processing integration

# PM Planner creates comprehensive PRD with:
# - Executive summary (problem, solution, success metrics)
# - User stories (checkout flow, payment methods, error handling)
# - DVF+V risk assessment (business viability, technical feasibility, compliance)
# - Functional requirements (API integration, webhooks, admin dashboard)
# - Non-functional requirements (PCI DSS compliance, performance, security)
# - Implementation tasks in backlog (30+ tasks created)
# - Acceptance criteria (extensive test scenarios)

# 3. Conduct research and validation
/jpspec:research Payment processing and PCI compliance requirements

# Researcher output:
# - Market analysis (payment processor comparison)
# - Competitive landscape (Stripe vs. PayPal vs. Adyen)
# - Technical feasibility (webhook handling, retry logic, error scenarios)
# - Compliance requirements (PCI DSS Level 1, data security)

# Business Validator output:
# - Financial viability (transaction fees, revenue impact)
# - Risk assessment (payment failures, fraud, chargebacks)
# - Recommendation: Go (with compliance requirements)

# 4. Architecture and platform planning
/jpspec:plan Payment processing microservice with Stripe integration

# Software Architect (parallel):
# - System architecture (payment service, webhook processor, admin UI)
# - Integration patterns (idempotent APIs, retry logic, circuit breakers)
# - ADRs (Stripe vs. alternatives, webhook vs. polling, PCI compliance approach)
# - Data flow (payment intent → processing → confirmation → reconciliation)

# Platform Engineer (parallel):
# - CI/CD with security scanning (SAST, secrets detection)
# - Kubernetes deployment (PCI-compliant network policies)
# - DevSecOps (encrypted secrets, audit logging, SBOM)
# - Observability (payment success/failure metrics, webhook latency, error rates)

# Consolidated output:
# - Complete architecture document
# - /speckit.constitution updated with payment service principles
# - 15+ architecture/infrastructure tasks created

# 5. Implementation with code review
/jpspec:implement Stripe payment integration

# Frontend Engineer:
# - Payment form with Stripe Elements
# - Checkout flow UI
# - Error handling and retry UX
# - Accessibility (WCAG 2.1 AA)

# Backend Engineer:
# - Payment service API (create payment intent, confirm payment)
# - Webhook handler (payment_intent.succeeded, payment_intent.failed)
# - Database schema (payments, transactions, webhooks)
# - Idempotency and retry logic
# - PCI compliance (no card data storage, tokenization)

# Code Reviewers:
# - Frontend: Verify secure handling of Stripe tokens, accessibility
# - Backend: CRITICAL security review (no card data in logs, webhook signature validation, idempotency keys)

# 6. Comprehensive validation
/jpspec:validate Stripe payment integration

# Quality Guardian:
# - Functional testing (successful payments, failed payments, refunds)
# - Integration testing (Stripe test mode, webhook delivery)
# - Performance testing (payment latency, webhook processing)
# - Edge cases (network failures, duplicate webhooks, race conditions)

# Secure-by-Design Engineer:
# - Security review (webhook signature validation, HTTPS enforcement, no sensitive data in logs)
# - Dependency scanning (Stripe SDK vulnerabilities)
# - PCI DSS compliance checklist (no card data storage, secure transmission, audit logging)
# - Penetration testing (payment manipulation attempts, webhook spoofing)

# Technical Writer:
# - API documentation (payment endpoints, webhook events, error codes)
# - User guide (checkout process, payment methods, troubleshooting)
# - Runbook (payment failures, webhook processing issues, reconciliation)

# Release Manager:
# - Verify all 30+ tasks complete with ACs checked
# - Review security assessment (PCI compliance verified)
# - Deployment plan (staged rollout, feature flag, monitoring)
# - Human approval request (executive sign-off for revenue-critical feature)

# 7. Operational deployment
/jpspec:operate Stripe payment service infrastructure

# SRE Agent:
# - SLOs (99.95% payment API availability, <500ms p95 latency, <1% error rate)
# - CI/CD pipeline (security scanning, PCI compliance checks, SBOM generation)
# - Kubernetes deployment (PCI-compliant network policies, encrypted secrets)
# - Observability (payment success/failure dashboards, webhook latency alerts, error tracking)
# - Incident response (payment failure runbook, webhook retry runbook)
# - Disaster recovery (payment data backup, reconciliation procedures)

# Deployment:
# - Staged rollout (1% → 10% → 50% → 100%)
# - Monitoring (payment success rate, webhook delivery rate, error alerts)
# - Validation (test transactions, webhook processing verification)
```

**Why Full SDD**:
- High coordination overhead (4-5 developers, cross-functional team)
- Revenue-critical (payment failures directly impact business)
- PCI compliance requirements (legal/regulatory mandates)
- Complex architecture (payment service, webhooks, admin, reconciliation)
- High technical risk (payment processing, error handling, idempotency)
- Multiple stakeholders (Engineering, Product, Legal, Security, Finance)

**Outcome**:
- Comprehensive documentation (PRD, architecture, ADRs, runbooks)
- All risks identified and mitigated (DVF+V assessment, security review)
- PCI compliance verified (security assessment, audit logging)
- Production-ready deployment (CI/CD, observability, incident response)
- Full traceability (30+ tasks with ACs, all tracked in backlog)

---

### Use Case 4: Microservices Refactoring (Architecture-Heavy)

**Scenario**: Refactor monolith into microservices (2000+ lines, 7+ developers, system-wide change).

**Workflow**:
```bash
# 1. Assess complexity
/jpspec:assess Refactor monolith to microservices architecture
# Output: Complex (30/32) → Full SDD required

# 2. Specification (focuses on outcomes and constraints)
/jpspec:specify Microservices migration for user and order domains

# PM Planner creates PRD with:
# - Executive summary (reduce deployment coupling, enable team autonomy)
# - Migration strategy (strangler fig pattern, incremental rollout)
# - Service boundaries (user service, order service, shared services)
# - Success metrics (deployment frequency, lead time, service availability)

# 3. Skip research (internal refactoring, no market validation needed)

# 4. CRITICAL: Extensive architecture planning
/jpspec:plan Microservices architecture and migration strategy

# Software Architect:
# - Service decomposition (bounded contexts, domain models)
# - ADRs (synchronous vs async communication, data consistency, service discovery)
# - Integration patterns (API Gateway, Event Bus, Saga pattern for distributed transactions)
# - Migration strategy (strangler fig, database decomposition, API versioning)

# Platform Engineer:
# - Kubernetes architecture (service mesh, network policies, service discovery)
# - CI/CD per service (independent pipelines, contract testing)
# - Observability (distributed tracing, service dependency mapping, cross-service alerts)
# - DevSecOps (service-to-service auth, secrets per service, audit logging)

# 5. Phased implementation
/jpspec:implement User service extraction (Phase 1)

# Backend Engineers (multiple):
# - Extract user service (API, database, business logic)
# - Implement API Gateway
# - Database migration (user tables to user service DB)
# - Contract tests (ensure backward compatibility)

# Repeat for order service, payment service, etc.

# 6. Rigorous validation
/jpspec:validate Microservices migration Phase 1

# QA: Integration testing (cross-service calls, API Gateway routing, distributed transactions)
# Security: Service-to-service auth, network policies, secrets management
# Tech Writer: Architecture docs, service APIs, migration runbooks

# 7. Operational excellence
/jpspec:operate Microservices platform infrastructure

# SRE:
# - Kubernetes service mesh (Istio/Linkerd for traffic management)
# - Distributed tracing (Jaeger/Zipkin for cross-service debugging)
# - Service-level SLOs (per service availability, latency, error rate)
# - Incident response (service dependency runbook, cascading failure procedures)
```

**Why Architecture-Heavy**:
- System-wide change affects all services
- Requires extensive planning (service boundaries, data decomposition, migration strategy)
- High coordination (7+ developers working across services)
- ADRs critical (decisions impact entire system long-term)
- Observability essential (distributed tracing, service dependency mapping)

---

### Use Case 5: Machine Learning Feature (AI/ML-Heavy)

**Scenario**: Recommendation engine for e-commerce (ML model, data pipeline, inference API).

**Workflow**:
```bash
# 1. Assess and specify
/jpspec:assess Product recommendation engine
# Output: Complex (24/32) → Full SDD

/jpspec:specify ML-powered product recommendations

# 2. Research and validation
/jpspec:research Recommendation algorithms and personalization strategies

# Researcher:
# - Collaborative filtering vs content-based vs hybrid approaches
# - Cold-start problem solutions
# - Real-time vs batch recommendations

# Business Validator:
# - Revenue impact (estimated conversion rate lift)
# - Personalization vs privacy trade-offs
# - Recommendation: Go (with phased rollout for measurement)

# 3. Planning with ML architecture
/jpspec:plan Recommendation engine architecture

# Software Architect:
# - ML architecture (training pipeline, feature store, inference service, feedback loop)
# - ADRs (batch vs real-time inference, model serving approach, A/B testing framework)

# Platform Engineer:
# - MLOps infrastructure (MLflow, model registry, experiment tracking)
# - CI/CD for ML (model training pipeline, model validation, staged deployment)
# - Observability (model performance metrics, prediction latency, data drift detection)

# 4. Implementation with ML engineer
/jpspec:implement Recommendation engine ML model and API

# AI/ML Engineer:
# - Training pipeline (data preprocessing, feature engineering, model training)
# - Model evaluation (offline metrics: precision@k, recall@k, NDCG)
# - Model deployment (inference service, A/B testing, canary deployment)
# - Monitoring (model performance, data drift, concept drift)

# Backend Engineer:
# - Recommendation API (fetch recommendations, log impressions/clicks)
# - Feature store integration
# - Caching layer (pre-computed recommendations)

# Frontend Engineer:
# - Recommendation widget UI
# - Impression and click tracking
# - A/B test integration

# 5. Validation with ML-specific testing
/jpspec:validate Recommendation engine

# QA:
# - Functional testing (recommendations generated, personalized per user)
# - Performance testing (inference latency <100ms p95)
# - A/B test setup (control vs treatment groups)

# Security:
# - User data privacy (GDPR compliance, data anonymization)
# - Model security (adversarial examples, model extraction attacks)

# 6. MLOps and monitoring
/jpspec:operate Recommendation engine ML infrastructure

# SRE:
# - ML-specific SLOs (model accuracy >X%, inference latency <Yms, data freshness <Zhours)
# - Model monitoring (prediction distribution, drift detection, performance degradation alerts)
# - Retraining pipeline (automated retraining on drift detection)
# - A/B testing infrastructure (feature flags, experimentation platform)
# - Incident response (model degradation runbook, rollback to previous model version)
```

**Why ML-Heavy**:
- Requires ML-specific architecture (training pipeline, feature store, inference, monitoring)
- Model performance metrics differ from software metrics (precision, recall, drift)
- MLOps infrastructure needed (experiment tracking, model registry, automated retraining)
- A/B testing essential (measure business impact, validate model improvements)
- Continuous monitoring (data drift, concept drift, model degradation)

---

## Integration with Backlog Tasks

The /jpspec workflow system is tightly integrated with backlog.md for comprehensive task lifecycle management.

### Task Creation

**Design Commands Create Tasks**:

1. **`/jpspec:specify`** - PM Planner creates implementation tasks in PRD section 6:
   ```bash
   backlog task create "Implement user authentication" \
     -d "Core auth implementation per PRD section 4" \
     --ac "Implement OAuth2 flow" \
     --ac "Add JWT token validation" \
     --ac "Write unit tests" \
     -a @pm-planner \
     -l implement,backend \
     --priority high
   ```

2. **`/jpspec:research`** - Researchers create follow-up tasks:
   ```bash
   backlog task create "Implement OAuth2 with Google provider" \
     -d "Implementation based on research findings" \
     --ac "Implement approach recommended in research report" \
     --ac "Address feasibility concerns from validation" \
     -l implement,research-followup \
     --priority high
   ```

3. **`/jpspec:plan`** - Architects and Platform Engineers create design/infrastructure tasks:
   ```bash
   # Architecture tasks
   backlog task create "ADR: OAuth2 vs SAML decision" \
     -d "Document authentication protocol decision" \
     --ac "Document context, options, decision, consequences" \
     -l architecture,adr \
     --priority high

   # Infrastructure tasks
   backlog task create "Setup CI/CD pipeline for auth service" \
     -d "Implement automated build, test, deployment" \
     --ac "Configure build pipeline with caching" \
     --ac "Setup security scanning" \
     -l infrastructure,cicd \
     --priority high
   ```

### Task Discovery

**Implementation Commands Discover Tasks**:

Before executing, implementation commands search for existing tasks:

```bash
# /jpspec:implement discovers tasks
backlog search "authentication" --plain
backlog task list -s "To Do" --plain

# /jpspec:validate discovers tasks ready for validation
backlog task list -s "In Progress" --plain
backlog task list -s "Done" --plain

# /jpspec:operate discovers operational tasks
backlog search "infrastructure" --plain
backlog task list -l infrastructure --plain
```

**Critical Rule**: `/jpspec:implement` will ERROR if no tasks are found. Always run `/jpspec:specify` first.

### Task Execution Workflow

**Engineers follow strict workflow**:

```bash
# 1. Pick a task (review details)
backlog task 42 --plain

# 2. Assign yourself and set status to In Progress
backlog task edit 42 -s "In Progress" -a @backend-engineer

# 3. Add implementation plan
backlog task edit 42 --plan $'1. Implement OAuth2 flow
2. Add JWT token generation
3. Implement token validation
4. Write unit tests
5. Integration testing'

# 4. Check ACs progressively as you complete them
backlog task edit 42 --check-ac 1  # After OAuth2 flow
backlog task edit 42 --check-ac 2  # After JWT generation
backlog task edit 42 --check-ac 3  # After token validation

# 5. Add implementation notes
backlog task edit 42 --notes $'Implemented OAuth2 with Google provider

Key changes:
- src/auth/oauth.ts - OAuth2 flow implementation
- src/auth/jwt.ts - JWT token generation and validation
- tests/auth/oauth.test.ts - Unit tests (95% coverage)

Trade-offs:
- Used short-lived tokens (15min) for security
- Implemented refresh token rotation per IETF best practices'

# 6. Verify all ACs are checked before marking Done
backlog task 42 --plain  # Ensure all ACs show [x]
```

### Code Reviewer Validation

**Code reviewers verify AC completion**:

```bash
# 1. Review task ACs
backlog task 42 --plain

# 2. Verify each checked AC has corresponding code
# If AC is checked but code doesn't implement it:

# 3. Uncheck AC if not satisfied
backlog task edit 42 --uncheck-ac 2  # JWT generation incomplete

# 4. Add review notes
backlog task edit 42 --append-notes $'Code Review (Backend):

Issues:
- AC #2: JWT generation lacks expiration claim
- Missing input validation on token payload

Suggestions:
- Add "exp" claim to JWT payload
- Validate token payload structure before signing'

# Engineer fixes issues, re-checks AC when complete
```

### Quality Guardian and Security Validation

**Validators mark ACs complete during testing**:

```bash
# Quality Guardian validates functional ACs
backlog task edit 42 --check-ac 4  # After unit tests pass
backlog task edit 42 --append-notes 'QA Testing:
- All unit tests passing (95% coverage)
- Integration tests passing
- Edge cases tested (expired tokens, invalid signatures)'

# Security Engineer validates security ACs
backlog task edit 42 --append-notes 'Security Review:
- OAuth2 flow follows IETF RFC 6749
- JWT tokens signed with RS256 (secure)
- Token expiration properly enforced
- Refresh token rotation implemented
- No security issues found'
```

### Release Manager Definition of Done

**Release Manager verifies Definition of Done before marking tasks Done**:

```bash
# 1. Review task for completeness
backlog task 42 --plain

# 2. Verify Definition of Done checklist:
# ✅ All acceptance criteria checked ([x])
# ✅ Implementation notes added
# ✅ Tests passing (verified by QA)
# ✅ Code reviewed (verified by reviewer notes)

# 3. Only then mark as Done
backlog task edit 42 -s Done

# If any checklist item fails, DO NOT mark as Done
# Instead, add notes explaining what's missing
backlog task edit 42 --append-notes 'Release Gate: Not Ready
Missing:
- AC #3 not checked (token validation incomplete)
- Integration test failures (see CI logs)
Action: Fix issues before re-submitting for release'
```

### Task Lifecycle States

Tasks transition through states as /jpspec commands execute:

```
To Do (created by design commands)
  ↓
In Progress (engineer assigns self and starts work)
  ↓
Code Review (reviewers validate, may uncheck ACs)
  ↓
In Progress (engineer fixes review issues)
  ↓
Validation (QA and Security validate and check ACs)
  ↓
Done (Release Manager verifies Definition of Done)
```

### Traceability

**Full traceability from requirements to implementation**:

```
PRD Section 4 (Functional Requirements)
  ↓ (specified in)
User Story: "As a user, I want to sign in with Google"
  ↓ (decomposed into)
task-42: "Implement OAuth2 with Google provider"
  ↓ (tracked with)
Acceptance Criteria:
  [x] AC #1: Implement OAuth2 flow
  [x] AC #2: Add JWT token generation
  [x] AC #3: Implement token validation
  [x] AC #4: Write unit tests (95% coverage)
  ↓ (validated by)
Implementation Notes: "Implemented OAuth2 with RS256 signing..."
Code Review Notes: "Security review passed..."
QA Testing Notes: "All tests passing..."
  ↓ (resulted in)
Feature Deployed: Users can sign in with Google
```

---

## Best Practices

### When to Use Which Command

**Decision Tree**:

```
Start: New feature request
  ↓
Run /jpspec:assess
  ↓
Complexity Score?
  ├─ 8-12 (Simple) → Skip workflow, implement directly
  ├─ 13-20 (Medium) → Spec-Light: /jpspec:specify → /jpspec:implement
  └─ 21-32 (Complex) → Full SDD workflow (all 7 commands)
```

**Specific Scenarios**:

| Scenario | Commands to Use | Rationale |
|----------|----------------|-----------|
| Bug fix with known solution | None (direct implementation) | Problem and solution well-understood |
| New UI component (moderate complexity) | `specify` → `implement` | Spec-Light: Need clear acceptance criteria, skip research/planning |
| New API endpoint with external integration | `specify` → `plan` → `implement` | Need architecture planning for integration patterns |
| Business-critical feature with market uncertainty | `specify` → `research` → `plan` → `implement` → `validate` → `operate` | Full workflow: validate business case, ensure quality gates |
| System-wide architectural change | `specify` → `plan` (heavy) → `implement` → `validate` → `operate` | Architecture-heavy: ADRs critical, extensive planning |
| Production deployment readiness | `validate` → `operate` | Validation and operational setup for existing implementation |

---

### Optimizing for Speed

**Parallel Execution**:
- Use `/jpspec:plan` parallel mode (Software Architect + Platform Engineer simultaneously)
- Use `/jpspec:implement` parallel mode (Frontend + Backend + AI/ML simultaneously)
- Use `/jpspec:validate` Phase 1 parallel mode (QA + Security simultaneously)

**Skip Optional Phases**:
- Skip `/jpspec:research` if business case is clear
- Skip `/jpspec:plan` for simple features using standard patterns
- Skip `/jpspec:validate` for low-risk internal tools (not recommended for production)

**Spec-Light Mode**:
- For medium complexity (13-20 score), use only `specify` → `implement`
- Lightweight PRD (1-2 pages) instead of comprehensive 10-section document
- Skip research, planning, and dedicated validation phases
- Rely on standard code review instead of full validation workflow

---

### Ensuring Quality

**Comprehensive Validation**:
- Always run `/jpspec:validate` for production features
- Never skip security review for features handling sensitive data
- Always create runbooks for operational alerts (`/jpspec:operate`)

**Backlog Task Discipline**:
- **Always verify all ACs are checked before marking Done**
- Code reviewers must validate AC completion (uncheck if not satisfied)
- Release Manager must verify Definition of Done before approval
- Implementation notes required (no "Done" without documentation)

**Human Approval Gates**:
- ALL production releases require explicit human approval (Release Manager)
- Critical features require executive sign-off (payment, auth, data security)
- Never skip human approval, even for automated deployments

---

### Team Coordination

**Task Assignment**:
- Design agents assign themselves when creating tasks (`-a @pm-planner`)
- Implementation engineers assign themselves when starting work (`-a @backend-engineer`)
- Clear ownership prevents duplicate work

**Communication**:
- Use task implementation notes to communicate context to other team members
- Code reviewers add review notes for engineers to address
- QA and Security add validation notes for release manager

**Dependencies**:
- Use `--dep` flag to specify task dependencies
- `/jpspec:specify` should link implementation tasks to each other
- Ensures correct ordering (e.g., database migration before API implementation)

---

### Avoiding Common Pitfalls

**Pitfall 1: Running /jpspec:implement without tasks**

❌ **Wrong**:
```bash
/jpspec:implement New authentication system
# ERROR: No backlog tasks found for: New authentication system
```

✅ **Correct**:
```bash
# First create tasks
/jpspec:specify New authentication system

# Verify tasks were created
backlog task list --plain | grep -i "auth"

# Then implement
/jpspec:implement New authentication system
```

**Pitfall 2: Marking tasks Done without verifying Definition of Done**

❌ **Wrong**:
```bash
# Engineer marks task as Done with unchecked ACs
backlog task edit 42 -s Done  # Bad: ACs not verified
```

✅ **Correct**:
```bash
# Verify all ACs are checked
backlog task 42 --plain
# Ensure output shows all ACs with [x]

# Only then mark Done (by Release Manager)
backlog task edit 42 -s Done
```

**Pitfall 3: Skipping code review validation of ACs**

❌ **Wrong**:
```bash
# Engineer checks all ACs, reviewer approves without verifying
# Result: ACs checked but code doesn't implement them
```

✅ **Correct**:
```bash
# Reviewer verifies each checked AC has corresponding code
backlog task 42 --plain

# If AC is checked but code is incomplete:
backlog task edit 42 --uncheck-ac 2
backlog task edit 42 --append-notes 'AC #2 incomplete: Missing token expiration validation'
```

**Pitfall 4: Using wrong execution pattern**

❌ **Wrong**:
```bash
# Running research after implementation (backward workflow)
/jpspec:implement → /jpspec:research  # Too late for research
```

✅ **Correct**:
```bash
# Follow natural workflow progression
/jpspec:specify → /jpspec:research → /jpspec:plan → /jpspec:implement
```

---

## Troubleshooting

### Command Fails: "No backlog tasks found"

**Problem**: `/jpspec:implement` errors because no tasks exist.

**Solution**:
```bash
# 1. Verify you ran /jpspec:specify first
backlog task list --plain | grep -i "<feature-keyword>"

# 2. If no tasks exist, run specify first
/jpspec:specify <feature-description>

# 3. Verify tasks were created
backlog task list --plain

# 4. Then run implement
/jpspec:implement <feature-description>
```

---

### Agent Doesn't Create Tasks

**Problem**: Design agent completes but no tasks appear in backlog.

**Diagnosis**:
```bash
# Check if tasks were created
backlog task list --plain

# Search for tasks related to feature
backlog search "<feature-keyword>" --plain
```

**Solution**:
- Re-run the design command with explicit instruction to create tasks
- Verify agent has backlog CLI instructions in context
- Check agent actually executed `backlog task create` commands (review agent output)

---

### AC Marked Complete but Code Doesn't Implement It

**Problem**: Code reviewer finds checked ACs without corresponding implementation.

**Solution**:
```bash
# Code reviewer unchecks AC
backlog task edit <task-id> --uncheck-ac <N>

# Add review note explaining issue
backlog task edit <task-id> --append-notes 'Code Review: AC #<N> checked but not implemented

Expected: <description>
Actual: <what's missing>
Action: Implement <specific requirement>'

# Engineer fixes and re-checks AC
```

---

### Tasks Stuck in "In Progress"

**Problem**: Tasks remain in "In Progress" for extended time.

**Diagnosis**:
```bash
# List all in-progress tasks
backlog task list -s "In Progress" --plain

# Check specific task status
backlog task <id> --plain
```

**Solution**:
- Review task implementation notes (are there blockers?)
- Check AC completion (how many ACs are checked?)
- Contact assignee for status update
- Consider breaking large tasks into smaller subtasks

---

### Release Manager Can't Approve: Definition of Done Not Met

**Problem**: Release Manager finds tasks missing Definition of Done criteria.

**Diagnosis**:
```bash
# Review task completeness
backlog task <id> --plain

# Check for missing criteria:
# - Are all ACs checked? (look for [ ] instead of [x])
# - Are implementation notes present?
# - Are code review notes present?
# - Are test results documented?
```

**Solution**:
```bash
# Release Manager adds notes explaining what's missing
backlog task edit <id> --append-notes 'Release Gate: Not Ready

Missing:
- AC #3 not checked (token validation incomplete)
- No implementation notes (how was this implemented?)
- No code review notes (was this reviewed?)

Action: Complete missing items before re-submitting for release'

# DO NOT mark as Done until all criteria met
```

---

### Parallel Agents Produce Conflicting Designs

**Problem**: Software Architect and Platform Engineer create incompatible designs.

**Solution**:
- This is expected during parallel execution
- **Integration Phase** explicitly resolves conflicts
- Review both outputs, identify conflicts, and consolidate
- Update /speckit.constitution with unified principles
- Create follow-up tasks to resolve design conflicts if needed

---

### Agent Uses Wrong Identity or Assignee

**Problem**: Agent creates tasks without assigning itself or uses wrong identity.

**Diagnosis**:
```bash
# Check task assignee
backlog task <id> --plain
# Look for "Assignee: @agent-identity"
```

**Solution**:
- Each agent has a specific identity (`@pm-planner`, `@backend-engineer`, etc.)
- Agent context includes "Your Agent Identity" section
- Verify agent used correct identity when creating/updating tasks
- Manually update if needed: `backlog task edit <id> -a @correct-agent`

---

## Advanced Topics

### Customizing the Workflow

The /jpspec workflow can be customized via `jpspec_workflow.yml` configuration:

**Example: Skip Research Phase**
```yaml
workflows:
  specify:
    command: "/jpspec:specify"
    agents: ["product-requirements-manager"]
    input_states: ["To Do"]
    output_state: "Specified"

  # Remove research workflow

  plan:
    command: "/jpspec:plan"
    agents: ["software-architect", "platform-engineer"]
    input_states: ["Specified"]  # Changed from ["Researched"]
    output_state: "Planned"
```

**Example: Add Custom Security Audit Phase**
```yaml
states:
  - name: "Security Audited"
    description: "Security audit completed"

workflows:
  security-audit:
    command: "/jpspec:audit"
    agents: ["secure-by-design-engineer"]
    input_states: ["Validated"]
    output_state: "Security Audited"

transitions:
  - from: "Security Audited"
    to: "Deployed"
    via: "operate"
```

See `docs/guides/workflow-architecture.md` for complete customization guide.

---

### MCP Integration

The /jpspec agents can be accessed via MCP (Model Context Protocol):

**MCP Server**:
- Backlog.md provides MCP server for task management
- Claude Code and other AI assistants can manage tasks via MCP
- See `docs/reference/agent-mcp-integrations.md` for details

**AI-Assisted Execution**:
```bash
# Claude Code can execute backlog commands via MCP
claude> Create a task for implementing user authentication
# Claude uses MCP to: backlog task create "Implement user auth" ...

claude> What tasks are in progress?
# Claude uses MCP to: backlog task list -s "In Progress" --plain
```

---

### Integration with CI/CD

The /jpspec workflow integrates with CI/CD pipelines:

**GitHub Actions Integration**:
```yaml
# .github/workflows/validate.yml
name: Validate
on: [push, pull_request]

jobs:
  jpspec-validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      # Run validation workflow
      - name: Run /jpspec:validate
        run: |
          # Automated QA testing
          pytest tests/

          # Automated security scanning
          trivy scan .

          # Update backlog tasks with results
          backlog task edit $TASK_ID --check-ac 1  # Tests passed
```

---

### Metrics and Analytics

Track workflow effectiveness:

**DORA Metrics**:
- Deployment Frequency: Tasks completed per week
- Lead Time: Time from "To Do" to "Done"
- Change Failure Rate: Tasks reopened after "Done"
- Mean Time to Restore: Time to fix production issues

**Workflow Metrics**:
```bash
# Count tasks by status
backlog task list -s "To Do" --plain | wc -l
backlog task list -s "In Progress" --plain | wc -l
backlog task list -s "Done" --plain | wc -l

# Identify bottlenecks (tasks stuck in specific states)
backlog task list -s "In Progress" --plain  # Long-running tasks?
```

---

## Diagram: /jpspec Workflow

The following diagram shows the complete /jpspec workflow with agent coordination and backlog integration:

![jpspec Workflow Diagram](../diagrams/jpspec-workflow.png)

---

## References

### Documentation
- **Workflow Architecture**: `docs/guides/workflow-architecture.md` - Configuration-driven workflow design
- **Backlog User Guide**: `docs/guides/backlog-user-guide.md` - Task management with backlog.md
- **Agent Loop Classification**: `docs/reference/agent-loop-classification.md` - Inner vs. outer loop agents
- **Inner Loop Principles**: `docs/reference/inner-loop.md` - Fast local iteration
- **Outer Loop Principles**: `docs/reference/outer-loop.md` - Production deployment
- **Agent-MCP Integrations**: `docs/reference/agent-mcp-integrations.md` - MCP integration details

### Command References
- **`/jpspec:assess`**: `.claude/commands/jpspec/assess.md`
- **`/jpspec:specify`**: `.claude/commands/jpspec/specify.md`
- **`/jpspec:research`**: `.claude/commands/jpspec/research.md`
- **`/jpspec:plan`**: `.claude/commands/jpspec/plan.md`
- **`/jpspec:implement`**: `.claude/commands/jpspec/implement.md`
- **`/jpspec:validate`**: `.claude/commands/jpspec/validate.md`
- **`/jpspec:operate`**: `.claude/commands/jpspec/operate.md`

### Frameworks and Principles
- **SVPG Product Operating Model**: Inspired, Empowered, Transformed (Marty Cagan)
- **Gregor Hohpe's Architecture**: Architect Elevator, Enterprise Integration Patterns
- **DORA Metrics**: DevOps Research and Assessment (Elite performance)
- **NIST SSDF**: Secure Software Development Framework
- **SLSA**: Supply-chain Levels for Software Artifacts

---

**Last Updated**: 2025-11-29
**Version**: 1.0
**Maintained By**: JP Spec Kit Project
