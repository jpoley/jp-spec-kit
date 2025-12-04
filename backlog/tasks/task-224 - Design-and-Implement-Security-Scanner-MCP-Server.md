---
id: task-224
title: Design and Implement Security Scanner MCP Server
status: To Do
assignee:
  - '@muckross'
created_date: '2025-12-03 02:16'
updated_date: '2025-12-04 14:21'
labels:
  - security
  - mcp
  - infrastructure
  - v2.0
dependencies: []
priority: high
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create MCP server exposing security scanning capabilities for tool composition. Enables other agents to query security findings, cross-repo dashboards, and IDE integrations.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Design MCP server schema with tools and resources
- [ ] #2 Implement security_scan tool
- [ ] #3 Implement security_triage tool
- [ ] #4 Implement security_fix tool
- [ ] #5 Expose security://findings resource
- [ ] #6 Expose security://status resource
- [ ] #7 Expose security://config resource
- [ ] #8 Add MCP server to .mcp.json configuration
- [ ] #9 Write MCP server documentation
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Design and Implement Security Scanner MCP Server

### Overview
Create MCP server exposing security scanning capabilities as tools/resources for IDE integrations and cross-repo dashboards.

### Step-by-Step Implementation

#### Step 1: Design MCP Server Schema (2 hours)
**File**: `docs/adr/ADR-007-security-mcp-server.md`

MCP tools to expose:
- `security_scan`: Run scan on repository
- `security_triage`: Triage findings with AI
- `security_fix`: Generate fixes
- `security_status`: Get security posture summary

MCP resources to expose:
- `security://findings`: List all findings
- `security://status`: Overall security status
- `security://config`: Current security configuration

#### Step 2: Implement MCP Server (4 hours)
**File**: `src/specify_cli/security/mcp_server.py`

```python
from mcp.server import Server
from mcp.types import Tool, Resource

server = Server("security-scanner")

@server.tool()
async def security_scan(repo_path: str, fail_on: str = "critical,high") -> dict:
    """Run security scan on repository."""
    result = subprocess.run([
        "specify", "security", "scan",
        "--path", repo_path,
        "--fail-on", fail_on,
        "--format", "json"
    ], capture_output=True)
    
    return json.loads(result.stdout)

@server.resource("security://findings")
async def get_findings() -> str:
    """Get all security findings."""
    findings_file = "docs/security/scan-results.json"
    if Path(findings_file).exists():
        with open(findings_file) as f:
            return f.read()
    return json.dumps({"findings": []})
```

#### Step 3: Add to .mcp.json Configuration (1 hour)
```json
{
  "mcpServers": {
    "security-scanner": {
      "command": "uv",
      "args": ["tool", "run", "specify-mcp-security"]
    }
  }
}
```

#### Step 4: Documentation (2 hours)
**File**: `docs/reference/security-mcp-server.md`

Sections:
1. MCP server overview
2. Available tools
3. Available resources
4. Integration examples (Claude Desktop, IDEs)
5. Cross-repo security dashboard use case

#### Step 5: Testing (2 hours)
- Test MCP tool invocations
- Test MCP resource access
- Test error handling
- Test with Claude Desktop

### Dependencies
- MCP SDK
- Security commands implemented

### Estimated Effort
**Total**: 11 hours (1.4 days)
<!-- SECTION:PLAN:END -->
