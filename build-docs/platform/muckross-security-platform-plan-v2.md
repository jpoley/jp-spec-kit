# Muckross Security Platform Plan v2 (CORRECTED)

**Feature**: muckross-security-platform-v2
**Platform Engineer**: @platform-engineer
**Date**: 2025-12-04
**Version**: 2.0 (CRITICAL CORRECTION)

---

## FUNDAMENTAL CONSTRAINT (NON-NEGOTIABLE)

**ZERO API KEYS. ZERO LLM SDK CALLS.**

All AI capabilities MUST be implemented as **skills/prompts** that native AI coding tools (Claude Code, Cursor, Codex) execute directly.

The MCP server exposes DATA and TOOLS that invoke SKILLS - it does NOT call LLM APIs.

This is the single most important architectural constraint. Any implementation that violates this constraint is fundamentally incorrect and must be rejected.

---

## Critical Correction Summary

**Previous plan incorrectly included:**
- LLM API calls in MCP server (`security_triage` tool calling Anthropic API)
- AI triage in CI/CD pipelines (GitHub Actions calling AI services)
- Anthropic SDK in Docker image (`pip install anthropic`)
- API key management and secret handling

**CORRECTED architecture:**
- MCP server = Data exposure + skill invocation instructions (NO API calls)
- CI/CD = Scanner automation only (NO AI in pipeline)
- Docker = CLI + scanners (NO Anthropic SDK, NO API dependencies)
- **ZERO API KEYS anywhere in the system**

---

## 1. Workflow Independence

**The Muckross Security Platform is NOT part of the core JP Spec workflow.**

This security scanning capability is an **optional, standalone feature** that can be used independently of the standard `/flow:specify → /flow:plan → /flow:implement` workflow.

**Key Points:**
- **No workflow state requirements**: Can be run at any time, in any project state
- **No dependency on /flowspec commands**: Works standalone without spec-driven workflow
- **Optional for developers**: Security scanning is a supplementary capability
- **CI/CD independence**: Can run in pipelines without flowspec context
- **Security engineer focused**: Designed for security practitioners, not feature development

**When to use:**
- Pre-commit scanning before any feature work
- CI/CD security gates (independent of feature branches)
- Ad-hoc security audits
- Security engineer triage and remediation
- Compliance scanning

**NOT required for:**
- Standard feature development workflow
- `/flow:implement` task execution
- Product requirement implementation

---

## 2. Architecture Overview

### 2.1 Component Roles

```
┌─────────────────────────────────────────────────────────────┐
│                    NATIVE AI CODING TOOL                     │
│              (Claude Code, Cursor, Codex, etc.)              │
│                                                              │
│  - Executes skills from .claude/skills/                     │
│  - Has access to LLM APIs (user's config)                   │
│  - Reads data from MCP resources                            │
│  - Invokes tools that return skill instructions             │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ MCP Protocol (stdio)
                       │
┌──────────────────────▼───────────────────────────────────────┐
│               SECURITY SCANNER MCP SERVER                    │
│                     (Pure Python)                            │
│                                                              │
│  Resources (Data Exposure):                                 │
│  - security://findings → JSON findings data                 │
│  - security://status → Scan status                          │
│                                                              │
│  Tools (Actions):                                           │
│  - security_scan → Runs Semgrep (Python subprocess)         │
│  - security_triage → Returns skill invocation instruction   │
│  - security_fix → Returns skill invocation instruction      │
│                                                              │
│  NO LLM API CALLS. NO ANTHROPIC SDK.                        │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       │ Python subprocess
                       │
┌──────────────────────▼───────────────────────────────────────┐
│                   SECURITY SCANNERS                          │
│                   (External Tools)                           │
│                                                              │
│  - Semgrep (SAST)                                           │
│  - CodeQL (dataflow analysis, optional)                     │
│  - Playwright (DAST, web security testing)                  │
│  - AFL++ (fuzzing, optional)                                │
│                                                              │
│  Pure automation. No AI.                                    │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 AI Integration Pattern (CORRECTED)

**How AI triage actually works:**

```
1. Developer runs scan (Python subprocess):
   $ specify security scan
   → Semgrep executes
   → Writes findings to docs/security/findings.json

2. Developer asks AI tool to triage:
   $ # In Claude Code
   → AI tool reads security://findings resource (via MCP)
   → AI tool invokes security_triage tool (via MCP)
   → MCP server returns: { "action": "invoke_skill", "skill": "security-triage.md", "input": "findings.json" }
   → AI tool executes skill (using its own LLM access)
   → AI tool writes triage results to docs/security/triage-results.json

3. Developer asks AI tool to generate fixes:
   $ # In Claude Code
   → AI tool reads triage results
   → AI tool invokes security_fix tool (via MCP)
   → MCP server returns: { "action": "invoke_skill", "skill": "security-fix.md", "findings": [...] }
   → AI tool executes skill (generates patches)
   → AI tool applies patches to code
