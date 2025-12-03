"""Core data models for Unified Finding Format (UFFormat).

This module defines the canonical security finding schema used across all
security scanners in JP Spec Kit. It provides:

1. Scanner-agnostic data model (any tool can map to this)
2. SARIF 2.1.0 compatibility (export to industry standard)
3. Extensibility via raw_data field (preserve scanner-specific metadata)
4. Fingerprint-based deduplication

See ADR-007 for architectural decisions and design rationale.
"""

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(Enum):
    """Security finding severity levels (aligned with SARIF and CVSS ranges).

    Severity levels map to CVSS score ranges:
        - CRITICAL: CVSS 9.0-10.0
        - HIGH: CVSS 7.0-8.9
        - MEDIUM: CVSS 4.0-6.9
        - LOW: CVSS 0.1-3.9
        - INFO: CVSS 0.0 (informational only)
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Confidence(Enum):
    """Confidence in finding accuracy.

    Confidence levels indicate how certain the scanner is that this
    is a true positive:
        - HIGH: >90% confident (manual review may not be needed)
        - MEDIUM: 70-90% confident (review recommended)
        - LOW: <70% confident (likely needs triage)
    """

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Location:
    """Location of security finding in source code.

    This class represents where a security vulnerability was found,
    including file path, line numbers, and code snippets.

    Attributes:
        file: Path to file containing the vulnerability
        line_start: Starting line number (1-indexed)
        line_end: Ending line number (inclusive)
        column_start: Starting column number (optional, 1-indexed)
        column_end: Ending column number (optional, inclusive)
        code_snippet: The vulnerable code itself
        context_snippet: Surrounding code for context (optional)
    """

    file: Path
    line_start: int
    line_end: int
    column_start: int | None = None
    column_end: int | None = None
    code_snippet: str = ""
    context_snippet: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize location to dictionary for JSON export.

        Returns:
            Dictionary representation with all fields.
        """
        return {
            "file": str(self.file),
            "line_start": self.line_start,
            "line_end": self.line_end,
            "column_start": self.column_start,
            "column_end": self.column_end,
            "code_snippet": self.code_snippet,
            "context_snippet": self.context_snippet,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Location":
        """Deserialize location from dictionary.

        Args:
            data: Dictionary with location fields

        Returns:
            Location instance
        """
        return cls(
            file=Path(data["file"]),
            line_start=data["line_start"],
            line_end=data["line_end"],
            column_start=data.get("column_start"),
            column_end=data.get("column_end"),
            code_snippet=data.get("code_snippet", ""),
            context_snippet=data.get("context_snippet"),
        )


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

    Attributes:
        id: Unique identifier from scanner (e.g., "SEMGREP-CWE-89-001")
        scanner: Tool that found it (e.g., "semgrep", "codeql")
        severity: Severity level (critical/high/medium/low/info)
        title: Short description (one-line summary)
        description: Detailed explanation of the vulnerability
        location: Where in the code the issue was found
        cwe_id: CWE identifier if applicable (e.g., "CWE-89")
        cvss_score: CVSS base score if available (0.0-10.0)
        confidence: Confidence in finding accuracy
        remediation: Fix guidance (how to resolve the issue)
        references: URLs to documentation, CVEs, etc.
        raw_data: Original scanner output (preserved for traceability)
        metadata: Additional metadata (timestamps, tool versions, etc.)
    """

    id: str
    scanner: str
    severity: Severity
    title: str
    description: str
    location: Location
    cwe_id: str | None = None
    cvss_score: float | None = None
    confidence: Confidence = Confidence.MEDIUM
    remediation: str | None = None
    references: list[str] = field(default_factory=list)
    raw_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def fingerprint(self) -> str:
        """Generate unique fingerprint for deduplication.

        The fingerprint is used to identify when multiple scanners find
        the same vulnerability. It's based on:
            - File path (relative to project root)
            - Line range (start and end)
            - CWE ID (or title if CWE is not available)

        Returns:
            SHA256 hash (first 16 characters) of fingerprint components.

        Example:
            >>> finding = Finding(
            ...     id="SEMGREP-001",
            ...     scanner="semgrep",
            ...     severity=Severity.HIGH,
            ...     title="SQL Injection",
            ...     description="Vulnerable to SQL injection",
            ...     location=Location(Path("app.py"), 42, 45),
            ...     cwe_id="CWE-89"
            ... )
            >>> finding.fingerprint()
            'a3f2d1e5b4c6a7d9'
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
        """Merge another finding with the same fingerprint.

        When multiple scanners find the same vulnerability, merge their
        findings to increase confidence and combine metadata.

        Merging Rules:
            1. Keep the highest severity level
            2. Increase confidence if both findings have medium confidence
            3. Combine references (deduplicate)
            4. Preserve both scanner outputs in raw_data
            5. Track which scanners were merged in metadata

        Args:
            other: Another finding to merge with this one

        Raises:
            ValueError: If fingerprints don't match (different vulnerabilities)

        Example:
            >>> semgrep_finding = Finding(...)
            >>> codeql_finding = Finding(...)  # Same vulnerability
            >>> semgrep_finding.merge(codeql_finding)
            >>> semgrep_finding.confidence
            Confidence.HIGH  # Increased because both scanners agreed
        """
        if other.fingerprint() != self.fingerprint():
            msg = "Cannot merge findings with different fingerprints"
            raise ValueError(msg)

        # Keep highest severity (lower enum ordinal = higher severity)
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4,
        }
        if severity_order[other.severity] < severity_order[self.severity]:
            self.severity = other.severity

        # Increase confidence (multiple tools agree = higher confidence)
        if (
            self.confidence == Confidence.MEDIUM
            and other.confidence == Confidence.MEDIUM
        ):
            self.confidence = Confidence.HIGH

        # Combine references (deduplicate)
        self.references = list(set(self.references + other.references))

        # Preserve both scanner outputs
        self.raw_data[f"{other.scanner}_data"] = other.raw_data

        # Update metadata to track merged scanners
        merged_scanners = self.metadata.get("merged_scanners", [self.scanner])
        if other.scanner not in merged_scanners:
            merged_scanners.append(other.scanner)
        self.metadata["merged_scanners"] = merged_scanners

    def to_dict(self) -> dict[str, Any]:
        """Serialize finding to dictionary for JSON export.

        Note: raw_data is intentionally omitted from standard export
        to reduce verbosity. It's preserved in the Finding object
        for debugging but not included in reports.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
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
        }

    def to_sarif(self) -> dict[str, Any]:
        """Convert to SARIF 2.1.0 result object.

        SARIF (Static Analysis Results Interchange Format) is the
        industry standard for static analysis results. It's consumed by:
            - GitHub Code Scanning
            - Azure DevOps
            - GitLab Security Dashboard
            - Many other security platforms

        Returns:
            SARIF result object (partial, full SARIF requires run context).

        Note:
            This returns a SARIF "result" object, not a complete SARIF
            document. Use SARIFExporter to create a full SARIF document.

        Reference:
            https://docs.oasis-open.org/sarif/sarif/v2.1.0/
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
        """Map UFFormat severity to SARIF level.

        SARIF has three levels: error, warning, note.
        We map our five severity levels to these three.

        Returns:
            SARIF level string ("error", "warning", or "note").
        """
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
        """Deserialize finding from dictionary.

        Args:
            data: Dictionary with finding fields

        Returns:
            Finding instance

        Example:
            >>> data = {
            ...     "id": "SEMGREP-001",
            ...     "scanner": "semgrep",
            ...     "severity": "high",
            ...     "title": "SQL Injection",
            ...     "description": "Vulnerable to SQL injection",
            ...     "location": {
            ...         "file": "app.py",
            ...         "line_start": 42,
            ...         "line_end": 45
            ...     }
            ... }
            >>> finding = Finding.from_dict(data)
        """
        location_data = data.pop("location")
        location = Location.from_dict(location_data)

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
