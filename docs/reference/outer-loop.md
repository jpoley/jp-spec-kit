# Outer Loop: Key Processes and Decisions

This document outlines the **objectives and key decisions** for building an effective outer development loop (CI/CD pipeline). Specific tooling and platform choices should be made based on these principles and your organization's specific needs.

## What the Outer Loop Owns
The **outer loop** is everything beyond your local iteration: PR → build → test → package → attest → deploy → observe → learn.  
Its mission: enforce consistency, safety, and speed between developer output and production reliability.

### Core Responsibilities
- **Code Movement:** PR policies, reviews, branch protections, semantic versioning.
- **Builds & Tests:** Deterministic, reproducible, and fast.
- **Supply Chain Security:** SBOMs, signatures, provenance, attestations.
- **Deployments:** Safe promotion, rollback, approvals, GitOps.
- **Observability:** Visibility across the entire lifecycle.
- **Governance:** Policy-as-code, separation of duties, audit trails.

---

## Core Principles

These principles are **MANDATORY** - they are not suggestions or best practices, but fundamental requirements:

### 🎯 Build Once in Dev, Promote Everywhere Else
- **THE MOST CRITICAL PRINCIPLE:** You MUST build exactly once in dev/CI, then promote that immutable artifact
- Rebuilding for environment promotion is a security and compliance violation
- Every rebuild breaks your provenance chain and supply chain security
- If you can't promote, you can't secure

### 🔐 Sign Everything, Trust Nothing
- Every production artifact **MUST** have a signed SBOM and provenance attestation
- Unsigned artifacts **MUST NOT** reach production
- Trust is established through cryptographic verification, not process

### 🏗️ Centralize Pipeline Components, Don't Duplicate
- Reusable pipeline components across projects beat copy-paste configuration
- Single source of truth for organizational standards
- Updates propagate automatically without touching every repository

### 🔄 Automate Rollback, Don't Require Heroics
- If rollback requires manual intervention or heroics, your process isn't production-ready
- One-click rollback to previous known-good state is mandatory
- Practice rollback procedures regularly

### 📊 Measure Everything Automatically
- DORA metrics (lead time, deployment frequency, MTTR, change failure rate) **MUST** be automatic outputs
- Manual reporting indicates broken observability
- Metrics drive continuous improvement

### ⚖️ Balance Speed and Safety
- Inner loop optimizes for developer velocity and rapid iteration
- Outer loop ensures organizational safety, compliance, and production reliability
- Both are equally important; sacrificing either creates technical debt

---

## Critical Anti-Patterns to Avoid

These are **MUST NOT** violations that fundamentally compromise security, traceability, and reliability:

### ❌ NEVER Rebuild Past Dev/CI
- **MUST NOT** rebuild artifacts for staging, production, or any environment beyond dev/CI
- Rebuilding breaks provenance chain and introduces untested code paths
- Each rebuild creates opportunity for supply chain compromise
- **ONLY BUILD ONCE** in dev/CI, then promote the immutable artifact

### ❌ NEVER Build in Higher Environments
- Production and staging **MUST NOT** have build tools (compilers, bundlers, etc.)
- Higher environments **MUST NOT** have access to source code
- Higher environments **MUST ONLY** run pre-built, signed, immutable artifacts
- Building in production is a critical security and compliance violation

### ❌ NEVER Embed Configuration in Artifacts
- Artifacts **MUST** be environment-agnostic
- Configuration **MUST** come from external sources (environment variables, ConfigMaps, parameter stores)
- **NEVER** rebuild an artifact to change configuration
- Configuration changes require deployment workflow, not rebuild workflow

### ❌ NEVER Deploy Untested Artifacts
- Every artifact **MUST** pass through validation gates before promotion
- Skipping test stages to "move faster" creates unacceptable production risk
- Emergency deployments still require automated validation, just with different thresholds

### ❌ NEVER Commit Secrets to Source Control
- Secrets **MUST NEVER** be committed to Git (even in private repos)
- Secrets **MUST NEVER** be embedded in build artifacts
- Use short-lived tokens (OIDC) or dedicated secret managers
- Implement automated secret scanning in pre-commit hooks and CI

### ❌ NEVER Allow Manual Configuration Changes
- All configuration changes **MUST** go through version-controlled deployment workflows
- Manual SSH/kubectl changes bypass audit trails and approvals
- "Emergency fixes" without GitOps create drift and future incidents

### ❌ NEVER Build Directly on Production Servers
- Production servers **MUST** be immutable and ephemeral
- Direct compilation on production creates:
  - Untraceable artifacts with no SBOM or provenance
  - No rollback capability
  - Security vulnerabilities from build tool presence
  - Compliance violations

---

## 1. Repository Strategy & Branching
- **Decisions:** mono vs multi repo, trunk-based vs GitFlow.  
- **Strong Default:** trunk-based, short-lived feature branches, semantic versioning, release tags.

---

