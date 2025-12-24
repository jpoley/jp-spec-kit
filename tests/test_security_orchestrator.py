"""Tests for ScannerOrchestrator.

This module tests:
1. Scanner registration and lifecycle
2. Parallel and sequential execution
3. Fingerprint-based deduplication
4. Error handling and graceful degradation
"""

from pathlib import Path
from unittest.mock import Mock

import pytest

from flowspec_cli.security.orchestrator import ScannerOrchestrator
from flowspec_cli.security.adapters.base import ScannerAdapter
from flowspec_cli.security.models import (
    Finding,
    Location,
    Severity,
    Confidence,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_finding():
    """Create a sample finding for testing."""
    return Finding(
        id="TEST-001",
        scanner="test-scanner",
        severity=Severity.HIGH,
        title="Test Vulnerability",
        description="Test description",
        location=Location(
            file=Path("test.py"),
            line_start=10,
            line_end=12,
        ),
        cwe_id="CWE-89",
        confidence=Confidence.HIGH,
    )


@pytest.fixture
def mock_adapter():
    """Create a mock scanner adapter."""
    adapter = Mock(spec=ScannerAdapter)
    adapter.name = "test-scanner"
    adapter.version = "1.0.0"
    adapter.is_available.return_value = True
    adapter.scan.return_value = []
    return adapter


@pytest.fixture
def orchestrator():
    """Create a fresh orchestrator instance."""
    return ScannerOrchestrator()


# ============================================================================
# ScannerOrchestrator Tests
# ============================================================================


class TestOrchestratorRegistration:
    """Test adapter registration."""

    def test_register_adapter(self, orchestrator, mock_adapter):
        """Test registering a scanner adapter."""
        # Act
        orchestrator.register(mock_adapter)

        # Assert
        assert "test-scanner" in orchestrator.list_scanners()
        assert orchestrator.get_adapter("test-scanner") == mock_adapter

    def test_register_duplicate_raises_error(self, orchestrator, mock_adapter):
        """Test that registering duplicate adapter raises ValueError."""
        # Arrange
        orchestrator.register(mock_adapter)

        # Act & Assert
        with pytest.raises(ValueError, match="already registered"):
            orchestrator.register(mock_adapter)

    def test_register_multiple_adapters(self, orchestrator):
        """Test registering multiple adapters."""
        # Arrange
        adapter1 = Mock(spec=ScannerAdapter)
        adapter1.name = "scanner1"

        adapter2 = Mock(spec=ScannerAdapter)
        adapter2.name = "scanner2"

        # Act
        orchestrator.register(adapter1)
        orchestrator.register(adapter2)

        # Assert
        scanners = orchestrator.list_scanners()
        assert len(scanners) == 2
        assert "scanner1" in scanners
        assert "scanner2" in scanners

    def test_init_with_adapters(self):
        """Test initializing orchestrator with adapters list."""
        # Arrange
        adapter = Mock(spec=ScannerAdapter)
        adapter.name = "scanner1"

        # Act
        orchestrator = ScannerOrchestrator(adapters=[adapter])

        # Assert
        assert "scanner1" in orchestrator.list_scanners()


class TestOrchestratorScan:
    """Test scan execution."""

    def test_scan_success(self, orchestrator, mock_adapter, sample_finding, tmp_path):
        """Test successful scan execution."""
        # Arrange
        mock_adapter.scan.return_value = [sample_finding]
        orchestrator.register(mock_adapter)

        target = tmp_path / "src"
        target.mkdir()

        # Act
        findings = orchestrator.scan(target=target)

        # Assert
        assert len(findings) == 1
        assert findings[0].id == "TEST-001"
        mock_adapter.scan.assert_called_once_with(target, {})

    def test_scan_specific_scanner(self, orchestrator, tmp_path):
        """Test scanning with specific scanner."""
        # Arrange
        adapter1 = Mock(spec=ScannerAdapter)
        adapter1.name = "scanner1"
        adapter1.is_available.return_value = True
        adapter1.scan.return_value = []

        adapter2 = Mock(spec=ScannerAdapter)
        adapter2.name = "scanner2"
        adapter2.is_available.return_value = True
        adapter2.scan.return_value = []

        orchestrator.register(adapter1)
        orchestrator.register(adapter2)

        target = tmp_path / "src"
        target.mkdir()

        # Act
        orchestrator.scan(target=target, scanners=["scanner1"])

        # Assert
        adapter1.scan.assert_called_once()
        adapter2.scan.assert_not_called()

    def test_scan_raises_on_missing_target(self, orchestrator, mock_adapter):
        """Test that scan raises ValueError when target doesn't exist."""
        # Arrange
        orchestrator.register(mock_adapter)
        target = Path("/nonexistent/path")

        # Act & Assert
        with pytest.raises(ValueError, match="Target path does not exist"):
            orchestrator.scan(target=target)

    def test_scan_raises_on_no_adapters(self):
        """Test that scan raises ValueError when no adapters registered."""
        # Arrange
        orchestrator = ScannerOrchestrator()

        # Act & Assert
        with pytest.raises(ValueError, match="No scanner adapters registered"):
            orchestrator.scan(target=Path("."))

    def test_scan_raises_on_unregistered_scanner(self, tmp_path):
        """Test that scan raises RuntimeError for unregistered scanner."""
        # Arrange
        orchestrator = ScannerOrchestrator()
        mock_adapter = Mock(spec=ScannerAdapter)
        mock_adapter.name = "test-scanner"
        mock_adapter.is_available.return_value = True
        orchestrator.register(mock_adapter)

        target = tmp_path / "src"
        target.mkdir()

        # Act & Assert
        with pytest.raises(RuntimeError):
            orchestrator.scan(target=target, scanners=["nonexistent"])

    def test_scan_raises_on_unavailable_scanner(self, orchestrator, tmp_path):
        """Test that scan raises RuntimeError when scanner is unavailable."""
        # Arrange
        adapter = Mock(spec=ScannerAdapter)
        adapter.name = "unavailable-scanner"
        adapter.is_available.return_value = False
        adapter.get_install_instructions.return_value = "Install instructions"

        orchestrator.register(adapter)

        target = tmp_path / "src"
        target.mkdir()

        # Act & Assert
        with pytest.raises(RuntimeError, match="not available"):
            orchestrator.scan(target=target)

    def test_scan_with_config(self, orchestrator, mock_adapter, tmp_path):
        """Test scan with scanner-specific configuration."""
        # Arrange
        mock_adapter.scan.return_value = []
        orchestrator.register(mock_adapter)

        target = tmp_path / "src"
        target.mkdir()

        config = {"test-scanner": {"rules": ["auto"], "exclude": ["tests/"]}}

        # Act
        orchestrator.scan(target=target, config=config)

        # Assert
        call_args = mock_adapter.scan.call_args
        assert call_args[0][0] == target
        assert call_args[0][1] == config["test-scanner"]


class TestSequentialExecution:
    """Test sequential scanner execution."""

    def test_sequential_execution(self, orchestrator, sample_finding, tmp_path):
        """Test sequential execution of multiple scanners."""
        # Arrange
        finding1 = Finding(
            id="SCANNER1-001",
            scanner="scanner1",
            severity=Severity.HIGH,
            title="Finding 1",
            description="Test",
            location=Location(file=Path("test.py"), line_start=1, line_end=1),
        )

        finding2 = Finding(
            id="SCANNER2-001",
            scanner="scanner2",
            severity=Severity.MEDIUM,
            title="Finding 2",
            description="Test",
            location=Location(file=Path("test.py"), line_start=10, line_end=10),
        )

        adapter1 = Mock(spec=ScannerAdapter)
        adapter1.name = "scanner1"
        adapter1.is_available.return_value = True
        adapter1.scan.return_value = [finding1]

        adapter2 = Mock(spec=ScannerAdapter)
        adapter2.name = "scanner2"
        adapter2.is_available.return_value = True
        adapter2.scan.return_value = [finding2]

        orchestrator.register(adapter1)
        orchestrator.register(adapter2)

        target = tmp_path / "src"
        target.mkdir()

        # Act
        findings = orchestrator.scan(target=target, parallel=False, deduplicate=False)

        # Assert
        assert len(findings) == 2
        assert findings[0].scanner == "scanner1"
        assert findings[1].scanner == "scanner2"

    def test_sequential_continues_on_error(self, orchestrator, tmp_path):
        """Test that sequential execution continues when one scanner fails."""
        # Arrange
        # Create a finding with scanner name matching adapter2
        scanner2_finding = Finding(
            id="SCANNER2-001",
            scanner="scanner2",
            severity=Severity.HIGH,
            title="Scanner 2 Finding",
            description="Test finding from scanner2",
            location=Location(file=Path("test.py"), line_start=10, line_end=12),
        )

        adapter1 = Mock(spec=ScannerAdapter)
        adapter1.name = "scanner1"
        adapter1.is_available.return_value = True
        adapter1.scan.side_effect = RuntimeError("Scanner 1 failed")

        adapter2 = Mock(spec=ScannerAdapter)
        adapter2.name = "scanner2"
        adapter2.is_available.return_value = True
        adapter2.scan.return_value = [scanner2_finding]

        orchestrator.register(adapter1)
        orchestrator.register(adapter2)

        target = tmp_path / "src"
        target.mkdir()

        # Act
        findings = orchestrator.scan(target=target, parallel=False)

        # Assert - scanner2 results still returned
        assert len(findings) == 1
        assert findings[0].scanner == "scanner2"


class TestParallelExecution:
    """Test parallel scanner execution."""

    def test_parallel_execution(self, orchestrator, tmp_path):
        """Test parallel execution of multiple scanners."""
        # Arrange
        finding1 = Finding(
            id="SCANNER1-001",
            scanner="scanner1",
            severity=Severity.HIGH,
            title="Finding 1",
            description="Test",
            location=Location(file=Path("test.py"), line_start=1, line_end=1),
        )

        finding2 = Finding(
            id="SCANNER2-001",
            scanner="scanner2",
            severity=Severity.MEDIUM,
            title="Finding 2",
            description="Test",
            location=Location(file=Path("test.py"), line_start=10, line_end=10),
        )

        adapter1 = Mock(spec=ScannerAdapter)
        adapter1.name = "scanner1"
        adapter1.is_available.return_value = True
        adapter1.scan.return_value = [finding1]

        adapter2 = Mock(spec=ScannerAdapter)
        adapter2.name = "scanner2"
        adapter2.is_available.return_value = True
        adapter2.scan.return_value = [finding2]

        orchestrator.register(adapter1)
        orchestrator.register(adapter2)

        target = tmp_path / "src"
        target.mkdir()

        # Act
        findings = orchestrator.scan(target=target, parallel=True, deduplicate=False)

        # Assert
        assert len(findings) == 2
        scanner_names = {f.scanner for f in findings}
        assert scanner_names == {"scanner1", "scanner2"}

    def test_parallel_continues_on_error(self, orchestrator, tmp_path):
        """Test that parallel execution continues when one scanner fails."""
        # Arrange
        # Create a finding with scanner name matching adapter2
        scanner2_finding = Finding(
            id="SCANNER2-001",
            scanner="scanner2",
            severity=Severity.HIGH,
            title="Scanner 2 Finding",
            description="Test finding from scanner2",
            location=Location(file=Path("test.py"), line_start=10, line_end=12),
        )

        adapter1 = Mock(spec=ScannerAdapter)
        adapter1.name = "scanner1"
        adapter1.is_available.return_value = True
        adapter1.scan.side_effect = RuntimeError("Scanner 1 failed")

        adapter2 = Mock(spec=ScannerAdapter)
        adapter2.name = "scanner2"
        adapter2.is_available.return_value = True
        adapter2.scan.return_value = [scanner2_finding]

        orchestrator.register(adapter1)
        orchestrator.register(adapter2)

        target = tmp_path / "src"
        target.mkdir()

        # Act
        findings = orchestrator.scan(target=target, parallel=True)

        # Assert - scanner2 results still returned
        assert len(findings) == 1
        assert findings[0].scanner == "scanner2"

    def test_single_scanner_uses_sequential(self, orchestrator, mock_adapter, tmp_path):
        """Test that single scanner doesn't use parallel execution."""
        # Arrange
        mock_adapter.scan.return_value = []
        orchestrator.register(mock_adapter)

        target = tmp_path / "src"
        target.mkdir()

        # Act
        orchestrator.scan(target=target, parallel=True)

        # Assert - scan was called (sequential path used)
        mock_adapter.scan.assert_called_once()


class TestDeduplication:
    """Test finding deduplication."""

    def test_deduplicate_identical_findings(self, orchestrator):
        """Test deduplication of identical findings from different scanners."""
        # Arrange
        location = Location(file=Path("app.py"), line_start=42, line_end=45)

        finding1 = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Vulnerability",
            location=location,
            cwe_id="CWE-89",
            confidence=Confidence.MEDIUM,
        )

        finding2 = Finding(
            id="CODEQL-002",
            scanner="codeql",
            severity=Severity.CRITICAL,
            title="SQL Injection",
            description="Vulnerability",
            location=location,
            cwe_id="CWE-89",
            confidence=Confidence.MEDIUM,
        )

        # Act
        deduplicated = orchestrator.deduplicate([finding1, finding2])

        # Assert
        assert len(deduplicated) == 1
        merged = deduplicated[0]
        assert merged.severity == Severity.CRITICAL  # Kept higher severity
        assert merged.confidence == Confidence.HIGH  # Increased confidence
        assert "merged_scanners" in merged.metadata
        assert "semgrep" in merged.metadata["merged_scanners"]
        assert "codeql" in merged.metadata["merged_scanners"]

    def test_deduplicate_different_findings(self, orchestrator):
        """Test that different findings are not deduplicated."""
        # Arrange
        finding1 = Finding(
            id="TEST-001",
            scanner="scanner1",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Test",
            location=Location(file=Path("app.py"), line_start=10, line_end=12),
            cwe_id="CWE-89",
        )

        finding2 = Finding(
            id="TEST-002",
            scanner="scanner2",
            severity=Severity.MEDIUM,
            title="XSS",
            description="Test",
            location=Location(file=Path("app.py"), line_start=20, line_end=22),
            cwe_id="CWE-79",
        )

        # Act
        deduplicated = orchestrator.deduplicate([finding1, finding2])

        # Assert
        assert len(deduplicated) == 2

    def test_deduplicate_empty_list(self, orchestrator):
        """Test deduplication of empty list."""
        # Act
        deduplicated = orchestrator.deduplicate([])

        # Assert
        assert deduplicated == []

    def test_deduplicate_single_finding(self, orchestrator, sample_finding):
        """Test deduplication of single finding."""
        # Act
        deduplicated = orchestrator.deduplicate([sample_finding])

        # Assert
        assert len(deduplicated) == 1
        assert deduplicated[0] == sample_finding

    def test_scan_with_deduplication_enabled(self, orchestrator, tmp_path):
        """Test scan with deduplication enabled (default)."""
        # Arrange
        location = Location(file=Path("app.py"), line_start=42, line_end=45)

        # Same vulnerability from two scanners
        finding1 = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Vulnerability",
            location=location,
            cwe_id="CWE-89",
        )

        finding2 = Finding(
            id="CODEQL-002",
            scanner="codeql",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Vulnerability",
            location=location,
            cwe_id="CWE-89",
        )

        adapter1 = Mock(spec=ScannerAdapter)
        adapter1.name = "semgrep"
        adapter1.is_available.return_value = True
        adapter1.scan.return_value = [finding1]

        adapter2 = Mock(spec=ScannerAdapter)
        adapter2.name = "codeql"
        adapter2.is_available.return_value = True
        adapter2.scan.return_value = [finding2]

        orchestrator.register(adapter1)
        orchestrator.register(adapter2)

        target = tmp_path / "src"
        target.mkdir()

        # Act
        findings = orchestrator.scan(target=target, deduplicate=True)

        # Assert - should be deduplicated to 1 finding
        assert len(findings) == 1

    def test_scan_with_deduplication_disabled(self, orchestrator, tmp_path):
        """Test scan with deduplication disabled."""
        # Arrange
        location = Location(file=Path("app.py"), line_start=42, line_end=45)

        finding1 = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Vulnerability",
            location=location,
            cwe_id="CWE-89",
        )

        finding2 = Finding(
            id="CODEQL-002",
            scanner="codeql",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Vulnerability",
            location=location,
            cwe_id="CWE-89",
        )

        adapter1 = Mock(spec=ScannerAdapter)
        adapter1.name = "semgrep"
        adapter1.is_available.return_value = True
        adapter1.scan.return_value = [finding1]

        adapter2 = Mock(spec=ScannerAdapter)
        adapter2.name = "codeql"
        adapter2.is_available.return_value = True
        adapter2.scan.return_value = [finding2]

        orchestrator.register(adapter1)
        orchestrator.register(adapter2)

        target = tmp_path / "src"
        target.mkdir()

        # Act
        findings = orchestrator.scan(target=target, deduplicate=False)

        # Assert - should have both findings
        assert len(findings) == 2


class TestOrchestratorHelpers:
    """Test helper methods."""

    def test_list_scanners_empty(self):
        """Test list_scanners with no registered adapters."""
        orchestrator = ScannerOrchestrator()
        assert orchestrator.list_scanners() == []

    def test_list_scanners_multiple(self, orchestrator):
        """Test list_scanners with multiple adapters."""
        adapter1 = Mock(spec=ScannerAdapter)
        adapter1.name = "scanner1"

        adapter2 = Mock(spec=ScannerAdapter)
        adapter2.name = "scanner2"

        orchestrator.register(adapter1)
        orchestrator.register(adapter2)

        scanners = orchestrator.list_scanners()
        assert len(scanners) == 2
        assert "scanner1" in scanners
        assert "scanner2" in scanners

    def test_get_adapter_exists(self, orchestrator, mock_adapter):
        """Test get_adapter for registered adapter."""
        orchestrator.register(mock_adapter)
        adapter = orchestrator.get_adapter("test-scanner")
        assert adapter == mock_adapter

    def test_get_adapter_not_exists(self, orchestrator):
        """Test get_adapter for unregistered adapter."""
        adapter = orchestrator.get_adapter("nonexistent")
        assert adapter is None
