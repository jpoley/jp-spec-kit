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
./scripts/bash/check-mcp-servers.sh

# Verbose output with custom timeout
./scripts/bash/check-mcp-servers.sh --verbose --timeout 15

# JSON output for automation
./scripts/bash/check-mcp-servers.sh --json
```

**Example output:**
```
[✓] github - Connected successfully
[✓] serena - Connected successfully
[✗] playwright-test - Failed: binary 'npx' not found
[✓] trivy - Connected successfully
[✓] semgrep - Connected successfully
[✓] shadcn-ui - Connected successfully
[✓] chrome-devtools - Connected successfully
[✓] backlog - Connected successfully

Summary: 7/8 servers healthy
```

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
