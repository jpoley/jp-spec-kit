"""Tests for vulnerability detectors."""

import pytest

from specify_cli.security.dast.vulnerabilities import (
    CSRFDetector,
    SecurityHeadersTester,
    SessionTester,
    VulnerabilityResult,
    XSSDetector,
)


class TestVulnerabilityResult:
    """Test VulnerabilityResult dataclass."""

    def test_creation(self) -> None:
        """Test creating VulnerabilityResult."""
        result = VulnerabilityResult(
            type="xss",
            severity="high",
            url="https://example.com/page",
            parameter="search",
            payload="<script>alert(1)</script>",
            evidence="Payload reflected in response",
            confidence=0.9,
            remediation="Sanitize user input",
        )

        assert result.type == "xss"
        assert result.severity == "high"
        assert result.url == "https://example.com/page"
        assert result.parameter == "search"
        assert result.confidence == 0.9
        assert result.remediation == "Sanitize user input"


class TestXSSDetector:
    """Test XSS vulnerability detector."""

    def test_initialization(self) -> None:
        """Test XSSDetector initializes."""
        detector = XSSDetector()
        assert len(detector.XSS_PAYLOADS) > 0

    def test_payloads_coverage(self) -> None:
        """Test XSS payloads cover common techniques."""
        detector = XSSDetector()

        # Check for different payload types
        payloads = detector.XSS_PAYLOADS

        # Basic script tag
        assert any("<script>" in p.lower() for p in payloads)

        # Event handler
        assert any("onerror" in p or "onload" in p for p in payloads)

        # Breaking out of attributes
        assert any(p.startswith('"') or p.startswith("'") for p in payloads)

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires mock page object - run manually")
    async def test_test_input(self) -> None:
        """Test XSS detection on input element.

        This test is skipped by default as it requires a mock Playwright page.
        """
        # Would need to create mock page object
        # detector = XSSDetector()
        # results = await detector.test_input(mock_page, input_data)
        # assert isinstance(results, list)
        pass


class TestCSRFDetector:
    """Test CSRF vulnerability detector."""

    def test_initialization(self) -> None:
        """Test CSRFDetector initializes."""
        detector = CSRFDetector()
        assert detector is not None

    @pytest.mark.asyncio
    async def test_test_cookies_missing_samesite(self) -> None:
        """Test cookie security detection."""
        detector = CSRFDetector()

        # Cookie without SameSite attribute
        cookies = [
            {
                "name": "session_id",
                "value": "abc123",
                "sameSite": "",
                "httpOnly": True,
                "secure": True,
            }
        ]

        results = await detector.test_cookies(cookies)

        assert len(results) > 0
        assert results[0].type == "csrf"
        assert "session_id" in results[0].parameter
        assert "SameSite" in results[0].evidence

    @pytest.mark.asyncio
    async def test_test_cookies_with_samesite(self) -> None:
        """Test cookie with proper SameSite attribute."""
        detector = CSRFDetector()

        # Cookie with SameSite attribute
        cookies = [
            {
                "name": "session_id",
                "value": "abc123",
                "sameSite": "Lax",
                "httpOnly": True,
                "secure": True,
            }
        ]

        results = await detector.test_cookies(cookies)

        # Should not flag cookies with proper SameSite
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_test_cookies_non_session(self) -> None:
        """Test non-session cookies are not flagged."""
        detector = CSRFDetector()

        # Non-session cookie without SameSite
        cookies = [
            {
                "name": "theme",
                "value": "dark",
                "sameSite": "",
                "httpOnly": False,
                "secure": False,
            }
        ]

        results = await detector.test_cookies(cookies)

        # Should not flag non-session cookies
        assert len(results) == 0


class TestSessionTester:
    """Test session management security tester."""

    def test_initialization(self) -> None:
        """Test SessionTester initializes."""
        tester = SessionTester()
        assert tester is not None

    @pytest.mark.asyncio
    async def test_cookie_security_missing_secure(self) -> None:
        """Test detection of insecure cookie flags."""
        tester = SessionTester()

        # Session cookie without Secure flag
        cookies = [
            {
                "name": "session_token",
                "value": "xyz789",
                "secure": False,
                "httpOnly": True,
                "sameSite": "Lax",
            }
        ]

        results = await tester.test_cookie_security(cookies)

        assert len(results) > 0
        assert results[0].type == "insecure_cookie"
        assert "Secure flag" in results[0].evidence

    @pytest.mark.asyncio
    async def test_cookie_security_missing_httponly(self) -> None:
        """Test detection of missing HttpOnly flag."""
        tester = SessionTester()

        # Session cookie without HttpOnly flag
        cookies = [
            {
                "name": "sess_id",
                "value": "xyz789",
                "secure": True,
                "httpOnly": False,
                "sameSite": "Lax",
            }
        ]

        results = await tester.test_cookie_security(cookies)

        assert len(results) > 0
        assert results[0].type == "insecure_cookie"
        assert "HttpOnly flag" in results[0].evidence

    @pytest.mark.asyncio
    async def test_cookie_security_all_flags_set(self) -> None:
        """Test properly secured cookie passes checks."""
        tester = SessionTester()

        # Properly secured session cookie
        cookies = [
            {
                "name": "session_id",
                "value": "abc123",
                "secure": True,
                "httpOnly": True,
                "sameSite": "Strict",
            }
        ]

        results = await tester.test_cookie_security(cookies)

        # Should not flag properly secured cookies
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_cookie_security_multiple_issues(self) -> None:
        """Test detection of multiple security issues."""
        tester = SessionTester()

        # Cookie with multiple issues
        cookies = [
            {
                "name": "session",
                "value": "abc",
                "secure": False,
                "httpOnly": False,
                "sameSite": "",
            }
        ]

        results = await tester.test_cookie_security(cookies)

        assert len(results) > 0
        # Should detect all three issues
        evidence = results[0].evidence
        assert "Secure" in evidence
        assert "HttpOnly" in evidence
        assert "SameSite" in evidence


class TestSecurityHeadersTester:
    """Test security headers tester."""

    def test_initialization(self) -> None:
        """Test SecurityHeadersTester initializes."""
        tester = SecurityHeadersTester()
        assert tester is not None

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires mock page/response object")
    async def test_test_headers_missing_csp(self) -> None:
        """Test detection of missing CSP header.

        This test is skipped by default as it requires mock Playwright objects.
        """
        # Would need to create mock page and response
        # tester = SecurityHeadersTester()
        # results = await tester.test_headers(mock_page)
        # assert any(r.type == "missing_csp" for r in results)
        pass


@pytest.mark.asyncio
class TestVulnerabilityDetectorIntegration:
    """Integration tests for vulnerability detectors."""

    @pytest.mark.skip(reason="Requires vulnerable test application")
    async def test_xss_detection_e2e(self) -> None:
        """End-to-end test for XSS detection.

        Requires a vulnerable test application. Skip by default.
        """
        # Would test against a known vulnerable app
        pass

    @pytest.mark.skip(reason="Requires vulnerable test application")
    async def test_csrf_detection_e2e(self) -> None:
        """End-to-end test for CSRF detection.

        Requires a vulnerable test application. Skip by default.
        """
        # Would test against a known vulnerable app
        pass
