# JPSpec → Specflow Migration Implementation Guide

## Executive Summary

This guide provides step-by-step instructions for executing the jpspec → specflow migration. The migration affects 900+ occurrences across 100+ files and requires approximately 3 hours to complete with full verification.

## Quick Start

```bash
# 1. Preview the migration
./scripts/bash/migrate-jpspec-to-specflow.sh --dry-run --verbose

# 2. Execute the migration
./scripts/bash/migrate-jpspec-to-specflow.sh

# 3. Verify the migration
./scripts/bash/verify-specflow-migration.sh --verbose

# 4. Test everything
pytest tests/
./scripts/bash/run-local-ci.sh
```

## Pre-Migration Checklist

### Prerequisites

- [ ] **Repository is clean** (no uncommitted changes) OR changes are stashed
- [ ] **All tests pass**: `pytest tests/` returns 0 failures
- [ ] **Required tools installed**: `git`, `sed`, `find`, `pytest`, `python3`
- [ ] **Backup plan ready**: Know how to rollback if needed
- [ ] **Time allocated**: 3 hours for complete migration and verification

### Pre-Flight Checks

```bash
# 1. Verify you're in the correct repository
cd /home/jpoley/ps/jp-spec-kit
ls -la pyproject.toml .claude/  # Should exist

# 2. Check git status
git status
# If dirty, decide: stash, commit, or proceed anyway

# 3. Run baseline tests
pytest tests/ -v
# All tests should pass

# 4. Create manual backup (optional, script creates one too)
tar -czf ../jp-spec-kit-backup-$(date +%Y%m%d).tar.gz .

# 5. Verify scripts are executable
ls -la scripts/bash/migrate-jpspec-to-specflow.sh
ls -la scripts/bash/verify-specflow-migration.sh
# Both should have execute permissions (x)
```

## Migration Steps

### Step 1: Dry-Run Migration (15 minutes)

**Purpose**: Preview all changes without modifying any files.

```bash
# Run dry-run with verbose output
./scripts/bash/migrate-jpspec-to-specflow.sh --dry-run --verbose

# Review output carefully
# - Check directories to be renamed
# - Check files to be renamed
# - Look for any unexpected changes
# - Verify no conflicts
```

**Expected Output**:
```
[INFO] Starting jpspec → specflow migration
[INFO] Repository: /home/jpoley/ps/jp-spec-kit
[INFO] Mode: DRY-RUN
[INFO] Running pre-migration validation...
[SUCCESS] Pre-migration validation passed
[INFO] DRY-RUN: Would create backup at ...
[INFO] Renaming directories...
[INFO] DRY-RUN: Would rename: templates/commands/jpspec -> templates/commands/specflow
[INFO] DRY-RUN: Would rename: .claude/commands/jpspec -> .claude/commands/specflow
[INFO] Renaming files...
[INFO] Found X files to rename
[INFO] Replacing content in files...
[INFO] Found Y files to update
[SUCCESS] Migration complete!
[INFO] This was a dry-run. No changes were made.
```

**Decision Point**:
- ✅ Output looks good → Proceed to Step 2
- ❌ Unexpected changes → Review script, check repository state

### Step 2: Execute Migration (10 minutes)

**Purpose**: Apply all migration changes to the repository.

```bash
# Execute migration (with confirmation prompt)
./scripts/bash/migrate-jpspec-to-specflow.sh --verbose

# OR execute without prompts (for automation)
./scripts/bash/migrate-jpspec-to-specflow.sh --force --verbose
```

**Script Actions**:
1. ✅ Validates preconditions (tools, repository state)
2. ✅ Creates backup at `.migration-backup-YYYYMMDD_HHMMSS/`
3. ✅ Creates git stash (if uncommitted changes)
4. ✅ Renames directories
5. ✅ Renames files (agents, tests, docs, configs)
6. ✅ Replaces content in all affected files
7. ✅ Verifies changes
8. ✅ Generates migration summary report

**Interactive Prompt**:
```
[WARN] This will rename directories, files, and modify content across the entire codebase.
[WARN] A backup will be created at: .migration-backup-YYYYMMDD_HHMMSS
Continue with migration? (y/N)
```

Type `y` to proceed.