## 2. PR Policy & Protections
- **Decisions:** Who merges, when, and how.  
- **Defaults:** Required checks (lint, SAST, SCA, build, IaC), CODEOWNERS enforcement, linear history, auto-merge for safe PRs.

---

## 3. Runners & Isolation
- **Objective:** Secure, isolated execution environments for CI/CD workloads.
- **Key considerations:**
  - Platform-managed runners for standard workloads, self-hosted ephemeral runners for specialized needs
  - No long-lived VMs, no persistent credentials
  - Short-lived tokens via OpenID Connect (OIDC) for cloud access
  - Proper network isolation and least-privilege access

---

## 4. Pipeline Architecture
- **Objective:** Maintainable, consistent pipeline definitions across projects.
- **Key considerations:**
  - Reusable pipeline components in a central repository
  - Minimal project-specific configuration
  - Matrix/parallel strategies for multi-platform builds
  - Concurrency control to avoid redundant runs
  - Version control for pipeline definitions
  - Easy rollback of pipeline changes

---

## 5. Identity, Secrets, and Cloud Access
- **Objective:** Secure authentication and authorization for pipeline workloads.
- **Key considerations:**
  - OIDC-based authentication with short-lived tokens per environment
  - Environment-scoped secrets and approvals
  - Never use static, long-lived credentials in pipelines
  - Principle of least privilege for all access
  - Automated secret rotation
  - Audit logging of all secret access

---

## 6. Deterministic Builds & Caching
- **Objective:** Balance build speed with reproducibility and security.
- **Key considerations:**
  - Dependency lock files for version pinning
  - Hermetic build containers for isolation
  - Intelligent caching with appropriate scope and invalidation
  - Build metadata embedded in artifacts (commit SHA, build timestamp, etc.)
  - Reproducible builds that produce identical outputs from identical inputs
  - Cache hit rate monitoring and optimization

---

## 7. Test Pyramid & Environments
- **Objective:** Appropriate test coverage at each stage of the pipeline.
- **Key considerations:**
  - **PR validation:** Fast unit tests and static analysis with mocks
  - **Main branch:** Integration tests and end-to-end scenarios
  - **Staging:** Full system tests with sanitized production-like data
  - **Scheduled runs:** Long-running tests, performance tests, and soak tests
  - Progressive test depth matching risk and feedback speed requirements
  - Clear separation between test types and their execution contexts

---

## 8. Artifacts, SBOM, Signatures, Provenance
- **Objective:** Ensure artifact integrity, traceability, and supply chain security.
- **Key considerations:**
  - **SBOM generation:** Automated Software Bill of Materials for all artifacts
  - **Vulnerability scanning:** Automated scanning of dependencies and containers
  - **Artifact signing:** Cryptographic signatures for authenticity
  - **Provenance attestation:** SLSA-compliant build provenance tracking
  - **Immutable storage:** Write-once artifact registries
  - **Retention policies:** Long retention for releases, appropriate cleanup for ephemeral builds

---

## 9. Policy-as-Code & Quality Gates
- **Objective:** Automated enforcement of organizational standards and compliance requirements.
- **Key considerations:**
  - Policy definitions as version-controlled code
  - Infrastructure-as-Code validation
  - License compliance checking
  - Security policy enforcement
  - Required status checks before merge
  - Automated compliance validation
  - Clear policy violation reporting and remediation guidance

---

## 10. Deployment Strategy & Promotions
- **Objective:** Safe, reliable code delivery to production environments.
- **Key considerations:**
  - **GitOps approach:** Declarative, version-controlled deployment specifications
  - **Progressive delivery:** Canary releases, blue-green deployments, traffic splitting
  - **Feature flags:** Runtime control of feature exposure independent of deployment
  - **Deployment gates:** Automated and manual approval requirements
  - **Rollout controls:** Pause, resume, and rollback capabilities
  - **Change windows:** Deployment freezes during critical business periods

---

## 11. Approvals & Separation of Duties (SoD)
- **Objective:** Enforce appropriate review and approval workflows based on risk.
- **Key considerations:**
  - Separate approval requirements for code review vs. deployment authorization
  - Environment-specific approval gates (e.g., staging automatic, production manual)
  - Role-based access control for different approval types
  - Complete audit trail including commit SHA, approvers, timestamps, and build IDs
  - Automated approval for low-risk changes meeting criteria
  - Emergency bypass procedures with enhanced logging

---

## 12. Observability & Feedback
- **Objective:** Comprehensive visibility into pipeline and deployment health.
- **Key considerations:**
  - Build and deployment IDs embedded in all logs and traces
  - Distributed tracing for build and deployment workflows
  - DORA metrics tracking: lead time, deployment frequency, MTTR, change failure rate
  - Automated post-deployment verification before traffic increase
  - Real-time alerting on pipeline and deployment failures
  - Correlation between deployments and production incidents
  - Feedback loops from production back to development

---

