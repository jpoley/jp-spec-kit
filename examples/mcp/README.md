# MCP Client Examples

This directory contains example scripts demonstrating how to build clients that consume the JP Spec Kit Security MCP Server.

## Examples

### 1. Claude Security Agent (`claude_security_agent.py`)

An AI-powered security agent that orchestrates the complete security workflow:

- Runs security scans via MCP server
- Triages findings using AI classification
- Generates fix suggestions for vulnerabilities
- Reports security posture

**Usage:**

```bash
# Install dependencies
pip install mcp anthropic

# Set API key
export ANTHROPIC_API_KEY="sk-..."

# Run the agent
python examples/mcp/claude_security_agent.py
```

**Architecture:**

```
┌─────────────────────┐
│  Claude Security    │
│      Agent          │
│  (MCP Client)       │
└──────────┬──────────┘
           │
           │ MCP Protocol (stdio)
           ▼
┌─────────────────────┐
│   JP Spec Kit       │
│   Security Server   │
│   (MCP Server)      │
└──────────┬──────────┘
           │
           ├──► security_scan (tool)
           ├──► security_triage (tool)
           ├──► security_fix (tool)
           │
           ├──► security://findings (resource)
           ├──► security://status (resource)
           └──► security://config (resource)
```

**Key Features:**