**Expected Outcome**:
```
[SUCCESS] Migration complete!

════════════════════════════════════════════════════════════════
                    MIGRATION SUMMARY
════════════════════════════════════════════════════════════════

Backup Location: .migration-backup-YYYYMMDD_HHMMSS

Directories Renamed:
  - templates/commands/jpspec → templates/commands/specflow
  - .claude/commands/jpspec → .claude/commands/specflow

Files Renamed (examples):
  - jpspec_workflow.yml → specflow_workflow.yml
  - memory/jpspec_workflow.yml → memory/specflow_workflow.yml
  ...

Content Replacements:
  - /jpspec: → /specflow:
  - jpspec_workflow → specflow_workflow
  ...

Next Steps:
  1. Review changes: git status
  2. Run tests: pytest tests/
  3. Verify CI: ./scripts/bash/run-local-ci.sh
  ...
```

**Checkpoint**:
```bash
# Quick sanity check
git status  # Should show many modified/renamed files
ls -la templates/commands/specflow/  # Should exist
ls -la .claude/commands/specflow/    # Should exist
cat specflow_workflow.yml | head    # Should exist and be valid
```

### Step 3: Verify Migration (10 minutes)

**Purpose**: Comprehensive validation of migration completeness.

```bash
# Run verification script
./scripts/bash/verify-specflow-migration.sh --verbose
```

**Verification Checks**:
1. ✅ Repository location verified
2. ✅ No remaining jpspec references (except allowed locations)
3. ✅ Expected directories exist
4. ✅ Old directories removed
5. ✅ Expected files exist
6. ✅ Old files removed
7. ✅ Agent files renamed correctly
8. ✅ Test files renamed correctly
9. ✅ YAML files valid
10. ✅ Command files updated

**Expected Output**:
```
[INFO] Starting specflow migration verification
[✓] Repository location verified
[✓] No remaining jpspec references found
[✓] Directory exists: templates/commands/specflow
[✓] Old directory removed: templates/commands/jpspec
...

════════════════════════════════════════════════════════════════
                  VERIFICATION SUMMARY
════════════════════════════════════════════════════════════════

Total Checks:    15
Passed:          15
Failed:          0
Warnings:        0

Overall Status:  PASSED
```

**If Verification Fails**:
- Review failed checks in verbose output
- Fix issues manually
- Re-run verification script
- If severe: Consider rollback (see Step 7)

### Step 4: Run Test Suite (20 minutes)

**Purpose**: Ensure all tests pass with new naming.

```bash
# Run full test suite
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/specify_cli --cov-report=term-missing --cov-report=html

# Check test files were renamed
ls tests/test_specflow_*.py
```

**Expected Outcome**:
- ✅ All tests pass (same count as pre-migration)
- ✅ No new test failures
- ✅ Test files renamed correctly
- ✅ Coverage maintained

**If Tests Fail**:
1. Review test output for specific failures
2. Common issues:
   - Import paths incorrect
   - File paths hardcoded
   - Test data referencing old names
3. Fix and re-run tests
4. Consider rollback if widespread failures

### Step 5: Functional Testing (30 minutes)

**Purpose**: Verify slash commands and workflows work end-to-end.

#### Test Workflow Configuration

```bash
# 1. Verify YAML is valid
python3 -c "import yaml; print(yaml.safe_load(open('specflow_workflow.yml')))"

# 2. Validate workflow schema
specify workflow validate --verbose

# 3. Check command files exist
ls -la .claude/commands/specflow/assess.md
ls -la .claude/commands/specflow/specify.md
ls -la .claude/commands/specflow/implement.md
ls -la .claude/commands/specflow/validate.md
```

#### Test Slash Commands (Manual)

If using VS Code or Claude Code:

1. **Open command palette** (Cmd/Ctrl+Shift+P)
2. **Test each command**:
   - `/specflow:assess` - Should load assess.md
   - `/specflow:specify` - Should load specify.md
   - `/specflow:plan` - Should load plan.md
   - `/specflow:implement` - Should load implement.md
   - `/specflow:validate` - Should load validate.md

3. **Verify agent files**:
   - Check `.github/agents/specflow-*.agent.md` exist
   - Verify GitHub Copilot can load them

#### Test Integration

```bash
# Test backlog integration
backlog task list --plain

# Test workflow in temporary directory
cd /tmp
mkdir test-specflow-migration
cd test-specflow-migration
specify init --feature "test-migration"

# In Claude Code/VS Code:
# - Run /specflow:assess
# - Run /specflow:specify
# - Verify tasks created in backlog
```

### Step 6: CI/CD Validation (20 minutes)

**Purpose**: Verify CI/CD pipelines work with new naming.

