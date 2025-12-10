"""Tests for Unified Finding Format (UFFormat) models and exporters.

This test module validates:
    1. Location and Finding dataclass creation
    2. Fingerprinting for deduplication
    3. Finding merging when multiple scanners find the same issue
    4. JSON serialization roundtrip
    5. SARIF export format validity
    6. Markdown export formatting

See ADR-007 for design rationale.
"""

import json
from pathlib import Path

import pytest

from specify_cli.security.exporters import (
    JSONExporter,
    MarkdownExporter,
    SARIFExporter,
)
from specify_cli.security.models import Confidence, Finding, Location, Severity


class TestLocation:
    """Test Location dataclass functionality."""

    def test_location_creation(self) -> None:
        """Test basic location creation with required fields."""
        location = Location(
            file=Path("src/app.py"),
            line_start=42,
            line_end=45,
        )

        assert location.file == Path("src/app.py")
        assert location.line_start == 42
        assert location.line_end == 45
        assert location.column_start is None
        assert location.column_end is None
        assert location.code_snippet == ""
        assert location.context_snippet is None

    def test_location_with_all_fields(self) -> None:
        """Test location with all optional fields populated."""
        location = Location(
            file=Path("src/app.py"),
            line_start=42,
            line_end=45,
            column_start=10,
            column_end=25,
            code_snippet='user_input = request.get("id")',
            context_snippet="def get_user():\n    user_input = request.get('id')\n    query = ...",
        )

        assert location.column_start == 10
        assert location.column_end == 25
        assert 'user_input = request.get("id")' in location.code_snippet
        assert location.context_snippet is not None

    def test_location_serialization(self) -> None:
        """Test Location to_dict and from_dict roundtrip."""
        location = Location(
            file=Path("src/app.py"),
            line_start=42,
            line_end=45,
            column_start=10,
            column_end=25,
            code_snippet="vulnerable_code()",
        )

        # Serialize
        data = location.to_dict()

        # Verify structure
        assert data["file"] == "src/app.py"
        assert data["line_start"] == 42
        assert data["line_end"] == 45
        assert data["column_start"] == 10
        assert data["column_end"] == 25
        assert data["code_snippet"] == "vulnerable_code()"

        # Deserialize
        restored = Location.from_dict(data)

        assert restored.file == location.file
        assert restored.line_start == location.line_start
        assert restored.line_end == location.line_end
        assert restored.column_start == location.column_start
        assert restored.code_snippet == location.code_snippet


