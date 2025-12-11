# ADR-009: CodeQL MCP Integration for Deep Security Analysis

**Status:** Proposed
**Date:** 2025-12-03
**Deciders:** @jpoley
**Tags:** security, mcp, codeql, sast

## Context

Flowspec currently integrates two SAST tools via MCP servers:
- **Semgrep** (`@returntocorp/semgrep-mcp`) - Fast pattern-based scanning
- **Trivy** (`@aquasecurity/trivy-mcp`) - Container/IaC security and SBOM

While Semgrep excels at fast, rule-based pattern matching, it lacks the deep **dataflow analysis** capabilities needed to detect complex vulnerabilities like:
- Taint propagation across function boundaries
- Second-order SQL injection
- Indirect object reference vulnerabilities
- Complex authentication bypass chains

**CodeQL** fills this gap with semantic code analysis that understands how data flows through an application.

### Why Not Include in Core CLI?

| Factor | Decision |
|--------|----------|
| **Dependency size** | CodeQL CLI bundle is ~500MB; keep core lean |
| **Installation complexity** | Requires database compilation per-language |
| **Not universally needed** | Many projects don't require deep dataflow analysis |
| **MCP architecture** | Clean separation of concerns; tools don't bloat core |

## Decision

Integrate CodeQL via MCP server using the existing [codeql-mcp](https://github.com/JordyZomer/codeql-mcp) project, following the established pattern for semgrep and trivy.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Flowspec Agents                          │
├─────────────────────────────────────────────────────────────────┤
│  secure-by-design-engineer  │  backend-code-reviewer  │  ...    │
│         ↓                   │           ↓             │         │
│    mcp__codeql__*           │    mcp__codeql__*       │         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     MCP Server Layer                             │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│   semgrep    │    trivy     │   codeql     │    (future)       │
│  (pattern)   │  (container) │  (dataflow)  │                   │
└──────────────┴──────────────┴──────────────┴───────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Scanner Orchestrator                          │
│              src/specify_cli/security/orchestrator.py            │
├─────────────────────────────────────────────────────────────────┤
│  • Tool discovery (PATH → venv → download-on-demand)            │
│  • Parallel execution                                            │
│  • Result normalization to UFFormat                              │
│  • Fingerprint-based deduplication                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Unified Finding Format (UFFormat)              │
│                 src/specify_cli/security/models.py               │
├─────────────────────────────────────────────────────────────────┤
│  Finding { id, scanner, severity, cwe_id, location, ... }       │
│  → SARIF 2.1.0 export for GitHub Security tab                   │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation Plan

### Phase 1: MCP Server Configuration (Effort: 30 min)

#### Task 1.1: Add CodeQL MCP to `.mcp.json`

```json
"codeql": {
  "command": "uvx",
  "args": [
    "--from", "git+https://github.com/JordyZomer/codeql-mcp",
    "mcp", "run", "server.py", "-t", "sse"
  ],
  "env": {},
  "description": "CodeQL deep dataflow analysis for security vulnerabilities"
}
```

**Note:** The codeql-mcp server requires the `codeql` binary in PATH.

#### Task 1.2: Document CodeQL Prerequisites

Add to `docs/guides/security-setup.md`:
- CodeQL CLI installation instructions
- Database creation workflow
- Supported languages (Java, JavaScript, Python, Go, C/C++, C#, Ruby)

---

### Phase 2: Agent Tool Assignments (Effort: 15 min)

Update the following agent definitions in `.agents/`:

#### Task 2.1: secure-by-design-engineer.md
```yaml
tools: Glob, Grep, Read, Write, Edit, mcp__github__*, mcp__serena__*, mcp__trivy__*, mcp__semgrep__*, mcp__codeql__*
```

#### Task 2.2: backend-code-reviewer.md
```yaml
tools: Glob, Grep, Read, Write, Edit, mcp__github__*, mcp__serena__*, mcp__trivy__*, mcp__semgrep__*, mcp__codeql__*
```

#### Task 2.3: quality-guardian.md
```yaml
# Add security tools for comprehensive quality gates
tools: Glob, Grep, Read, Write, Edit, mcp__github__*, mcp__serena__*, mcp__trivy__*, mcp__semgrep__*, mcp__codeql__*, mcp__chrome-devtools__*
```

---

### Phase 3: CodeQL Adapter Implementation (Effort: 2-4 hours)

Create `src/specify_cli/security/adapters/codeql.py`:

#### Task 3.1: Implement CodeQLAdapter class

```python
@dataclass
class CodeQLAdapter(ScannerAdapter):
    """Adapter for CodeQL semantic analysis."""

    name: str = "codeql"

    async def discover(self) -> bool:
        """Check if codeql binary is available."""

    async def scan(
        self,
        target: Path,
        language: str,
        query_pack: str = "security-extended"
    ) -> list[Finding]:
        """Run CodeQL analysis and return normalized findings."""

    def _normalize_finding(self, raw: dict) -> Finding:
        """Convert CodeQL SARIF output to UFFormat."""
```

#### Task 3.2: Database management utilities

```python
class CodeQLDatabaseManager:
    """Manage CodeQL database lifecycle."""

    async def create_database(
        self,
        source_root: Path,
        language: str,
        database_path: Path
    ) -> Path:
        """Create a CodeQL database for analysis."""

    async def get_or_create(self, source_root: Path, language: str) -> Path:
        """Get existing database or create new one."""

    def detect_language(self, source_root: Path) -> str:
        """Auto-detect primary language from source."""
```

#### Task 3.3: Register adapter in orchestrator

Update `src/specify_cli/security/orchestrator.py`:
```python
from .adapters.codeql import CodeQLAdapter

ADAPTERS = [
    SemgrepAdapter(),
    TrivyAdapter(),
    CodeQLAdapter(),  # Add this
]
```

---

### Phase 4: CLI Integration (Effort: 1-2 hours)

#### Task 4.1: Add CodeQL to security scan command

Update `/flow:security scan` to include CodeQL:

```python
@app.command()
def scan(
    target: Path,
    scanners: list[str] = ["semgrep", "trivy", "codeql"],
    codeql_language: str = "auto",
    codeql_queries: str = "security-extended",
):
    """Run security scan with specified scanners."""
```

#### Task 4.2: Add database management commands

```bash
# Create/update CodeQL database
specify security codeql-db create --language python

# List available databases
specify security codeql-db list

# Clean stale databases
specify security codeql-db clean --older-than 7d
```

---

### Phase 5: CI/CD Integration (Effort: 1 hour)

#### Task 5.1: Update GitHub Actions workflow

Add CodeQL job to `.github/workflows/security-scan.yml`:

```yaml
codeql-analysis:
  runs-on: ubuntu-latest
  permissions:
    security-events: write
  steps:
    - uses: github/codeql-action/init@v3
      with:
        languages: ${{ matrix.language }}
        queries: security-extended

    - uses: github/codeql-action/autobuild@v3

    - uses: github/codeql-action/analyze@v3
      with:
        output: results
        upload: always
```

#### Task 5.2: SARIF upload integration

Ensure CodeQL SARIF results are uploaded to GitHub Security tab alongside Semgrep findings.

---

### Phase 6: Documentation (Effort: 1 hour)

#### Task 6.1: Create security setup guide

`docs/guides/security-setup.md`:
- Prerequisites (CodeQL CLI, supported languages)
- MCP server configuration
- Database creation workflow
- Query pack selection

#### Task 6.2: Update agent documentation

Document which agents have CodeQL access and when to use deep analysis vs. pattern matching.

#### Task 6.3: Add troubleshooting section

Common issues:
- CodeQL binary not found
- Database creation failures
- Memory/timeout issues for large codebases

---

## Agent Assignment Summary

| Agent | semgrep | trivy | codeql | Rationale |
|-------|---------|-------|--------|-----------|
| **secure-by-design-engineer** | ✅ | ✅ | ✅ | Primary security analysis agent |
| **backend-code-reviewer** | ✅ | ✅ | ✅ | Server-side code needs dataflow analysis |
| **frontend-code-reviewer** | ✅ | ✅ | ⚠️ | Optional - XSS/injection detection |
| **quality-guardian** | ✅ | ✅ | ✅ | Comprehensive quality gates |
| **release-manager** | ❌ | ✅ | ❌ | Only needs SBOM/CVE scanning |
| **platform-engineer** | ❌ | ✅ | ❌ | IaC security via Trivy |
| **sre-agent** | ❌ | ✅ | ❌ | Runtime security focus |

## Consequences

### Positive
- Deep dataflow analysis catches vulnerabilities Semgrep misses
- Consistent MCP-based architecture
- No changes to core CLI dependencies
- Optional for projects that don't need it

### Negative
- Requires users to install CodeQL CLI separately (~500MB)
- Database creation adds time to first scan
- Memory-intensive for large codebases

### Mitigations
- Document installation clearly
- Cache databases between scans
- Provide incremental scan options
- Default to Semgrep-only for small projects

## Alternatives Considered

### 1. Bundle CodeQL in core CLI
**Rejected:** Too heavy (~500MB), not universally needed.

### 2. Create CodeQL "skill" instead of MCP
**Rejected:** Skills are for prompt-based domain expertise, not tool integrations. MCP is the correct abstraction.

### 3. Use only Semgrep with custom rules
**Rejected:** Cannot replicate dataflow analysis with pattern matching alone.

## References

- [codeql-mcp GitHub](https://github.com/JordyZomer/codeql-mcp)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [ADR-005: Scanner Orchestrator](./ADR-005-scanner-orchestrator.md)
- [ADR-007: Unified Finding Format](./ADR-007-unified-finding-format.md)
- [Task-225: CodeQL Integration](../backlog/tasks/task-225.md)