```bash
# 1. Test GitHub Actions locally
./scripts/bash/run-local-ci.sh --act

# OR test specific jobs
act -j test
act -j lint
act -j build

# 2. Test pre-commit hooks
./scripts/bash/pre-commit-dev-setup.sh

# 3. Test MCP servers (if applicable)
./scripts/bash/check-mcp-servers.sh

# 4. Build documentation (if using DocFX/MkDocs)
docfx docs/docfx.json  # Or mkdocs build
```

**Expected Outcome**:
- ✅ All GitHub Actions jobs pass
- ✅ Pre-commit hooks work
- ✅ MCP servers healthy
- ✅ Documentation builds successfully

### Step 7: Review and Commit (30 minutes)

**Purpose**: Final review and commit changes to version control.

```bash
# 1. Review all changes
git status
git diff --stat
git diff specflow_workflow.yml  # Spot check key files

# 2. Check for any uncommitted files
git ls-files --others --exclude-standard

# 3. Stage all changes
git add -A

# 4. Create commit
git commit -m "Rename /jpspec to /specflow

- Rename slash commands (/jpspec:* → /specflow:*)
- Rename directories (templates/commands/jpspec → specflow)
- Rename workflow config (jpspec_workflow.yml → specflow_workflow.yml)
- Rename test files (test_jpspec_* → test_specflow_*)
- Rename agent files (jpspec-*.agent.md → specflow-*.agent.md)
- Update all documentation references
- Verify all tests pass
- Update CI/CD workflows

Migration executed by scripts/bash/migrate-jpspec-to-specflow.sh
Verified by scripts/bash/verify-specflow-migration.sh

Refs: task-411, task-412, task-413, task-414"

# 5. Create tag (optional)
git tag -a migration-specflow-$(date +%Y%m%d) -m "JPSpec → Specflow migration"

# 6. Push (when ready)
# git push origin main
# git push origin --tags
```

## Post-Migration Tasks

### Update Documentation

```bash
# 1. Update CHANGELOG.md
cat >> CHANGELOG.md <<'EOF'

## [Unreleased] - Migration to Specflow

### Changed
- **BREAKING**: Renamed all /jpspec: commands to /specflow:
  - `/jpspec:assess` → `/specflow:assess`
  - `/jpspec:specify` → `/specflow:specify`
  - `/jpspec:plan` → `/specflow:plan`
  - `/jpspec:implement` → `/specflow:implement`
  - `/jpspec:validate` → `/specflow:validate`
- Renamed `jpspec_workflow.yml` to `specflow_workflow.yml`
- Updated all documentation to reflect Specflow branding

### Migration Guide
See docs/migration-implementation-guide.md for upgrade instructions.
EOF

# 2. Update README.md
# - Change jpspec references to specflow
# - Update quick start examples
# - Add migration notice

# 3. Build and deploy documentation site
docfx docs/docfx.json
# Deploy to hosting (GitHub Pages, etc.)
```

### Communication

1. **Create release with migration notes**:
   ```bash
   gh release create v0.X.0 \
     --title "Specflow Migration Release" \
     --notes-file docs/release-notes-specflow.md
   ```

2. **Update external documentation**:
   - Project website
   - GitHub Wiki
   - Examples repository
   - Tutorial videos/blog posts

3. **Notify users**:
   - GitHub Discussions
   - Discord/Slack
   - Email list
   - Social media

### Monitoring

```bash
# Monitor for issues
git log --oneline --since="1 week ago"

# Check for reported issues
gh issue list --label "migration,specflow"

# Monitor CI/CD
gh run list --limit 10
```

## Rollback Procedures

### Emergency Rollback (if migration fails)

#### Method 1: Restore from Backup

```bash
# Find backup directory
ls -la .migration-backup-*/

# Restore
BACKUP_DIR=.migration-backup-YYYYMMDD_HHMMSS
cp -r "$BACKUP_DIR"/* .

# Verify restoration
grep -r "jpspec" . --exclude-dir=.git | wc -l  # Should be high
pytest tests/  # Should pass
```

#### Method 2: Git Restore (if not committed)

```bash
# Restore all files
git restore .

# Clean untracked files
git clean -fd

# Verify
git status  # Should be clean
```

#### Method 3: Git Revert (if committed)

```bash
# Revert the migration commit
git revert HEAD

# Or reset (destructive)
git reset --hard HEAD~1

# Push force (if already pushed)
git push origin main --force-with-lease
```

### Partial Rollback (fix specific issues)