```

**Key insight**: The MCP server is a **router**, not an **executor** of AI operations.

---

## 3. Command Execution Context

**Two types of slash commands exist in Flowspec:**

### 3.1 CLI Commands (Deterministic)

| Aspect | Details |
|--------|---------|
| **Location** | `src/specify_cli/commands/` |
| **Execution** | Python code, no LLM |
| **Purpose** | Automation, CI/CD, scripting |
| **Example** | `specify security scan` |
| **Use in** | GitHub Actions, pre-commit hooks, Docker |

**Characteristics:**
- Runs scanner tools (Semgrep, CodeQL, etc.)
- Pure Python subprocess orchestration
- Deterministic, reproducible results
- No AI/LLM dependencies
- Safe for CI/CD pipelines

### 3.2 Agentic Commands (LLM-Powered)

| Aspect | Details |
|--------|---------|
| **Location** | `.claude/commands/` |
| **Execution** | AI coding tool (Claude Code, Cursor) |
| **Purpose** | Intelligent triage, fix generation |
| **Example** | `/flow:security_triage` |
| **Use in** | Local development with AI tools |

**Characteristics:**
- Executes skills from `.claude/skills/`
- Uses AI coding tool's LLM access
- Context-aware analysis
- Code generation and patching
- **NEVER in CI/CD**

### 3.3 Command Naming Convention

**All security commands use underscores (matching flowspec pattern):**

| Command | Type | Purpose |
|---------|------|---------|
| `specify security scan` | CLI | Run security scanners |
| `/flow:security_scan` | Agentic | Invoke scan with context |
| `/flow:security_triage` | Agentic | AI-powered triage |
| `/flow:security_fix` | Agentic | Generate security fixes |
| `/flow:security_report` | Agentic | Generate security reports |

**Rationale**: Underscores match the `/flow:*` command pattern and are more shell-friendly than hyphens.

### 3.4 CI/CD Pipeline Uses CLI Commands ONLY

**Critical constraint**: CI/CD pipelines MUST use CLI commands, NEVER agentic commands.

**Why:**
- No LLM access in CI/CD runners
- Deterministic, reproducible results required
- No API keys or secrets needed
- Fast execution (no AI inference delay)
- Compliance and audit requirements

**Example:**
```yaml
# GitHub Actions - CORRECT
- name: Run Security Scan
  run: specify security scan --fail-on critical,high

# GitHub Actions - WRONG (would fail)
- name: Run Security Triage
  run: /flow:security_triage  # ERROR: No AI tool in CI/CD
```

---

## 4. Security Memory Integration

**The Muckross Security Platform uses a centralized security knowledge base:**

### 4.1 Memory Directory Structure

```
memory/security/
├── security-facts.md        # Key security facts, thresholds, policies
├── cwe-knowledge.md         # CWE categories and remediation patterns
├── scanner-config.md        # Scanner defaults and customizations
├── triage-guidelines.md     # Classification rules and examples
└── compliance-mapping.md    # OWASP, CWE, NIST mappings
```

### 4.2 How Skills and Commands Use Memory

**Skills import memory files:**
```markdown
# .claude/skills/security-triage.md

@import memory/security/security-facts.md
@import memory/security/triage-guidelines.md
@import memory/security/cwe-knowledge.md

# Security Triage Skill

You are a security expert performing triage...
```

**Commands reference memory:**
```markdown
# .claude/commands/flow-security_triage.md

This command invokes the security-triage skill which references:
- Security facts and thresholds
- CWE vulnerability knowledge
- Triage classification guidelines
```

### 4.3 MCP Server Memory Integration

**The MCP server exposes memory as resources:**

```python
@server.resource("security://knowledge/cwe")
async def get_cwe_knowledge() -> Resource:
    """Expose CWE knowledge base for AI tools."""
    cwe_file = Path("memory/security/cwe-knowledge.md")
    return Resource(
        uri="security://knowledge/cwe",
        name="CWE Knowledge Base",
        mimeType="text/markdown",
        text=cwe_file.read_text(),
    )

@server.resource("security://knowledge/triage-guidelines")
async def get_triage_guidelines() -> Resource:
    """Expose triage guidelines for AI tools."""
    triage_file = Path("memory/security/triage-guidelines.md")
    return Resource(
        uri="security://knowledge/triage-guidelines",
        name="Triage Guidelines",
        mimeType="text/markdown",
        text=triage_file.read_text(),
    )
```

**AI tools can read these resources directly:**
- `security://knowledge/cwe` - CWE vulnerability patterns
- `security://knowledge/triage-guidelines` - Classification rules
- `security://knowledge/security-facts` - Key thresholds and policies
- `security://knowledge/scanner-config` - Scanner configurations
- `security://knowledge/compliance-mapping` - OWASP/NIST mappings

### 4.4 Memory File Maintenance

**Security memory files should contain:**

**security-facts.md**:
- Severity thresholds (critical, high, medium, low)
- False positive rate expectations
- Scanner performance benchmarks
- Known scanner limitations

**cwe-knowledge.md**:
- CWE category descriptions
- Remediation patterns by CWE
- Common exploit scenarios
- Language-specific mitigations

**scanner-config.md**:
- Default scanner configurations
- Custom rule paths
- Exclusion patterns
- Scanner-specific settings

**triage-guidelines.md**:
- Classification criteria (true positive, false positive, needs investigation)
- Risk scoring formulas
- Context analysis examples
- Edge case handling

**compliance-mapping.md**:
- OWASP Top 10 mappings
- CWE to CVE mappings
- NIST controls
- Industry standard references

---

## 5. MCP Server Design (CORRECTED)

