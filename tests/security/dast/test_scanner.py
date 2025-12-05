"""Tests for DAST scanner."""

import pytest

from specify_cli.security.dast.scanner import DASTScanner, DASTScanResult
from specify_cli.security.models import Confidence, Finding, Severity


class TestDASTScanResult:
    """Test DASTScanResult dataclass."""

    def test_creation(self) -> None:
        """Test creating DASTScanResult."""
        result = DASTScanResult(
            vulnerabilities=[],
            findings=[],
            pages_scanned=5,
            forms_tested=3,
            duration_seconds=10.5,
            errors=[],
        )

        assert result.pages_scanned == 5
        assert result.forms_tested == 3
        assert result.duration_seconds == 10.5
        assert len(result.vulnerabilities) == 0
        assert len(result.findings) == 0


class TestDASTScanner:
    """Test DAST scanner."""

    def test_initialization(self) -> None:
        """Test scanner initializes with configuration."""
        scanner = DASTScanner(
            base_url="https://example.com",
            max_depth=2,
            max_pages=50,
        )

        assert scanner.base_url == "https://example.com"
        assert scanner.max_depth == 2
        assert scanner.max_pages == 50
        assert scanner.auth_callback is None
        assert scanner.excluded_patterns == []

    def test_initialization_with_auth(self) -> None:
        """Test scanner accepts auth callback."""

        async def mock_auth(page):
            pass

        scanner = DASTScanner(
            base_url="https://example.com",
            auth_callback=mock_auth,
        )

        assert scanner.auth_callback == mock_auth

    def test_initialization_with_exclusions(self) -> None:
        """Test scanner accepts excluded patterns."""
        scanner = DASTScanner(
            base_url="https://example.com",
            excluded_patterns=["/admin", "/logout"],
        )

        assert "/admin" in scanner.excluded_patterns
        assert "/logout" in scanner.excluded_patterns

    def test_get_title(self) -> None:
        """Test vulnerability type to title mapping."""
        scanner = DASTScanner(base_url="https://example.com")

        assert scanner._get_title("xss") == "Cross-Site Scripting (XSS)"
        assert scanner._get_title("csrf") == "Cross-Site Request Forgery (CSRF)"
        assert scanner._get_title("session_fixation") == "Session Fixation"
        assert scanner._get_title("clickjacking") == "Clickjacking Vulnerability"

    def test_get_references(self) -> None:
        """Test vulnerability type to references mapping."""
        scanner = DASTScanner(base_url="https://example.com")

        xss_refs = scanner._get_references("xss")
        assert len(xss_refs) > 0
        assert any("owasp.org" in ref for ref in xss_refs)

        csrf_refs = scanner._get_references("csrf")
        assert len(csrf_refs) > 0
        assert any("owasp.org" in ref for ref in csrf_refs)

    def test_convert_to_findings(self) -> None:
        """Test conversion of vulnerabilities to UFFormat findings."""
        from specify_cli.security.dast.vulnerabilities import VulnerabilityResult

        scanner = DASTScanner(base_url="https://example.com")

        # Create test vulnerability
        vuln = VulnerabilityResult(
            type="xss",
            severity="high",
            url="https://example.com/search",
            parameter="q",
            payload="<script>alert(1)</script>",
            evidence="Payload reflected in response",
            confidence=0.9,
            remediation="Sanitize user input",
        )

        findings = scanner._convert_to_findings([vuln])

        assert len(findings) == 1
        finding = findings[0]

        # Check Finding attributes
        assert isinstance(finding, Finding)
        assert finding.scanner == "dast-playwright"
        assert finding.severity == Severity.HIGH
        assert finding.title == "Cross-Site Scripting (XSS)"
        assert finding.cwe_id == "CWE-79"
        assert finding.confidence == Confidence.HIGH
        assert finding.remediation == "Sanitize user input"

        # Check metadata
        assert finding.metadata["url"] == "https://example.com/search"
        assert finding.metadata["parameter"] == "q"
        assert finding.metadata["payload"] == "<script>alert(1)</script>"

    def test_convert_to_findings_severity_mapping(self) -> None:
        """Test severity string to Severity enum mapping."""
        from specify_cli.security.dast.vulnerabilities import VulnerabilityResult

        scanner = DASTScanner(base_url="https://example.com")

        test_cases = [
            ("critical", Severity.CRITICAL),
            ("high", Severity.HIGH),
            ("medium", Severity.MEDIUM),
            ("low", Severity.LOW),
            ("info", Severity.INFO),
        ]

        for severity_str, expected_enum in test_cases:
            vuln = VulnerabilityResult(
                type="test",
                severity=severity_str,
                url="https://example.com",
                parameter=None,
                payload=None,
                evidence="Test",
                confidence=0.5,
            )

            findings = scanner._convert_to_findings([vuln])
            assert findings[0].severity == expected_enum

    def test_convert_to_findings_confidence_mapping(self) -> None:
        """Test confidence float to Confidence enum mapping."""
        from specify_cli.security.dast.vulnerabilities import VulnerabilityResult

        scanner = DASTScanner(base_url="https://example.com")

        test_cases = [
            (0.95, Confidence.HIGH),
            (0.85, Confidence.MEDIUM),
            (0.65, Confidence.LOW),
            (0.5, Confidence.LOW),
        ]

        for confidence_float, expected_enum in test_cases:
            vuln = VulnerabilityResult(
                type="test",
                severity="medium",
                url="https://example.com",
                parameter=None,
                payload=None,
                evidence="Test",
                confidence=confidence_float,
            )

            findings = scanner._convert_to_findings([vuln])
            assert findings[0].confidence == expected_enum

    def test_convert_to_findings_cwe_mapping(self) -> None:
        """Test vulnerability type to CWE mapping."""
        from specify_cli.security.dast.vulnerabilities import VulnerabilityResult

        scanner = DASTScanner(base_url="https://example.com")

        cwe_tests = [
            ("xss", "CWE-79"),
            ("csrf", "CWE-352"),
            ("session_fixation", "CWE-384"),
            ("insecure_cookie", "CWE-614"),
            ("clickjacking", "CWE-1021"),
        ]

        for vuln_type, expected_cwe in cwe_tests:
            vuln = VulnerabilityResult(
                type=vuln_type,
                severity="medium",
                url="https://example.com",
                parameter=None,
                payload=None,
                evidence="Test",
                confidence=0.5,
            )

            findings = scanner._convert_to_findings([vuln])
            assert findings[0].cwe_id == expected_cwe

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires playwright and network access")
    async def test_scan_integration(self) -> None:
        """Integration test for full scan.

        This test is skipped by default as it requires:
        - Playwright installed
        - Network access
        - A test web application

        To run manually:
        1. Set up a test web application
        2. Update the base_url
        3. Remove the skip decorator
        """
        scanner = DASTScanner(
            base_url="http://localhost:8000",
            max_depth=1,
            max_pages=5,
        )

        result = await scanner.scan()

        assert isinstance(result, DASTScanResult)
        assert result.pages_scanned >= 0
        assert result.duration_seconds > 0
        assert isinstance(result.findings, list)
        assert isinstance(result.vulnerabilities, list)


