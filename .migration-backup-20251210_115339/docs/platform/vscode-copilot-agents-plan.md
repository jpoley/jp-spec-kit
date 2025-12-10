# VS Code Copilot Agent Handoffs - Technical Plan

**Feature**: VS Code Copilot Agent Support with SDD Workflow Handoffs
**Status**: Planned
**Date**: 2025-12-08
**Related Tasks**: task-326 to task-336

---

## Executive Summary

This plan enables JP Spec Kit to work with VS Code GitHub Copilot in addition to Claude Code CLI. The `.claude/commands/` directory remains the single source of truth, with `.github/agents/` generated via automated transformation including workflow handoffs.

**Business Impact**:
- Market expansion to VS Code's 20M+ developers
- Platform resilience (no single AI vendor lock-in)
- Consistent SDD workflow experience across platforms

---

## 1. Architecture Overview

### 1.1 Data Flow

```
templates/commands/*.md (canonical source)
       │
       ├──> .claude/commands/*.md (symlinks, runtime include resolution)
       │
       └──> .github/agents/*.agent.md (generated, pre-resolved includes, handoffs)
```

### 1.2 Key Differences

| Aspect | Claude Code | VS Code Copilot |
|--------|-------------|-----------------|
| Directory | `.claude/commands/` | `.github/agents/` |
| File extension | `.md` | `.agent.md` |
| Frontmatter | `description:` only | `name:`, `description:`, `tools:`, `handoffs:` |
| Include resolution | Runtime `{{INCLUDE:}}` | Pre-resolved (embedded) |
| Workflow transitions | None | `handoffs:` array |

### 1.3 File Counts

- **Jpspec commands**: 15 files (workflow orchestration)
- **Speckit commands**: 8 files (utilities)
- **Total**: 23 agent files to generate

---

## 2. Handoff Architecture

### 2.1 SDD Workflow State Transitions

```
assess → specify → research → plan → implement → validate → operate
                      ↑         │
                      └─────────┘ (research optional)
```

### 2.2 Handoff Configuration by Agent

| Agent | Handoff Label | Target Agent |
|-------|---------------|--------------|
| jpspec-assess | ✓ Assessment Complete → Specify Requirements | jpspec-specify |
| jpspec-specify | ✓ Specification Complete → Conduct Research | jpspec-research |
| jpspec-specify | ✓ Specification Complete → Create Technical Design | jpspec-plan |
| jpspec-research | ✓ Research Complete → Create Technical Design | jpspec-plan |
| jpspec-plan | ✓ Planning Complete → Begin Implementation | jpspec-implement |
| jpspec-implement | ✓ Implementation Complete → Run Validation | jpspec-validate |
| jpspec-validate | ✓ Validation Complete → Deploy to Production | jpspec-operate |
| jpspec-operate | (none - terminal state) | - |
| speckit-* | (none - utilities) | - |

### 2.3 Handoff YAML Format

```yaml
handoffs:
  - label: "✓ Assessment Complete → Specify Requirements"
    agent: "jpspec-specify"
    prompt: "The assessment is complete. Based on the assessment, create detailed product requirements."
    send: false
```

**Key Design Decisions**:
- `send: false` - Users review prompt before proceeding
- Checkmark (✓) indicates phase completion
- Arrow (→) shows next step
- Context-aware prompts reference previous phase

---

## 3. Script Architecture: sync-copilot-agents.sh

### 3.1 CLI Interface

```bash
sync-copilot-agents.sh [OPTIONS]

Options:
  --dry-run     Show what would be generated without writing
  --validate    Check if .github/agents/ matches expected output (exit 2 if drift)
  --force       Overwrite files without confirmation
  --verbose     Show detailed processing information
  --help        Show usage
```

### 3.2 Processing Pipeline

1. **Discover**: Find all `.md` files in `.claude/commands/{jpspec,speckit}/`
2. **Filter**: Skip partials (files starting with `_`)
3. **Resolve**: Follow symlinks to actual template paths
4. **Parse**: Extract frontmatter and body
5. **Expand**: Resolve `{{INCLUDE:path}}` directives (recursive, max depth 3)
6. **Transform**: Generate enhanced frontmatter (name, tools, handoffs)
7. **Write**: Output to `.github/agents/{namespace}-{command}.agent.md`
8. **Validate**: Check file count, YAML validity, no unresolved includes

### 3.3 Include Resolution Algorithm

```
resolve_includes(content, depth=0):
    if depth > 3: ERROR "Max depth exceeded"

    for each {{INCLUDE:path}} in content:
        included = read_file(path)
        included = resolve_includes(included, depth+1)
        content = replace({{INCLUDE:path}}, included)

    return content
```

### 3.4 Performance Requirements

- **Sync time**: < 2 seconds for 23 commands
- **Per-file processing**: < 100ms
- **Include resolution**: < 50ms per include

---

## 4. CI/CD Pipeline

### 4.1 GitHub Actions Workflow

**File**: `.github/workflows/validate-agent-sync.yml`

**Triggers**:
- PR changes to `.claude/commands/**/*.md`
- PR changes to `.github/agents/**/*.agent.md`
- Push to main with command changes

**Matrix**:
- ubuntu-latest
- macos-latest
- windows-latest

**Steps**:
1. Checkout code
2. Install dependencies (yq)
3. Run `sync-copilot-agents.sh --validate`
4. Run smoke tests
5. Check for drift (fail if generated differs from committed)

### 4.2 Drift Detection

