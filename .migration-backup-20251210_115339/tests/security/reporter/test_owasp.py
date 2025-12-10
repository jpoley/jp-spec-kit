"""Tests for OWASP compliance checking."""

from dataclasses import dataclass
from enum import Enum


from specify_cli.security.reporter.models import ComplianceStatus
from specify_cli.security.reporter.owasp import (
    OWASP_TOP_10,
    get_owasp_category,
    check_owasp_compliance,
)


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
    cwe_id: str
    severity: MockSeverity


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


class TestOWASPDefinitions:
    """Tests for OWASP Top 10 definitions."""

    def test_top_10_count(self):
        """Test we have all 10 categories."""
        assert len(OWASP_TOP_10) == 10

    def test_category_ids(self):
        """Test category IDs follow expected format."""
        expected_ids = [
            "A01:2021",
            "A02:2021",
            "A03:2021",
            "A04:2021",
            "A05:2021",
            "A06:2021",
            "A07:2021",
            "A08:2021",
            "A09:2021",
            "A10:2021",
        ]
        actual_ids = [cat.id for cat in OWASP_TOP_10]
        assert actual_ids == expected_ids

    def test_all_have_cwes(self):
        """Test all categories have at least one CWE."""
        for category in OWASP_TOP_10:
            assert len(category.cwes) > 0, f"{category.id} has no CWEs"

    def test_injection_includes_sql_injection(self):
        """Test A03:2021 Injection includes SQL injection CWE."""
        injection_cat = next(c for c in OWASP_TOP_10 if c.id == "A03:2021")
        assert "CWE-89" in injection_cat.cwes

    def test_injection_includes_xss(self):
        """Test A03:2021 Injection includes XSS CWE."""
        injection_cat = next(c for c in OWASP_TOP_10 if c.id == "A03:2021")
        assert "CWE-79" in injection_cat.cwes

    def test_access_control_includes_path_traversal(self):
        """Test A01:2021 includes path traversal CWE."""
        access_cat = next(c for c in OWASP_TOP_10 if c.id == "A01:2021")
        assert "CWE-22" in access_cat.cwes

    def test_crypto_failures_includes_weak_crypto(self):
        """Test A02:2021 includes weak cryptography CWE."""
        crypto_cat = next(c for c in OWASP_TOP_10 if c.id == "A02:2021")
        assert "CWE-327" in crypto_cat.cwes

    def test_auth_failures_includes_hardcoded_creds(self):
        """Test A07:2021 includes hardcoded credentials CWE."""
        auth_cat = next(c for c in OWASP_TOP_10 if c.id == "A07:2021")
        assert "CWE-798" in auth_cat.cwes


class TestGetOwaspCategory:
    """Tests for get_owasp_category function."""

    def test_find_sql_injection(self):
        """Test finding SQL injection category."""
        category = get_owasp_category("CWE-89")

        assert category is not None
        assert category.id == "A03:2021"
        assert category.name == "Injection"

    def test_find_xss(self):
        """Test finding XSS category."""
        category = get_owasp_category("CWE-79")

        assert category is not None
        assert category.id == "A03:2021"

    def test_find_path_traversal(self):
        """Test finding path traversal category."""
        category = get_owasp_category("CWE-22")

        assert category is not None
        assert category.id == "A01:2021"

    def test_find_hardcoded_creds(self):
        """Test finding hardcoded credentials category."""
        category = get_owasp_category("CWE-798")

        assert category is not None
        assert category.id == "A07:2021"

    def test_unknown_cwe_returns_none(self):
        """Test unknown CWE returns None."""
        category = get_owasp_category("CWE-99999")
        assert category is None