## 13. Cost & Performance of CI
- **Objective:** Optimize pipeline efficiency and resource utilization.
- **Key considerations:**
  - Path-based filtering to skip irrelevant pipeline runs
  - Fail-fast strategies to avoid wasted compute
  - Cache effectiveness monitoring and optimization
  - Ephemeral compute resources for cost and security benefits
  - Parallel execution where possible
  - Pipeline duration tracking and optimization
  - Cost attribution and budgeting per team/project

---

## 14. Incident Response & Rollback
- **Objective:** Enable rapid recovery from problematic deployments.
- **Key considerations:**
  - One-click rollback to previous known-good state
  - Automated rollback triggers based on health checks
  - Linked incident response runbooks
  - Clear rollback procedures for different scenarios
  - Blameless postmortem process
  - Feedback loop from incidents to automated policy gates
  - Practice rollback procedures regularly

---

## 15. Compliance, Retention, & Audit
- **Objective:** Meet regulatory and organizational compliance requirements.
- **Key considerations:**
  - Appropriate retention periods for SBOMs, provenance, approvals, and scan results
  - Immutable artifact storage for releases
  - Complete audit trails for all pipeline activities
  - Scheduled automated compliance validation
  - Tamper-evident logging
  - Regular compliance reporting
  - Data lifecycle management and automated cleanup

---

## 16. Governance Model
- **Objective:** Clear ownership and control of pipeline infrastructure and standards.
- **Key considerations:**
  - Platform/Infrastructure team owns central pipeline components
  - Product teams consume standardized, reusable pipeline definitions
  - Organization-wide rules for consistency (code review requirements, commit signing, etc.)
  - Clear escalation path for exceptions and special requirements
  - Regular review and updates of pipeline standards
  - Versioning strategy for pipeline components

---

## 17. Promotion Model
- **Objective:** Ensure consistency and traceability across environment promotions.
- **CRITICAL REQUIREMENT:** Build ONCE in dev/CI, promote EVERYWHERE else.
- **Key considerations:**
  - **Build only in dev/CI environment** - NEVER rebuild for staging, production, or any other environment
  - Promote the **exact same immutable artifact** (identified by digest/hash) across all environments
  - Content-addressable artifact identification ensures bit-for-bit identical artifacts
  - Configuration externalized from artifacts (environment variables, ConfigMaps, parameter stores)
  - Clear provenance chain showing artifact journey from build → staging → production
  - Validation gates at each promotion stage
  - Higher environments (staging, production) should NEVER have build tools, compilers, or source code
  - Rebuilding for environment promotion breaks provenance and violates supply chain security

---

## 18. Post-Deployment Feedback
- **Objective:** Close the feedback loop from production to development.
- **Key considerations:**
  - Automated issue creation when post-deployment checks fail
  - Integration with source control for visibility (PR comments, issue links)
  - AI-assisted triage and summarization of failures
  - Pattern detection across multiple deployment issues
  - Feedback integration into test coverage and quality metrics
  - Automatic linking of production incidents to originating changes
  - Knowledge base building from production learnings

---

## 19. Outer Loop Checklist

| Category | Objective | Ideal State |
|-----------|-----------|-------------|
| Repo & Branching | Structure | Trunk-based with branch protection |
| PR & Checks | Quality Gate | Required automated checks before merge |
| Runners | Security | Ephemeral with least privilege |
| Secrets | Auth | Short-lived tokens, environment scoped |
| Build | Speed & Reliability | Cached and deterministic |
| Test | Coverage | Progressive depth (PR fast, scheduled deep) |
| Artifacts | Custody | Immutable and signed |
| Policy | Governance | Automated policy enforcement |
| Deploy | Method | GitOps with progressive delivery |
| Approvals | SoD | Risk-based automated + manual gates |
| Observability | Feedback | DORA metrics tracked automatically |
| Cost | Optimization | Efficient caching and concurrency control |
| Compliance | Audit | Complete provenance and retention |

---

# NEXT STEPS

Once you've reviewed and aligned on these outer loop principles, the next phase is to:

1. **Select your CI/CD platform** based on organizational requirements, existing infrastructure, and team expertise

2. **Choose implementation tools** for each objective area:
   - SBOM generation and vulnerability scanning
   - Artifact signing and provenance attestation
   - Policy enforcement and compliance checking
   - GitOps and deployment orchestration
   - Observability and metrics collection

3. **Design your pipeline architecture:**
   - Create reusable, parameterized pipeline components
   - Define environment promotion workflows
   - Establish approval and gate mechanisms
   - Configure OIDC and secrets management

4. **Implement incrementally:**
   - Start with foundational elements (deterministic builds, artifact signing)
   - Add progressive delivery capabilities
   - Layer in observability and metrics
   - Refine based on feedback and DORA metrics

5. **Document and evangelize:**
   - Create runbooks for common operations
   - Document the "why" behind each decision
   - Train teams on new workflows
   - Establish feedback channels for continuous improvement

The goal is to translate these objectives into a concrete, secure, and efficient outer loop that scales with your organization.  