@pytest.mark.asyncio
class TestDASTScannerE2E:
    """End-to-end tests for DAST scanner."""

    @pytest.mark.skip(reason="Requires vulnerable test application")
    async def test_detect_xss_vulnerability(self) -> None:
        """Test detection of real XSS vulnerability.

        Requires a vulnerable test application with known XSS.
        """
        scanner = DASTScanner(base_url="http://localhost:8000/vulnerable")
        result = await scanner.scan()

        # Should detect XSS
        xss_findings = [f for f in result.findings if f.cwe_id == "CWE-79"]
        assert len(xss_findings) > 0

    @pytest.mark.skip(reason="Requires test application")
    async def test_detect_missing_csrf_protection(self) -> None:
        """Test detection of missing CSRF protection.

        Requires a test application with forms lacking CSRF tokens.
        """
        scanner = DASTScanner(base_url="http://localhost:8000/no-csrf")
        result = await scanner.scan()

        # Should detect CSRF vulnerability
        csrf_findings = [f for f in result.findings if f.cwe_id == "CWE-352"]
        assert len(csrf_findings) > 0

    @pytest.mark.skip(reason="Requires test application")
    async def test_authenticated_scan(self) -> None:
        """Test scanning with authentication.

        Requires a test application with login functionality.
        """

        async def login(page):
            await page.goto("http://localhost:8000/login")
            await page.fill("#username", "testuser")
            await page.fill("#password", "testpass")
            await page.click("#login-button")
            await page.wait_for_url("http://localhost:8000/dashboard")

        scanner = DASTScanner(
            base_url="http://localhost:8000",
            auth_callback=login,
        )

        result = await scanner.scan()

        # Should successfully scan authenticated pages
        assert result.pages_scanned > 1
