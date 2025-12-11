# Agent Loop Classification

This document defines which agents are part of the **Inner Loop** vs **Outer Loop** in the Spec-Driven Development workflow.

## Overview

The development workflow is divided into two loops:

- **Inner Loop**: Fast, local iteration cycle (edit → run/tests → debug → repeat) focused on instant feedback and developer flow
- **Outer Loop**: Post-commit CI/CD pipeline (PR → build → test → package → attest → deploy → observe) focused on consistency, safety, and production reliability

## Inner Loop Agents

The inner loop is optimized for developer velocity and rapid iteration. These agents support local development, testing, and validation **before commit**.

### Planning Agents

These agents help plan and design features before implementation:

| Agent | Description | Primary Use |
|-------|-------------|-------------|
| **product-requirements-manager** | PM/PRD creation and management | Create detailed product requirements and user stories |
| **software-architect** | System architecture and design patterns | Design system architecture, ADRs, and integration patterns |
| **platform-engineer** | Platform and infrastructure planning | Design CI/CD, infrastructure, and platform architecture |
| **researcher** | Research and analysis | Conduct research for technical decisions and validation |
| **business-validator** | Business case validation | Validate business value and feasibility |

### Implementation Agents

These agents write production code:

| Agent | Description | Primary Use |
|-------|-------------|-------------|
| **frontend-engineer** | React/React Native development | Build UI components, state management, and mobile apps |
| **backend-engineer** | API and services development | Build REST/GraphQL/gRPC APIs, business logic, and data models |
| **ai-ml-engineer** | ML/AI implementation | Build ML pipelines, models, and inference services |

### Code Review Agents

These agents review code for quality, security, and best practices:

| Agent | Description | Primary Use |
|-------|-------------|-------------|
| **frontend-code-reviewer** | Frontend code review | Review React/mobile code for performance, accessibility, and quality |
| **backend-code-reviewer** | Backend code review | Review API/service code for security, performance, and architecture |
| **python-code-reviewer** | Python code review | Review Python code for best practices and quality |

### Testing & Quality Agents

These agents ensure quality through testing:

| Agent | Description | Primary Use |
|-------|-------------|-------------|
| **quality-guardian** | Comprehensive QA testing | Functional, integration, performance, and non-functional testing |
| **playwright-test-generator** | E2E test generation | Generate Playwright tests for user workflows |
| **playwright-test-healer** | Test maintenance | Fix broken tests and improve test reliability |
| **playwright-test-planner** | Test planning | Plan comprehensive test coverage strategy |

### Security Agents

These agents ensure security throughout development:

| Agent | Description | Primary Use |
|-------|-------------|-------------|
| **secure-by-design-engineer** | Security validation | Code security review, dependency scanning, threat modeling |

### Language Specialist Agents

These agents provide language-specific expertise:

| Agent | Description | Primary Use |
|-------|-------------|-------------|
| **go-expert-developer** | Go development | Go-specific implementation and best practices |
| **java-developer** | Java development | Java-specific implementation and best practices |
| **js-ts-expert-developer** | JavaScript/TypeScript | JS/TS-specific implementation and patterns |
| **go-expert-advisor** | Go advisory | Go architecture and design guidance |

### Documentation Agents

These agents create and maintain documentation:

| Agent | Description | Primary Use |
|-------|-------------|-------------|
| **tech-writer** | Technical documentation | API docs, user guides, release notes, technical documentation |
| **star-framework-writer** | STAR framework writing | Create structured narrative documentation |

### Other Agents

| Agent | Description | Primary Use |
|-------|-------------|-------------|
| **executive-tech-recruiter** | Technical recruiting | Assist with technical hiring and job descriptions |

## Outer Loop Agents

The outer loop ensures organizational safety, compliance, and production reliability. These agents handle CI/CD, infrastructure, and operational concerns **after commit**.

| Agent | Description | Primary Use |
|-------|-------------|-------------|
| **sre-agent** | Site Reliability Engineering | CI/CD pipelines (GitHub Actions), Kubernetes, DevSecOps, observability, monitoring, alerting, incident management |
| **release-manager** | Release and deployment management | Release readiness assessment, deployment strategy, promotion workflows, change management, production releases |

## Inner Loop Requirements

As defined in task-004.md, the inner loop **MUST** include:

### Testing & CI Simulation

- **Local testing capabilities** with options to build as much of CI as possible before commit
- **Fast feedback loops** (< 2s hot reload)
- **Local CI execution** matching remote CI to catch issues before push
- **Pre-commit validation** with hooks and local checks

