# ADR-007: Unified Security Finding Format (UFFormat)

**Status:** Proposed
**Date:** 2025-12-02
**Author:** Enterprise Software Architect
**Context:** /flow:security commands - Common data model for security findings
**Supersedes:** None
**Amended by:** None

---

## Strategic Context (Penthouse View)

### Business Problem

Security scanners output findings in **incompatible formats**:
- Semgrep: Custom JSON schema
- CodeQL: SARIF 2.1.0
- Trivy: JSON with nested structures
- Snyk: Proprietary JSON
- AFL++: Plain text crash reports

**The Core Tension:** Triage, reporting, and workflow integration require **a single canonical schema**, but each scanner has its own format.

**Business Impact:**
- **Tool Fragmentation:** Each scanner requires custom parsing logic
- **Lost Context:** Format conversions lose metadata
- **Integration Brittleness:** Tool updates break parsers
- **Compliance Gap:** Auditors require standardized reports (SARIF)

### Business Value

**Primary Value Streams:**

1. **Interoperability** - Any scanner can feed triage engine, report generator, MCP server
2. **Compliance** - SARIF export for GitHub Code Scanning, audit trails
3. **Maintainability** - Add new scanners without changing downstream logic
4. **Data Portability** - Export findings to JIRA, GitHub Issues, Linear

**Success Metrics:**

- Schema stability: <1 breaking change per year
- Scanner coverage: 100% of core scanners supported
- SARIF compliance: Validates against SARIF 2.1.0 schema
- Lossless conversion: No metadata lost in roundtrip (Scanner → UFFormat → SARIF → UFFormat)

---

## Decision

### Chosen Architecture: Domain-Driven Data Model with SARIF Compatibility

Define **Unified Finding Format (UFFormat)** as:
1. **Core Schema:** Python dataclasses representing security findings
2. **SARIF Alignment:** Field mapping compatible with SARIF 2.1.0 (but simpler)
3. **Extensibility:** Preserve scanner-specific metadata in `raw_data` field
4. **Serialization:** JSON, Markdown, SARIF export

**Key Pattern:** **Canonical Data Model (EIP)** + **Message Translator (EIP)**

```
┌─────────────────────────────────────────────────────────────────┐
│                   UNIFIED FINDING FORMAT (UFFormat)              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Finding                                                   │   │
│  │  - id: str (e.g., "SEMGREP-CWE-89-001")                  │   │
│  │  - scanner: str (e.g., "semgrep")                        │   │
│  │  - severity: "critical" | "high" | "medium" | "low"      │   │
│  │  - title: str (short description)                        │   │
│  │  - description: str (detailed explanation)               │   │
│  │  - cwe_id: str | None (e.g., "CWE-89")                   │   │
│  │  - cvss_score: float | None (0.0-10.0)                   │   │
│  │  - location: Location (file, line, code snippet)         │   │
│  │  - confidence: "high" | "medium" | "low"                 │   │
│  │  - remediation: str | None (fix guidance)                │   │
│  │  - references: list[str] (URLs to docs, CVEs)            │   │
│  │  - raw_data: dict (original scanner output)              │   │
│  │  - metadata: dict (timestamps, tool versions)            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Location                                                  │   │
│  │  - file: Path                                            │   │
│  │  - line_start: int                                       │   │
│  │  - line_end: int                                         │   │
│  │  - column_start: int | None                              │   │
│  │  - column_end: int | None                                │   │
│  │  - code_snippet: str (vulnerable code)                   │   │
│  │  - context_snippet: str | None (surrounding code)        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
    ┌────▼────┐      ┌────▼────┐     ┌────▼────┐
    │ Semgrep │      │ CodeQL  │     │  Trivy  │
    │ Adapter │      │ Adapter │     │ Adapter │
    └─────────┘      └─────────┘     └─────────┘
         │                │                │
         ▼                ▼                ▼
    [Semgrep JSON]  [SARIF 2.1.0]   [Trivy JSON]
```

---

## Engine Room View: Technical Architecture

### Core Data Model

