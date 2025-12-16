# ADR: Upgrade Commands Architecture

## Status
Accepted - Implemented 2025-12-07

## Context

The `specify` CLI has a confusing upgrade story:
- `specify --version` shows available upgrades for flowspec, spec-kit, and backlog.md with `↑` indicators
- The hint says "Run 'specify upgrade' to update components"
- **BUT** `specify upgrade` only upgrades repo templates, not the actual CLI tools

The tools are installed per-user:
| Tool | Installation Method | Location |
|------|---------------------|----------|
| flowspec | `uv tool install flowspec-cli --from git+...` | `~/.local/bin/specify` |
| spec-kit | `uv tool install spec-kit` | uv managed |
| backlog.md | `pnpm add -g backlog-md` | npm global |

Users need BOTH types of upgrades:
1. **Tool upgrades**: Update the CLI binaries themselves
2. **Repo upgrades**: Update templates/commands in a project repo

## Decision

Implement two distinct upgrade commands:

### `specify upgrade-tools`
Upgrades globally installed CLI tools:
```bash
specify upgrade-tools                    # Upgrade all tools
specify upgrade-tools -c flowspec     # Upgrade specific tool
specify upgrade-tools --dry-run          # Preview changes
```

Implementation:
- flowspec: `uv tool upgrade flowspec-cli`
- backlog.md: `pnpm add -g backlog-md@latest` (or npm)
- Verify version after upgrade

### `specify upgrade-repo`
Upgrades repository templates (current behavior):
```bash
specify upgrade-repo                     # Upgrade repo templates
specify upgrade-repo --templates-only    # Only templates
specify upgrade-repo --dry-run           # Preview changes
```

### `specify upgrade` (updated)
Becomes an interactive dispatcher:
```bash
specify upgrade              # Interactive: asks tools or repo
specify upgrade --tools      # Same as upgrade-tools
specify upgrade --repo       # Same as upgrade-repo
specify upgrade --all        # Upgrade both
```

## Tasks Created

| Task | Description | Priority |
|------|-------------|----------|
| task-296 | Implement upgrade-tools command | High |
| task-297 | Rename upgrade to upgrade-repo | High |
| task-298 | Update upgrade as interactive dispatcher | Medium |
| task-299 | Fix version hint to point to correct command | High |

## Implementation Order

1. **task-299** - Fix version hint (quick fix, immediate value)
2. **task-297** - Rename upgrade to upgrade-repo (foundation)
3. **task-296** - Implement upgrade-tools (main feature)
4. **task-298** - Update upgrade dispatcher (polish)

## Consequences

### Positive
- Clear separation between tool and repo upgrades
- Version hint will be accurate
- Users can upgrade tools without being in a project directory

### Negative
- Breaking change for users who expect `specify upgrade` to upgrade tools
- Need documentation updates

## Next Command

```
/flow:implement
```

Focus on tasks: task-299, task-297, task-296, task-298 (in order)
