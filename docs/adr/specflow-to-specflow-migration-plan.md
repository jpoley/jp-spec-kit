# ADR: /specflow → /specflow Command Migration Plan

**Date**: 2025-12-09
**Status**: Proposed
**Decision**: Rename all `/specflow` commands to `/specflow` across the entire codebase

## Context

The project is undergoing a branding/naming change from `/specflow` to `/specflow`. This affects:
- 912+ occurrences across 100+ files
- Slash command directories and files
- Configuration files (workflow YAML, JSON schemas)
- Test files (10 test files with `specflow` in their names)
- Documentation (extensive references in guides, ADRs, PRDs)
- GitHub agent files
- Source code (Python CLI)
- Backlog task files

## Migration Plan

### Phase 1: Directory Structure Changes

#### 1.1 Rename Command Directories

**Source (templates):**
```bash
mv templates/commands/specflow templates/commands/specflow
```

**Source (.claude/commands):**
```bash
mv .claude/commands/specflow .claude/commands/specflow
```

#### 1.2 Rename GitHub Agent Files

Rename 15 files:
```
.github/agents/specflow-*.agent.md → .github/agents/specflow-*.agent.md
```

Files to rename:
- specflow-init.agent.md → specflow-init.agent.md
- specflow-operate.agent.md → specflow-operate.agent.md
- specflow-prune-branch.agent.md → specflow-prune-branch.agent.md
- specflow-reset.agent.md → specflow-reset.agent.md
- specflow-security_fix.agent.md → specflow-security_fix.agent.md
- specflow-security_report.agent.md → specflow-security_report.agent.md
- specflow-security_triage.agent.md → specflow-security_triage.agent.md
- specflow-security_web.agent.md → specflow-security_web.agent.md
- specflow-security_workflow.agent.md → specflow-security_workflow.agent.md
- specflow-assess.agent.md → specflow-assess.agent.md
- specflow-implement.agent.md → specflow-implement.agent.md
- specflow-plan.agent.md → specflow-plan.agent.md
- specflow-research.agent.md → specflow-research.agent.md
- specflow-specify.agent.md → specflow-specify.agent.md
- specflow-validate.agent.md → specflow-validate.agent.md

#### 1.3 Rename Configuration Files

```bash
mv memory/specflow_workflow.yml memory/specflow_workflow.yml
mv memory/specflow_workflow.schema.json memory/specflow_workflow.schema.json
# Note: specflow_workflow.yml at root already appears to be transitioning to specflow_workflow.yml
```

### Phase 2: Test File Renames

Rename 10 test files:
```
tests/test_specflow_*.py → tests/test_specflow_*.py
```

Files to rename:
- test_specflow_specify_backlog.py → test_specflow_specify_backlog.py
- test_specflow_operate_backlog.py → test_specflow_operate_backlog.py
- test_specflow_research_backlog.py → test_specflow_research_backlog.py
- test_specflow_backlog_integration.py → test_specflow_backlog_integration.py
- test_specflow_assess.py → test_specflow_assess.py
- test_specflow_implement_backlog.py → test_specflow_implement_backlog.py
- test_specflow_plan_backlog.py → test_specflow_plan_backlog.py
- test_specflow_validate_backlog.py → test_specflow_validate_backlog.py
- test_specflow_workflow_integration.py → test_specflow_workflow_integration.py
- test_specflow_e2e.py → test_specflow_e2e.py

### Phase 3: Content Updates (Text Replacements)

#### 3.1 Primary Replacements

| Pattern | Replacement | Scope |
|---------|-------------|-------|
| `/specflow:` | `/specflow:` | All files |
| `specflow:` (in commands) | `specflow:` | YAML, Python |
| `specflow_workflow` | `specflow_workflow` | All files |
| `"specflow-` | `"specflow-` | Agent references |
| `/specflow` | `/specflow` | Documentation |
| `specflow.` (namespace) | `specflow.` | Python imports |

#### 3.2 File Types to Update

