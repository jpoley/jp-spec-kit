"""Tests for scanner orchestrator.

Tests cover:
- Scanner registration
- Parallel and sequential scanning
- Deduplication of findings
- Error handling and graceful degradation
"""

from pathlib import Path

import pytest

from specify_cli.security.adapters.base import ScannerAdapter
from specify_cli.security.models import Confidence, Finding, Location, Severity
from specify_cli.security.orchestrator import ScannerOrchestrator


class MockAdapter(ScannerAdapter):
    """Mock scanner adapter for testing."""

    def __init__(
        self,
        name: str = "mock",
        available: bool = True,
        findings: list[Finding] | None = None,
        raises: Exception | None = None,
    ):
        self._name = name
        self._available = available
        self._findings = findings or []
        self._raises = raises
        self.scan_count = 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return "1.0.0"

    def is_available(self) -> bool:
        return self._available

    def scan(self, target: Path, config: dict | None = None) -> list[Finding]:
        self.scan_count += 1
        if self._raises:
            raise self._raises
        return self._findings

    def get_install_instructions(self) -> str:
        return f"Install {self._name}"


def make_finding(
    scanner: str = "test",
    file: str = "test.py",
    line: int = 1,
    cwe: str | None = "CWE-1",
    severity: Severity = Severity.HIGH,
) -> Finding:
    """Helper to create test findings."""
    return Finding(
        id=f"{scanner.upper()}-001",
        scanner=scanner,
        severity=severity,
        title=f"{scanner} Finding",
        description="Test finding",
        location=Location(file=Path(file), line_start=line, line_end=line + 2),
        cwe_id=cwe,
    )


