"""DAST (Dynamic Application Security Testing) module.

This module provides dynamic web application security testing capabilities using
Playwright for browser automation. It supports:

1. Authenticated web crawling with session management
2. Dynamic XSS detection through payload injection
3. CSRF vulnerability detection
4. Session management testing
5. Security header validation
6. Cookie security testing

See task-222 for implementation details.
"""

from specify_cli.security.dast.crawler import (
    CrawlConfig,
    CrawlResult,
    PlaywrightCrawler,
)
from specify_cli.security.dast.scanner import DASTScanner, DASTScanResult
from specify_cli.security.dast.vulnerabilities import (
    CSRFDetector,
    SessionTester,
    VulnerabilityResult,
    XSSDetector,
)

__all__ = [
    "CrawlConfig",
    "CrawlResult",
    "CSRFDetector",
    "DASTScanner",
    "DASTScanResult",
    "PlaywrightCrawler",
    "SessionTester",
    "VulnerabilityResult",
    "XSSDetector",
]