```python
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from typing import Any
from datetime import datetime
import hashlib

class Severity(Enum):
    """Security finding severity levels (aligned with SARIF)."""
    CRITICAL = "critical"  # CVSS 9.0-10.0
    HIGH = "high"          # CVSS 7.0-8.9
    MEDIUM = "medium"      # CVSS 4.0-6.9
    LOW = "low"            # CVSS 0.1-3.9
    INFO = "info"          # CVSS 0.0

class Confidence(Enum):
    """Confidence in finding accuracy."""
    HIGH = "high"          # >90% confident
    MEDIUM = "medium"      # 70-90% confident
    LOW = "low"            # <70% confident

@dataclass
class Location:
    """Location of security finding in source code."""
    file: Path
    line_start: int
    line_end: int
    column_start: int | None = None
    column_end: int | None = None
    code_snippet: str = ""
    context_snippet: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "file": str(self.file),
            "line_start": self.line_start,
            "line_end": self.line_end,
            "column_start": self.column_start,
            "column_end": self.column_end,
            "code_snippet": self.code_snippet,
            "context_snippet": self.context_snippet,
        }

@dataclass
class Finding:
    """Unified security finding format.

    This is the canonical data model for all security findings,
    regardless of source scanner. All downstream processing
    (triage, reporting, MCP) operates on this format.

    Design Principles:
    1. Scanner-agnostic (any tool can map to this)
    2. SARIF-compatible (can export to SARIF 2.1.0)
    3. Extensible (raw_data preserves scanner-specific details)
    4. Fingerprint-based deduplication
    """
    id: str                          # Unique identifier (scanner-specific)
    scanner: str                     # Tool that found it (e.g., "semgrep")
    severity: Severity               # Critical/High/Medium/Low/Info
    title: str                       # Short description
    description: str                 # Detailed explanation
    location: Location               # Where in code
    cwe_id: str | None = None        # CWE identifier (e.g., "CWE-89")
    cvss_score: float | None = None  # CVSS base score (0.0-10.0)
    confidence: Confidence = Confidence.MEDIUM
    remediation: str | None = None   # Fix guidance
    references: list[str] = field(default_factory=list)  # URLs to docs
    raw_data: dict[str, Any] = field(default_factory=dict)  # Original output
    metadata: dict[str, Any] = field(default_factory=dict)  # Timestamps, etc.

    def fingerprint(self) -> str:
        """Generate unique fingerprint for deduplication.

        Fingerprint components:
        - File path (relative to project root)
        - Line range
        - CWE ID (or title if CWE missing)

        Returns:
            SHA256 hash of fingerprint components.
        """
        components = [
            str(self.location.file),
            str(self.location.line_start),
            str(self.location.line_end),
            self.cwe_id or self.title,
        ]
        fingerprint_str = "|".join(components)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]

    def merge(self, other: "Finding") -> None:
        """Merge another finding with same fingerprint.

        When multiple scanners find the same vulnerability,
        merge their findings to increase confidence.

        Rules:
        - Keep highest severity
        - Increase confidence if scanners agree
        - Combine references
        - Preserve both raw_data entries
        """
        if other.fingerprint() != self.fingerprint():
            raise ValueError("Cannot merge findings with different fingerprints")

        # Increase severity if other is higher
        if other.severity.value < self.severity.value:  # Lower enum = higher severity
            self.severity = other.severity

        # Increase confidence (multiple tools agree = higher confidence)
        if self.confidence == Confidence.MEDIUM and other.confidence == Confidence.MEDIUM:
            self.confidence = Confidence.HIGH

        # Combine references (deduplicate)
        self.references = list(set(self.references + other.references))

        # Preserve both scanner outputs
        self.raw_data[f"{other.scanner}_data"] = other.raw_data

        # Update metadata
        self.metadata["merged_scanners"] = self.metadata.get("merged_scanners", [self.scanner]) + [other.scanner]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary (for JSON export)."""
        return {
            "id": self.id,
            "scanner": self.scanner,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "cwe_id": self.cwe_id,
            "cvss_score": self.cvss_score,
            "location": self.location.to_dict(),
            "confidence": self.confidence.value,
            "remediation": self.remediation,
            "references": self.references,
            "metadata": self.metadata,
            # Omit raw_data from standard export (too verbose)
        }

    def to_sarif(self) -> dict[str, Any]:
        """Convert to SARIF 2.1.0 result object.

        SARIF is the industry standard for static analysis results.
        GitHub Code Scanning, Azure DevOps, GitLab all consume SARIF.

        Returns:
            SARIF result object (partial, full SARIF requires run context).
        """
        return {
            "ruleId": self.cwe_id or self.id,
            "level": self._severity_to_sarif_level(),
            "message": {
                "text": self.description,
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": str(self.location.file),
                        },
                        "region": {
                            "startLine": self.location.line_start,
                            "endLine": self.location.line_end,
                            "startColumn": self.location.column_start,
                            "endColumn": self.location.column_end,
                            "snippet": {
                                "text": self.location.code_snippet,
                            },
                        },
                    }
                }
            ],
            "properties": {
                "scanner": self.scanner,
                "cvss": self.cvss_score,
                "confidence": self.confidence.value,
                "remediation": self.remediation,
                "references": self.references,
            },
        }

    def _severity_to_sarif_level(self) -> str:
        """Map UFFormat severity to SARIF level."""
        mapping = {
            Severity.CRITICAL: "error",
            Severity.HIGH: "error",
            Severity.MEDIUM: "warning",
            Severity.LOW: "note",
            Severity.INFO: "note",
        }
        return mapping[self.severity]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Finding":
        """Deserialize from dictionary."""
        location_data = data.pop("location")
        location = Location(
            file=Path(location_data["file"]),
            line_start=location_data["line_start"],
            line_end=location_data["line_end"],
            column_start=location_data.get("column_start"),
            column_end=location_data.get("column_end"),
            code_snippet=location_data.get("code_snippet", ""),
            context_snippet=location_data.get("context_snippet"),
        )

        return cls(
            id=data["id"],
            scanner=data["scanner"],
            severity=Severity(data["severity"]),
            title=data["title"],
            description=data["description"],
            location=location,
            cwe_id=data.get("cwe_id"),
            cvss_score=data.get("cvss_score"),
            confidence=Confidence(data.get("confidence", "medium")),
            remediation=data.get("remediation"),
            references=data.get("references", []),
            metadata=data.get("metadata", {}),
        )
```

