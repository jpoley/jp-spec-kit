# dev-setup Platform Principles

## For /speckit.constitution Integration

This document contains operational standards and platform principles for the dev-setup consistency architecture. These should be integrated into the project constitution as platform-level requirements.

---

## dev-setup Consistency Requirements (NON-NEGOTIABLE)

### Single Source of Truth

All command content MUST live in `templates/commands/`:
- `.claude/commands/` contains ONLY symlinks in the source repository
- No command files (.md) are allowed as regular files in `.claude/commands/`
- Any file modification happens in templates, never in `.claude/commands/`

**Rationale**: Eliminates content drift between development and distribution. What we ship is exactly what we use.

### CI/CD Gates

All pull requests MUST pass dev-setup validation:
- No merge allowed with non-symlink command files in `.claude/commands/`
- Symlink validation runs on every commit to main branch
- Broken symlinks block merges
- Tests must verify dev-setup-init equivalence

**Rationale**: Automated enforcement prevents human error and maintains architecture integrity.

### Developer Workflow

Standard operating procedure for command development:

1. **Edit commands in `templates/commands/`** - Never edit `.claude/commands/` directly
2. **Run `specify dev-setup --force`** after adding new commands to create symlinks
3. **Use `make dev-validate`** to verify setup before committing
4. **Pre-commit hooks** automatically validate on every commit

**Rationale**: Clear, consistent workflow reduces mistakes and cognitive load.

### Recovery Procedures

When validation fails, recovery is simple and fast:

- **Quick fix**: `make dev-fix` recreates all symlinks correctly
- **Status check**: `make dev-status` shows current state
- **Full validation**: `make dev-validate` runs all checks
- **Never manually create files** in `.claude/commands/` - always use automated tools

**Rationale**: Self-healing infrastructure minimizes downtime and reduces operational burden.

---

## DORA Elite Performance Alignment

This architecture directly supports DORA Elite metrics:

### Deployment Frequency (DF)
- **Target**: Multiple times per day
- **Support**: Fast validation (< 2 minutes) enables frequent safe deployments
- **Mechanism**: Automated checks prevent breaking changes

### Lead Time for Changes (LT)
- **Target**: Less than one hour
- **Support**: Pre-commit hooks catch issues before CI, reducing feedback loops
- **Mechanism**: Local validation matches CI validation exactly

### Change Failure Rate (CFR)
- **Target**: 0-15%
- **Support**: Automated validation prevents architectural violations
- **Mechanism**: Tests fail before code reaches production

### Mean Time to Restore (MTTR)
- **Target**: Less than one hour
- **Support**: `make dev-fix` restores consistency in seconds
- **Mechanism**: Runbook provides clear recovery procedures

---

## Platform Engineering Standards

### Infrastructure as Code

All dev-setup infrastructure is versioned and automated:
- CI/CD pipelines defined in `.github/workflows/dev-setup-validation.yml`
- Pre-commit hooks in `scripts/bash/pre-commit-dev-setup.sh`
- Make targets provide consistent interface
- Test suites verify behavior

**Benefit**: Infrastructure changes are reviewed, tested, and reversible.

### Shift-Left Testing

Validation happens at earliest possible point:
1. **Editor**: Symlinks work immediately on file save
2. **Pre-commit**: Catches issues before commit
3. **Local CI**: `make ci-local` simulates full pipeline
4. **CI/CD**: Final gate before merge

**Benefit**: Issues found closer to source are cheaper and faster to fix.

### Observable Operations

All validation provides detailed feedback:
- Clear error messages explain what's wrong
- Actionable fix instructions included in output
- Status commands show current state
- Metrics track validation health

**Benefit**: Developers can self-service most issues without escalation.

### Self-Healing Systems

Automated recovery reduces operational load:
- `make dev-fix` recreates correct state
- Idempotent operations safe to retry
- No manual symlink management required
- Clear escalation paths for complex issues

**Benefit**: Reduces MTTR and cognitive load on developers.

---

## Quality Gates

### Pre-Merge Requirements

All PRs must pass:
- [ ] No non-symlink .md files in `.claude/commands/`
- [ ] All symlinks resolve to existing templates
- [ ] dev-setup command executes successfully
- [ ] Test suite passes (test_dev-setup_*.py)
- [ ] No broken symlinks
- [ ] Template coverage is complete

