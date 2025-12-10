# ADR: /jpspec → /specflow Migration Architecture

**Date**: 2025-12-09
**Status**: Proposed
**Supersedes**: docs/adr/jpspec-to-specflow-migration-plan.md
**Author**: Enterprise Software Architect

## Executive Summary

This ADR provides comprehensive architectural guidance for migrating 912+ occurrences of `/jpspec` to `/specflow` across 150+ files in the JP Spec Kit codebase. The migration requires careful orchestration due to complex file dependencies, symlink structures, include paths, and extensive cross-references between documentation, code, and configuration.

## Context

### Scope of Change

**File Categories Affected:**
- **31** command template files (templates/commands/jpspec/)
- **15** GitHub agent files (.github/agents/jpspec-*.agent.md)
- **10** test files (tests/test_jpspec_*.py)
- **18** symlinks (.claude/commands/jpspec/ → templates/commands/jpspec/)
- **3** configuration files (jpspec_workflow.yml, jpspec_workflow.schema.json)
- **50+** documentation files (docs/)
- **6+** Python source files (src/specify_cli/)
- **20+** backlog task files
- **100+** include path references ({{INCLUDE:.claude/commands/jpspec/...}})

**Pattern Types to Replace:**
1. `/jpspec:` → `/specflow:` (slash commands)
2. `jpspec_workflow` → `specflow_workflow` (configuration)
3. `jpspec-` → `specflow-` (file names, agent references)
4. `INCLUDE:.claude/commands/jpspec/` → `INCLUDE:.claude/commands/specflow/`
5. `test_jpspec_` → `test_specflow_` (test files)

### Critical Architectural Constraints

1. **Symlink Integrity**: 18 symlinks in `.claude/commands/jpspec/` must maintain valid targets after template directory rename
2. **Include Path Cascades**: Include paths in templates are used by agent files, which are used by other templates - breaking order matters
3. **Schema Validation**: `jpspec_workflow.schema.json` has hardcoded schema ID that must match filename
4. **Test Discovery**: pytest discovers tests by filename pattern - renaming test files changes test discovery behavior
5. **Git History**: Maintaining file history through renames requires specific git strategies
6. **User Impact**: Existing projects using `/jpspec` commands need deprecation strategy

## Migration Architecture

### Phase Dependency Graph

```
Phase 1: Configuration Foundation
    ├── 1.1 Rename workflow schema (jpspec_workflow.schema.json)
    ├── 1.2 Update schema $id field
    └── 1.3 Rename workflow config (jpspec_workflow.yml)
         ↓
Phase 2: Template Infrastructure
    ├── 2.1 Rename templates/commands/jpspec/ directory
    ├── 2.2 Update include paths in all template files
    └── 2.3 Update command: fields in template frontmatter
         ↓
Phase 3: Local Commands (Symlinks)
    ├── 3.1 Delete .claude/commands/jpspec/ directory
    ├── 3.2 Recreate .claude/commands/specflow/ directory
    └── 3.3 Recreate symlinks pointing to new template paths
         ↓
Phase 4: GitHub Agents
    ├── 4.1 Rename agent files (jpspec-*.agent.md → specflow-*.agent.md)
    └── 4.2 Update include paths and command references in agent files
         ↓
Phase 5: Test Suite
    ├── 5.1 Rename test files (test_jpspec_*.py → test_specflow_*.py)
    ├── 5.2 Update test content (assertions, fixtures, docstrings)
    └── 5.3 Run full test suite for validation
         ↓
Phase 6: Source Code
    ├── 6.1 Update Python imports and references
    ├── 6.2 Update workflow config loading logic
    └── 6.3 Update CLI command definitions
         ↓
Phase 7: Documentation
    ├── 7.1 Rename jpspec-specific doc files
    ├── 7.2 Update all /jpspec references in docs
    ├── 7.3 Update diagrams and images
    └── 7.4 Update table of contents (toc.yml)
         ↓
Phase 8: Backlog & Historical Files
    ├── 8.1 Update active backlog tasks
    ├── 8.2 Update archived tasks (optional)
    └── 8.3 Update task templates
         ↓
Phase 9: Validation & Cleanup
    ├── 9.1 Run workflow schema validation
    ├── 9.2 Run full test suite
    ├── 9.3 Verify no broken links
    ├── 9.4 Verify no remaining /jpspec references
    └── 9.5 Update version/changelog
```

### Critical Path Analysis

