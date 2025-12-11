# ADR-008: Security Scanner MCP Server Architecture

**Status:** Proposed
**Date:** 2025-12-02
**Author:** Enterprise Software Architect
**Context:** /flow:security commands - MCP server for tool composition (v2.0 feature)
**Supersedes:** None
**Amended by:** None

---

## Strategic Context (Penthouse View)

### Business Problem

Security scanning currently operates in **isolation**:
- Findings are locked in local JSON files (`docs/security/{feature}-scan-results.json`)
- Other AI agents can't query vulnerability status
- No cross-repo security dashboard
- IDE integrations require custom parsers

**The Core Tension:** Security data is valuable for **multiple consumers** (CLI, IDE, dashboard, other agents), but **each requires a custom integration**.

**Business Impact:**
- **Limited Composability:** Can't combine security scanning with other agents (e.g., "Generate ADR for all CWE-89 findings")
- **Fragmented UX:** Developers switch between CLI, IDE, and web dashboard
- **Maintenance Burden:** Each integration point requires custom code

### Business Value (v2.0 Strategic Investment)

**Primary Value Streams:**

1. **Tool Composition** - Other agents can query security findings (MCP protocol)
2. **Cross-Repo Dashboard** - Aggregate security posture across all projects
3. **IDE Integration** - Real-time vulnerability highlighting in VS Code
4. **Agent Orchestration** - Chain security scanning with other workflows

**Success Metrics:**

| Metric | Target | Timeline |
|--------|--------|----------|
| MCP client adoption | >5 integrations | 6 months |
| Cross-repo queries | >100/month | 3 months |
| Dashboard active users | >20 users | 3 months |

### Investment Justification (Selling the Option)

**Option Value:**
- **Composability Premium:** MCP enables exponential value (N agents × M tools = N×M integrations)
- **Platform Play:** Security MCP server positions Flowspec as security platform, not just CLI
- **Competitive Moat:** First SDD toolkit with MCP-based security integration

**Cost:**
- **Development:** 2-3 weeks (MCP server + client examples)
- **Maintenance:** Low (MCP protocol is stable)

**Decision:** Build in v2.0 (after MVP validates demand)

---

## Decision

### Chosen Architecture: MCP Server with Tools + Resources

Implement **Security Scanner MCP Server** exposing:
1. **Tools** (actions agents can invoke):
   - `security_scan` - Trigger security scan
   - `security_triage` - AI-powered triage
   - `security_fix` - Generate fix suggestions
2. **Resources** (queryable data):
   - `security://findings` - List all findings
   - `security://findings/{id}` - Get specific finding
   - `security://status` - Overall security posture
   - `security://config` - Scanner configuration

**Key Pattern:** **Service-Oriented Architecture** + **Resource-Oriented Architecture (REST)**

```
┌─────────────────────────────────────────────────────────────────┐
│                  SECURITY SCANNER MCP SERVER                     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    MCP PROTOCOL LAYER                     │   │
│  │  - JSON-RPC 2.0 over stdio                               │   │
│  │  - Tool invocation (security_scan, triage, fix)          │   │
│  │  - Resource queries (security://findings)                │   │
│  └────────────────┬─────────────────────────────────────────┘   │
│                   │                                              │
│  ┌────────────────▼─────────────────────────────────────────┐   │
│  │                   TOOLS LAYER                             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐               │   │
│  │  │  scan    │  │  triage  │  │   fix    │               │   │
│  │  │  tool    │  │  tool    │  │   tool   │               │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘               │   │
│  └───────┼──────────────┼──────────────┼─────────────────────┘   │
│          │              │              │                         │
│  ┌───────▼──────────────▼──────────────▼─────────────────────┐   │
│  │               RESOURCES LAYER                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │  findings    │  │    status    │  │   config     │   │   │
│  │  │  resource    │  │   resource   │  │  resource    │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                   │                                              │
│  ┌────────────────▼─────────────────────────────────────────┐   │
│  │              SECURITY CORE LIBRARY                        │   │
│  │  (Scanner Orchestrator, Triage Engine, Report Generator)  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                   │
         ┌─────────┼─────────┬─────────────┐
         │         │         │             │
    ┌────▼────┐ ┌──▼───┐ ┌──▼───────┐ ┌───▼──────┐
    │ Claude  │ │ IDE  │ │Dashboard │ │ Custom   │
    │ Agent   │ │Plugin│ │ Web App  │ │ Client   │
    └─────────┘ └──────┘ └──────────┘ └──────────┘
```

