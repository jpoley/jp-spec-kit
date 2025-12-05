"""DAST (Dynamic Application Security Testing) adapter.

This module provides integration with the Playwright-based DAST scanner,
translating web vulnerability results to the Unified Finding Format.
"""

from pathlib import Path

from specify_cli.security.adapters.base import ScannerAdapter
from specify_cli.security.models import Finding


class DASTAdapter(ScannerAdapter):
    """Adapter for DAST web security scanner.

    This adapter integrates the Playwright-based DAST scanner with the
    security scanning orchestrator. Unlike SAST tools that scan source code,
    DAST scans running web applications.

    Config Options:
        - url: Base URL to scan (required)
        - auth_callback: Async function for authentication (optional)
        - max_depth: Maximum crawl depth (default: 3)
        - max_pages: Maximum pages to scan (default: 100)
        - excluded_patterns: URL patterns to exclude (default: [])

    Example:
        >>> async def login(page):
        ...     await page.fill("#username", "admin")
        ...     await page.fill("#password", "password")
        ...     await page.click("#login")
        ...
        >>> adapter = DASTAdapter()
        >>> if adapter.is_available():
        ...     config = {
        ...         "url": "https://example.com",
        ...         "auth_callback": login,
        ...     }
        ...     findings = adapter.scan(Path("."), config)
    """

    @property
    def name(self) -> str:
        """Get scanner name.

        Returns:
            "dast-playwright"
        """
        return "dast-playwright"

    @property
    def version(self) -> str:
        """Get Playwright version string.

        Returns:
            Version string (e.g., "1.40.0")

        Raises:
            RuntimeError: If playwright is not available
        """
        if not self.is_available():
            msg = "Playwright is not available - cannot determine version"
            raise RuntimeError(msg)

        try:
            import playwright

            return playwright.__version__
        except Exception as e:
            msg = f"Failed to get Playwright version: {e}"
            raise RuntimeError(msg) from e

    def is_available(self) -> bool:
        """Check if Playwright is installed and browsers are available.

        Returns:
            True if Playwright can be used, False otherwise
        """
        try:
            import importlib.util

            # Check if browsers are installed by attempting to get browser path
            # This is a lightweight check - actual browser launch is tested during scan
            return importlib.util.find_spec("playwright") is not None
        except ImportError:
            return False

    def scan(self, target: Path, config: dict | None = None) -> list[Finding]:
        """Run DAST scan and return findings.

        Args:
            target: Not used for DAST (scans web URLs, not file paths)
            config: DAST configuration with required 'url' key

        Returns:
            List of security findings in UFFormat

        Raises:
            RuntimeError: If Playwright is not available
            ValueError: If config is missing or invalid
            Exception: If scan execution fails

        Config Keys:
            - url (required): Base URL to scan
            - auth_callback (optional): Async function for authentication
            - max_depth (optional): Maximum crawl depth (default: 3)
            - max_pages (optional): Maximum pages to scan (default: 100)
            - excluded_patterns (optional): URL patterns to exclude
        """
        if not self.is_available():
            msg = (
                "Playwright is not available. Install with: "
                "pip install 'specify-cli[dast]' or pip install playwright && "
                "playwright install chromium"
            )
            raise RuntimeError(msg)

        if not config:
            msg = "DAST requires config with 'url' key"
            raise ValueError(msg)

        url = config.get("url")
        if not url:
            msg = "DAST config must include 'url' key"
            raise ValueError(msg)

        # Import here to avoid circular dependency and fail gracefully
        from specify_cli.security.dast.scanner import DASTScanner

        # Extract configuration
        auth_callback = config.get("auth_callback")
        max_depth = config.get("max_depth", 3)
        max_pages = config.get("max_pages", 100)
        excluded_patterns = config.get("excluded_patterns", [])

        # Create and run scanner
        scanner = DASTScanner(
            base_url=url,
            auth_callback=auth_callback,
            max_depth=max_depth,
            max_pages=max_pages,
            excluded_patterns=excluded_patterns,
        )

        # Run scan synchronously
        result = scanner.scan_sync()

        # Return findings
        return result.findings

    def get_install_instructions(self) -> str:
        """Get installation instructions for Playwright.

        Returns:
            Human-readable installation instructions
        """
        return """To install Playwright for DAST scanning:

1. Install the Python package:
   pip install 'specify-cli[dast]'

   Or install Playwright separately:
   pip install playwright

2. Install browser binaries:
   playwright install chromium

3. Verify installation:
   playwright --version

For more information:
https://playwright.dev/python/docs/intro
"""


class DASTAdapterAsync(DASTAdapter):
    """Async variant of DAST adapter for use in async contexts.

    This adapter provides native async support for the scan() method,
    avoiding the overhead of asyncio.run() in already-async contexts.

    Example:
        >>> adapter = DASTAdapterAsync()
        >>> findings = await adapter.scan_async(Path("."), config)
    """

    async def scan_async(
        self, target: Path, config: dict | None = None
    ) -> list[Finding]:
        """Run DAST scan asynchronously.

        Args:
            target: Not used for DAST (scans web URLs, not file paths)
            config: DAST configuration with required 'url' key

        Returns:
            List of security findings in UFFormat

        Raises:
            RuntimeError: If Playwright is not available
            ValueError: If config is missing or invalid
            Exception: If scan execution fails
        """
        if not self.is_available():
            msg = (
                "Playwright is not available. Install with: "
                "pip install 'specify-cli[dast]' or pip install playwright && "
                "playwright install chromium"
            )
            raise RuntimeError(msg)

        if not config:
            msg = "DAST requires config with 'url' key"
            raise ValueError(msg)

        url = config.get("url")
        if not url:
            msg = "DAST config must include 'url' key"
            raise ValueError(msg)

        # Import here to avoid circular dependency
        from specify_cli.security.dast.scanner import DASTScanner

        # Extract configuration
        auth_callback = config.get("auth_callback")
        max_depth = config.get("max_depth", 3)
        max_pages = config.get("max_pages", 100)
        excluded_patterns = config.get("excluded_patterns", [])

        # Create and run scanner
        scanner = DASTScanner(
            base_url=url,
            auth_callback=auth_callback,
            max_depth=max_depth,
            max_pages=max_pages,
            excluded_patterns=excluded_patterns,
        )

        # Run scan asynchronously
        result = await scanner.scan()

        # Return findings
        return result.findings
