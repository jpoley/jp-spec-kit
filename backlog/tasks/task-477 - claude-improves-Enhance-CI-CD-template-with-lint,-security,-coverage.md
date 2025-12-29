---
id: task-477
title: 'claude-improves: Enhance CI/CD template with lint, security, coverage'
status: Done
assignee:
  - '@kinsale'
created_date: '2025-12-12 01:15'
updated_date: '2025-12-28 22:15'
labels:
  - claude-improves
  - templates
  - cicd
  - github-actions
  - phase-2
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
CI pipeline template is minimal (21 lines) - only checkout, build, pytest.

Missing critical steps:
- Linting (ruff check)
- Type checking (mypy)
- Security scanning (trivy, bandit)
- Coverage reporting (codecov/coveralls)

Should provide comprehensive CI/CD template based on project type.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Python template includes: ruff check, mypy, pytest with coverage, bandit
- [ ] #2 Node template includes: eslint, tsc, vitest with coverage, npm audit
- [ ] #3 Security scanning job with trivy for containers
- [ ] #4 Coverage upload to codecov or similar
- [ ] #5 Matrix testing for multiple Python/Node versions
- [ ] #6 Separate jobs for lint, test, security (parallel execution)
<!-- AC:END -->
