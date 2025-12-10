"""Tests for Semgrep scanner adapter.

Tests cover:
- Availability checking
- Scan execution with mocked Semgrep output
- Finding conversion to UFFormat
- Severity mapping
- CWE extraction
- Error handling
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from specify_cli.security.adapters.semgrep import SemgrepAdapter
from specify_cli.security.models import Confidence, Severity


# Sample Semgrep JSON output for testing
SAMPLE_SEMGREP_OUTPUT = {
    "results": [
        {
            "check_id": "python.lang.security.audit.dangerous-exec-use.dangerous-exec-use",
            "path": "src/app.py",
            "start": {"line": 42, "col": 5},
            "end": {"line": 42, "col": 25},
            "extra": {
                "severity": "ERROR",
                "message": "Detected string concatenation in SQL query. This could be vulnerable to SQL injection.",
                "lines": 'query = "SELECT * FROM users WHERE id = " + user_id',
                "metadata": {
                    "cwe": ["CWE-89"],
                    "owasp": ["A03:2021"],
                    "references": ["https://owasp.org/Top10/A03_2021-Injection/"],
                    "remediation": "Use parameterized queries instead of string concatenation.",
                },
            },
        },
        {
            "check_id": "python.lang.security.audit.hardcoded-password",
            "path": "src/config.py",
            "start": {"line": 10, "col": 1},
            "end": {"line": 10, "col": 30},
            "extra": {
                "severity": "WARNING",
                "message": "Hardcoded password detected",
                "lines": 'PASSWORD = "secretpass123"',
                "metadata": {
                    "cwe": "CWE-798",
                    "references": ["https://cwe.mitre.org/data/definitions/798.html"],
                },
            },
        },
        {
            "check_id": "python.lang.best-practice.logging-format",
            "path": "src/utils.py",
            "start": {"line": 100, "col": 1},
            "end": {"line": 100, "col": 50},
            "extra": {
                "severity": "INFO",
                "message": "Use lazy % formatting in logging functions",
                "lines": 'logging.info("User %s logged in" % username)',
                "metadata": {},
            },
        },
    ],
    "errors": [],
    "version": "1.50.0",
}


EMPTY_SEMGREP_OUTPUT = {"results": [], "errors": [], "version": "1.50.0"}


class TestSemgrepAdapterAvailability:
    """Tests for Semgrep availability checking."""

    def test_name_property(self):
        """Test adapter name is 'semgrep'."""
        adapter = SemgrepAdapter()
        assert adapter.name == "semgrep"

    @patch("specify_cli.security.adapters.semgrep.ToolDiscovery")
    def test_is_available_true(self, mock_discovery_class):
        """Test is_available returns True when Semgrep is installed."""
        mock_discovery = MagicMock()
        mock_discovery.is_available.return_value = True
        mock_discovery_class.return_value = mock_discovery

        adapter = SemgrepAdapter()
        assert adapter.is_available() is True
        mock_discovery.is_available.assert_called_with("semgrep")

    @patch("specify_cli.security.adapters.semgrep.ToolDiscovery")
    def test_is_available_false(self, mock_discovery_class):
        """Test is_available returns False when Semgrep is not installed."""
        mock_discovery = MagicMock()
        mock_discovery.is_available.return_value = False
        mock_discovery_class.return_value = mock_discovery

        adapter = SemgrepAdapter()
        assert adapter.is_available() is False

    @patch("specify_cli.security.adapters.semgrep.subprocess.run")
    @patch("specify_cli.security.adapters.semgrep.ToolDiscovery")
    def test_version_property(self, mock_discovery_class, mock_run):
        """Test version property returns Semgrep version."""
        mock_discovery = MagicMock()
        mock_discovery.is_available.return_value = True
        mock_discovery.find_tool.return_value = Path("/usr/bin/semgrep")
        mock_discovery_class.return_value = mock_discovery

        mock_run.return_value = Mock(stdout="1.50.0\n", returncode=0)

        adapter = SemgrepAdapter()
        assert adapter.version == "1.50.0"

    @patch("specify_cli.security.adapters.semgrep.ToolDiscovery")
    def test_version_not_available_raises(self, mock_discovery_class):
        """Test version raises when Semgrep not available."""
        mock_discovery = MagicMock()
        mock_discovery.is_available.return_value = False
        mock_discovery_class.return_value = mock_discovery

        adapter = SemgrepAdapter()
        with pytest.raises(RuntimeError, match="not available"):
            _ = adapter.version

    def test_get_install_instructions(self):
        """Test install instructions are provided."""
        adapter = SemgrepAdapter()
        instructions = adapter.get_install_instructions()

        assert "pip install semgrep" in instructions
        assert "brew install semgrep" in instructions


class TestSemgrepAdapterScanning:
    """Tests for Semgrep scanning functionality."""

    @pytest.fixture
    def mock_adapter(self):
        """Create adapter with mocked discovery."""
        with patch("specify_cli.security.adapters.semgrep.ToolDiscovery") as mock_class:
            mock_discovery = MagicMock()
            mock_discovery.is_available.return_value = True
            mock_discovery.find_tool.return_value = Path("/usr/bin/semgrep")
            mock_class.return_value = mock_discovery

            adapter = SemgrepAdapter()
            yield adapter

    @pytest.fixture
    def temp_dir(self, tmp_path):
        """Create temporary directory with test file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")
        return tmp_path

    @patch("specify_cli.security.adapters.semgrep.subprocess.run")
    def test_scan_basic(self, mock_run, mock_adapter, temp_dir):
        """Test basic scan execution and result parsing."""
        mock_run.return_value = Mock(
            stdout=json.dumps(SAMPLE_SEMGREP_OUTPUT),
            stderr="",
            returncode=1,  # 1 means findings
        )

        findings = mock_adapter.scan(temp_dir)

        assert len(findings) == 3
        assert findings[0].scanner == "semgrep"
        mock_run.assert_called_once()

    @patch("specify_cli.security.adapters.semgrep.subprocess.run")
    def test_scan_no_findings(self, mock_run, mock_adapter, temp_dir):
        """Test scan with no findings returns empty list."""
        mock_run.return_value = Mock(
            stdout=json.dumps(EMPTY_SEMGREP_OUTPUT),
            stderr="",
            returncode=0,
        )

        findings = mock_adapter.scan(temp_dir)

        assert len(findings) == 0

    @patch("specify_cli.security.adapters.semgrep.subprocess.run")
    def test_scan_converts_to_unified_format(self, mock_run, mock_adapter, temp_dir):
        """Test findings are converted to UFFormat correctly."""
        mock_run.return_value = Mock(
            stdout=json.dumps(SAMPLE_SEMGREP_OUTPUT),
            stderr="",
            returncode=1,
        )

        findings = mock_adapter.scan(temp_dir)

        # Check first finding (SQL injection)
        sql_finding = findings[0]
        assert sql_finding.id.startswith("SEMGREP-")
        assert sql_finding.severity == Severity.HIGH  # ERROR maps to HIGH
        assert sql_finding.cwe_id == "CWE-89"
        assert sql_finding.location.file == Path("src/app.py")
        assert sql_finding.location.line_start == 42
        assert sql_finding.confidence == Confidence.HIGH
        assert "parameterized" in (sql_finding.remediation or "").lower()

    @patch("specify_cli.security.adapters.semgrep.subprocess.run")
    def test_scan_target_not_exists(self, mock_run, mock_adapter):
        """Test scan with nonexistent target raises error."""
        with pytest.raises(ValueError, match="does not exist"):
            mock_adapter.scan(Path("/nonexistent/path"))

    @patch("specify_cli.security.adapters.semgrep.ToolDiscovery")
    def test_scan_not_available_raises(self, mock_discovery_class, tmp_path):
        """Test scan raises when Semgrep not available."""
        mock_discovery = MagicMock()
        mock_discovery.is_available.return_value = False
        mock_discovery_class.return_value = mock_discovery

        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        adapter = SemgrepAdapter()
        with pytest.raises(RuntimeError, match="not available"):
            adapter.scan(tmp_path)

    @patch("specify_cli.security.adapters.semgrep.subprocess.run")
    def test_scan_error_exit_code(self, mock_run, mock_adapter, temp_dir):
        """Test scan handles error exit codes."""
        mock_run.return_value = Mock(
            stdout="",
            stderr="Error: invalid config",
            returncode=2,
        )

        with pytest.raises(RuntimeError, match="scan failed"):
            mock_adapter.scan(temp_dir)

    @patch("specify_cli.security.adapters.semgrep.subprocess.run")
    def test_scan_timeout(self, mock_run, mock_adapter, temp_dir):
        """Test scan handles timeout."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="semgrep", timeout=600)

        with pytest.raises(RuntimeError, match="timed out"):
            mock_adapter.scan(temp_dir)

    @patch("specify_cli.security.adapters.semgrep.subprocess.run")
    def test_scan_invalid_json(self, mock_run, mock_adapter, temp_dir):
        """Test scan handles invalid JSON output."""
        mock_run.return_value = Mock(
            stdout="not valid json",
            stderr="",
            returncode=0,
        )

        with pytest.raises(RuntimeError, match="parse.*output"):
            mock_adapter.scan(temp_dir)

    @patch("specify_cli.security.adapters.semgrep.subprocess.run")
    def test_scan_with_config(self, mock_run, mock_adapter, temp_dir):
        """Test scan passes configuration options."""
        mock_run.return_value = Mock(
            stdout=json.dumps(EMPTY_SEMGREP_OUTPUT),
            stderr="",
            returncode=0,
        )

        config = {
            "rules": ["p/security-audit", "p/owasp-top-ten"],
            "exclude": ["tests/", "*.test.py"],
            "timeout": 300,
        }
        mock_adapter.scan(temp_dir, config=config)

        call_args = mock_run.call_args
        cmd = call_args[0][0]

        # Check rules
        assert "--config" in cmd
        config_idx = cmd.index("--config")
        assert "p/security-audit,p/owasp-top-ten" in cmd[config_idx + 1]

        # Check excludes
        exclude_indices = [i for i, arg in enumerate(cmd) if arg == "--exclude"]
        assert len(exclude_indices) == 2

        # Check timeout passed to subprocess
        assert call_args[1]["timeout"] == 300


class TestSeverityMapping:
    """Tests for Semgrep severity to UFFormat mapping."""

    @pytest.fixture
    def adapter(self):
        with patch("specify_cli.security.adapters.semgrep.ToolDiscovery") as mock_class:
            mock_discovery = MagicMock()
            mock_discovery.is_available.return_value = True
            mock_class.return_value = mock_discovery
            yield SemgrepAdapter()

    def test_error_maps_to_high(self, adapter):
        """Test Semgrep ERROR maps to UFFormat HIGH."""
        assert adapter._map_severity("ERROR") == Severity.HIGH

    def test_warning_maps_to_medium(self, adapter):
        """Test Semgrep WARNING maps to UFFormat MEDIUM."""
        assert adapter._map_severity("WARNING") == Severity.MEDIUM

    def test_info_maps_to_low(self, adapter):
        """Test Semgrep INFO maps to UFFormat LOW."""
        assert adapter._map_severity("INFO") == Severity.LOW

    def test_unknown_maps_to_info(self, adapter):
        """Test unknown severity maps to INFO."""
        assert adapter._map_severity("UNKNOWN") == Severity.INFO
        assert adapter._map_severity("") == Severity.INFO

    def test_case_insensitive(self, adapter):
        """Test severity mapping is case insensitive."""
        assert adapter._map_severity("error") == Severity.HIGH
        assert adapter._map_severity("Error") == Severity.HIGH
        assert adapter._map_severity("WARNING") == Severity.MEDIUM


class TestCWEExtraction:
    """Tests for CWE extraction from Semgrep metadata."""

    @pytest.fixture
    def adapter(self):
        with patch("specify_cli.security.adapters.semgrep.ToolDiscovery") as mock_class:
            mock_discovery = MagicMock()
            mock_class.return_value = mock_discovery
            yield SemgrepAdapter()

    def test_cwe_from_list(self, adapter):
        """Test CWE extraction from list."""
        finding = {
            "extra": {
                "metadata": {
                    "cwe": ["CWE-89", "CWE-90"],
                }
            }
        }
        assert adapter._extract_cwe(finding) == "CWE-89"

    def test_cwe_from_string(self, adapter):
        """Test CWE extraction from string."""
        finding = {
            "extra": {
                "metadata": {
                    "cwe": "CWE-79",
                }
            }
        }
        assert adapter._extract_cwe(finding) == "CWE-79"

    def test_cwe_from_integer(self, adapter):
        """Test CWE extraction from integer."""
        finding = {
            "extra": {
                "metadata": {
                    "cwe": 89,
                }
            }
        }
        assert adapter._extract_cwe(finding) == "CWE-89"

    def test_cwe_from_list_of_integers(self, adapter):
        """Test CWE extraction from list of integers."""
        finding = {
            "extra": {
                "metadata": {
                    "cwe": [89, 90],
                }
            }
        }
        assert adapter._extract_cwe(finding) == "CWE-89"

    def test_cwe_missing(self, adapter):
        """Test CWE extraction when missing."""
        finding = {"extra": {"metadata": {}}}
        assert adapter._extract_cwe(finding) is None

        finding = {"extra": {}}
        assert adapter._extract_cwe(finding) is None

    def test_cwe_empty_list(self, adapter):
        """Test CWE extraction from empty list."""
        finding = {"extra": {"metadata": {"cwe": []}}}
        assert adapter._extract_cwe(finding) is None


class TestReferenceExtraction:
    """Tests for reference URL extraction."""

    @pytest.fixture
    def adapter(self):
        with patch("specify_cli.security.adapters.semgrep.ToolDiscovery") as mock_class:
            mock_discovery = MagicMock()
            mock_class.return_value = mock_discovery
            yield SemgrepAdapter()

    def test_references_from_list(self, adapter):
        """Test reference extraction from list."""
        metadata = {
            "references": [
                "https://owasp.org/Top10/",
                "https://cwe.mitre.org/",
            ]
        }
        refs = adapter._extract_references(metadata)
        assert len(refs) == 2
        assert "https://owasp.org/Top10/" in refs

    def test_reference_from_string(self, adapter):
        """Test reference extraction from single string."""
        metadata = {"reference": "https://example.com"}
        refs = adapter._extract_references(metadata)
        assert refs == ["https://example.com"]

    def test_source_reference(self, adapter):
        """Test extraction of 'source' field."""
        metadata = {"source": "https://semgrep.dev/r/rule-id"}
        refs = adapter._extract_references(metadata)
        assert "https://semgrep.dev/r/rule-id" in refs

    def test_no_references(self, adapter):
        """Test empty references when none present."""
        metadata = {}
        refs = adapter._extract_references(metadata)
        assert refs == []

    def test_multiple_reference_fields(self, adapter):
        """Test combining multiple reference fields."""
        metadata = {
            "references": ["https://ref1.com"],
            "source": "https://ref2.com",
        }
        refs = adapter._extract_references(metadata)
        assert len(refs) == 2


class TestFindingConversion:
    """Integration tests for full finding conversion."""

    @pytest.fixture
    def adapter(self):
        with patch("specify_cli.security.adapters.semgrep.ToolDiscovery") as mock_class:
            mock_discovery = MagicMock()
            mock_class.return_value = mock_discovery
            yield SemgrepAdapter()

    def test_full_finding_conversion(self, adapter):
        """Test complete finding conversion with all fields."""
        semgrep_finding = SAMPLE_SEMGREP_OUTPUT["results"][0]
        finding = adapter._to_finding(semgrep_finding)

        assert finding.id.startswith("SEMGREP-")
        assert finding.scanner == "semgrep"
        assert finding.severity == Severity.HIGH
        assert finding.title == semgrep_finding["check_id"]
        assert "SQL" in finding.description
        assert finding.location.file == Path("src/app.py")
        assert finding.location.line_start == 42
        assert finding.location.column_start == 5
        assert finding.cwe_id == "CWE-89"
        assert finding.confidence == Confidence.HIGH
        assert finding.remediation is not None
        assert len(finding.references) > 0
        assert finding.raw_data == semgrep_finding

    def test_minimal_finding_conversion(self, adapter):
        """Test finding conversion with minimal metadata."""
        semgrep_finding = {
            "check_id": "test.rule",
            "path": "test.py",
            "start": {"line": 1},
            "end": {"line": 1},
            "extra": {
                "severity": "INFO",
                "message": "Test message",
                "metadata": {},
            },
        }
        finding = adapter._to_finding(semgrep_finding)

        assert finding.id == "SEMGREP-test.rule"
        assert finding.severity == Severity.LOW
        assert finding.cwe_id is None
        assert finding.remediation is None
        assert finding.references == []
