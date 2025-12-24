"""Tests for security scanner adapters.

This module tests:
1. SemgrepAdapter with mocked subprocess calls
2. Base adapter interface compliance
3. Tool discovery mechanisms
4. Error handling and edge cases
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from flowspec_cli.security.adapters.semgrep import SemgrepAdapter
from flowspec_cli.security.adapters.discovery import ToolDiscovery
from flowspec_cli.security.models import (
    Severity,
    Confidence,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_discovery():
    """Create a mock ToolDiscovery instance."""
    discovery = Mock(spec=ToolDiscovery)
    discovery.is_available.return_value = True
    discovery.find_tool.return_value = Path("/usr/bin/semgrep")
    return discovery


@pytest.fixture
def semgrep_json_output():
    """Sample Semgrep JSON output with findings."""
    return {
        "results": [
            {
                "check_id": "python.lang.security.audit.sql-injection",
                "path": "app.py",
                "start": {"line": 42, "col": 10},
                "end": {"line": 45, "col": 25},
                "extra": {
                    "severity": "ERROR",
                    "message": "SQL injection vulnerability detected",
                    "lines": 'cursor.execute("SELECT * FROM users WHERE id = " + user_id)',
                    "metadata": {
                        "cwe": ["CWE-89"],
                        "remediation": "Use parameterized queries",
                        "references": [
                            "https://cwe.mitre.org/data/definitions/89.html"
                        ],
                    },
                },
            },
            {
                "check_id": "python.lang.security.audit.hardcoded-password",
                "path": "config.py",
                "start": {"line": 10, "col": 0},
                "end": {"line": 10, "col": 30},
                "extra": {
                    "severity": "WARNING",
                    "message": "Hardcoded password detected",
                    "lines": 'PASSWORD = "secret123"',
                    "metadata": {
                        "cwe": 798,  # Integer CWE
                    },
                },
            },
        ]
    }


@pytest.fixture
def semgrep_empty_output():
    """Semgrep output with no findings."""
    return {"results": []}


# ============================================================================
# SemgrepAdapter Tests
# ============================================================================


class TestSemgrepAdapter:
    """Test SemgrepAdapter functionality."""

    def test_name_property(self, mock_discovery):
        """Test that name property returns 'semgrep'."""
        adapter = SemgrepAdapter(discovery=mock_discovery)
        assert adapter.name == "semgrep"

    def test_is_available_when_tool_exists(self, mock_discovery):
        """Test is_available returns True when Semgrep is installed."""
        mock_discovery.is_available.return_value = True
        adapter = SemgrepAdapter(discovery=mock_discovery)

        assert adapter.is_available() is True
        mock_discovery.is_available.assert_called_once_with("semgrep")

    def test_is_available_when_tool_missing(self, mock_discovery):
        """Test is_available returns False when Semgrep is not installed."""
        mock_discovery.is_available.return_value = False
        adapter = SemgrepAdapter(discovery=mock_discovery)

        assert adapter.is_available() is False

    @patch("subprocess.run")
    def test_version_property(self, mock_run, mock_discovery):
        """Test version property retrieves Semgrep version."""
        # Arrange
        mock_run.return_value = Mock(
            stdout="1.45.0\n",
            stderr="",
            returncode=0,
        )
        adapter = SemgrepAdapter(discovery=mock_discovery)

        # Act
        version = adapter.version

        # Assert
        assert version == "1.45.0"
        mock_run.assert_called_once_with(
            ["/usr/bin/semgrep", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )

    @patch("subprocess.run")
    def test_version_caches_result(self, mock_run, mock_discovery):
        """Test that version is cached after first call."""
        # Arrange
        mock_run.return_value = Mock(stdout="1.45.0\n", returncode=0)
        adapter = SemgrepAdapter(discovery=mock_discovery)

        # Act - call twice
        version1 = adapter.version
        version2 = adapter.version

        # Assert - subprocess called only once
        assert version1 == version2 == "1.45.0"
        assert mock_run.call_count == 1

    @patch("subprocess.run")
    def test_version_with_prefix(self, mock_run, mock_discovery):
        """Test version parsing when output has 'semgrep version' prefix."""
        # Arrange
        mock_run.return_value = Mock(stdout="semgrep version 1.45.0\n", returncode=0)
        adapter = SemgrepAdapter(discovery=mock_discovery)

        # Act
        version = adapter.version

        # Assert
        assert version == "1.45.0"

    def test_version_raises_when_not_available(self, mock_discovery):
        """Test that version raises RuntimeError when Semgrep is not available."""
        # Arrange
        mock_discovery.is_available.return_value = False
        adapter = SemgrepAdapter(discovery=mock_discovery)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Semgrep is not available"):
            _ = adapter.version

    @patch("subprocess.run")
    def test_scan_success(
        self, mock_run, mock_discovery, semgrep_json_output, tmp_path
    ):
        """Test successful scan execution and parsing."""
        # Arrange
        mock_run.return_value = Mock(
            stdout=json.dumps(semgrep_json_output),
            stderr="",
            returncode=1,  # Exit code 1 means findings
        )
        adapter = SemgrepAdapter(discovery=mock_discovery)
        target = tmp_path / "src"
        target.mkdir()

        # Act
        findings = adapter.scan(target)

        # Assert
        assert len(findings) == 2

        # Check first finding (SQL injection)
        sql_finding = findings[0]
        assert sql_finding.id == "SEMGREP-python.lang.security.audit.sql-injection"
        assert sql_finding.scanner == "semgrep"
        assert sql_finding.severity == Severity.HIGH  # ERROR maps to HIGH
        assert sql_finding.cwe_id == "CWE-89"
        assert sql_finding.confidence == Confidence.HIGH
        assert sql_finding.location.file == Path("app.py")
        assert sql_finding.location.line_start == 42
        assert sql_finding.location.line_end == 45
        assert "parameterized queries" in sql_finding.remediation

        # Check second finding (hardcoded password)
        pwd_finding = findings[1]
        assert pwd_finding.severity == Severity.MEDIUM  # WARNING maps to MEDIUM
        assert pwd_finding.cwe_id == "CWE-798"  # Integer CWE converted

    @patch("subprocess.run")
    def test_scan_with_config(
        self, mock_run, mock_discovery, semgrep_empty_output, tmp_path
    ):
        """Test scan with custom configuration."""
        # Arrange
        mock_run.return_value = Mock(
            stdout=json.dumps(semgrep_empty_output),
            returncode=0,
        )
        adapter = SemgrepAdapter(discovery=mock_discovery)
        target = tmp_path / "src"
        target.mkdir()

        config = {
            "rules": ["p/security-audit", "p/owasp-top-10"],
            "exclude": ["tests/", "vendor/"],
            "timeout": 300,
        }

        # Act
        findings = adapter.scan(target, config=config)

        # Assert
        assert findings == []

        # Verify command construction
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert "/usr/bin/semgrep" in str(cmd[0])
        assert "--config" in cmd
        assert "p/security-audit,p/owasp-top-10" in cmd
        assert "--exclude" in cmd
        assert "tests/" in cmd
        assert "vendor/" in cmd
        assert str(target) in cmd

    @patch("subprocess.run")
    def test_scan_no_findings(
        self, mock_run, mock_discovery, semgrep_empty_output, tmp_path
    ):
        """Test scan with no findings."""
        # Arrange
        mock_run.return_value = Mock(
            stdout=json.dumps(semgrep_empty_output),
            returncode=0,
        )
        adapter = SemgrepAdapter(discovery=mock_discovery)
        target = tmp_path / "src"
        target.mkdir()

        # Act
        findings = adapter.scan(target)

        # Assert
        assert findings == []

    def test_scan_raises_when_not_available(self, mock_discovery, tmp_path):
        """Test that scan raises RuntimeError when Semgrep is not available."""
        # Arrange
        mock_discovery.is_available.return_value = False
        adapter = SemgrepAdapter(discovery=mock_discovery)
        target = tmp_path / "src"
        target.mkdir()

        # Act & Assert
        with pytest.raises(RuntimeError, match="Semgrep is not available"):
            adapter.scan(target)

    def test_scan_raises_when_target_missing(self, mock_discovery):
        """Test that scan raises ValueError when target doesn't exist."""
        # Arrange
        adapter = SemgrepAdapter(discovery=mock_discovery)
        target = Path("/nonexistent/path")

        # Act & Assert
        with pytest.raises(ValueError, match="Target path does not exist"):
            adapter.scan(target)

    @patch("subprocess.run")
    def test_scan_timeout(self, mock_run, mock_discovery, tmp_path):
        """Test scan timeout handling."""
        # Arrange
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["semgrep"], timeout=60)
        adapter = SemgrepAdapter(discovery=mock_discovery)
        target = tmp_path / "src"
        target.mkdir()

        # Act & Assert
        with pytest.raises(RuntimeError, match="timed out"):
            adapter.scan(target, config={"timeout": 60})

    @patch("subprocess.run")
    def test_scan_semgrep_error(self, mock_run, mock_discovery, tmp_path):
        """Test handling of Semgrep execution errors."""
        # Arrange
        mock_run.return_value = Mock(
            stdout="",
            stderr="Semgrep error: invalid config",
            returncode=2,  # Error exit code
        )
        adapter = SemgrepAdapter(discovery=mock_discovery)
        target = tmp_path / "src"
        target.mkdir()

        # Act & Assert
        with pytest.raises(RuntimeError, match="Semgrep scan failed"):
            adapter.scan(target)

    @patch("subprocess.run")
    def test_scan_invalid_json(self, mock_run, mock_discovery, tmp_path):
        """Test handling of invalid JSON output."""
        # Arrange
        mock_run.return_value = Mock(
            stdout="invalid json {",
            stderr="",
            returncode=0,
        )
        adapter = SemgrepAdapter(discovery=mock_discovery)
        target = tmp_path / "src"
        target.mkdir()

        # Act & Assert
        with pytest.raises(RuntimeError, match="Failed to parse Semgrep output"):
            adapter.scan(target)

    def test_get_install_instructions(self, mock_discovery):
        """Test that install instructions are returned."""
        # Arrange
        adapter = SemgrepAdapter(discovery=mock_discovery)

        # Act
        instructions = adapter.get_install_instructions()

        # Assert
        assert "pip install semgrep" in instructions
        assert "brew install semgrep" in instructions
        assert "https://semgrep.dev" in instructions