### 5.1 MCP Server Implementation

```python
# src/specify_cli/security/mcp_server.py
from mcp.server import Server
from mcp.types import Tool, Resource, TextContent
from pathlib import Path
import json
import subprocess

class SecurityScannerMCPServer:
    """MCP server exposing security scanning capabilities.

    CRITICAL: This server does NOT call LLM APIs.
    It exposes data and returns instructions for AI tools to execute skills.
    """

    def __init__(self):
        self.server = Server("security-scanner")
        self._register_tools()
        self._register_resources()
        self._register_memory_resources()

    def _register_tools(self) -> None:
        """Register security scanning tools."""

        @self.server.tool()
        async def security_scan(
            target: str = ".",
            scanners: list[str] = ["semgrep"],
            fail_on: list[str] = ["critical", "high"]
        ) -> dict[str, Any]:
            """Run security scan on target directory.

            This runs SCANNERS ONLY. No AI processing.
            """
            # Run Semgrep via Python subprocess
            result = subprocess.run(
                ["semgrep", "scan", "--config", "auto", "--json", target],
                capture_output=True,
                text=True
            )

            # Parse findings
            findings = json.loads(result.stdout)

            # Write to findings file
            findings_file = Path("docs/security/findings.json")
            findings_file.parent.mkdir(parents=True, exist_ok=True)
            findings_file.write_text(json.dumps(findings, indent=2))

            return {
                "findings_count": len(findings.get("results", [])),
                "findings_file": str(findings_file),
                "scanner": "semgrep"
            }

        @self.server.tool()
        async def security_triage() -> dict[str, Any]:
            """Returns instruction for AI coding tool to run triage skill.

            DOES NOT CALL LLM API.
            Returns skill invocation instruction for AI tool to execute.

            The skill imports memory files:
            - memory/security/security-facts.md
            - memory/security/triage-guidelines.md
            - memory/security/cwe-knowledge.md
            """
            return {
                "action": "invoke_skill",
                "skill": ".claude/skills/security-triage.md",
                "input_file": "docs/security/findings.json",
                "output_file": "docs/security/triage-results.json",
                "memory_imports": [
                    "memory/security/security-facts.md",
                    "memory/security/triage-guidelines.md",
                    "memory/security/cwe-knowledge.md"
                ],
                "description": "AI coding tool should execute security-triage skill using its own LLM access"
            }

        @self.server.tool()
        async def security_fix(
            finding_ids: list[str] | None = None
        ) -> dict[str, Any]:
            """Returns instruction for AI coding tool to generate fixes.

            DOES NOT CALL LLM API.
            Returns skill invocation instruction for AI tool to execute.

            The skill imports memory files:
            - memory/security/cwe-knowledge.md
            - memory/security/security-facts.md
            """
            # Load triage results to get true positives
            triage_file = Path("docs/security/triage-results.json")
            if triage_file.exists():
                triage_results = json.loads(triage_file.read_text())
                true_positives = [
                    r for r in triage_results
                    if r.get("classification") == "true_positive"
                ]
            else:
                true_positives = []

            return {
                "action": "invoke_skill",
                "skill": ".claude/skills/security-fix.md",
                "findings": true_positives if not finding_ids else [
                    f for f in true_positives if f["id"] in finding_ids
                ],
                "memory_imports": [
                    "memory/security/cwe-knowledge.md",
                    "memory/security/security-facts.md"
                ],
                "description": "AI coding tool should execute security-fix skill to generate patches"
            }

    def _register_resources(self) -> None:
        """Register security data resources."""

        @self.server.resource("security://findings")
        async def list_findings() -> list[Resource]:
            """List all security findings.

            Returns raw JSON data. No AI processing.
            """
            findings_file = Path("docs/security/findings.json")
            if not findings_file.exists():
                return []

            findings = json.loads(findings_file.read_text())

            return [
                Resource(
                    uri="security://findings",
                    name="Security Findings",
                    mimeType="application/json",
                    text=json.dumps(findings, indent=2),
                )
            ]

        @self.server.resource("security://status")
        async def get_status() -> Resource:
            """Get overall security posture.

            Returns computed statistics. No AI processing.
            """
            findings_file = Path("docs/security/findings.json")
            if not findings_file.exists():
                status = {"total_findings": 0}
            else:
                findings = json.loads(findings_file.read_text())
                results = findings.get("results", [])
                status = {
                    "total_findings": len(results),
                    "by_severity": self._count_by_severity(results),
                }

            return Resource(
                uri="security://status",
                name="Security Status",
                mimeType="application/json",
                text=json.dumps(status, indent=2),
            )

    def _register_memory_resources(self) -> None:
        """Register security memory/knowledge resources."""

        @self.server.resource("security://knowledge/cwe")
        async def get_cwe_knowledge() -> Resource:
            """Expose CWE knowledge base."""
            cwe_file = Path("memory/security/cwe-knowledge.md")
            return Resource(
                uri="security://knowledge/cwe",
                name="CWE Knowledge Base",
                mimeType="text/markdown",
                text=cwe_file.read_text() if cwe_file.exists() else "",
            )

        @self.server.resource("security://knowledge/triage-guidelines")
        async def get_triage_guidelines() -> Resource:
            """Expose triage guidelines."""
            triage_file = Path("memory/security/triage-guidelines.md")
            return Resource(
                uri="security://knowledge/triage-guidelines",
                name="Triage Guidelines",
                mimeType="text/markdown",
                text=triage_file.read_text() if triage_file.exists() else "",
            )

        @self.server.resource("security://knowledge/security-facts")
        async def get_security_facts() -> Resource:
            """Expose security facts and thresholds."""
            facts_file = Path("memory/security/security-facts.md")
            return Resource(
                uri="security://knowledge/security-facts",
                name="Security Facts",
                mimeType="text/markdown",
                text=facts_file.read_text() if facts_file.exists() else "",
            )

    def run(self) -> None:
        """Start MCP server on stdio."""
        self.server.run()
```