---

## Engine Room View: Technical Architecture

### MCP Server Implementation

```python
from mcp.server import Server
from mcp.types import Tool, Resource, TextContent
from typing import Any

class SecurityScannerMCPServer:
    """MCP server exposing security scanning capabilities.

    Reference: https://modelcontextprotocol.io/docs/
    """

    def __init__(self):
        self.server = Server("security-scanner")
        self.orchestrator = ScannerOrchestrator()
        self.triage_engine = TriageEngine()
        self._register_tools()
        self._register_resources()

    def _register_tools(self) -> None:
        """Register security scanning tools."""

        @self.server.tool()
        async def security_scan(
            target: str = ".",
            scanners: list[str] = ["semgrep"],
            fail_on: list[str] = ["critical", "high"]
        ) -> dict[str, Any]:
            """Run security scan on target directory.

            Args:
                target: Directory to scan (default: current directory)
                scanners: List of scanners to run (default: ["semgrep"])
                fail_on: Severity levels that cause failure (default: ["critical", "high"])

            Returns:
                Scan results with findings and metadata.

            Example:
                ```json
                {
                  "name": "security_scan",
                  "arguments": {
                    "target": "src/",
                    "scanners": ["semgrep", "trivy"],
                    "fail_on": ["critical"]
                  }
                }
                ```
            """
            config = ScanConfig(
                target=Path(target),
                scanners=scanners,
                fail_on=fail_on,
            )

            result = self.orchestrator.scan(config)

            return {
                "findings_count": len(result.findings),
                "by_severity": self._count_by_severity(result.findings),
                "findings": [f.to_dict() for f in result.findings],
                "metadata": result.metadata,
            }

        @self.server.tool()
        async def security_triage(
            scan_results: dict[str, Any] | None = None,
            interactive: bool = False
        ) -> dict[str, Any]:
            """AI-powered triage of security findings.

            Args:
                scan_results: Previous scan results (or use latest if None)
                interactive: Enable interactive mode for confirmation

            Returns:
                Triaged findings with classifications and risk scores.

            Example:
                ```json
                {
                  "name": "security_triage",
                  "arguments": {
                    "interactive": false
                  }
                }
                ```
            """
            # Load findings
            if scan_results:
                findings = [Finding.from_dict(f) for f in scan_results["findings"]]
            else:
                findings = self._load_latest_findings()

            # Triage
            if interactive:
                triage_engine = InteractiveTriageEngine()
            else:
                triage_engine = self.triage_engine

            results = triage_engine.triage(findings)

            return {
                "triaged_count": len(results),
                "true_positives": len([r for r in results if r.classification == Classification.TRUE_POSITIVE]),
                "false_positives": len([r for r in results if r.classification == Classification.FALSE_POSITIVE]),
                "needs_investigation": len([r for r in results if r.classification == Classification.NEEDS_INVESTIGATION]),
                "results": [asdict(r) for r in results],
            }

        @self.server.tool()
        async def security_fix(
            finding_ids: list[str] | None = None,
            apply: bool = False
        ) -> dict[str, Any]:
            """Generate fix suggestions for security findings.

            Args:
                finding_ids: Specific findings to fix (or all TP if None)
                apply: Automatically apply patches (default: False)

            Returns:
                Generated fixes with patches and explanations.

            Example:
                ```json
                {
                  "name": "security_fix",
                  "arguments": {
                    "finding_ids": ["SEMGREP-CWE-89-001"],
                    "apply": false
                  }
                }
                ```
            """
            # Load triaged findings
            triage_results = self._load_latest_triage()

            # Filter to True Positives
            if finding_ids:
                findings_to_fix = [r for r in triage_results if r.finding_id in finding_ids]
            else:
                findings_to_fix = [r for r in triage_results if r.classification == Classification.TRUE_POSITIVE]

            # Generate fixes
            fixes = []
            for result in findings_to_fix:
                finding = self._load_finding(result.finding_id)
                fix = self._generate_fix(finding)
                fixes.append(fix)

                if apply:
                    self._apply_patch(fix.patch_file)

            return {
                "fixes_generated": len(fixes),
                "applied": apply,
                "fixes": [asdict(f) for f in fixes],
            }

    def _register_resources(self) -> None:
        """Register security data resources."""

        @self.server.resource("security://findings")
        async def list_findings(
            severity: str | None = None,
            scanner: str | None = None,
            limit: int = 100
        ) -> list[Resource]:
            """List all security findings.

            Query parameters:
            - severity: Filter by severity (critical, high, medium, low)
            - scanner: Filter by scanner (semgrep, codeql, trivy)
            - limit: Maximum findings to return (default: 100)

            Returns:
                List of findings as resources.

            Example:
                ```
                security://findings?severity=critical&scanner=semgrep
                ```
            """
            findings = self._load_all_findings()

            # Filter
            if severity:
                findings = [f for f in findings if f.severity.value == severity]
            if scanner:
                findings = [f for f in findings if f.scanner == scanner]

            # Limit
            findings = findings[:limit]

            return [
                Resource(
                    uri=f"security://findings/{f.id}",
                    name=f.title,
                    mimeType="application/json",
                    text=json.dumps(f.to_dict(), indent=2),
                )
                for f in findings
            ]

        @self.server.resource("security://findings/{id}")
        async def get_finding(id: str) -> Resource:
            """Get specific finding by ID.

            Args:
                id: Finding ID (e.g., "SEMGREP-CWE-89-001")

            Returns:
                Finding details as resource.

            Example:
                ```
                security://findings/SEMGREP-CWE-89-001
                ```
            """
            finding = self._load_finding(id)

            return Resource(
                uri=f"security://findings/{id}",
                name=finding.title,
                mimeType="application/json",
                text=json.dumps(finding.to_dict(), indent=2),
            )

        @self.server.resource("security://status")
        async def get_status() -> Resource:
            """Get overall security posture.

            Returns:
                Security status summary (findings count, posture, trends).

            Example:
                ```
                security://status
                ```
            """
            findings = self._load_all_findings()
            triage_results = self._load_latest_triage()

            status = {
                "total_findings": len(findings),
                "by_severity": self._count_by_severity(findings),
                "true_positives": len([r for r in triage_results if r.classification == Classification.TRUE_POSITIVE]),
                "false_positives": len([r for r in triage_results if r.classification == Classification.FALSE_POSITIVE]),
                "security_posture": self._calculate_posture(findings),
                "last_scan": self._get_last_scan_timestamp(),
            }

            return Resource(
                uri="security://status",
                name="Security Status",
                mimeType="application/json",
                text=json.dumps(status, indent=2),
            )

        @self.server.resource("security://config")
        async def get_config() -> Resource:
            """Get scanner configuration.

            Returns:
                Current scanner configuration and available options.

            Example:
                ```
                security://config
                ```
            """
            config = {
                "available_scanners": ["semgrep", "codeql", "trivy"],
                "default_scanners": ["semgrep"],
                "rulesets": {
                    "semgrep": "auto",  # OWASP + community
                    "codeql": "security-extended",
                },
                "fail_on": ["critical", "high"],
            }

            return Resource(
                uri="security://config",
                name="Scanner Configuration",
                mimeType="application/json",
                text=json.dumps(config, indent=2),
            )

    def run(self) -> None:
        """Start MCP server on stdio."""
        self.server.run()


# Entry point for MCP server
if __name__ == "__main__":
    server = SecurityScannerMCPServer()
    server.run()
```

