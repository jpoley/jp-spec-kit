# CI/CD Impact Analysis: JPSpec → Specflow Migration

## Overview

This document analyzes the impact of the jpspec → specflow migration on CI/CD pipelines, GitHub Actions workflows, and automated processes.

## Affected Workflows

### GitHub Actions

#### 1. Main CI Workflow (`.github/workflows/ci.yml`)

**Potential Impacts**:
- Workflow file itself may reference jpspec in comments/documentation
- Test job runs `pytest tests/` - affected by test file renames
- No direct path references to jpspec directories (good!)

**Required Changes**:
- ✅ None if workflow uses `pytest tests/` (discovers renamed tests automatically)
- ⚠️ Check for any hardcoded test file paths
- ⚠️ Update workflow comments/documentation if present

**Verification**:
```bash
# Check workflow file for jpspec references
grep -i "jpspec" .github/workflows/ci.yml

# Test locally
act -j test
act -j lint
```

#### 2. Documentation Build Workflow

**Potential Impacts**:
- DocFX configuration may reference jpspec files
- Table of contents (toc.yml) may have jpspec links
- Internal documentation links may break

**Required Changes**:
- Update `docs/toc.yml` with new file paths
- Update navigation structure
- Verify all cross-references

**Verification**:
```bash
# Test documentation build
docfx docs/docfx.json --serve

# Check for broken links
# (Use documentation site link checker)
```

#### 3. Release Workflow

**Potential Impacts**:
- Release notes may reference jpspec
- Changelog generation may include jpspec references
- Version tagging unaffected

**Required Changes**:
- ✅ Likely none (release process agnostic to naming)
- Update CHANGELOG.md to document migration

**Verification**:
```bash
# Test release script
./scripts/bash/prune-releases.sh 0.0.1 --dry-run
```

#### 4. GitHub Copilot Agent Sync

**Potential Impacts**:
- HIGH IMPACT: `.github/agents/jpspec-*.agent.md` files renamed
- Copilot may cache old agent names
- Agent references in workflows updated

**Required Changes**:
- ✅ Rename all `jpspec-*.agent.md` to `specflow-*.agent.md` (handled by migration script)
- Update sync script if it hardcodes jpspec paths
- Clear Copilot cache after migration

**Verification**:
```bash
# Verify agent files
ls -la .github/agents/specflow-*.agent.md

# Test sync script
./scripts/bash/sync-copilot-agents.sh --dry-run
```

## Local CI Testing

### Act (Local GitHub Actions)

**Impact**: Low - act runs workflows from `.github/workflows/` which get updated.

**Required Changes**:
- ✅ None (act reads updated workflow files)

**Verification**:
```bash
# Test all jobs locally
./scripts/bash/run-local-ci.sh --act
```

### Pre-commit Hooks

**Impact**: Medium - hooks may reference jpspec paths.

**Files to Check**:
- `.pre-commit-config.yaml`
- `scripts/bash/pre-commit-hook.sh`
- `scripts/bash/pre-commit-dev-setup.sh`

**Required Changes**:
- Update hook references to `.claude/commands/specflow/`
- Verify symlink validation works with new paths

**Verification**:
```bash
# Test pre-commit hooks
./scripts/bash/pre-commit-dev-setup.sh

# Run hooks manually
pre-commit run --all-files
```

## Dependency Impacts

### Python Package Dependencies

**Impact**: None - package name stays `specify-cli`, imports unchanged.

```python
# These remain unchanged
from specify_cli.workflow.config import WorkflowConfig
from specify_cli.workflow.validator import validate_workflow
```

**Verification**:
```bash
# Reinstall package
uv tool install . --force

# Verify imports
python3 -c "from specify_cli.workflow.config import WorkflowConfig; print('OK')"
```

### MCP Server Integration

**Impact**: Low - MCP configuration uses backlog server, not jpspec-specific.

**Files to Check**:
- `.mcp.json` - should not reference jpspec
- MCP server implementations

**Verification**:
```bash
# Check MCP config
cat .mcp.json | grep -i jpspec

# Test MCP servers
./scripts/bash/check-mcp-servers.sh
```

### External Integrations

**Impact**: Low - most integrations use backlog.md, not jpspec-specific endpoints.

**Integrations to Verify**:
- GitHub API (uses repo, not jpspec paths)
- Backlog.md server (agnostic to workflow naming)
- VS Code extensions (may cache slash commands)