**Critical Path Files (Must be updated first):**
1. `memory/jpspec_workflow.schema.json` - Schema defines validation rules
2. `memory/jpspec_workflow.yml` - Config loaded by all workflows
3. `templates/commands/jpspec/*.md` - Source templates for symlinks
4. `.claude/commands/jpspec/` - Symlinks consumed by Claude Code

**Dependent Files (Rely on critical path):**
1. `.github/agents/jpspec-*.agent.md` - Include templates via {{INCLUDE}}
2. `tests/test_jpspec_*.py` - Import config and test command execution
3. `src/specify_cli/workflow/config.py` - Loads jpspec_workflow.yml
4. Documentation files - Reference commands and config paths

**Independent Files (Can update in any order):**
1. Backlog task files - Historical references, not executed
2. Archive documentation - Historical, not linked
3. Example scripts - Standalone demonstrations
4. Deprecated template files (_DEPRECATED_*.md)

### Risk Assessment Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Broken Symlinks** | High | Critical | Phase ordering: templates before symlinks |
| **Include Path Failures** | High | Critical | Automated validation after each phase |
| **Test Discovery Breaks** | Medium | High | Verify pytest collection after rename |
| **Schema Validation Fails** | Medium | High | Update $id field atomically with rename |
| **Git History Loss** | Low | Medium | Use `git mv` for renames |
| **User Confusion** | High | Low | Deprecation aliases + migration guide |
| **Incomplete Migration** | Medium | High | Comprehensive grep validation |

## Decision: Automated vs Manual Migration

### Option A: Fully Automated Script ✅ **RECOMMENDED**

**Approach**: Single bash script executing all phases with rollback capability

**Advantages:**
- **Consistency**: All replacements follow identical patterns
- **Speed**: Complete migration in seconds vs hours
- **Auditability**: Script serves as executable documentation
- **Repeatability**: Can test in branches, rollback if needed
- **Error Prevention**: No human typos or missed files
- **Atomic Execution**: All-or-nothing via git transactions

**Disadvantages:**
- **Upfront Complexity**: Script development takes 2-4 hours
- **Testing Required**: Must test in isolated branch first
- **Edge Cases**: May miss nuanced context-specific replacements

**Implementation:**
```bash
#!/usr/bin/env bash
# scripts/bash/migrate-jpspec-to-specflow.sh

set -euo pipefail

# Backup strategy
git checkout -b migration-jpspec-to-specflow-$(date +%Y%m%d)
git add -A
git commit -m "chore: pre-migration snapshot"

# Phase 1: Configuration
git mv memory/jpspec_workflow.schema.json memory/specflow_workflow.schema.json
sed -i 's|jpspec_workflow.schema.json|specflow_workflow.schema.json|g' memory/specflow_workflow.schema.json
git mv memory/jpspec_workflow.yml memory/specflow_workflow.yml

# Phase 2: Templates
git mv templates/commands/jpspec templates/commands/specflow
find templates/commands/specflow -type f -exec sed -i 's|/jpspec:|/specflow:|g' {} +
find templates/commands/specflow -type f -exec sed -i 's|commands/jpspec/|commands/specflow/|g' {} +

# Phase 3: Symlinks
rm -rf .claude/commands/jpspec
mkdir -p .claude/commands/specflow
# Recreate symlinks...

# ... (continue for all phases)

# Validation
pytest tests/ -v
specify workflow validate
grep -r "/jpspec" . || echo "✓ No /jpspec references remaining"
```

### Option B: Semi-Automated (Phases)

**Approach**: Scripts for critical phases, manual for documentation

**Use Case**: If automation concerns exist, automate risky parts (symlinks, includes), manual for docs

### Option C: Fully Manual ❌ **NOT RECOMMENDED**

**Rationale**: 912+ occurrences across 150+ files creates unacceptable human error risk

## File Categorization

### Tier 1: Critical Infrastructure (Update First)

**Configuration Files:**
```
memory/jpspec_workflow.schema.json → memory/specflow_workflow.schema.json
memory/jpspec_workflow.yml → memory/specflow_workflow.yml
jpspec_workflow.yml → specflow_workflow.yml (root)
```

**Schema Update Required:**
```json
{
  "$id": "https://jp-spec-kit/schemas/specflow_workflow.schema.json",  // Changed
  "title": "JP Spec Kit Workflow Configuration",  // Keep
  "properties": {
    "workflows": {
      "additionalProperties": {
        "properties": {
          "command": {
            "pattern": "^/specflow:[a-z][a-z0-9_-]*$"  // Changed
          }
        }
      }
    }
  }
}
```

