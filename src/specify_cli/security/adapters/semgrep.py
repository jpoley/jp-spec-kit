"""Semgrep security scanner adapter.

This module provides integration with Semgrep, a fast static analysis tool
for finding bugs and enforcing code standards. It translates Semgrep's JSON
output to the Unified Finding Format (UFFormat).

See ADR-005 for architectural decisions.
"""

import json
import subprocess
from pathlib import Path

from specify_cli.security.adapters.base import ScannerAdapter
from specify_cli.security.adapters.discovery import ToolDiscovery
from specify_cli.security.models import Confidence, Finding, Location, Severity


class SemgrepAdapter(ScannerAdapter):
    """Adapter for Semgrep static analysis scanner.

    Semgrep is a fast, open-source static analysis tool that supports
    multiple languages and rule formats. This adapter:

    1. Discovers Semgrep installation (system/venv/cache)
    2. Runs Semgrep with appropriate configuration
    3. Parses JSON output to UFFormat
    4. Maps Semgrep severity to standard severity levels

    Config Options:
        - rules: List of rule configs (default: ["auto"] for OWASP + community)
        - exclude: List of paths to exclude (globs supported)
        - timeout: Scan timeout in seconds (default: 600)
        - max_memory: Max memory in MB (default: unlimited)

    Example:
        >>> adapter = SemgrepAdapter()
        >>> if adapter.is_available():
        ...     findings = adapter.scan(Path("/path/to/code"))
        ...     print(f"Found {len(findings)} issues")
    """

    def __init__(self, discovery: ToolDiscovery | None = None):
        """Initialize Semgrep adapter.

        Args:
            discovery: Tool discovery instance (default: creates new instance).
        """
        self._discovery = discovery or ToolDiscovery()
        self._version_cache: str | None = None

    @property
    def name(self) -> str:
        """Get scanner name.

        Returns:
            "semgrep"
        """
        return "semgrep"

    @property
    def version(self) -> str:
        """Get Semgrep version string.

        Returns:
            Version string (e.g., "1.45.0").

        Raises:
            RuntimeError: If Semgrep is not available.
        """
        if self._version_cache:
            return self._version_cache

        if not self.is_available():
            msg = "Semgrep is not available - cannot determine version"
            raise RuntimeError(msg)

        tool_path = self._discovery.find_tool("semgrep")
        try:
            result = subprocess.run(
                [str(tool_path), "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )
            # Output format: "1.45.0" or "semgrep version 1.45.0"
            version = result.stdout.strip().split()[-1]
            self._version_cache = version
            return version

        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            msg = f"Failed to get Semgrep version: {e}"
            raise RuntimeError(msg) from e

    def is_available(self) -> bool:
        """Check if Semgrep is installed and accessible.

        Returns:
            True if Semgrep can be executed, False otherwise.
        """
        return self._discovery.is_available("semgrep")

    def scan(self, target: Path, config: dict | None = None) -> list[Finding]:
        """Run Semgrep scan and return findings.

        Args:
            target: Directory or file to scan.
            config: Optional configuration dict with keys:
                - rules: List of rule configs (default: ["auto"])
                - exclude: List of paths to exclude
                - timeout: Scan timeout in seconds (default: 600)
                - max_memory: Max memory in MB

        Returns:
            List of security findings in UFFormat.

        Raises:
            RuntimeError: If Semgrep is not available.
            ValueError: If target does not exist.
            Exception: If scan execution fails.

        Example:
            >>> adapter = SemgrepAdapter()
            >>> findings = adapter.scan(
            ...     Path("/path/to/code"),
            ...     config={"rules": ["auto"], "exclude": ["tests/"]}
            ... )
        """
        if not self.is_available():
            msg = "Semgrep is not available"
            raise RuntimeError(msg)

        if not target.exists():
            msg = f"Target path does not exist: {target}"
            raise ValueError(msg)

        config = config or {}
        rules = config.get("rules", ["auto"])
        exclude = config.get("exclude", [])
        timeout = config.get("timeout", 600)

        # Build command
        tool_path = self._discovery.find_tool("semgrep")
        cmd = [
            str(tool_path),
            "--config",
            ",".join(rules),
            "--json",
            "--quiet",  # Suppress progress output
        ]

        # Add exclude patterns
        for pattern in exclude:
            cmd.extend(["--exclude", pattern])

        # Add target
        cmd.append(str(target))

        # Execute scan
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,  # Exit code 1 means findings, not error
            )

            # Exit codes: 0 = clean, 1 = findings, 2+ = error
            if result.returncode >= 2:
                msg = f"Semgrep scan failed: {result.stderr}"
                raise RuntimeError(msg)

            # Parse JSON output
            semgrep_output = json.loads(result.stdout)
            findings = [self._to_finding(f) for f in semgrep_output.get("results", [])]

            return findings

        except subprocess.TimeoutExpired as e:
            msg = f"Semgrep scan timed out after {timeout}s"
            raise RuntimeError(msg) from e
        except json.JSONDecodeError as e:
            msg = f"Failed to parse Semgrep output: {e}"
            raise RuntimeError(msg) from e

    def _to_finding(self, semgrep_finding: dict) -> Finding:
        """Convert Semgrep result to Unified Finding Format.

        Args:
            semgrep_finding: Semgrep JSON result object.

        Returns:
            Finding in UFFormat.
        """
        extra = semgrep_finding.get("extra", {})
        metadata = extra.get("metadata", {})

        # Extract CWE
        cwe_id = self._extract_cwe(semgrep_finding)

        # Map severity
        severity = self._map_severity(extra.get("severity", "INFO"))

        # Build location
        location = Location(
            file=Path(semgrep_finding["path"]),
            line_start=semgrep_finding["start"]["line"],
            line_end=semgrep_finding["end"]["line"],
            column_start=semgrep_finding["start"].get("col"),
            column_end=semgrep_finding["end"].get("col"),
            code_snippet=extra.get("lines", ""),
        )

        # Build finding
        return Finding(
            id=f"SEMGREP-{semgrep_finding['check_id']}",
            scanner="semgrep",
            severity=severity,
            title=semgrep_finding["check_id"],
            description=extra.get("message", ""),
            location=location,
            cwe_id=cwe_id,
            confidence=Confidence.HIGH,  # Semgrep has high precision
            remediation=metadata.get("remediation"),
            references=self._extract_references(metadata),
            raw_data=semgrep_finding,
        )

    def _map_severity(self, semgrep_severity: str) -> Severity:
        """Map Semgrep severity to UFFormat severity.

        Semgrep severities: ERROR, WARNING, INFO
        UFFormat severities: CRITICAL, HIGH, MEDIUM, LOW, INFO

        Args:
            semgrep_severity: Semgrep severity string.

        Returns:
            UFFormat Severity enum.
        """
        mapping = {
            "ERROR": Severity.HIGH,
            "WARNING": Severity.MEDIUM,
            "INFO": Severity.LOW,
        }
        return mapping.get(semgrep_severity.upper(), Severity.INFO)

    def _extract_cwe(self, finding: dict) -> str | None:
        """Extract CWE ID from Semgrep metadata.

        Args:
            finding: Semgrep JSON result object.

        Returns:
            CWE ID string (e.g., "CWE-89") or None.
        """
        metadata = finding.get("extra", {}).get("metadata", {})
        cwe = metadata.get("cwe")

        if isinstance(cwe, list) and cwe:
            # Take first CWE if multiple
            return cwe[0] if isinstance(cwe[0], str) else f"CWE-{cwe[0]}"
        elif isinstance(cwe, str):
            return cwe
        elif isinstance(cwe, int):
            return f"CWE-{cwe}"

        return None

    def _extract_references(self, metadata: dict) -> list[str]:
        """Extract reference URLs from Semgrep metadata.

        Args:
            metadata: Semgrep metadata dict.

        Returns:
            List of reference URLs.
        """
        refs = []

        # Common reference fields
        for key in ["references", "reference", "source", "source-rule"]:
            value = metadata.get(key)
            if isinstance(value, list):
                refs.extend([str(v) for v in value if v])
            elif isinstance(value, str) and value:
                refs.append(value)

        return refs

    def get_install_instructions(self) -> str:
        """Get installation instructions for Semgrep.

        Returns:
            Human-readable installation instructions.
        """
        return """To install Semgrep:

1. Using pip (recommended):
   pip install semgrep

2. Using Homebrew (macOS):
   brew install semgrep

3. Using Docker:
   docker pull semgrep/semgrep

For more installation options, visit:
https://semgrep.dev/docs/getting-started/
"""
