"""Tests for security CLI commands."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from specify_cli import app
from specify_cli.security.models import (
    Confidence,
    Finding,
    Location,
    Severity,
)

runner = CliRunner()


@pytest.fixture
def sample_findings():
    """Create sample findings for testing."""
    return [
        Finding(
            id="SEMGREP-001",
            scanner="semgrep",
            severity=Severity.HIGH,
            title="SQL Injection in user query",
            description="Potentially vulnerable to SQL injection",
            location=Location(
                file=Path("app.py"),
                line_start=42,
                line_end=45,
                code_snippet='cursor.execute("SELECT * FROM users WHERE id = " + user_id)',
            ),
            cwe_id="CWE-89",
            confidence=Confidence.HIGH,
        ),
        Finding(
            id="SEMGREP-002",
            scanner="semgrep",
            severity=Severity.MEDIUM,
            title="Hardcoded secret detected",
            description="API key found in source code",
            location=Location(
                file=Path("config.py"),
                line_start=10,
                line_end=10,
                code_snippet='API_KEY = "sk_test_1234567890"',
            ),
            cwe_id="CWE-798",
            confidence=Confidence.MEDIUM,
        ),
        Finding(
            id="SEMGREP-003",
            scanner="semgrep",
            severity=Severity.LOW,
            title="Weak hash algorithm",
            description="MD5 is not cryptographically secure",
            location=Location(
                file=Path("utils.py"),
                line_start=100,
                line_end=100,
                code_snippet="hashlib.md5(data).hexdigest()",
            ),
            cwe_id="CWE-327",
            confidence=Confidence.MEDIUM,
        ),
    ]


class TestSecurityScan:
    """Test security scan command."""

    @patch("specify_cli.security.adapters.semgrep.SemgrepAdapter")
    @patch("specify_cli.security.orchestrator.ScannerOrchestrator")
    def test_scan_command_success(
        self, mock_orchestrator_class, mock_adapter_class, sample_findings
    ):
        """Test successful scan with findings."""
        # Arrange
        mock_adapter = MagicMock()
        mock_adapter.name = "Semgrep"
        mock_adapter.is_available.return_value = True
        mock_adapter_class.return_value = mock_adapter

        mock_orchestrator = MagicMock()
        mock_orchestrator.scan.return_value = sample_findings
        mock_orchestrator.list_scanners.return_value = ["semgrep"]
        mock_orchestrator_class.return_value = mock_orchestrator

        # Act
        result = runner.invoke(app, ["security", "scan", ".", "--fail-on", "critical"])

        # Assert
        assert result.exit_code == 0  # No critical findings
        assert "3 findings" in result.stdout or "Total: 3" in result.stdout

    @patch("specify_cli.security.adapters.semgrep.SemgrepAdapter")
    @patch("specify_cli.security.orchestrator.ScannerOrchestrator")
    def test_scan_command_fails_on_threshold(
        self, mock_orchestrator_class, mock_adapter_class, sample_findings
    ):
        """Test scan exits 1 when findings exceed threshold."""
        # Arrange
        mock_adapter = MagicMock()
        mock_adapter.name = "Semgrep"
        mock_adapter.is_available.return_value = True
        mock_adapter_class.return_value = mock_adapter

        mock_orchestrator = MagicMock()
        mock_orchestrator.scan.return_value = sample_findings
        mock_orchestrator.list_scanners.return_value = ["semgrep"]
        mock_orchestrator_class.return_value = mock_orchestrator

        # Act
        result = runner.invoke(app, ["security", "scan", ".", "--fail-on", "high"])

        # Assert
        assert result.exit_code == 1
        assert "findings at or above high" in result.stdout

    @patch("specify_cli.security.adapters.semgrep.SemgrepAdapter")
    @patch("specify_cli.security.orchestrator.ScannerOrchestrator")
    def test_scan_command_no_findings(
        self, mock_orchestrator_class, mock_adapter_class
    ):
        """Test scan with no findings."""
        # Arrange
        mock_adapter = MagicMock()
        mock_adapter.name = "Semgrep"
        mock_adapter.is_available.return_value = True
        mock_adapter_class.return_value = mock_adapter

        mock_orchestrator = MagicMock()
        mock_orchestrator.scan.return_value = []
        mock_orchestrator.list_scanners.return_value = ["semgrep"]
        mock_orchestrator_class.return_value = mock_orchestrator

        # Act
        result = runner.invoke(app, ["security", "scan", "."])

        # Assert
        assert result.exit_code == 0
        assert "No security issues found" in result.stdout

    @patch("specify_cli.security.adapters.semgrep.SemgrepAdapter")
    @patch("specify_cli.security.orchestrator.ScannerOrchestrator")
    def test_scan_command_json_output(
        self, mock_orchestrator_class, mock_adapter_class, sample_findings, tmp_path
    ):
        """Test scan with JSON output format."""
        # Arrange
        mock_adapter = MagicMock()
        mock_adapter.name = "Semgrep"
        mock_adapter.is_available.return_value = True
        mock_adapter_class.return_value = mock_adapter

        mock_orchestrator = MagicMock()
        mock_orchestrator.scan.return_value = sample_findings
        mock_orchestrator.list_scanners.return_value = ["semgrep"]
        mock_orchestrator_class.return_value = mock_orchestrator

        output_file = tmp_path / "findings.json"

        # Act
        result = runner.invoke(
            app,
            ["security", "scan", ".", "--format", "json", "-o", str(output_file)],
        )

        # Assert
        assert result.exit_code == 1  # Has high severity findings
        assert output_file.exists()

        data = json.loads(output_file.read_text())
        assert "findings" in data
        assert len(data["findings"]) == 3

    @patch("specify_cli.security.adapters.semgrep.SemgrepAdapter")
    @patch("specify_cli.security.orchestrator.ScannerOrchestrator")
    def test_scan_command_sarif_output(
        self, mock_orchestrator_class, mock_adapter_class, sample_findings, tmp_path
    ):
        """Test scan with SARIF output format."""
        # Arrange
        mock_adapter = MagicMock()
        mock_adapter.name = "Semgrep"
        mock_adapter.is_available.return_value = True
        mock_adapter_class.return_value = mock_adapter

        mock_orchestrator = MagicMock()
        mock_orchestrator.scan.return_value = sample_findings
        mock_orchestrator.list_scanners.return_value = ["semgrep"]
        mock_orchestrator_class.return_value = mock_orchestrator

        output_file = tmp_path / "findings.sarif"

        # Act
        result = runner.invoke(
            app,
            ["security", "scan", ".", "--format", "sarif", "-o", str(output_file)],
        )

        # Assert
        assert result.exit_code == 1
        assert output_file.exists()

        data = json.loads(output_file.read_text())
        assert data["version"] == "2.1.0"
        assert "$schema" in data

    def test_scan_command_invalid_severity(self):
        """Test scan with invalid severity level."""
        # Act
        result = runner.invoke(app, ["security", "scan", ".", "--fail-on", "invalid"])

        # Assert
        assert result.exit_code == 2
        assert "Invalid severity level" in result.stdout

    @patch("specify_cli.security.adapters.semgrep.SemgrepAdapter")
    def test_scan_command_tool_not_available(self, mock_adapter_class):
        """Test scan when tool is not available."""
        # Arrange
        mock_adapter = MagicMock()
        mock_adapter.name = "Semgrep"
        mock_adapter.is_available.return_value = False
        mock_adapter.get_install_instructions.return_value = (
            "Install with: pip install semgrep"
        )
        mock_adapter_class.return_value = mock_adapter

        # Act
        result = runner.invoke(app, ["security", "scan", "."])

        # Assert
        assert result.exit_code == 2
        assert "not available" in result.stdout


class TestSecurityTriage:
    """Test security triage command (placeholder)."""

    def test_triage_command_placeholder(self, tmp_path):
        """Test triage command shows coming soon message."""
        # Arrange
        findings_file = tmp_path / "findings.json"
        findings_file.write_text('{"findings": []}')

        # Act
        result = runner.invoke(app, ["security", "triage", str(findings_file)])

        # Assert
        assert result.exit_code == 0
        assert "Phase 2" in result.stdout


class TestSecurityFix:
    """Test security fix command (placeholder)."""

    def test_fix_command_placeholder(self):
        """Test fix command shows coming soon message."""
        # Act
        result = runner.invoke(app, ["security", "fix", "SEMGREP-001", "--dry-run"])

        # Assert
        assert result.exit_code == 0
        assert "Phase 2" in result.stdout


class TestSecurityAudit:
    """Test security audit command (placeholder)."""

    def test_audit_command_placeholder(self):
        """Test audit command shows coming soon message."""
        # Act
        result = runner.invoke(app, ["security", "audit", "."])

        # Assert
        assert result.exit_code == 0
        assert "Phase 2" in result.stdout


class TestExitCodes:
    """Test exit code behavior."""

    @patch("specify_cli.security.adapters.semgrep.SemgrepAdapter")
    @patch("specify_cli.security.orchestrator.ScannerOrchestrator")
    def test_exit_code_0_no_findings(self, mock_orchestrator_class, mock_adapter_class):
        """Test exit code 0 when no findings."""
        # Arrange
        mock_adapter = MagicMock()
        mock_adapter.name = "Semgrep"
        mock_adapter.is_available.return_value = True
        mock_adapter_class.return_value = mock_adapter

        mock_orchestrator = MagicMock()
        mock_orchestrator.scan.return_value = []
        mock_orchestrator.list_scanners.return_value = ["semgrep"]
        mock_orchestrator_class.return_value = mock_orchestrator

        # Act
        result = runner.invoke(app, ["security", "scan", "."])

        # Assert
        assert result.exit_code == 0

    @patch("specify_cli.security.adapters.semgrep.SemgrepAdapter")
    @patch("specify_cli.security.orchestrator.ScannerOrchestrator")
    def test_exit_code_1_findings_above_threshold(
        self, mock_orchestrator_class, mock_adapter_class, sample_findings
    ):
        """Test exit code 1 when findings exceed threshold."""
        # Arrange
        mock_adapter = MagicMock()
        mock_adapter.name = "Semgrep"
        mock_adapter.is_available.return_value = True
        mock_adapter_class.return_value = mock_adapter

        mock_orchestrator = MagicMock()
        mock_orchestrator.scan.return_value = sample_findings
        mock_orchestrator.list_scanners.return_value = ["semgrep"]
        mock_orchestrator_class.return_value = mock_orchestrator

        # Act
        result = runner.invoke(app, ["security", "scan", ".", "--fail-on", "medium"])

        # Assert
        assert result.exit_code == 1

    def test_exit_code_2_error(self):
        """Test exit code 2 on error."""
        # Act - invalid severity triggers error
        result = runner.invoke(app, ["security", "scan", ".", "--fail-on", "invalid"])

        # Assert
        assert result.exit_code == 2