### 5.2 Skill Templates

Skills are executed by native AI tools, not by the MCP server:

```markdown
# .claude/skills/security-triage.md

@import memory/security/security-facts.md
@import memory/security/triage-guidelines.md
@import memory/security/cwe-knowledge.md

# Security Triage Skill

You are a security expert performing triage on security findings.

## Input

Read the findings from: `docs/security/findings.json`

## Context

Use the imported memory files for:
- Severity thresholds and policies (security-facts.md)
- Classification criteria and examples (triage-guidelines.md)
- CWE vulnerability patterns and remediation (cwe-knowledge.md)

## Task

For each finding:
1. Analyze the code context
2. Determine if it's a true positive, false positive, or needs investigation
3. Assign a risk score (1-10)
4. Provide justification

## Output

Write results to: `docs/security/triage-results.json`

Format:
```json
[
  {
    "finding_id": "SEMGREP-001",
    "classification": "true_positive",
    "risk_score": 9,
    "justification": "SQL injection vulnerability with user input"
  }
]
```

## Example

Given finding:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
```

Classification: true_positive
Justification: Direct string interpolation of user input into SQL query. Classic SQL injection.
```

```markdown
# .claude/skills/security-fix.md

@import memory/security/cwe-knowledge.md
@import memory/security/security-facts.md

# Security Fix Generation Skill

You are a security expert generating code fixes for vulnerabilities.

## Input

Read the triage results from: `docs/security/triage-results.json`

## Context

Use the imported memory files for:
- CWE-specific remediation patterns (cwe-knowledge.md)
- Security best practices and policies (security-facts.md)

## Task

For each true positive finding:
1. Analyze the vulnerable code
2. Generate a secure fix
3. Create a unified diff patch
4. Explain the fix

## Output

Write patches to: `docs/security/patches/{finding-id}.patch`
Write explanations to: `docs/security/fix-explanations.md`

## Example

Finding: SQL injection in user query

Fix:
```python
# Before
query = f"SELECT * FROM users WHERE id = {user_id}"

# After
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

Explanation: Use parameterized queries to prevent SQL injection.
```

---

## 6. CI/CD Pipeline Design (CORRECTED)

### 6.1 What Runs in CI/CD

**CRITICAL: CI/CD pipelines use CLI commands ONLY, never agentic commands.**

**GitHub Actions workflow runs:**
1. `specify security scan` - CLI command (Python runs Semgrep, deterministic)
2. Upload SARIF to GitHub Security tab
3. **NO AI triage** (that happens locally with AI coding tool)
4. **NO LLM API calls** (no AI dependencies in pipeline)
5. **NO API keys or secrets** (pure scanner automation)

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  pull_request:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install tools
        run: |
          pip install uv
          uv tool install flowspec-cli
          pip install semgrep

      - name: Run Security Scan
        run: |
          # CLI command: deterministic, no LLM, safe for CI/CD
          # ONLY run scanner. NO AI triage.
          specify security scan \
            --format sarif \
            --output security-results.sarif \
            --fail-on critical,high

      - name: Upload SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: security-results.sarif

      - name: Upload findings artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: security-findings
          path: docs/security/findings.json
```

**What's included**: CLI scanner commands only (deterministic, reproducible).

**What's missing**: NO AI triage, NO agentic commands, NO API calls, NO secret management.

**Why**:
- AI triage happens locally when developer uses AI coding tool with MCP
- CI/CD requires deterministic, reproducible results
- No LLM access in CI/CD runners
- Compliance and audit requirements prohibit AI in pipeline

### 6.2 Local Workflow with AI Tool

**Developer uses agentic commands (LLM-powered) for triage and fixes:**

```bash
# 1. Developer runs scan (CLI command - deterministic)
$ specify security scan

# 2. Developer asks AI tool to triage (agentic command - LLM-powered)
$ # In Claude Code:
# User: "/flow:security_triage"
# → Claude Code reads security://findings via MCP
# → Claude Code invokes security_triage tool via MCP
# → MCP server returns skill invocation instruction
# → Claude Code executes .claude/skills/security-triage.md
#   (which imports memory/security/*.md files)
# → Claude Code writes docs/security/triage-results.json

# 3. Developer asks AI tool to generate fixes (agentic command - LLM-powered)
$ # In Claude Code:
# User: "/flow:security_fix"
# → Claude Code reads triage results
# → Claude Code invokes security_fix tool via MCP
# → MCP server returns skill invocation instruction
# → Claude Code executes .claude/skills/security-fix.md
#   (which imports memory/security/*.md files)
# → Claude Code writes patches to docs/security/patches/