### SARIF Export

```python
from typing import Literal

@dataclass
class SARIFExporter:
    """Export findings to SARIF 2.1.0 format.

    SARIF (Static Analysis Results Interchange Format) is the
    industry standard for sharing security scan results.

    Reference: https://docs.oasis-open.org/sarif/sarif/v2.1.0/
    """

    tool_name: str = "flowspec-security"
    tool_version: str = "1.0.0"

    def export(self, findings: list[Finding]) -> dict[str, Any]:
        """Export findings to SARIF document.

        Args:
            findings: List of findings in UFFormat.

        Returns:
            SARIF 2.1.0 document (JSON-serializable dict).
        """
        # Group findings by scanner (SARIF has one run per tool)
        by_scanner = defaultdict(list)
        for finding in findings:
            by_scanner[finding.scanner].append(finding)

        runs = []
        for scanner, scanner_findings in by_scanner.items():
            run = self._create_run(scanner, scanner_findings)
            runs.append(run)

        return {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": runs,
        }

    def _create_run(self, scanner: str, findings: list[Finding]) -> dict[str, Any]:
        """Create SARIF run object for one scanner."""
        # Extract unique rules (CWE IDs)
        rules = {}
        for finding in findings:
            rule_id = finding.cwe_id or finding.id
            if rule_id not in rules:
                rules[rule_id] = {
                    "id": rule_id,
                    "name": finding.title,
                    "shortDescription": {
                        "text": finding.title,
                    },
                    "fullDescription": {
                        "text": finding.description,
                    },
                    "help": {
                        "text": finding.remediation or "No remediation guidance available.",
                    },
                    "properties": {
                        "cwe": finding.cwe_id,
                        "cvss": finding.cvss_score,
                    },
                }

        return {
            "tool": {
                "driver": {
                    "name": scanner,
                    "informationUri": f"https://flowspec-cli.dev/security/{scanner}",
                    "rules": list(rules.values()),
                }
            },
            "results": [f.to_sarif() for f in findings],
        }
```

### Markdown Export