### Post-Merge Monitoring

Continuous validation on main:
- Automated checks run on every push
- Alerts on validation failures
- Dashboard shows dev-setup health
- Quarterly architecture reviews

---

## Developer Experience Requirements

### Fast Feedback

Validation must be fast to maintain developer flow:
- Pre-commit hook: < 10 seconds
- Full validation: < 2 minutes
- CI pipeline: < 5 minutes
- Local test suite: < 30 seconds

**Rationale**: Slow checks get disabled or ignored.

### Clear Error Messages

All validation failures must include:
- **What went wrong**: Specific files or checks that failed
- **Why it matters**: Impact of the issue
- **How to fix**: Exact commands to run
- **When to escalate**: When automated fixes don't work

**Rationale**: Developers fix what they understand.

### Consistent Interface

All operations use standard commands:
- `make dev-setup-*` for all dev-setup operations
- `specify dev-setup` for core functionality
- `backlog task *` for task management
- No manual file manipulation required

**Rationale**: Consistency reduces learning curve and mistakes.

---

## Architecture Decisions

### Why Symlinks?

Benefits:
- Single source of truth enforced by filesystem
- Changes propagate automatically
- Development matches distribution exactly
- Git tracks one file, not two

Tradeoffs:
- Requires education on symlink behavior
- Pre-commit hooks needed for enforcement
- Recovery procedures for mistakes

**Decision**: Benefits outweigh costs. Education and automation mitigate risks.

### Why Templates First?

Benefits:
- Clear ownership: templates are canonical
- Distribution is automated from templates
- No manual sync between locations
- Testing validates actual distribution

Tradeoffs:
- Can't quick-fix in `.claude/commands/`
- Extra step to see effect of changes
- Learning curve for new contributors

**Decision**: Prevents entire class of drift bugs. Worth the extra discipline.

### Why Automated Validation?

Benefits:
- Catches mistakes before they reach main
- Consistent enforcement across team
- Self-documenting requirements
- Reduces review burden

Tradeoffs:
- CI time overhead
- Initial setup complexity
- False positives possible

**Decision**: Automation is prerequisite for scaling. Manual enforcement fails.

---

## Migration Path

For projects adopting this architecture:

### Phase 1: Infrastructure (Week 1)
- Create templates/commands/ structure
- Add CI/CD validation workflow
- Create pre-commit hook
- Add Makefile targets

### Phase 2: Content Migration (Week 2)
- Move enhanced commands to templates
- Create symlinks with dev-setup command
- Verify equivalence with tests
- Document workflows

### Phase 3: Enforcement (Week 3)
- Enable pre-commit hooks for team
- Block merges on validation failures
- Training sessions for contributors
- Update contribution guidelines

### Phase 4: Optimization (Ongoing)
- Monitor validation performance
- Improve error messages based on feedback
- Add metrics and dashboards
- Quarterly architecture reviews

---

## Success Metrics

### Engineering Metrics
- **Validation time**: < 2 minutes (P50), < 5 minutes (P95)
- **False positive rate**: < 2%
- **MTTR for dev-setup issues**: < 5 minutes
- **Pre-commit hook adoption**: > 90%

### Quality Metrics
- **Content drift incidents**: 0 per quarter
- **Broken symlinks in main**: 0
- **Non-symlink files in main**: 0
- **dev-setup-init equivalence**: 100%

### Developer Experience
- **Time to understand workflow**: < 30 minutes
- **Self-service resolution rate**: > 80%
- **Developer satisfaction**: > 4/5
- **Documentation clarity**: > 4/5

---

## References

- [dev-setup Consistency Guide](/docs/reference/dev-setup-consistency.md)
- [Operational Runbook](/docs/runbooks/dev-setup-recovery.md)
- [CI/CD Workflow](/.github/workflows/dev-setup-validation.yml)
- [Test Suite](/tests/test_dev-setup_validation.py)

---

## Governance

These principles are:
- **Mandatory**: Non-negotiable for all command development
- **Enforced**: Via CI/CD and pre-commit hooks
- **Reviewed**: Quarterly by platform engineering team
- **Updated**: When architecture changes or new patterns emerge

**Exceptions**: Require platform team approval and documented rationale.

**Version**: 1.0.0
**Ratified**: 2025-12-03
**Next Review**: 2026-03-03