class TestCheckOwaspCompliance:
    """Tests for check_owasp_compliance function."""

    def test_empty_findings_all_compliant(self):
        """Test no findings results in all compliant."""
        results = check_owasp_compliance([])

        assert len(results) == 10
        for result in results:
            assert result.status == ComplianceStatus.COMPLIANT
            assert result.finding_count == 0
            assert result.critical_count == 0

    def test_single_finding_partial(self):
        """Test single non-critical finding results in partial compliance."""
        findings = [MockFinding(id="F1", cwe_id="CWE-89", severity=MockSeverity.HIGH)]

        results = check_owasp_compliance(findings)

        # A03:2021 Injection should be partial
        injection = next(r for r in results if r.id == "A03:2021")
        assert injection.status == ComplianceStatus.PARTIAL
        assert injection.finding_count == 1
        assert injection.critical_count == 0

        # Other categories should be compliant
        access = next(r for r in results if r.id == "A01:2021")
        assert access.status == ComplianceStatus.COMPLIANT

    def test_critical_finding_non_compliant(self):
        """Test critical finding results in non-compliant."""
        findings = [
            MockFinding(id="F1", cwe_id="CWE-89", severity=MockSeverity.CRITICAL)
        ]

        results = check_owasp_compliance(findings)

        injection = next(r for r in results if r.id == "A03:2021")
        assert injection.status == ComplianceStatus.NON_COMPLIANT
        assert injection.finding_count == 1
        assert injection.critical_count == 1

    def test_multiple_findings_same_category(self):
        """Test multiple findings in same category."""
        findings = [
            MockFinding(id="F1", cwe_id="CWE-89", severity=MockSeverity.HIGH),
            MockFinding(id="F2", cwe_id="CWE-79", severity=MockSeverity.MEDIUM),
            MockFinding(id="F3", cwe_id="CWE-77", severity=MockSeverity.CRITICAL),
        ]

        results = check_owasp_compliance(findings)

        injection = next(r for r in results if r.id == "A03:2021")
        assert injection.status == ComplianceStatus.NON_COMPLIANT
        assert injection.finding_count == 3
        assert injection.critical_count == 1

    def test_findings_across_categories(self):
        """Test findings across multiple categories."""
        findings = [
            MockFinding(
                id="F1", cwe_id="CWE-89", severity=MockSeverity.HIGH
            ),  # Injection
            MockFinding(
                id="F2", cwe_id="CWE-22", severity=MockSeverity.MEDIUM
            ),  # Access Control
            MockFinding(id="F3", cwe_id="CWE-327", severity=MockSeverity.LOW),  # Crypto
        ]

        results = check_owasp_compliance(findings)

        injection = next(r for r in results if r.id == "A03:2021")
        assert injection.status == ComplianceStatus.PARTIAL
        assert injection.finding_count == 1

        access = next(r for r in results if r.id == "A01:2021")
        assert access.status == ComplianceStatus.PARTIAL
        assert access.finding_count == 1

        crypto = next(r for r in results if r.id == "A02:2021")
        assert crypto.status == ComplianceStatus.PARTIAL
        assert crypto.finding_count == 1

    def test_triage_filters_false_positives(self):
        """Test false positives are filtered from compliance check."""
        findings = [
            MockFinding(id="F1", cwe_id="CWE-89", severity=MockSeverity.CRITICAL),
            MockFinding(id="F2", cwe_id="CWE-89", severity=MockSeverity.HIGH),
        ]

        triage_results = [
            MockTriageResult(
                finding_id="F1", classification=MockClassification.FALSE_POSITIVE
            ),
        ]

        results = check_owasp_compliance(findings, triage_results)

        injection = next(r for r in results if r.id == "A03:2021")
        # Only F2 counted (F1 is FP)
        assert injection.status == ComplianceStatus.PARTIAL
        assert injection.finding_count == 1
        assert injection.critical_count == 0

    def test_triage_true_positives_counted(self):
        """Test true positives are counted in compliance check."""
        findings = [
            MockFinding(id="F1", cwe_id="CWE-89", severity=MockSeverity.CRITICAL),
        ]

        triage_results = [
            MockTriageResult(
                finding_id="F1", classification=MockClassification.TRUE_POSITIVE
            ),
        ]

        results = check_owasp_compliance(findings, triage_results)

        injection = next(r for r in results if r.id == "A03:2021")
        assert injection.status == ComplianceStatus.NON_COMPLIANT
        assert injection.finding_count == 1
        assert injection.critical_count == 1

    def test_unknown_cwe_not_counted(self):
        """Test findings with unknown CWE don't affect compliance."""
        findings = [
            MockFinding(id="F1", cwe_id="CWE-99999", severity=MockSeverity.CRITICAL),
        ]

        results = check_owasp_compliance(findings)

        # All categories should be compliant since CWE-99999 doesn't map
        for result in results:
            assert result.status == ComplianceStatus.COMPLIANT
            assert result.finding_count == 0

    def test_result_includes_cwes(self):
        """Test results include the CWE list."""
        results = check_owasp_compliance([])

        injection = next(r for r in results if r.id == "A03:2021")
        assert "CWE-89" in injection.cwes
        assert "CWE-79" in injection.cwes
