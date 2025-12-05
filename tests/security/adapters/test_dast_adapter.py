"""Tests for DAST adapter."""

import pytest
from pathlib import Path

from specify_cli.security.adapters.dast import DASTAdapter, DASTAdapterAsync


class TestDASTAdapter:
    """Test DAST adapter."""

    def test_name(self) -> None:
        """Test adapter returns correct name."""
        adapter = DASTAdapter()
        assert adapter.name == "dast-playwright"

    def test_is_available_with_playwright(self) -> None:
        """Test availability check when playwright is installed."""
        import importlib.util

        adapter = DASTAdapter()

        # This test assumes playwright is installed (dev dependency)
        # In CI/dev environments, this should be True
        # In production without DAST extras, would be False
        has_playwright = importlib.util.find_spec("playwright") is not None

        if has_playwright:
            assert adapter.is_available() is True
        else:
            assert adapter.is_available() is False

    def test_version_requires_availability(self) -> None:
        """Test version property requires playwright to be available."""
        adapter = DASTAdapter()

        if adapter.is_available():
            version = adapter.version
            assert isinstance(version, str)
            assert len(version) > 0
        else:
            with pytest.raises(RuntimeError, match="not available"):
                _ = adapter.version

    def test_get_install_instructions(self) -> None:
        """Test installation instructions are provided."""
        adapter = DASTAdapter()
        instructions = adapter.get_install_instructions()

        assert "playwright" in instructions.lower()
        assert "pip install" in instructions.lower()
        assert "chromium" in instructions.lower()

    def test_scan_requires_config(self) -> None:
        """Test scan raises error without config."""
        adapter = DASTAdapter()

        # Mock is_available to return True to bypass playwright check
        original_is_available = adapter.is_available
        adapter.is_available = lambda: True

        try:
            with pytest.raises(ValueError, match="config"):
                adapter.scan(Path("."), config=None)
        finally:
            adapter.is_available = original_is_available

    def test_scan_requires_url_in_config(self) -> None:
        """Test scan requires 'url' key in config."""
        adapter = DASTAdapter()

        # Mock is_available to return True to bypass playwright check
        original_is_available = adapter.is_available
        adapter.is_available = lambda: True

        try:
            with pytest.raises(ValueError, match="url"):
                adapter.scan(Path("."), config={})
        finally:
            adapter.is_available = original_is_available

    def test_scan_raises_if_not_available(self) -> None:
        """Test scan raises helpful error if playwright not installed."""
        adapter = DASTAdapter()

        # Mock is_available to return False
        original_is_available = adapter.is_available
        adapter.is_available = lambda: False

        try:
            with pytest.raises(RuntimeError, match="Playwright is not available"):
                adapter.scan(Path("."), config={"url": "https://example.com"})
        finally:
            adapter.is_available = original_is_available

    @pytest.mark.skip(reason="Requires playwright and network access")
    def test_scan_integration(self) -> None:
        """Integration test for scan method.

        Requires:
        - Playwright installed
        - Network access
        - Test web application

        Skip by default.
        """
        adapter = DASTAdapter()

        if not adapter.is_available():
            pytest.skip("Playwright not available")

        config = {
            "url": "http://localhost:8000",
            "max_depth": 1,
            "max_pages": 5,
        }

        findings = adapter.scan(Path("."), config)

        assert isinstance(findings, list)
        # Findings may be empty if test app has no vulnerabilities


class TestDASTAdapterAsync:
    """Test async variant of DAST adapter."""

    def test_inherits_from_base_adapter(self) -> None:
        """Test async adapter extends base adapter."""
        adapter = DASTAdapterAsync()
        assert isinstance(adapter, DASTAdapter)

    def test_name(self) -> None:
        """Test async adapter has same name."""
        adapter = DASTAdapterAsync()
        assert adapter.name == "dast-playwright"

    @pytest.mark.asyncio
    async def test_scan_async_requires_config(self) -> None:
        """Test async scan requires config."""
        adapter = DASTAdapterAsync()

        # Mock is_available to return True to bypass playwright check
        original_is_available = adapter.is_available
        adapter.is_available = lambda: True

        try:
            with pytest.raises(ValueError, match="config"):
                await adapter.scan_async(Path("."), config=None)
        finally:
            adapter.is_available = original_is_available

    @pytest.mark.asyncio
    async def test_scan_async_requires_url(self) -> None:
        """Test async scan requires url in config."""
        adapter = DASTAdapterAsync()

        # Mock is_available to return True to bypass playwright check
        original_is_available = adapter.is_available
        adapter.is_available = lambda: True

        try:
            with pytest.raises(ValueError, match="url"):
                await adapter.scan_async(Path("."), config={})
        finally:
            adapter.is_available = original_is_available

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires playwright and network access")
    async def test_scan_async_integration(self) -> None:
        """Integration test for async scan.

        Skip by default - requires test web application.
        """
        adapter = DASTAdapterAsync()

        if not adapter.is_available():
            pytest.skip("Playwright not available")

        config = {
            "url": "http://localhost:8000",
            "max_depth": 1,
            "max_pages": 5,
        }

        findings = await adapter.scan_async(Path("."), config)

        assert isinstance(findings, list)


@pytest.mark.asyncio
class TestDASTAdapterWithAuth:
    """Test DAST adapter with authentication."""

    @pytest.mark.skip(reason="Requires test application with auth")
    async def test_scan_with_auth_callback(self) -> None:
        """Test scanning with authentication callback.

        Skip by default - requires test application with login.
        """

        async def login(page):
            await page.goto("http://localhost:8000/login")
            await page.fill("#username", "test")
            await page.fill("#password", "test")
            await page.click("#login")

        adapter = DASTAdapterAsync()

        config = {
            "url": "http://localhost:8000",
            "auth_callback": login,
            "max_depth": 2,
        }

        findings = await adapter.scan_async(Path("."), config)

        assert isinstance(findings, list)
