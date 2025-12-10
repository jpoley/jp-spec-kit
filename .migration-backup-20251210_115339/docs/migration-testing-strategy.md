# JPSpec → Specflow Migration Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for the jpspec → specflow migration. The migration affects 900+ occurrences across 100+ files and requires careful validation to ensure system integrity.

## Pre-Migration Testing

### 1. Baseline Test Run

**Purpose**: Establish known-good state before migration.

```bash
# Full test suite
pytest tests/ -v --cov=src/specify_cli --cov-report=term-missing

# Record results
pytest tests/ --junit-xml=pre-migration-results.xml
```

**Success Criteria**:
- All tests pass
- No test failures or errors
- Coverage baseline documented

### 2. Migration Script Dry-Run

**Purpose**: Validate migration script logic without making changes.

```bash
# Dry-run migration
./scripts/bash/migrate-jpspec-to-specflow.sh --dry-run --verbose

# Review output for issues
```

**Success Criteria**:
- Script completes without errors
- No file/directory conflicts detected
- Expected changes look correct

### 3. Backup Verification

**Purpose**: Ensure rollback capability exists.

```bash
# Create backup
./scripts/bash/migrate-jpspec-to-specflow.sh --dry-run  # Creates backup location

# Verify backup completeness
ls -lR .migration-backup-*/
```

**Success Criteria**:
- Backup directory created
- All critical files backed up
- Backup can be restored

## During Migration Testing

### 1. Migration Execution

**Purpose**: Apply migration changes to repository.

```bash
# Execute migration with confirmation
./scripts/bash/migrate-jpspec-to-specflow.sh --verbose

# OR execute without prompts (for CI/automation)
./scripts/bash/migrate-jpspec-to-specflow.sh --force --verbose
```

**Monitor for**:
- Unexpected errors
- File conflicts
- Permission issues
- Broken symlinks

### 2. Immediate Verification

**Purpose**: Quick sanity check after migration.

```bash
# Quick checks
git status  # Review changed files
git diff    # Spot-check changes

# Verify critical files
ls -la templates/commands/specflow/
ls -la .claude/commands/specflow/
cat specflow_workflow.yml | head -20
```

**Success Criteria**:
- Directories renamed correctly
- No unexpected deletions
- File structure intact

## Post-Migration Testing

### 1. Automated Verification Suite

**Purpose**: Comprehensive validation of migration completeness.

```bash
# Run verification script
./scripts/bash/verify-specflow-migration.sh --verbose

# JSON output for CI integration
./scripts/bash/verify-specflow-migration.sh --json > migration-verification.json
```

**Checks Performed**:
- ✅ No remaining jpspec references (except allowed locations)
- ✅ Expected directories exist
- ✅ Expected files exist
- ✅ Old directories/files removed
- ✅ Agent files renamed correctly
- ✅ Test files renamed correctly
- ✅ YAML files valid
- ✅ Command files updated

**Success Criteria**:
- All verification checks pass
- Zero critical failures
- Warnings reviewed and addressed

### 2. Test Suite Execution

**Purpose**: Ensure all tests pass with new naming.

```bash
# Full test suite
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/specify_cli --cov-report=html

# Compare to baseline
pytest tests/ --junit-xml=post-migration-results.xml
diff pre-migration-results.xml post-migration-results.xml
```

**Success Criteria**:
- All tests pass
- Same number of tests as pre-migration
- No new test failures
- Coverage maintained or improved

### 3. Functional Testing

**Purpose**: Verify slash commands work with new naming.

#### Test Plan

| Test Case | Command | Expected Behavior |
|-----------|---------|-------------------|
| TC-001 | `/specflow:assess` | Loads assess.md from .claude/commands/specflow/ |
| TC-002 | `/specflow:specify` | Loads specify.md, creates tasks in backlog |
| TC-003 | `/specflow:plan` | Loads plan.md, creates design docs |
| TC-004 | `/specflow:implement` | Loads implement.md, executes agents |
| TC-005 | `/specflow:validate` | Loads validate.md, runs QA checks |
| TC-006 | Workflow config | `specflow_workflow.yml` loads correctly |
| TC-007 | Workflow validation | `specify workflow validate` passes |
| TC-008 | Agent files | GitHub Copilot agents load correctly |

#### Manual Test Script

```bash
# Test workflow config loading
cat specflow_workflow.yml
python3 -c "import yaml; print(yaml.safe_load(open('specflow_workflow.yml')))"

# Test workflow validation
specify workflow validate --verbose

# Test command file access
cat .claude/commands/specflow/assess.md
cat .claude/commands/specflow/specify.md
cat .claude/commands/specflow/implement.md

# Test symlinks (if using dev-setup)
ls -la .claude/commands/specflow/
./scripts/bash/pre-commit-dev-setup.sh
```

**Success Criteria**:
- All slash commands load correctly
- Workflow YAML parses without errors
- Command files accessible
- Agents load and execute

### 4. Integration Testing

**Purpose**: Test end-to-end workflows with new naming.

```bash
# Create test feature
cd /tmp/test-specflow-migration
specify init --feature "test-migration"

# Run workflow commands
# (In Claude Code or VS Code)
/specflow:assess
/specflow:specify
/specflow:plan

# Verify task creation
backlog task list --plain
```