# 4. Developer reviews and applies patches
$ git apply docs/security/patches/*.patch
$ git commit -m "fix: apply security patches"
```

**Key distinction:**
- **CLI commands** (`specify security scan`): Deterministic, safe for CI/CD
- **Agentic commands** (`/flow:security_triage`): LLM-powered, local development only

---

## 7. Docker Image Design (CORRECTED)

### 7.1 What's Included

```dockerfile
# docker/security-scanner.Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python tools
RUN pip install --no-cache-dir \
    uv \
    semgrep==1.50.0

# Install flowspec-cli
RUN uv tool install flowspec-cli

# NO ANTHROPIC SDK
# NO API KEY HANDLING
# NO AI DEPENDENCIES

WORKDIR /src

ENTRYPOINT ["specify", "security", "scan"]
CMD ["--help"]
```

**What's NOT included**:
- ❌ Anthropic SDK (`anthropic`)
- ❌ OpenAI SDK (`openai`)
- ❌ Any LLM client libraries
- ❌ API key environment variables

**Size**: ~100MB (Python + Semgrep only)

---

## 8. Testing Strategy (CORRECTED)

### 8.1 What to Test

**Python Component Tests (pytest):**
- Scanner execution (Semgrep subprocess)
- Finding normalization (parse Semgrep JSON)
- Report generation (SARIF, Markdown)
- MCP server responses (tool/resource data)

**Skill Tests (manual/fixture-based):**
- Create test fixtures with expected triage outputs
- Manually validate skills produce correct results
- Document skill behavior and edge cases

### 8.2 What NOT to Test

❌ AI inference quality (that's the AI tool's job)
❌ LLM API reliability (no API calls)
❌ Prompt engineering effectiveness (test manually with fixtures)

### 8.3 Test Implementation

```python
# tests/security/test_mcp_server.py
import pytest
from specify_cli.security.mcp_server import SecurityScannerMCPServer

def test_security_scan_tool_returns_scanner_results():
    """Test that security_scan tool runs Semgrep and returns findings."""
    server = SecurityScannerMCPServer()

    # Call tool
    result = await server.security_scan(target="tests/fixtures/vulnerable_code")

    # Verify Python ran Semgrep (no AI involved)
    assert result["scanner"] == "semgrep"
    assert result["findings_count"] > 0
    assert Path(result["findings_file"]).exists()

def test_security_triage_tool_returns_skill_instruction():
    """Test that security_triage tool returns skill invocation instruction."""
    server = SecurityScannerMCPServer()

    # Call tool
    result = await server.security_triage()

    # Verify it returns instruction, NOT triage results
    assert result["action"] == "invoke_skill"
    assert result["skill"] == ".claude/skills/security-triage.md"
    assert "input_file" in result

def test_security_fix_tool_returns_skill_instruction():
    """Test that security_fix tool returns skill invocation instruction."""
    server = SecurityScannerMCPServer()

    # Call tool
    result = await server.security_fix()

    # Verify it returns instruction, NOT patches
    assert result["action"] == "invoke_skill"
    assert result["skill"] == ".claude/skills/security-fix.md"
    assert "findings" in result
```

**Skill fixture tests:**

```json
// tests/fixtures/triage/expected-triage-output.json
[
  {
    "finding_id": "SEMGREP-SQL-INJECTION-001",
    "classification": "true_positive",
    "risk_score": 9,
    "justification": "Direct user input in SQL query without sanitization"
  },
  {
    "finding_id": "SEMGREP-XSS-002",
    "classification": "false_positive",
    "risk_score": 2,
    "justification": "Output is already HTML-escaped by template engine"
  }
]
```

Manual validation: Run skill, compare output to fixture, adjust skill if needed.

---

## 9. Observability Strategy (CORRECTED)

### 9.1 What to Measure

**Python component metrics:**
- Scan duration (time to run Semgrep)
- Findings count by severity
- SARIF upload success rate
- MCP server tool invocation counts

**What NOT to measure:**
- ❌ "AI inference time" (AI tool handles that)
- ❌ "Prompt token usage" (no API calls)
- ❌ "Model accuracy" (test with fixtures)

### 9.2 Metrics Implementation

```python
# src/specify_cli/security/metrics.py
from prometheus_client import Histogram, Counter, Gauge

SCAN_DURATION = Histogram(
    'flowspec_security_scan_duration_seconds',
    'Semgrep scan execution time',
    ['tool', 'scan_type'],
    buckets=[1, 5, 10, 30, 60, 120, 300]
)

FINDINGS_TOTAL = Counter(
    'flowspec_security_findings_total',
    'Total security findings from scanners',
    ['severity', 'cwe_id', 'tool']
)

MCP_TOOL_INVOCATIONS = Counter(
    'flowspec_security_mcp_tool_invocations_total',
    'MCP tool invocation count',
    ['tool_name']
)

# Usage
with SCAN_DURATION.labels(tool='semgrep', scan_type='incremental').time():
    results = run_semgrep_scan()

MCP_TOOL_INVOCATIONS.labels(tool_name='security_triage').inc()
```

---

## 10. Task Implementation Plans (CORRECTED)

### 10.1 Task 224: Design and Implement Security Scanner MCP Server

**Implementation Plan:**

1. **MCP Server Skeleton** (Python subprocess orchestration)
   - Implement `security_scan` tool (runs Semgrep via subprocess) - CLI command
   - Implement `security_triage` tool (returns skill invocation instruction) - Agentic command
   - Implement `security_fix` tool (returns skill invocation instruction) - Agentic command
   - Implement `security://findings` resource (returns JSON data)
   - Implement `security://status` resource (returns computed stats)
   - Implement `security://knowledge/*` resources (expose memory files)

2. **NO LLM API Integration**
   - Do NOT import `anthropic` package
   - Do NOT call any LLM APIs
   - Do NOT handle API keys

3. **Testing**
   - Test Semgrep subprocess execution
   - Test MCP tool returns correct instructions
   - Test MCP resources return correct data
   - Do NOT test AI inference (that's skill tests)

**Acceptance Criteria (CORRECTED):**
- MCP server runs Semgrep (CLI) and returns findings
- MCP tools return skill invocation instructions (agentic) with memory imports
- Memory resources exposed via `security://knowledge/*`
- No Anthropic SDK imported
- No API calls made from MCP server
- All security commands use underscores: `/flow:security_scan`, `/flow:security_triage`, `/flow:security_fix`

### 10.2 Task 258: Implement ADR-008 Security MCP Server Architecture

**Implementation Plan:**

1. **Update ADR-008** to reflect ZERO API KEYS constraint
2. **Document skill-based architecture** (AI tool executes skills)
3. **Remove all references** to LLM API calls in MCP server
4. **Add examples** of skill invocation flow
5. **Document memory integration** (skills import memory/security/*.md)
6. **Clarify CLI vs agentic commands** (deterministic vs LLM-powered)
7. **Document workflow independence** (not part of core flowspec flow)

**Acceptance Criteria (CORRECTED):**
- ADR-008 explicitly states "NO LLM API calls in MCP server"
- Architecture diagrams show skill invocation pattern
- Code examples show subprocess calls, not API calls
- Memory integration documented (skills import security knowledge)
- CLI vs agentic command distinction clearly explained
- Workflow independence section added (optional capability)

### 10.3 Task 248: Setup CI/CD Security Scanning Pipeline

**Implementation Plan:**

1. **Create GitHub Actions workflow** for security scanning
   - Install Semgrep
   - Run `specify security scan` (CLI command - deterministic)
   - Upload SARIF to GitHub Security tab
   - **NO agentic commands in CI/CD** (no `/flow:security_triage`)
   - **NO AI triage in CI/CD** (happens locally with AI tool)

2. **Artifact Storage**
   - Upload findings.json as artifact
   - Developer downloads and uses AI tool locally for triage

**Acceptance Criteria (CORRECTED):**
- CI/CD runs CLI commands only (`specify security scan`)
- No agentic commands in CI/CD (no `/flow:*` commands)
- No AI triage in pipeline
- No API keys or LLM dependencies in CI/CD
- Findings artifact uploaded for local triage with AI tool
- Pipeline documentation clarifies "CLI only, no LLM"

### 10.4 Task 254: Build and Publish Security Scanner Docker Image

**Implementation Plan:**

1. **Create Dockerfile** with:
   - Python 3.11
   - Semgrep
   - flowspec-cli (uv tool install)
   - **NO Anthropic SDK**

2. **Publish to GHCR**
   - Tag as `ghcr.io/jpoley/muckross-security-scanner:v1.0.0`
   - Document usage for air-gapped environments

**Acceptance Criteria (CORRECTED):**
- Docker image contains Semgrep only
- No Anthropic SDK in image
- No API key handling in image
- Image size < 200MB

### 10.5 Task 219: Build Security Commands Test Suite

**Implementation Plan:**

1. **Python Tests** (pytest)
   - Test scanner execution
   - Test finding normalization
   - Test MCP server responses

2. **Skill Fixture Tests** (manual validation)
   - Create test fixtures with expected outputs
   - Document skill behavior

**Acceptance Criteria (CORRECTED):**
- Python tests cover scanner execution
- Skill tests use fixtures for validation
- No tests for AI inference quality

### 10.6 Task 222: Implement Web Security Testing with Playwright DAST

**Implementation Plan:**

1. **Playwright Integration**
   - Add Playwright to scanner orchestrator
   - Run DAST scans (browser-based security testing)
   - Normalize findings to unified format

2. **NO AI Analysis**
   - DAST findings written to JSON
   - AI tool can analyze findings using skills

**Acceptance Criteria (CORRECTED):**
- Playwright DAST scanner executes
- Findings normalized to JSON format
- No AI analysis in scanner

### 10.7 Task 225: Integrate CodeQL for Deep Dataflow Analysis

**Implementation Plan:**

1. **CodeQL Integration** (optional, license check required)
   - Check for GitHub Advanced Security license
   - Download CodeQL CLI if licensed
   - Run CodeQL analysis
   - **Defer to v2.0 if licensing complex**

2. **NO AI Analysis**
   - CodeQL findings written to JSON
   - AI tool can analyze findings using skills

**Acceptance Criteria (CORRECTED):**
- CodeQL license check implemented
- CodeQL executes if licensed
- No AI analysis in scanner
- Deferred to v2.0 if licensing complex

### 10.8 Task 226: Implement Optional AFL++ Fuzzing Support

**Implementation Plan:**

1. **AFL++ Integration** (optional)
   - Add AFL++ to scanner orchestrator
   - Run fuzzing tests
   - Normalize findings to unified format

2. **NO AI Analysis**
   - Fuzzing findings written to JSON
   - AI tool can analyze findings using skills

**Acceptance Criteria (CORRECTED):**
- AFL++ scanner executes (if enabled)
- Findings normalized to JSON format
- No AI analysis in scanner

### 10.9 Task 250: Implement Security Scanning Observability

**Implementation Plan:**

1. **Prometheus Metrics**
   - Scan duration histogram
   - Findings counter by severity
   - MCP tool invocation counter

2. **Structured Logging**
   - Scan lifecycle events
   - Tool execution logs

3. **NO AI Metrics**
   - Do NOT track "AI inference time"
   - Do NOT track "prompt token usage"

**Acceptance Criteria (CORRECTED):**
- Metrics track scanner performance only
- No AI-related metrics
- Structured logs for scanner events

### 10.10 Task 251: Create Pre-commit Hook Configuration for Security Scanning

**Implementation Plan:**

1. **Pre-commit Hook** for fast local scanning
   - Run `specify security scan --fast` (CLI command) on commit
   - **NO agentic commands in pre-commit hook** (too slow, requires LLM)
   - **NO AI triage in pre-commit hook** (happens separately with AI tool)

2. **Documentation**
   - Install instructions
   - Usage examples

**Acceptance Criteria (CORRECTED):**
- Pre-commit hook runs CLI command only (`specify security scan --fast`)
- No agentic commands in pre-commit hook
- No AI triage in pre-commit hook
- Hook completes in < 10 seconds (deterministic scanner execution)

### 10.11 Task 253: Track DORA Metrics for Security Scanning

**Implementation Plan:**

1. **DORA Metrics Collection**
   - Track deployment frequency (unaffected by scans)
   - Track lead time for security fixes
   - Track MTTR for critical vulnerabilities

2. **Monthly Reporting**
   - Generate DORA report for security workflow impact

**Acceptance Criteria (CORRECTED):**
- DORA metrics tracked for scanner workflow
- No metrics for AI triage (happens locally)
- Monthly report generation

---

## 11. Workflow Summary

### 11.1 Development Workflow

```
1. Developer writes code
   ↓
2. Pre-commit hook runs `specify security scan --fast` (CLI - deterministic)
   ↓
3. Developer pushes to branch
   ↓
4. CI/CD runs `specify security scan --incremental` (CLI - deterministic)
   ↓
5. CI/CD uploads SARIF to GitHub Security tab
   ↓
6. Developer downloads findings artifact
   ↓
7. Developer asks AI tool to triage: "/flow:security_triage" (agentic - LLM)
   ↓
8. AI tool reads security://findings via MCP
   ↓
9. AI tool invokes security_triage tool via MCP
   ↓
10. MCP server returns skill invocation instruction with memory imports
    ↓
11. AI tool executes .claude/skills/security-triage.md (imports memory/security/*.md)
    ↓
12. AI tool writes triage results to docs/security/triage-results.json
    ↓
13. Developer asks AI tool to generate fixes: "/flow:security_fix" (agentic - LLM)
    ↓
14. AI tool invokes security_fix tool via MCP
    ↓
15. MCP server returns skill invocation instruction with memory imports
    ↓
16. AI tool executes .claude/skills/security-fix.md (imports memory/security/*.md)
    ↓
17. AI tool generates patches
    ↓
18. Developer reviews and applies patches
    ↓
19. Developer commits fixes
    ↓
20. CI/CD verifies fixes (re-run scan, expect fewer findings)
```

### 11.2 Where AI Happens

**AI happens ONLY in step 11 and 16 (agentic commands):**
- Step 11: AI tool executes security-triage skill with `/flow:security_triage` (LLM-powered)
- Step 16: AI tool executes security-fix skill with `/flow:security_fix` (LLM-powered)

**AI does NOT happen in (CLI commands only):**
- Pre-commit hooks (step 2) - CLI: `specify security scan --fast`
- CI/CD pipelines (step 4-5) - CLI: `specify security scan --incremental`
- MCP server (step 9-10, 14-15) - Returns instructions, doesn't execute AI
- Docker image (scanner execution) - CLI: `specify security scan`

**Command types:**
- **CLI (deterministic)**: `specify security scan` - Safe for automation
- **Agentic (LLM-powered)**: `/flow:security_triage`, `/flow:security_fix` - Local development only

---

## 12. Dependencies and Licensing

### 12.1 What's Included

| Component | License | API Required | Included In |
|-----------|---------|--------------|-------------|
| Python 3.11 | PSF | No | All |
| Semgrep | LGPL 2.1 | No | All |
| CodeQL | GitHub Terms | No (license check) | Optional |
| Playwright | Apache 2.0 | No | Optional |
| AFL++ | Apache 2.0 | No | Optional |
| uv | Apache 2.0 | No | All |
| MCP Python SDK | MIT | No | All |

### 12.2 What's NOT Included

| Component | Reason |
|-----------|--------|
| Anthropic SDK | No LLM API calls |
| OpenAI SDK | No LLM API calls |
| Any LLM client libraries | No LLM API calls |
| API key management | No API keys |

---

## 13. Validation Checklist

Before declaring any implementation complete, verify:

- [ ] No `import anthropic` or `import openai` in Python code
- [ ] No API key handling in environment variables or config
- [ ] No LLM API calls in MCP server code
- [ ] No agentic commands (no `/flow:*`) in CI/CD pipelines
- [ ] CI/CD uses CLI commands only (`specify security scan`)
- [ ] Skills exist in `.claude/skills/` directory with `@import memory/security/*.md`
- [ ] Memory files exist in `memory/security/` directory
- [ ] MCP server exposes `security://knowledge/*` resources
- [ ] MCP tools return skill invocation instructions with `memory_imports`, not AI results
- [ ] Docker image contains NO Anthropic SDK
- [ ] Tests cover scanner execution, not AI inference
- [ ] Documentation explicitly states "ZERO API KEYS"
- [ ] All security commands use underscores: `/flow:security_scan`, `/flow:security_triage`, `/flow:security_fix`, `/flow:security_report`
- [ ] Documentation clarifies CLI vs agentic command distinction
- [ ] Documentation clarifies workflow independence (not part of core flowspec flow)

---

## 14. Migration from Previous Plan

### 14.1 Changes Required

**Code Changes:**
1. Remove `anthropic` from `pyproject.toml` dependencies
2. Remove `TriageEngine` class that called LLM APIs
3. Replace AI API calls with skill invocation instructions
4. Create skill templates in `.claude/skills/` with `@import memory/security/*.md`
5. Create memory files in `memory/security/` directory
6. Update all command names to use underscores (`/flow:security_scan`, etc.)

**CI/CD Changes:**
1. Remove AI triage (agentic commands) from GitHub Actions workflow
2. Use CLI commands only (`specify security scan`)
3. Remove API key secrets from GitHub Actions
4. Upload findings artifact for local triage with AI tool
5. Document "CLI only, no LLM" in pipeline

**Docker Changes:**
1. Remove Anthropic SDK from Dockerfile
2. Remove API key handling from entrypoint

**Documentation Changes:**
1. Update ADR-008 to reflect ZERO API KEYS constraint
2. Document skill-based architecture pattern
3. Add examples of local AI tool workflow
4. Add "Security Memory Integration" section
5. Add "Command Execution Context" section (CLI vs Agentic)
6. Add "Workflow Independence" section
7. Update all command names to use underscores
8. Clarify CI/CD uses CLI only (no LLM in pipeline)

### 14.2 Breaking Changes

**For users who expected AI in CI/CD:**
- AI triage (agentic commands) now happens locally with AI coding tool
- CI/CD only runs CLI commands (scanners - deterministic)
- No `/flow:*` commands in CI/CD
- Developer must use AI tool (Claude Code, etc.) for triage with `/flow:security_triage`

**For users who expected MCP server to call AI APIs:**
- MCP server returns skill invocation instructions (agentic commands)
- Skills import memory files for context (`@import memory/security/*.md`)
- AI tool executes skills using its own LLM access
- No API keys needed in deployment
- Command names changed to use underscores: `/flow:security_scan`, `/flow:security_triage`, etc.

---

## 15. Success Criteria

**Platform is complete when:**

1. ✅ MCP server runs scanners (Semgrep, CodeQL, Playwright, AFL++) via CLI commands
2. ✅ MCP server returns skill invocation instructions with memory imports (agentic commands)
3. ✅ Skills exist in `.claude/skills/` with `@import memory/security/*.md` and are documented
4. ✅ Memory files exist in `memory/security/` directory
5. ✅ MCP server exposes `security://knowledge/*` resources
6. ✅ CI/CD runs CLI commands only (no agentic commands, no AI triage)
7. ✅ Docker image contains scanners only (no Anthropic SDK)
8. ✅ Tests cover scanner execution (not AI inference)
9. ✅ Documentation explicitly states "ZERO API KEYS"
10. ✅ All security commands use underscores: `/flow:security_scan`, `/flow:security_triage`, `/flow:security_fix`, `/flow:security_report`
11. ✅ Documentation clarifies CLI vs agentic command distinction
12. ✅ Documentation clarifies workflow independence (optional capability, not core flowspec flow)
13. ✅ All 11 tasks have updated implementation plans
14. ✅ Validation checklist passes for all components
15. ✅ **ZERO API DEPENDENCIES anywhere in the system**

---

## 16. References

### 16.1 Related Documents

- **ADR-008**: Security MCP Server Architecture (needs update)
- **Platform Plan v1**: `docs/platform/flowspec-security-platform.md` (superseded)
- **Assessment**: `docs/assess/flowspec-security-commands-assessment.md`
- **PRD**: `docs/prd/flowspec-security-commands.md`

### 16.2 External References

- [MCP Protocol Specification](https://modelcontextprotocol.io/docs/)
- [Semgrep Documentation](https://semgrep.dev/docs/)
- [GitHub Code Scanning](https://docs.github.com/en/code-security/code-scanning)

---

**Document Status**: ✅ CORRECTED
**Next Steps**: Update all 11 tasks with corrected implementation plans
**Critical Constraint**: **ZERO API KEYS. ZERO LLM SDK CALLS.**