### Validation & Contracts

- **Validation tests/contracts** for specific key boundaries and interfaces
- **API contract testing** to ensure compatibility
- **Integration point validation** between components
- **Fast unit tests** with watch mode

### Development Environment

- **Containerized dev environment** with production parity
- **Hot reload capabilities** for immediate feedback
- **Local mocks and emulators** for external dependencies
- **Automated dependency installation**

## Outer Loop Requirements

As defined in task-004.md, the outer loop **MUST** include:

### CI/CD Pipeline (GitHub Actions)

- **Complete GitHub Actions process** for CI to:
  - Build artifacts
  - Run comprehensive test suites
  - Scan for security vulnerabilities (SAST, DAST, SCA)
  - Generate SBOM (Software Bill of Materials)
  - Sign artifacts cryptographically

### Continuous Delivery

- **CD step to promote** artifacts upon:
  - Testing completion and validation
  - Required approvals (manual/automated)
  - Security scan passage
  - Quality gate satisfaction

### Stack-Specific CI

- **Stack-specific CI steps** that:
  - Work with the specific technology stack in use
  - Don't overpopulate `.github/workflows/` folder by default
  - Are only added once the stack is validated through the correct process (before implementation)

### Build-Once, Promote Everywhere

- **Build exactly once** in dev/CI environment
- **Promote immutable artifacts** to staging and production
- **NEVER rebuild** for different environments
- **Environment-agnostic artifacts** with externalized configuration

### Security & Compliance

- **Supply chain security** with SLSA compliance
- **Artifact signing and provenance** attestation
- **Policy-as-code** enforcement
- **Complete audit trails** for all pipeline activities

## Agent Usage in Workflows

### /flow:specify (Inner Loop)
Uses: `product-requirements-manager`

### /flow:plan (Inner Loop)
Uses: `software-architect-enhanced`, `platform-engineer-enhanced`

### /flow:research (Inner Loop)
Uses: `researcher`, `business-validator`

### /flow:implement (Inner Loop)
Uses: `frontend-engineer`, `backend-engineer`, `ai-ml-engineer`, `frontend-code-reviewer`, `backend-code-reviewer`

### /flow:validate (Inner Loop with Outer Loop preparation)
Uses: `quality-guardian`, `secure-by-design-engineer`, `tech-writer`, `release-manager`

Note: The validate workflow bridges inner and outer loops by preparing artifacts for outer loop deployment while still part of inner loop quality checks.

### /flow:operate (Outer Loop)
Uses: `sre-agent`

## Best Practices

### Inner Loop

1. **Keep iterations fast**: Every tool and check should run in seconds, not minutes
2. **Test locally first**: Validate changes locally before pushing to CI
3. **Use pre-commit hooks**: Catch issues before they enter version control
4. **Mirror CI locally**: Run the same checks locally that will run in CI
5. **Fail fast**: Surface errors immediately for quick resolution

### Outer Loop

1. **Automate everything**: Manual steps are error-prone and slow
2. **Build once, deploy many**: Never rebuild for different environments
3. **Sign all artifacts**: Ensure cryptographic verification of all releases
4. **Progressive delivery**: Use canary/blue-green for safe deployments
5. **Monitor continuously**: Observe system health and performance metrics
6. **Practice rollback**: Regular rollback drills ensure preparedness

## Loop Transition Points

### From Inner to Outer Loop

The transition happens at **commit/push to main branch**:

1. **Developer completes inner loop**:
   - Planning, implementation, local testing complete
   - Pre-commit hooks pass
   - Local CI simulation passes
   - Code reviewed and approved

2. **Commit triggers outer loop**:
   - PR created and merged
   - CI pipeline executes (build, test, scan, sign)
   - Artifacts stored in registry
   - Deployment pipelines triggered

### From Outer to Inner Loop

Feedback flows back from outer loop to inform inner loop:

1. **Production insights**:
   - Monitoring and observability data
   - Performance metrics and issues
   - User feedback and bugs

2. **Inner loop adjustments**:
   - Update tests based on production issues
   - Refine monitoring and alerting
   - Improve error handling
   - Enhance documentation

## References

- [Inner Loop Principles](./inner-loop.md) - Detailed inner loop concepts and objectives
- [Outer Loop Principles](./outer-loop.md) - Detailed outer loop concepts and requirements
- [Task 004](../../TODO/task-004.md) - Original task defining loop classifications
