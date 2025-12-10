"""Tests for reporter models."""

from datetime import datetime

import pytest

from specify_cli.security.reporter.models import (
    SecurityPosture,
    ComplianceStatus,
    OWASPCategory,
    FindingSummary,
    Remediation,
    AuditReport,
)


class TestSecurityPosture:
    """Tests for SecurityPosture enum."""

    def test_values(self):
        """Test posture values."""
        assert SecurityPosture.SECURE.value == "secure"
        assert SecurityPosture.CONDITIONAL.value == "conditional"
        assert SecurityPosture.AT_RISK.value == "at_risk"


class TestComplianceStatus:
    """Tests for ComplianceStatus enum."""

    def test_values(self):
        """Test status values."""
        assert ComplianceStatus.COMPLIANT.value == "compliant"
        assert ComplianceStatus.PARTIAL.value == "partial"
        assert ComplianceStatus.NON_COMPLIANT.value == "non_compliant"


class TestOWASPCategory:
    """Tests for OWASPCategory dataclass."""

    @pytest.fixture
    def sample_category(self):
        """Create a sample OWASP category."""
        return OWASPCategory(
            id="A01:2021",
            name="Broken Access Control",
            status=ComplianceStatus.PARTIAL,
            finding_count=3,
            critical_count=1,
            cwes=["CWE-22", "CWE-284"],
        )

    def test_to_dict(self, sample_category):
        """Test serialization."""
        data = sample_category.to_dict()

        assert data["id"] == "A01:2021"
        assert data["name"] == "Broken Access Control"
        assert data["status"] == "partial"
        assert data["finding_count"] == 3
        assert data["critical_count"] == 1
        assert "CWE-22" in data["cwes"]


class TestFindingSummary:
    """Tests for FindingSummary dataclass."""

    @pytest.fixture
    def sample_summary(self):
        """Create a sample findings summary."""
        return FindingSummary(
            total=20,
            critical=2,
            high=5,
            medium=8,
            low=3,
            info=2,
            true_positives=15,
            false_positives=3,
            needs_investigation=2,
        )

    def test_actionable_property(self, sample_summary):
        """Test actionable returns true positives."""
        assert sample_summary.actionable == 15

    def test_false_positive_rate(self, sample_summary):
        """Test FP rate calculation."""
        # 3 FPs / 20 total = 0.15
        assert sample_summary.false_positive_rate == 0.15

    def test_false_positive_rate_zero_total(self):
        """Test FP rate with no findings."""
        summary = FindingSummary(
            total=0,
            critical=0,
            high=0,
            medium=0,
            low=0,
            info=0,
            true_positives=0,
            false_positives=0,
            needs_investigation=0,
        )
        assert summary.false_positive_rate == 0.0

    def test_to_dict(self, sample_summary):
        """Test serialization."""
        data = sample_summary.to_dict()

        assert data["total"] == 20
        assert data["critical"] == 2
        assert data["actionable"] == 15
        assert data["false_positive_rate"] == 15.0  # Percentage


class TestRemediation:
    """Tests for Remediation dataclass."""

    @pytest.fixture
    def sample_remediation(self):
        """Create a sample remediation."""
        return Remediation(
            finding_id="FINDING-001",
            priority=1,
            title="SQL Injection in user query",
            description="User input is concatenated directly into SQL query",
            fix_guidance="Use parameterized queries",
            estimated_effort="2-4 hours",
            cwe_id="CWE-89",
        )

    def test_to_dict(self, sample_remediation):
        """Test serialization."""
        data = sample_remediation.to_dict()

        assert data["finding_id"] == "FINDING-001"
        assert data["priority"] == 1
        assert data["title"] == "SQL Injection in user query"
        assert data["cwe_id"] == "CWE-89"

    def test_without_cwe(self):
        """Test remediation without CWE."""
        rem = Remediation(
            finding_id="F1",
            priority=1,
            title="Issue",
            description="Desc",
            fix_guidance="Fix it",
            estimated_effort="1 hour",
        )
        assert rem.cwe_id is None


