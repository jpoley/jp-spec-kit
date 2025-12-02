# Scripts Directory

## Available Scripts

### bash/
| Script | Purpose |
|--------|---------|
| `check-mcp-servers.sh` | Test MCP server connectivity and health |
| `run-local-ci.sh` | Run full CI simulation locally |
| `flush-backlog.sh` | Archive Done tasks with summary report |
| `install-act.sh` | Install act for local GitHub Actions testing |

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