### MCP Client Example (Claude Agent)

```python
from mcp.client import Client

async def security_analysis_agent():
    """Example: Claude agent using security MCP server."""

    # Connect to MCP server
    async with Client("security-scanner") as client:
        # 1. Scan codebase
        scan_result = await client.call_tool(
            "security_scan",
            arguments={
                "target": "src/",
                "scanners": ["semgrep", "trivy"],
            }
        )

        print(f"Found {scan_result['findings_count']} vulnerabilities")

        # 2. Triage findings
        triage_result = await client.call_tool(
            "security_triage",
            arguments={"scan_results": scan_result}
        )

        true_positives = triage_result["true_positives"]
        print(f"{true_positives} true positives require remediation")

        # 3. Query critical findings
        critical_findings = await client.read_resource(
            "security://findings?severity=critical"
        )

        # 4. Generate fixes
        fix_result = await client.call_tool(
            "security_fix",
            arguments={"apply": False}  # Dry-run
        )

        print(f"Generated {fix_result['fixes_generated']} patches")

        # 5. Check overall status
        status = await client.read_resource("security://status")
        posture = json.loads(status.text)["security_posture"]

        print(f"Security posture: {posture}")
```

### Cross-Repo Dashboard Example

```python
from mcp.client import Client

async def security_dashboard():
    """Aggregate security status across all projects."""

    projects = ["proj-a", "proj-b", "proj-c"]
    dashboard_data = []

    for project in projects:
        # Connect to project's MCP server
        async with Client(f"security-scanner-{project}") as client:
            # Query status
            status = await client.read_resource("security://status")
            project_status = json.loads(status.text)

            dashboard_data.append({
                "project": project,
                "total_findings": project_status["total_findings"],
                "true_positives": project_status["true_positives"],
                "posture": project_status["security_posture"],
                "last_scan": project_status["last_scan"],
            })

    # Render dashboard
    print("\n=== Security Dashboard ===\n")
    for data in dashboard_data:
        print(f"{data['project']:15} | {data['posture']:10} | {data['true_positives']} TP | {data['last_scan']}")
```

