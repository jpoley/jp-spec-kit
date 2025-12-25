# Flowspec Logging System

The Flowspec logging system provides comprehensive visibility into agent execution, user interactions, and workflow operations. It implements **Level 2: TTY + Hooks** logging as described in the [Logger Plan](/build-docs/logger-plan.md).

## Quick Start

Logging is **enabled by default** in the devcontainer. All logs are written to `.logs/`:

```bash
# Use claude normally - logging happens automatically
claude

# Logs appear in:
# .logs/claude-code.TIMESTAMP.stdin.log   # User input
# .logs/claude-code.TIMESTAMP.stdout.log  # Claude output
# .logs/hooks.log                          # Hook execution log
```

## What is Captured

### TTY Layer (Level 1)
- All user input to `claude-code`
- All text responses from Claude
- Main session terminal I/O

### Hook Layer (Level 2)
- Hook execution timestamps
- Hook names and events
- Hook success/failure status
- Hook output and error messages

## Configuration

### Environment Variables

```bash
export FLOWSPEC_CAPTURE_TTY=true       # Enable TTY capture (default: true)
export FLOWSPEC_CAPTURE_HOOKS=true     # Enable hook logging (default: true)
export LOG_DIR=".logs"                 # Log directory (default: .logs)
```

These are set automatically in `.devcontainer/devcontainer.json` but can be overridden.

### Disable Logging

To disable all logging for a single session:

```bash
FLOWSPEC_CAPTURE_TTY=false FLOWSPEC_CAPTURE_HOOKS=false claude
```

To disable logging permanently, edit `.devcontainer/devcontainer.json` and set the environment variables to `false`.

## Log Files

### Directory Structure

```
.logs/
├── claude-code.20251225T120000Z.stdin.log   # Raw user keystrokes
├── claude-code.20251225T120000Z.stdout.log  # Claude's responses
├── claude-code.20251225T143000Z.stdin.log   # Next session
├── claude-code.20251225T143000Z.stdout.log
└── hooks.log                                 # All hook executions
```

### Log Format

**TTY Logs** (stdin/stdout): Raw terminal I/O streams

**Hook Logs**:
```
[2025-12-25T12:00:00] START: pre-tool-use-git-safety <args>
[2025-12-25T12:00:00] pre-tool-use-git-safety: Checking git safety for tool: Bash
[2025-12-25T12:00:00] pre-tool-use-git-safety: Dangerous git command detected: git push --force
[2025-12-25T12:00:01] END: pre-tool-use-git-safety (exit 0)
```

## Usage Examples

### Debug Workflow Failure

```bash
# Run failing workflow
claude
/flow:implement

# Review hook logs
tail -f .logs/hooks.log

# Look for errors
grep -i "error\|fail" .logs/hooks.log
```

### Review Full Conversation

```bash
# View Claude's output from latest session
ls -t .logs/claude-code.*.stdout.log | head -1 | xargs cat
```

### Search Across All Sessions

```bash
# Find all mentions of a specific error
grep -r "TypeError" .logs/
```

## Log Cleanup

Logs are **excluded from git** via `.gitignore`.

### Manual Cleanup

```bash
# Remove logs older than 7 days
find .logs -name "*.log" -mtime +7 -delete

# Remove all logs
rm -rf .logs/
```

### Automated Cleanup

The devcontainer automatically cleans up logs older than 7 days on startup (configured in `.devcontainer/post-create.sh`).

## Architecture

### How TTY Capture Works

The `wrap.mjs` script uses `node-pty` to create a pseudo-terminal that:
1. Spawns `claude-code` in a PTY
2. Forwards all user input to claude-code's stdin
3. Captures all output from claude-code's stdout
4. Logs both streams to separate files

### How Hook Logging Works

**Bash Hooks**: The `_wrapper.sh` script wraps all hook executions when `FLOWSPEC_CAPTURE_HOOKS=true`.

**Python Hooks**: Import `logging_helper.setup_hook_logging()` at the start of `main()`:

```python
from logging_helper import setup_hook_logging

def main():
    logger = setup_hook_logging("my-hook-name")

    if logger:
        logger.info("Starting hook execution")
        logger.warning("Dangerous operation detected")

    # Rest of hook logic
```

## Security Considerations

### Log Content

**Logs may contain sensitive data:**
- API keys (if accidentally logged)
- User credentials
- Personal information
- Proprietary code

**Mitigations:**
1. `.logs/` is in `.gitignore` (prevents commit)
2. Log files have restrictive permissions in devcontainer
3. Review logs before sharing externally

### Scrubbing Sensitive Data

```bash
# Example: Remove GitHub tokens from logs
sed -i 's/ghp_[a-zA-Z0-9]\{36\}/[REDACTED]/g' .logs/*.log
```

## Performance Impact

**Level 2 (TTY + Hooks):**
- CPU: Negligible (<1%)
- Memory: ~15MB total
- Disk I/O: Low (~200KB/session)

## Adding Logging to Custom Hooks

### Python Hooks

```python
#!/usr/bin/env python3
from logging_helper import setup_hook_logging

def main():
    logger = setup_hook_logging(__name__)

    # Your hook logic here
    if logger:
        logger.info("Hook started")
        logger.debug("Detailed debugging info")
        logger.warning("Something unexpected")
        logger.error("An error occurred")

    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### Bash Hooks

Bash hooks automatically use the `_wrapper.sh` when `FLOWSPEC_CAPTURE_HOOKS=true`. No code changes needed.

## Troubleshooting

### Logs Not Being Created

```bash
# Verify environment variables
echo $FLOWSPEC_CAPTURE_TTY
echo $FLOWSPEC_CAPTURE_HOOKS
echo $LOG_DIR

# Check directory permissions
ls -ld .logs/

# Ensure wrap.mjs exists
ls -l wrap.mjs
```

### Hook Logs Empty

```bash
# Verify wrapper exists
ls -l .claude/hooks/_wrapper.sh

# Check wrapper is executable
chmod +x .claude/hooks/_wrapper.sh

# Verify environment variable
echo $FLOWSPEC_CAPTURE_HOOKS
```

## References

- [Full Implementation Plan](/build-docs/logger-plan.md)
- [Claude Code Hooks Documentation](/.claude/hooks/README.md)
- [wrap.mjs](/wrap.mjs) - TTY capture script
- [logging_helper.py](/.claude/hooks/logging_helper.py) - Python hook logging
- [_wrapper.sh](/.claude/hooks/_wrapper.sh) - Bash hook wrapper

---

**Status**: ✅ Level 2 Implementation Complete
