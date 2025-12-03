"""Scanner orchestration for parallel security scanning.

This module implements the Scanner Orchestrator pattern that coordinates
execution of multiple security scanners, aggregates results, and performs
fingerprint-based deduplication.

See ADR-005 for architectural decisions.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from specify_cli.security.adapters.base import ScannerAdapter
from specify_cli.security.models import Finding


class ScannerOrchestrator:
    """Orchestrate multiple security scanners with parallel execution.

    This class coordinates the execution of multiple security scanners,
    managing their lifecycle, aggregating results, and deduplicating
    findings. Key features:

    1. Parallel execution when safe (scanner coordination)
    2. Fingerprint-based deduplication across scanners
    3. Graceful degradation (one scanner fails, others continue)
    4. Progress reporting and cancellation support

    Example:
        >>> from specify_cli.security.adapters.semgrep import SemgrepAdapter
        >>> orchestrator = ScannerOrchestrator()
        >>> orchestrator.register(SemgrepAdapter())
        >>> findings = orchestrator.scan(
        ...     target=Path("/path/to/code"),
        ...     scanners=["semgrep"],
        ...     deduplicate=True
        ... )
        >>> print(f"Found {len(findings)} unique issues")
    """

    def __init__(self, adapters: list[ScannerAdapter] | None = None):
        """Initialize scanner orchestrator.

        Args:
            adapters: Optional list of pre-configured adapters.
        """
        self._adapters: dict[str, ScannerAdapter] = {}

        if adapters:
            for adapter in adapters:
                self.register(adapter)

    def register(self, adapter: ScannerAdapter) -> None:
        """Register a scanner adapter.

        Args:
            adapter: Scanner adapter to register.

        Raises:
            ValueError: If adapter with same name already registered.

        Example:
            >>> orchestrator = ScannerOrchestrator()
            >>> orchestrator.register(SemgrepAdapter())
        """
        if adapter.name in self._adapters:
            msg = f"Adapter '{adapter.name}' is already registered"
            raise ValueError(msg)

        self._adapters[adapter.name] = adapter

    def scan(
        self,
        target: Path,
        scanners: list[str] | None = None,
        parallel: bool = True,
        deduplicate: bool = True,
        config: dict | None = None,
    ) -> list[Finding]:
        """Run scans and return aggregated findings.

        This method coordinates scanner execution, handling:
        - Scanner availability validation
        - Parallel or sequential execution
        - Result aggregation
        - Deduplication (optional)

        Args:
            target: Directory or file to scan.
            scanners: List of scanner names to use (default: all registered).
            parallel: Run scanners in parallel when safe (default: True).
            deduplicate: Remove duplicate findings by fingerprint (default: True).
            config: Scanner-specific configuration dict (optional).

        Returns:
            List of findings, optionally deduplicated.

        Raises:
            ValueError: If target does not exist or no scanners available.
            RuntimeError: If required scanner is not registered or available.

        Example:
            >>> orchestrator = ScannerOrchestrator()
            >>> orchestrator.register(SemgrepAdapter())
            >>> findings = orchestrator.scan(
            ...     target=Path("/path/to/code"),
            ...     scanners=["semgrep"],
            ...     config={"semgrep": {"rules": ["auto"]}}
            ... )
        """
        if not target.exists():
            msg = f"Target path does not exist: {target}"
            raise ValueError(msg)

        if not self._adapters:
            msg = "No scanner adapters registered"
            raise ValueError(msg)

        # Determine which scanners to use
        scanner_names = scanners or list(self._adapters.keys())

        # Validate scanner availability
        active_adapters = []
        for name in scanner_names:
            if name not in self._adapters:
                msg = f"Scanner '{name}' is not registered"
                raise RuntimeError(msg)

            adapter = self._adapters[name]
            if not adapter.is_available():
                msg = f"Scanner '{name}' is not available. {adapter.get_install_instructions()}"
                raise RuntimeError(msg)

            active_adapters.append(adapter)

        if not active_adapters:
            msg = "No available scanners found"
            raise ValueError(msg)

        # Get scanner-specific configs
        config = config or {}

        # Execute scanners
        if parallel and len(active_adapters) > 1:
            findings = self._scan_parallel(target, active_adapters, config)
        else:
            findings = self._scan_sequential(target, active_adapters, config)

        # Deduplicate if requested
        if deduplicate:
            findings = self.deduplicate(findings)

        return findings

    def _scan_sequential(
        self,
        target: Path,
        adapters: list[ScannerAdapter],
        config: dict,
    ) -> list[Finding]:
        """Run scanners sequentially.

        Args:
            target: Directory or file to scan.
            adapters: List of scanner adapters to execute.
            config: Scanner-specific configuration.

        Returns:
            Aggregated list of findings from all scanners.
        """
        findings = []

        for adapter in adapters:
            scanner_config = config.get(adapter.name, {})
            try:
                results = adapter.scan(target, scanner_config)
                findings.extend(results)
            except Exception as e:
                # Log error but continue with other scanners
                print(f"Warning: {adapter.name} scan failed: {e}")

        return findings

    def _scan_parallel(
        self,
        target: Path,
        adapters: list[ScannerAdapter],
        config: dict,
    ) -> list[Finding]:
        """Run scanners in parallel.

        Uses ThreadPoolExecutor to run multiple scanners concurrently.
        Gracefully handles individual scanner failures.

        Args:
            target: Directory or file to scan.
            adapters: List of scanner adapters to execute.
            config: Scanner-specific configuration.

        Returns:
            Aggregated list of findings from all scanners.
        """
        findings = []

        with ThreadPoolExecutor(max_workers=len(adapters)) as executor:
            # Submit all scan tasks
            futures = {}
            for adapter in adapters:
                scanner_config = config.get(adapter.name, {})
                future = executor.submit(adapter.scan, target, scanner_config)
                futures[future] = adapter

            # Collect results as they complete
            for future in as_completed(futures):
                adapter = futures[future]
                try:
                    results = future.result()
                    findings.extend(results)
                except Exception as e:
                    # Log error but continue with other scanners
                    print(f"Warning: {adapter.name} scan failed: {e}")

        return findings

    def deduplicate(self, findings: list[Finding]) -> list[Finding]:
        """Remove duplicate findings using fingerprint-based matching.

        When multiple scanners find the same vulnerability, this method:
        1. Groups findings by fingerprint (file + line + CWE)
        2. Merges duplicate findings (increases confidence)
        3. Returns deduplicated list

        Args:
            findings: List of findings from multiple scanners.

        Returns:
            Deduplicated list of findings with merged metadata.

        Example:
            >>> findings = [
            ...     Finding(..., scanner="semgrep", ...),
            ...     Finding(..., scanner="codeql", ...),  # Same vulnerability
            ... ]
            >>> unique = orchestrator.deduplicate(findings)
            >>> len(unique) < len(findings)  # Duplicates removed
            True
        """
        by_fingerprint: dict[str, Finding] = {}

        for finding in findings:
            fp = finding.fingerprint()
            if fp in by_fingerprint:
                # Merge duplicate finding (increases confidence)
                by_fingerprint[fp].merge(finding)
            else:
                by_fingerprint[fp] = finding

        return list(by_fingerprint.values())

    def list_scanners(self) -> list[str]:
        """Get list of registered scanner names.

        Returns:
            List of scanner names (e.g., ["semgrep", "codeql"]).

        Example:
            >>> orchestrator = ScannerOrchestrator()
            >>> orchestrator.register(SemgrepAdapter())
            >>> orchestrator.list_scanners()
            ['semgrep']
        """
        return list(self._adapters.keys())

    def get_adapter(self, name: str) -> ScannerAdapter | None:
        """Get registered adapter by name.

        Args:
            name: Scanner name (e.g., "semgrep").

        Returns:
            Scanner adapter if registered, None otherwise.

        Example:
            >>> orchestrator = ScannerOrchestrator()
            >>> orchestrator.register(SemgrepAdapter())
            >>> adapter = orchestrator.get_adapter("semgrep")
            >>> adapter.is_available()
            True
        """
        return self._adapters.get(name)
