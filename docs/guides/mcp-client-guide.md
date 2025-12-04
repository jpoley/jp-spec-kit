# MCP Client Integration Guide

## Overview

This guide shows how to build client applications that consume the JP Spec Kit Security MCP Server. You'll learn how to connect to the server, invoke tools, query resources, and build AI-powered security workflows.

**Target Audience:**
- Security engineers building automation
- DevOps teams integrating security into CI/CD
- Developers creating security dashboards
- AI agent developers building security assistants

**Prerequisites:**
- Python 3.11+
- JP Spec Kit installed (`uv tool install . --force`)
- MCP Python SDK (`pip install mcp`)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [MCP Client Basics](#mcp-client-basics)
3. [Tool Invocation](#tool-invocation)
4. [Resource Queries](#resource-queries)
5. [Building Security Workflows](#building-security-workflows)
6. [AI Agent Integration](#ai-agent-integration)
7. [Dashboard Examples](#dashboard-examples)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Install Dependencies

```bash
# Install MCP Python SDK
pip install mcp

# Optional: Rich for better terminal output
pip install rich

# Optional: Anthropic for AI integration
pip install anthropic
```

### Basic Client Example

```python
import asyncio
import json
from mcp.client import Client
from mcp.client.stdio import stdio_client, StdioServerParameters

async def basic_example():
    """Basic MCP client example."""

    # Configure server connection
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "specify_cli.security.mcp_server"],
        env={},
    )

    # Connect to server
    async with stdio_client(server_params) as (read, write):
        async with Client(read, write) as client:
            # Call security_scan tool
            result = await client.call_tool(
                "security_scan",
                arguments={"target": "."}
            )

            print(f"Found {result['findings_count']} vulnerabilities")
            print(f"Critical: {result['by_severity']['critical']}")
            print(f"High: {result['by_severity']['high']}")

# Run the example
asyncio.run(basic_example())
```

---

## MCP Client Basics

### Connection Lifecycle

The MCP client uses a context manager pattern for connection management:

```python
from mcp.client import Client
from mcp.client.stdio import stdio_client, StdioServerParameters

async def connect_to_server():
    """Demonstrate MCP connection lifecycle."""

    # 1. Configure server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "specify_cli.security.mcp_server"],
        env={},
    )

    # 2. Create stdio transport
    async with stdio_client(server_params) as (read, write):
        # 3. Create MCP client
        async with Client(read, write) as client:
            # 4. Use the client
            config = await client.read_resource("security://config")
            data = json.loads(config.text)
            print(f"Available scanners: {data['available_scanners']}")

            # 5. Connection automatically closes when exiting context
```

### Error Handling

Always wrap MCP calls in try/except blocks:

```python
from mcp.client import Client

async def safe_scan():
    """Example with proper error handling."""

    try:
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "specify_cli.security.mcp_server"],
            env={},
        )

        async with stdio_client(server_params) as (read, write):
            async with Client(read, write) as client:
                result = await client.call_tool("security_scan")
                print(f"Scan complete: {result['findings_count']} findings")

    except FileNotFoundError:
        print("Error: MCP server not found. Is JP Spec Kit installed?")
    except ConnectionError:
        print("Error: Could not connect to MCP server")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

---

## Tool Invocation

Tools are actions that can be invoked on the MCP server. The security server provides three primary tools.

### security_scan

Run a security scan on the target directory.

```python
async def run_scan(client: Client, target: str = "."):
    """Run security scan with custom parameters."""

    result = await client.call_tool(
        "security_scan",
        arguments={
            "target": target,              # Directory to scan
            "scanners": ["semgrep"],       # Scanners to use
            "fail_on": ["critical", "high"] # Severity threshold
        }
    )

    print(f"Scan Results:")
    print(f"  Total Findings: {result['findings_count']}")
    print(f"  Critical: {result['by_severity']['critical']}")
    print(f"  High: {result['by_severity']['high']}")
    print(f"  Medium: {result['by_severity']['medium']}")
    print(f"  Should Fail: {result['should_fail']}")
    print(f"  Findings File: {result['findings_file']}")

    return result
```

### security_triage

Get skill invocation instruction for AI-powered triage.

**CRITICAL:** This tool does NOT perform triage directly. It returns instructions for the AI to invoke the security-triage skill.

```python
async def get_triage_instruction(client: Client):
    """Get triage instruction from MCP server."""

    instruction = await client.call_tool("security_triage")

    if "error" in instruction:
        print(f"Error: {instruction['error']}")
        print(f"Suggestion: {instruction['suggestion']}")
        return None

    print(f"Action: {instruction['action']}")
    print(f"Skill: {instruction['skill']}")
    print(f"Input: {instruction['input_file']}")
    print(f"Output: {instruction['output_file']}")
    print(f"Instruction: {instruction['instruction']}")

    # AI agent would now invoke the skill
    # Example: claude.invoke_skill(instruction['skill'], instruction['input_file'])

    return instruction
```

### security_fix

Get skill invocation instruction for fix generation.

```python
async def get_fix_instruction(client: Client, finding_ids: list[str] | None = None):
    """Get fix instruction from MCP server."""

    arguments = {}
    if finding_ids:
        arguments["finding_ids"] = finding_ids

    instruction = await client.call_tool("security_fix", arguments=arguments)

    if "error" in instruction:
        print(f"Error: {instruction['error']}")
        return None

    print(f"Action: {instruction['action']}")
    print(f"Skill: {instruction['skill']}")

    if "filter" in instruction:
        print(f"Filter: {instruction['filter']}")

    return instruction
```

---

## Resource Queries

Resources are read-only data endpoints. They provide access to security findings, status, and configuration.

### security://findings

Get all security findings.

```python
async def get_all_findings(client: Client) -> list[dict]:
    """Get all security findings."""

    findings_response = await client.read_resource("security://findings")
    findings = json.loads(findings_response.text)

    print(f"Retrieved {len(findings)} findings")

    # Filter by severity
    critical = [f for f in findings if f["severity"] == "critical"]
    print(f"Critical findings: {len(critical)}")

    # Filter by scanner
    semgrep = [f for f in findings if f["scanner"] == "semgrep"]
    print(f"Semgrep findings: {len(semgrep)}")

    return findings
```

### security://findings/{id}

Get a specific finding by ID.

```python
async def get_finding_details(client: Client, finding_id: str) -> dict | None:
    """Get details for a specific finding."""

    finding_response = await client.read_resource(
        f"security://findings/{finding_id}"
    )
    finding = json.loads(finding_response.text)

    if "error" in finding:
        print(f"Finding not found: {finding_id}")
        return None

    print(f"Finding: {finding['title']}")
    print(f"Severity: {finding['severity']}")
    print(f"Location: {finding['location']['file']}:{finding['location']['line_start']}")
    print(f"CWE: {finding.get('cwe_id', 'N/A')}")

    return finding
```

### security://status

Get overall security posture.

```python
async def get_security_status(client: Client) -> dict:
    """Get overall security status."""

    status_response = await client.read_resource("security://status")
    status = json.loads(status_response.text)

    print(f"Security Posture: {status['security_posture'].upper()}")
    print(f"Total Findings: {status['total_findings']}")
    print(f"By Severity:")
    print(f"  Critical: {status['by_severity']['critical']}")
    print(f"  High: {status['by_severity']['high']}")
    print(f"  Medium: {status['by_severity']['medium']}")
    print(f"  Low: {status['by_severity']['low']}")

    if status['triage_status'] == "completed":
        print(f"Triage Status: Complete")
        print(f"  True Positives: {status['true_positives']}")
        print(f"  False Positives: {status['false_positives']}")
    else:
        print(f"Triage Status: {status['triage_status']}")

    return status
```

### security://config

Get scanner configuration.

```python
async def get_config(client: Client) -> dict:
    """Get scanner configuration."""

    config_response = await client.read_resource("security://config")
    config = json.loads(config_response.text)

    print(f"Available Scanners: {config['available_scanners']}")
    print(f"Default Scanners: {config['default_scanners']}")
    print(f"Fail On: {config['fail_on']}")
    print(f"Findings Directory: {config['findings_directory']}")

    return config
```

---

## Building Security Workflows

### End-to-End Security Workflow

Combine tools and resources to build complete workflows:

```python
async def security_workflow():
    """Complete security workflow: scan → status → triage → fix."""

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "specify_cli.security.mcp_server"],
        env={},
    )

    async with stdio_client(server_params) as (read, write):
        async with Client(read, write) as client:
            print("=== Security Workflow ===\n")

            # Step 1: Run scan
            print("[1/4] Running security scan...")
            scan_result = await client.call_tool(
                "security_scan",
                arguments={"target": "src/"}
            )
            print(f"  ✓ Found {scan_result['findings_count']} vulnerabilities\n")

            if scan_result['findings_count'] == 0:
                print("✓ No vulnerabilities found!")
                return

            # Step 2: Check status
            print("[2/4] Checking security posture...")
            status_response = await client.read_resource("security://status")
            status = json.loads(status_response.text)
            print(f"  Posture: {status['security_posture'].upper()}\n")

            # Step 3: Get triage instruction
            print("[3/4] Getting triage instruction...")
            triage_instruction = await client.call_tool("security_triage")
            if "error" not in triage_instruction:
                print(f"  ✓ Next: {triage_instruction['instruction']}\n")

            # Step 4: Get fix instruction
            print("[4/4] Getting fix instruction...")
            fix_instruction = await client.call_tool("security_fix")
            if "error" not in fix_instruction:
                print(f"  ✓ Next: {fix_instruction['instruction']}\n")

            print("=== Workflow Complete ===")
```

### Vulnerability Filtering

Filter findings by various criteria:

```python
async def filter_vulnerabilities(client: Client):
    """Filter vulnerabilities by various criteria."""

    # Get all findings
    findings_response = await client.read_resource("security://findings")
    findings = json.loads(findings_response.text)

    # Filter by CWE (SQL Injection)
    sql_injections = [
        f for f in findings if f.get("cwe_id") == "CWE-89"
    ]
    print(f"SQL Injections: {len(sql_injections)}")

    # Filter by file
    auth_findings = [
        f for f in findings
        if "auth" in f["location"]["file"].lower()
    ]
    print(f"Auth-related findings: {len(auth_findings)}")

    # Filter by severity threshold
    high_risk = [
        f for f in findings
        if f["severity"] in ["critical", "high"]
    ]
    print(f"High-risk findings: {len(high_risk)}")

    # Sort by CVSS score
    sorted_findings = sorted(
        findings,
        key=lambda f: f.get("cvss_score", 0),
        reverse=True
    )
    print(f"Highest CVSS: {sorted_findings[0].get('cvss_score', 'N/A')}")

    return {
        "sql_injections": sql_injections,
        "auth_findings": auth_findings,
        "high_risk": high_risk,
    }
```

---

## AI Agent Integration

### Using with Claude

Integrate the MCP server with Claude for AI-powered security analysis:

```python
from anthropic import Anthropic

async def claude_security_agent():
    """Use Claude to analyze security findings via MCP server."""

    # Initialize Claude client
    claude = Anthropic()

    # Connect to MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "specify_cli.security.mcp_server"],
        env={},
    )

    async with stdio_client(server_params) as (read, write):
        async with Client(read, write) as mcp_client:
            # Run scan
            scan_result = await mcp_client.call_tool("security_scan")

            if scan_result['findings_count'] == 0:
                print("No vulnerabilities found!")
                return

            # Get triage instruction
            triage_instruction = await mcp_client.call_tool("security_triage")

            # Use Claude to invoke the skill
            # NOTE: In production, Claude would invoke the skill natively
            # This example shows the pattern

            message = claude.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": f"Please invoke the security triage skill.\n\n"
                                   f"Instruction: {triage_instruction['instruction']}\n"
                                   f"Skill: {triage_instruction['skill']}\n"
                                   f"Input: {triage_instruction['input_file']}\n"
                                   f"Output: {triage_instruction['output_file']}"
                    }
                ]
            )

            print(f"Claude response: {message.content}")
