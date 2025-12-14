# Pre-commit Security Hooks Guide

This guide explains how to use Flowspec's pre-commit security hooks to catch vulnerabilities before they're committed.

## Overview

The security pre-commit hook runs a fast security scan on staged files before each commit. It blocks commits with critical vulnerabilities while allowing through lower-severity issues (which should be addressed in CI).

**Key Features:**
- Fast scanning (<10 seconds for typical commits)
- Only scans staged files
- Blocks critical vulnerabilities
- Audit logging for bypasses
- Integrates with pre-commit framework

## Quick Start

### Installation

```bash
# Run the setup script
./scripts/bash/setup-security-hooks.sh

# Or manually install
pip install pre-commit
pre-commit install
```

### Verify Installation

```bash
# Check status
./scripts/bash/setup-security-hooks.sh --check

# Test the hook
pre-commit run flowspec-security-scan --all-files
```

## How It Works

1. When you run `git commit`, the pre-commit framework triggers
2. The security hook scans only staged files matching scannable patterns
3. If critical vulnerabilities are found, the commit is blocked
4. Lower-severity issues are logged but don't block the commit
5. You can bypass the hook with `--no-verify` (logged for audit)

```
┌─────────────────────────────────────────────────────┐
│                    git commit                        │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              pre-commit framework                    │
│  • ruff (format/lint)                               │
│  • flowspec-security-scan ◄── Security Hook        │
│  • trailing-whitespace                              │
└─────────────────────────────────────────────────────┘
                         │
           ┌─────────────┴─────────────┐
           │                           │
           ▼                           ▼
    Critical Found              No Critical Issues
           │                           │
           ▼                           ▼
    ┌─────────────┐            ┌─────────────┐
    │ COMMIT      │            │ COMMIT      │
    │ BLOCKED     │            │ ALLOWED     │
    └─────────────┘            └─────────────┘
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLOWSPEC_SECURITY_FAIL_ON` | `critical` | Severity threshold to block commit |
| `FLOWSPEC_SECURITY_TIMEOUT` | `30` | Scan timeout in seconds |
| `FLOWSPEC_SECURITY_BYPASS` | (unset) | Set to "1" to skip scanning (logged) |

### Severity Levels

- **critical**: Always blocks commit (SQL injection, RCE, etc.)
- **high**: Blocks if `FLOWSPEC_SECURITY_FAIL_ON=high`
- **medium**: Warning only
- **low**: Warning only

### Example: Change Severity Threshold

```bash
# Block on high and critical severity
export FLOWSPEC_SECURITY_FAIL_ON=high

# Now all commits will be checked against high+critical
git commit -m "My changes"
```

## Bypassing the Hook

### For a Single Commit

Use `--no-verify` to skip all pre-commit hooks:

```bash
git commit --no-verify -m "Emergency hotfix"
```

> **Warning:** This bypasses ALL pre-commit hooks, not just security.

### Using Environment Variable

Set `FLOWSPEC_SECURITY_BYPASS=1` to skip security scanning only:

```bash
FLOWSPEC_SECURITY_BYPASS=1 git commit -m "WIP: Will fix later"
```

### Bypass Audit Log

All bypasses are logged to `.flowspec/security-bypass.log`:

```
2025-12-14T19:15:00Z|alice|env_bypass|WIP: experimental feature
2025-12-14T19:20:00Z|bob|no_verify|Emergency production fix
```

Review bypasses:

```bash
# View recent bypasses
cat .flowspec/security-bypass.log

# Count bypasses
wc -l .flowspec/security-bypass.log
```

## Performance

The hook is optimized for fast feedback:

| Scenario | Expected Time |
|----------|---------------|
| 1-5 files | <5 seconds |
| 5-10 files | <10 seconds |
| 10+ files | May exceed timeout |

### Tips for Faster Scans

1. **Stage fewer files**: Commit in smaller batches
2. **Increase timeout**: `export FLOWSPEC_SECURITY_TIMEOUT=60`
3. **Skip large files**: Binary files are automatically skipped

## Supported File Types

The hook scans these file extensions:

| Language | Extensions |
|----------|------------|
| Python | `.py` |
| JavaScript/TypeScript | `.js`, `.ts`, `.tsx`, `.jsx` |
| Go | `.go` |
| Rust | `.rs` |
| Java | `.java` |
| Ruby | `.rb` |
| PHP | `.php` |

## Troubleshooting

### Hook Not Running

```bash
# Verify pre-commit is installed
pre-commit --version

# Reinstall hooks
pre-commit install --force

# Check configuration
./scripts/bash/setup-security-hooks.sh --check
```

### Hook Timing Out

```bash
# Increase timeout
export FLOWSPEC_SECURITY_TIMEOUT=60

# Or bypass for this commit
git commit --no-verify -m "Large commit"
```

### False Positives

If the hook blocks a commit incorrectly:

1. Check the specific finding
2. If it's a false positive, bypass with `--no-verify`
3. Report the false positive to improve the scanner

### specify Command Not Found

```bash
# Install specify-cli
pip install specify-cli

# Or use uv
uv pip install specify-cli
```

## Integration with CI

The pre-commit hook provides fast local feedback. For thorough scanning, also run security scans in CI:

```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install specify-cli
      - run: specify security scan --full
```

## Uninstalling

```bash
# Remove security hooks
./scripts/bash/setup-security-hooks.sh --uninstall

# Or remove all pre-commit hooks
pre-commit uninstall
```

## Related Commands

- `/flow:security scan` - Full security scan
- `/flow:security triage` - AI-assisted triage
- `/sec:report` - Generate security report

## See Also

- [Security Workflow Guide](./security-workflow.md)
- [Pre-commit Framework](https://pre-commit.com)
- [Bandit Documentation](https://bandit.readthedocs.io/)
