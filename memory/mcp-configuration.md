# MCP Configuration

JP Spec Kit uses Model Context Protocol (MCP) servers for enhanced capabilities.

## MCP Server List

| Server | Description |
|--------|-------------|
| `github` | GitHub API: repos, issues, PRs, code search, workflows |
| `serena` | LSP-grade code understanding & safe semantic edits |
| `playwright-test` | Browser automation for testing and E2E workflows |
| `trivy` | Container/IaC security scans and SBOM generation |
| `semgrep` | SAST code scanning for security vulnerabilities |
| `shadcn-ui` | shadcn/ui component library access and installation |
| `chrome-devtools` | Chrome DevTools Protocol for browser inspection |
| `backlog` | Backlog.md task management with kanban integration |

## Health Check

Test connectivity for all configured MCP servers:

```bash
# Check all servers with default settings
./scripts/check-mcp-servers.sh

# Verbose output showing command paths and versions
./scripts/check-mcp-servers.sh -v

# Quiet mode - only errors and summary
./scripts/check-mcp-servers.sh -q

# Custom config file
./scripts/check-mcp-servers.sh -c /path/to/.mcp.json

# Show help
./scripts/check-mcp-servers.sh --help
```

**Example output:**
```
[INFO] Checking MCP server configuration: .mcp.json

[PASS] github (npx)
[PASS] serena (uvx)
[FAIL] playwright-test: Command 'npx' not found
[PASS] backlog (backlog)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MCP Server Health Check Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total:    4
Passed:   3
Failed:   1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Some MCP servers are unavailable.
Run with -v flag for installation hints.
```

**Exit codes:**
- `0` - All servers healthy
- `1` - One or more servers failed
- `2` - Configuration error (file not found, invalid JSON)

## Troubleshooting MCP Issues

If health checks fail:

1. **Binary not found**: Install missing prerequisites
   - `npx` - Install Node.js: `brew install node` (macOS) or via nvm
   - `uvx` - Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - `backlog` - Install backlog CLI: `cargo install backlog-md` or use binary

2. **Startup failed**: Check server dependencies
   - Review .mcp.json configuration for typos
   - Verify environment variables are set if required
   - Check server-specific logs in ~/.mcp/logs/

3. **Timeout**: Increase timeout for slow systems
   - Use `--timeout 20` for systems with limited resources
   - Check system load: `uptime`, `top`

4. **Connection refused**: Verify network and firewall settings
   - Some servers may require internet connectivity
   - Check firewall isn't blocking local connections

## MCP Configuration File

MCP servers are configured in `.mcp.json` at the project root. See [MCP documentation](https://modelcontextprotocol.io/docs) for details.