class TestFinding:
    """Test Finding dataclass functionality."""

    def test_finding_creation(self) -> None:
        """Test basic finding creation with required fields."""
        location = Location(
            file=Path("src/app.py"),
            line_start=42,
            line_end=45,
        )

        finding = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="User input is passed directly to SQL query without sanitization",
            location=location,
        )

        assert finding.id == "SEMGREP-001"
        assert finding.scanner == "semgrep"
        assert finding.severity == Severity.HIGH
        assert finding.title == "SQL Injection"
        assert finding.confidence == Confidence.MEDIUM  # default
        assert finding.cwe_id is None
        assert finding.cvss_score is None
        assert finding.references == []
        assert finding.raw_data == {}
        assert finding.metadata == {}

    def test_finding_with_all_fields(self) -> None:
        """Test finding with all optional fields populated."""
        location = Location(
            file=Path("src/app.py"),
            line_start=42,
            line_end=45,
        )

        finding = Finding(
            id="SEMGREP-CWE-89-001",
            scanner="semgrep",
            severity=Severity.CRITICAL,
            title="SQL Injection",
            description="SQL injection vulnerability detected",
            location=location,
            cwe_id="CWE-89",
            cvss_score=9.8,
            confidence=Confidence.HIGH,
            remediation="Use parameterized queries instead of string concatenation",
            references=[
                "https://cwe.mitre.org/data/definitions/89.html",
                "https://owasp.org/www-community/attacks/SQL_Injection",
            ],
            raw_data={"semgrep_rule": "python.lang.security.audit.sql-injection"},
            metadata={"scan_time": "2025-12-02T10:00:00Z"},
        )

        assert finding.cwe_id == "CWE-89"
        assert finding.cvss_score == 9.8
        assert finding.confidence == Confidence.HIGH
        assert finding.remediation is not None
        assert len(finding.references) == 2
        assert "semgrep_rule" in finding.raw_data

    def test_finding_fingerprint_consistency(self) -> None:
        """Test that fingerprinting produces consistent results."""
        location = Location(
            file=Path("src/app.py"),
            line_start=42,
            line_end=45,
        )

        finding1 = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="SQL injection vulnerability",
            location=location,
            cwe_id="CWE-89",
        )

        finding2 = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="SQL injection vulnerability",
            location=location,
            cwe_id="CWE-89",
        )

        # Same fingerprint for identical findings
        assert finding1.fingerprint() == finding2.fingerprint()

    def test_finding_fingerprint_uniqueness(self) -> None:
        """Test that different findings have different fingerprints."""
        location1 = Location(file=Path("src/app.py"), line_start=42, line_end=45)
        location2 = Location(file=Path("src/app.py"), line_start=50, line_end=52)

        finding1 = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Vulnerability",
            location=location1,
            cwe_id="CWE-89",
        )

        finding2 = Finding(
            id="SEMGREP-002",
            scanner="semgrep",
            severity=Severity.MEDIUM,
            title="XSS",
            description="Vulnerability",
            location=location2,
            cwe_id="CWE-79",
        )

        # Different fingerprints for different findings
        assert finding1.fingerprint() != finding2.fingerprint()

    def test_finding_fingerprint_uses_cwe_or_title(self) -> None:
        """Test that fingerprint uses CWE if available, otherwise title."""
        location = Location(file=Path("src/app.py"), line_start=42, line_end=45)

        # With CWE
        finding_with_cwe = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Vulnerability",
            location=location,
            cwe_id="CWE-89",
        )

        # Without CWE (uses title)
        finding_without_cwe = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Vulnerability",
            location=location,
        )

        # Different fingerprints because CWE vs title
        assert finding_with_cwe.fingerprint() != finding_without_cwe.fingerprint()

    def test_finding_merge_same_fingerprint(self) -> None:
        """Test merging two findings with the same fingerprint."""
        location = Location(file=Path("src/app.py"), line_start=42, line_end=45)

        # Finding from Semgrep
        semgrep_finding = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="SQL injection vulnerability",
            location=location,
            cwe_id="CWE-89",
            confidence=Confidence.MEDIUM,
            references=["https://semgrep.dev/r/sql-injection"],
        )

        # Finding from CodeQL (same vulnerability)
        codeql_finding = Finding(
            id="CODEQL-002",
            scanner="codeql",
            severity=Severity.CRITICAL,
            title="SQL Injection",
            description="SQL injection vulnerability",
            location=location,
            cwe_id="CWE-89",
            confidence=Confidence.MEDIUM,
            references=["https://codeql.github.com/sql-injection"],
        )

        # Merge CodeQL finding into Semgrep finding
        semgrep_finding.merge(codeql_finding)

        # Should keep higher severity (CRITICAL > HIGH)
        assert semgrep_finding.severity == Severity.CRITICAL

        # Should increase confidence (both were MEDIUM, merged = HIGH)
        assert semgrep_finding.confidence == Confidence.HIGH

        # Should combine references
        assert len(semgrep_finding.references) == 2
        assert "https://semgrep.dev/r/sql-injection" in semgrep_finding.references
        assert "https://codeql.github.com/sql-injection" in semgrep_finding.references

        # Should preserve both scanner outputs
        assert "codeql_data" in semgrep_finding.raw_data

        # Should track merged scanners
        assert "merged_scanners" in semgrep_finding.metadata
        assert "semgrep" in semgrep_finding.metadata["merged_scanners"]
        assert "codeql" in semgrep_finding.metadata["merged_scanners"]

    def test_finding_merge_different_fingerprints_raises_error(self) -> None:
        """Test that merging findings with different fingerprints raises ValueError."""
        location1 = Location(file=Path("src/app.py"), line_start=42, line_end=45)
        location2 = Location(file=Path("src/app.py"), line_start=50, line_end=52)

        finding1 = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Vulnerability",
            location=location1,
        )

        finding2 = Finding(
            id="SEMGREP-002",
            scanner="semgrep",
            severity=Severity.MEDIUM,
            title="XSS",
            description="Vulnerability",
            location=location2,
        )

        with pytest.raises(
            ValueError, match="Cannot merge findings with different fingerprints"
        ):
            finding1.merge(finding2)

    def test_finding_json_serialization(self) -> None:
        """Test Finding to_dict and from_dict roundtrip."""
        location = Location(
            file=Path("src/app.py"),
            line_start=42,
            line_end=45,
            code_snippet="query = 'SELECT * FROM users WHERE id=' + user_id",
        )

        finding = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="SQL injection vulnerability detected",
            location=location,
            cwe_id="CWE-89",
            cvss_score=8.5,
            confidence=Confidence.HIGH,
            remediation="Use parameterized queries",
            references=["https://cwe.mitre.org/data/definitions/89.html"],
            metadata={"scan_time": "2025-12-02T10:00:00Z"},
        )

        # Serialize
        data = finding.to_dict()

        # Verify structure
        assert data["id"] == "SEMGREP-001"
        assert data["scanner"] == "semgrep"
        assert data["severity"] == "high"
        assert data["cwe_id"] == "CWE-89"
        assert data["cvss_score"] == 8.5
        assert data["confidence"] == "high"
        assert "location" in data

        # Should be JSON-serializable
        json_str = json.dumps(data)
        assert json_str is not None

        # Deserialize
        restored = Finding.from_dict(data)

        assert restored.id == finding.id
        assert restored.scanner == finding.scanner
        assert restored.severity == finding.severity
        assert restored.title == finding.title
        assert restored.cwe_id == finding.cwe_id
        assert restored.cvss_score == finding.cvss_score
        assert restored.confidence == finding.confidence
        assert restored.location.file == finding.location.file
        assert restored.location.line_start == finding.location.line_start

    def test_finding_to_sarif(self) -> None:
        """Test SARIF conversion for a single finding."""
        location = Location(
            file=Path("src/app.py"),
            line_start=42,
            line_end=45,
            column_start=10,
            column_end=25,
            code_snippet="query = 'SELECT * FROM users WHERE id=' + user_id",
        )

        finding = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.CRITICAL,
            title="SQL Injection",
            description="SQL injection vulnerability detected",
            location=location,
            cwe_id="CWE-89",
            cvss_score=9.8,
            confidence=Confidence.HIGH,
            remediation="Use parameterized queries",
            references=["https://cwe.mitre.org/data/definitions/89.html"],
        )

        sarif_result = finding.to_sarif()

        # Verify SARIF structure
        assert sarif_result["ruleId"] == "CWE-89"
        assert sarif_result["level"] == "error"  # CRITICAL maps to error
        assert sarif_result["message"]["text"] == "SQL injection vulnerability detected"

        # Verify location
        assert len(sarif_result["locations"]) == 1
        physical_location = sarif_result["locations"][0]["physicalLocation"]
        assert physical_location["artifactLocation"]["uri"] == "src/app.py"
        assert physical_location["region"]["startLine"] == 42
        assert physical_location["region"]["endLine"] == 45
        assert physical_location["region"]["startColumn"] == 10
        assert "query = 'SELECT" in physical_location["region"]["snippet"]["text"]

        # Verify properties
        props = sarif_result["properties"]
        assert props["scanner"] == "semgrep"
        assert props["cvss"] == 9.8
        assert props["confidence"] == "high"

    def test_severity_to_sarif_level_mapping(self) -> None:
        """Test that all severity levels map correctly to SARIF levels."""
        location = Location(file=Path("test.py"), line_start=1, line_end=1)

        # CRITICAL -> error
        critical_finding = Finding(
            id="TEST-001",
            scanner="test",
            severity=Severity.CRITICAL,
            title="Test",
            description="Test",
            location=location,
        )
        assert critical_finding.to_sarif()["level"] == "error"

        # HIGH -> error
        high_finding = Finding(
            id="TEST-002",
            scanner="test",
            severity=Severity.HIGH,
            title="Test",
            description="Test",
            location=location,
        )
        assert high_finding.to_sarif()["level"] == "error"

        # MEDIUM -> warning
        medium_finding = Finding(
            id="TEST-003",
            scanner="test",
            severity=Severity.MEDIUM,
            title="Test",
            description="Test",
            location=location,
        )
        assert medium_finding.to_sarif()["level"] == "warning"

        # LOW -> note
        low_finding = Finding(
            id="TEST-004",
            scanner="test",
            severity=Severity.LOW,
            title="Test",
            description="Test",
            location=location,
        )
        assert low_finding.to_sarif()["level"] == "note"

        # INFO -> note
        info_finding = Finding(
            id="TEST-005",
            scanner="test",
            severity=Severity.INFO,
            title="Test",
            description="Test",
            location=location,
        )
        assert info_finding.to_sarif()["level"] == "note"