- End-to-end workflow automation
- AI-powered triage and fix generation
- Zero-API architecture (MCP server doesn't make LLM calls)
- Skill invocation pattern for AI tasks

---

### 2. Security Dashboard (`security_dashboard.py`)

A cross-repository security dashboard that aggregates findings across multiple projects:

- Monitors multiple repositories
- Aggregates security metrics
- Displays posture across projects
- Exports dashboard data to JSON

**Usage:**

```bash
# Install dependencies
pip install mcp rich

# Edit PROJECTS list in the script
# Update with your actual project paths

# Run the dashboard
python examples/mcp/security_dashboard.py
```

**Output:**

```
Monitoring 4 projects...

=== Security Dashboard ===

┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━┳━━━━━━┳━━━━━━━━┳━━━━━┳━━━━━━━━━━━━┓
┃ Project            ┃ Posture    ┃ Total ┃ Critical ┃ High ┃ Medium ┃ Low ┃ Triage     ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━╇━━━━━━╇━━━━━━━━╇━━━━━╇━━━━━━━━━━━━┩
│ api-service        │ CRITICAL   │    42 │        5 │   12 │     15 │  10 │ completed  │
│ web-app            │ HIGH RISK  │    28 │        0 │    8 │     12 │   8 │ not_run    │
│ mobile-backend     │ GOOD       │     3 │        0 │    0 │      2 │   1 │ not_run    │
│ jp-spec-kit        │ GOOD       │     0 │        0 │    0 │      0 │   0 │ not_run    │
└────────────────────┴────────────┴───────┴──────────┴──────┴────────┴─────┴────────────┘

╭─ Summary ─────────────────╮
│ Total Projects: 4         │
│ Total Findings: 73        │
│ Critical: 5               │
│ High: 20                  │
│ Projects at Risk: 2       │
╰───────────────────────────╯

✓ Dashboard exported to security-dashboard.json
```

**Use Cases:**

- Security team monitoring multiple projects
- Organization-wide security posture tracking
- Compliance reporting across repos
- Identifying security debt hotspots

---

## Installation

### Prerequisites

1. **JP Spec Kit** must be installed:

```bash
cd /path/to/jp-spec-kit
uv tool install . --force
```

2. **MCP Python SDK**:

```bash
pip install mcp
```

3. **Optional dependencies**:

```bash
# For rich terminal output (dashboard)
pip install rich

# For AI integration (Claude agent)
pip install anthropic
```

### Verify Installation

```bash
# Test MCP server
python -m specify_cli.security.mcp_server --help

# Test MCP client
python -c "from mcp.client import Client; print('MCP client OK')"
```

---

## Architecture

### Zero-API Design

The MCP server follows a **zero-API architecture**:

1. **MCP Server exposes data** (no LLM API calls)
2. **Returns skill invocation instructions** (for AI tools)
3. **Runs scanners via subprocess** (semgrep, trivy, etc.)

**Why this matters:**

- **Separation of concerns**: MCP server handles I/O, AI tools handle intelligence
- **Composability**: Any AI agent can consume the server
- **Testability**: No mocking LLM APIs in tests
- **Flexibility**: Skills can be updated independently

### Skill Invocation Pattern

```
┌─────────────────┐
│   MCP Client    │
│  (Your Script)  │
└────────┬────────┘
         │
         │ 1. Call security_triage tool
         ▼
┌─────────────────┐
│   MCP Server    │
│  (JP Spec Kit)  │
└────────┬────────┘
         │
         │ 2. Return skill invocation instruction
         │    { "action": "invoke_skill",
         │      "skill": ".claude/skills/security-triage.md",
         │      "input_file": "docs/security/scan-results.json" }
         ▼
┌─────────────────┐
│   AI Agent      │
│   (Claude)      │
└────────┬────────┘
         │
         │ 3. Invoke skill with findings data
         │ 4. Write triage results to JSON
         ▼
┌─────────────────┐
│  Triage Results │
│     (JSON)      │
└─────────────────┘
```

---

## Configuration

### .mcp.json

The MCP server is configured in `.mcp.json` at the project root:

```json
{
  "mcpServers": {
    "jpspec-security": {
      "command": "python",
      "args": ["-m", "specify_cli.security.mcp_server"],
      "env": {},
      "description": "JP Spec Kit Security Scanner: scan, triage, and fix security findings"
    }
  }
}
```

### Environment Variables

You can configure the server with environment variables:

```python
server_params = StdioServerParameters(
    command="python",
    args=["-m", "specify_cli.security.mcp_server"],
    env={
        "PROJECT_ROOT": "/path/to/project",  # Optional: override project root
    },
)
```

---

## Extending the Examples

### Custom Workflows

Build custom workflows by combining tools and resources:

```python
async def custom_workflow(client: Client):
    """Custom security workflow."""

    # 1. Get config to check available scanners
    config = await client.read_resource("security://config")
    scanners = json.loads(config.text)["available_scanners"]

    # 2. Run scan with all available scanners
    result = await client.call_tool(
        "security_scan",
        arguments={"scanners": scanners}
    )

    # 3. Filter findings by CWE
    findings = await client.read_resource("security://findings")
    sql_injections = [
        f for f in json.loads(findings.text)
        if f.get("cwe_id") == "CWE-89"
    ]

    # 4. Generate fixes for SQL injections only
    if sql_injections:
        fix_instruction = await client.call_tool(
            "security_fix",
            arguments={
                "finding_ids": [f["id"] for f in sql_injections]
            }
        )

    return result
```

### Custom Filters

Create reusable filter functions:

```python
def filter_by_cwe(findings: list[dict], cwe_id: str) -> list[dict]:
    """Filter findings by CWE ID."""
    return [f for f in findings if f.get("cwe_id") == cwe_id]

def filter_by_file_pattern(findings: list[dict], pattern: str) -> list[dict]:
    """Filter findings by file path pattern."""
    import re
    regex = re.compile(pattern)
    return [f for f in findings if regex.search(f["location"]["file"])]

def filter_by_severity_threshold(findings: list[dict], min_severity: str) -> list[dict]:
    """Filter findings by minimum severity."""
    severity_order = ["info", "low", "medium", "high", "critical"]
    min_index = severity_order.index(min_severity)
    return [
        f for f in findings
        if severity_order.index(f["severity"]) >= min_index
    ]
```

---

## Testing

### Unit Tests

Test your MCP clients with mock servers:

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_scan_workflow():
    """Test security scan workflow."""

    # Mock MCP client
    mock_client = AsyncMock()
    mock_client.call_tool.return_value = {
        "findings_count": 10,
        "by_severity": {"critical": 2, "high": 3, "medium": 5, "low": 0},
        "should_fail": True,
    }

    # Test your workflow
    result = await run_scan(mock_client)

    assert result["findings_count"] == 10
    assert result["should_fail"] is True
```

### Integration Tests

Test against the actual MCP server:

```bash
# Run integration tests
pytest tests/integration/test_mcp_client.py

# Test with real MCP server
python examples/mcp/claude_security_agent.py
```

---

## Best Practices

1. **Use context managers** for automatic connection cleanup
2. **Handle errors gracefully** with try/except blocks
3. **Cache resources** when appropriate (config doesn't change)
4. **Use async/await** for parallel operations
5. **Add logging** for debugging and monitoring
6. **Document workflows** for team collaboration

---

## Troubleshooting

### Error: "MCP server not found"

```bash
# Install JP Spec Kit
uv tool install . --force

# Verify installation
python -c "import specify_cli.security.mcp_server"
```

### Error: "mcp package not installed"

```bash
pip install mcp
```

### Error: "Findings file not found"

Run a scan first:

```python
await client.call_tool("security_scan", arguments={"target": "."})
```

---

## Related Documentation

- [MCP Client Integration Guide](../../docs/guides/mcp-client-guide.md) - Comprehensive client guide
- [Security MCP Server Guide](../../docs/guides/security-mcp-guide.md) - Server documentation
- [ADR-008: Security MCP Server Architecture](../../docs/adr/ADR-008-security-mcp-server-architecture.md)

---

## Contributing

To add new examples:

1. Create a new Python file in `examples/mcp/`
2. Add documentation in this README
3. Include usage instructions and requirements
4. Test the example thoroughly
5. Submit a PR

---

**Last Updated:** 2025-12-04
**Version:** 1.0.0
