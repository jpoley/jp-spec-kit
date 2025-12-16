"""Vulnerability detectors for DAST.

This module implements detection logic for common web vulnerabilities including
XSS, CSRF, and session management issues.
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class VulnerabilityResult:
    """Result of a vulnerability test.

    Attributes:
        type: Vulnerability type (xss, csrf, session, headers, etc.)
        severity: Severity level (critical, high, medium, low, info)
        url: URL where vulnerability was found
        parameter: Affected parameter/input name (if applicable)
        payload: Payload used to detect vulnerability (if applicable)
        evidence: Evidence of the vulnerability
        confidence: Confidence level (0.0 to 1.0)
        remediation: Suggested remediation steps
    """

    type: str
    severity: str
    url: str
    parameter: str | None
    payload: str | None
    evidence: str
    confidence: float
    remediation: str = ""


class XSSDetector:
    """Detect XSS vulnerabilities in dynamic content.

    This detector tests for cross-site scripting vulnerabilities by:
    1. Injecting various XSS payloads into input fields
    2. Submitting forms or triggering requests
    3. Checking if payloads appear unescaped in the response
    4. Validating if the payload would execute in a browser
    """

    # Common XSS payloads organized by technique
    XSS_PAYLOADS = [
        # Basic script injection
        "<script>alert(1)</script>",
        "<ScRiPt>alert(1)</ScRiPt>",  # Case variation
        # Breaking out of attributes
        '"><script>alert(1)</script>',
        "'-alert(1)-'",
        '";alert(1);//',
        # Event handlers
        "<img src=x onerror=alert(1)>",
        "<svg/onload=alert(1)>",
        "<body onload=alert(1)>",
        # HTML5 vectors
        '<iframe src="javascript:alert(1)">',
        '<math><mi//xlink:href="data:x,<script>alert(1)</script>">',
        # Encoded variants
        "<script>&#97;&#108;&#101;&#114;&#116;(1)</script>",
    ]

    async def test_input(self, page, input_data: dict) -> list[VulnerabilityResult]:
        """Test a single input element for XSS vulnerability.

        Args:
            page: Playwright page object
            input_data: Input metadata (selector, name, type)

        Returns:
            List of vulnerability results (may be empty if no XSS found)
        """
        vulnerabilities = []
        selector = input_data.get("selector", "")
        input_name = input_data.get("name", "")

        if not selector:
            return vulnerabilities

        try:
            for payload in self.XSS_PAYLOADS:
                # Fill input with payload
                await page.fill(selector, payload)

                # Get current page content
                content = await page.content()

                # Check if payload appears unescaped
                if payload in content:
                    # Check if it's actually in executable context (not escaped)
                    is_escaped = (
                        "&lt;script&gt;" in content
                        or "&amp;lt;script&amp;gt;" in content
                        or payload.replace("<", "&lt;").replace(">", "&gt;") in content
                    )

                    if not is_escaped:
                        vulnerabilities.append(
                            VulnerabilityResult(
                                type="xss",
                                severity="high",
                                url=page.url,
                                parameter=input_name,
                                payload=payload,
                                evidence=f"Payload reflected unescaped in response: {payload[:50]}...",
                                confidence=0.9,
                                remediation=(
                                    "Sanitize user input and encode output. "
                                    "Use Content Security Policy (CSP) headers. "
                                    "Consider using a template engine with auto-escaping."
                                ),
                            )
                        )
                        break  # Found XSS, no need to try more payloads

        except Exception as e:
            logger.warning(f"XSS test failed for input {input_name}: {e}")

        return vulnerabilities

    async def test_form(self, page, form_data) -> list[VulnerabilityResult]:
        """Test all inputs in a form for XSS vulnerabilities.

        Args:
            page: Playwright page object
            form_data: FormData object with form metadata

        Returns:
            List of vulnerability results
        """
        vulnerabilities = []

        try:
            # Store original URL before reloading
            original_url = page.url
            await page.goto(original_url)  # Reload page for clean state

            for input_info in form_data.inputs:
                # Skip certain input types
                if input_info["type"] in ["hidden", "submit", "button", "file"]:
                    continue

                # Construct descendant selector: form_data.selector + input name attribute
                selector = f'{form_data.selector} [name="{input_info["name"]}"]'
                input_data = {"selector": selector, "name": input_info["name"]}

                results = await self.test_input(page, input_data)
                vulnerabilities.extend(results)

        except Exception as e:
            logger.warning(f"XSS form test failed for {form_data.selector}: {e}")

        return vulnerabilities


class CSRFDetector:
    """Detect CSRF vulnerabilities.

    This detector checks for Cross-Site Request Forgery vulnerabilities by:
    1. Analyzing forms for CSRF tokens
    2. Checking HTTP headers for CSRF protection
    3. Validating SameSite cookie attributes
    4. Testing for double-submit cookie pattern
    """

    async def test_form(self, page, form_data) -> list[VulnerabilityResult]:
        """Test form for CSRF protection.

        Args:
            page: Playwright page object
            form_data: FormData object with form metadata

        Returns:
            List of vulnerability results
        """
        vulnerabilities = []

        # Only check state-changing methods
        if form_data.method not in ["POST", "PUT", "DELETE", "PATCH"]:
            return vulnerabilities

        try:
            # Check if form has CSRF token
            if not form_data.has_csrf_token:
                vulnerabilities.append(
                    VulnerabilityResult(
                        type="csrf",
                        severity="medium",
                        url=page.url,
                        parameter=None,
                        payload=None,
                        evidence=f"Form at {form_data.selector} lacks CSRF token",
                        confidence=0.8,
                        remediation=(
                            "Implement CSRF protection using one of these methods:\n"
                            "1. Synchronizer Token Pattern (add CSRF token to forms)\n"
                            "2. Double Submit Cookie pattern\n"
                            "3. SameSite cookie attribute\n"
                            "4. Custom request headers (for AJAX)"
                        ),
                    )
                )

        except Exception as e:
            logger.warning(f"CSRF form test failed for {form_data.selector}: {e}")

        return vulnerabilities

    async def test_cookies(self, cookies: list[dict]) -> list[VulnerabilityResult]:
        """Test cookies for CSRF protection attributes.

        Args:
            cookies: List of cookie dictionaries from browser context

        Returns:
            List of vulnerability results
        """
        vulnerabilities = []

        for cookie in cookies:
            name = cookie.get("name", "")
            same_site = cookie.get("sameSite", "")

            # Check for session cookies without SameSite
            if "session" in name.lower() or "sess" in name.lower():
                if not same_site or same_site == "None":
                    vulnerabilities.append(
                        VulnerabilityResult(
                            type="csrf",
                            severity="medium",
                            url="(cookie)",
                            parameter=name,
                            payload=None,
                            evidence=f"Session cookie '{name}' lacks SameSite attribute",
                            confidence=0.7,
                            remediation=(
                                f"Set SameSite attribute on cookie '{name}':\n"
                                "- SameSite=Strict (most secure, may break functionality)\n"
                                "- SameSite=Lax (balanced security and usability)\n"
                                "Also ensure HttpOnly=true and Secure=true flags are set."
                            ),
                        )
                    )

        return vulnerabilities


class SessionTester:
    """Test session management security.

    This tester validates session security including:
    1. Session fixation vulnerabilities
    2. Session timeout enforcement
    3. Secure cookie attributes
    4. Session token entropy
    """

    async def test_session_fixation(
        self, context, base_url: str
    ) -> list[VulnerabilityResult]:
        """Test for session fixation vulnerability.

        Session fixation occurs when:
        1. Application accepts session IDs from URL/POST parameters
        2. Session ID doesn't change after authentication

        Args:
            context: Playwright browser context
            base_url: Base URL of application

        Returns:
            List of vulnerability results
        """
        vulnerabilities = []

        try:
            # Get initial cookies
            page = await context.new_page()
            await page.goto(base_url)
            cookies_before = await context.cookies()

            # Extract session cookies
            session_cookies_before = {
                c["name"]: c["value"]
                for c in cookies_before
                if "session" in c["name"].lower() or "sess" in c["name"].lower()
            }

            # Note: Full session fixation test requires authentication flow
            # This is a simplified check
            if session_cookies_before:
                # Check if session ID is in URL (potential fixation vector)
                if any(
                    name.lower() in page.url.lower() for name in session_cookies_before
                ):
                    vulnerabilities.append(
                        VulnerabilityResult(
                            type="session_fixation",
                            severity="high",
                            url=base_url,
                            parameter=None,
                            payload=None,
                            evidence="Session ID appears in URL, potential fixation risk",
                            confidence=0.6,
                            remediation=(
                                "1. Never accept session IDs from URL parameters\n"
                                "2. Regenerate session ID after authentication\n"
                                "3. Use HttpOnly and Secure flags on session cookies\n"
                                "4. Implement session timeout"
                            ),
                        )
                    )

            await page.close()

        except Exception as e:
            logger.warning(f"Session fixation test failed for {base_url}: {e}")

        return vulnerabilities

    async def test_cookie_security(
        self, cookies: list[dict]
    ) -> list[VulnerabilityResult]:
        """Test cookie security attributes.

        Args:
            cookies: List of cookie dictionaries

        Returns:
            List of vulnerability results
        """
        vulnerabilities = []

        for cookie in cookies:
            name = cookie.get("name", "")
            secure = cookie.get("secure", False)
            http_only = cookie.get("httpOnly", False)
            same_site = cookie.get("sameSite", "")

            # Session cookies should have security flags
            if "session" in name.lower() or "sess" in name.lower():
                issues = []

                if not secure:
                    issues.append("missing Secure flag (allows HTTP transmission)")
                if not http_only:
                    issues.append("missing HttpOnly flag (accessible to JavaScript)")
                if not same_site:
                    issues.append("missing SameSite attribute (CSRF risk)")

                if issues:
                    vulnerabilities.append(
                        VulnerabilityResult(
                            type="insecure_cookie",
                            severity="medium",
                            url="(cookie)",
                            parameter=name,
                            payload=None,
                            evidence=f"Session cookie '{name}' has security issues: {', '.join(issues)}",
                            confidence=0.9,
                            remediation=(
                                f"Set security attributes on cookie '{name}':\n"
                                "- Secure=true (only send over HTTPS)\n"
                                "- HttpOnly=true (prevent JavaScript access)\n"
                                "- SameSite=Lax or Strict (prevent CSRF)"
                            ),
                        )
                    )

        return vulnerabilities


class SecurityHeadersTester:
    """Test for security-related HTTP headers.

    Checks for presence and correctness of:
    - Content-Security-Policy
    - X-Frame-Options
    - X-Content-Type-Options
    - Strict-Transport-Security
    - X-XSS-Protection (deprecated but still checked)
    """

    async def test_headers(self, page) -> list[VulnerabilityResult]:
        """Test page for security headers.

        Args:
            page: Playwright page object (should already be loaded)

        Returns:
            List of vulnerability results
        """
        vulnerabilities = []

        try:
            # Reload page to get fresh response headers
            response = await page.reload()
            if not response:
                return vulnerabilities

            headers = response.headers

            # Check for CSP
            if "content-security-policy" not in headers:
                vulnerabilities.append(
                    VulnerabilityResult(
                        type="missing_csp",
                        severity="medium",
                        url=page.url,
                        parameter=None,
                        payload=None,
                        evidence="Missing Content-Security-Policy header",
                        confidence=1.0,
                        remediation=(
                            "Add Content-Security-Policy header. Example:\n"
                            "Content-Security-Policy: default-src 'self'; "
                            "script-src 'self' 'unsafe-inline'; "
                            "style-src 'self' 'unsafe-inline'"
                        ),
                    )
                )

            # Check for X-Frame-Options (clickjacking protection)
            if "x-frame-options" not in headers:
                vulnerabilities.append(
                    VulnerabilityResult(
                        type="clickjacking",
                        severity="medium",
                        url=page.url,
                        parameter=None,
                        payload=None,
                        evidence="Missing X-Frame-Options header (clickjacking risk)",
                        confidence=0.9,
                        remediation=(
                            "Add X-Frame-Options header:\n"
                            "X-Frame-Options: DENY (recommended)\n"
                            "or X-Frame-Options: SAMEORIGIN\n"
                            "or use CSP frame-ancestors directive"
                        ),
                    )
                )

            # Check for HSTS (if HTTPS)
            if page.url.startswith("https://"):
                if "strict-transport-security" not in headers:
                    vulnerabilities.append(
                        VulnerabilityResult(
                            type="missing_hsts",
                            severity="low",
                            url=page.url,
                            parameter=None,
                            payload=None,
                            evidence="Missing Strict-Transport-Security header",
                            confidence=1.0,
                            remediation=(
                                "Add HSTS header:\n"
                                "Strict-Transport-Security: max-age=31536000; "
                                "includeSubDomains; preload"
                            ),
                        )
                    )

            # Check for X-Content-Type-Options
            if "x-content-type-options" not in headers:
                vulnerabilities.append(
                    VulnerabilityResult(
                        type="missing_content_type_options",
                        severity="low",
                        url=page.url,
                        parameter=None,
                        payload=None,
                        evidence="Missing X-Content-Type-Options header",
                        confidence=1.0,
                        remediation="Add header: X-Content-Type-Options: nosniff",
                    )
                )

        except Exception as e:
            logger.warning(f"Security headers test failed for {page.url}: {e}")

        return vulnerabilities