```bash
# Regenerate
scripts/bash/sync-copilot-agents.sh --force

# Compare
if ! git diff --exit-code .github/agents/; then
    echo "ERROR: Drift detected"
    exit 2
fi
```

---

## 5. Git Hook Integration

### 5.1 Pre-Commit Hook

**File**: `.specify/hooks/hooks.yaml`

```yaml
hooks:
  pre-commit:
    - name: sync-copilot-agents
      trigger:
        paths:
          - ".claude/commands/**/*.md"
      action: scripts/bash/sync-copilot-agents.sh
      auto_stage: true
      fail_on_error: true
```

### 5.2 Hook Behavior

1. Detect staged `.claude/commands/**/*.md` files
2. Run sync script
3. Auto-stage generated `.github/agents/*.agent.md` files
4. Show summary: "Synced N agent files"
5. Bypass with `git commit --no-verify`

---

## 6. Tool Mapping

### 6.1 Jpspec Commands (Full Workflow)

```yaml
tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Grep"
  - "Glob"
  - "Bash"
  - "mcp__backlog__*"
  - "mcp__serena__*"
  - "Skill"
```

### 6.2 Speckit Commands (Utilities)

```yaml
tools:
  - "Read"
  - "Write"
  - "Grep"
  - "Glob"
  - "mcp__backlog__*"
```

---

## 7. Validation Checks

### 7.1 Pre-Generation

- [ ] All 23 source files exist
- [ ] All include targets exist
- [ ] No circular references
- [ ] Valid YAML frontmatter in sources

### 7.2 Post-Generation

- [ ] Exactly 23 `.agent.md` files created
- [ ] No `{{INCLUDE:}}` strings in output
- [ ] Valid YAML frontmatter in all files
- [ ] Required fields present: `name`, `description`, `target`, `tools`, `handoffs`
- [ ] All handoff targets reference existing agents
- [ ] No duplicate agent names

---

## 8. Implementation Tasks

### Planning Tasks (workflow:Planned)

| Task | Description |
|------|-------------|
| task-326 | Design: sync-copilot-agents.sh Script Architecture |
| task-327 | Design: CI/CD Pipeline for Agent Sync Validation |
| task-328 | Design: Git Hook Integration for Agent Sync |

### Phase 1: Foundation (HIGH priority)

| Task | Description | Dependencies |
|------|-------------|--------------|
| task-329 | Create `.github/agents/` directory structure | None |
| task-330 | Convert jpspec commands to Copilot format | task-329 |
| task-331 | Convert speckit commands to Copilot format | task-329 |

### Phase 2: Automation (HIGH priority)

| Task | Description | Dependencies |
|------|-------------|--------------|
| task-332 | Build sync-copilot-agents.sh script | task-330, task-331 |
| task-333 | Test commands in VS Code and Insiders | task-330, task-331 |

### Phase 3: Quality Gates (MEDIUM priority)

| Task | Description | Dependencies |
|------|-------------|--------------|
| task-334 | Create pre-commit hook for agent sync | task-332 |
| task-335 | Add CI check for agent sync drift | task-332 |

### Phase 4: Documentation (MEDIUM priority)

| Task | Description | Dependencies |
|------|-------------|--------------|
| task-336 | Update documentation for VS Code Copilot support | All above |

---

## 9. Architecture Decision Records

### ADR-001: Source of Truth Location

**Decision**: `.claude/commands/` is the canonical source. `.github/agents/` is generated.

**Rationale**:
- Single edit point prevents divergence
- Generation can be re-run anytime
- Easy to add future platforms (IntelliJ, Cursor)

### ADR-002: Include Resolution Strategy

**Decision**: Pre-resolve all includes during generation (embed content).

**Rationale**:
- Copilot agents must be self-contained
- No runtime resolution overhead
- Portable without external dependencies

### ADR-003: Workflow State to Handoff Mapping

**Decision**: Map SDD phases to Copilot handoffs with `send: false`.

**Rationale**:
- Guided workflow improves discoverability
- Users review prompts before proceeding
- Branching support (specify → research OR plan)

### ADR-004: Tool Specification Strategy

**Decision**: Use MCP wildcards (`mcp__backlog__*`) for tool access.

**Rationale**:
- Future-proof against new MCP tools
- Clear capability boundaries per command type
- Minimal privileges for utility commands

---

## 10. Success Criteria

### Technical

- [ ] All 23 commands convert successfully
- [ ] Sync completes in < 2s on all platforms
- [ ] CI validation passes on macOS, Linux, Windows
- [ ] No unresolved includes in generated files
- [ ] Pre-commit hook auto-stages generated files

### User Acceptance

- [ ] Commands appear in VS Code Copilot autocomplete
- [ ] Commands execute without errors
- [ ] Handoff buttons appear and function
- [ ] Works in both VS Code and VS Code Insiders
- [ ] Documentation is clear and complete

---

## 11. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Include resolution bugs | Medium | High | Extensive testing with edge cases |
| Handoff workflow breaks UX | Low | High | Manual testing in VS Code |
| CI drift detection false positives | Medium | Medium | Idempotent generation |
| Users manually edit .github/agents/ | High | Medium | Clear documentation + CI warnings |
| VS Code Copilot API changes | Low | High | Monitor release notes, test on Insiders |

---

## 12. Next Steps

1. **Implement task-329**: Create directory structure
2. **Implement task-332**: Build sync script (core automation)
3. **Test in VS Code**: Verify commands appear and execute
4. **Add CI validation**: Prevent drift in production

---

*Generated by /jpspec:plan on 2025-12-08*
