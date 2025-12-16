# Command Objective: `flowspec dev-setup`

## Summary
Set up the flowspec source repository for development by creating symlinks to template commands.

## Objective
Enable flowspec developers to use the repository's own /spec:* and /flow:* commands during development without installing the package.

## IMPORTANT: Scope Limitation
**This command is ONLY for developing flowspec itself.** It is NOT for end users setting up their projects. End users should use `flowspec init` instead.

## Features

### Core Features
1. **Source repo detection** - Only runs if `.flowspec-source` marker exists
2. **Claude Code symlinks** - Creates symlinks in .claude/commands/spec/ and .claude/commands/flow/
3. **VS Code Copilot prompts** - Creates symlinks in .github/prompts/
4. **VS Code settings** - Enables chat.promptFiles in .vscode/settings.json

### Command Options
```bash
flowspec dev-setup          # Set up for development
flowspec dev-setup --force  # Recreate symlinks even if they exist
```

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| `flowspec dev-setup --force` | Creates symlinks | Creates all symlinks | PASS |
| Source repo check | Requires .flowspec-source | Checks correctly | PASS |
| Claude commands | 10 spec + 20 flow | 10 spec + 20 flow created | PASS |
| Copilot prompts | 30 prompts | 30 prompts created | PASS |
| VS Code settings | Enables chat.promptFiles | Working | PASS |

## Acceptance Criteria
- [x] Detects flowspec source repository
- [x] Blocks execution in non-source repos
- [x] Creates Claude Code spec command symlinks
- [x] Creates Claude Code flow command symlinks
- [x] Creates VS Code Copilot prompt symlinks
- [x] Creates/updates .vscode/settings.json
- [x] Supports --force for recreation
- [x] Reports broken symlinks
