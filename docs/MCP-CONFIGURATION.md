# MCP Server Configuration Guide

## Overview

This project uses Model Context Protocol (MCP) servers to extend Claude Code capabilities with specialized tools for development, security, and collaboration.

## MCP Server Configuration

MCP servers are configured in `.mcp.json` at the project root. This file is checked into version control so all team members have access to the same tools.

## Environment Variables Required

Create a `.env` file in the project root with the following variables:

```bash
# Context7 - Required for up-to-date library documentation
CONTEXT7_API_KEY=your_context7_api_key_here

# Figma - Required for design file access (frontend agents)
FIGMA_API_KEY=your_figma_api_key_here

# PROJECT_ROOT is automatically set to current working directory
```

### Getting API Keys

**Context7 API Key:**
1. Visit: https://github.com/upstash/context7
2. Follow the setup instructions to get your API key
3. Add to `.env` file

**Figma API Key:**
1. Visit: https://www.figma.com/developers/api#access-tokens
2. Generate a personal access token
3. Add to `.env` file

## Installed MCP Servers

### Universal MCPs (All Agents)

**1. GitHub (`mcp__github__*`)**
- **Purpose**: Full GitHub API access for repos, issues, PRs, code search, workflows
- **Package**: `@modelcontextprotocol/server-github`
- **Requirements**: None (uses your GitHub authentication)

**2. Serena (`mcp__serena__*`)**
- **Purpose**: LSP-grade code understanding and safe semantic edits
- **Package**: `git+https://github.com/oraios/serena`
- **Requirements**: Python with `uv` installed

**3. Context7 (`mcp__context7__*`)**
- **Purpose**: Up-to-date, version-specific library documentation
- **Package**: `@upstash/context7-mcp`
- **Requirements**: `CONTEXT7_API_KEY` environment variable

### Frontend-Specific MCPs

**4. Playwright (`mcp__playwright-test__*`)**
- **Purpose**: Browser automation for testing and E2E workflows
- **Package**: `@playwright/mcp`
- **Agents**: frontend-engineer, frontend-code-reviewer, js-ts-expert-developer, js-ts-expert-developer-enhanced, playwright test agents

**5. Figma (`mcp__figma__*`)**
- **Purpose**: Figma API integration for design files and components
- **Package**: `figma-developer-mcp`
- **Requirements**: `FIGMA_API_KEY` environment variable
- **Agents**: frontend-engineer, frontend-code-reviewer, js-ts-expert-developer, js-ts-expert-developer-enhanced

**6. shadcn-ui (`mcp__shadcn-ui__*`)**
- **Purpose**: shadcn/ui component library access and installation
- **Package**: `@heilgar/shadcn-ui-mcp-server`
- **Agents**: frontend-engineer, frontend-code-reviewer, js-ts-expert-developer, js-ts-expert-developer-enhanced

**7. Chrome DevTools (`mcp__chrome-devtools__*`)**
- **Purpose**: Browser inspection, performance analysis, console logs, network monitoring, and UI testing via Chrome DevTools Protocol
- **Package**: `chrome-devtools-mcp`
- **Requirements**: Chrome browser installed, Node.js ≥20.19
- **Agents**: frontend-engineer, frontend-code-reviewer, quality-guardian, sre-agent
- **Key Capabilities**:
  - Navigate pages and interact with DOM (click, fill, hover)
  - Capture performance traces and analyze metrics
  - Monitor console logs and network requests
  - Emulate network conditions and CPU throttling
  - Take screenshots and test responsive layouts
  - Debug web applications in real browser context

### Security-Specific MCPs

**8. Trivy (`mcp__trivy__*`)**
- **Purpose**: Container/IaC security scans and SBOM generation
- **Package**: `@aquasecurity/trivy-mcp`
- **Agents**: secure-by-design-engineer, all code reviewers, release-manager

**9. Semgrep (`mcp__semgrep__*`)**
- **Purpose**: SAST (Static Application Security Testing) code scanning
- **Package**: `@returntocorp/semgrep-mcp`
- **Agents**: secure-by-design-engineer, all code reviewers

## Agent MCP Assignments

### All Agents (31 total)
- `mcp__github__*` - GitHub API
- `mcp__context7__*` - Documentation
- `mcp__serena__*` - Code understanding

