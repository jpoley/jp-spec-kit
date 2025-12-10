# ADR-005: Scanner Orchestration Pattern

**Status:** Proposed
**Date:** 2025-12-02
**Author:** Enterprise Software Architect
**Context:** /jpspec:security commands - Tool integration architecture
**Supersedes:** None
**Amended by:** None

---

## Strategic Context (Penthouse View)

### Business Problem

Security scanning tools (Semgrep, CodeQL, Trivy, Snyk, AFL++) are **disparate command-line executables** with different:
- Installation methods (pip, npm, binary download, container)
- Configuration formats (YAML, TOML, CLI flags)
- Output formats (JSON, XML, SARIF, plain text)
- Performance characteristics (seconds to hours)
- Licensing models (open source, commercial, freemium)

**The Core Tension:** Developers want **one button** to scan their code, but underlying tools require manual installation, configuration, and result interpretation.

### Business Value

**Primary Value Streams:**

1. **Developer Productivity** - Single command (`/jpspec:security scan`) replaces manual tool orchestration
2. **Consistency** - Normalized findings format enables unified triage and reporting
3. **Flexibility** - Add new scanners without changing user-facing commands
4. **Compliance** - Track tool versions for SLSA attestation

**Success Metrics:**

- Tool installation success rate >95% (first-run experience)
- Scan initiation time <30 seconds (tool discovery + launch)
- Developer satisfaction: "Security scanning is easy" (NPS >40)

---

## Decision

### Chosen Architecture: Pluggable Scanner Orchestrator with Adapters

Implement a **Scanner Orchestrator** that:
1. Discovers available scanners (system, venv, download-on-demand)
2. Executes scanners in parallel (when safe)
3. Normalizes results to Unified Finding Format (UFFormat)
4. Aggregates and deduplicates findings
5. Provides progress reporting and cancellation

**Key Pattern:** **Adapter Pattern (GoF)** + **Service Activator Pattern (EIP)**

```
┌─────────────────────────────────────────────────────────────────┐
│                   SCANNER ORCHESTRATOR                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────┐         │
│  │ 1. Tool Discovery (PATH → venv → download)        │         │
│  │ 2. Parallel Execution (when no conflicts)         │         │
│  │ 3. Result Collection and Normalization            │         │
│  │ 4. Deduplication and Aggregation                  │         │
│  │ 5. Progress Reporting                             │         │
│  └────────────────────────────────────────────────────┘         │
│                          │                                       │
│              ┌───────────┼───────────┬───────────┐              │
│              │           │           │           │              │
│         ┌────▼────┐ ┌────▼────┐ ┌────▼────┐ ┌───▼────┐         │
│         │Semgrep  │ │ CodeQL  │ │  Trivy  │ │ Custom │         │
│         │Adapter  │ │ Adapter │ │ Adapter │ │ Adapter│         │
│         └────┬────┘ └────┬────┘ └────┬────┘ └───┬────┘         │
│              │           │           │           │              │
└──────────────┼───────────┼───────────┼───────────┼──────────────┘
               │           │           │           │
         ┌─────▼─────┐┌────▼─────┐┌───▼──────┐┌───▼──────┐
         │ semgrep   ││codeql    ││  trivy   ││.semgrep/ │
         │ (binary)  ││(binary)  ││ (binary) ││ rules/   │
         └───────────┘└──────────┘└──────────┘└──────────┘
```

---

## Engine Room View: Technical Architecture

### Component Design

#### 1. ScannerOrchestrator (Core Component)

**Responsibilities:**
- Coordinate execution of multiple scanners
- Manage scanner lifecycle (detect, install, execute, cleanup)
- Aggregate and deduplicate findings
- Provide unified progress reporting