class TestJSONExporter:
    """Test JSONExporter functionality."""

    def test_json_export_empty_list(self) -> None:
        """Test exporting empty findings list."""
        exporter = JSONExporter()
        result = exporter.export([])

        data = json.loads(result)
        assert data["findings"] == []

    def test_json_export_single_finding(self) -> None:
        """Test exporting a single finding."""
        location = Location(file=Path("test.py"), line_start=1, line_end=1)
        finding = Finding(
            id="TEST-001",
            scanner="test",
            severity=Severity.HIGH,
            title="Test Vulnerability",
            description="Test description",
            location=location,
        )

        exporter = JSONExporter()
        result = exporter.export([finding])

        data = json.loads(result)
        assert len(data["findings"]) == 1
        assert data["findings"][0]["id"] == "TEST-001"
        assert data["findings"][0]["severity"] == "high"

    def test_json_export_pretty_vs_compact(self) -> None:
        """Test pretty vs compact JSON output."""
        location = Location(file=Path("test.py"), line_start=1, line_end=1)
        finding = Finding(
            id="TEST-001",
            scanner="test",
            severity=Severity.HIGH,
            title="Test",
            description="Test",
            location=location,
        )

        # Pretty format (default)
        pretty_exporter = JSONExporter(pretty=True)
        pretty_result = pretty_exporter.export([finding])
        assert "\n" in pretty_result  # Has newlines

        # Compact format
        compact_exporter = JSONExporter(pretty=False)
        compact_result = compact_exporter.export([finding])
        assert "\n" not in compact_result  # No newlines

    def test_json_export_dict(self) -> None:
        """Test export_dict returns dictionary."""
        location = Location(file=Path("test.py"), line_start=1, line_end=1)
        finding = Finding(
            id="TEST-001",
            scanner="test",
            severity=Severity.HIGH,
            title="Test",
            description="Test",
            location=location,
        )

        exporter = JSONExporter()
        result = exporter.export_dict([finding])

        assert isinstance(result, dict)
        assert "findings" in result
        assert len(result["findings"]) == 1


