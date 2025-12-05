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
- Get triage instructions (skill invocation)
- Get fix generation instructions (skill invocation)
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
  Security posture: HIGH_RISK
  Total findings: 5

Step 5: Querying all findings...
  1. SQL Injection vulnerability
     Location: src/database.py:42
     Severity: HIGH
```

### 2. Security Dashboard (`security_dashboard.py`)

Demonstrates cross-repository security monitoring:
- Query status from multiple repositories
- Aggregate findings across projects
- Display unified security dashboard
- Show critical findings

**Usage:**
```bash
# Monitor multiple repositories
python examples/mcp/security_dashboard.py --repos /path/to/repo1 /path/to/repo2

# Monitor current and other project
python examples/mcp/security_dashboard.py --repos . ../other-project

# Show critical findings
python examples/mcp/security_dashboard.py --repos . ../other-project --show-critical
```

**Expected Output:**
```
================ SECURITY DASHBOARD ================

Repository            | Posture      | Total | C | H | M | L | Triage
-------------------------------------------------------------------------
jp-spec-kit          | GOOD         | 0     | 0 | 0 | 0 | 0 | NOT_RUN
my-api               | HIGH RISK    | 12    | 1 | 5 | 6 | 0 | 8TP/4FP
frontend-app         | MEDIUM       | 3     | 0 | 1 | 2 | 0 | NOT_RUN
-------------------------------------------------------------------------

Summary:
  Total Repositories: 3
  Total Findings: 15
  Critical Findings: 1
  High Findings: 6

Recommendations:
  URGENT: 1 repo has CRITICAL vulnerabilities!
          Review and fix immediately.
  WARNING: 1 repo has HIGH risk issues.
           Prioritize remediation.
```

## Architecture Notes

### MCP Server Design

The MCP server follows a **ZERO API CALLS** architecture:

1. **Tools** (actions):
   - `security_scan`: Runs scanners via subprocess
   - `security_triage`: Returns skill invocation instruction
   - `security_fix`: Returns skill invocation instruction

2. **Resources** (read-only data):
   - `security://findings`: List all findings
   - `security://status`: Security posture summary
   - `security://config`: Scanner configuration

3. **No LLM Calls**:
   - Server exposes data and orchestrates tools
   - AI agents consume the MCP server and invoke skills
   - Skills perform AI-powered analysis

### Skill Invocation Pattern

Instead of making LLM API calls, tools return **skill invocation instructions**:

```python
# Tool returns instruction
{
  "action": "invoke_skill",
  "skill": ".claude/skills/security-triage.md",
  "input_file": "docs/security/scan-results.json",
  "instruction": "Invoke security-triage skill to classify findings"
}

# AI agent then invokes the skill with context
```

This pattern:
- Separates concerns (MCP = I/O, AI = intelligence)
- Enables composability (any AI can consume)
- Reduces coupling (no LLM provider lock-in)
- Improves testability (no mocking APIs)

## Testing

### Test with MCP Inspector

```bash
# Install inspector
npm install -g @modelcontextprotocol/inspector

# Launch inspector
mcp-inspector python -m specify_cli.security.mcp_server

# Test tools and resources in the UI
```

### Test Examples

```bash
# Test Claude agent example
python examples/mcp/claude_security_agent.py --target .

# Test dashboard example (requires multiple repos with scans)
python examples/mcp/security_dashboard.py --repos . ../other-project
```

## Troubleshooting

### Error: "mcp package not installed"

```bash
uv add mcp
# or
pip install mcp
```

### Error: "Findings file not found"

Run a scan first:
```bash
specify security scan .
```

### Error: "Server not responding"

Verify installation:
```bash
python -c "import specify_cli.security.mcp_server"
```

## Related Documentation

- [Security MCP Server Guide](../../docs/guides/security-mcp-guide.md)
- [ADR-008: Security MCP Server Architecture](../../docs/adr/ADR-008-security-mcp-server-architecture.md)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/docs/)

---

**Last Updated:** 2025-12-05
