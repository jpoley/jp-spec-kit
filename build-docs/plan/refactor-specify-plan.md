# Implementation Plan: Refactor specify-cli to flowspec-cli

**Beads Epic**: spec-l8o
**Related ADR**: [ADR-refactor-specify-to-flowspec](../adr/ADR-refactor-specify-to-flowspec.md)
**Status**: Planning Complete
**Created**: 2024-12-15

## Executive Summary

Rename all references from `specify-cli`/`specify` to `flowspec-cli`/`flowspec` across the codebase. This is a breaking change with no backward compatibility, requiring a phased approach.

## File Inventory

### Documentation Files (Phase 2)

#### build-docs/ (~15 files, ~45 references)
| File | References | Pattern |
|------|------------|---------|
| research/spec-kitty.md | 1 | specify-cli |
| research/opcode.md | 2 | specify-cli |
| adr/design-command-migration-path.md | 2 | specify-cli |
| adr/upgrade-commands-plan.md | 2 | specify-cli |
| adr/ADR-007-unified-security-finding-format.md | 1 | specify-cli |
| evaluations/claude-review.md | 4 | specify-cli |
| specs/architecture-enhancements-functional.md | 1 | specify-cli |
| platform/muckross-security-platform-plan-v2.md | 4 | specify-cli |
| platform/security-cicd-integration.md | 16+ | specify-cli |
| platform/flowspec-security-platform.md | 6 | specify-cli |
| prd/MARKETPLACE.md | 2 | specify-cli |

#### user-docs/ (~10 files, ~35 references)
| File | References | Pattern |
|------|------------|---------|
| user-guides/constitution-validation.md | 1 | specify-cli |
| user-guides/backlog-user-guide.md | 1 | specify-cli |
| user-guides/security-cicd-integration.md | 20+ | specify-cli |
| user-guides/workflow-customization.md | 1 | specify-cli |
| user-guides/release-workflow-fix.md | 1 | specify-cli |
| user-guides/workflow-troubleshooting.md | 3 | specify-cli |
| user-guides/security-dast.md | 2 | specify-cli |
| installation.md | 1 | specify-cli |

#### backlog/ (~15 files)
| File | References |
|------|------------|
| task-084, task-437.01, task-248, task-254 | Multiple |
| task-081, task-222, task-079, task-310 | Multiple |
| task-310.02, task-251 | Multiple |
| archive/task-085, task-078, task-308, task-296, task-080 | Multiple |
| docs/claude-ideas.md | 1 |

#### Root Documentation
| File | References |
|------|------------|
| README.md | 1 |
| CLAUDE.md | 1 |
| AGENTS.md | 1 |
| .spec-kit-compatibility.yml | 1 |
| .claude-plugin/README.md | 2 |

### Source Code Files (Phase 3)

#### Directory Rename
```
src/specify_cli/ → src/flowspec_cli/
```

#### Files with Code References
| File | References | Type |
|------|------------|------|
| src/specify_cli/__init__.py | 8 | Comments, strings, metadata |
| src/specify_cli/security/exporters/sarif.py | 1 | URL string |
| src/specify_cli/security/integrations/cicd.py | 3 | pip install commands |
| src/specify_cli/security/adapters/dast.py | 3 | pip install commands |
| src/specify_cli/security/dast/scanner.py | 1 | pip install command |
| src/specify_cli/security/dast/crawler.py | 1 | pip install command |

#### pyproject.toml
```toml
# Current
name = "specify-cli"
[project.scripts]
specify = "specify_cli:main"

# Target
name = "flowspec-cli"
[project.scripts]
flowspec = "flowspec_cli:main"
```

#### Test Files
| File | Assertions |
|------|------------|
| tests/security/test_security_workflows.py | 2 |
| tests/test_github_auth.py | 2 |

## Task Breakdown by Phase

### Phase 1: Planning (This PR) - spec-l8o.1
- [x] Create ADR document
- [x] Create this plan document
- [x] Create JSONL decision log
- [x] Create beads tasks with dependencies
- [x] Create and push planning branch
- [ ] Verify CI passes
- [ ] PR ready for merge

### Phase 2: Documentation Updates - spec-l8o.2 through spec-l8o.5

**Task spec-l8o.2**: Update build-docs/
```bash
# Pattern for sed replacement
find build-docs -type f \( -name "*.md" -o -name "*.yaml" \) -exec \
  sed -i '' 's/specify-cli/flowspec-cli/g' {} \;
```

**Task spec-l8o.3**: Update user-docs/
```bash
find user-docs -type f \( -name "*.md" -o -name "*.yaml" \) -exec \
  sed -i '' 's/specify-cli/flowspec-cli/g' {} \;
```

**Task spec-l8o.4**: Update backlog/
```bash
find backlog -type f -name "*.md" -exec \
  sed -i '' 's/specify-cli/flowspec-cli/g' {} \;
```

**Task spec-l8o.5**: Update root documentation
```bash
for file in README.md CLAUDE.md AGENTS.md .spec-kit-compatibility.yml; do
  sed -i '' 's/specify-cli/flowspec-cli/g' "$file"
done
sed -i '' 's/specify-cli/flowspec-cli/g' .claude-plugin/README.md
```

### Phase 3: Code Changes - spec-l8o.6 through spec-l8o.8

**Task spec-l8o.6**: Rename src/specify_cli/
```bash
# 1. Rename directory
git mv src/specify_cli src/flowspec_cli

# 2. Update imports in all Python files
find . -name "*.py" -exec sed -i '' 's/from specify_cli/from flowspec_cli/g' {} \;
find . -name "*.py" -exec sed -i '' 's/import specify_cli/import flowspec_cli/g' {} \;
```

**Task spec-l8o.7**: Update pyproject.toml
```toml
[project]
name = "flowspec-cli"

[project.scripts]
flowspec = "flowspec_cli:main"
```

**Task spec-l8o.8**: Update test assertions
```python
# tests/security/test_security_workflows.py
assert "uv tool install flowspec-cli" not in workflow_content

# tests/test_github_auth.py
assert headers["User-Agent"] == "flowspec/flowspec-cli"
```

### Phase 4: Migration - spec-l8o.9

Create migration guide documenting:
1. Uninstall old package: `uv tool uninstall specify-cli`
2. Install new package: `uv tool install flowspec-cli --from git+...`
3. Update any shell aliases
4. Clean up old data directories

## Verification Checklist

### After Each Phase
- [ ] All tests pass (`pytest tests/`)
- [ ] Linting passes (`ruff check . --fix && ruff format .`)
- [ ] CLI works (`flowspec --help`)
- [ ] Installation works from git

### After Full Completion
- [ ] Fresh install works
- [ ] No references to `specify-cli` remain
- [ ] Documentation is consistent
- [ ] Migration guide is accurate

## Rollback Plan

If issues are discovered:
1. Revert the commits in reverse order
2. Phase 3 can be rolled back independently of Phase 2
3. Documentation changes are low-risk and easily reversible

## Timeline

| Phase | Tasks | Estimated Effort |
|-------|-------|-----------------|
| Phase 1 | spec-l8o.1 | Complete |
| Phase 2 | spec-l8o.2-5 | 1-2 hours |
| Phase 3 | spec-l8o.6-8 | 2-3 hours |
| Phase 4 | spec-l8o.9 | 1 hour |

**Total**: ~5-7 hours of focused work

## Success Criteria

1. `grep -r "specify-cli" --include="*.py" --include="*.md"` returns no results
2. `uv tool install flowspec-cli --from git+...` works
3. `flowspec --help` shows correct branding
4. All CI/CD pipelines pass
5. Migration documentation published