```

### Skill Invocation Pattern

The MCP server returns skill invocation instructions rather than making LLM API calls:

```python
async def skill_invocation_example(client: Client):
    """Example of skill invocation pattern."""

    # 1. MCP server returns skill invocation instruction
    instruction = await client.call_tool("security_triage")

    # 2. Instruction tells AI what to do
    print(f"Action: {instruction['action']}")          # "invoke_skill"
    print(f"Skill: {instruction['skill']}")            # ".claude/skills/security-triage.md"
    print(f"Input: {instruction['input_file']}")       # "docs/security/scan-results.json"
    print(f"Output: {instruction['output_file']}")     # "docs/security/triage-results.json"

    # 3. AI agent invokes the skill (not shown - done by Claude)
    # claude.invoke_skill(
    #     skill_path=instruction['skill'],
    #     input_file=instruction['input_file'],
    #     output_file=instruction['output_file']
    # )

    # 4. Check results via MCP resource
    status = await client.read_resource("security://status")
    status_data = json.loads(status.text)
    print(f"Triage Status: {status_data['triage_status']}")
```

---

## Dashboard Examples

### Basic Dashboard

Create a simple security dashboard:

```python
from rich.console import Console
from rich.table import Table

async def create_dashboard():
    """Create a basic security dashboard."""

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "specify_cli.security.mcp_server"],
        env={},
    )

    async with stdio_client(server_params) as (read, write):
        async with Client(read, write) as client:
            # Get status
            status_response = await client.read_resource("security://status")
            status = json.loads(status_response.text)

            # Create table
            console = Console()
            table = Table(title="Security Dashboard")

            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="bold")

            table.add_row("Security Posture", status['security_posture'].upper())
            table.add_row("Total Findings", str(status['total_findings']))
            table.add_row("Critical", str(status['by_severity']['critical']))
            table.add_row("High", str(status['by_severity']['high']))
            table.add_row("Medium", str(status['by_severity']['medium']))
            table.add_row("Low", str(status['by_severity']['low']))

            if status['triage_status'] == "completed":
                table.add_row("True Positives", str(status['true_positives']))
                table.add_row("False Positives", str(status['false_positives']))

            console.print(table)
