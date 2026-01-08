"""Tests for scanner orchestration pattern.

This test module validates:
1. ScannerAdapter interface contract
2. ToolDiscovery chain (system → venv → cache)
3. SemgrepAdapter output parsing
4. Parallel execution
5. Fingerprint-based deduplication
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from flowspec_cli.security.adapters.base import ScannerAdapter
from flowspec_cli.security.adapters.discovery import ToolDiscovery
from flowspec_cli.security.adapters.semgrep import SemgrepAdapter
from flowspec_cli.security.models import Finding, Location, Severity
from flowspec_cli.security.orchestrator import ScannerOrchestrator


# --- Fixtures ---


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Temporary cache directory for tool discovery."""
    cache_dir = tmp_path / ".flowspec" / "tools"
    cache_dir.mkdir(parents=True)
    return cache_dir


@pytest.fixture
def mock_semgrep_output():
    """Mock Semgrep JSON output."""
    return {
        "results": [
            {
                "check_id": "python.lang.security.injection.sql-injection",
                "path": "app.py",
                "start": {"line": 42, "col": 5},
                "end": {"line": 42, "col": 20},
                "extra": {
                    "message": "Potential SQL injection vulnerability",
                    "severity": "ERROR",
                    "lines": '    cursor.execute("SELECT * FROM users WHERE id = " + user_id)',
                    "metadata": {
                        "cwe": ["CWE-89"],
                        "references": [
                            "https://owasp.org/www-community/attacks/SQL_Injection"
                        ],
                    },
                },
            },
            {
                "check_id": "python.lang.security.injection.command-injection",
                "path": "utils.py",
                "start": {"line": 10, "col": 1},
                "end": {"line": 10, "col": 30},
                "extra": {
                    "message": "Command injection vulnerability",
                    "severity": "WARNING",
                    "lines": '    os.system("ls " + user_input)',
                    "metadata": {
                        "cwe": ["CWE-78"],
                    },
                },
            },
        ],
        "errors": [],
        "time": 1.23,
    }


# --- Test ToolDiscovery ---


class TestToolDiscovery:
    """Test tool discovery chain."""

    def test_find_tool_in_system_path(self, temp_cache_dir):
        """Test finding tool in system PATH."""
        discovery = ToolDiscovery(cache_dir=temp_cache_dir)

        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/semgrep"
            result = discovery.find_tool("semgrep")

            assert result == Path("/usr/bin/semgrep")
            mock_which.assert_called_once_with("semgrep")

    def test_find_tool_in_venv(self, temp_cache_dir, tmp_path):
        """Test finding tool in project venv."""
        # Create fake venv
        venv_dir = tmp_path / ".venv"
        bin_dir = venv_dir / "bin"
        bin_dir.mkdir(parents=True)
        semgrep_path = bin_dir / "semgrep"
        semgrep_path.touch()

        discovery = ToolDiscovery(cache_dir=temp_cache_dir)

        with patch("shutil.which", return_value=None):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                result = discovery.find_tool("semgrep")
                assert result == semgrep_path

    def test_find_tool_in_cache(self, temp_cache_dir, tmp_path):
        """Test finding tool in specify cache."""
        # Create fake cached tool
        cached_tool = temp_cache_dir / "semgrep"
        cached_tool.touch()

        discovery = ToolDiscovery(cache_dir=temp_cache_dir)

        # Must patch both shutil.which AND sys.prefix to prevent finding the tool
        # in the system PATH or the current venv (sys.prefix check in _find_in_venv)
        with patch(
            "flowspec_cli.security.adapters.discovery.shutil.which", return_value=None
        ):
            with patch(
                "flowspec_cli.security.adapters.discovery.sys.prefix",
                str(tmp_path / "fake_venv"),
            ):
                result = discovery.find_tool("semgrep")
                assert result == cached_tool

    def test_find_tool_not_found(self, temp_cache_dir):
        """Test tool not found in any location."""
        discovery = ToolDiscovery(cache_dir=temp_cache_dir)

        with patch("shutil.which", return_value=None):
            result = discovery.find_tool("nonexistent-tool")
            assert result is None

    def test_is_available(self, temp_cache_dir):
        """Test is_available convenience method."""
        discovery = ToolDiscovery(cache_dir=temp_cache_dir)

        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/semgrep"
            assert discovery.is_available("semgrep") is True

        with patch("shutil.which", return_value=None):
            assert discovery.is_available("nonexistent") is False

    def test_ensure_available_found(self, temp_cache_dir):
        """Test ensure_available when tool is already installed."""
        discovery = ToolDiscovery(cache_dir=temp_cache_dir)

        with patch("shutil.which") as mock_which:
            mock_which.return_value = "/usr/bin/semgrep"
            result = discovery.ensure_available("semgrep", auto_install=False)
            assert result == Path("/usr/bin/semgrep")

    def test_ensure_available_not_found_no_install(self, temp_cache_dir, tmp_path):
        """Test ensure_available when tool not found and auto_install=False."""
        discovery = ToolDiscovery(cache_dir=temp_cache_dir)

        # Must patch both shutil.which AND sys.prefix to prevent finding the tool
        # in the system PATH or the current venv (sys.prefix check in _find_in_venv)
        with patch(
            "flowspec_cli.security.adapters.discovery.shutil.which", return_value=None
        ):
            with patch(
                "flowspec_cli.security.adapters.discovery.sys.prefix",
                str(tmp_path / "fake_venv"),
            ):
                result = discovery.ensure_available("semgrep", auto_install=False)
                assert result is None


