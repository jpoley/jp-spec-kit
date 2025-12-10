# ADR-005: MCP Configuration Path Portability

## Status
Accepted

## Context
The `.mcp.json` configuration file contained hardcoded absolute paths (e.g., `/Users/jasonpoley/ps/jp-spec-kit`) that prevented the configuration from working on other machines or when the repository is cloned to a different location.

## Decision
Replace hardcoded absolute paths with the `${PWD}` environment variable, which resolves to the current working directory at runtime.

### Changes Made
- Serena MCP server `--project` argument: `/Users/jasonpoley/ps/jp-spec-kit` → `${PWD}`

## Alternatives Considered

1. **Custom environment variables** (e.g., `$JPSPEC_ROOT`)
   - Pros: Explicit, user-controlled
   - Cons: Requires manual setup, another thing to configure

2. **Relative paths** (e.g., `.` or `./`)
   - Pros: Simple, no env vars needed
   - Cons: Some MCP servers may not handle relative paths correctly

3. **Keep hardcoded paths**
   - Pros: No changes needed
   - Cons: Breaks portability entirely

## Consequences

### Positive
- Configuration works on any machine without modification
- No additional environment variable setup required
- `${PWD}` is universally available in shell environments

### Negative
- Requires Claude Code to be started from the project root directory
- Windows users need WSL2, Git Bash, or similar POSIX-compatible shell

## Notes
- Test by cloning repo to new location and verifying MCP servers start correctly
- `${PWD}` expansion happens at MCP server spawn time, not config parse time