class TestScannerOrchestrator:
    """Tests for ScannerOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create an empty orchestrator."""
        return ScannerOrchestrator()

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create a temporary directory for scanning."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")
        return tmp_path

    def test_register_adapter(self, orchestrator):
        """Test registering a scanner adapter."""
        adapter = MockAdapter(name="semgrep")
        orchestrator.register(adapter)

        assert "semgrep" in orchestrator.list_scanners()

    def test_register_duplicate_adapter_raises(self, orchestrator):
        """Test registering duplicate adapter raises error."""
        orchestrator.register(MockAdapter(name="semgrep"))

        with pytest.raises(ValueError, match="already registered"):
            orchestrator.register(MockAdapter(name="semgrep"))

    def test_list_scanners(self, orchestrator):
        """Test listing registered scanners."""
        orchestrator.register(MockAdapter(name="scanner1"))
        orchestrator.register(MockAdapter(name="scanner2"))

        scanners = orchestrator.list_scanners()
        assert "scanner1" in scanners
        assert "scanner2" in scanners

    def test_get_adapter(self, orchestrator):
        """Test getting adapter by name."""
        adapter = MockAdapter(name="test")
        orchestrator.register(adapter)

        assert orchestrator.get_adapter("test") is adapter
        assert orchestrator.get_adapter("nonexistent") is None

    def test_scan_basic(self, orchestrator, temp_dir):
        """Test basic scanning with single adapter."""
        findings = [make_finding(scanner="semgrep")]
        adapter = MockAdapter(name="semgrep", findings=findings)
        orchestrator.register(adapter)

        results = orchestrator.scan(temp_dir)

        assert len(results) == 1
        assert results[0].scanner == "semgrep"
        assert adapter.scan_count == 1

    def test_scan_target_not_exists_raises(self, orchestrator):
        """Test scanning nonexistent path raises error."""
        orchestrator.register(MockAdapter())

        with pytest.raises(ValueError, match="does not exist"):
            orchestrator.scan(Path("/nonexistent/path"))

    def test_scan_no_adapters_raises(self, orchestrator, temp_dir):
        """Test scanning with no adapters raises error."""
        with pytest.raises(ValueError, match="No scanner adapters"):
            orchestrator.scan(temp_dir)

    def test_scan_unregistered_scanner_raises(self, orchestrator, temp_dir):
        """Test requesting unregistered scanner raises error."""
        orchestrator.register(MockAdapter(name="semgrep"))

        with pytest.raises(RuntimeError, match="not registered"):
            orchestrator.scan(temp_dir, scanners=["nonexistent"])

    def test_scan_unavailable_scanner_raises(self, orchestrator, temp_dir):
        """Test scanning with unavailable scanner raises error."""
        adapter = MockAdapter(name="semgrep", available=False)
        orchestrator.register(adapter)

        with pytest.raises(RuntimeError, match="not available"):
            orchestrator.scan(temp_dir, scanners=["semgrep"])

    def test_scan_sequential(self, orchestrator, temp_dir):
        """Test sequential scanning."""
        adapter1 = MockAdapter(
            name="scanner1", findings=[make_finding(scanner="scanner1")]
        )
        adapter2 = MockAdapter(
            name="scanner2", findings=[make_finding(scanner="scanner2")]
        )
        orchestrator.register(adapter1)
        orchestrator.register(adapter2)

        results = orchestrator.scan(temp_dir, parallel=False, deduplicate=False)

        assert len(results) == 2
        assert adapter1.scan_count == 1
        assert adapter2.scan_count == 1

    def test_scan_parallel(self, orchestrator, temp_dir):
        """Test parallel scanning."""
        adapter1 = MockAdapter(
            name="scanner1", findings=[make_finding(scanner="scanner1")]
        )
        adapter2 = MockAdapter(
            name="scanner2", findings=[make_finding(scanner="scanner2")]
        )
        orchestrator.register(adapter1)
        orchestrator.register(adapter2)

        results = orchestrator.scan(temp_dir, parallel=True, deduplicate=False)

        assert len(results) == 2
        assert adapter1.scan_count == 1
        assert adapter2.scan_count == 1

    def test_scan_with_config(self, orchestrator, temp_dir):
        """Test scanning with scanner-specific config."""

        class ConfigCapturingAdapter(MockAdapter):
            captured_config = None

            def scan(self, target: Path, config: dict | None = None) -> list[Finding]:
                ConfigCapturingAdapter.captured_config = config
                return []

        adapter = ConfigCapturingAdapter(name="test")
        orchestrator.register(adapter)

        config = {"test": {"rules": ["auto"], "timeout": 300}}
        orchestrator.scan(temp_dir, config=config)

        assert ConfigCapturingAdapter.captured_config == {
            "rules": ["auto"],
            "timeout": 300,
        }

    def test_scan_graceful_degradation_sequential(self, orchestrator, temp_dir, capsys):
        """Test sequential scan continues after adapter failure."""
        adapter1 = MockAdapter(name="failing", raises=RuntimeError("Scan failed"))
        adapter2 = MockAdapter(
            name="working", findings=[make_finding(scanner="working")]
        )
        orchestrator.register(adapter1)
        orchestrator.register(adapter2)

        results = orchestrator.scan(temp_dir, parallel=False, deduplicate=False)

        # Should have results from working adapter
        assert len(results) == 1
        assert results[0].scanner == "working"

        # Warning should be printed
        captured = capsys.readouterr()
        assert "failing scan failed" in captured.out

    def test_scan_graceful_degradation_parallel(self, orchestrator, temp_dir, capsys):
        """Test parallel scan continues after adapter failure."""
        adapter1 = MockAdapter(name="failing", raises=RuntimeError("Scan failed"))
        adapter2 = MockAdapter(
            name="working", findings=[make_finding(scanner="working")]
        )
        orchestrator.register(adapter1)
        orchestrator.register(adapter2)

        results = orchestrator.scan(temp_dir, parallel=True, deduplicate=False)

        # Should have results from working adapter
        assert len(results) == 1
        assert results[0].scanner == "working"