**Interface:**
```python
from pathlib import Path
from typing import Protocol
from dataclasses import dataclass

@dataclass
class ScanConfig:
    """Configuration for security scan."""
    target: Path                    # Directory to scan
    scanners: list[str]             # e.g., ["semgrep", "codeql"]
    rulesets: dict[str, str]        # Scanner-specific rulesets
    exclude_paths: list[str]        # Paths to ignore
    fail_on: list[str]              # Severities that cause non-zero exit
    output_format: str              # "json" | "markdown" | "sarif"
    incremental: bool               # Only scan changed files
    max_workers: int                # Parallel scanner limit

class ScannerOrchestrator:
    """Orchestrates multiple security scanners."""

    def __init__(self, config: ScanConfig):
        self.config = config
        self.adapters: dict[str, ScannerAdapter] = {}
        self._register_adapters()

    def scan(self) -> ScanResult:
        """Execute all configured scanners and aggregate results.

        Returns:
            ScanResult with aggregated findings and metadata.

        Raises:
            ScannerNotFoundError: If required scanner not available.
            ScanError: If scan execution fails.
        """
        findings = []
        metadata = {}

        # Discover and validate scanners
        for scanner in self.config.scanners:
            adapter = self.adapters.get(scanner)
            if not adapter:
                raise ScannerNotFoundError(f"No adapter for {scanner}")

            if not adapter.is_available():
                self._install_scanner(adapter)

        # Execute scanners (parallel when safe)
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {
                executor.submit(adapter.scan, self.config): scanner
                for scanner, adapter in self.adapters.items()
                if scanner in self.config.scanners
            }

            for future in as_completed(futures):
                scanner = futures[future]
                try:
                    result = future.result()
                    findings.extend(result.findings)
                    metadata[scanner] = result.metadata
                except Exception as e:
                    logger.error(f"{scanner} scan failed: {e}")
                    metadata[scanner] = {"error": str(e)}

        # Deduplicate findings
        findings = self._deduplicate(findings)

        return ScanResult(
            findings=findings,
            metadata=metadata,
            scan_config=self.config
        )

    def _deduplicate(self, findings: list[Finding]) -> list[Finding]:
        """Remove duplicate findings using fingerprinting.

        Fingerprint: hash(file, line_start, line_end, cwe_id)
        """
        by_fingerprint = {}
        for finding in findings:
            fp = finding.fingerprint()
            if fp in by_fingerprint:
                # Merge: increase confidence if multiple tools agree
                by_fingerprint[fp].merge(finding)
            else:
                by_fingerprint[fp] = finding

        return list(by_fingerprint.values())
```

#### 2. ScannerAdapter (Interface)

**Pattern:** Adapter Pattern (translates tool-specific API to common interface)

```python
from abc import ABC, abstractmethod

class ScannerAdapter(ABC):
    """Abstract base class for security scanner integrations."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if scanner is installed and accessible.

        Returns:
            True if scanner can be executed, False otherwise.
        """
        pass

    @abstractmethod
    def install(self) -> None:
        """Install scanner if not available.

        Raises:
            InstallationError: If installation fails.
        """
        pass

    @abstractmethod
    def scan(self, config: ScanConfig) -> ScanResult:
        """Execute scanner and return normalized results.

        Args:
            config: Scan configuration.

        Returns:
            ScanResult with findings in Unified Finding Format.

        Raises:
            ScanError: If scan execution fails.
        """
        pass

    @abstractmethod
    def get_version(self) -> str:
        """Get scanner version for SLSA attestation.

        Returns:
            Version string (e.g., "1.45.0").
        """
        pass
```

#### 3. SemgrepAdapter (Reference Implementation)

