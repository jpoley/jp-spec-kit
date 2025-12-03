"""Base exporter interface for security findings.

This module defines the abstract base class that all exporters must implement.
"""

from abc import ABC, abstractmethod
from typing import Any

from specify_cli.security.models import Finding


class BaseExporter(ABC):
    """Abstract base class for security finding exporters.

    All exporters must implement the export() method to convert
    findings to their target format.
    """

    @abstractmethod
    def export(self, findings: list[Finding]) -> Any:
        """Export findings to target format.

        Args:
            findings: List of security findings in UFFormat

        Returns:
            Exported data in target format (type varies by implementation)
        """
        ...