# --- Test SemgrepAdapter ---


class TestSemgrepAdapter:
    """Test Semgrep adapter implementation."""

    def test_adapter_name(self):
        """Test adapter name property."""
        adapter = SemgrepAdapter()
        assert adapter.name == "semgrep"

    def test_is_available(self):
        """Test availability check."""
        adapter = SemgrepAdapter()

        with patch.object(adapter._discovery, "is_available") as mock_available:
            mock_available.return_value = True
            assert adapter.is_available() is True

            mock_available.return_value = False
            assert adapter.is_available() is False

    def test_get_version(self):
        """Test version retrieval."""
        adapter = SemgrepAdapter()

        with patch.object(adapter._discovery, "is_available", return_value=True):
            with patch.object(
                adapter._discovery, "find_tool", return_value=Path("/usr/bin/semgrep")
            ):
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = Mock(
                        stdout="1.45.0\n",
                        returncode=0,
                    )
                    version = adapter.version
                    assert version == "1.45.0"

    def test_get_version_not_available(self):
        """Test version retrieval when tool not available."""
        adapter = SemgrepAdapter()

        with patch.object(adapter._discovery, "is_available", return_value=False):
            with pytest.raises(RuntimeError, match="not available"):
                _ = adapter.version

    def test_scan_not_available(self, tmp_path):
        """Test scan when Semgrep not available."""
        adapter = SemgrepAdapter()
        target = tmp_path / "code"
        target.mkdir()

        with patch.object(adapter._discovery, "is_available", return_value=False):
            with pytest.raises(RuntimeError, match="not available"):
                adapter.scan(target)

    def test_scan_target_not_exists(self):
        """Test scan with non-existent target."""
        adapter = SemgrepAdapter()
        target = Path("/nonexistent/path")

        with patch.object(adapter._discovery, "is_available", return_value=True):
            with pytest.raises(ValueError, match="does not exist"):
                adapter.scan(target)

    def test_scan_success(self, tmp_path, mock_semgrep_output):
        """Test successful scan with mocked Semgrep output."""
        adapter = SemgrepAdapter()
        target = tmp_path / "code"
        target.mkdir()

        with patch.object(adapter._discovery, "is_available", return_value=True):
            with patch.object(
                adapter._discovery, "find_tool", return_value=Path("/usr/bin/semgrep")
            ):
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = Mock(
                        stdout=json.dumps(mock_semgrep_output),
                        stderr="",
                        returncode=1,  # Exit code 1 = findings
                    )

                    findings = adapter.scan(target)

                    assert len(findings) == 2
                    assert all(isinstance(f, Finding) for f in findings)

                    # Validate first finding
                    f1 = findings[0]
                    assert f1.scanner == "semgrep"
                    assert f1.severity == Severity.HIGH  # ERROR -> HIGH
                    assert f1.cwe_id == "CWE-89"
                    assert f1.location.file == Path("app.py")
                    assert f1.location.line_start == 42

                    # Validate second finding
                    f2 = findings[1]
                    assert f2.scanner == "semgrep"
                    assert f2.severity == Severity.MEDIUM  # WARNING -> MEDIUM
                    assert f2.cwe_id == "CWE-78"
                    assert f2.location.file == Path("utils.py")
                    assert f2.location.line_start == 10

    def test_scan_with_config(self, tmp_path, mock_semgrep_output):
        """Test scan with custom configuration."""
        adapter = SemgrepAdapter()
        target = tmp_path / "code"
        target.mkdir()

        config = {
            "rules": ["p/owasp-top-10", "p/python"],
            "exclude": ["tests/", "*.test.py"],
            "timeout": 300,
        }

        with patch.object(adapter._discovery, "is_available", return_value=True):
            with patch.object(
                adapter._discovery, "find_tool", return_value=Path("/usr/bin/semgrep")
            ):
                with patch("subprocess.run") as mock_run:
                    mock_run.return_value = Mock(
                        stdout=json.dumps(mock_semgrep_output),
                        stderr="",
                        returncode=0,
                    )

                    adapter.scan(target, config)

                    # Verify command construction
                    call_args = mock_run.call_args[0][0]
                    assert "--config" in call_args
                    assert "p/owasp-top-10,p/python" in call_args
                    assert "--exclude" in call_args
                    assert "tests/" in call_args

    def test_map_severity(self):
        """Test severity mapping."""
        adapter = SemgrepAdapter()

        assert adapter._map_severity("ERROR") == Severity.HIGH
        assert adapter._map_severity("WARNING") == Severity.MEDIUM
        assert adapter._map_severity("INFO") == Severity.LOW
        assert adapter._map_severity("UNKNOWN") == Severity.INFO

    def test_extract_cwe(self):
        """Test CWE extraction from metadata."""
        adapter = SemgrepAdapter()

        # Test list of strings
        finding = {"extra": {"metadata": {"cwe": ["CWE-89", "CWE-90"]}}}
        assert adapter._extract_cwe(finding) == "CWE-89"

        # Test single string
        finding = {"extra": {"metadata": {"cwe": "CWE-78"}}}
        assert adapter._extract_cwe(finding) == "CWE-78"

        # Test integer
        finding = {"extra": {"metadata": {"cwe": 89}}}
        assert adapter._extract_cwe(finding) == "CWE-89"

        # Test no CWE
        finding = {"extra": {"metadata": {}}}
        assert adapter._extract_cwe(finding) is None

    def test_get_install_instructions(self):
        """Test installation instructions."""
        adapter = SemgrepAdapter()
        instructions = adapter.get_install_instructions()

        assert "pip install semgrep" in instructions
        assert "https://semgrep.dev" in instructions


