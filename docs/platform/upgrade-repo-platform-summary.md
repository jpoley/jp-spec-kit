# upgrade-repo Testing & CI/CD Platform - Executive Summary

**Document**: [Full Platform Design](./upgrade-repo-testing-cicd-platform.md)
**Date**: 2026-01-06
**Epic**: task-579 - Flowspec Release Alignment

---

## Overview

This platform design addresses the **completely broken** `flowspec upgrade-repo` command identified in the Release Alignment effort. The design provides comprehensive testing, CI/CD pipelines, and verification automation to ensure all 18 subtasks under epic task-579 are validated before release.

---

## Critical Problems Being Solved

The current `upgrade-repo` command fails to:
1. ✗ Copy correct agent templates (uses hyphen instead of dot notation)
2. ✗ Update .mcp.json configuration
3. ✗ Migrate flowspec_workflow.yml to v2.0
4. ✗ Remove deprecated files (`.specify/`, `_DEPRECATED_operate.md`)
5. ✗ Remove `/flow:operate` references everywhere
6. ✗ Sync .claude/skills directory (21 skills)
7. ✗ Remove broken `{{INCLUDE:}}` directives

**Impact**: Running `upgrade-repo` on auth.poley.dev TODAY produced incorrect deployments.

---

## Solution Architecture

### 1. Test Pyramid

```
     E2E Tests (5-10)          - Full upgrade on mock repos
   Integration (20-30)         - Multi-component upgrades
 Unit Tests (50-100)           - Individual upgrade functions
```

**Test Coverage Target**: 85% overall (80% minimum threshold)

### 2. Quality Gates (7 Automated Checks)

All gates must pass before merge:

| Gate | Check | Exit Code on Failure |
|------|-------|---------------------|
| 1 | Zero `/flow:operate` references | 1 |
| 2 | Agent files use dot notation (flow.X.agent.md) | 1 |
| 3 | Agent names are PascalCase (FlowAssess) | 1 |
| 4 | No `{{INCLUDE:}}` directives in templates | 1 |
| 5 | MCP config has required servers (backlog, github, serena) | 1 |
| 6 | Workflow config is v2.0 (no operate workflow) | 1 |
| 7 | All 21+ skills present in templates | 1 |

**Implementation**: `scripts/bash/quality-gates.sh` (runs in CI/CD)

### 3. CI/CD Pipelines

#### Pre-Merge (PR Validation)
- Lint and format checks (ruff)
- Unit tests (80%+ coverage)
- Integration tests
- E2E tests
- Quality gates

**Workflow**: `.github/workflows/pr-upgrade-validation.yml`

#### Post-Merge (Main Branch)
- Build package from main
- Install and test upgrade-repo
- Run verification on mock repository

**Workflow**: `.github/workflows/post-merge-validation.yml`

#### Release Gate
- Full test suite
- Quality gates
- Version consistency checks
- Build release artifacts

**Workflow**: `.github/workflows/release-gate.yml`

### 4. Verification Automation

#### Post-Upgrade Verification Script
**Location**: `scripts/bash/verify-upgrade.sh`

Checks:
- ✓ Agent files use dot notation
- ✓ Agent names are PascalCase
- ✓ flow.assess.agent.md exists
- ✓ .mcp.json has required servers
- ✓ flowspec_workflow.yml is v2.0
- ✓ Deprecated files removed (.specify/, _DEPRECATED_operate.md)
- ✓ No /flow:operate references
- ✓ No {{INCLUDE:}} directives
- ✓ Skills synced (21+ skills)
- ✓ 6 agents present

**Usage**:
```bash
# After upgrade-repo
./scripts/bash/verify-upgrade.sh /path/to/upgraded/repo
```

#### MCP Config Validator
**Location**: `scripts/bash/validate-mcp-config.sh`

Validates:
- JSON syntax
- Required `mcpServers` key
- Required servers: backlog, github, serena
- Server structure (command, args, description)

#### Workflow Config Validator
**Location**: `scripts/bash/validate-workflow-config.sh`

Validates:
- YAML syntax
- Version 2.0
- No `operate` workflow
- Required workflows: assess, specify, plan, implement, validate
- Required states (no `Deployed` state)

---

## Test Fixtures

**Location**: `tests/fixtures/mock_repos/`

Mock repositories for testing:

| Fixture | Purpose |
|---------|---------|
| `v1.0-minimal/` | Minimal v1.0 project (baseline) |
| `v1.0-full/` | Full v1.0 with all legacy artifacts |
| `v1.0-custom/` | v1.0 with user customizations |
| `v2.0-current/` | Reference v2.0 (target state) |

**Generator**: `tests/fixtures/create_mock_repos.py`

---

## Rollback Strategy

### Current Backup Mechanism
Automatic timestamped backups on every upgrade:
```
.flowspec-backup-YYYYMMDD-HHMMSS/
├── .flowspec/
├── .claude/
├── .github/
└── templates/
```

### Manual Rollback
```bash
# Find backup
ls -lt | grep flowspec-backup

# Restore
BACKUP_DIR=".flowspec-backup-20260106-143022"
rm -rf .flowspec .claude .github templates
cp -r $BACKUP_DIR/* .
```

### Proposed Automated Rollback (Future)
```bash
flowspec rollback-upgrade
flowspec rollback-upgrade --backup .flowspec-backup-20260106-143022
```

---

## Developer Workflow

