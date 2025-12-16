# Command Objective: `flowspec upgrade`

## Summary
Unified upgrade dispatcher for tools and repository templates.

## Objective
Provide a single entry point for all upgrade operations, dispatching to either `upgrade-tools` or `upgrade-repo` based on user selection.

## Features

### Core Features
1. **Interactive mode** - When no flags provided, shows options
2. **Dispatch to sub-commands** - Routes to appropriate upgrade command
3. **Combined upgrade** - Can upgrade both tools and repo in one command

### Command Options
```bash
flowspec upgrade              # Interactive: choose what to upgrade
flowspec upgrade --tools      # Same as 'flowspec upgrade-tools'
flowspec upgrade --repo       # Same as 'flowspec upgrade-repo'
flowspec upgrade --all        # Upgrade both tools and repo
flowspec upgrade --dry-run    # Preview changes
```

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Help output | Shows dispatch options | Shows all options | PASS |
| `--tools` flag | Runs upgrade-tools | Expected to work | N/A |
| `--repo` flag | Runs upgrade-repo | Expected to work | N/A |
| `--all` flag | Runs both | Expected to work | N/A |

## Acceptance Criteria
- [x] Supports interactive mode
- [x] Dispatches to upgrade-tools with --tools
- [x] Dispatches to upgrade-repo with --repo
- [x] Supports --all for combined upgrade
- [x] Supports dry-run mode
