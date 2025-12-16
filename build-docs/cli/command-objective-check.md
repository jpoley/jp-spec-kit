# Command Objective: `flowspec check`

## Summary
Verify that all required and optional tools are installed for the flowspec ecosystem.

## Objective
Provide a comprehensive health check of the development environment, showing which tools are available and offering guidance for missing components.

## Features

### Core Features
1. **Tool detection** - Checks for presence of various tools:
   - Git (version control)
   - AI assistants (Claude, Copilot, Gemini, Cursor, Codex, etc.)
   - VS Code / VS Code Insiders
   - backlog-md (task management)

2. **Version validation** - Shows installed versions where available
3. **Upgrade recommendations** - Suggests upgrades when versions mismatch

### Command Options
```bash
flowspec check  # No options - simple health check
```

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| `flowspec check` | Shows tool status | Shows all tool statuses | PASS |
| Git detection | Shows version | Working | PASS |
| Claude Code detection | Shows available/not found | Working | PASS |
| backlog-md detection | Shows version | Shows version with recommendation | PASS |

## Acceptance Criteria
- [x] Checks git installation
- [x] Checks all supported AI assistants
- [x] Checks VS Code installations
- [x] Checks backlog-md installation
- [x] Shows version comparison for backlog-md
- [x] Provides actionable recommendations