```python
class MarkdownExporter:
    """Export findings to Markdown report."""

    def export(self, findings: list[Finding]) -> str:
        """Generate Markdown report from findings."""
        lines = [
            "# Security Scan Results",
            "",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Findings:** {len(findings)}",
            "",
        ]

        # Summary by severity
        by_severity = defaultdict(list)
        for finding in findings:
            by_severity[finding.severity].append(finding)

        lines.append("## Summary")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("|----------|-------|")
        for severity in Severity:
            count = len(by_severity[severity])
            if count > 0:
                emoji = self._severity_emoji(severity)
                lines.append(f"| {emoji} {severity.value.title()} | {count} |")
        lines.append("")

        # Findings by severity
        for severity in Severity:
            findings_at_severity = by_severity[severity]
            if not findings_at_severity:
                continue

            lines.append(f"## {severity.value.title()} Severity Findings")
            lines.append("")

            for i, finding in enumerate(findings_at_severity, 1):
                lines.append(f"### {i}. {finding.title}")
                lines.append("")
                lines.append(f"**Location:** `{finding.location.file}:{finding.location.line_start}`")
                lines.append(f"**CWE:** {finding.cwe_id or 'N/A'}")
                lines.append(f"**Scanner:** {finding.scanner}")
                lines.append(f"**Confidence:** {finding.confidence.value}")
                lines.append("")
                lines.append(finding.description)
                lines.append("")

                if finding.location.code_snippet:
                    lines.append("**Vulnerable Code:**")
                    lines.append("```")
                    lines.append(finding.location.code_snippet)
                    lines.append("```")
                    lines.append("")

                if finding.remediation:
                    lines.append("**Remediation:**")
                    lines.append(finding.remediation)
                    lines.append("")

                if finding.references:
                    lines.append("**References:**")
                    for ref in finding.references:
                        lines.append(f"- {ref}")
                    lines.append("")

        return "\n".join(lines)

    def _severity_emoji(self, severity: Severity) -> str:
        """Get emoji for severity level."""
        mapping = {
            Severity.CRITICAL: "🔴",
            Severity.HIGH: "🟠",
            Severity.MEDIUM: "🟡",
            Severity.LOW: "🔵",
            Severity.INFO: "⚪",
        }
        return mapping[severity]