class TestSeverityMapping:
    """Test Semgrep severity to UFFormat severity mapping."""

    @pytest.fixture
    def adapter(self, mock_discovery):
        return SemgrepAdapter(discovery=mock_discovery)

    def test_map_error_severity(self, adapter):
        """Test ERROR maps to HIGH."""
        assert adapter._map_severity("ERROR") == Severity.HIGH

    def test_map_warning_severity(self, adapter):
        """Test WARNING maps to MEDIUM."""
        assert adapter._map_severity("WARNING") == Severity.MEDIUM

    def test_map_info_severity(self, adapter):
        """Test INFO maps to LOW."""
        assert adapter._map_severity("INFO") == Severity.LOW

    def test_map_unknown_severity(self, adapter):
        """Test unknown severity maps to INFO."""
        assert adapter._map_severity("UNKNOWN") == Severity.INFO

    def test_map_lowercase_severity(self, adapter):
        """Test case-insensitive severity mapping."""
        assert adapter._map_severity("error") == Severity.HIGH
        assert adapter._map_severity("warning") == Severity.MEDIUM


class TestCWEExtraction:
    """Test CWE ID extraction from Semgrep metadata."""

    @pytest.fixture
    def adapter(self, mock_discovery):
        return SemgrepAdapter(discovery=mock_discovery)

    def test_extract_cwe_list_string(self, adapter):
        """Test CWE extraction from list of strings."""
        finding = {"extra": {"metadata": {"cwe": ["CWE-89", "CWE-564"]}}}
        assert adapter._extract_cwe(finding) == "CWE-89"

    def test_extract_cwe_list_int(self, adapter):
        """Test CWE extraction from list of integers."""
        finding = {"extra": {"metadata": {"cwe": [89, 564]}}}
        assert adapter._extract_cwe(finding) == "CWE-89"

    def test_extract_cwe_string(self, adapter):
        """Test CWE extraction from string."""
        finding = {"extra": {"metadata": {"cwe": "CWE-79"}}}
        assert adapter._extract_cwe(finding) == "CWE-79"

    def test_extract_cwe_int(self, adapter):
        """Test CWE extraction from integer."""
        finding = {"extra": {"metadata": {"cwe": 798}}}
        assert adapter._extract_cwe(finding) == "CWE-798"

    def test_extract_cwe_missing(self, adapter):
        """Test CWE extraction when metadata missing."""
        finding = {"extra": {"metadata": {}}}
        assert adapter._extract_cwe(finding) is None

    def test_extract_cwe_empty_list(self, adapter):
        """Test CWE extraction from empty list."""
        finding = {"extra": {"metadata": {"cwe": []}}}
        assert adapter._extract_cwe(finding) is None


