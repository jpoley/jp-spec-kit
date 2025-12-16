# Security MCP Server Guide

## Overview

The Flowspec Security Scanner MCP Server exposes security scanning capabilities through the Model Context Protocol (MCP). This enables AI agents, IDEs, and dashboards to query security findings and trigger scans programmatically.

**CRITICAL ARCHITECTURE NOTE:** The MCP server does NOT make LLM API calls. It:
1. Exposes security data as resources (read-only queries)
2. Returns skill invocation instructions for AI tools
3. Runs scanners via subprocess orchestration

See [ADR-008: Security MCP Server Architecture](../adr/ADR-008-security-mcp-server-architecture.md) for design decisions.

---

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Tools](#tools)
   - [security_scan](#security_scan)
   - [security_triage](#security_triage)
   - [security_fix](#security_fix)
4. [Resources](#resources)
   - [security://findings](#securityfindings)
   - [security://findings/{id}](#securityfindingsid)
   - [security://status](#securitystatus)
   - [security://config](#securityconfig)
5. [Usage Examples](#usage-examples)
6. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- Python 3.11+
- Flowspec installed (`uv tool install . --force`)
- MCP-compatible client (Claude Desktop, MCP Inspector, etc.)

### Install MCP Python SDK

The MCP server requires the `mcp` Python package:

```bash
# Add to dependencies
uv add mcp

# Or install globally
pip install mcp
```

---

## Configuration

### Add to .mcp.json

Add the security scanner server to your `.mcp.json` configuration:

```json
{
  "mcpServers": {
    "flowspec-security": {
      "command": "python",
      "args": ["-m", "specify_cli.security.mcp_server"],
      "env": {},
      "description": "Flowspec Security Scanner: scan, triage, and fix security findings"
    }
  }
}
```

### Verify Server is Running

Use the MCP Inspector to test the server:

```bash
# Install MCP Inspector (if not already installed)
npm install -g @modelcontextprotocol/inspector

# Test the server
mcp-inspector python -m specify_cli.security.mcp_server
```

---

## Tools

Tools are actions that can be invoked by MCP clients. The security server provides three primary tools.

### security_scan

Trigger a security scan on the target directory.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target` | string | `"."` | Directory to scan (relative to project root) |
| `scanners` | list[string] | all available | List of scanners to run (e.g., `["semgrep"]`) |
| `fail_on` | list[string] | `["critical", "high"]` | Severity levels that cause failure |

**Returns:**

```json
{
  "findings_count": 42,
  "by_severity": {
    "critical": 2,
    "high": 8,
    "medium": 15,
    "low": 17,
    "info": 0
  },
  "should_fail": true,
  "fail_on": ["critical", "high"],
  "findings_file": "docs/security/scan-results.json",
  "metadata": {
    "scanners_used": ["semgrep"],
    "target": "."
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `findings_count` | integer | Total number of findings |
| `by_severity` | object | Count of findings by severity level |
| `should_fail` | boolean | True if findings match any `fail_on` severity |
| `fail_on` | list[string] | Severity levels that trigger failure |
| `findings_file` | string | Path to findings JSON file |
| `metadata` | object | Scan metadata (scanners used, target) |

**Example:**

```python
from mcp.client import Client

async with Client("flowspec-security") as client:
    result = await client.call_tool(
        "security_scan",
        arguments={
            "target": "src/",
            "scanners": ["semgrep"],
        }
    )
    print(f"Found {result['findings_count']} vulnerabilities")
```

---

### security_triage

Get skill invocation instruction for AI-powered triage.

**IMPORTANT:** This tool does NOT perform triage directly. It returns instructions for the AI tool to invoke the `security-triage.md` skill.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `findings_file` | string | latest scan | Path to findings JSON file |

**Returns:**

```json
{
  "action": "invoke_skill",
  "skill": ".claude/skills/security-triage.md",
  "input_file": "docs/security/scan-results.json",
  "output_file": "docs/security/triage-results.json",
  "instruction": "Invoke security-triage skill to classify findings as TP/FP/NI"
}
```

**Example:**

```python
async with Client("flowspec-security") as client:
    # Get triage instruction
    instruction = await client.call_tool("security_triage")

    # AI tool should then invoke the skill
    print(f"Next action: {instruction['action']}")
    print(f"Invoke skill: {instruction['skill']}")
    # --> AI invokes .claude/skills/security-triage.md
```

---

### security_fix

Get skill invocation instruction for fix generation.

**IMPORTANT:** This tool does NOT generate fixes directly. It returns instructions for the AI tool to invoke the `security-fix.md` skill.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `finding_ids` | list[string] | all true positives | Specific finding IDs to fix |

**Returns:**

```json
{
  "action": "invoke_skill",
  "skill": ".claude/skills/security-fix.md",
  "input_file": "docs/security/triage-results.json",
  "output_file": "docs/security/fix-suggestions.json",
  "instruction": "Invoke security-fix skill to generate remediation patches",
  "filter": {
    "finding_ids": ["SEMGREP-CWE-89-001"]
  }
}
```

**Example:**

```python
async with Client("flowspec-security") as client:
    # Get fix instruction
    instruction = await client.call_tool(
        "security_fix",
        arguments={"finding_ids": ["SEMGREP-001"]}
    )

    # AI tool should then invoke the skill
    # --> AI invokes .claude/skills/security-fix.md
```

---

## Resources

Resources are queryable data endpoints (read-only). They provide access to security findings, status, and configuration.

### security://findings

List all security findings with optional filtering.

**Query Parameters:**

> **Note:** The `security://findings` resource does **not** support query parameters for server-side filtering. All filtering (by severity, scanner, or limiting results) must be performed client-side after retrieving the full list of findings.

**Example:**

```python
async with Client("flowspec-security") as client:
    # Get all findings
    findings = await client.read_resource("security://findings")
    data = json.loads(findings.text)

    # Filter by severity (critical)
    critical = [f for f in data if f["severity"] == "critical"]

    # Filter by scanner (semgrep)
    semgrep = [f for f in data if f["scanner"] == "semgrep"]

    # Limit results
    top10 = data[:10]
```

---

### security://findings/{id}

Get a specific finding by its ID.

**Example:**

```python
async with Client("flowspec-security") as client:
    finding = await client.read_resource("security://findings/SEMGREP-CWE-89-001")
    data = json.loads(finding.text)

    print(f"Title: {data['title']}")
    print(f"Severity: {data['severity']}")
    print(f"Location: {data['location']['file']}:{data['location']['line_start']}")
```

---

### security://status

Get overall security posture and summary statistics.

**Returns:**

```json
{
  "total_findings": 42,
  "by_severity": {
    "critical": 2,
    "high": 8,
    "medium": 15,
    "low": 17,
    "info": 0
  },
  "triage_status": "completed",
  "true_positives": 10,
  "false_positives": 32,
  "security_posture": "high_risk"
}
```

**Security Posture Calculation:**

| Posture | Condition |
|---------|-----------|
| `critical` | Any critical findings |
| `high_risk` | >5 high severity findings |
| `medium_risk` | 1-5 high severity findings |
| `good` | No critical or high findings |

**Example:**

```python
async with Client("flowspec-security") as client:
    status = await client.read_resource("security://status")
    data = json.loads(status.text)

    print(f"Security Posture: {data['security_posture']}")
    print(f"Total Findings: {data['total_findings']}")
    print(f"True Positives: {data.get('true_positives', 'Not triaged')}")
```

---

### security://config

Get scanner configuration and available options.

**Returns:**

```json
{
  "available_scanners": ["semgrep", "trivy"],
  "default_scanners": ["semgrep"],
  "fail_on": ["critical", "high"],
  "findings_directory": "docs/security"
}
```

**Example:**

```python
async with Client("flowspec-security") as client:
    config = await client.read_resource("security://config")
    data = json.loads(config.text)

    print(f"Available Scanners: {data['available_scanners']}")
```

---

## Usage Examples

### Example 1: Security Workflow with Claude Agent

```python
from mcp.client import Client
import json

async def security_workflow():
    """Complete security workflow: scan → triage → fix."""

    async with Client("flowspec-security") as client:
        # 1. Run security scan
        print("Running security scan...")
        scan_result = await client.call_tool(
            "security_scan",
            arguments={"target": "src/", "scanners": ["semgrep"]}
        )
        print(f"Found {scan_result['findings_count']} vulnerabilities")

        # 2. Get triage instruction
        print("\nGetting triage instruction...")
        triage_instruction = await client.call_tool("security_triage")
        print(f"Next: {triage_instruction['instruction']}")

        # AI tool invokes .claude/skills/security-triage.md here
        # (not shown - this is done by the AI agent consuming the MCP server)

        # 3. Get fix instruction
        print("\nGetting fix instruction...")
        fix_instruction = await client.call_tool("security_fix")
        print(f"Next: {fix_instruction['instruction']}")

        # AI tool invokes .claude/skills/security-fix.md here

        # 4. Check final status
        status = await client.read_resource("security://status")
        status_data = json.loads(status.text)
        print(f"\nFinal Posture: {status_data['security_posture']}")
```

---

### Example 2: Cross-Repo Security Dashboard

```python
from mcp.client import Client
import json

async def security_dashboard(projects: list[str]):
    """Aggregate security status across multiple projects."""

    dashboard_data = []

    for project in projects:
        # Each project has its own MCP server instance
        async with Client(f"flowspec-security-{project}") as client:
            status = await client.read_resource("security://status")
            data = json.loads(status.text)

            dashboard_data.append({
                "project": project,
                "total_findings": data["total_findings"],
                "critical": data["by_severity"]["critical"],
                "high": data["by_severity"]["high"],
                "posture": data["security_posture"],
            })

    # Display dashboard
    print("\n=== Security Dashboard ===\n")
    for row in dashboard_data:
        print(f"{row['project']:20} | {row['posture']:12} | C:{row['critical']} H:{row['high']}")
```

---

### Example 3: Query Specific Vulnerability Types

```python
import json

async def find_sql_injections():
    """Find all SQL injection vulnerabilities."""

    async with Client("flowspec-security") as client:
        # Get all findings
        findings_response = await client.read_resource("security://findings")
        findings = json.loads(findings_response.text)

        # Filter for SQL injection (CWE-89)
        sql_injections = []
        for finding in findings:
            if finding.get("cwe_id") == "CWE-89":
                sql_injections.append(finding)

        print(f"Found {len(sql_injections)} SQL injection vulnerabilities:")
        for vuln in sql_injections:
            print(f"  - {vuln['location']['file']}:{vuln['location']['line_start']}")
```

---

## Troubleshooting

### Error: "mcp package not installed"

**Solution:** Install the MCP Python SDK:

```bash
uv add mcp
# or
pip install mcp
```

---

### Error: "Findings file not found"

**Cause:** No scan has been run yet.

**Solution:** Run `security_scan` tool first:

```python
await client.call_tool("security_scan", arguments={"target": "."})
```

---

### Error: "Triage results not found"

**Cause:** Triage has not been performed.

**Solution:**
1. Get triage instruction: `await client.call_tool("security_triage")`
2. AI tool invokes `.claude/skills/security-triage.md` skill
3. Then run `security_fix`

---

### Server Not Responding

**Solution:** Verify the server is configured correctly:

1. Check `.mcp.json` configuration
2. Test with MCP Inspector: `mcp-inspector python -m specify_cli.security.mcp_server`
3. Check Python path and virtual environment
4. Verify `specify_cli` is installed: `python -c "import specify_cli.security.mcp_server"`

---

### No Scanners Available

**Cause:** Required scanner tools (semgrep, trivy) are not installed.

**Solution:** Install scanners:

```bash
# Install semgrep
pip install semgrep

# Install trivy (Linux)
brew install aquasecurity/trivy/trivy
```

---

## Architecture Notes

### Why No LLM Calls?

The MCP server is designed to **expose data** and **orchestrate tools**, NOT to make LLM API calls. This architectural decision:

1. **Separates concerns**: MCP server handles I/O, AI tools handle intelligence
2. **Enables composability**: Any AI agent can consume the server
3. **Reduces coupling**: Server doesn't depend on specific LLM providers
4. **Improves testability**: No mocking LLM APIs in tests

### Skill Invocation Pattern

The `security_triage` and `security_fix` tools return **skill invocation instructions** rather than performing triage/fix directly. This pattern:

1. **Delegates to AI**: Skills are invoked by Claude/AI agents with context
2. **Preserves flexibility**: Skills can be updated independently
3. **Enables human-in-the-loop**: AI can ask for confirmation before applying fixes

Example workflow:

```
1. MCP Client calls security_triage tool
2. Server returns: "invoke .claude/skills/security-triage.md"
3. AI agent reads the skill and invokes it with findings data
4. Skill performs triage and writes results to JSON
5. MCP Client queries security://status to see results
```

---

## Related Documentation

- [ADR-008: Security MCP Server Architecture](../adr/ADR-008-security-mcp-server-architecture.md)
- [Security Commands PRD](../prd/flowspec-security-commands.md)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/docs/)

---

## Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review [ADR-008](../adr/ADR-008-security-mcp-server-architecture.md) for architecture details
3. Open an issue on the Flowspec repository

---

**Last Updated:** 2025-12-04
**Author:** Backend Engineer
**Version:** 1.0.0