class TestSARIFExporter:
    """Test SARIFExporter functionality."""

    def test_sarif_export_structure(self) -> None:
        """Test that SARIF export has correct top-level structure."""
        location = Location(file=Path("test.py"), line_start=1, line_end=1)
        finding = Finding(
            id="TEST-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="Test",
            description="Test",
            location=location,
        )

        exporter = SARIFExporter()
        sarif_doc = exporter.export([finding])

        # Verify SARIF 2.1.0 structure
        assert "$schema" in sarif_doc
        assert "sarif-schema-2.1.0.json" in sarif_doc["$schema"]
        assert sarif_doc["version"] == "2.1.0"
        assert "runs" in sarif_doc
        assert len(sarif_doc["runs"]) == 1

    def test_sarif_export_run_structure(self) -> None:
        """Test that SARIF runs have correct structure."""
        location = Location(file=Path("test.py"), line_start=1, line_end=1)
        finding = Finding(
            id="TEST-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="Test Vulnerability",
            description="Test description",
            location=location,
            cwe_id="CWE-89",
        )

        exporter = SARIFExporter(tool_name="test-tool", tool_version="1.2.3")
        sarif_doc = exporter.export([finding])

        run = sarif_doc["runs"][0]

        # Verify tool metadata
        assert "tool" in run
        assert run["tool"]["driver"]["name"] == "semgrep"
        assert run["tool"]["driver"]["version"] == "1.2.3"
        assert "informationUri" in run["tool"]["driver"]

        # Verify rules
        assert "rules" in run["tool"]["driver"]
        assert len(run["tool"]["driver"]["rules"]) == 1
        rule = run["tool"]["driver"]["rules"][0]
        assert rule["id"] == "CWE-89"

        # Verify results
        assert "results" in run
        assert len(run["results"]) == 1

    def test_sarif_export_multiple_scanners(self) -> None:
        """Test that findings from multiple scanners create separate runs."""
        location = Location(file=Path("test.py"), line_start=1, line_end=1)

        semgrep_finding = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="Test",
            description="Test",
            location=location,
        )

        codeql_finding = Finding(
            id="CODEQL-001",
            scanner="codeql",
            severity=Severity.MEDIUM,
            title="Test",
            description="Test",
            location=location,
        )

        exporter = SARIFExporter()
        sarif_doc = exporter.export([semgrep_finding, codeql_finding])

        # Should have 2 runs (one per scanner)
        assert len(sarif_doc["runs"]) == 2

        # Verify scanner names
        scanner_names = {run["tool"]["driver"]["name"] for run in sarif_doc["runs"]}
        assert scanner_names == {"semgrep", "codeql"}

    def test_sarif_export_is_json_serializable(self) -> None:
        """Test that SARIF export can be serialized to JSON."""
        location = Location(file=Path("test.py"), line_start=1, line_end=1)
        finding = Finding(
            id="TEST-001",
            scanner="test",
            severity=Severity.HIGH,
            title="Test",
            description="Test",
            location=location,
        )

        exporter = SARIFExporter()
        sarif_doc = exporter.export([finding])

        # Should be JSON-serializable
        json_str = json.dumps(sarif_doc, indent=2)
        assert json_str is not None

        # Should be deserializable
        parsed = json.loads(json_str)
        assert parsed["version"] == "2.1.0"