### Tier 2: Template Source Files

**Directory Rename:**
```bash
templates/commands/jpspec/ → templates/commands/specflow/
```

**Files (31 total):**
- assess.md, implement.md, init.md, operate.md, plan.md
- research.md, reset.md, specify.md, validate.md, prune-branch.md
- security_fix.md, security_report.md, security_triage.md
- security_web.md, security_workflow.md
- _backlog-instructions.md, _constitution-check.md, _workflow-state.md
- 13 _DEPRECATED_*.md files

**Content Updates:**
- Command declarations: `/jpspec:assess` → `/specflow:assess`
- Include paths: `{{INCLUDE:.claude/commands/jpspec/...}}` → `{{INCLUDE:.claude/commands/specflow/...}}`

### Tier 3: Symlinks (.claude/commands/)

**Current Structure (18 symlinks):**
```
.claude/commands/jpspec/assess.md → ../../../templates/commands/jpspec/assess.md
.claude/commands/jpspec/init.md → ../../../templates/commands/jpspec/init.md
# ... (16 more symlinks)
```

**Migration Strategy:**
```bash
# Delete old directory
rm -rf .claude/commands/jpspec

# Create new directory
mkdir -p .claude/commands/specflow

# Recreate symlinks with updated paths
for cmd in assess implement init operate plan research reset specify validate \
           prune-branch security_fix security_report security_triage \
           security_web security_workflow _backlog-instructions \
           _constitution-check _workflow-state; do
  ln -s ../../../templates/commands/specflow/${cmd}.md \
        .claude/commands/specflow/${cmd}.md
done
```

### Tier 4: GitHub Agents (15 files)

**Rename Pattern:**
```
.github/agents/jpspec-{command}.agent.md → .github/agents/specflow-{command}.agent.md
```

**Files:**
- jpspec-assess.agent.md → specflow-assess.agent.md
- jpspec-implement.agent.md → specflow-implement.agent.md
- jpspec-init.agent.md → specflow-init.agent.md
- jpspec-operate.agent.md → specflow-operate.agent.md
- jpspec-plan.agent.md → specflow-plan.agent.md
- jpspec-prune-branch.agent.md → specflow-prune-branch.agent.md
- jpspec-research.agent.md → specflow-research.agent.md
- jpspec-reset.agent.md → specflow-reset.agent.md
- jpspec-security_fix.agent.md → specflow-security_fix.agent.md
- jpspec-security_report.agent.md → specflow-security_report.agent.md
- jpspec-security_triage.agent.md → specflow-security_triage.agent.md
- jpspec-security_web.agent.md → specflow-security_web.agent.md
- jpspec-security_workflow.agent.md → specflow-security_workflow.agent.md
- jpspec-specify.agent.md → specflow-specify.agent.md
- jpspec-validate.agent.md → specflow-validate.agent.md

**Content Updates Per File:**
- Include paths: `{{INCLUDE:.claude/commands/jpspec/...}}`
- Command references: `/jpspec:command`
- Identity references: `@jpspec-command` (verify if needed)

### Tier 5: Test Suite (10 files)

**Rename Pattern:**
```
tests/test_jpspec_{name}.py → tests/test_specflow_{name}.py
```

**Files:**
- test_jpspec_assess.py → test_specflow_assess.py
- test_jpspec_backlog_integration.py → test_specflow_backlog_integration.py
- test_jpspec_e2e.py → test_specflow_e2e.py
- test_jpspec_implement_backlog.py → test_specflow_implement_backlog.py
- test_jpspec_operate_backlog.py → test_specflow_operate_backlog.py
- test_jpspec_plan_backlog.py → test_specflow_plan_backlog.py
- test_jpspec_research_backlog.py → test_specflow_research_backlog.py
- test_jpspec_specify_backlog.py → test_specflow_specify_backlog.py
- test_jpspec_validate_backlog.py → test_specflow_validate_backlog.py
- test_jpspec_workflow_integration.py → test_specflow_workflow_integration.py

**Content Pattern Updates:**
```python
# Before
WORKFLOW_CONFIG = "jpspec_workflow.yml"
cmd = "/jpspec:assess"
assert "jpspec_workflow" in result

# After
WORKFLOW_CONFIG = "specflow_workflow.yml"
cmd = "/specflow:assess"
assert "specflow_workflow" in result
```

