# Command Objective: `flowspec vscode`

## Summary
VS Code integration for role-based agent pinning.

## Objective
Generate VS Code settings that configure GitHub Copilot agent suggestions based on user role.

## Subcommands

### `flowspec vscode generate`
Generate VS Code settings for role-based agent pinning.

**Features:**
- Role-based agent prioritization
- Merges with existing settings
- Custom output path support

**Supported Roles:**
- `dev` - Developer (frontend, backend, AI/ML, platform, quality, release)
- Other roles TBD

**Options:**
```bash
flowspec vscode generate                    # Use primary role from config
flowspec vscode generate --role dev         # Generate for dev role
flowspec vscode generate --force            # Overwrite without merging
flowspec vscode generate -o custom.json     # Custom output path
flowspec vscode generate --no-merge         # Don't merge with existing
```

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| `flowspec vscode generate` | Creates settings | Creates with pinned agents | PASS |
| Default role | Uses dev | Uses dev | PASS |
| Pinned agents | Shows agent list | Shows 6 agents | PASS |

## Acceptance Criteria
- [x] Generates VS Code settings
- [x] Supports role selection
- [x] Merges with existing settings
- [x] Lists pinned agents
- [x] Custom output path support