### Frontend Agents (4)
- frontend-engineer
- frontend-code-reviewer
- js-ts-expert-developer
- js-ts-expert-developer-enhanced

**Additional Tools:**
- `mcp__figma__*`
- `mcp__shadcn-ui__*`
- `mcp__playwright-test__*`
- `mcp__chrome-devtools__*` (frontend-engineer, frontend-code-reviewer only)

### Security Agents (5)
- secure-by-design-engineer
- python-code-reviewer
- python-code-reviewer-enhanced
- backend-code-reviewer
- frontend-code-reviewer

**Additional Tools:**
- `mcp__trivy__*`
- `mcp__semgrep__*`

### Release Manager (1)
- release-manager

**Additional Tools:**
- `mcp__trivy__*` (for SBOM generation)

### Playwright Test Agents (3)
- playwright-test-healer
- playwright-test-generator
- playwright-test-planner

**Additional Tools:**
- `mcp__playwright-test__*` (with specific test tools)

### Quality Assurance Agent (1)
- quality-guardian

**Additional Tools:**
- `mcp__chrome-devtools__*` (for browser testing and performance analysis)

### SRE/Operations Agent (1)
- sre-agent

**Additional Tools:**
- `mcp__chrome-devtools__*` (for performance monitoring and web application observability)

## Installation and Usage

### Prerequisites

```bash
# Install Node.js (for npx)
node --version  # Should be v18+

# Install Python with uv (for Serena)
pip install uv
# or
brew install uv  # on macOS
```

### First Use

MCP servers are installed automatically on first use via `npx` (Node) or `uvx` (Python). No manual installation required.

When you first invoke an MCP tool, Claude Code will:
1. Download the MCP server package
2. Start the server process
3. Connect to it and execute the tool

### Testing MCP Configuration

```bash
# Test MCP Inspector (optional)
npx @modelcontextprotocol/inspector -- npx -y @modelcontextprotocol/server-github

# Verify .mcp.json is valid JSON
cat .mcp.json | jq .
```

## Known Limitations

### Missing MCP Servers

The following capabilities do not have dedicated MCP servers and should be handled via CLI tools or CI/CD:

**1. DAST (Dynamic Application Security Testing)**
- **Alternative**: Use OWASP ZAP directly
- **CI/CD**: Configure in GitHub Actions workflow
- **Agents Affected**: secure-by-design-engineer

**2. Binary Signing**
- **Alternative**: Use cosign/sigstore CLI tools
- **CI/CD**: Already configured in `.github/workflows/ci.yml`
- **Agents Affected**: release-manager
- **Note**: See `TODO/task-004-completion.md` for cosign setup

**3. IAST (Interactive Application Security Testing)**
- **Alternative**: Use dedicated IAST tools
- **Agents Affected**: secure-by-design-engineer

## Troubleshooting

### Context7 API Key Missing
```
Error: CONTEXT7_API_KEY environment variable not set
Solution: Add CONTEXT7_API_KEY to .env file
```

### Figma API Key Missing
```
Error: FIGMA_API_KEY environment variable not set
Solution: Add FIGMA_API_KEY to .env file (required for frontend agents)
```

### Serena Installation Issues
```
Error: uv not found
Solution: Install uv via pip or brew
```

### npx Permission Issues
```
Error: EACCES permission denied
Solution: Fix npm permissions or use nvm
```

## References

- **Official MCP Documentation**: https://modelcontextprotocol.io/
- **Claude Code MCP Guide**: https://docs.claude.com/en/docs/claude-code/mcp
- **MCP Server Registry**: https://mcpservers.org/
- **Project MCP Lists**:
  - `TODO/mcp-1.md` - Top 100 cross-language MCP servers
  - `TODO/mcp-2.md` - Top 100 unified MCP servers

## Updates and Maintenance

To add new MCP servers:

1. Update `.mcp.json` with new server configuration
2. Update agent tools in `.agents/<agent>.md` with `mcp__<server-name>__*`
3. Update this documentation
4. Test the new MCP with relevant agents
5. Commit changes to version control

## Support

For issues with MCP configuration:
1. Check `.mcp.json` syntax (must be valid JSON)
2. Verify environment variables are set correctly
3. Check Node.js and Python versions meet requirements
4. Consult MCP server documentation for server-specific issues
