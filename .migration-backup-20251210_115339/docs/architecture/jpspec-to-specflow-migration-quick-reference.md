# /jpspec → /specflow Migration - Quick Reference Card

**Status**: Ready for Review
**Tasks**: task-411 through task-427

## Quick Stats

- **Files Changed**: 150+
- **Occurrences**: 912+
- **Phases**: 9
- **Validation Checkpoints**: 9
- **Estimated Time**: ~7 hours
- **Approach**: Fully Automated
- **Git Strategy**: Atomic Single Commit

## Task Sequence

```
1. task-411: Review ADR                [1h]    REVIEW
2. task-417: Implement Script          [3h]    DEVELOP
3. task-418: Phase 1 - Config          [15m]   EXECUTE
4. task-419: Phase 2 - Templates       [15m]   EXECUTE
5. task-420: Phase 3 - Symlinks        [10m]   EXECUTE
6. task-421: Phase 4 - Agents          [15m]   EXECUTE
7. task-422: Phase 5 - Tests           [15m]   EXECUTE
8. task-423: Phase 6 - Source          [10m]   EXECUTE
9. task-424: Phase 7 - Docs            [30m]   EXECUTE
10. task-425: Phase 8 - Backlog        [15m]   EXECUTE
11. task-426: Phase 9 - Validation     [30m]   VALIDATE
12. task-427: Execute Migration        [1h]    DEPLOY
```

## Phase Checklist

### Phase 1: Configuration ✓
- [ ] Rename `memory/jpspec_workflow.schema.json`
- [ ] Update schema `$id` field
- [ ] Rename `memory/jpspec_workflow.yml`
- [ ] Rename root `jpspec_workflow.yml`
- [ ] Update command patterns
- [ ] ✅ Validate: `specify workflow validate`

### Phase 2: Templates ✓
- [ ] Rename `templates/commands/jpspec/` directory
- [ ] Update `/jpspec:` → `/specflow:` in 31 files
- [ ] Update include paths
- [ ] Update workflow references
- [ ] ✅ Validate: Include path resolution

### Phase 3: Symlinks ✓
- [ ] Delete `.claude/commands/jpspec/`
- [ ] Create `.claude/commands/specflow/`
- [ ] Recreate 18 symlinks
- [ ] ✅ Validate: No broken symlinks

### Phase 4: Agents ✓
- [ ] Rename 15 agent files
- [ ] Update include paths
- [ ] Update command references
- [ ] ✅ Validate: Include resolution

### Phase 5: Tests ✓
- [ ] Rename 10 test files
- [ ] Update test content
- [ ] ✅ Validate: `pytest --collect-only`
- [ ] ✅ Validate: `pytest tests/ -v`

### Phase 6: Source ✓
- [ ] Update config references
- [ ] Update command patterns
- [ ] Update event names
- [ ] ✅ Validate: `ruff check src/`

### Phase 7: Documentation ✓
- [ ] Rename 16 doc files
- [ ] Update 50+ docs
- [ ] Update CLAUDE.md, README.md
- [ ] Update toc.yml
- [ ] ✅ Validate: Link checker

### Phase 8: Backlog ✓
- [ ] Update active tasks
- [ ] Handle archives (decide)
- [ ] Update templates
- [ ] ✅ Validate: `backlog search specflow`

### Phase 9: Final Validation ✓
- [ ] ✅ `specify workflow validate`
- [ ] ✅ `pytest tests/ -v --cov`
- [ ] ✅ Coverage maintained
- [ ] ✅ `grep -r "/jpspec"` → 0
- [ ] ✅ CLI shows /specflow
- [ ] ✅ Version bumped
- [ ] ✅ CHANGELOG.md updated
- [ ] ✅ Migration guide created

## Pattern Replacements

| Find | Replace | Files |
|------|---------|-------|
| `/jpspec:` | `/specflow:` | All |
| `jpspec_workflow` | `specflow_workflow` | Config, code, docs |
| `commands/jpspec/` | `commands/specflow/` | Templates, agents |
| `jpspec-` | `specflow-` | Agents |
| `test_jpspec_` | `test_specflow_` | Tests |
| `jpspec.` | `specflow.` | Python |

## Validation Commands

```bash
# Phase 1
specify workflow validate

# Phase 2
for f in templates/commands/specflow/*.md; do
  grep -o '{{INCLUDE:[^}]*}}' "$f" | while read inc; do
    path=$(echo "$inc" | sed 's/{{INCLUDE:\(.*\)}}/\1/')
    [ -f "$path" ] || echo "BROKEN: $path in $f"
  done
done

# Phase 3
find .claude/commands/specflow -type l -exec test ! -e {} \; -print | wc -l
# Should be 0

# Phase 4
# Same as Phase 2, but for .github/agents/specflow-*.agent.md

# Phase 5
pytest --collect-only
pytest tests/ -v

# Phase 6
ruff check src/

# Phase 7
# Link checker (manual or automated)

# Phase 8
backlog search "specflow" --plain

# Phase 9
specify workflow validate
pytest tests/ -v --cov=src/specify_cli
grep -r "/jpspec:" --include="*.md" --include="*.py" --include="*.yml" \
  --exclude-dir=archive . | wc -l
# Should be 0
```

## Rollback Commands

### Immediate (During Execution)
```bash
git reset --hard HEAD~1
git branch -D migration-jpspec-to-specflow-$(date +%Y%m%d)
```

### Post-Commit
```bash
git revert <migration-commit-hash>
```

### Emergency
```bash
git checkout pre-specflow-migration
git checkout -b emergency-rollback
```

## File Counts by Phase

| Phase | Files |
|-------|-------|
| 1. Config | 4 |
| 2. Templates | 31 |
| 3. Symlinks | 18 |
| 4. Agents | 15 |
| 5. Tests | 10 |
| 6. Source | 6+ |
| 7. Docs | 50+ |
| 8. Backlog | 20+ |

## Critical Dependencies

```
Config → Templates → Symlinks → Agents → Tests → Source → Docs → Backlog
```

**Do NOT skip or reorder phases**

## Success Criteria

- ✅ All tests pass
- ✅ Coverage maintained
- ✅ No /jpspec refs
- ✅ No broken links
- ✅ CLI shows /specflow
- ✅ Schema validates

## Emergency Contacts

- **Architect**: Review docs/adr/ADR-jpspec-to-specflow-migration-architecture.md
- **Execution Plan**: docs/architecture/jpspec-to-specflow-migration-execution-plan.md
- **Summary**: docs/architecture/jpspec-to-specflow-migration-summary.md

## Migration Script

**Location**: `scripts/bash/migrate-jpspec-to-specflow.sh` (task-417)

**Execution**:
```bash
git checkout -b migration-jpspec-to-specflow-$(date +%Y%m%d)
bash scripts/bash/migrate-jpspec-to-specflow.sh --dry-run
bash scripts/bash/migrate-jpspec-to-specflow.sh
```

## Commit Message Template

```
refactor: rename /jpspec to /specflow across codebase

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

Files changed: 150+
Occurrences replaced: 912+

Validation:
- ✅ specify workflow validate
- ✅ pytest tests/ -v (all pass)
- ✅ No broken links
- ✅ No /jpspec references remaining

Resolves: task-411, task-417, task-418, task-419, task-420, task-421,
         task-422, task-423, task-424, task-425, task-426, task-427
```

---

**Quick Reference Version**: 1.0
**Last Updated**: 2025-12-09