```

### Multi-Project Dashboard

See `examples/mcp/security_dashboard.py` for a complete multi-project dashboard example.

---

## Best Practices

### 1. Connection Management

Always use context managers for automatic cleanup:

```python
# GOOD: Automatic cleanup
async with stdio_client(server_params) as (read, write):
    async with Client(read, write) as client:
        result = await client.call_tool("security_scan")

# BAD: Manual cleanup required
client = Client(read, write)
result = await client.call_tool("security_scan")
client.close()  # Easy to forget!
```

### 2. Error Handling

Handle specific errors gracefully:

```python
try:
    result = await client.call_tool("security_scan")
except FileNotFoundError:
    print("MCP server not found")
except ConnectionError:
    print("Connection failed")
except json.JSONDecodeError:
    print("Invalid response format")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 3. Resource Caching

Cache resource queries when appropriate:

```python
class SecurityClient:
    def __init__(self):
        self._config_cache = None

    async def get_config(self, client: Client) -> dict:
        """Get config with caching."""
        if self._config_cache is None:
            response = await client.read_resource("security://config")
            self._config_cache = json.loads(response.text)
        return self._config_cache
```

### 4. Async Best Practices

Use `asyncio.gather` for parallel operations:

```python
async def parallel_queries(client: Client):
    """Run multiple queries in parallel."""

    status_task = client.read_resource("security://status")
    config_task = client.read_resource("security://config")
    findings_task = client.read_resource("security://findings")

    # Wait for all to complete
    status, config, findings = await asyncio.gather(
        status_task,
        config_task,
        findings_task
    )

    return {
        "status": json.loads(status.text),
        "config": json.loads(config.text),
        "findings": json.loads(findings.text),
    }
```