## Deployment Impacts

### Package Distribution

**Impact**: None - package name, version, and distribution unchanged.

**PyPI/Distribution**:
- ✅ Package name: `specify-cli` (unchanged)
- ✅ Entry points: `specify` (unchanged)
- ✅ Version: No impact on versioning

**Post-Migration Release**:
```bash
# Build and publish
uv build
uv publish

# Or using release script
python scripts/release.py
```

### Docker Images (if applicable)

**Impact**: None - no Docker usage detected in repository.

### Documentation Site

**Impact**: High - extensive documentation references jpspec.

**Affected Files**:
- `docs/guides/jpspec-*.md` → `docs/guides/specflow-*.md`
- `docs/reference/jpspec-*.md` → `docs/reference/specflow-*.md`
- `docs/diagrams/jpspec-*.png` → `docs/diagrams/specflow-*.png`
- `docs/toc.yml` - navigation structure

**Required Updates**:
1. Rename all documentation files
2. Update internal links
3. Update navigation (toc.yml)
4. Rebuild documentation site
5. Verify all links work

**Verification**:
```bash
# Find all jpspec references in docs
grep -r "jpspec" docs/ --exclude-dir=_site

# Build documentation
docfx docs/docfx.json

# Serve locally and test
docfx docs/docfx.json --serve
```

## Breaking Changes Analysis

### User-Facing Breaking Changes

#### 1. Slash Command Names

**Before**: `/jpspec:assess`, `/jpspec:specify`, etc.
**After**: `/specflow:assess`, `/specflow:specify`, etc.

**Impact**: HIGH - Users must update their workflows.

**Migration Path**:
- Provide deprecation notice
- Consider keeping `/jpspec:*` as aliases temporarily
- Update all documentation
- Communicate in release notes

#### 2. Workflow Configuration File

**Before**: `jpspec_workflow.yml`
**After**: `specflow_workflow.yml`

**Impact**: MEDIUM - Existing projects must rename config file.

**Migration Path**:
- Migration script renames automatically
- Provide upgrade guide
- Tool could auto-detect and migrate

#### 3. Test File Names

**Before**: `test_jpspec_*.py`
**After**: `test_specflow_*.py`

**Impact**: LOW - Internal to repository.

**Migration Path**:
- Migration script handles automatically
- No user action required

### API Breaking Changes

**Python API**:
- ✅ No breaking changes - imports use `specify_cli`, not jpspec

**CLI Commands**:
- ✅ No breaking changes - CLI is `specify`, not jpspec

**MCP Protocol**:
- ✅ No breaking changes - MCP servers use backlog, not jpspec

## Rollout Strategy

### Recommended Approach: Big Bang Migration

**Rationale**: Name change affects so many files that gradual migration would be extremely complex.

**Steps**:
1. **Pre-release** (Week before):
   - Announce upcoming change in README
   - Update documentation with migration guide
   - Tag current version as "last jpspec version"

2. **Migration Day**:
   - Run migration script
   - Comprehensive testing (3 hours)
   - Create migration PR
   - Merge to main

3. **Release**:
   - Create new release with migration notes
   - Update all external documentation
   - Announce on communication channels

4. **Post-release**:
   - Monitor for issues
   - Provide support for users migrating
   - Update examples/tutorials

### Alternative: Deprecation Period

**If backward compatibility is critical**:

1. Keep `/jpspec:*` as aliases:
   ```bash
   # Create symlinks
   ln -s specflow .claude/commands/jpspec
   ```

2. Add deprecation warnings:
   ```python
   # In slash command handlers
   if command.startswith("/jpspec:"):
       print("DEPRECATED: /jpspec: commands renamed to /specflow:")
       print("Please update your workflows.")
   ```

3. Remove aliases in future release (e.g., 3 months later)

**Recommendation**: Big bang migration is cleaner and simpler given scope.

## CI/CD Checklist

### Pre-Migration

- [ ] Document current CI/CD setup
- [ ] Backup workflow files
- [ ] Test baseline (all CI jobs pass)
- [ ] Identify all workflow files

### During Migration

- [ ] Run migration script
- [ ] Update workflow comments/docs
- [ ] Rename agent files
- [ ] Update documentation site config
- [ ] Test workflows locally (act)

### Post-Migration

