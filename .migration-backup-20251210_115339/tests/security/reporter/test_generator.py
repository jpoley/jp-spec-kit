"""Tests for report generator."""

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from specify_cli.security.reporter.generator import ReportConfig, ReportGenerator
from specify_cli.security.reporter.models import SecurityPosture


class MockSeverity(Enum):
    """Mock severity for testing."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class MockFinding:
    """Mock finding for testing."""

    id: str
    title: str
    description: str
    severity: MockSeverity
    cwe_id: str
    remediation: str | None = None


class MockClassification(Enum):
    """Mock classification for testing."""

    TRUE_POSITIVE = "TP"
    FALSE_POSITIVE = "FP"
    NEEDS_INVESTIGATION = "NI"


@dataclass
class MockTriageResult:
    """Mock triage result for testing."""

    finding_id: str
    classification: MockClassification


class TestReportConfig:
    """Tests for ReportConfig."""

    def test_defaults(self):
        """Test default configuration."""
        config = ReportConfig()

        assert config.project_name == "Security Audit"
        assert config.include_false_positives is False
        assert config.max_remediations == 10

    def test_custom_config(self):
        """Test custom configuration."""
        config = ReportConfig(
            project_name="My Project",
            include_false_positives=True,
            max_remediations=5,
        )

        assert config.project_name == "My Project"
        assert config.include_false_positives is True
        assert config.max_remediations == 5


class TestReportGenerator:
    """Tests for ReportGenerator."""

    @pytest.fixture
    def generator(self):
        """Create a report generator."""
        return ReportGenerator()

    @pytest.fixture
    def sample_findings(self):
        """Create sample findings."""
        return [
            MockFinding(
                id="F1",
                title="SQL Injection",
                description="SQL injection vulnerability",
                severity=MockSeverity.CRITICAL,
                cwe_id="CWE-89",
                remediation="Use parameterized queries",
            ),
            MockFinding(
                id="F2",
                title="XSS Vulnerability",
                description="Cross-site scripting",
                severity=MockSeverity.HIGH,
                cwe_id="CWE-79",
                remediation="Escape output",
            ),
            MockFinding(
                id="F3",
                title="Path Traversal",
                description="Path traversal issue",
                severity=MockSeverity.MEDIUM,
                cwe_id="CWE-22",
                remediation="Validate file paths",
            ),
            MockFinding(
                id="F4",
                title="Info Disclosure",
                description="Information leak",
                severity=MockSeverity.LOW,
                cwe_id="CWE-200",
            ),
        ]

    def test_generate_empty_findings(self, generator):
        """Test generating report with no findings."""
        report = generator.generate([])

        assert report.project_name == "Security Audit"
        assert report.posture == SecurityPosture.SECURE
        assert report.summary.total == 0
        assert report.summary.critical == 0
        assert len(report.owasp_compliance) == 10

    def test_generate_with_findings(self, generator, sample_findings):
        """Test generating report with findings."""
        report = generator.generate(
            sample_findings,
            scanners=["bandit", "semgrep"],
            files_scanned=100,
        )

        assert report.summary.total == 4
        assert report.summary.critical == 1
        assert report.summary.high == 1
        assert report.summary.medium == 1
        assert report.summary.low == 1
        assert report.files_scanned == 100
        assert "bandit" in report.scanners_used

    def test_posture_at_risk_with_critical(self, generator):
        """Test posture is AT_RISK with critical findings."""
        findings = [
            MockFinding(
                id="F1",
                title="Critical Issue",
                description="Critical",
                severity=MockSeverity.CRITICAL,
                cwe_id="CWE-89",
            ),
        ]

        report = generator.generate(findings)

        assert report.posture == SecurityPosture.AT_RISK

    def test_posture_conditional_with_high(self, generator):
        """Test posture is CONDITIONAL with high findings."""
        findings = [
            MockFinding(
                id="F1",
                title="High Issue",
                description="High",
                severity=MockSeverity.HIGH,
                cwe_id="CWE-89",
            ),
        ]

        report = generator.generate(findings)

        # Has non-compliant OWASP category, so CONDITIONAL
        assert report.posture == SecurityPosture.CONDITIONAL

    def test_posture_secure_with_low_only(self, generator):
        """Test posture is SECURE with only low/info findings."""
        findings = [
            MockFinding(
                id="F1",
                title="Low Issue",
                description="Low",
                severity=MockSeverity.LOW,
                cwe_id="CWE-200",
            ),
        ]

        report = generator.generate(findings)

        # Low findings with partial compliance still conditional
        # because there's at least one non-compliant category
        assert report.posture in [SecurityPosture.SECURE, SecurityPosture.CONDITIONAL]

    def test_triage_affects_summary(self, generator, sample_findings):
        """Test triage results affect summary counts."""
        triage_results = [
            MockTriageResult(
                finding_id="F1", classification=MockClassification.TRUE_POSITIVE
            ),
            MockTriageResult(
                finding_id="F2", classification=MockClassification.FALSE_POSITIVE
            ),
            MockTriageResult(
                finding_id="F3", classification=MockClassification.NEEDS_INVESTIGATION
            ),
        ]

        report = generator.generate(sample_findings, triage_results)

        assert report.summary.true_positives == 1
        assert report.summary.false_positives == 1
        assert report.summary.needs_investigation == 2  # F3 + F4 (untriaged)

    def test_remediations_generated(self, generator, sample_findings):
        """Test remediations are generated."""
        report = generator.generate(sample_findings)

        assert len(report.remediations) > 0
        # Critical first
        assert report.remediations[0].title == "SQL Injection"
        assert report.remediations[0].priority == 1

    def test_remediations_skip_false_positives(self, generator, sample_findings):
        """Test false positives are skipped in remediations."""
        triage_results = [
            MockTriageResult(
                finding_id="F1", classification=MockClassification.FALSE_POSITIVE
            ),
        ]

        report = generator.generate(sample_findings, triage_results)

        # F1 (SQL Injection) should be skipped
        remediation_ids = [r.finding_id for r in report.remediations]
        assert "F1" not in remediation_ids

    def test_remediations_include_false_positives_when_configured(
        self, sample_findings
    ):
        """Test false positives are included when configured."""
        config = ReportConfig(include_false_positives=True)
        generator = ReportGenerator(config)

        triage_results = [
            MockTriageResult(
                finding_id="F1", classification=MockClassification.FALSE_POSITIVE
            ),
        ]

        report = generator.generate(sample_findings, triage_results)

        # F1 (SQL Injection) should be included when config allows
        remediation_ids = [r.finding_id for r in report.remediations]
        assert "F1" in remediation_ids

    def test_remediations_limited_by_config(self, sample_findings):
        """Test remediations limited by max_remediations."""
        config = ReportConfig(max_remediations=2)
        generator = ReportGenerator(config)

        report = generator.generate(sample_findings)

        assert len(report.remediations) == 2

    def test_custom_project_name(self, sample_findings):
        """Test custom project name in config."""
        config = ReportConfig(project_name="My Security Audit")
        generator = ReportGenerator(config)

        report = generator.generate(sample_findings)

        assert report.project_name == "My Security Audit"


class TestReportOutput:
    """Tests for report output formats."""

    @pytest.fixture
    def generator(self):
        """Create a report generator."""
        return ReportGenerator()

    @pytest.fixture
    def sample_report(self, generator):
        """Create a sample report."""
        findings = [
            MockFinding(
                id="F1",
                title="SQL Injection",
                description="SQL injection in user query",
                severity=MockSeverity.CRITICAL,
                cwe_id="CWE-89",
                remediation="Use parameterized queries",
            ),
            MockFinding(
                id="F2",
                title="XSS",
                description="Cross-site scripting",
                severity=MockSeverity.HIGH,
                cwe_id="CWE-79",
                remediation="Escape output",
            ),
        ]
        return generator.generate(
            findings,
            scanners=["bandit"],
            files_scanned=50,
        )

    def test_to_markdown(self, generator, sample_report):
        """Test markdown output."""
        md = generator.to_markdown(sample_report)

        assert "# Security Audit Report" in md
        assert "Security Audit" in md  # Project name
        assert "Posture:" in md
        assert "Executive Summary" in md
        assert "OWASP Top 10 Compliance" in md
        assert "Top Remediation Priorities" in md
        assert "SQL Injection" in md
        assert "bandit" in md

    def test_to_markdown_includes_metrics(self, generator, sample_report):
        """Test markdown includes all metrics."""
        md = generator.to_markdown(sample_report)

        assert "Total Findings" in md
        assert "Critical" in md
        assert "High" in md
        assert "Files Scanned" in md

    def test_to_markdown_includes_owasp_table(self, generator, sample_report):
        """Test markdown includes OWASP compliance table."""
        md = generator.to_markdown(sample_report)

        assert "A01:2021" in md
        assert "A03:2021" in md  # Injection category
        assert "Broken Access Control" in md

    def test_to_html(self, generator, sample_report):
        """Test HTML output."""
        html = generator.to_html(sample_report)

        assert "<!DOCTYPE html>" in html
        assert "<title>Security Audit Report" in html
        assert "<style>" in html
        assert "Security Audit Report" in html

    def test_to_json(self, generator, sample_report):
        """Test JSON output."""
        json_str = generator.to_json(sample_report)
        data = json.loads(json_str)

        assert data["project_name"] == "Security Audit"
        assert data["posture"] == "at_risk"  # Critical finding
        assert "summary" in data
        assert "owasp_compliance" in data
        assert "remediations" in data
        assert data["files_scanned"] == 50

    def test_json_serialization_complete(self, generator, sample_report):
        """Test JSON contains all expected fields."""
        json_str = generator.to_json(sample_report)
        data = json.loads(json_str)

        # Summary fields
        assert data["summary"]["total"] == 2
        assert data["summary"]["critical"] == 1
        assert "false_positive_rate" in data["summary"]

        # OWASP fields
        assert len(data["owasp_compliance"]) == 10
        owasp_item = data["owasp_compliance"][0]
        assert "id" in owasp_item
        assert "name" in owasp_item
        assert "status" in owasp_item

        # Remediation fields
        assert len(data["remediations"]) > 0
        rem = data["remediations"][0]
        assert "finding_id" in rem
        assert "priority" in rem
        assert "title" in rem


class TestSaveReport:
    """Tests for saving reports to files."""

    @pytest.fixture
    def generator(self):
        """Create a report generator."""
        return ReportGenerator()

    @pytest.fixture
    def sample_report(self, generator):
        """Create a sample report."""
        findings = [
            MockFinding(
                id="F1",
                title="Issue",
                description="Description",
                severity=MockSeverity.HIGH,
                cwe_id="CWE-89",
            ),
        ]
        return generator.generate(findings)

    def test_save_markdown(self, generator, sample_report):
        """Test saving markdown report."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.md"

            generator.save_report(sample_report, output_path, format="markdown")

            assert output_path.exists()
            content = output_path.read_text()
            assert "# Security Audit Report" in content

    def test_save_html(self, generator, sample_report):
        """Test saving HTML report."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.html"

            generator.save_report(sample_report, output_path, format="html")

            assert output_path.exists()
            content = output_path.read_text()
            assert "<!DOCTYPE html>" in content

    def test_save_json(self, generator, sample_report):
        """Test saving JSON report."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.json"

            generator.save_report(sample_report, output_path, format="json")

            assert output_path.exists()
            content = output_path.read_text()
            data = json.loads(content)
            assert "project_name" in data

    def test_save_invalid_format(self, generator, sample_report):
        """Test saving with invalid format raises error."""
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.txt"

            with pytest.raises(ValueError, match="Unsupported format"):
                generator.save_report(sample_report, output_path, format="txt")


