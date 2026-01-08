# [PROJECT_NAME] Constitution
<!-- TIER: Medium - Standard controls for typical business projects -->
<!-- NEEDS_VALIDATION: Project name -->

## Core Principles

### Quality-Driven Development
<!-- SECTION:QUALITY_PRINCIPLES:BEGIN -->
<!-- NEEDS_VALIDATION: Adjust quality principles to team practices -->
Code quality is a shared responsibility. Every team member maintains the codebase.

- **Test Coverage**: Critical paths must have test coverage
- **Code Review**: All changes require at least one reviewer
- **Documentation**: Public APIs and complex logic must be documented
<!-- SECTION:QUALITY_PRINCIPLES:END -->

### Continuous Improvement
Regularly evaluate and improve processes. Technical debt should be tracked and addressed.

## Git Commit Requirements

### Branch Strategy
<!-- SECTION:BRANCHING:BEGIN -->
<!-- NEEDS_VALIDATION: Branch strategy matches team workflow -->
- All changes go through feature branches
- Branch naming: `feature/`, `fix/`, `chore/` prefixes
- Main branch is protected - no direct commits
<!-- SECTION:BRANCHING:END -->

### Pull Request Requirements
<!-- SECTION:PR_REQUIREMENTS:BEGIN -->
<!-- NEEDS_VALIDATION: PR requirements appropriate for team -->
- Descriptive title following conventional commits
- Link to related issue/task when applicable
- At least one approval required before merge
- CI checks must pass
<!-- SECTION:PR_REQUIREMENTS:END -->

### DCO Sign-Off
All commits MUST include a `Signed-off-by` line (Developer Certificate of Origin).

Use `git commit -s` to automatically add the sign-off.

## Task Management

### Task Quality
<!-- SECTION:TASK_QUALITY:BEGIN -->
<!-- NEEDS_VALIDATION: Task requirements match team workflow -->
Every task MUST have:
- **Clear description** explaining the "why"
- **Acceptance criteria** that are testable and verifiable
- **Labels** for categorization and filtering
<!-- SECTION:TASK_QUALITY:END -->

### Definition of Done
A task is complete when:
1. All acceptance criteria are met
2. Code is reviewed and approved
3. Tests pass
4. Documentation is updated (if applicable)
5. PR is merged

## Testing Standards
<!-- SECTION:TESTING:BEGIN -->
<!-- NEEDS_VALIDATION: Testing requirements based on project needs -->
- Unit tests for business logic
- Integration tests for API endpoints
- E2E tests for critical user flows
- Minimum coverage target: 70%
<!-- SECTION:TESTING:END -->

## Technology Stack
<!-- SECTION:TECH_STACK:BEGIN -->
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]

### Linting & Formatting
<!-- NEEDS_VALIDATION: Detected linting tools -->
[LINTING_TOOLS]
<!-- SECTION:TECH_STACK:END -->

## Security
<!-- SECTION:SECURITY:BEGIN -->
<!-- NEEDS_VALIDATION: Security practices appropriate for project -->
- No secrets in code - use environment variables
- Dependencies regularly updated for security patches
- Input validation on all external data
<!-- SECTION:SECURITY:END -->

## Governance

This constitution guides team practices. Changes require team consensus.

**Version**: 1.0.0 | **Ratified**: [DATE] | **Last Amended**: [DATE]
<!-- NEEDS_VALIDATION: Version and dates -->