```bash
# Restore specific file from backup
BACKUP_DIR=.migration-backup-YYYYMMDD_HHMMSS
cp "$BACKUP_DIR/path/to/file" path/to/file

# Or from git
git restore path/to/file
```

## Troubleshooting

### Issue: "Permission denied" during migration

**Cause**: Script not executable.

**Fix**:
```bash
chmod +x scripts/bash/migrate-jpspec-to-specflow.sh
```

### Issue: Tests fail after migration

**Cause**: Import paths or file references incorrect.

**Fix**:
```bash
# 1. Check for remaining jpspec references
grep -r "jpspec" tests/

# 2. Fix imports manually
# Example: from specify_cli.jpspec_* → specify_cli.specflow_*

# 3. Re-run migration script for content
./scripts/bash/migrate-jpspec-to-specflow.sh --force
```

### Issue: Slash commands don't load in VS Code

**Cause**: VS Code cache.

**Fix**:
```bash
# 1. Clear VS Code cache
# Cmd/Ctrl+Shift+P → "Developer: Reload Window"

# 2. Verify symlinks
ls -la .claude/commands/specflow/

# 3. Rebuild dev-setup
specify dev-setup --force
```

### Issue: Verification script reports failures

**Cause**: Migration incomplete or files missing.

**Fix**:
```bash
# 1. Review specific failures
./scripts/bash/verify-specflow-migration.sh --verbose

# 2. Fix manually or re-run migration
./scripts/bash/migrate-jpspec-to-specflow.sh --force

# 3. Re-verify
./scripts/bash/verify-specflow-migration.sh
```

### Issue: Documentation build fails

**Cause**: Broken links or missing files.

**Fix**:
```bash
# 1. Find broken references
grep -r "jpspec" docs/ --exclude-dir=_site

# 2. Update manually
sed -i 's|jpspec|specflow|g' docs/problematic-file.md

# 3. Rebuild
docfx docs/docfx.json
```

## Success Metrics

Migration is complete when:

- ✅ All verification checks pass (0 failures)
- ✅ All tests pass (pytest tests/)
- ✅ Slash commands work in VS Code/Claude Code
- ✅ CI/CD pipelines pass
- ✅ Documentation builds successfully
- ✅ No critical warnings
- ✅ Changes committed to version control
- ✅ Release created (if applicable)
- ✅ Users notified

## Timeline Summary

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Pre-migration prep | 15 min | 0:15 |
| Dry-run migration | 15 min | 0:30 |
| Execute migration | 10 min | 0:40 |
| Verify migration | 10 min | 0:50 |
| Run tests | 20 min | 1:10 |
| Functional testing | 30 min | 1:40 |
| CI/CD validation | 20 min | 2:00 |
| Review and commit | 30 min | 2:30 |
| Documentation update | 30 min | 3:00 |

**Total: 3 hours**

## References

- **Migration Script**: `scripts/bash/migrate-jpspec-to-specflow.sh`
- **Verification Script**: `scripts/bash/verify-specflow-migration.sh`
- **Testing Strategy**: `docs/migration-testing-strategy.md`
- **CI/CD Impact**: `docs/migration-cicd-impact.md`
- **Migration Plan**: `docs/adr/jpspec-to-specflow-migration-plan.md`

## Support

If you encounter issues during migration:

1. Check this guide's Troubleshooting section
2. Review verification script output: `./scripts/bash/verify-specflow-migration.sh --verbose`
3. Check backlog tasks: `backlog task list`
4. File an issue: `gh issue create --label migration`
5. Rollback if necessary (see Rollback Procedures)

## Appendix: Migration Checklist

Print this checklist and check off each item:

### Pre-Migration
- [ ] Repository clean or changes stashed
- [ ] Baseline tests pass
- [ ] Tools installed (git, sed, find, pytest)
- [ ] Dry-run completed successfully
- [ ] Backup plan ready

### Migration
- [ ] Migration script executed
- [ ] Backup created automatically
- [ ] No errors during execution
- [ ] Migration summary reviewed

### Verification
- [ ] Verification script passes all checks
- [ ] Test suite passes (pytest)
- [ ] Slash commands work
- [ ] Workflow YAML valid
- [ ] CI/CD pipelines pass

### Post-Migration
- [ ] Changes reviewed in git
- [ ] Commit created with descriptive message
- [ ] CHANGELOG.md updated
- [ ] Documentation updated
- [ ] Release created
- [ ] Users notified

### Completion
- [ ] All success metrics met
- [ ] No critical issues
- [ ] Rollback tested (optional)
- [ ] Migration tasks archived
