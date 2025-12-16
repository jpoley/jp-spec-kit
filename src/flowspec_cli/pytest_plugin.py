"""Pytest plugin for AC test markers.

This plugin registers the @pytest.mark.ac marker for marking tests
that cover specific acceptance criteria.

Usage:
    @pytest.mark.ac("AC1: Description")
    def test_feature():
        pass
"""

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers.

    Args:
        config: Pytest configuration object.
    """
    config.addinivalue_line(
        "markers",
        "ac(description): mark test as covering an acceptance criterion",
    )