```

---

## Platform Quality Assessment (7 C's)

### 1. Clarity - 10/10

**Strengths:**
- Clear schema with well-defined fields
- Enums for severity and confidence (no magic strings)
- Self-documenting code with docstrings

### 2. Consistency - 10/10

**Strengths:**
- All scanners map to same schema (no special cases)
- SARIF export follows official specification
- Severity levels align with CVSS ranges

### 3. Composability - 10/10

**Strengths:**
- Scanners don't need to know about each other (adapter pattern)
- Findings can be merged (deduplication)
- Export to any format (JSON, Markdown, SARIF)

### 4. Consumption (Developer Experience) - 9/10

**Strengths:**
- Simple dataclasses (no ORM complexity)
- JSON serialization built-in
- Clear field names (no abbreviations)

**Improvement:**
- Add schema documentation (JSON Schema or OpenAPI)

### 5. Correctness (Validation) - 9/10

**Strengths:**
- Type hints enforce schema
- Enums prevent invalid values
- Fingerprinting prevents duplicate counts

**Improvement:**
- Add schema validation (pydantic or dataclasses-json)

### 6. Completeness - 9/10

**Covers:**
- All SARIF required fields
- Scanner-specific metadata (raw_data)
- Export to multiple formats

**Missing:**
- Fix suggestions (separate from remediation)
- Historical tracking (when first detected, last seen)

### 7. Changeability - 10/10

**Strengths:**
- Add new fields: extend dataclass (backward compatible if optional)
- Add new export format: implement new exporter class
- Change severity levels: update enum (centralized)

---

## Alternatives Considered and Rejected

### Option A: Use SARIF Directly as Internal Format

**Approach:** Adopt SARIF 2.1.0 as the internal data model (no UFFormat).

**Pros:**
- Industry standard (no translation needed)
- Rich schema (handles complex scenarios)
- Native GitHub Code Scanning support

**Cons:**
- Overly complex (100+ fields, nested structures)
- Verbose JSON (hard to read and debug)
- Designed for interchange, not internal use
- Poor Python ergonomics (nested dicts, not dataclasses)

**Hohpe Assessment:** "Tool-driven design" - let external standard dictate internal model

**Rejected:** Complexity outweighs benefits; use SARIF as export format only

---

### Option B: Scanner-Specific Schemas

**Approach:** Keep each scanner's native format internally, translate only for display.

**Pros:**
- No information loss (preserve original)
- Simple adapters (passthrough)

**Cons:**
- Every downstream component needs scanner-specific logic
- Deduplication impossible (different schemas)
- Triage engine needs N classifiers (one per format)

**Hohpe Assessment:** Violates "Canonical Data Model" pattern

**Rejected:** Breaks composability

---

### Option C: Minimal Schema (ID, Severity, File, Line)

**Approach:** Ultra-simple schema with only essential fields.

**Pros:**
- Easiest to implement
- Fast serialization
- Small JSON files

**Cons:**
- Loses important metadata (CWE, CVSS, remediation)
- Can't export to SARIF (missing required fields)
- Limits triage accuracy (no code context)

**Hohpe Assessment:** "Premature optimization" - sacrifices functionality for simplicity

**Rejected:** Insufficient information for AI triage and compliance

---

### Option D: Domain-Driven Schema with SARIF Compatibility (RECOMMENDED)

**Approach:** Python dataclasses optimized for internal use, export to SARIF.

**Pros:**
- Clean Python API (dataclasses with type hints)
- SARIF-compatible (all required fields present)
- Extensible (raw_data preserves scanner-specific details)
- Human-readable (Markdown export for developers)
- Fingerprinting enables deduplication

**Cons:**
- Requires translation layer (adapters)
- Schema maintenance (but centralized)

**Hohpe Assessment:**
- **Canonical Data Model** ✓ - Single source of truth
- **Message Translator** ✓ - Adapters handle conversions
- **Composability** ✓ - Any scanner, any export format

**Accepted:** Best balance of simplicity and functionality

---

## Implementation Guidance

### Phase 1: Core Schema (Week 1)

**Scope:** Define dataclasses and serialization

```bash
src/specify_cli/security/
├── models.py              # Finding, Location, enums
├── exporters/
│   ├── __init__.py
│   ├── json.py           # JSON export
│   ├── markdown.py       # Markdown export
│   └── sarif.py          # SARIF 2.1.0 export
```

**Tasks:**
- [ ] Define Finding and Location dataclasses
- [ ] Implement fingerprinting
- [ ] Implement finding merging
- [ ] JSON serialization (to_dict/from_dict)

### Phase 2: Export Formats (Week 1)

**Scope:** SARIF and Markdown exporters

**Tasks:**
- [ ] Implement SARIFExporter
- [ ] Implement MarkdownExporter
- [ ] Validate SARIF against official schema
- [ ] Unit tests for all export formats

### Phase 3: Validation and Schema Evolution (Week 2)

**Scope:** Schema validation and versioning

**Tasks:**
- [ ] Add pydantic validation (optional)
- [ ] Generate JSON Schema documentation
- [ ] Add schema version field (for future evolution)
- [ ] Migration guide for schema changes

---

## Schema Evolution Strategy

### Versioning

- Schema version in metadata: `{"schema_version": "1.0.0"}`
- Semantic versioning:
  - **Major:** Breaking changes (field removal, type change)
  - **Minor:** Backward-compatible additions (new optional field)
  - **Patch:** Documentation or validation changes

### Backward Compatibility

**Guaranteed:**
- Adding optional fields is backward compatible
- Changing field documentation is backward compatible

**Breaking:**
- Removing fields
- Changing field types
- Making optional fields required

**Migration Path:**
- Provide converter functions for major version upgrades
- Deprecate fields before removal (1 major version grace period)

---

## Success Criteria

**Objective Measures:**

1. **Schema Stability** - <1 breaking change per year
2. **Scanner Coverage** - 100% of planned scanners supported (Semgrep, CodeQL, Trivy)
3. **SARIF Compliance** - Validates against SARIF 2.1.0 JSON schema
4. **Lossless Roundtrip** - Scanner → UFFormat → SARIF → UFFormat (no data loss)

**Subjective Measures:**

1. **Developer Feedback** - "Schema is easy to work with" (in code reviews)
2. **Maintainability** - New scanner adapters take <4 hours to implement

---

## Decision

**APPROVED for implementation as Option D: Domain-Driven Schema with SARIF Compatibility**

**Next Steps:**

1. Create implementation task for Phase 1 (Core Schema)
2. Validate SARIF export with GitHub Code Scanning
3. Document schema with examples

**Review Date:** 2025-12-10 (after Phase 2 complete)

---

## References

### Standards Applied

1. **SARIF 2.1.0** - Static Analysis Results Interchange Format
2. **CWE** - Common Weakness Enumeration
3. **CVSS 3.1** - Common Vulnerability Scoring System

### Related Documents

- **Architecture:** `docs/architecture/flowspec-security-architecture.md`
- **ADR-005:** Scanner Orchestration Pattern
- **ADR-006:** AI Triage Engine Design
- **PRD:** `docs/prd/flowspec-security-commands.md`

### External References

- [SARIF Specification](https://docs.oasis-open.org/sarif/sarif/v2.1.0/)
- [GitHub Code Scanning](https://docs.github.com/en/code-security/code-scanning)
- [CWE Database](https://cwe.mitre.org/)
- [CVSS Calculator](https://www.first.org/cvss/calculator/3.1)

---

*This ADR follows Gregor Hohpe's architectural philosophy: strategic framing (why), engine room details (how), quality assessment (verification), and alternatives considered (decision rationale).*