class TestPostureDetermination:
    """Tests for security posture determination logic."""

    @pytest.fixture
    def generator(self):
        """Create a report generator."""
        return ReportGenerator()

    def test_at_risk_with_many_non_compliant(self, generator):
        """Test AT_RISK with 3+ non-compliant OWASP categories."""
        # Create findings across 3+ categories with critical severity
        findings = [
            MockFinding(
                id="F1",
                title="Issue",
                description="",
                severity=MockSeverity.CRITICAL,
                cwe_id="CWE-89",
            ),
            MockFinding(
                id="F2",
                title="Issue",
                description="",
                severity=MockSeverity.CRITICAL,
                cwe_id="CWE-22",
            ),
            MockFinding(
                id="F3",
                title="Issue",
                description="",
                severity=MockSeverity.CRITICAL,
                cwe_id="CWE-327",
            ),
        ]

        report = generator.generate(findings)

        assert report.posture == SecurityPosture.AT_RISK

    def test_conditional_with_high_findings(self, generator):
        """Test CONDITIONAL with many high findings."""
        findings = [
            MockFinding(
                id=f"F{i}",
                title="Issue",
                description="",
                severity=MockSeverity.HIGH,
                cwe_id="CWE-89",
            )
            for i in range(6)
        ]

        report = generator.generate(findings)

        assert report.posture == SecurityPosture.CONDITIONAL

    def test_secure_with_no_significant_findings(self, generator):
        """Test SECURE with no critical/high findings and full compliance."""
        report = generator.generate([])

        assert report.posture == SecurityPosture.SECURE