class TestAuditReport:
    """Tests for AuditReport dataclass."""

    @pytest.fixture
    def sample_report(self):
        """Create a sample audit report."""
        summary = FindingSummary(
            total=10,
            critical=1,
            high=3,
            medium=4,
            low=2,
            info=0,
            true_positives=8,
            false_positives=1,
            needs_investigation=1,
        )

        owasp = [
            OWASPCategory(
                id="A01:2021",
                name="Broken Access Control",
                status=ComplianceStatus.COMPLIANT,
                finding_count=0,
                critical_count=0,
                cwes=["CWE-22"],
            ),
            OWASPCategory(
                id="A03:2021",
                name="Injection",
                status=ComplianceStatus.PARTIAL,
                finding_count=3,
                critical_count=0,
                cwes=["CWE-89"],
            ),
        ]

        remediations = [
            Remediation(
                finding_id="F1",
                priority=1,
                title="Fix SQL Injection",
                description="SQL issue",
                fix_guidance="Use params",
                estimated_effort="2 hours",
            ),
            Remediation(
                finding_id="F2",
                priority=2,
                title="Fix XSS",
                description="XSS issue",
                fix_guidance="Escape output",
                estimated_effort="1 hour",
            ),
        ]

        return AuditReport(
            project_name="Test Project",
            scan_date=datetime(2024, 1, 15, 10, 30),
            posture=SecurityPosture.CONDITIONAL,
            summary=summary,
            owasp_compliance=owasp,
            remediations=remediations,
            scanners_used=["bandit", "semgrep"],
            files_scanned=150,
        )

    def test_compliance_score_all_compliant(self):
        """Test compliance score with all compliant categories."""
        summary = FindingSummary(
            total=0,
            critical=0,
            high=0,
            medium=0,
            low=0,
            info=0,
            true_positives=0,
            false_positives=0,
            needs_investigation=0,
        )

        owasp = [
            OWASPCategory(
                id=f"A0{i}:2021",
                name=f"Category {i}",
                status=ComplianceStatus.COMPLIANT,
                finding_count=0,
                critical_count=0,
                cwes=[],
            )
            for i in range(1, 11)
        ]

        report = AuditReport(
            project_name="Test",
            scan_date=datetime.now(),
            posture=SecurityPosture.SECURE,
            summary=summary,
            owasp_compliance=owasp,
            remediations=[],
            scanners_used=[],
            files_scanned=0,
        )

        assert report.compliance_score == 100.0

    def test_compliance_score_mixed(self, sample_report):
        """Test compliance score with mixed compliance."""
        # 1 compliant (10 pts) + 1 partial (5 pts) = 15 pts
        # 15 / 2 categories = 7.5
        # 7.5 * 10 = 75.0
        assert sample_report.compliance_score == 75.0

    def test_compliance_score_no_categories(self):
        """Test compliance score with no OWASP categories."""
        summary = FindingSummary(
            total=0,
            critical=0,
            high=0,
            medium=0,
            low=0,
            info=0,
            true_positives=0,
            false_positives=0,
            needs_investigation=0,
        )

        report = AuditReport(
            project_name="Test",
            scan_date=datetime.now(),
            posture=SecurityPosture.SECURE,
            summary=summary,
            owasp_compliance=[],
            remediations=[],
            scanners_used=[],
            files_scanned=0,
        )

        assert report.compliance_score == 100.0

    def test_top_remediations(self, sample_report):
        """Test top remediations returns sorted by priority."""
        top = sample_report.top_remediations

        assert len(top) == 2
        assert top[0].priority == 1
        assert top[1].priority == 2

    def test_top_remediations_limited_to_5(self):
        """Test top remediations limited to 5."""
        summary = FindingSummary(
            total=10,
            critical=0,
            high=0,
            medium=0,
            low=0,
            info=0,
            true_positives=0,
            false_positives=0,
            needs_investigation=0,
        )

        remediations = [
            Remediation(
                finding_id=f"F{i}",
                priority=i,
                title=f"Fix {i}",
                description="Desc",
                fix_guidance="Fix",
                estimated_effort="1 hour",
            )
            for i in range(1, 11)
        ]

        report = AuditReport(
            project_name="Test",
            scan_date=datetime.now(),
            posture=SecurityPosture.CONDITIONAL,
            summary=summary,
            owasp_compliance=[],
            remediations=remediations,
            scanners_used=[],
            files_scanned=0,
        )

        top = report.top_remediations
        assert len(top) == 5
        assert top[0].priority == 1
        assert top[4].priority == 5

    def test_to_dict(self, sample_report):
        """Test serialization."""
        data = sample_report.to_dict()

        assert data["project_name"] == "Test Project"
        assert data["posture"] == "conditional"
        assert data["compliance_score"] == 75.0
        assert len(data["owasp_compliance"]) == 2
        assert len(data["remediations"]) == 2
        assert data["files_scanned"] == 150
        assert "bandit" in data["scanners_used"]
