# Command Objective: `flowspec upgrade-tools`

## Summary
Install or upgrade CLI tools (flowspec, backlog-md, beads).

## Objective
Manage the installation and upgrades of all CLI tools in the flowspec ecosystem through a single command.

## Features

### Core Features
1. **Multi-tool management** - Installs/upgrades:
   - flowspec (via uv tool)
   - backlog-md (via npm/pnpm)
   - beads (via npm/pnpm)

2. **Selective upgrade** - Can upgrade specific components
3. **Dry-run mode** - Preview what would happen
4. **Version pinning** - Install specific versions
5. **Version listing** - Show available versions

### Command Options
```bash
flowspec upgrade-tools                      # Install/upgrade all tools
flowspec upgrade-tools -c flowspec          # Upgrade only flowspec
flowspec upgrade-tools -c backlog           # Install/upgrade backlog-md
flowspec upgrade-tools -c beads             # Install/upgrade beads
flowspec upgrade-tools --dry-run            # Preview changes
flowspec upgrade-tools --version 0.2.325    # Specific flowspec version
flowspec upgrade-tools --list-versions      # Show available versions
```

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| Help output | Shows all options | Shows all options | PASS |
| Dry-run mode | Preview without changes | Not fully tested | N/A |
| Version listing | Lists available versions | Not fully tested | N/A |

## Acceptance Criteria
- [x] Supports upgrading flowspec via uv
- [x] Supports upgrading backlog-md via npm/pnpm
- [x] Supports upgrading beads via npm/pnpm
- [x] Supports component selection via -c flag
- [x] Supports dry-run mode
- [x] Supports version pinning
- [x] Supports version listing