class TestMarkdownExporter:
    """Test MarkdownExporter functionality."""

    def test_markdown_export_empty_list(self) -> None:
        """Test exporting empty findings list."""
        exporter = MarkdownExporter()
        result = exporter.export([])

        assert "# Security Scan Results" in result
        assert "**Total Findings:** 0" in result

    def test_markdown_export_structure(self) -> None:
        """Test that Markdown export has expected structure."""
        location = Location(
            file=Path("test.py"),
            line_start=42,
            line_end=45,
            code_snippet="vulnerable_code()",
        )
        finding = Finding(
            id="TEST-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="SQL injection vulnerability detected",
            location=location,
            cwe_id="CWE-89",
            remediation="Use parameterized queries",
            references=["https://cwe.mitre.org/data/definitions/89.html"],
        )

        exporter = MarkdownExporter()
        result = exporter.export([finding])

        # Verify structure
        assert "# Security Scan Results" in result
        assert "## Summary" in result
        assert "## High Severity Findings" in result
        assert "### 1. SQL Injection" in result
        assert "**Location:** `test.py:42`" in result
        assert "**CWE:** CWE-89" in result
        assert "**Scanner:** semgrep" in result
        assert "**Vulnerable Code:**" in result
        assert "vulnerable_code()" in result
        assert "**Remediation:**" in result
        assert "Use parameterized queries" in result
        assert "**References:**" in result
        assert "https://cwe.mitre.org/data/definitions/89.html" in result

    def test_markdown_export_severity_summary(self) -> None:
        """Test that severity summary table is correct."""
        location = Location(file=Path("test.py"), line_start=1, line_end=1)

        findings = [
            Finding(
                id="TEST-001",
                scanner="test",
                severity=Severity.CRITICAL,
                title="Critical Issue",
                description="Test",
                location=location,
            ),
            Finding(
                id="TEST-002",
                scanner="test",
                severity=Severity.CRITICAL,
                title="Another Critical",
                description="Test",
                location=location,
            ),
            Finding(
                id="TEST-003",
                scanner="test",
                severity=Severity.HIGH,
                title="High Issue",
                description="Test",
                location=location,
            ),
            Finding(
                id="TEST-004",
                scanner="test",
                severity=Severity.MEDIUM,
                title="Medium Issue",
                description="Test",
                location=location,
            ),
        ]

        exporter = MarkdownExporter()
        result = exporter.export(findings)

        # Verify summary counts
        assert "**Total Findings:** 4" in result
        assert "🔴 Critical | 2 |" in result
        assert "🟠 High | 1 |" in result
        assert "🟡 Medium | 1 |" in result

    def test_markdown_export_multiple_severities(self) -> None:
        """Test that findings are grouped by severity."""
        location = Location(file=Path("test.py"), line_start=1, line_end=1)

        findings = [
            Finding(
                id="HIGH-001",
                scanner="test",
                severity=Severity.HIGH,
                title="High Issue",
                description="Test",
                location=location,
            ),
            Finding(
                id="LOW-001",
                scanner="test",
                severity=Severity.LOW,
                title="Low Issue",
                description="Test",
                location=location,
            ),
        ]

        exporter = MarkdownExporter()
        result = exporter.export(findings)

        # Verify sections
        assert "## High Severity Findings" in result
        assert "## Low Severity Findings" in result
        assert "### 1. High Issue" in result
        assert "### 1. Low Issue" in result


