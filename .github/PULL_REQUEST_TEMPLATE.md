## Description

<!-- Describe what this PR does and why. Link to any relevant issues or discussions. -->

**What**:

**Why**:

## Related Issues

<!-- Link to related issues. Use keywords to auto-close: Closes #123, Fixes #456, Resolves #789 -->

- Closes #

## Type of Change

<!-- Check all that apply -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Tests (adding or updating tests)
- [ ] Configuration/Infrastructure (CI/CD, dependencies, build)
- [ ] Performance improvement
- [ ] Style/formatting (no functional changes)

## Conventional Commit Format

<!-- Ensure your PR title follows conventional commit format -->

PR titles should follow: `type(scope): description`

Examples:
- `feat(cli): add github setup command`
- `fix(templates): resolve variable substitution bug`
- `docs(guides): update workflow documentation`
- `chore(deps): update dependencies`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

## Testing Checklist

<!-- Check all that apply -->

- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally (`pytest tests/`)
- [ ] I have tested manually and verified the expected behavior
- [ ] Test coverage has not decreased

## Documentation Checklist

<!-- Check all that apply -->

- [ ] I have updated the README if needed
- [ ] I have updated relevant documentation in `docs/`
- [ ] I have added code comments for complex logic
- [ ] API changes are documented
- [ ] I have updated CONTRIBUTING.md if the contribution process changed

## Security Checklist

<!-- Check all that apply. Security issues should be reported privately via SECURITY.md -->

- [ ] No secrets, credentials, or API keys are committed
- [ ] User inputs are validated and sanitized
- [ ] I have considered security implications of this change
- [ ] Dependencies have been checked for known vulnerabilities
- [ ] Authentication/authorization changes have been reviewed
- [ ] Error messages do not expose sensitive information

## Breaking Changes

<!-- If this is a breaking change, describe the impact and migration path -->

**Is this a breaking change?** Yes / No

If yes, describe:
- What breaks:
- Migration steps:

## Final Checklist

- [ ] My code follows the project's code style (ruff check, ruff format)
- [ ] I have performed a self-review of my code
- [ ] I have commented my code where necessary
- [ ] My changes generate no new warnings
- [ ] All tests pass
- [ ] PR title follows conventional commit format
- [ ] DCO sign-off is included in commits (`git commit -s`)

---

<!--
AI Agent Notes:
This template is designed to work with both human contributors and AI coding agents.
When filling this out programmatically:
1. Parse the sections and fill in the relevant checkboxes
2. Use git diff analysis to determine type of change
3. Extract issue references from commit messages
4. Verify tests pass before marking the testing checklist
-->
