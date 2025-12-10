"""Tests for security models - Unified Finding Format (UFFormat).

Tests cover:
- Severity and Confidence enums
- Location dataclass
- Finding dataclass with fingerprinting and merging
- Serialization (to_dict, from_dict, to_sarif)
"""

from pathlib import Path

import pytest

from specify_cli.security.models import Confidence, Finding, Location, Severity


class TestSeverity:
    """Tests for Severity enum."""

    def test_severity_values(self):
        """Test severity enum values are correct."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
        assert Severity.INFO.value == "info"

    def test_severity_from_string(self):
        """Test creating severity from string value."""
        assert Severity("critical") == Severity.CRITICAL
        assert Severity("high") == Severity.HIGH
        assert Severity("medium") == Severity.MEDIUM
        assert Severity("low") == Severity.LOW
        assert Severity("info") == Severity.INFO

    def test_severity_invalid_value(self):
        """Test invalid severity raises error."""
        with pytest.raises(ValueError):
            Severity("invalid")


class TestConfidence:
    """Tests for Confidence enum."""

    def test_confidence_values(self):
        """Test confidence enum values are correct."""
        assert Confidence.HIGH.value == "high"
        assert Confidence.MEDIUM.value == "medium"
        assert Confidence.LOW.value == "low"

    def test_confidence_from_string(self):
        """Test creating confidence from string value."""
        assert Confidence("high") == Confidence.HIGH
        assert Confidence("medium") == Confidence.MEDIUM
        assert Confidence("low") == Confidence.LOW


class TestLocation:
    """Tests for Location dataclass."""

    @pytest.fixture
    def sample_location(self):
        """Create a sample location for testing."""
        return Location(
            file=Path("src/app.py"),
            line_start=42,
            line_end=45,
            column_start=8,
            column_end=50,
            code_snippet='query = "SELECT * FROM users WHERE id = " + user_id',
            context_snippet="def get_user(user_id):\n    ...",
        )

    def test_location_creation(self, sample_location):
        """Test basic location creation."""
        assert sample_location.file == Path("src/app.py")
        assert sample_location.line_start == 42
        assert sample_location.line_end == 45
        assert sample_location.column_start == 8
        assert sample_location.column_end == 50

    def test_location_minimal(self):
        """Test location with minimal required fields."""
        loc = Location(file=Path("test.py"), line_start=1, line_end=1)
        assert loc.file == Path("test.py")
        assert loc.column_start is None
        assert loc.code_snippet == ""

    def test_location_to_dict(self, sample_location):
        """Test location serialization to dict."""
        data = sample_location.to_dict()

        assert data["file"] == "src/app.py"
        assert data["line_start"] == 42
        assert data["line_end"] == 45
        assert data["column_start"] == 8
        assert data["column_end"] == 50
        assert "user_id" in data["code_snippet"]
        assert data["context_snippet"] is not None

    def test_location_from_dict(self, sample_location):
        """Test location deserialization from dict."""
        data = sample_location.to_dict()
        restored = Location.from_dict(data)

        assert restored.file == sample_location.file
        assert restored.line_start == sample_location.line_start
        assert restored.line_end == sample_location.line_end
        assert restored.column_start == sample_location.column_start
        assert restored.code_snippet == sample_location.code_snippet

    def test_location_from_dict_minimal(self):
        """Test location deserialization with minimal fields."""
        data = {"file": "test.py", "line_start": 10, "line_end": 15}
        loc = Location.from_dict(data)

        assert loc.file == Path("test.py")
        assert loc.line_start == 10
        assert loc.column_start is None


class TestFinding:
    """Tests for Finding dataclass."""

    @pytest.fixture
    def sample_finding(self):
        """Create a sample finding for testing."""
        return Finding(
            id="SEMGREP-CWE-89-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="User input directly concatenated into SQL query",
            location=Location(
                file=Path("src/db.py"),
                line_start=42,
                line_end=45,
                code_snippet='query = "SELECT * FROM users WHERE id = " + user_id',
            ),
            cwe_id="CWE-89",
            cvss_score=8.5,
            confidence=Confidence.HIGH,
            remediation="Use parameterized queries instead",
            references=["https://owasp.org/SQL_Injection"],
        )

    def test_finding_creation(self, sample_finding):
        """Test basic finding creation."""
        assert sample_finding.id == "SEMGREP-CWE-89-001"
        assert sample_finding.scanner == "semgrep"
        assert sample_finding.severity == Severity.HIGH
        assert sample_finding.title == "SQL Injection"
        assert sample_finding.cwe_id == "CWE-89"
        assert sample_finding.cvss_score == 8.5

    def test_finding_minimal(self):
        """Test finding with minimal required fields."""
        finding = Finding(
            id="TEST-001",
            scanner="test",
            severity=Severity.INFO,
            title="Test Finding",
            description="Test description",
            location=Location(file=Path("test.py"), line_start=1, line_end=1),
        )

        assert finding.cwe_id is None
        assert finding.cvss_score is None
        assert finding.confidence == Confidence.MEDIUM
        assert finding.remediation is None
        assert finding.references == []

    def test_finding_fingerprint(self, sample_finding):
        """Test fingerprint generation."""
        fp = sample_finding.fingerprint()

        assert len(fp) == 16
        assert fp.isalnum()

    def test_finding_fingerprint_consistency(self, sample_finding):
        """Test fingerprint is consistent for same finding."""
        fp1 = sample_finding.fingerprint()
        fp2 = sample_finding.fingerprint()

        assert fp1 == fp2

    def test_finding_fingerprint_uniqueness(self, sample_finding):
        """Test different findings have different fingerprints."""
        other = Finding(
            id="OTHER-001",
            scanner="other",
            severity=Severity.LOW,
            title="Different Finding",
            description="Different",
            location=Location(file=Path("other.py"), line_start=100, line_end=105),
        )

        assert sample_finding.fingerprint() != other.fingerprint()

    def test_finding_fingerprint_same_location_same_cwe(self, sample_finding):
        """Test findings with same location and CWE have same fingerprint."""
        other = Finding(
            id="CODEQL-001",  # Different ID
            scanner="codeql",  # Different scanner
            severity=Severity.CRITICAL,  # Different severity
            title="SQL Injection",
            description="Different description",
            location=Location(
                file=Path("src/db.py"),  # Same file
                line_start=42,  # Same lines
                line_end=45,
            ),
            cwe_id="CWE-89",  # Same CWE
        )

        assert sample_finding.fingerprint() == other.fingerprint()

    def test_finding_merge_basic(self, sample_finding):
        """Test basic merge of duplicate findings."""
        other = Finding(
            id="CODEQL-001",
            scanner="codeql",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="CodeQL detected SQL injection",
            location=Location(
                file=Path("src/db.py"),
                line_start=42,
                line_end=45,
            ),
            cwe_id="CWE-89",
            confidence=Confidence.MEDIUM,
            references=["https://codeql.example.com"],
        )

        sample_finding.merge(other)

        # Confidence should increase when both agree
        assert sample_finding.confidence == Confidence.HIGH

        # References should be combined
        assert "https://owasp.org/SQL_Injection" in sample_finding.references
        assert "https://codeql.example.com" in sample_finding.references

        # Scanner should be tracked in metadata
        assert "codeql" in sample_finding.metadata.get("merged_scanners", [])

    def test_finding_merge_takes_higher_severity(self, sample_finding):
        """Test merge takes higher severity."""
        other = Finding(
            id="CODEQL-001",
            scanner="codeql",
            severity=Severity.CRITICAL,  # Higher than sample's HIGH
            title="SQL Injection",
            description="Critical SQL injection",
            location=Location(
                file=Path("src/db.py"),
                line_start=42,
                line_end=45,
            ),
            cwe_id="CWE-89",
        )

        sample_finding.merge(other)

        assert sample_finding.severity == Severity.CRITICAL

    def test_finding_merge_different_fingerprint_raises(self, sample_finding):
        """Test merging different findings raises error."""
        other = Finding(
            id="OTHER-001",
            scanner="other",
            severity=Severity.LOW,
            title="Different",
            description="Different finding",
            location=Location(file=Path("other.py"), line_start=1, line_end=1),
        )

        with pytest.raises(ValueError, match="different fingerprints"):
            sample_finding.merge(other)

    def test_finding_to_dict(self, sample_finding):
        """Test finding serialization to dict."""
        data = sample_finding.to_dict()

        assert data["id"] == "SEMGREP-CWE-89-001"
        assert data["scanner"] == "semgrep"
        assert data["severity"] == "high"
        assert data["title"] == "SQL Injection"
        assert data["cwe_id"] == "CWE-89"
        assert data["cvss_score"] == 8.5
        assert data["confidence"] == "high"
        assert "location" in data
        assert data["location"]["file"] == "src/db.py"

    def test_finding_from_dict(self, sample_finding):
        """Test finding deserialization from dict."""
        data = sample_finding.to_dict()
        restored = Finding.from_dict(data)

        assert restored.id == sample_finding.id
        assert restored.scanner == sample_finding.scanner
        assert restored.severity == sample_finding.severity
        assert restored.title == sample_finding.title
        assert restored.cwe_id == sample_finding.cwe_id
        assert restored.location.file == sample_finding.location.file

    def test_finding_to_sarif(self, sample_finding):
        """Test SARIF conversion."""
        sarif = sample_finding.to_sarif()

        assert sarif["ruleId"] == "CWE-89"
        assert sarif["level"] == "error"  # HIGH maps to error
        assert sarif["message"]["text"] == sample_finding.description

        # Check location
        loc = sarif["locations"][0]["physicalLocation"]
        assert loc["artifactLocation"]["uri"] == "src/db.py"
        assert loc["region"]["startLine"] == 42
        assert loc["region"]["endLine"] == 45

        # Check properties
        assert sarif["properties"]["scanner"] == "semgrep"
        assert sarif["properties"]["cvss"] == 8.5

    def test_finding_sarif_severity_mapping(self):
        """Test all severities map to correct SARIF levels."""
        test_cases = [
            (Severity.CRITICAL, "error"),
            (Severity.HIGH, "error"),
            (Severity.MEDIUM, "warning"),
            (Severity.LOW, "note"),
            (Severity.INFO, "note"),
        ]

        for severity, expected_level in test_cases:
            finding = Finding(
                id="TEST",
                scanner="test",
                severity=severity,
                title="Test",
                description="Test",
                location=Location(file=Path("test.py"), line_start=1, line_end=1),
            )
            sarif = finding.to_sarif()
            assert sarif["level"] == expected_level, (
                f"{severity} should map to {expected_level}"
            )

    def test_finding_sarif_without_cwe(self):
        """Test SARIF conversion uses ID when CWE is missing."""
        finding = Finding(
            id="CUSTOM-001",
            scanner="custom",
            severity=Severity.MEDIUM,
            title="Custom Finding",
            description="No CWE",
            location=Location(file=Path("test.py"), line_start=1, line_end=1),
            cwe_id=None,
        )
        sarif = finding.to_sarif()

        assert sarif["ruleId"] == "CUSTOM-001"

    def test_finding_from_dict_defaults(self):
        """Test from_dict uses correct defaults."""
        data = {
            "id": "TEST-001",
            "scanner": "test",
            "severity": "medium",
            "title": "Test",
            "description": "Test description",
            "location": {"file": "test.py", "line_start": 1, "line_end": 1},
        }
        finding = Finding.from_dict(data)

        assert finding.confidence == Confidence.MEDIUM
        assert finding.remediation is None
        assert finding.references == []
        assert finding.metadata == {}


class TestFindingEdgeCases:
    """Edge case tests for Finding."""

    def test_finding_with_empty_references(self):
        """Test finding with explicitly empty references."""
        finding = Finding(
            id="TEST",
            scanner="test",
            severity=Severity.INFO,
            title="Test",
            description="Test",
            location=Location(file=Path("test.py"), line_start=1, line_end=1),
            references=[],
        )

        data = finding.to_dict()
        assert data["references"] == []

    def test_finding_merge_deduplicates_references(self):
        """Test merge deduplicates references."""
        finding1 = Finding(
            id="TEST-1",
            scanner="test1",
            severity=Severity.HIGH,
            title="Test",
            description="Test",
            location=Location(file=Path("test.py"), line_start=1, line_end=1),
            cwe_id="CWE-1",
            references=["https://example.com/1", "https://example.com/2"],
        )
        finding2 = Finding(
            id="TEST-2",
            scanner="test2",
            severity=Severity.HIGH,
            title="Test",
            description="Test",
            location=Location(file=Path("test.py"), line_start=1, line_end=1),
            cwe_id="CWE-1",
            references=["https://example.com/2", "https://example.com/3"],  # Overlap
        )

        finding1.merge(finding2)

        # Should have 3 unique references
        assert len(finding1.references) == 3
        assert "https://example.com/1" in finding1.references
        assert "https://example.com/2" in finding1.references
        assert "https://example.com/3" in finding1.references

    def test_finding_fingerprint_uses_title_when_no_cwe(self):
        """Test fingerprint uses title when CWE is None."""
        finding1 = Finding(
            id="TEST-1",
            scanner="test",
            severity=Severity.HIGH,
            title="Same Title",
            description="Test",
            location=Location(file=Path("test.py"), line_start=1, line_end=1),
            cwe_id=None,
        )
        finding2 = Finding(
            id="TEST-2",
            scanner="test",
            severity=Severity.HIGH,
            title="Same Title",  # Same title
            description="Test",
            location=Location(file=Path("test.py"), line_start=1, line_end=1),
            cwe_id=None,
        )
        finding3 = Finding(
            id="TEST-3",
            scanner="test",
            severity=Severity.HIGH,
            title="Different Title",  # Different title
            description="Test",
            location=Location(file=Path("test.py"), line_start=1, line_end=1),
            cwe_id=None,
        )

        # Same location and title should match
        assert finding1.fingerprint() == finding2.fingerprint()
        # Different title should not match
        assert finding1.fingerprint() != finding3.fingerprint()
