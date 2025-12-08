# VS Code Copilot Agents

This directory contains custom agents for VS Code GitHub Copilot, providing the JP Spec Kit SDD (Spec-Driven Development) workflow.

## Directory Structure

```
.github/agents/
├── README.md                    # This file
├── jpspec-*.agent.md           # Workflow orchestration agents
└── speckit-*.agent.md          # Utility agents
```

## Important: Generated Files

**DO NOT EDIT FILES IN THIS DIRECTORY DIRECTLY**

These `.agent.md` files are **generated** from `.claude/commands/`. The canonical source of truth is:

```
.claude/commands/
├── jpspec/                      # Workflow commands (source)
└── speckit/                     # Utility commands (source)
```

## Sync Process

To regenerate agents after modifying `.claude/commands/`:

```bash
# Manual sync
scripts/bash/sync-copilot-agents.sh

# Validate sync (CI mode)
scripts/bash/sync-copilot-agents.sh --validate

# Preview changes without writing
scripts/bash/sync-copilot-agents.sh --dry-run
```

## Key Differences from Claude Code Commands

| Aspect | Claude Code | VS Code Copilot |
|--------|-------------|-----------------|
| Directory | `.claude/commands/` | `.github/agents/` |
| File extension | `.md` | `.agent.md` |
| Frontmatter | `description:` only | `name:`, `description:`, `tools:`, `handoffs:` |
| Include resolution | Runtime `{{INCLUDE:}}` | Pre-resolved (embedded) |
| Workflow transitions | None | `handoffs:` array |

## Agent Handoffs

SDD workflow phases are connected via handoffs:

```
assess -> specify -> research -> plan -> implement -> validate -> operate
                        ^          |
                        └──────────┘ (research optional)
```

Each jpspec agent can hand off to the next workflow phase. Users review the handoff prompt before proceeding.

## Using Agents in VS Code

1. Open VS Code with Copilot enabled
2. Type `@` in chat to see available agents
3. Select an agent (e.g., `@jpspec-specify`)
4. Follow the workflow prompts

## CI/CD Integration

The `.github/workflows/validate-agent-sync.yml` workflow:
- Runs on PRs touching `.claude/commands/` or `.github/agents/`
- Validates no drift between source and generated files
- Ensures all includes are resolved
- Checks YAML frontmatter validity

## Questions?

See [VS Code Copilot Agents Plan](../../docs/platform/vscode-copilot-agents-plan.md) for architecture details.