- [ ] Verify all CI jobs pass
- [ ] Test documentation build
- [ ] Verify MCP servers
- [ ] Test pre-commit hooks
- [ ] Validate GitHub Actions
- [ ] Check external integrations
- [ ] Update release notes
- [ ] Deploy documentation site

## Monitoring & Validation

### Automated Checks

```yaml
# Add to CI workflow
- name: Verify no jpspec references
  run: |
    # Allowed: CHANGELOG.md, migration docs
    JPSPEC_COUNT=$(grep -r "jpspec" . \
      --exclude-dir=.git \
      --exclude-dir=.venv \
      --exclude="CHANGELOG.md" \
      --exclude="migration-*.md" \
      | wc -l)

    if [ $JPSPEC_COUNT -gt 0 ]; then
      echo "ERROR: Found $JPSPEC_COUNT jpspec references"
      grep -r "jpspec" . --exclude-dir=.git --exclude-dir=.venv
      exit 1
    fi
```

### Manual Validation

1. **Workflow Execution**:
   - Run each GitHub Actions workflow
   - Verify all jobs complete successfully
   - Check for deprecation warnings

2. **Documentation Site**:
   - Build documentation
   - Navigate through all sections
   - Test search functionality
   - Verify all links work

3. **Integration Testing**:
   - Test end-to-end workflows
   - Verify slash commands work
   - Test agent execution
   - Validate task creation

## Risk Mitigation

### High-Risk Areas

1. **GitHub Actions Workflows**
   - Risk: Workflows fail after migration
   - Mitigation: Test with `act` before merge
   - Rollback: Git revert + redeploy

2. **Documentation Site**
   - Risk: Broken links, navigation issues
   - Mitigation: Run link checker, manual review
   - Rollback: Rebuild from previous commit

3. **User Workflows**
   - Risk: Users' existing workflows break
   - Mitigation: Communication, migration guide, deprecation period
   - Rollback: Not feasible - provide upgrade instructions

### Medium-Risk Areas

1. **Pre-commit Hooks**
   - Risk: Hooks fail, block commits
   - Mitigation: Test manually before merge
   - Rollback: Update hooks independently

2. **MCP Servers**
   - Risk: Integration breaks
   - Mitigation: Test all MCP endpoints
   - Rollback: MCP config is separate

## Communication Plan

### Internal (Team)

- [ ] Update project README
- [ ] Update CONTRIBUTING.md
- [ ] Update internal documentation
- [ ] Notify team members

### External (Users)

- [ ] Release notes with migration guide
- [ ] Update public documentation
- [ ] Update examples/tutorials
- [ ] Social media announcement (if applicable)
- [ ] Support documentation for common issues

### Migration Guide Template

```markdown
# Migrating from /jpspec to /specflow

## Overview
JP Spec Kit has been rebranded to Specflow...

## What Changed
- Slash commands: `/jpspec:*` → `/specflow:*`
- Config file: `jpspec_workflow.yml` → `specflow_workflow.yml`
- Agent files: `jpspec-*.agent.md` → `specflow-*.agent.md`

## Migration Steps
1. Update slash commands in your workflows
2. Rename config file
3. Update any custom scripts
4. Clear VS Code cache
5. Test your workflows

## Need Help?
- File an issue: [link]
- See FAQ: [link]
```

## Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| **Pre-migration** | 1 week | Announcement, documentation prep, testing strategy |
| **Migration Day** | 3 hours | Execute migration, test, verify |
| **CI/CD Updates** | 2 hours | Update workflows, test pipelines |
| **Documentation** | 4 hours | Update site, rebuild, deploy |
| **Verification** | 2 hours | End-to-end testing, validation |
| **Release** | 1 hour | Create release, publish, announce |
| **Post-release** | 1 week | Monitor, support users, fix issues |

## Success Criteria

Migration is successful when:

- ✅ All GitHub Actions workflows pass
- ✅ Documentation site builds and deploys
- ✅ All tests pass (pytest)
- ✅ MCP servers functional
- ✅ Pre-commit hooks work
- ✅ No critical bugs reported
- ✅ Migration guide published
- ✅ Users successfully migrating

## References

- Migration Script: `scripts/bash/migrate-jpspec-to-specflow.sh`
- Verification Script: `scripts/bash/verify-specflow-migration.sh`
- Testing Strategy: `docs/migration-testing-strategy.md`
- GitHub Actions: `.github/workflows/`
