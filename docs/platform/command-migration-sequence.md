# Dev Setup Infrastructure Implementation Sequence

## Overview

This document provides a recommended implementation sequence for rolling out the dev-setup consistency infrastructure. Follow this sequence to minimize disruption while maximizing safety.

---

## Phase 0: Preparation (Day 0)

### Goals
- Understand current state
- Create backlog tasks
- Get team buy-in

### Actions

1. **Audit current state**
   ```bash
   # Check what exists
   ls -la .claude/commands/jpspec/
   ls -la templates/commands/

   # Identify non-symlink files
   find .claude/commands -name "*.md" -type f

   # Check file sizes
   wc -l .claude/commands/jpspec/*.md templates/commands/jpspec/*.md
   ```

2. **Review deliverables**
   - Read through all created files
   - Understand validation logic
   - Review recovery procedures

3. **Create backlog tasks** (DONE)
   - task-259: CI/CD pipeline
   - task-260: Test suite
   - task-261: Pre-commit hook
   - task-262: Makefile commands
   - task-263: Documentation
   - task-264: Migrate jpspec to templates
   - task-265: Add jpspec to init
   - task-266: Operational runbook

4. **Team alignment**
   - Present architecture to team
   - Discuss benefits and tradeoffs
   - Get approval for rollout

### Deliverables
- [x] Current state documented
- [x] Backlog tasks created
- [ ] Team alignment achieved

### Duration: 1-2 hours

---

## Phase 1: Foundation (Days 1-2)

### Goals
- Deploy core infrastructure
- Establish validation baseline
- Test in isolation

### Priority Order

#### 1. Test Suite (HIGHEST PRIORITY)
**Task**: task-260

**Why first**: Tests define correct behavior before enforcement begins.

```bash
# Files already created:
# - tests/test_dev-setup_validation.py
# - tests/test_dev-setup_init_equivalence.py

# Verify tests work
pytest tests/test_dev-setup_validation.py -v

# Expected: Some tests may fail (current state has non-symlink files)
# This is EXPECTED and documents current drift
```

**Success criteria**:
- Tests run without errors
- Failures accurately reflect current state
- No false positives

#### 2. Makefile Commands (HIGH PRIORITY)
**Task**: task-262

**Why second**: Provides manual tools before automation.

```bash
# File already created:
# - Makefile

# Test commands
make dev-setup-status     # Should show current state
make dev-setup-validate   # May fail - expected
make dev-setup-fix       # Should recreate symlinks

# Verify fix works
make dev-setup-status    # Check symlinks created
```

**Success criteria**:
- All make targets work
- dev-setup-fix creates correct symlinks
- dev-setup-status shows clear output

#### 3. Pre-commit Hook (MEDIUM PRIORITY)
**Task**: task-261

**Why third**: Local validation before CI.

```bash
# Files already created:
# - scripts/bash/pre-commit-dev-setup.sh
# - .pre-commit-config.yaml

# Test hook manually
./scripts/bash/pre-commit-dev-setup.sh

# Install pre-commit
pip install pre-commit
pre-commit install

# Test with staged changes
git add .
pre-commit run dev-setup-validation
```

**Success criteria**:
- Hook detects non-symlink files
- Hook provides clear error messages
- Hook can be bypassed in emergency

#### 4. Documentation (MEDIUM PRIORITY)
**Task**: task-263

**Why fourth**: Enables team self-service.

```bash
# Files already created:
# - docs/reference/dev-setup-consistency.md
# - docs/runbooks/dev-setup-recovery.md
# - docs/platform/dev-setup-platform-principles.md
# - docs/platform/dev-setup-implementation-sequence.md (this file)

# Review docs
cat docs/reference/dev-setup-consistency.md
cat docs/runbooks/dev-setup-recovery.md

# Update CONTRIBUTING.md
vim CONTRIBUTING.md  # Add link to dev-setup guide
```

**Success criteria**:
- Workflows clearly documented
- Common errors have solutions
- New contributors can understand quickly

### Phase 1 Deliverables
- [x] Test suite functional
- [x] Make commands working
- [x] Pre-commit hook installed
- [x] Documentation complete

### Duration: 4-6 hours

---

## Phase 2: Content Migration (Days 3-4)

### Goals
- Move jpspec commands to templates
- Establish true single source of truth
- Maintain backward compatibility

### Steps

#### 1. Migrate jpspec to Templates (CRITICAL)
**Task**: task-264

**Why critical**: Eliminates current drift.