**Configuration Files:**
- `specflow_workflow.yml` (root) - update remaining `/specflow:` references
- `memory/specflow_workflow.yml` → `memory/specflow_workflow.yml`
- `memory/specflow_workflow.schema.json` → `memory/specflow_workflow.schema.json`
- `schemas/specflow_workflow.schema.json` - verify content

**Python Source Code:**
- `src/specify_cli/__init__.py`
- `src/specify_cli/hooks/events.py`
- `src/specify_cli/workflow/assessor.py`
- `src/specify_cli/workflow/config.py`
- `src/specify_cli/workflow/state_guard.py`
- `src/specify_cli/task_context.py`

**Documentation Files (docs/):**
- `docs/guides/specflow-workflow-guide.md` → rename and update
- `docs/guides/specflow-backlog-workflow.md` → rename and update
- `docs/reference/specflow-security-commands.md` → rename and update
- `docs/architecture/specflow-security-architecture.md` → rename and update
- `docs/platform/specflow-security-platform.md` → rename and update
- `docs/assess/specflow-security-commands-assessment.md` → rename and update
- `docs/prd/specflow-security-commands.md` → rename and update
- `docs/diagrams/specflow-workflow.*` → rename and update
- All other docs with `/specflow` references (40+ files)

**Template Files:**
- All files in `templates/commands/specflow/` (after rename)
- Files with include paths referencing `specflow/`

**Root Files:**
- `CLAUDE.md`
- `README.md`
- `CONTRIBUTING.md`

**Backlog Files:**
- All task files with `/specflow` references (currently ~20 files)
- Archive files with historical references

**Hooks:**
- `.claude/hooks/pre-implement.sh`
- `.claude/hooks/pre-implement.py`
- `.claude/hooks/post-slash-command-emit.py`
- `.claude/hooks/test-post-slash-command-emit.py`

**Skills:**
- `.claude/skills/security-*.md` files with specflow references

**Plugin/Integration:**
- `.claude-plugin/README.md`
- `.claude-plugin/marketplace.json`
- `.claude/AGENTS-INTEGRATION.md`
- `.claude/INTEGRATION-COMPLETE.md`

### Phase 4: Include Path Updates

Update all `{{INCLUDE:...}}` paths in command templates:
```
{{INCLUDE:.claude/commands/specflow/_...}} → {{INCLUDE:.claude/commands/specflow/_...}}
```

### Phase 5: Verification

#### 5.1 Run Tests
```bash
pytest tests/ -v
```

#### 5.2 Verify No Remaining References
```bash
# Check for any remaining /specflow references
grep -r "/specflow" --include="*.md" --include="*.py" --include="*.yml" --include="*.yaml" --include="*.json" .

# Should return 0 results (except potentially historical archive files)
```

#### 5.3 Validate Workflow Configuration
```bash
specify workflow validate
```

## Execution Strategy

### Option A: Automated Script (Recommended)

Create a migration script that:
1. Creates backup of all files
2. Renames directories
3. Renames individual files
4. Performs text replacements
5. Validates changes
6. Runs tests

### Option B: Manual Step-by-Step

Execute each phase sequentially with verification after each step.

## Risks

1. **Broken Internal Links**: Include paths in templates may break
2. **Test Failures**: Tests may have hardcoded paths
3. **Documentation Links**: External references to old paths
4. **User Impact**: Users with existing projects referencing `/specflow`

## Mitigation

1. Create deprecation aliases (optional)
2. Update all documentation simultaneously
3. Clear communication in release notes
4. Provide migration guide for existing users

## Files Summary

| Category | Count | Action |
|----------|-------|--------|
| Command directories | 2 | Rename |
| Template command files | 31 | Rename dir + update content |
| GitHub agent files | 15 | Rename + update content |
| Test files | 10 | Rename + update content |
| Configuration files | 3 | Rename + update content |
| Documentation files | 50+ | Update content |
| Python source files | 6+ | Update content |
| Backlog task files | 20+ | Update content |
| Other (hooks, skills, etc.) | 15+ | Update content |

**Total estimated file changes: 150+ files**
**Total occurrences to replace: 900+**

## Decision

Proceed with the migration using the automated approach for consistency and to minimize human error.