```python
import json
import subprocess
from pathlib import Path

class SemgrepAdapter(ScannerAdapter):
    """Adapter for Semgrep SAST scanner."""

    TOOL_NAME = "semgrep"
    DEFAULT_RULESET = "auto"  # OWASP + community rules

    def is_available(self) -> bool:
        """Check if semgrep is in PATH or venv."""
        return shutil.which(self.TOOL_NAME) is not None

    def install(self) -> None:
        """Install semgrep via pip."""
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "semgrep"
        ])

    def scan(self, config: ScanConfig) -> ScanResult:
        """Execute Semgrep and normalize results."""
        ruleset = config.rulesets.get(self.TOOL_NAME, self.DEFAULT_RULESET)

        cmd = [
            self.TOOL_NAME,
            "--config", ruleset,
            "--json",
            "--quiet",  # Suppress progress (we handle it)
        ]

        # Add exclude paths
        for exclude in config.exclude_paths:
            cmd.extend(["--exclude", exclude])

        # Add target
        cmd.append(str(config.target))

        # Execute
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode not in (0, 1):  # 1 = findings, 0 = clean
            raise ScanError(f"Semgrep failed: {result.stderr}")

        # Parse JSON output
        semgrep_output = json.loads(result.stdout)

        # Translate to Unified Finding Format
        findings = [
            self._to_finding(f) for f in semgrep_output.get("results", [])
        ]

        metadata = {
            "version": self.get_version(),
            "ruleset": ruleset,
            "scan_time": semgrep_output.get("time", 0),
            "files_scanned": len(semgrep_output.get("paths", {}).get("scanned", [])),
        }

        return ScanResult(findings=findings, metadata=metadata)

    def _to_finding(self, semgrep_finding: dict) -> Finding:
        """Convert Semgrep result to Unified Finding Format."""
        return Finding(
            id=f"SEMGREP-{semgrep_finding['check_id']}",
            scanner="semgrep",
            severity=self._map_severity(semgrep_finding.get("extra", {}).get("severity")),
            title=semgrep_finding["check_id"],
            description=semgrep_finding["extra"]["message"],
            cwe_id=self._extract_cwe(semgrep_finding),
            location=Location(
                file=Path(semgrep_finding["path"]),
                line_start=semgrep_finding["start"]["line"],
                line_end=semgrep_finding["end"]["line"],
                code_snippet=semgrep_finding["extra"]["lines"],
            ),
            cvss_score=None,  # Semgrep doesn't provide CVSS
            confidence="high",
            raw_data=semgrep_finding,  # Preserve original for debugging
        )

    def _map_severity(self, semgrep_severity: str) -> str:
        """Map Semgrep severity to UFFormat severity."""
        mapping = {
            "ERROR": "critical",
            "WARNING": "high",
            "INFO": "medium",
        }
        return mapping.get(semgrep_severity, "low")

    def _extract_cwe(self, finding: dict) -> str | None:
        """Extract CWE ID from Semgrep metadata."""
        metadata = finding.get("extra", {}).get("metadata", {})
        cwe = metadata.get("cwe")
        if isinstance(cwe, list) and cwe:
            return cwe[0]  # Take first CWE if multiple
        return cwe

    def get_version(self) -> str:
        """Get Semgrep version."""
        result = subprocess.run(
            [self.TOOL_NAME, "--version"],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
```

### Tool Discovery Strategy

**Chain of Responsibility Pattern:**

```python
def discover_scanner(tool_name: str) -> Path | None:
    """Discover scanner using fallback chain.

    1. Check system PATH
    2. Check project venv
    3. Check ~/.specify/tools/ cache
    4. Return None (caller can offer download)

    Returns:
        Path to executable or None if not found.
    """
    # 1. System PATH
    system_path = shutil.which(tool_name)
    if system_path:
        return Path(system_path)

    # 2. Project venv
    venv_path = Path.cwd() / ".venv" / "bin" / tool_name
    if venv_path.exists():
        return venv_path

    # 3. Specify cache
    cache_path = Path.home() / ".specify" / "tools" / tool_name
    if cache_path.exists():
        return cache_path

    return None
```

### Parallel Execution Strategy

**Concurrency Model:**

```python
def can_run_parallel(scanner_a: str, scanner_b: str) -> bool:
    """Check if two scanners can run in parallel safely.

    Some scanners conflict:
    - CodeQL modifies .codeql/ directory (serial only)
    - Semgrep + Trivy are safe (read-only)
    """
    # CodeQL must run alone (writes to .codeql/)
    if "codeql" in (scanner_a, scanner_b):
        return False

    # All others are safe (read-only scans)
    return True

def schedule_scans(scanners: list[str]) -> list[list[str]]:
    """Schedule scanners into parallel batches.

    Returns:
        List of batches, each batch can run in parallel.

    Example:
        >>> schedule_scans(["semgrep", "trivy", "codeql"])
        [["semgrep", "trivy"], ["codeql"]]
    """
    # Separate conflicting scanners
    exclusive = [s for s in scanners if "codeql" in s]
    parallel_safe = [s for s in scanners if s not in exclusive]

    batches = []
    if parallel_safe:
        batches.append(parallel_safe)
    for scanner in exclusive:
        batches.append([scanner])  # Each exclusive scanner in own batch

    return batches
```

---

## Platform Quality Assessment (7 C's)

### 1. Clarity - 9/10

**Strengths:**
- Clear separation: Orchestrator coordinates, Adapters translate
- Each adapter owns one tool (single responsibility)
- Unified Finding Format provides common vocabulary

**Improvement:**
- Document adapter contract with examples

### 2. Consistency - 10/10