### Tier 6: Python Source Code (6+ files)

**Files:**
- `src/specify_cli/__init__.py`
- `src/specify_cli/workflow/config.py`
- `src/specify_cli/workflow/state_guard.py`
- `src/specify_cli/workflow/assessor.py`
- `src/specify_cli/hooks/events.py`
- `src/specify_cli/task_context.py`

**Pattern Updates:**
```python
# Config loading
DEFAULT_WORKFLOW_CONFIG = "jpspec_workflow.yml"  # → specflow_workflow.yml
SCHEMA_FILE = "jpspec_workflow.schema.json"     # → specflow_workflow.schema.json

# Command patterns
JPSPEC_COMMAND_PATTERN = r"/jpspec:(\w+)"       # → /specflow:(\w+)

# Event names
"jpspec.assess.complete"                         # → "specflow.assess.complete"
```

### Tier 7: Documentation (50+ files)

**Rename Files:**
```
docs/guides/jpspec-workflow-guide.md → docs/guides/specflow-workflow-guide.md
docs/guides/jpspec-backlog-workflow.md → docs/guides/specflow-backlog-workflow.md
docs/reference/jpspec-security-commands.md → docs/reference/specflow-security-commands.md
docs/architecture/jpspec-security-architecture.md → docs/architecture/specflow-security-architecture.md
docs/platform/jpspec-security-platform.md → docs/platform/specflow-security-platform.md
docs/assess/jpspec-security-commands-assessment.md → docs/assess/specflow-security-commands-assessment.md
docs/prd/jpspec-security-commands.md → docs/prd/specflow-security-commands.md
docs/diagrams/jpspec-workflow.* → docs/diagrams/specflow-workflow.*
```

**Content Pattern Updates:**
- Inline command references: `/jpspec:command` → `/specflow:command`
- Config file references: `jpspec_workflow.yml` → `specflow_workflow.yml`
- File path references: `commands/jpspec/` → `commands/specflow/`
- Cross-reference links: `[workflow guide](jpspec-workflow-guide.md)` → `[workflow guide](specflow-workflow-guide.md)`

**High-Impact Files (Update Priority):**
1. `CLAUDE.md` - Primary AI instruction file
2. `README.md` - User-facing documentation
3. `docs/index.md` - Documentation entry point
4. `docs/guides/workflow-*.md` - Core workflow docs
5. `docs/reference/` - API reference docs

### Tier 8: Backlog & Historical (20+ files)

**Active Backlog Tasks:**
- Update tasks with `/jpspec` command references
- Update task descriptions and acceptance criteria
- Preserve task IDs and status

**Archived Tasks:**
- **DECISION POINT**: Update or preserve?
  - **Option A**: Update for consistency (full migration)
  - **Option B**: Leave as historical artifacts (partial migration)
  - **RECOMMENDATION**: Update archived tasks for future searchability

**Pattern Updates:**
```markdown
# Task acceptance criteria
- [ ] Run `/jpspec:assess` on feature  # → /specflow:assess
- [ ] Create `jpspec_workflow.yml`     # → specflow_workflow.yml
```

## Rollback Strategy

### Rollback Levels

**Level 1: Immediate Rollback (Within 1 hour)**
```bash
# If migration fails during execution
git reset --hard HEAD~1
git branch -D migration-jpspec-to-specflow-YYYYMMDD
# Resume from main branch
```

**Level 2: Post-Commit Rollback (Within 24 hours)**
```bash
# If issues discovered after merge
git revert <commit-hash>
# Or create fix-forward commits for specific issues
```

**Level 3: Emergency Rollback (Production Issues)**
```bash
# Tag current state before migration
git tag pre-specflow-migration

# If critical production issues
git checkout pre-specflow-migration
git checkout -b emergency-rollback
git push origin emergency-rollback --force
```

### Validation Checkpoints

**Checkpoint 1: After Configuration Rename**
```bash
specify workflow validate
# Must pass before proceeding
```

**Checkpoint 2: After Template Updates**
```bash
# Verify all include paths resolve
for template in templates/commands/specflow/*.md; do
  grep -o '{{INCLUDE:[^}]*}}' "$template" | while read -r include; do
    path=$(echo "$include" | sed 's/{{INCLUDE:\(.*\)}}/\1/')
    [ -f "$path" ] || echo "BROKEN: $path in $template"
  done
done
```