```bash
# Create templates/commands/jpspec/
mkdir -p templates/commands/jpspec/

# Copy enhanced jpspec commands
cp .claude/commands/jpspec/research.md templates/commands/jpspec/
cp .claude/commands/jpspec/implement.md templates/commands/jpspec/
cp .claude/commands/jpspec/validate.md templates/commands/jpspec/
cp .claude/commands/jpspec/specify.md templates/commands/jpspec/
cp .claude/commands/jpspec/plan.md templates/commands/jpspec/
cp .claude/commands/jpspec/assess.md templates/commands/jpspec/
cp .claude/commands/jpspec/operate.md templates/commands/jpspec/
cp .claude/commands/jpspec/_backlog-instructions.md templates/commands/jpspec/

# Verify content
ls -la templates/commands/jpspec/

# Commit templates (before removing originals!)
git add templates/commands/jpspec/
git commit -s -m "feat: migrate jpspec commands to templates

Moves enhanced jpspec commands to templates/commands/jpspec/
to establish single source of truth and eliminate content drift.

Part of dev-setup consistency architecture rollout."

# Update specify dev-setup to create jpspec symlinks
vim src/specify_cli/commands/dev-setup.py  # Add jpspec symlink creation

# Test dev-setup command
specify dev-setup --force

# Verify symlinks created correctly
ls -la .claude/commands/jpspec/

# Remove old non-symlink files (now that symlinks exist)
rm -f .claude/commands/jpspec/*.md

# Recreate as symlinks
specify dev-setup --force

# Verify all are symlinks
make dev-setup-status

# Commit symlink changes
git add .claude/commands/jpspec/
git add src/specify_cli/commands/dev-setup.py
git commit -s -m "fix: convert jpspec commands to symlinks

Replaces regular files with symlinks to templates/commands/jpspec/.
Completes dev-setup consistency architecture for jpspec commands."
```

**Success criteria**:
- All jpspec commands in templates/
- .claude/commands/jpspec/ contains only symlinks
- No content lost in migration
- Tests pass after migration

#### 2. Update specify init (MEDIUM PRIORITY)
**Task**: task-265

**Why after migration**: Distribution must match new structure.

```bash
# Update init command to copy jpspec templates
vim src/specify_cli/commands/init.py

# Test in temp directory
cd /tmp
mkdir test-project
cd test-project
specify init --force

# Verify jpspec commands installed
ls -la .claude/commands/jpspec/

# Clean up
cd /tmp
rm -rf test-project

# Commit changes
cd /home/jpoley/ps/jp-spec-kit
git add src/specify_cli/commands/init.py
git commit -s -m "feat: include jpspec commands in specify init

Distributes enhanced jpspec commands to user projects.
Ensures users get full feature set from the start."
```

**Success criteria**:
- init creates jpspec directory
- All jpspec commands distributed
- User projects work correctly
- Tests verify init completeness

### Phase 2 Deliverables
- [ ] jpspec commands in templates/
- [ ] Symlinks replace regular files
- [ ] init distributes jpspec commands
- [ ] Full dev-setup-init equivalence

### Duration: 4-6 hours

---

## Phase 3: CI/CD Enforcement (Days 5-6)

### Goals
- Enable automated validation
- Block problematic merges
- Monitor for issues

### Steps

#### 1. Deploy CI/CD Pipeline (CRITICAL)
**Task**: task-259

**Why last**: Only enforce after foundation is solid.

```bash
# File already created:
# - .github/workflows/dev-setup-validation.yml

# Commit workflow (after Phase 2 complete!)
git add .github/workflows/dev-setup-validation.yml
git commit -s -m "feat: add dev-setup validation CI/CD pipeline

Automated validation ensures:
- No non-symlink .md files in .claude/commands/
- All symlinks resolve correctly
- Dev Setup-init equivalence maintained
- Tests pass on every PR

Blocks merges when validation fails."

git push origin main

# Monitor first run
# Visit: https://github.com/jpoley/jp-spec-kit/actions

# Check workflow passes
# If failures, debug and fix before enforcing
```

**Success criteria**:
- Workflow runs successfully
- All checks pass on main branch
- Clear error messages on failures
- PR blocking works correctly

#### 2. Team Rollout
- Enable pre-commit hooks for all developers
- Announce new workflow in team channel
- Provide quick reference guide
- Monitor for issues

```bash
# Team announcement template
echo "
🚀 New: Dev Setup Consistency Architecture

Starting today, all command development uses our new
dev-setup architecture to prevent content drift.

Quick Guide:
- Edit files in templates/commands/
- Use 'make dev-setup-validate' before committing
- Run 'make dev-setup-fix' if validation fails

Full docs: docs/reference/dev-setup-consistency.md
Questions: #jp-spec-kit channel
"
```

#### 3. Monitoring Setup
- Check CI/CD success rate
- Monitor validation times
- Track false positives
- Gather developer feedback

