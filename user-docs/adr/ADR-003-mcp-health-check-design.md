# ADR-003: MCP Server Health Check Design

## Status

Accepted

## Context

Flowspec integrates with 8 Model Context Protocol (MCP) servers that provide critical capabilities including GitHub API access, code understanding, security scanning, and browser automation. When MCP servers fail to start or become unresponsive, development workflows are blocked with unclear error messages.

**Problems with current state:**
- No systematic way to verify MCP server availability
- Difficult to diagnose which server is failing when Claude Code reports connection issues
- Manual testing of each server is time-consuming (8 servers × multiple commands)
- No visibility into server health across the fleet
- Developers waste time debugging connectivity issues that could be quickly identified

**Key requirements:**
- Test connectivity for all configured MCP servers from .mcp.json
- Report clear success/failure status for each server
- Handle edge cases: missing binaries, timeout scenarios, invalid config
- Provide actionable troubleshooting guidance
- Support both human-readable and machine-readable (JSON) output
- Complete health checks within reasonable time (< 2 minutes for 8 servers)

**Operational context:**
This is a diagnostic tool for developers and SREs, not a production monitoring solution. It's designed for:
- Pre-flight checks before starting Claude Code sessions
- Troubleshooting connection failures
- CI/CD pipeline validation
- Documentation of MCP server configuration

## Decision

We will implement a Bash-based health check script (`check-mcp-servers.sh`) that:

1. **Configuration Discovery**: Parse .mcp.json to extract server definitions
2. **Process Spawning Strategy**: Spawn each MCP server as a subprocess with timeout
3. **Health Check Logic**: Server is "healthy" if it starts and runs for 2+ seconds without crashing
4. **Failure Categorization**: Classify failures as binary_not_found, startup_failed, or timeout
5. **Parallel Safety**: Test servers sequentially to avoid port conflicts and resource contention
6. **Output Formats**: Support both human-friendly terminal output and JSON for automation

### Implementation approach

**Health check methodology:**
```bash
# For each server:
1. Verify command binary exists (npx, uvx, backlog, etc.)
2. Spawn server process with timeout (default 10s)
3. Wait 2 seconds for startup
4. Check if process is still running
5. Terminate server cleanly
6. Report status
```

**Why process spawning vs API calls:**
- MCP protocol doesn't define a health check endpoint
- Spawning server validates both binary availability and startup capability
- Simulates real-world Claude Code server initialization
- Can detect crashes, missing dependencies, permission issues

**Timeout strategy:**
- Default: 10 seconds per server (configurable via --timeout)
- 2-second startup grace period (servers should start quickly)
- Cleanup via trap handlers to prevent zombie processes
- Total execution time: ~10-15 seconds for all 8 servers

### Configuration file validation

The script validates .mcp.json structure:
```bash
# Required checks:
- File exists and is readable
- Valid JSON syntax (via jq)
- Contains "mcpServers" key
- At least one server configured (warning if zero)
```

### Error categorization

| Error Type | Cause | User Action |
|------------|-------|-------------|
| binary_not_found | Command not in PATH | Install missing tool (npx, uvx, etc.) |
| startup_failed | Server crashed immediately | Check dependencies, permissions, env vars |
| timeout | Server hung or slow to start | Increase timeout, check system resources |

### Exit codes

Following Unix conventions:
- **0**: All servers healthy
- **1**: Some servers failed (partial failure)
- **2**: Configuration error (missing/invalid .mcp.json)
- **3**: Prerequisites missing (jq not installed)

## Consequences

### Positive

- **Fast Diagnosis**: Identify failing servers in 10-15 seconds vs manual testing
- **Actionable Output**: Clear error messages guide developers to resolution
- **Automation-Friendly**: JSON output enables CI/CD integration
- **Portable**: Pure Bash with minimal dependencies (jq only)
- **Safe Cleanup**: Trap handlers prevent zombie processes
- **Extensible**: Easy to add new health check tests or metrics

### Negative

- **Limited Depth**: Doesn't test actual MCP protocol communication (just process startup)
- **Sequential Testing**: Could be slower than parallel execution (but safer)
- **Subprocess Overhead**: Spawning 8 servers has resource cost (CPU, memory spikes)
- **Binary Dependency**: Requires jq installed (not always present in minimal environments)
- **Platform Variations**: Process spawning behavior differs slightly between Linux/macOS

### Neutral

- Script is diagnostic-only, not a monitoring solution (one-time checks, not continuous)
- Health check definition may evolve as MCP protocol matures
- Timeout values are heuristic-based (may need tuning for slow systems)

## Alternatives Considered

### Alternative 1: Python-based health checker with MCP protocol client

- **Pros:** Could test actual MCP protocol handshake; richer error reporting; cross-platform
- **Cons:** Requires Python + MCP SDK dependencies; slower startup; harder to maintain
- **Why rejected:** Adds dependency complexity, slower execution, overkill for basic health checks

### Alternative 2: Simple binary existence check only

- **Pros:** Very fast (<1 second total); no process spawning; zero risk
- **Cons:** Doesn't detect startup failures, missing dependencies, configuration issues
- **Why rejected:** Too shallow - misses majority of real-world failures (server installed but won't start)

### Alternative 3: Parallel server testing with timeout

- **Pros:** Faster total execution (all servers tested simultaneously)
- **Cons:** Risk of port conflicts, resource exhaustion, harder cleanup, timing races
- **Why rejected:** Complexity and risk outweigh speed benefit for diagnostic tool (10s → 5s not critical)

### Alternative 4: Docker-based isolated testing

- **Pros:** Complete isolation, reproducible environments, no local system pollution
- **Cons:** Requires Docker, much slower, complex setup, doesn't match actual usage
- **Why rejected:** Docker requirement too heavy for simple diagnostic tool; doesn't reflect real developer environment

## References

- MCP Configuration: `.mcp.json` in project root
- MCP Protocol Specification: https://modelcontextprotocol.io/docs
- Related Task: task-194 - Create MCP Health Check Script
- Related Documentation: docs/prd/claude-capabilities-review.md Section 2.4

---

*This ADR follows the [Michael Nygard format](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).*