### 5. Logging

Add proper logging for debugging:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def logged_scan(client: Client):
    """Scan with logging."""
    logger.info("Starting security scan...")

    try:
        result = await client.call_tool("security_scan")
        logger.info(f"Scan complete: {result['findings_count']} findings")
        return result
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        raise
```

---

## Troubleshooting

### Error: "MCP server not found"

**Cause:** JP Spec Kit not installed or Python path incorrect.

**Solution:**
```bash
# Install JP Spec Kit
uv tool install . --force

# Verify installation
python -c "import specify_cli.security.mcp_server"
```

### Error: "Connection refused"

**Cause:** MCP server not starting properly.

**Solution:**
```bash
# Test server manually
python -m specify_cli.security.mcp_server

# Check for import errors
python -c "from mcp.server.fastmcp import FastMCP"
```

### Error: "Findings file not found"

**Cause:** No scan has been run yet.

**Solution:**
```python
# Run scan first
await client.call_tool("security_scan", arguments={"target": "."})

# Then query findings
findings = await client.read_resource("security://findings")
```

### Error: "Invalid response format"

**Cause:** Response is not valid JSON.

**Solution:**
```python
try:
    response = await client.read_resource("security://status")
    data = json.loads(response.text)
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
    print(f"Raw response: {response.text}")
```

---

## Related Documentation

- [Security MCP Server Guide](security-mcp-guide.md) - Server-side documentation
- [ADR-008: Security MCP Server Architecture](../adr/ADR-008-security-mcp-server-architecture.md)
- [Security Commands PRD](../prd/jpspec-security-commands.md)
- [Example: Claude Security Agent](../../examples/mcp/claude_security_agent.py)
- [Example: Security Dashboard](../../examples/mcp/security_dashboard.py)

---

## Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [Security MCP Server Guide](security-mcp-guide.md)
3. Open an issue on the JP Spec Kit repository

---

**Last Updated:** 2025-12-04
**Author:** Backend Engineer
**Version:** 1.0.0