---

## Platform Quality Assessment (7 C's)

### 1. Clarity - 9/10

**Strengths:**
- Clear separation: Tools (actions) vs Resources (queries)
- RESTful resource URIs (`security://findings/{id}`)
- Self-documenting tool schemas

**Improvement:**
- Document MCP server discovery (how clients find server)

### 2. Consistency - 10/10

**Strengths:**
- All tools return consistent JSON structure
- Resource URIs follow REST conventions
- Error handling matches MCP specification

### 3. Composability - 10/10

**Strengths:**
- Any MCP client can use security server (Claude, IDE, dashboard)
- Tools can be chained (scan → triage → fix)
- Resources are queryable independently

### 4. Consumption (Developer Experience) - 8/10

**Strengths:**
- MCP protocol abstracts transport (stdio, HTTP, WebSocket)
- JSON-RPC 2.0 (simple, widely supported)
- Self-documenting tools (arguments schema)

**Needs Work:**
- MCP server installation/configuration (add to `.mcp.json`)

### 5. Correctness (Validation) - 9/10

**Strengths:**
- MCP protocol validation (JSON-RPC 2.0 spec)
- Type hints on tool arguments
- Error handling for invalid requests

### 6. Completeness - 8/10

**Covers:**
- Core tools (scan, triage, fix)
- Core resources (findings, status, config)
- Examples (Claude agent, dashboard)

**Missing (Future):**
- Subscriptions (real-time finding updates)
- Batch operations (scan multiple projects)
- Historical queries (findings over time)

### 7. Changeability - 10/10

**Strengths:**
- Add new tools: register new @server.tool() method
- Add new resources: register new @server.resource() method
- Backward compatibility: tools/resources are versioned in URI

---

## Alternatives Considered and Rejected

### Option A: REST API Server

**Approach:** Build HTTP REST API instead of MCP server.

**Pros:**
- Familiar (developers know REST)
- Tooling (Swagger, Postman)
- Language-agnostic (any HTTP client)

**Cons:**
- Requires server deployment (MCP uses stdio, no deployment)
- Authentication/authorization complexity
- Doesn't integrate with Model Context Protocol (no agent composition)

**Hohpe Assessment:** Violates "composability" - doesn't enable agent-to-agent communication

**Rejected:** MCP is designed for agent composition (REST is for traditional services)

---

### Option B: gRPC Server

**Approach:** Build gRPC server for high-performance RPC.

**Pros:**
- High performance (protobuf)
- Bi-directional streaming
- Strong typing (protobuf schema)

**Cons:**
- Requires server deployment
- Protobuf complexity (vs. JSON simplicity)
- No native support for Model Context Protocol

**Hohpe Assessment:** "Premature optimization" - performance not a concern for security scanning

**Rejected:** Overkill for use case, doesn't integrate with MCP ecosystem

---

### Option C: Shared File System

**Approach:** Write scan results to shared JSON files, clients read directly.

**Pros:**
- Simplest implementation
- No server process required

**Cons:**
- No query interface (clients parse JSON manually)
- No access control (any process can read/write)
- No real-time updates (polling required)
- Doesn't scale to cross-repo queries

**Hohpe Assessment:** Violates "service-oriented architecture" - file sharing is anti-pattern

**Rejected:** Insufficient for multi-client scenarios

---

### Option D: MCP Server with Tools + Resources (RECOMMENDED)

**Approach:** Implement MCP server exposing tools and resources.