class TestReferenceExtraction:
    """Test reference URL extraction from Semgrep metadata."""

    @pytest.fixture
    def adapter(self, mock_discovery):
        return SemgrepAdapter(discovery=mock_discovery)

    def test_extract_references_list(self, adapter):
        """Test reference extraction from list."""
        metadata = {
            "references": [
                "https://cwe.mitre.org/data/definitions/89.html",
                "https://owasp.org/www-community/attacks/SQL_Injection",
            ]
        }
        refs = adapter._extract_references(metadata)
        assert len(refs) == 2
        assert "https://cwe.mitre.org" in refs[0]

    def test_extract_references_string(self, adapter):
        """Test reference extraction from string."""
        metadata = {"reference": "https://example.com"}
        refs = adapter._extract_references(metadata)
        assert len(refs) == 1
        assert refs[0] == "https://example.com"

    def test_extract_references_multiple_fields(self, adapter):
        """Test reference extraction from multiple metadata fields."""
        metadata = {
            "references": ["https://url1.com"],
            "source": "https://url2.com",
            "source-rule": ["https://url3.com"],
        }
        refs = adapter._extract_references(metadata)
        assert len(refs) == 3

    def test_extract_references_empty(self, adapter):
        """Test reference extraction with no references."""
        metadata = {}
        refs = adapter._extract_references(metadata)
        assert refs == []

    def test_extract_references_filters_none(self, adapter):
        """Test that None values are filtered out."""
        metadata = {"references": ["https://url1.com", None, "https://url2.com"]}
        refs = adapter._extract_references(metadata)
        assert len(refs) == 2
        assert None not in refs


