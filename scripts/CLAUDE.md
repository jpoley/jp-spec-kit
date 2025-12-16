# Scripts Directory

## Available Scripts

### bash/
| Script | Purpose |
|--------|---------|
| `check-mcp-servers.sh` | Test MCP server connectivity and health |
| `run-local-ci.sh` | Run full CI simulation locally |
| `flush-backlog.sh` | Archive Done tasks with summary report |
| `install-act.sh` | Install act for local GitHub Actions testing |
| `pre-commit-dev-setup.sh` | Validate dev-setup symlink structure |
| `pre-commit-agent-sync.sh` | Auto-sync Claude commands to Copilot agents |
| `migrate-commands-to-subdirs.sh` | Migrate flat command structure to subdirectories |
| `prune-releases.sh` | Delete old GitHub releases below a version threshold |

### powershell/
PowerShell equivalents of bash scripts for Windows.

### hooks/
Git hooks and Claude Code hooks.

## Usage

Always run scripts from the project root:
```bash
./scripts/bash/check-mcp-servers.sh        # Check MCP health
./scripts/bash/flush-backlog.sh --dry-run  # Preview
./scripts/bash/flush-backlog.sh            # Execute
./scripts/bash/run-local-ci.sh             # Local CI
./scripts/bash/pre-commit-dev-setup.sh     # Validate dev-setup structure
```

## check-mcp-servers.sh

Tests connectivity and operational status for all configured MCP servers.

```bash
# Check all servers with default settings
./scripts/bash/check-mcp-servers.sh

# Verbose output with custom timeout
./scripts/bash/check-mcp-servers.sh --verbose --timeout 15

# JSON output for automation/CI
./scripts/bash/check-mcp-servers.sh --json

# Use custom config file
./scripts/bash/check-mcp-servers.sh --config /path/to/.mcp.json

# Show help
./scripts/bash/check-mcp-servers.sh --help
```

**Exit codes:**
- 0: All servers healthy
- 1: Some servers failed health checks
- 2: Configuration error (missing/invalid .mcp.json)
- 3: Prerequisites missing (jq not installed)

**Example output:**
```
[✓] github - Connected successfully
[✓] serena - Connected successfully
[✗] playwright-test - Failed: binary 'npx' not found
[✓] backlog - Connected successfully

Summary: 3/4 servers healthy

Troubleshooting:
  1. Verify required binaries are installed (npx, uvx, backlog)
  2. Check network connectivity and firewall settings
  3. Review server-specific logs for detailed errors
  4. Ensure required environment variables are set
  5. Try manually starting failed servers for detailed output
```

**Testing:**
```bash
# Run test suite to verify health check functionality
./scripts/bash/test-mcp-health-check.sh
```

**Design rationale:** See `docs/adr/ADR-003-mcp-health-check-design.md`

## flush-backlog.sh

Archives completed tasks and generates summary reports.

```bash
# Preview what would be archived
./scripts/bash/flush-backlog.sh --dry-run

# Archive all Done tasks
./scripts/bash/flush-backlog.sh

# Archive without summary
./scripts/bash/flush-backlog.sh --no-summary

# Archive and auto-commit
./scripts/bash/flush-backlog.sh --auto-commit
```

**Exit codes:**
- 0: Success
- 1: Validation error
- 2: No Done tasks to archive
- 3: Partial failure

## prune-releases.sh

Delete old GitHub releases and tags below a specified version threshold.

```bash
# Dry-run: show what would be deleted
./scripts/bash/prune-releases.sh 0.0.100

# Actually delete releases below v0.0.100
./scripts/bash/prune-releases.sh 0.0.100 --execute

# Delete all 0.0.x releases
./scripts/bash/prune-releases.sh 0.1.0 --execute
```

**How it works:**
1. Fetches all releases via `gh release list --json`
2. Parses version numbers and compares to threshold
3. In dry-run mode, shows what would be deleted
4. With `--execute`, requires typing "DELETE" to confirm
5. Deletes both GitHub releases and git tags

**Exit codes:**
- 0: Success (or no releases to delete)
- 1: Invalid arguments or version format

**Requirements:**
- GitHub CLI (`gh`) authenticated
- Git remote access for tag deletion

## pre-commit-dev-setup.sh

Validates .claude/commands/ structure to ensure single-source-of-truth architecture.

```bash
# Run validation manually
./scripts/bash/pre-commit-dev-setup.sh
```

**Validation rules:**
- R1: All .md files in .claude/commands/ must be symlinks (no regular files)
- R2: All symlinks must resolve to existing files (no broken symlinks)
- R3: All symlinks must point to templates/commands/ directory
- R7: Expected subdirectories (flowspec/, speckit/) must exist

**Exit codes:**
- 0: All validations passed
- 1: One or more validation failures

**Integration with git hooks:**

To run this automatically before commits, add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
./scripts/bash/pre-commit-dev-setup.sh || exit 1
```

Or install via symlink:
```bash
ln -s ../../scripts/bash/pre-commit-dev-setup.sh .git/hooks/pre-commit-dev-setup
```

**If using pre-commit framework**, add to `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: dev-setup-validation
        name: Dev Setup Validation
        entry: ./scripts/bash/pre-commit-dev-setup.sh
        language: system
        pass_filenames: false
        always_run: true
