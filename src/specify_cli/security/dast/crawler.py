"""Playwright-based web crawler for DAST.

This module implements an asynchronous web crawler using Playwright to discover
and analyze web application structure for security testing.
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


@dataclass
class CrawlConfig:
    """Configuration for web crawler.

    Attributes:
        base_url: Starting URL for crawling
        max_depth: Maximum crawl depth (default: 3)
        max_pages: Maximum pages to visit (default: 100)
        timeout_ms: Page load timeout in milliseconds (default: 30000)
        auth_callback: Optional async function for authentication
        excluded_patterns: URL patterns to exclude from crawling
        include_external: Whether to crawl external links (default: False)
    """

    base_url: str
    max_depth: int = 3
    max_pages: int = 100
    timeout_ms: int = 30000
    auth_callback: Callable | None = None
    excluded_patterns: list[str] = field(default_factory=list)
    include_external: bool = False


@dataclass
class FormData:
    """Metadata about discovered HTML form.

    Attributes:
        selector: CSS selector for the form element
        action: Form action URL
        method: HTTP method (GET, POST, etc.)
        inputs: List of input field metadata
        has_csrf_token: Whether form includes CSRF protection
        source_url: URL of the page where form was discovered
    """

    selector: str
    action: str
    method: str
    inputs: list[dict[str, str]]
    has_csrf_token: bool
    source_url: str = ""


@dataclass
class CrawlResult:
    """Results from web crawling operation.

    Attributes:
        pages_visited: List of URLs successfully crawled
        forms_found: List of discovered forms with metadata
        inputs_found: List of discovered input elements
        cookies: List of cookies observed during crawl
        duration_seconds: Total crawl duration
        errors: List of errors encountered during crawl
    """

    pages_visited: list[str]
    forms_found: list[FormData]
    inputs_found: list[dict[str, str]]
    cookies: list[dict[str, str]]
    duration_seconds: float
    errors: list[str] = field(default_factory=list)


class PlaywrightCrawler:
    """Web crawler using Playwright for dynamic page interaction.

    This crawler navigates web applications using a headless browser,
    discovering pages, forms, and inputs for security testing.

    Example:
        >>> config = CrawlConfig(base_url="https://example.com")
        >>> crawler = PlaywrightCrawler(config)
        >>> result = await crawler.crawl()
        >>> print(f"Visited {len(result.pages_visited)} pages")
    """

    def __init__(self, config: CrawlConfig):
        """Initialize crawler with configuration.

        Args:
            config: Crawl configuration settings
        """
        self.config = config
        self._visited: set[str] = set()
        self._queue: list[tuple[str, int]] = []  # (url, depth)
        self._forms: list[FormData] = []
        self._inputs: list[dict[str, str]] = []
        self._cookies: list[dict[str, str]] = []
        self._errors: list[str] = []

    async def crawl(self) -> CrawlResult:
        """Crawl the target website.

        Returns:
            CrawlResult with discovered pages, forms, and metadata

        Raises:
            ImportError: If playwright is not installed
            RuntimeError: If browser launch fails
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError as e:
            msg = (
                "Playwright is not installed. Install with: "
                "pip install 'specify-cli[dast]' or pip install playwright"
            )
            raise ImportError(msg) from e

        start_time = time.time()

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (DAST Scanner)",
                )

                # Authenticate if callback provided
                if self.config.auth_callback:
                    page = await context.new_page()
                    try:
                        await self.config.auth_callback(page)
                    except Exception as e:
                        self._errors.append(f"Authentication failed: {e}")
                    finally:
                        await page.close()

                # Initialize crawl queue
                self._queue = [(self.config.base_url, 0)]

                # Crawl pages
                while self._queue and len(self._visited) < self.config.max_pages:
                    url, depth = self._queue.pop(0)

                    if url in self._visited or depth > self.config.max_depth:
                        continue

                    if not self._should_crawl(url):
                        continue

                    await self._crawl_page(context, url, depth)

                # Extract cookies
                self._cookies = await context.cookies()

                await browser.close()

        except Exception as e:
            self._errors.append(f"Crawl failed: {e}")
            raise

        duration = time.time() - start_time

        return CrawlResult(
            pages_visited=list(self._visited),
            forms_found=self._forms,
            inputs_found=self._inputs,
            cookies=self._cookies,
            duration_seconds=duration,
            errors=self._errors,
        )

    async def _crawl_page(self, context, url: str, depth: int) -> None:
        """Crawl a single page and extract metadata.

        Args:
            context: Playwright browser context
            url: URL to crawl
            depth: Current crawl depth
        """
        page = await context.new_page()

        try:
            await page.goto(
                url, timeout=self.config.timeout_ms, wait_until="networkidle"
            )
            self._visited.add(url)

            # Extract forms (with source URL)
            forms = await self._extract_forms(page, url)
            self._forms.extend(forms)

            # Extract standalone inputs (with source URL)
            inputs = await self._extract_inputs(page, url)
            self._inputs.extend(inputs)

            # Extract links for further crawling
            links = await self._extract_links(page, url)

            # Add links to queue
            for link in links:
                if link not in self._visited:
                    self._queue.append((link, depth + 1))

        except Exception as e:
            self._errors.append(f"Failed to crawl {url}: {e}")

        finally:
            await page.close()

    async def _extract_forms(self, page, source_url: str) -> list[FormData]:
        """Extract form metadata from page.

        Args:
            page: Playwright page object
            source_url: URL of the page being crawled

        Returns:
            List of discovered forms
        """
        forms = []

        try:
            form_elements = await page.query_selector_all("form")

            for idx, form in enumerate(form_elements):
                action = await form.get_attribute("action") or ""
                method = await form.get_attribute("method") or "GET"

                # Extract input fields
                inputs = []
                input_elements = await form.query_selector_all(
                    "input, textarea, select"
                )

                for input_elem in input_elements:
                    input_type = await input_elem.get_attribute("type") or "text"
                    input_name = await input_elem.get_attribute("name") or ""
                    input_id = await input_elem.get_attribute("id") or ""

                    if input_name:  # Only include named inputs
                        inputs.append(
                            {
                                "type": input_type,
                                "name": input_name,
                                "id": input_id,
                            }
                        )

                # Check for CSRF token (case-insensitive)
                has_csrf = any(
                    "csrf" in inp["name"].lower() or "token" in inp["name"].lower()
                    for inp in inputs
                    if inp["name"]
                )

                forms.append(
                    FormData(
                        selector=f"form:nth-of-type({idx + 1})",
                        action=action,
                        method=method.upper(),
                        inputs=inputs,
                        has_csrf_token=has_csrf,
                        source_url=source_url,
                    )
                )

        except Exception as e:
            error_msg = f"Form extraction failed: {e}"
            logger.warning(error_msg)
            self._errors.append(error_msg)

        return forms

    async def _extract_inputs(self, page, source_url: str) -> list[dict[str, str]]:
        """Extract standalone input elements not in forms.

        Args:
            page: Playwright page object
            source_url: URL of the page being crawled

        Returns:
            List of input metadata dictionaries
        """
        inputs = []

        try:
            # Find inputs not inside forms
            input_elements = await page.query_selector_all(
                "input:not(form input), textarea:not(form textarea)"
            )

            for input_elem in input_elements:
                input_type = await input_elem.get_attribute("type") or "text"
                input_name = await input_elem.get_attribute("name") or ""
                input_id = await input_elem.get_attribute("id") or ""

                if input_name or input_id:
                    inputs.append(
                        {
                            "type": input_type,
                            "name": input_name,
                            "id": input_id,
                            "selector": f"#{input_id}"
                            if input_id
                            else f'[name="{input_name}"]',
                            "source_url": source_url,  # Track which page input was found on
                        }
                    )

        except Exception as e:
            error_msg = f"Input extraction failed: {e}"
            logger.warning(error_msg)
            self._errors.append(error_msg)

        return inputs

    async def _extract_links(self, page, current_url: str) -> list[str]:
        """Extract valid links from page for crawling.

        Args:
            page: Playwright page object
            current_url: Current page URL for resolving relative links

        Returns:
            List of absolute URLs to crawl
        """
        links = []

        try:
            link_elements = await page.query_selector_all("a[href]")

            for link_elem in link_elements:
                href = await link_elem.get_attribute("href")
                if not href:
                    continue

                # Convert to absolute URL
                absolute_url = urljoin(current_url, href)

                # Remove fragment
                absolute_url = absolute_url.split("#")[0]

                if self._should_crawl(absolute_url):
                    links.append(absolute_url)

        except Exception as e:
            error_msg = f"Link extraction failed: {e}"
            logger.warning(error_msg)
            self._errors.append(error_msg)

        return links

    def _should_crawl(self, url: str) -> bool:
        """Check if URL should be crawled based on configuration.

        Args:
            url: URL to check

        Returns:
            True if URL should be crawled, False otherwise
        """
        parsed = urlparse(url)
        base_parsed = urlparse(self.config.base_url)

        # Check if same origin (unless external links allowed)
        if not self.config.include_external:
            if parsed.netloc != base_parsed.netloc:
                return False

        # Check excluded patterns
        for pattern in self.config.excluded_patterns:
            if pattern in url:
                return False

        # Skip common non-HTML resources
        excluded_extensions = [
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".svg",
            ".css",
            ".js",
            ".ico",
            ".woff",
            ".woff2",
            ".ttf",
            ".zip",
            ".tar",
            ".gz",
            ".mp4",
            ".mp3",
            ".avi",
        ]
        if any(url.lower().endswith(ext) for ext in excluded_extensions):
            return False

        return True