class TestToolDiscovery:
    """Test ToolDiscovery functionality."""

    def test_is_available_in_path(self):
        """Test tool discovery when tool is in PATH."""
        with patch("shutil.which", return_value="/usr/bin/python"):
            discovery = ToolDiscovery()
            assert discovery.is_available("python") is True

    def test_is_available_not_found(self):
        """Test tool discovery when tool is not found."""
        with patch("shutil.which", return_value=None):
            discovery = ToolDiscovery()
            assert discovery.is_available("nonexistent-tool") is False

    def test_find_tool_in_path(self):
        """Test finding tool in PATH."""
        with patch("shutil.which", return_value="/usr/bin/python"):
            discovery = ToolDiscovery()
            tool_path = discovery.find_tool("python")
            assert tool_path == Path("/usr/bin/python")

    def test_find_tool_not_found(self):
        """Test finding tool that doesn't exist returns None."""
        with patch("shutil.which", return_value=None):
            discovery = ToolDiscovery()
            tool_path = discovery.find_tool("nonexistent-tool")
            assert tool_path is None

    def test_find_tool_in_cache(self, tmp_path):
        """Test finding tool in cache directory."""
        # Arrange
        cache_dir = tmp_path / "tools"
        cache_dir.mkdir()
        tool_file = cache_dir / "custom-scanner"
        tool_file.write_text("#!/bin/bash\necho 'scanner'")

        with patch("shutil.which", return_value=None):
            discovery = ToolDiscovery(cache_dir=cache_dir)

            # Act
            tool_path = discovery.find_tool("custom-scanner")

            # Assert
            assert tool_path == tool_file

    def test_init_creates_cache_dir(self, tmp_path):
        """Test that initialization creates cache directory."""
        cache_dir = tmp_path / "cache"
        assert not cache_dir.exists()

        ToolDiscovery(cache_dir=cache_dir)

        assert cache_dir.exists()
        assert cache_dir.is_dir()