class TestDeduplication:
    """Tests for finding deduplication."""

    @pytest.fixture
    def orchestrator(self):
        return ScannerOrchestrator()

    @pytest.fixture
    def temp_dir(self, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")
        return tmp_path

    def test_deduplicate_removes_duplicates(self, orchestrator):
        """Test deduplication removes findings with same fingerprint."""
        # Two findings with same location and CWE
        finding1 = make_finding(
            scanner="semgrep", file="test.py", line=10, cwe="CWE-89"
        )
        finding2 = make_finding(scanner="codeql", file="test.py", line=10, cwe="CWE-89")

        results = orchestrator.deduplicate([finding1, finding2])

        assert len(results) == 1

    def test_deduplicate_keeps_unique_findings(self, orchestrator):
        """Test deduplication keeps findings with different fingerprints."""
        finding1 = make_finding(
            scanner="semgrep", file="test.py", line=10, cwe="CWE-89"
        )
        finding2 = make_finding(
            scanner="semgrep", file="other.py", line=20, cwe="CWE-79"
        )

        results = orchestrator.deduplicate([finding1, finding2])

        assert len(results) == 2

    def test_deduplicate_merges_metadata(self, orchestrator):
        """Test deduplication merges metadata from duplicates."""
        finding1 = make_finding(
            scanner="semgrep", file="test.py", line=10, cwe="CWE-89"
        )
        finding1.references = ["https://semgrep.example.com"]
        finding1.confidence = Confidence.MEDIUM

        finding2 = make_finding(scanner="codeql", file="test.py", line=10, cwe="CWE-89")
        finding2.references = ["https://codeql.example.com"]
        finding2.confidence = Confidence.MEDIUM

        results = orchestrator.deduplicate([finding1, finding2])

        assert len(results) == 1
        # References should be merged
        assert len(results[0].references) == 2
        # Confidence should increase
        assert results[0].confidence == Confidence.HIGH
        # Merged scanners should be tracked
        assert "codeql" in results[0].metadata.get("merged_scanners", [])

    def test_scan_with_deduplication(self, orchestrator, temp_dir):
        """Test scan applies deduplication by default."""
        # Both scanners find the same vulnerability
        same_finding1 = make_finding(
            scanner="scanner1", file="test.py", line=10, cwe="CWE-89"
        )
        same_finding2 = make_finding(
            scanner="scanner2", file="test.py", line=10, cwe="CWE-89"
        )

        adapter1 = MockAdapter(name="scanner1", findings=[same_finding1])
        adapter2 = MockAdapter(name="scanner2", findings=[same_finding2])
        orchestrator.register(adapter1)
        orchestrator.register(adapter2)

        # Deduplication is on by default
        results = orchestrator.scan(temp_dir)

        assert len(results) == 1

    def test_scan_without_deduplication(self, orchestrator, temp_dir):
        """Test scan can skip deduplication."""
        same_finding1 = make_finding(
            scanner="scanner1", file="test.py", line=10, cwe="CWE-89"
        )
        same_finding2 = make_finding(
            scanner="scanner2", file="test.py", line=10, cwe="CWE-89"
        )

        adapter1 = MockAdapter(name="scanner1", findings=[same_finding1])
        adapter2 = MockAdapter(name="scanner2", findings=[same_finding2])
        orchestrator.register(adapter1)
        orchestrator.register(adapter2)

        results = orchestrator.scan(temp_dir, deduplicate=False)

        assert len(results) == 2


class TestOrchestratorWithInitialAdapters:
    """Tests for orchestrator initialization with adapters."""

    def test_init_with_adapters(self, tmp_path):
        """Test orchestrator can be initialized with adapters."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        adapter1 = MockAdapter(
            name="scanner1", findings=[make_finding(scanner="scanner1")]
        )
        adapter2 = MockAdapter(
            name="scanner2", findings=[make_finding(scanner="scanner2")]
        )

        orchestrator = ScannerOrchestrator(adapters=[adapter1, adapter2])

        assert len(orchestrator.list_scanners()) == 2
        assert "scanner1" in orchestrator.list_scanners()
        assert "scanner2" in orchestrator.list_scanners()

    def test_init_empty(self):
        """Test orchestrator can be initialized empty."""
        orchestrator = ScannerOrchestrator()

        assert len(orchestrator.list_scanners()) == 0


class TestScannerSelection:
    """Tests for scanner selection during scan."""

    @pytest.fixture
    def orchestrator_with_scanners(self, tmp_path):
        """Create orchestrator with multiple scanners."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        orchestrator = ScannerOrchestrator()
        orchestrator.register(
            MockAdapter(
                name="scanner1",
                findings=[make_finding(scanner="scanner1", file="a.py", line=1)],
            )
        )
        orchestrator.register(
            MockAdapter(
                name="scanner2",
                findings=[make_finding(scanner="scanner2", file="b.py", line=2)],
            )
        )
        orchestrator.register(
            MockAdapter(
                name="scanner3",
                findings=[make_finding(scanner="scanner3", file="c.py", line=3)],
            )
        )

        return orchestrator, tmp_path

    def test_scan_all_scanners_by_default(self, orchestrator_with_scanners):
        """Test all registered scanners are used by default."""
        orchestrator, temp_dir = orchestrator_with_scanners

        results = orchestrator.scan(temp_dir, deduplicate=False)

        scanners_used = {f.scanner for f in results}
        assert scanners_used == {"scanner1", "scanner2", "scanner3"}

    def test_scan_specific_scanners(self, orchestrator_with_scanners):
        """Test only specified scanners are used."""
        orchestrator, temp_dir = orchestrator_with_scanners

        results = orchestrator.scan(
            temp_dir, scanners=["scanner1", "scanner3"], deduplicate=False
        )

        scanners_used = {f.scanner for f in results}
        assert scanners_used == {"scanner1", "scanner3"}
        assert "scanner2" not in scanners_used

    def test_scan_single_scanner(self, orchestrator_with_scanners):
        """Test scanning with single scanner."""
        orchestrator, temp_dir = orchestrator_with_scanners

        results = orchestrator.scan(temp_dir, scanners=["scanner2"], deduplicate=False)

        assert len(results) == 1
        assert results[0].scanner == "scanner2"