# --- Test ScannerOrchestrator ---


class MockAdapter(ScannerAdapter):
    """Mock scanner adapter for testing."""

    def __init__(
        self, name: str, available: bool = True, findings: list[Finding] | None = None
    ):
        self._name = name
        self._available = available
        self._findings = findings or []

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return "1.0.0"

    def is_available(self) -> bool:
        return self._available

    def scan(self, target: Path, config: dict | None = None) -> list[Finding]:
        return self._findings

    def get_install_instructions(self) -> str:
        return f"Install {self._name}"


class TestScannerOrchestrator:
    """Test scanner orchestrator."""

    def test_register_adapter(self):
        """Test adapter registration."""
        orchestrator = ScannerOrchestrator()
        adapter = MockAdapter("test-scanner")

        orchestrator.register(adapter)
        assert "test-scanner" in orchestrator.list_scanners()

    def test_register_duplicate(self):
        """Test registering duplicate adapter raises error."""
        orchestrator = ScannerOrchestrator()
        adapter1 = MockAdapter("test-scanner")
        adapter2 = MockAdapter("test-scanner")

        orchestrator.register(adapter1)
        with pytest.raises(ValueError, match="already registered"):
            orchestrator.register(adapter2)

    def test_scan_target_not_exists(self):
        """Test scan with non-existent target."""
        orchestrator = ScannerOrchestrator()
        adapter = MockAdapter("test-scanner")
        orchestrator.register(adapter)

        with pytest.raises(ValueError, match="does not exist"):
            orchestrator.scan(Path("/nonexistent"))

    def test_scan_no_adapters(self, tmp_path):
        """Test scan with no adapters registered."""
        orchestrator = ScannerOrchestrator()

        with pytest.raises(ValueError, match="No scanner adapters"):
            orchestrator.scan(tmp_path)

    def test_scan_scanner_not_registered(self, tmp_path):
        """Test scan with unregistered scanner."""
        orchestrator = ScannerOrchestrator()
        adapter = MockAdapter("scanner-a")
        orchestrator.register(adapter)

        with pytest.raises(RuntimeError, match="not registered"):
            orchestrator.scan(tmp_path, scanners=["scanner-b"])

    def test_scan_scanner_not_available(self, tmp_path):
        """Test scan when scanner not available."""
        orchestrator = ScannerOrchestrator()
        adapter = MockAdapter("test-scanner", available=False)
        orchestrator.register(adapter)

        with pytest.raises(RuntimeError, match="not available"):
            orchestrator.scan(tmp_path)

    def test_scan_sequential(self, tmp_path):
        """Test sequential scanning."""
        finding1 = Finding(
            id="SCANNER-A-001",
            scanner="scanner-a",
            severity=Severity.HIGH,
            title="Issue 1",
            description="Description 1",
            location=Location(Path("test.py"), 1, 1),
        )
        finding2 = Finding(
            id="SCANNER-B-001",
            scanner="scanner-b",
            severity=Severity.MEDIUM,
            title="Issue 2",
            description="Description 2",
            location=Location(Path("test.py"), 2, 2),
        )

        orchestrator = ScannerOrchestrator()
        orchestrator.register(MockAdapter("scanner-a", findings=[finding1]))
        orchestrator.register(MockAdapter("scanner-b", findings=[finding2]))

        findings = orchestrator.scan(tmp_path, parallel=False, deduplicate=False)

        assert len(findings) == 2
        assert finding1 in findings
        assert finding2 in findings

    def test_scan_parallel(self, tmp_path):
        """Test parallel scanning."""
        finding1 = Finding(
            id="SCANNER-A-001",
            scanner="scanner-a",
            severity=Severity.HIGH,
            title="Issue 1",
            description="Description 1",
            location=Location(Path("test.py"), 1, 1),
        )
        finding2 = Finding(
            id="SCANNER-B-001",
            scanner="scanner-b",
            severity=Severity.MEDIUM,
            title="Issue 2",
            description="Description 2",
            location=Location(Path("test.py"), 2, 2),
        )

        orchestrator = ScannerOrchestrator()
        orchestrator.register(MockAdapter("scanner-a", findings=[finding1]))
        orchestrator.register(MockAdapter("scanner-b", findings=[finding2]))

        findings = orchestrator.scan(tmp_path, parallel=True, deduplicate=False)

        assert len(findings) == 2

    def test_deduplicate(self, tmp_path):
        """Test fingerprint-based deduplication."""
        # Same location + CWE = duplicate
        finding1 = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Found by Semgrep",
            location=Location(Path("app.py"), 42, 45),
            cwe_id="CWE-89",
        )
        finding2 = Finding(
            id="CODEQL-002",
            scanner="codeql",
            severity=Severity.CRITICAL,  # Higher severity
            title="SQL Injection",
            description="Found by CodeQL",
            location=Location(Path("app.py"), 42, 45),
            cwe_id="CWE-89",
        )

        orchestrator = ScannerOrchestrator()
        deduplicated = orchestrator.deduplicate([finding1, finding2])

        # Should have only one finding
        assert len(deduplicated) == 1

        # Should keep highest severity (CRITICAL)
        merged = deduplicated[0]
        assert merged.severity == Severity.CRITICAL

        # Should track merged scanners
        assert "merged_scanners" in merged.metadata
        assert "semgrep" in merged.metadata["merged_scanners"]
        assert "codeql" in merged.metadata["merged_scanners"]

    def test_deduplicate_different_locations(self):
        """Test deduplication with different locations (should not dedupe)."""
        finding1 = Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Location 1",
            location=Location(Path("app.py"), 42, 45),
            cwe_id="CWE-89",
        )
        finding2 = Finding(
            id="SEMGREP-002",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection",
            description="Location 2",
            location=Location(Path("app.py"), 100, 105),  # Different line
            cwe_id="CWE-89",
        )

        orchestrator = ScannerOrchestrator()
        deduplicated = orchestrator.deduplicate([finding1, finding2])

        # Should keep both (different locations)
        assert len(deduplicated) == 2

    def test_list_scanners(self):
        """Test listing registered scanners."""
        orchestrator = ScannerOrchestrator()
        orchestrator.register(MockAdapter("scanner-a"))
        orchestrator.register(MockAdapter("scanner-b"))

        scanners = orchestrator.list_scanners()
        assert set(scanners) == {"scanner-a", "scanner-b"}

    def test_get_adapter(self):
        """Test getting registered adapter by name."""
        orchestrator = ScannerOrchestrator()
        adapter = MockAdapter("test-scanner")
        orchestrator.register(adapter)

        retrieved = orchestrator.get_adapter("test-scanner")
        assert retrieved is adapter

        none_adapter = orchestrator.get_adapter("nonexistent")
        assert none_adapter is None