**Strengths:**
- All adapters implement same interface (ScannerAdapter)
- Tool discovery follows same pattern for all scanners
- Result normalization ensures consistent schema

### 3. Composability - 10/10

**Strengths:**
- Add new scanner = implement ScannerAdapter + register
- Scanners can be mixed and matched arbitrarily
- Deduplication works across any scanner combination

**Example:**
```python
# Adding new scanner
class SnykAdapter(ScannerAdapter):
    # Implement interface methods
    pass

# Register in orchestrator
orchestrator.register_adapter("snyk", SnykAdapter())
```

### 4. Consumption (Developer Experience) - 8/10

**Strengths:**
- Single command runs all scanners: `/jpspec:security scan`
- Progress reporting with ETAs
- Graceful degradation (one scanner fails, others continue)

**Needs Work:**
- First-run tool installation messaging (avoid surprise downloads)
- Clearer error messages when scanner unavailable

### 5. Correctness (Validation) - 9/10

**Strengths:**
- Fingerprint-based deduplication prevents false counts
- Tool version tracking for SLSA compliance
- Timeout prevents hanging scans

**Risks:**
- Fingerprint collisions (mitigated by including file+line+CWE)
- Parallel scans may have race conditions (mitigated by read-only assumption)

### 6. Completeness - 7/10

**Covers:**
- Discovery, installation, execution, normalization
- Parallel execution, progress reporting
- Error handling and retry

**Missing (Future):**
- Incremental scanning (only changed files)
- Scan result caching (avoid re-scanning unchanged code)
- Distributed scanning (scale beyond single machine)

### 7. Changeability - 10/10

**Strengths:**
- New scanners: implement adapter, no core changes
- New output formats: add translator, no scanner changes
- Change discovery logic: modify discovery chain, adapters unaffected

---

## Alternatives Considered and Rejected

### Option A: Shell Script Orchestra

**Approach:** Write bash script that runs each tool and concatenates outputs.

**Pros:**
- Simple to implement
- No Python dependencies

**Cons:**
- No parallelization
- No normalization (raw tool outputs)
- Hard to test
- No progress reporting
- Platform-specific (Windows issues)

**Hohpe Assessment:** "Scripts grow into monsters" - violates architectural discipline

**Rejected:** Lacks composability and testability

---

### Option B: Single Unified Scanner

**Approach:** Pick one tool (e.g., Semgrep) and use only that.

**Pros:**
- Simplest implementation
- No orchestration complexity
- Single configuration format

**Cons:**
- Tool lock-in (what if Semgrep changes licensing?)
- Missing tool-specific strengths (CodeQL for dataflow, Trivy for containers)
- Can't leverage multiple tools for defense-in-depth

**Hohpe Assessment:** Violates "Composability" - not future-proof

**Rejected:** Insufficient coverage and flexibility

---

### Option C: Container-Based Orchestration (Raptor's Approach)

**Approach:** Package all tools in 6GB Docker container, use DevContainer.

**Pros:**
- Guaranteed tool availability
- Consistent environment
- No installation complexity

**Cons:**
- 6GB download on first run
- Requires Docker (not available in all CI environments)
- Requires `--privileged` for some scans
- High resource overhead (container startup time)

**Hohpe Assessment:** "Premature optimization" - over-engineered for MVP

**Rejected:** Violates lightweight CLI philosophy, poor developer experience

---

### Option D: Plugin-Based Architecture (RECOMMENDED)

**Approach:** Adapter pattern with registry for scanner plugins.

**Pros:**
- Clean separation of concerns
- Scanners are pluggable (add/remove without core changes)
- Testable (mock adapters)
- Lightweight (install tools on-demand)
- Works offline (if tools pre-installed)

**Cons:**
- More complex than Option B (single scanner)
- Requires adapter implementation per tool

**Hohpe Assessment:**
- **Composability** ✓ - Adapters compose freely
- **Consistency** ✓ - Unified Finding Format
- **Changeability** ✓ - Add scanners without breaking core

**Accepted:** Best balance of flexibility and simplicity

---

## Implementation Guidance

### Phase 1: Foundation (Week 1)

**Scope:** Core orchestrator + Semgrep adapter

```bash
src/specify_cli/security/
├── __init__.py
├── orchestrator.py        # ScannerOrchestrator
├── adapters/
│   ├── __init__.py
│   ├── base.py           # ScannerAdapter interface
│   └── semgrep.py        # SemgrepAdapter
├── models.py             # Finding, ScanConfig, ScanResult
└── discovery.py          # Tool discovery chain
```