**Pros:**
- Native Model Context Protocol support (agent composition)
- No deployment required (stdio transport)
- Simple JSON-RPC 2.0 protocol
- Supports multiple clients (Claude, IDE, dashboard)
- Future-proof (MCP is growing ecosystem)

**Cons:**
- Requires MCP-compatible clients
- Less familiar than REST (but simpler)

**Hohpe Assessment:**
- **Composability** ✓ - Enables agent-to-agent communication
- **Consumption** ✓ - Simple protocol, no deployment
- **Consistency** ✓ - Follows MCP specification

**Accepted:** Best fit for agent composition use case

---

## Implementation Guidance

### Phase 1: Core MCP Server (Week 7)

**Scope:** Basic MCP server with scan tool

```bash
src/specify_cli/security/
├── mcp_server.py         # SecurityScannerMCPServer
└── .mcp.json            # MCP server configuration
```

**Configuration:**
```json
{
  "mcpServers": {
    "security-scanner": {
      "command": "python",
      "args": ["-m", "specify_cli.security.mcp_server"],
      "env": {}
    }
  }
}
```

**Tasks:**
- [ ] Implement MCP server skeleton
- [ ] Implement security_scan tool
- [ ] Implement security://findings resource
- [ ] Test with MCP inspector

### Phase 2: Triage and Fix Tools (Week 8)

**Scope:** Add triage and fix tools

**Tasks:**
- [ ] Implement security_triage tool
- [ ] Implement security_fix tool
- [ ] Implement security://status resource
- [ ] Implement security://config resource
- [ ] Integration tests with MCP client

### Phase 3: Client Examples (Week 9)

**Scope:** Demonstrate MCP server usage

**Tasks:**
- [ ] Claude agent example (security analysis workflow)
- [ ] Cross-repo dashboard example
- [ ] IDE plugin proof-of-concept (VS Code)
- [ ] Documentation and tutorials

---

## Risks and Mitigations

### Risk 1: MCP Protocol Adoption

**Likelihood:** Medium
**Impact:** Medium (if MCP doesn't gain traction)

**Mitigation:**
- MCP is backed by Anthropic (Claude) - strong ecosystem support
- Protocol is simple (JSON-RPC 2.0) - easy to implement
- Can add REST API later if needed (MCP server wraps core logic)

### Risk 2: Client Implementation Complexity

**Likelihood:** Low
**Impact:** Medium

**Mitigation:**
- Provide client examples (Python, TypeScript)
- MCP client libraries available for major languages
- Documentation with tutorials

### Risk 3: Performance (stdio Transport)

**Likelihood:** Low
**Impact:** Low

**Mitigation:**
- stdio is sufficient for security scanning (not latency-sensitive)
- MCP supports HTTP transport if needed (future)
- Caching reduces repeated queries

---

## Success Criteria

**Objective Measures:**

1. **MCP Compliance** - Validates against MCP specification
2. **Client Compatibility** - Works with Claude agent, MCP Inspector
3. **Performance** - Tool calls <5 seconds (p95)
4. **Resource Queries** - <1 second (p95)

**Subjective Measures:**

1. **Adoption** - >5 MCP client integrations within 6 months
2. **Developer Feedback** - "MCP server is easy to use" (NPS >40)

---

## Decision

**APPROVED for implementation as Option D: MCP Server with Tools + Resources**

**Timing:** v2.0 feature (after MVP and v1.5)

**Next Steps:**

1. Create implementation task for Phase 1 (Core MCP Server)
2. Test MCP server with MCP Inspector
3. Create client examples

**Review Date:** 2026-Q1 (after v2.0 release)

---

## References

### Protocols Applied

1. **Model Context Protocol (MCP)** - Agent composition protocol
2. **JSON-RPC 2.0** - RPC protocol
3. **REST** - Resource URI conventions

### Related Documents

- **Architecture:** `docs/architecture/flowspec-security-architecture.md`
- **ADR-005:** Scanner Orchestration Pattern
- **ADR-006:** AI Triage Engine Design
- **ADR-007:** Unified Security Finding Format
- **PRD:** `docs/prd/flowspec-security-commands.md`

### External References

- [Model Context Protocol](https://modelcontextprotocol.io/docs/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [MCP Python SDK](https://github.com/anthropics/mcp-python)

---

*This ADR follows Gregor Hohpe's architectural philosophy: strategic framing (why), engine room details (how), quality assessment (verification), and alternatives considered (decision rationale).*