class TestIntegration:
    """Integration tests for the complete UFFormat system."""

    def test_roundtrip_json_serialization(self) -> None:
        """Test complete roundtrip: Finding → JSON → Finding."""
        location = Location(
            file=Path("src/app.py"),
            line_start=42,
            line_end=45,
            column_start=10,
            column_end=25,
            code_snippet="query = 'SELECT * FROM users WHERE id=' + user_id",
        )

        original = Finding(
            id="SEMGREP-CWE-89-001",
            scanner="semgrep",
            severity=Severity.CRITICAL,
            title="SQL Injection",
            description="SQL injection vulnerability detected",
            location=location,
            cwe_id="CWE-89",
            cvss_score=9.8,
            confidence=Confidence.HIGH,
            remediation="Use parameterized queries",
            references=["https://cwe.mitre.org/data/definitions/89.html"],
            metadata={"scan_time": "2025-12-02T10:00:00Z"},
        )

        # Serialize
        data = original.to_dict()
        json_str = json.dumps(data)

        # Deserialize
        parsed = json.loads(json_str)
        restored = Finding.from_dict(parsed)

        # Verify all fields
        assert restored.id == original.id
        assert restored.scanner == original.scanner
        assert restored.severity == original.severity
        assert restored.title == original.title
        assert restored.description == original.description
        assert restored.cwe_id == original.cwe_id
        assert restored.cvss_score == original.cvss_score
        assert restored.confidence == original.confidence
        assert restored.remediation == original.remediation
        assert restored.references == original.references
        assert restored.metadata == original.metadata
        assert restored.location.file == original.location.file
        assert restored.location.line_start == original.location.line_start

    def test_export_all_formats(self) -> None:
        """Test that a finding can be exported to all formats."""
        location = Location(
            file=Path("test.py"),
            line_start=1,
            line_end=1,
            code_snippet="test()",
        )

        finding = Finding(
            id="TEST-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="Test Vulnerability",
            description="Test description",
            location=location,
            cwe_id="CWE-79",
            remediation="Fix it",
            references=["https://example.com"],
        )

        # JSON export
        json_exporter = JSONExporter()
        json_output = json_exporter.export([finding])
        assert json_output is not None
        assert "TEST-001" in json_output

        # SARIF export
        sarif_exporter = SARIFExporter()
        sarif_output = sarif_exporter.export([finding])
        assert sarif_output is not None
        assert sarif_output["version"] == "2.1.0"

        # Markdown export
        md_exporter = MarkdownExporter()
        md_output = md_exporter.export([finding])
        assert md_output is not None
        assert "# Security Scan Results" in md_output
        assert "Test Vulnerability" in md_output