**Tasks:**
- [ ] Define ScannerAdapter interface
- [ ] Implement ScannerOrchestrator
- [ ] Implement SemgrepAdapter
- [ ] Implement tool discovery chain
- [ ] Unit tests with mocked Semgrep output

### Phase 2: Multi-Tool Support (Week 2)

**Scope:** Add CodeQL and Trivy adapters

```bash
src/specify_cli/security/adapters/
├── codeql.py             # CodeQLAdapter
└── trivy.py              # TrivyAdapter
```

**Tasks:**
- [ ] Implement CodeQLAdapter
- [ ] Implement TrivyAdapter
- [ ] Implement parallel scheduling
- [ ] Implement deduplication logic
- [ ] Integration tests with real tools

### Phase 3: Polish (Week 3)

**Scope:** Progress reporting, error handling, caching

**Tasks:**
- [ ] Implement progress reporter (tqdm or rich)
- [ ] Implement scan result caching
- [ ] Implement incremental scanning
- [ ] Error recovery and retry logic
- [ ] Documentation and examples

---

## Risks and Mitigations

### Risk 1: Tool Installation Failures

**Likelihood:** Medium
**Impact:** High (blocks scanning)

**Mitigation:**
- Fallback to system tools if download fails
- Clear error messages with manual installation instructions
- Retry logic with exponential backoff
- Offline mode (require pre-installed tools)

### Risk 2: Fingerprint Collisions

**Likelihood:** Low
**Impact:** Medium (duplicate findings missed)

**Mitigation:**
- Include file path, line numbers, CWE ID in fingerprint
- Use SHA256 hash (collision probability negligible)
- Log deduplication decisions for audit

### Risk 3: Parallel Execution Race Conditions

**Likelihood:** Low
**Impact:** Medium (scan results corrupted)

**Mitigation:**
- Assume scanners are read-only (validate in adapter docs)
- Serialize conflicting scanners (CodeQL writes to .codeql/)
- File locking if scanner modifies shared state

### Risk 4: Performance Regression on Large Codebases

**Likelihood:** Medium
**Impact:** Medium (poor UX)

**Mitigation:**
- Incremental scanning (only changed files)
- Parallel execution where safe
- Progress indicators with ETA
- Cancellation support (Ctrl+C)

---

## Success Criteria

**Objective Measures:**

1. **Tool Discovery Success Rate** - >95% (tools installed successfully on first run)
2. **Scan Initiation Time** - <30 seconds (from command to first progress update)
3. **Deduplication Accuracy** - >99% (no false duplicates or missed duplicates)
4. **Performance** - 10K LOC in <1 minute, 100K LOC in <5 minutes

**Subjective Measures:**

1. **Developer Feedback** - "Security scanning just works" (NPS >40)
2. **Reduced Tool Fragmentation** - Teams stop using separate Semgrep/CodeQL scripts

---

## Decision

**APPROVED for implementation as Option D: Plugin-Based Architecture**

**Next Steps:**

1. Create implementation task for Phase 1 (Semgrep adapter)
2. Design Unified Finding Format (see ADR-007)
3. Begin development in `src/specify_cli/security/`

**Review Date:** 2025-12-15 (after Phase 1 complete)

---

## References

### Design Patterns Applied

1. **Adapter Pattern (GoF)** - ScannerAdapter translates tool APIs to common interface
2. **Service Activator Pattern (EIP)** - Launch external scanners as services
3. **Chain of Responsibility (GoF)** - Tool discovery fallback chain
4. **Registry Pattern** - Adapter registration and lookup

### Related Documents

- **Architecture:** `docs/architecture/jpspec-security-architecture.md`
- **ADR-007:** Unified Security Finding Format
- **PRD:** `docs/prd/jpspec-security-commands.md`

### External References

- [Semgrep Documentation](https://semgrep.dev/docs/)
- [CodeQL CLI](https://github.com/github/codeql-cli-binaries)
- [Trivy Security Scanner](https://trivy.dev/)
- [Enterprise Integration Patterns](https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessageTranslator.html)

---

*This ADR follows Gregor Hohpe's architectural philosophy: strategic framing (why), engine room details (how), quality assessment (verification), and alternatives considered (decision rationale).*