**Success Criteria**:
- Workflow executes end-to-end
- Tasks created correctly
- No broken references
- Agent execution succeeds

### 5. Documentation Build Testing

**Purpose**: Verify documentation site builds with new references.

```bash
# If using DocFX
docfx docs/docfx.json

# If using MkDocs
mkdocs build --strict

# If using Sphinx
sphinx-build -b html docs/ docs/_build/html
```

**Success Criteria**:
- Documentation builds without errors
- No broken links
- All references updated
- Navigation works correctly

## Regression Testing

### Critical Functionality Checklist

- [ ] Slash commands load and execute
- [ ] Workflow state transitions work
- [ ] Task creation works
- [ ] Agent assignment works
- [ ] File templates load correctly
- [ ] Workflow validation passes
- [ ] CLI commands function (`specify workflow validate`)
- [ ] GitHub Copilot integration works
- [ ] MCP server integration works (if applicable)
- [ ] Pre-commit hooks work
- [ ] CI/CD pipelines execute

### Known Gotchas to Test

1. **Symlinks**: If using `specify dev-setup`, verify symlinks updated
2. **Cached files**: Clear Python cache (`find . -type d -name __pycache__ -exec rm -rf {} +`)
3. **Git hooks**: Verify pre-commit hooks work with new paths
4. **Environment variables**: Check for hardcoded paths in env configs
5. **Documentation links**: Verify internal doc links updated

## Rollback Testing

### Rollback Procedure

```bash
# Method 1: Restore from backup
cp -r .migration-backup-*/* .

# Method 2: Git restore (if committed)
git restore .
git clean -fd

# Method 3: Git stash
git stash pop

# Verify rollback
./scripts/bash/verify-specflow-migration.sh  # Should fail
grep -r "jpspec" . --exclude-dir=.git | wc -l  # Should be high
```

**Success Criteria**:
- Repository restored to pre-migration state
- Tests pass after rollback
- No corruption or data loss

## CI/CD Integration

### GitHub Actions Testing

```bash
# Test locally with act
./scripts/bash/run-local-ci.sh --act

# Or test workflow file directly
act -j test
act -j lint
act -j build
```

**Verify**:
- Workflow YAML syntax valid
- All jobs execute
- No failures introduced by migration

### Continuous Testing Strategy

1. **Pre-merge**: All tests must pass before merging migration PR
2. **Post-merge**: Monitor CI for any delayed failures
3. **Deployment**: Stage deployment before production
4. **Monitoring**: Watch for errors in logs/metrics

## Test Results Documentation

### Test Report Template

```markdown
# Migration Test Report

**Date**: YYYY-MM-DD
**Tester**: Name
**Migration Script Version**: X.Y.Z

## Summary
- ✅/❌ Pre-migration tests passed
- ✅/❌ Migration executed successfully
- ✅/❌ Post-migration verification passed
- ✅/❌ Functional tests passed
- ✅/❌ Integration tests passed

## Detailed Results
- Total test cases: N
- Passed: N
- Failed: N
- Warnings: N

## Issues Found
1. Issue description
2. Issue description

## Recommendations
- Action item 1
- Action item 2
```

## Test Automation

### Recommended Test Automation Script

```bash
#!/bin/bash
# test-migration.sh - Automated migration testing

set -e

echo "=== Pre-Migration Tests ==="
pytest tests/ --junit-xml=pre-migration.xml

echo "=== Migration Dry-Run ==="
./scripts/bash/migrate-jpspec-to-specflow.sh --dry-run

echo "=== Execute Migration ==="
./scripts/bash/migrate-jpspec-to-specflow.sh --force

echo "=== Post-Migration Verification ==="
./scripts/bash/verify-specflow-migration.sh

echo "=== Post-Migration Tests ==="
pytest tests/ --junit-xml=post-migration.xml

echo "=== Compare Results ==="
diff pre-migration.xml post-migration.xml || echo "Test results differ!"

echo "=== All Tests Passed ==="
```

## Success Metrics

Migration is considered successful when:

1. ✅ All verification checks pass (0 failures)
2. ✅ All pre-migration tests still pass
3. ✅ No new test failures introduced
4. ✅ All slash commands work
5. ✅ Workflow YAML validates
6. ✅ Documentation builds successfully
7. ✅ CI/CD pipelines pass
8. ✅ Manual functional testing complete
9. ✅ No critical warnings
10. ✅ Rollback tested and verified

## Timeline

| Phase | Duration | Milestone |
|-------|----------|-----------|
| Pre-migration prep | 30 min | Baseline established, backup created |
| Migration execution | 10 min | Scripts run, files renamed |
| Automated verification | 10 min | Verification suite passes |
| Manual testing | 1 hour | Functional tests complete |
| CI/CD validation | 30 min | All pipelines pass |
| Documentation | 30 min | Migration report created |
| **Total** | **~3 hours** | Migration complete and verified |

## References

- Migration Script: `scripts/bash/migrate-jpspec-to-specflow.sh`
- Verification Script: `scripts/bash/verify-specflow-migration.sh`
- Migration Plan: `docs/adr/jpspec-to-specflow-migration-plan.md`
- Test Documentation: `tests/README.md`