```

**Design rationale:** See `docs/architecture/command-single-source-of-truth.md`

## pre-commit-agent-sync.sh

Auto-syncs Claude commands to VS Code Copilot agents when command files change.

```bash
# Automatically run by pre-commit framework
# Or run manually:
./scripts/bash/pre-commit-agent-sync.sh
```

**What it does:**
1. Detects staged `.claude/commands/**/*.md` or `templates/commands/**/*.md` files
2. Runs `sync-copilot-agents.sh --force` to regenerate agents
3. Auto-stages generated `.github/agents/` files
4. Shows summary of synced files

**Exit codes:**
- 0: Success (sync completed or nothing to do)
- 1: Sync failed

**Pre-commit integration** (already configured in `.pre-commit-config.yaml`):
```yaml
- id: sync-copilot-agents
  name: Sync Copilot agents
  entry: scripts/bash/pre-commit-agent-sync.sh
  language: script
  files: ^\.claude/commands/.*\.md$|^templates/commands/.*\.md$
  pass_filenames: false
```

**Bypass:** Use `git commit --no-verify` to skip this hook for emergency commits.

**Example output:**
```
[agent-sync] Detected staged command files, syncing agents...
[agent-sync] Staged command files:
  .claude/commands/flow/implement.md
OK: Created: flow-implement.agent.md
[agent-sync] Auto-staged .github/agents/ files
[agent-sync] Synced 1 agent files:
  .github/agents/flow-implement.agent.md
[agent-sync] Agent sync complete
```

**Design rationale:** See `build-docs/design/git-hook-agent-sync-design.md`

## migrate-commands-to-subdirs.sh

Migrates slash commands from flat structure (e.g., `flowspec.implement.md`) to subdirectory structure (e.g., `flowspec/implement.md`).

```bash
# Preview what would be moved
./scripts/bash/migrate-commands-to-subdirs.sh --dry-run

# Migrate commands in .claude/commands/
./scripts/bash/migrate-commands-to-subdirs.sh --path .claude/commands

# Migrate template commands
./scripts/bash/migrate-commands-to-subdirs.sh --path templates/commands

# Show help
./scripts/bash/migrate-commands-to-subdirs.sh --help
```

**What it does:**
- Moves `flowspec.*.md` files to `flowspec/` subdirectory (renamed to `*.md`)
- Moves `speckit.*.md` files to `speckit/` subdirectory (renamed to `*.md`)
- Creates subdirectories if they don't exist
- Checks for broken symlinks after migration

**Exit codes:**
- 0: Success (files migrated or nothing to migrate)
- 1: Error during migration
- 2: Invalid arguments or target path not found

**Next steps after migration:**
1. Review changes: `git status`
2. If migrating `.claude/commands/`, run: `flowspec dev-setup --force`
3. Commit changes: `git add -A && git commit -m 'Migrate commands to subdirectories'`

## Local CI with act

Run GitHub Actions workflows locally:

```bash
# Direct execution (default, no Docker needed)
./scripts/bash/run-local-ci.sh

# Using act (requires Docker)
./scripts/bash/run-local-ci.sh --act

# Run specific job
./scripts/bash/run-local-ci.sh --act --job test

# Specify workflow file
./scripts/bash/run-local-ci.sh --act --job lint --workflow .github/workflows/ci.yml

# List available jobs
./scripts/bash/run-local-ci.sh --act --list

# Show help
./scripts/bash/run-local-ci.sh --help
```

### Platform Support
- **Primary platform**: Linux (Ubuntu 22.04/24.04) - fully tested and supported
- **Portable design**: Script uses POSIX-compliant bash constructs and should work on macOS
- **Future**: macOS CI matrix testing planned (separate task)

**Script compatibility features**:
- `#!/usr/bin/env bash` - finds bash via PATH (works on all platforms)
- Bash 3.2+ compatible (macOS default bash version)
- POSIX-compliant commands (`command -v`, `grep -q`, `read -r`)
- No GNU-specific extensions
- Cross-platform tools: `act`, `uv`, `docker`

### act Limitations
- **Docker required**: act runs workflows in Docker containers
- **OIDC not supported**: Jobs using OIDC authentication will fail
- **Secrets**: Use `.secrets` file or `-s` flag for secrets
- **Platform compatibility**: Use `--container-architecture linux/amd64` on M1/M2 Macs
- **Some actions unsupported**: Complex marketplace actions may not work

### Troubleshooting
- If act fails, the script automatically uses `--container-architecture linux/amd64`
- Check Docker is running: `docker info`
- For manual act usage: `act -l` (list jobs), `act -j <job-name>` (run job)
- Install act manually: `./scripts/bash/install-act.sh`

**Requirements:** Docker must be running for --act mode.

## Making Scripts Executable

```bash
chmod +x scripts/bash/*.sh
chmod +x scripts/hooks/*
```

## Documentation

- Flush details: `docs/guides/backlog-flush.md`
- act setup: See act documentation at https://github.com/nektos/act
