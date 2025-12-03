"""SARIF 2.1.0 validation tests.

This module validates that exported SARIF documents conform to the
SARIF 2.1.0 specification structure without requiring the full JSON schema.

For production use, consider adding sarif-om package for full validation:
    pip install sarif-om

Reference: https://docs.oasis-open.org/sarif/sarif/v2.1.0/
"""

from pathlib import Path

from specify_cli.security.exporters import SARIFExporter
from specify_cli.security.models import Confidence, Finding, Location, Severity


class TestSARIFValidation:
    """Validate SARIF 2.1.0 structure compliance."""

    def test_sarif_document_has_required_top_level_fields(self) -> None:
        """Test SARIF document has required top-level fields."""
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
        sarif = exporter.export([finding])

        # Required top-level fields per SARIF 2.1.0 spec
        assert "$schema" in sarif
        assert "version" in sarif
        assert "runs" in sarif

        # Version must be "2.1.0"
        assert sarif["version"] == "2.1.0"

        # Schema must reference SARIF 2.1.0
        assert "sarif-schema-2.1.0.json" in sarif["$schema"]

        # Runs must be an array
        assert isinstance(sarif["runs"], list)

    def test_sarif_run_has_required_fields(self) -> None:
        """Test SARIF run has required fields."""
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
        sarif = exporter.export([finding])

        run = sarif["runs"][0]

        # Required run fields per SARIF 2.1.0 spec
        assert "tool" in run
        assert "results" in run

        # Tool must have driver
        assert "driver" in run["tool"]

        # Driver must have name
        assert "name" in run["tool"]["driver"]

    def test_sarif_tool_driver_has_required_fields(self) -> None:
        """Test SARIF tool driver has required fields."""
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
        sarif = exporter.export([finding])

        driver = sarif["runs"][0]["tool"]["driver"]

        # Required driver fields
        assert "name" in driver

        # Optional but recommended fields
        assert "version" in driver
        assert "informationUri" in driver
        assert "rules" in driver

    def test_sarif_result_has_required_fields(self) -> None:
        """Test SARIF result has required fields."""
        location = Location(
            file=Path("test.py"),
            line_start=42,
            line_end=45,
            code_snippet="test()",
        )
        finding = Finding(
            id="TEST-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="Test Vulnerability",
            description="Test description",
            location=location,
            cwe_id="CWE-89",
        )

        exporter = SARIFExporter()
        sarif = exporter.export([finding])

        result = sarif["runs"][0]["results"][0]

        # Required result fields per SARIF 2.1.0 spec
        assert "ruleId" in result
        assert "message" in result

        # Message must have text
        assert "text" in result["message"]

        # Optional but important fields
        assert "level" in result
        assert "locations" in result

    def test_sarif_location_has_required_fields(self) -> None:
        """Test SARIF location has required fields."""
        location = Location(
            file=Path("src/app.py"),
            line_start=42,
            line_end=45,
            column_start=10,
            column_end=25,
            code_snippet="query = 'SELECT * FROM users'",
        )
        finding = Finding(
            id="TEST-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="SQL injection detected",
            location=location,
        )

        exporter = SARIFExporter()
        sarif = exporter.export([finding])

        result_location = sarif["runs"][0]["results"][0]["locations"][0]

        # Must have physicalLocation
        assert "physicalLocation" in result_location

        physical = result_location["physicalLocation"]

        # Required physicalLocation fields
        assert "artifactLocation" in physical
        assert "region" in physical

        # ArtifactLocation must have uri
        assert "uri" in physical["artifactLocation"]

        # Region must have line information
        region = physical["region"]
        assert "startLine" in region
        assert "endLine" in region

    def test_sarif_rule_has_required_fields(self) -> None:
        """Test SARIF rule has required fields."""
        location = Location(file=Path("test.py"), line_start=1, line_end=1)
        finding = Finding(
            id="TEST-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="SQL injection vulnerability",
            location=location,
            cwe_id="CWE-89",
            remediation="Use parameterized queries",
        )

        exporter = SARIFExporter()
        sarif = exporter.export([finding])

        rule = sarif["runs"][0]["tool"]["driver"]["rules"][0]

        # Required rule fields
        assert "id" in rule

        # Optional but recommended fields
        assert "name" in rule
        assert "shortDescription" in rule
        assert "fullDescription" in rule
        assert "help" in rule

        # Descriptions must have text
        assert "text" in rule["shortDescription"]
        assert "text" in rule["fullDescription"]
        assert "text" in rule["help"]

    def test_sarif_level_values_are_valid(self) -> None:
        """Test that SARIF level values are valid."""
        location = Location(file=Path("test.py"), line_start=1, line_end=1)

        valid_levels = {"error", "warning", "note", "none"}

        for severity in Severity:
            finding = Finding(
                id="TEST-001",
                scanner="test",
                severity=severity,
                title="Test",
                description="Test",
                location=location,
            )

            exporter = SARIFExporter()
            sarif = exporter.export([finding])

            result = sarif["runs"][0]["results"][0]
            level = result["level"]

            # Level must be one of the valid SARIF levels
            assert level in valid_levels, f"{severity} mapped to invalid level: {level}"

    def test_sarif_with_multiple_findings(self) -> None:
        """Test SARIF export with multiple findings."""
        findings = [
            Finding(
                id="TEST-001",
                scanner="semgrep",
                severity=Severity.CRITICAL,
                title="SQL Injection",
                description="SQL injection vulnerability",
                location=Location(file=Path("app.py"), line_start=10, line_end=12),
                cwe_id="CWE-89",
            ),
            Finding(
                id="TEST-002",
                scanner="semgrep",
                severity=Severity.HIGH,
                title="XSS",
                description="Cross-site scripting vulnerability",
                location=Location(file=Path("app.py"), line_start=20, line_end=22),
                cwe_id="CWE-79",
            ),
            Finding(
                id="TEST-003",
                scanner="codeql",
                severity=Severity.MEDIUM,
                title="Path Traversal",
                description="Path traversal vulnerability",
                location=Location(file=Path("utils.py"), line_start=30, line_end=32),
                cwe_id="CWE-22",
            ),
        ]

        exporter = SARIFExporter()
        sarif = exporter.export(findings)

        # Should have 2 runs (semgrep and codeql)
        assert len(sarif["runs"]) == 2

        # Find semgrep run
        semgrep_run = next(
            r for r in sarif["runs"] if r["tool"]["driver"]["name"] == "semgrep"
        )
        assert len(semgrep_run["results"]) == 2

        # Find codeql run
        codeql_run = next(
            r for r in sarif["runs"] if r["tool"]["driver"]["name"] == "codeql"
        )
        assert len(codeql_run["results"]) == 1

    def test_sarif_with_all_finding_fields(self) -> None:
        """Test SARIF export with a fully-populated finding."""
        location = Location(
            file=Path("src/app.py"),
            line_start=42,
            line_end=45,
            column_start=10,
            column_end=25,
            code_snippet="query = 'SELECT * FROM users WHERE id=' + user_id",
            context_snippet="def get_user():\n    query = '...' + user_id\n    return db.execute(query)",
        )

        finding = Finding(
            id="SEMGREP-CWE-89-001",
            scanner="semgrep",
            severity=Severity.CRITICAL,
            title="SQL Injection",
            description="User input is passed directly to SQL query without sanitization",
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

        exporter = SARIFExporter()
        sarif = exporter.export([finding])

        result = sarif["runs"][0]["results"][0]

        # Verify all fields are present
        assert result["ruleId"] == "CWE-89"
        assert result["level"] == "error"
        assert result["message"]["text"] == finding.description

        # Verify location
        physical = result["locations"][0]["physicalLocation"]
        assert physical["artifactLocation"]["uri"] == "src/app.py"
        assert physical["region"]["startLine"] == 42
        assert physical["region"]["endLine"] == 45
        assert physical["region"]["startColumn"] == 10
        assert physical["region"]["endColumn"] == 25
        assert "SELECT" in physical["region"]["snippet"]["text"]

        # Verify properties
        props = result["properties"]
        assert props["scanner"] == "semgrep"
        assert props["cvss"] == 9.8
        assert props["confidence"] == "high"
        assert "Use parameterized queries" in props["remediation"]
        assert len(props["references"]) == 2