**Checkpoint 3: After Symlink Recreation**
```bash
# Verify all symlinks valid
find .claude/commands/specflow -type l -exec test ! -e {} \; -print
# Should return empty (no broken symlinks)
```

**Checkpoint 4: After Test Rename**
```bash
pytest tests/ --collect-only
# Verify all tests discovered
pytest tests/ -v
# All tests must pass
```

**Checkpoint 5: Final Validation**
```bash
# No /jpspec references (except archives if preserved)
grep -r "/jpspec:" --include="*.md" --include="*.py" --include="*.yml" . \
  --exclude-dir=archive | wc -l
# Should be 0 (or low count if archives preserved)

# Schema validation
specify workflow validate

# Full test suite
pytest tests/ -v --cov=src/specify_cli

# Integration test
specify init --help  # Should show /specflow commands
```

### Git Strategy

**Single Commit vs Multi-Commit**

**Option A: Atomic Single Commit ✅ RECOMMENDED**
```bash
git add -A
git commit -m "refactor: rename /jpspec to /specflow across codebase

BREAKING CHANGE: All /jpspec commands renamed to /specflow

- Rename jpspec_workflow.yml → specflow_workflow.yml
- Rename jpspec_workflow.schema.json → specflow_workflow.schema.json
- Rename templates/commands/jpspec/ → templates/commands/specflow/
- Rename .github/agents/jpspec-*.agent.md → specflow-*.agent.md
- Rename tests/test_jpspec_*.py → test_specflow_*.py
- Update 912+ references across 150+ files
- Recreate symlinks in .claude/commands/specflow/
- Update include paths in templates and agents
- Update documentation and guides

Affects: Configuration, templates, agents, tests, docs, source code

Resolves: #XXX
"
```

**Advantages:**
- Single rollback point
- Clear atomic change
- Preserves bisectability
- Easier to review as one change

**Option B: Multi-Phase Commits**
```bash
# Commit 1: Configuration
git add memory/
git commit -m "refactor: rename jpspec_workflow to specflow_workflow"

# Commit 2: Templates
git add templates/
git commit -m "refactor: rename jpspec templates to specflow"

# ... (5-9 commits total)
```

**Advantages:**
- Easier to review in smaller chunks
- Can rollback individual phases
- Better for learning/auditing

**Disadvantages:**
- Leaves codebase in broken state between commits
- Harder to bisect issues
- More complex rollback

**DECISION**: Use atomic single commit for production migration

## Deprecation Strategy (Optional)

### User-Facing Aliases

If backward compatibility is critical:

```bash
# .claude/commands/jpspec/ → symlinks to .claude/commands/specflow/
# Maintains /jpspec:command functionality temporarily

# Add deprecation warnings
echo '⚠️  DEPRECATED: Use /specflow:command instead of /jpspec:command' >> templates/commands/jpspec/*.md
```

**Deprecation Timeline:**
- **v0.0.140**: Deprecation warnings added, both commands work
- **v0.0.145**: Remove /jpspec commands, migration guide published
- **v1.0.0**: Full removal, clean slate

### Migration Guide for Users

Create `docs/guides/jpspec-to-specflow-migration.md`:

```markdown
# Migrating from /jpspec to /specflow

## For Existing Projects

1. **Update .claude/commands/ symlinks**
2. **Rename workflow config**: `jpspec_workflow.yml` → `specflow_workflow.yml`
3. **Update custom templates** with include path changes
4. **Search and replace** in project docs

## Command Mapping

| Old Command | New Command |
|-------------|-------------|
| /jpspec:assess | /specflow:assess |
| /jpspec:specify | /specflow:specify |
| ... | ... |
```

## Implementation Backlog Tasks

I will now create atomic backlog tasks for each phase of this migration.

## Conclusion

**RECOMMENDATION**: Proceed with **fully automated migration** using atomic single commit strategy.

**Rationale:**
1. **Scale**: 912+ occurrences across 150+ files makes manual error-prone
2. **Consistency**: Automated replacements ensure uniform patterns
3. **Testability**: Can test in branch, rollback cleanly if needed
4. **Auditability**: Script serves as executable documentation
5. **Speed**: Entire migration completes in minutes vs days

**Next Steps:**
1. Review and approve this ADR
2. Create migration script (`scripts/bash/migrate-jpspec-to-specflow.sh`)
3. Create backlog tasks for implementation and validation
4. Execute migration in feature branch
5. Comprehensive testing and validation
6. Merge to main with release notes
