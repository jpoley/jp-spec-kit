# MCP Security Examples

This directory contains example clients demonstrating how to use the JP Spec Kit Security Scanner MCP server.

## Prerequisites

Before running these examples:

1. **Install JP Spec Kit:**
   ```bash
   cd /path/to/jp-spec-kit
   uv tool install . --force
   ```

2. **Install MCP Python SDK:**
   ```bash
   uv add mcp
   # or
   pip install mcp
   ```

3. **Install Security Scanners:**
   ```bash
   pip install semgrep
   ```

4. **Run a Security Scan:**
   ```bash
   # Generate initial findings data
   specify security scan .
   ```

## Examples

### 1. Claude Security Agent (`claude_security_agent.py`)

Demonstrates a complete security workflow using the MCP server:
- Run security scans
- Get triage instructions (skill invocation pattern)
- Get fix generation instructions (skill invocation pattern)
- Query security status
- Query specific findings

**Usage:**
```bash
# Scan current directory
python examples/mcp/claude_security_agent.py --target .

# Scan specific directory
python examples/mcp/claude_security_agent.py --target src/

# Use specific scanners
python examples/mcp/claude_security_agent.py --target . --scanners semgrep

# Show more findings in preview
python examples/mcp/claude_security_agent.py --target . --preview-count 10

# Verbose output
python examples/mcp/claude_security_agent.py --target . --verbose
```

**Expected Output:**
```
Step 1: Running security scan...
  Total findings: 5
  By severity:
    CRITICAL: 0
    HIGH: 2
    MEDIUM: 3

Step 2: Getting triage instruction...
  Action: invoke_skill
  Skill: .claude/skills/security-triage.md

Step 3: Getting fix generation instruction...
  Action: invoke_skill
  Skill: .claude/skills/security-fix.md

Step 4: Querying security status...
  Total findings: 5
  Security posture: HIGH RISK

Step 5: Querying all findings...
  1. SQL Injection in user_query
     ID: SEMGREP-SQL-001
     Severity: HIGH
     ...
```

### 2. Security Dashboard (`security_dashboard.py`)

Aggregates security status across multiple repositories:
- Query multiple repos concurrently
- Display unified security dashboard
- Show critical findings across repos

**Usage:**
```bash
# Dashboard for multiple repos
python examples/mcp/security_dashboard.py --repos /path/to/repo1 /path/to/repo2

# Current repo and sibling
python examples/mcp/security_dashboard.py --repos . ../other-project

# Show critical findings detail
python examples/mcp/security_dashboard.py --repos . ../other-project --show-critical

# Custom timeout
python examples/mcp/security_dashboard.py --repos . --timeout 60
```

**Expected Output:**
```
================ SECURITY DASHBOARD ================
Repository            | Posture      | Total | C | H | M | L | Triage
--------------------------------------------------------------------
jp-spec-kit          | GOOD         | 0     | 0 | 0 | 0 | 0 | NOT_RUN
other-project        | HIGH RISK    | 12    | 1 | 5 | 6 | 0 | NOT_RUN
--------------------------------------------------------------------

Summary:
  Total Repositories: 2
  Total Findings: 12
  Critical Findings: 1
  High Findings: 5

Recommendations:
  URGENT: 1 repos have CRITICAL vulnerabilities!
          Review and fix immediately.
```

### 3. Shared Utilities (`mcp_utils.py`)

Common utilities used by both examples:
- Connection management with timeouts
- Response parsing with validation
- Path validation
- Constants for configuration

## Architecture

```
examples/mcp/
├── README.md                    # This file
├── mcp_utils.py                 # Shared utilities (DRY)
├── claude_security_agent.py     # Single-repo workflow
└── security_dashboard.py        # Multi-repo dashboard
```

### Key Design Decisions

1. **Shared Utilities**: Common code extracted to `mcp_utils.py` to avoid duplication
2. **Proper Error Handling**: Custom exception types, no broad `except Exception`
3. **Timeout Support**: All MCP operations have configurable timeouts
4. **Input Validation**: Path validation, response validation
5. **Type Safety**: Full type hints, runtime validation
6. **Security**: Safe environment variables, no stack trace exposure

## Troubleshooting

### "mcp package not installed"

```bash
uv add mcp
# or
pip install mcp
```

### "MCP server connection timeout"

- Check server health: `./scripts/bash/check-mcp-servers.sh`
- Increase timeout: `--timeout 60`

### "Could not connect to any MCP servers"

Make sure each repository has:
1. JP Spec Kit installed
2. Security scan has been run at least once (`specify security scan .`)
3. MCP server is configured in `.mcp.json`

### "Findings file not found"

Run a security scan first:
```bash
specify security scan .
```

## Related Documentation

- [Security MCP Server Guide](../../docs/guides/security-mcp-guide.md)
- [MCP Client Integration Guide](../../docs/guides/mcp-client-guide.md)
- [ADR-008: Security MCP Server Architecture](../../docs/adr/ADR-008-security-mcp-server-architecture.md)