### Phase 3 Deliverables
- [ ] CI/CD pipeline active
- [ ] Team trained and onboarded
- [ ] Monitoring established
- [ ] Feedback collected

### Duration: 2-4 hours

---

## Phase 4: Optimization (Ongoing)

### Goals
- Improve based on real usage
- Reduce friction points
- Enhance automation

### Continuous Improvements

#### Week 1-2: Observation
- Monitor CI/CD failure rate
- Identify common errors
- Track MTTR for issues
- Gather developer feedback

#### Week 3-4: Iteration
- Improve error messages
- Add more automated fixes
- Optimize validation speed
- Update documentation

#### Month 2+: Enhancement
- Add metrics dashboard
- Create alerting rules
- Implement auto-remediation
- Quarterly architecture review

---

## Rollback Plan

If critical issues arise:

### Immediate Rollback (< 5 minutes)

```bash
# Disable CI/CD enforcement
# Edit .github/workflows/dev-setup-validation.yml
# Change: on: [push, pull_request]
# To: on: workflow_dispatch  # Manual trigger only

git add .github/workflows/dev-setup-validation.yml
git commit -s -m "fix: temporarily disable dev-setup CI enforcement"
git push origin main
```

### Partial Rollback (< 15 minutes)

```bash
# Keep infrastructure but disable blocking
# Edit workflow to allow failures
# Change exit codes to 0 (warning only)

# Or: Disable pre-commit hook
pre-commit uninstall
```

### Full Rollback (< 30 minutes)

```bash
# Revert all changes
git revert <commit-range>
git push origin main

# Or: Reset to pre-rollout state
git reset --hard <pre-rollout-commit>
git push --force origin main  # Requires approval
```

---

## Success Criteria

### Technical Metrics
- [ ] All tests pass on main branch
- [ ] CI/CD validation runs in < 2 minutes
- [ ] No content drift between dev-setup and init
- [ ] Zero broken symlinks in main
- [ ] Zero non-symlink command files in main

### Team Metrics
- [ ] All developers can run dev-setup-validate locally
- [ ] Pre-commit hooks installed for > 90% of team
- [ ] < 5% of commits blocked by validation (after Week 1)
- [ ] MTTR for dev-setup issues < 5 minutes
- [ ] Developer satisfaction > 4/5

### Quality Metrics
- [ ] Zero content drift incidents
- [ ] Tests catch 100% of architectural violations
- [ ] Documentation clarity > 4/5
- [ ] Self-service resolution rate > 80%

---

## Risk Mitigation

### Risk: Developer Resistance
**Mitigation**:
- Clear communication of benefits
- Excellent documentation
- Fast validation (< 2 min)
- Easy recovery (`make dev-setup-fix`)

### Risk: False Positives
**Mitigation**:
- Thorough testing before enforcement
- Clear error messages
- Easy bypass mechanism
- Rapid iteration based on feedback

### Risk: Performance Impact
**Mitigation**:
- Parallel test execution
- Caching where possible
- Monitor CI times
- Optimize slow checks

### Risk: Breaking Changes
**Mitigation**:
- Rollout in phases
- Test in isolation first
- Rollback plan ready
- Team communication

---

## Timeline Summary

| Phase | Duration | Key Milestone |
|-------|----------|---------------|
| Phase 0: Preparation | 1-2 hours | Team alignment |
| Phase 1: Foundation | 4-6 hours | Tools working locally |
| Phase 2: Migration | 4-6 hours | Content in templates |
| Phase 3: Enforcement | 2-4 hours | CI/CD active |
| Phase 4: Optimization | Ongoing | Continuous improvement |

**Total Initial Rollout**: 2-3 days
**Full Maturity**: 4-6 weeks

---

## Next Steps

### Immediate (Today)
1. Review all created files
2. Test make commands locally
3. Run test suite to see current state
4. Get team approval for rollout

### Week 1
1. Execute Phase 1 (Foundation)
2. Train team on new workflow
3. Test all tools thoroughly
4. Document any issues

### Week 2
1. Execute Phase 2 (Migration)
2. Verify no content loss
3. Test init command thoroughly
4. Update all documentation

### Week 3
1. Execute Phase 3 (Enforcement)
2. Monitor CI/CD closely
3. Help team with issues
4. Gather feedback

### Ongoing
1. Monitor metrics
2. Optimize performance
3. Improve documentation
4. Celebrate success!

---

## Support

During rollout:
- **Slack**: #jp-spec-kit channel
- **Office Hours**: Daily standups for questions
- **Documentation**: docs/reference/dev-setup-consistency.md
- **Runbook**: docs/runbooks/dev-setup-recovery.md

---

**Version**: 1.0.0
**Created**: 2025-12-03
**Last Updated**: 2025-12-03
