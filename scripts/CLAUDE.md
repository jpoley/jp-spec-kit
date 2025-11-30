# Scripts Directory

## Available Scripts

### bash/
| Script | Purpose |
|--------|---------|
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
./scripts/bash/flush-backlog.sh --dry-run  # Preview
./scripts/bash/flush-backlog.sh            # Execute
./scripts/bash/run-local-ci.sh             # Local CI
```

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
