"""Base interface for security scanner adapters.

This module defines the abstract ScannerAdapter interface that all security
scanner integrations must implement. The interface provides a consistent API
for tool discovery, execution, and result normalization.

See ADR-005 for architectural decisions.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from specify_cli.security.models import Finding


class ScannerAdapter(ABC):
    """Abstract base class for security scanner integrations.

    All scanner adapters must implement this interface to integrate with
    the scanner orchestrator. The adapter pattern allows us to:

    1. Present a uniform interface to the orchestrator
    2. Hide tool-specific implementation details
    3. Translate tool outputs to Unified Finding Format
    4. Handle tool-specific installation and configuration

    Example:
        >>> class CustomAdapter(ScannerAdapter):
        ...     @property
        ...     def name(self) -> str:
        ...         return "custom-tool"
        ...
        ...     @property
        ...     def version(self) -> str:
        ...         return "1.0.0"
        ...
        ...     def is_available(self) -> bool:
        ...         return shutil.which("custom-tool") is not None
        ...
        ...     def scan(self, target: Path, config: dict | None = None) -> list[Finding]:
        ...         # Run tool and convert output to UFFormat
        ...         return findings
        ...
        ...     def get_install_instructions(self) -> str:
        ...         return "pip install custom-tool"
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Get scanner name (e.g., 'semgrep', 'codeql').

        Returns:
            Scanner identifier used in configuration and reporting.
        """
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Get scanner version string for SLSA attestation.

        Returns:
            Version string (e.g., "1.45.0").

        Raises:
            RuntimeError: If scanner is not available or version cannot be determined.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if scanner is installed and accessible.

        Returns:
            True if scanner can be executed, False otherwise.

        Note:
            This should check system PATH, virtual environment, and any
            other expected locations. It should NOT attempt installation.
        """
        pass

    @abstractmethod
    def scan(self, target: Path, config: dict | None = None) -> list[Finding]:
        """Run scanner and return findings in Unified Finding Format.

        Args:
            target: Directory or file to scan.
            config: Scanner-specific configuration options (optional).

        Returns:
            List of security findings in UFFormat.

        Raises:
            RuntimeError: If scanner is not available.
            ValueError: If target does not exist or is invalid.
            Exception: If scan execution fails.

        Note:
            The config dictionary is scanner-specific. Common keys:
            - rules: List of rule configs to use
            - exclude: List of paths to exclude
            - timeout: Scan timeout in seconds
            - severity_threshold: Minimum severity to report
        """
        pass

    @abstractmethod
    def get_install_instructions(self) -> str:
        """Get installation instructions for this scanner.

        Returns:
            Human-readable installation instructions.

        Example:
            >>> adapter = SemgrepAdapter()
            >>> if not adapter.is_available():
            ...     print(adapter.get_install_instructions())
            To install Semgrep:
              pip install semgrep
            Or visit: https://semgrep.dev/docs/getting-started/
        """
        pass
