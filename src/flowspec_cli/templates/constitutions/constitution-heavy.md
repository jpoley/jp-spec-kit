# [PROJECT_NAME] Constitution
<!-- TIER: Heavy - Strict controls for enterprise/regulated environments -->
<!-- NEEDS_VALIDATION: Project name -->

## Core Principles (NON-NEGOTIABLE)

### Production-Grade Quality
<!-- SECTION:QUALITY_PRINCIPLES:BEGIN -->
<!-- NEEDS_VALIDATION: Verify quality standards meet regulatory requirements -->
There is no distinction between "dev code" and "production code". All code is production code.

- **Test-First Development**: TDD is mandatory - write tests, verify they fail, then implement
- **Code Review**: Minimum two reviewers required, including one senior engineer
- **Documentation**: All public APIs, architectural decisions, and complex logic must be documented
- **No Technical Debt**: Address issues immediately; do not defer quality
<!-- SECTION:QUALITY_PRINCIPLES:END -->

### Security by Design
Security is not an afterthought. Threat modeling during design phase is mandatory.

### Auditability
All changes must be traceable. Decisions must be documented and justified.

## Git Commit Requirements (NON-NEGOTIABLE)

### No Direct Commits to Main (ABSOLUTE)
**NEVER commit directly to the main branch.** All changes MUST go through a PR.

1. Create a branch for the task
2. Make changes on the branch
3. Create a PR referencing the backlog task
4. PR must pass CI before merge
5. Task marked Done only after PR is merged

**NO EXCEPTIONS.** Not for "urgent" fixes, not for "small" changes, not for any reason.

### Branch Protection
<!-- SECTION:BRANCH_PROTECTION:BEGIN -->
<!-- NEEDS_VALIDATION: Branch protection rules match security requirements -->
- Main branch: Protected, requires 2 approvals
- Release branches: Protected, requires security team approval
- Feature branches: Must be deleted after merge
- Force push: Disabled on protected branches
<!-- SECTION:BRANCH_PROTECTION:END -->

### DCO Sign-Off Required
All commits MUST include a `Signed-off-by` line (Developer Certificate of Origin).

**Always use `git commit -s` to automatically add the sign-off.**

Commits without sign-off will block PRs from being merged.

### Conventional Commits
All commit messages must follow conventional commit format:
```
type(scope): description

[body]

Signed-off-by: Name <email>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `security`

## Pull Request Requirements (NON-NEGOTIABLE)
<!-- SECTION:PR_REQUIREMENTS:BEGIN -->
<!-- NEEDS_VALIDATION: PR requirements meet compliance needs -->
- Descriptive title following conventional commits
- Link to backlog task (mandatory)
- Security impact assessment for changes touching sensitive areas
- Minimum 2 approvals required
- CI pipeline must pass (tests, lint, security scan)
- No merge until all review comments are resolved
<!-- SECTION:PR_REQUIREMENTS:END -->

## Task Management (NON-NEGOTIABLE)

### Task Quality
Every task created MUST have:
- **At least one acceptance criterion** - Tasks without ACs are incomplete
- **Clear, testable criteria** - Each AC must be outcome-oriented and objectively verifiable
- **Proper description** - Explains the "why" and context
- **Risk assessment** - Security/compliance implications noted

Tasks without acceptance criteria will be rejected or archived.

### PR-Task Synchronization
When creating a PR that completes a backlog task:

1. **Before PR creation**: Mark all completed acceptance criteria
2. **With PR creation**: Update task status and reference the PR
3. **PR-Task coupling**: If the PR fails CI or is rejected, revert task status
4. **Traceability**: Every PR must reference its task; every task must reference its PR

## Testing Standards (NON-NEGOTIABLE)
<!-- SECTION:TESTING:BEGIN -->
<!-- NEEDS_VALIDATION: Testing requirements meet regulatory standards -->
- **Unit Tests**: Mandatory for all business logic (minimum 80% coverage)
- **Integration Tests**: Mandatory for all API endpoints and service boundaries
- **E2E Tests**: Mandatory for all critical user journeys
- **Security Tests**: SAST, DAST, and dependency scanning on every PR
- **Performance Tests**: Load testing for user-facing endpoints
- **Contract Tests**: Required for all inter-service communication
<!-- SECTION:TESTING:END -->

## Security Requirements (NON-NEGOTIABLE)
<!-- SECTION:SECURITY:BEGIN -->
<!-- NEEDS_VALIDATION: Security controls meet compliance requirements -->
### Secrets Management
- No secrets in code, configs, or environment files checked into git
- Use approved secrets management solution
- Rotate secrets according to policy

### Access Control
- Principle of least privilege
- All access logged and auditable
- Regular access reviews (quarterly minimum)

### Vulnerability Management
- Dependencies scanned on every build
- Critical vulnerabilities: Fix within 24 hours
- High vulnerabilities: Fix within 7 days
- Security patches applied within SLA

### Data Protection
- PII/sensitive data encrypted at rest and in transit
- Data classification enforced
- Retention policies applied
<!-- SECTION:SECURITY:END -->

## Compliance
<!-- SECTION:COMPLIANCE:BEGIN -->
<!-- NEEDS_VALIDATION: Compliance frameworks applicable to project -->
This project must comply with:
- [COMPLIANCE_FRAMEWORKS]

### Audit Requirements
- All changes logged with user, timestamp, and justification
- Audit logs retained for [RETENTION_PERIOD]
- Regular compliance audits scheduled
<!-- SECTION:COMPLIANCE:END -->

## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]

### Approved Technologies
All technology choices must be from the approved list or require architecture review.

### Linting & Formatting
<!-- NEEDS_VALIDATION: Detected linting tools -->
[LINTING_TOOLS]

### CI/CD Pipeline
<!-- NEEDS_VALIDATION: CI/CD configuration matches security requirements -->
[CI_CD_TOOLS]
<!-- SECTION:TECH_STACK:END -->

## Parallel Task Execution

### Git Worktree Requirements
When executing tasks in parallel, git worktrees MUST be used:

1. **Worktree name must match branch name**
2. **One branch per worktree**
3. **Clean isolation** - no cross-contamination between parallel work
4. **Worktree cleanup** - remove when work is complete

## Change Management
<!-- SECTION:CHANGE_MANAGEMENT:BEGIN -->
<!-- NEEDS_VALIDATION: Change management process meets requirements -->
### Standard Changes
- Pre-approved, low-risk changes
- Follow standard PR process

### Normal Changes
- Require change request documentation
- Impact assessment required
- Rollback plan documented

### Emergency Changes
- Require incident ticket reference
- Post-implementation review mandatory
- Retrospective within 48 hours
<!-- SECTION:CHANGE_MANAGEMENT:END -->

## Incident Response
<!-- SECTION:INCIDENT_RESPONSE:BEGIN -->
<!-- NEEDS_VALIDATION: Incident response meets regulatory requirements -->
- All security incidents reported within [REPORTING_WINDOW]
- Incident severity classification enforced
- Post-incident reviews mandatory
- Lessons learned documented and shared
<!-- SECTION:INCIDENT_RESPONSE:END -->

## Governance

### Constitution Authority
This constitution supersedes all other practices. Violations are escalated.

### Amendments
Changes to this constitution require:
1. Written proposal with justification
2. Impact assessment
3. Security/compliance review
4. Approval from [APPROVAL_AUTHORITY]
5. Migration plan for existing work

**Version**: 1.0.0 | **Ratified**: [DATE] | **Last Amended**: [DATE]
<!-- NEEDS_VALIDATION: Version, dates, and approval authority -->