### Local Testing
```bash
# 1. Setup
uv sync
uv tool install . --force

# 2. Run tests
pytest tests/test_upgrade*.py -v                    # Unit tests
pytest tests/integration/test_upgrade*.py -v        # Integration
pytest tests/e2e/test_upgrade*.py -v                # E2E
pytest tests/ -k upgrade --cov=src/flowspec_cli     # All with coverage

# 3. Manual testing
mkdir /tmp/test-upgrade
cp -r tests/fixtures/mock_repos/v1.0-full/* /tmp/test-upgrade/
cd /tmp/test-upgrade
flowspec upgrade-repo --dry-run
flowspec upgrade-repo
/path/to/flowspec/scripts/bash/verify-upgrade.sh .
```

### Pre-Commit Hook
**Location**: `scripts/bash/pre-commit-upgrade-check.sh`

Runs quality gates and relevant tests automatically before commit.

---

## Implementation Roadmap

### Week 1: Test Infrastructure
- Days 1-2: Create mock repository fixtures
- Days 3-4: Write unit tests (80%+ coverage)
- Day 5: Write integration tests

### Week 2: CI/CD Pipelines
- Days 1-2: Implement quality gates script
- Days 3-4: Configure CI/CD workflows
- Day 5: Implement verification scripts

### Week 3: E2E Tests & Documentation
- Days 1-2: Write E2E tests
- Days 3-4: Write testing and rollback guides
- Day 5: Final verification on auth.poley.dev (task-579.18)

---

## Success Criteria

### Test Coverage
- Unit tests: 90% (minimum 80%)
- Integration tests: 85% (minimum 75%)
- E2E tests: 70% (minimum 60%)
- Overall: 85% (minimum 80%)

### Quality Gates
All 7 gates must pass (see table above)

### Final Verification (task-579.18)
All checklist items on auth.poley.dev:
- [ ] upgrade-repo runs successfully
- [ ] 6 agents with correct naming
- [ ] MCP config complete
- [ ] Workflow config v2.0
- [ ] Deprecated artifacts removed
- [ ] No /flow:operate or {{INCLUDE:}} references

---

## Key Deliverables

### Scripts
| Script | Purpose |
|--------|---------|
| `quality-gates.sh` | 7 automated quality checks |
| `verify-upgrade.sh` | Post-upgrade verification |
| `validate-mcp-config.sh` | MCP config validator |
| `validate-workflow-config.sh` | Workflow config validator |
| `pre-commit-upgrade-check.sh` | Pre-commit hook |

### Tests
| Test Suite | Location | Count |
|------------|----------|-------|
| Unit tests | `tests/test_upgrade_repo_enhancements.py` | 50-100 |
| Integration tests | `tests/integration/test_upgrade_repo_workflow.py` | 20-30 |
| E2E tests | `tests/e2e/test_upgrade_repo_e2e.py` | 5-10 |

### CI/CD Workflows
| Workflow | Purpose |
|----------|---------|
| `pr-upgrade-validation.yml` | Pre-merge PR checks |
| `post-merge-validation.yml` | Post-merge integration tests |
| `release-gate.yml` | Release validation |

### Documentation
| Document | Purpose |
|----------|---------|
| `upgrade-rollback.md` | Rollback procedures |
| `testing-upgrade-repo-locally.md` | Developer testing guide |
| This document | Platform design |

---

## Security Considerations

### Template Injection Prevention
- Static templates only (no dynamic rendering)
- Safe placeholder substitution
- No user input in template generation

### Backup Security
- Backups stored locally (not uploaded)
- Add `.flowspec-backup-*` to `.gitignore`
- Document cleanup in rollback guide

### Supply Chain Security
- Pin template versions with `--base-version` / `--extension-version`
- Branch-based upgrades for testing only (not production)
- Future: Verify checksums of downloaded archives

---

## Future Enhancements

1. **Automated Rollback Command**: `flowspec rollback-upgrade`
2. **Upgrade Health Checks**: `flowspec health-check` (post-upgrade validation)
3. **Upgrade Telemetry**: Track patterns, failures, rollbacks
4. **Differential Upgrades**: `flowspec upgrade-repo --diff` (selective upgrades)

---

## Next Steps

1. ✓ Platform design complete (this document)
2. ⏳ Create test fixtures (mock repositories)
3. ⏳ Implement unit tests for P0 tasks
4. ⏳ Set up quality gates script
5. ⏳ Configure CI/CD pipelines
6. ⏳ Test on auth.poley.dev (dry-run)
7. ⏳ Execute final verification (task-579.18)

---

## References

- **Full Platform Design**: [upgrade-repo-testing-cicd-platform.md](./upgrade-repo-testing-cicd-platform.md)
- **Release Alignment Plan**: [../building/fix-flowspec-plan.md](../building/fix-flowspec-plan.md)
- **Epic Task**: [../../backlog/tasks/task-579 - EPIC-Flowspec-Release-Alignment-Fix-upgrade-repo-and-Agent-Integration.md](../../backlog/tasks/task-579%20-%20EPIC-Flowspec-Release-Alignment-Fix-upgrade-repo-and-Agent-Integration.md)
- **Verification Task**: [../../backlog/tasks/task-579.18 - P5-Verification-Test-upgrade-repo-fixes-on-auth.poley.dev.md](../../backlog/tasks/task-579.18%20-%20P5-Verification-Test-upgrade-repo-fixes-on-auth.poley.dev.md)

---

**Platform Owner**: Principal Platform Engineer
**Review Status**: Ready for Review
**Implementation Priority**: P0 (Release Blocker)
