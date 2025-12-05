"""Main DAST scanner orchestrating crawl and vulnerability detection.

This module provides the primary DASTScanner class that coordinates web crawling
and vulnerability detection to produce security findings.
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urljoin

from specify_cli.security.dast.crawler import CrawlConfig, PlaywrightCrawler
from specify_cli.security.dast.vulnerabilities import (
    CSRFDetector,
    SecurityHeadersTester,
    SessionTester,
    VulnerabilityResult,
    XSSDetector,
)
from specify_cli.security.models import Confidence, Finding, Location, Severity


@dataclass
class DASTScanResult:
    """Results from DAST scan.

    Attributes:
        vulnerabilities: List of detected vulnerabilities
        findings: List of findings in Unified Finding Format
        pages_scanned: Number of pages crawled
        forms_tested: Number of forms tested
        duration_seconds: Total scan duration
        errors: List of errors encountered during scan
    """

    vulnerabilities: list[VulnerabilityResult]
    findings: list[Finding]
    pages_scanned: int
    forms_tested: int
    duration_seconds: float
    errors: list[str] = field(default_factory=list)


class DASTScanner:
    """Dynamic Application Security Testing scanner.

    This scanner performs comprehensive web application security testing by:
    1. Crawling the application to discover pages and forms
    2. Testing for common vulnerabilities (XSS, CSRF, etc.)
    3. Validating security headers and cookies
    4. Converting results to Unified Finding Format

    Example:
        >>> async def login(page):
        ...     await page.fill("#username", "test@example.com")
        ...     await page.fill("#password", "password")
        ...     await page.click("#login-button")
        ...
        >>> scanner = DASTScanner(
        ...     base_url="https://example.com",
        ...     auth_callback=login
        ... )
        >>> result = await scanner.scan()
        >>> print(f"Found {len(result.findings)} vulnerabilities")
    """

    def __init__(
        self,
        base_url: str,
        auth_callback: Callable | None = None,
        max_depth: int = 3,
        max_pages: int = 100,
        excluded_patterns: list[str] | None = None,
    ):
        """Initialize DAST scanner.

        Args:
            base_url: Starting URL for scanning
            auth_callback: Optional async function for authentication
            max_depth: Maximum crawl depth (default: 3)
            max_pages: Maximum pages to scan (default: 100)
            excluded_patterns: URL patterns to exclude from scanning
        """
        self.base_url = base_url
        self.auth_callback = auth_callback
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.excluded_patterns = excluded_patterns or []

    async def scan(self) -> DASTScanResult:
        """Run full DAST scan.

        Returns:
            DASTScanResult with vulnerabilities and findings

        Raises:
            ImportError: If playwright is not installed
            RuntimeError: If scan fails
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError as e:
            msg = (
                "Playwright is not installed. Install with: "
                "pip install 'specify-cli[dast]' or pip install playwright && "
                "playwright install chromium"
            )
            raise ImportError(msg) from e

        # Step 1: Crawl the application
        crawler = PlaywrightCrawler(
            CrawlConfig(
                base_url=self.base_url,
                max_depth=self.max_depth,
                max_pages=self.max_pages,
                auth_callback=self.auth_callback,
                excluded_patterns=self.excluded_patterns,
            )
        )

        crawl_result = await crawler.crawl()

        # Step 2: Test for vulnerabilities
        vulnerabilities: list[VulnerabilityResult] = []
        errors = list(crawl_result.errors)

        # Initialize detectors
        xss_detector = XSSDetector()
        csrf_detector = CSRFDetector()
        session_tester = SessionTester()
        headers_tester = SecurityHeadersTester()

        # Test each page for vulnerabilities
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            # Authenticate if needed
            if self.auth_callback:
                page = await context.new_page()
                try:
                    await self.auth_callback(page)
                except Exception as e:
                    errors.append(f"Authentication failed during testing: {e}")
                finally:
                    await page.close()

            # Test forms for XSS and CSRF
            for form_data in crawl_result.forms_found:
                page = await context.new_page()
                try:
                    # Navigate to form's page
                    # Use source_url if action is empty or relative
                    form_url = (
                        form_data.action if form_data.action else form_data.source_url
                    )
                    if not form_url.startswith("http"):
                        # Relative URL - resolve against source page
                        form_url = urljoin(form_data.source_url, form_url)

                    await page.goto(form_url, timeout=30000)

                    # Test for XSS
                    xss_results = await xss_detector.test_form(page, form_data)
                    vulnerabilities.extend(xss_results)

                    # Test for CSRF
                    csrf_results = await csrf_detector.test_form(page, form_data)
                    vulnerabilities.extend(csrf_results)

                except Exception as e:
                    errors.append(f"Failed to test form {form_data.selector}: {e}")
                finally:
                    await page.close()

            # Test standalone inputs for XSS
            for input_data in crawl_result.inputs_found:
                page = await context.new_page()
                try:
                    # Use source page URL if available, otherwise fall back to base_url
                    source_url = input_data.get("source_url", self.base_url)
                    await page.goto(source_url, timeout=30000)
                    xss_results = await xss_detector.test_input(page, input_data)
                    vulnerabilities.extend(xss_results)
                except Exception as e:
                    errors.append(
                        f"Failed to test input {input_data.get('name', 'unknown')}: {e}"
                    )
                finally:
                    await page.close()

            # Test cookies for CSRF and security attributes
            csrf_cookie_results = await csrf_detector.test_cookies(crawl_result.cookies)
            vulnerabilities.extend(csrf_cookie_results)

            cookie_security_results = await session_tester.test_cookie_security(
                crawl_result.cookies
            )
            vulnerabilities.extend(cookie_security_results)

            # Test for session fixation
            session_fixation_results = await session_tester.test_session_fixation(
                context, self.base_url
            )
            vulnerabilities.extend(session_fixation_results)

            # Test security headers on main page
            page = await context.new_page()
            try:
                await page.goto(self.base_url, timeout=30000)
                headers_results = await headers_tester.test_headers(page)
                vulnerabilities.extend(headers_results)
            except Exception as e:
                errors.append(f"Failed to test security headers: {e}")
            finally:
                await page.close()

            await browser.close()

        # Step 3: Convert to Unified Finding Format
        findings = self._convert_to_findings(vulnerabilities)

        return DASTScanResult(
            vulnerabilities=vulnerabilities,
            findings=findings,
            pages_scanned=len(crawl_result.pages_visited),
            forms_tested=len(crawl_result.forms_found),
            duration_seconds=crawl_result.duration_seconds,
            errors=errors,
        )

    def scan_sync(self) -> DASTScanResult:
        """Synchronous wrapper for scan().

        Returns:
            DASTScanResult with vulnerabilities and findings

        Note:
            This is a convenience method that runs the async scan()
            in a new event loop. Prefer using scan() directly if
            you're already in an async context.
        """
        return asyncio.run(self.scan())

    def _convert_to_findings(
        self, vulnerabilities: list[VulnerabilityResult]
    ) -> list[Finding]:
        """Convert vulnerability results to Unified Finding Format.

        Args:
            vulnerabilities: List of detected vulnerabilities

        Returns:
            List of Finding objects
        """
        findings = []

        for idx, vuln in enumerate(vulnerabilities):
            # Map severity string to Severity enum
            severity_map = {
                "critical": Severity.CRITICAL,
                "high": Severity.HIGH,
                "medium": Severity.MEDIUM,
                "low": Severity.LOW,
                "info": Severity.INFO,
            }
            severity = severity_map.get(vuln.severity.lower(), Severity.MEDIUM)

            # Map confidence float to Confidence enum
            if vuln.confidence >= 0.9:
                confidence = Confidence.HIGH
            elif vuln.confidence >= 0.7:
                confidence = Confidence.MEDIUM
            else:
                confidence = Confidence.LOW

            # Map vulnerability type to CWE
            cwe_map = {
                "xss": "CWE-79",
                "csrf": "CWE-352",
                "session_fixation": "CWE-384",
                "insecure_cookie": "CWE-614",
                "clickjacking": "CWE-1021",
                "missing_csp": "CWE-1021",
                "missing_hsts": "CWE-523",
                "missing_content_type_options": "CWE-693",
            }
            cwe_id = cwe_map.get(vuln.type)

            # Create location (web vulnerabilities don't have file/line)
            # Use a placeholder path
            location = Location(
                file=Path(f"web://{vuln.url}"),
                line_start=1,
                line_end=1,
                code_snippet=vuln.evidence[:200] if vuln.evidence else "",
            )

            # Create Finding
            finding = Finding(
                id=f"DAST-{vuln.type.upper()}-{idx + 1:03d}",
                scanner="dast-playwright",
                severity=severity,
                title=self._get_title(vuln.type),
                description=vuln.evidence,
                location=location,
                cwe_id=cwe_id,
                confidence=confidence,
                remediation=vuln.remediation,
                references=self._get_references(vuln.type),
                metadata={
                    "url": vuln.url,
                    "parameter": vuln.parameter,
                    "payload": vuln.payload,
                    "vulnerability_type": vuln.type,
                },
            )

            findings.append(finding)

        return findings

    def _get_title(self, vuln_type: str) -> str:
        """Get human-readable title for vulnerability type.

        Args:
            vuln_type: Vulnerability type identifier

        Returns:
            Human-readable title
        """
        titles = {
            "xss": "Cross-Site Scripting (XSS)",
            "csrf": "Cross-Site Request Forgery (CSRF)",
            "session_fixation": "Session Fixation",
            "insecure_cookie": "Insecure Cookie Configuration",
            "clickjacking": "Clickjacking Vulnerability",
            "missing_csp": "Missing Content Security Policy",
            "missing_hsts": "Missing HTTP Strict Transport Security",
            "missing_content_type_options": "Missing X-Content-Type-Options Header",
        }
        return titles.get(vuln_type, vuln_type.replace("_", " ").title())

    def _get_references(self, vuln_type: str) -> list[str]:
        """Get reference URLs for vulnerability type.

        Args:
            vuln_type: Vulnerability type identifier

        Returns:
            List of reference URLs
        """
        references = {
            "xss": [
                "https://owasp.org/www-community/attacks/xss/",
                "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html",
            ],
            "csrf": [
                "https://owasp.org/www-community/attacks/csrf",
                "https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html",
            ],
            "session_fixation": [
                "https://owasp.org/www-community/attacks/Session_fixation",
            ],
            "insecure_cookie": [
                "https://owasp.org/www-community/controls/SecureCookieAttribute",
            ],
            "clickjacking": [
                "https://owasp.org/www-community/attacks/Clickjacking",
            ],
            "missing_csp": [
                "https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP",
            ],
            "missing_hsts": [
                "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security",
            ],
        }
        return references.get(vuln_type, [])
