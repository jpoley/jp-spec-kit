"""Tests for Security Scanner MCP Server.

This module tests the MCP server implementation, verifying:
1. Tool invocations (scan, triage, fix)
2. Resource queries (findings, status, config)
3. NO LLM API CALLS (only subprocess and file operations)
4. Error handling and edge cases

See ADR-008 for architectural context.
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from specify_cli.security.models import Confidence, Finding, Location, Severity


# Import MCP server module
import specify_cli.security.mcp_server as mcp_server


@pytest.fixture
def temp_project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory with security findings."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()

    # Create docs/security directory
    security_dir = project_dir / "docs" / "security"
    security_dir.mkdir(parents=True)

    # Create sample findings file
    findings_data = {
        "findings": [
            {
                "id": "SEMGREP-001",
                "scanner": "semgrep",
                "severity": "high",
                "title": "SQL Injection",
                "description": "Potential SQL injection vulnerability",
                "location": {
                    "file": "app.py",
                    "line_start": 42,
                    "line_end": 45,
                    "code_snippet": 'query = f"SELECT * FROM users WHERE id = {user_id}"',
                },
                "cwe_id": "CWE-89",
                "confidence": "high",
            },
            {
                "id": "SEMGREP-002",
                "scanner": "semgrep",
                "severity": "critical",
                "title": "Hardcoded Secret",
                "description": "API key hardcoded in source",
                "location": {
                    "file": "config.py",
                    "line_start": 10,
                    "line_end": 10,
                    "code_snippet": "API_KEY = 'sk-1234567890abcdef'",
                },
                "cwe_id": "CWE-798",
                "confidence": "high",
            },
        ],
        "metadata": {
            "scanners_used": ["semgrep"],
            "total_count": 2,
        },
    }

    findings_file = security_dir / "scan-results.json"
    with findings_file.open("w") as f:
        json.dump(findings_data, f)

    return project_dir


@pytest.fixture
def mock_orchestrator():
    """Mock scanner orchestrator to avoid subprocess calls."""
    with patch.object(mcp_server, "_get_orchestrator") as mock:
        orchestrator = Mock()
        orchestrator.list_scanners.return_value = ["semgrep"]
        orchestrator.scan.return_value = [
            Finding(
                id="SEMGREP-001",
                scanner="semgrep",
                severity=Severity.HIGH,
                title="SQL Injection",
                description="Potential SQL injection",
                location=Location(
                    file=Path("app.py"),
                    line_start=42,
                    line_end=45,
                    code_snippet='query = f"SELECT * FROM users WHERE id = {user_id}"',
                ),
                cwe_id="CWE-89",
                confidence=Confidence.HIGH,
            )
        ]
        mock.return_value = orchestrator
        yield orchestrator


@pytest.fixture(autouse=True)
def set_project_root(temp_project_dir: Path):
    """Set PROJECT_ROOT for all tests."""
    original_root = mcp_server.PROJECT_ROOT
    mcp_server.PROJECT_ROOT = temp_project_dir
    mcp_server._orchestrator = None  # Reset orchestrator
    yield
    mcp_server.PROJECT_ROOT = original_root
    mcp_server._orchestrator = None


class TestSecurityScanTool:
    """Tests for security_scan tool."""

    @pytest.mark.asyncio
    async def test_security_scan_success(self, mock_orchestrator):
        """Test successful security scan."""
        result = await mcp_server.security_scan(target=".", scanners=["semgrep"])

        # Verify result structure
        assert "findings_count" in result
        assert "by_severity" in result
        assert "findings_file" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_security_scan_counts_by_severity(self, mock_orchestrator):
        """Test that scan results include severity counts."""
        result = await mcp_server.security_scan(target=".")

        # Verify severity breakdown
        assert "by_severity" in result
        by_severity = result["by_severity"]

        assert "critical" in by_severity
        assert "high" in by_severity
        assert "medium" in by_severity
        assert "low" in by_severity
        assert "info" in by_severity

        # All counts should be non-negative integers
        for severity, count in by_severity.items():
            assert isinstance(count, int)
            assert count >= 0

    @pytest.mark.asyncio
    async def test_security_scan_with_multiple_scanners(self, mock_orchestrator):
        """Test scan with multiple scanners."""
        # Update mock to return both scanners as available
        mock_orchestrator.list_scanners.return_value = ["semgrep", "trivy"]

        result = await mcp_server.security_scan(
            target=".", scanners=["semgrep", "trivy"]
        )

        assert result["metadata"]["scanners_used"] == ["semgrep", "trivy"]

    @pytest.mark.asyncio
    async def test_security_scan_includes_fail_on_result(self, mock_orchestrator):
        """Test that scan includes should_fail and fail_on in result."""
        result = await mcp_server.security_scan(
            target=".", fail_on=["high", "critical"]
        )

        # Verify fail_on fields are included
        assert "should_fail" in result
        assert "fail_on" in result
        assert result["fail_on"] == ["high", "critical"]

        # Since mock returns HIGH severity finding, should_fail should be True
        assert result["should_fail"] is True

    @pytest.mark.asyncio
    async def test_security_scan_should_fail_false_when_no_matching_severity(
        self, mock_orchestrator
    ):
        """Test that should_fail is False when no findings match fail_on severities."""
        # Reconfigure mock to return only LOW severity findings
        mock_orchestrator.scan.return_value = [
            Finding(
                id="SEMGREP-003",
                scanner="semgrep",
                severity=Severity.LOW,
                title="Minor Issue",
                description="A low priority issue",
                location=Location(
                    file=Path("app.py"),
                    line_start=10,
                    line_end=10,
                    code_snippet="x = 1",
                ),
                cwe_id="CWE-000",
                confidence=Confidence.LOW,
            )
        ]

        result = await mcp_server.security_scan(
            target=".", fail_on=["high", "critical"]
        )

        # With only LOW severity finding, should_fail should be False
        assert result["should_fail"] is False


class TestSecurityTriageTool:
    """Tests for security_triage tool."""

    @pytest.mark.asyncio
    async def test_security_triage_returns_skill_instruction(self):
        """Test that triage returns skill invocation instruction (NO LLM CALL)."""
        result = await mcp_server.security_triage()

        # Verify it returns skill invocation instruction
        assert result["action"] == "invoke_skill"
        assert result["skill"] == ".claude/skills/security-triage.md"
        assert "input_file" in result
        assert "output_file" in result
        assert "instruction" in result

    @pytest.mark.asyncio
    async def test_security_triage_checks_findings_exist(self, temp_project_dir: Path):
        """Test that triage checks if findings file exists."""
        # Test with existing findings file
        result = await mcp_server.security_triage()
        assert "action" in result
        assert result["action"] == "invoke_skill"

        # Test with non-existent findings file
        findings_file = temp_project_dir / "docs" / "security" / "scan-results.json"
        findings_file.unlink()

        result = await mcp_server.security_triage()
        assert "error" in result
        assert "suggestion" in result


class TestSecurityFixTool:
    """Tests for security_fix tool."""

    @pytest.mark.asyncio
    async def test_security_fix_returns_skill_instruction(self, temp_project_dir: Path):
        """Test that fix returns skill invocation instruction (NO LLM CALL)."""
        # Create triage results file
        triage_file = temp_project_dir / "docs" / "security" / "triage-results.json"
        with triage_file.open("w") as f:
            json.dump({"true_positives": 2, "false_positives": 0}, f)

        result = await mcp_server.security_fix()

        # Verify it returns skill invocation instruction
        assert result["action"] == "invoke_skill"
        assert result["skill"] == ".claude/skills/security-fix.md"
        assert "input_file" in result
        assert "output_file" in result
        assert "instruction" in result

    @pytest.mark.asyncio
    async def test_security_fix_with_specific_findings(self, temp_project_dir: Path):
        """Test fix with specific finding IDs."""
        # Create triage results file
        triage_file = temp_project_dir / "docs" / "security" / "triage-results.json"
        with triage_file.open("w") as f:
            json.dump({"true_positives": 2}, f)

        result = await mcp_server.security_fix(
            finding_ids=["SEMGREP-001", "SEMGREP-002"]
        )

        assert "filter" in result
        assert result["filter"]["finding_ids"] == ["SEMGREP-001", "SEMGREP-002"]

    @pytest.mark.asyncio
    async def test_security_fix_checks_triage_exists(self):
        """Test that fix checks if triage results exist."""
        result = await mcp_server.security_fix()

        assert "error" in result
        assert "suggestion" in result


class TestListFindingsResource:
    """Tests for security://findings resource."""

    @pytest.mark.asyncio
    async def test_list_findings_success(self):
        """Test listing all findings."""
        result_str = await mcp_server.list_findings()
        results = json.loads(result_str)

        assert isinstance(results, list)
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_list_findings_returns_all(self):
        """Test that list_findings returns all findings (client-side filtering)."""
        result_str = await mcp_server.list_findings()
        results = json.loads(result_str)

        # Should return all findings (2 in fixture)
        assert len(results) == 2

        # Verify both findings are present
        ids = [f["id"] for f in results]
        assert "SEMGREP-001" in ids
        assert "SEMGREP-002" in ids

    @pytest.mark.asyncio
    async def test_list_findings_empty(self, temp_project_dir: Path):
        """Test listing findings when no scan results exist."""
        # Remove findings file
        findings_file = temp_project_dir / "docs" / "security" / "scan-results.json"
        findings_file.unlink()

        result_str = await mcp_server.list_findings()
        results = json.loads(result_str)

        assert results == []


class TestGetFindingResource:
    """Tests for security://findings/{id} resource."""

    @pytest.mark.asyncio
    async def test_get_finding_by_id_success(self):
        """Test getting specific finding by ID."""
        result_str = await mcp_server.get_finding(id="SEMGREP-001")
        result = json.loads(result_str)

        assert result["id"] == "SEMGREP-001"
        assert result["title"] == "SQL Injection"

    @pytest.mark.asyncio
    async def test_get_finding_by_id_not_found(self):
        """Test getting non-existent finding."""
        result_str = await mcp_server.get_finding(id="NONEXISTENT")
        result = json.loads(result_str)

        assert "error" in result


class TestStatusResource:
    """Tests for security://status resource."""

    @pytest.mark.asyncio
    async def test_get_status_with_findings(self):
        """Test getting security status with findings."""
        result_str = await mcp_server.get_status()
        result = json.loads(result_str)

        assert "total_findings" in result
        assert "by_severity" in result
        assert "security_posture" in result

        assert result["total_findings"] == 2
        assert result["by_severity"]["critical"] == 1
        assert result["by_severity"]["high"] == 1

    @pytest.mark.asyncio
    async def test_get_status_posture_calculation(self):
        """Test security posture calculation."""
        result_str = await mcp_server.get_status()
        result = json.loads(result_str)

        # Should be "critical" because we have critical findings
        assert result["security_posture"] == "critical"

    @pytest.mark.asyncio
    async def test_get_status_with_triage(self, temp_project_dir: Path):
        """Test status includes triage results if available."""
        # Create triage results
        triage_file = temp_project_dir / "docs" / "security" / "triage-results.json"
        with triage_file.open("w") as f:
            json.dump({"true_positives": 1, "false_positives": 1}, f)

        result_str = await mcp_server.get_status()
        result = json.loads(result_str)

        assert result["triage_status"] == "completed"
        assert result["true_positives"] == 1
        assert result["false_positives"] == 1


class TestConfigResource:
    """Tests for security://config resource."""

    @pytest.mark.asyncio
    async def test_get_config(self, mock_orchestrator):
        """Test getting scanner configuration."""
        result_str = await mcp_server.get_config()
        result = json.loads(result_str)

        assert "available_scanners" in result
        assert "default_scanners" in result
        assert "fail_on" in result
        assert "findings_directory" in result

        assert "semgrep" in result["available_scanners"]
        assert result["fail_on"] == ["critical", "high"]


class TestNoLLMCalls:
    """CRITICAL: Integration tests verifying NO LLM API calls."""

    @pytest.mark.asyncio
    async def test_all_tools_no_llm_calls(
        self, mock_orchestrator, temp_project_dir: Path
    ):
        """Test that ALL tools make ZERO LLM API calls."""
        # Create triage file for fix tool
        triage_file = temp_project_dir / "docs" / "security" / "triage-results.json"
        with triage_file.open("w") as f:
            json.dump({"true_positives": 2}, f)

        # Mock ANY potential LLM client imports
        with patch(
            "specify_cli.security.triage.classifiers.base.LLMClient"
        ) as mock_llm:
            # Test scan tool
            await mcp_server.security_scan(target=".")

            # Test triage tool
            await mcp_server.security_triage()

            # Test fix tool
            await mcp_server.security_fix()

            # Verify ZERO LLM calls
            mock_llm.assert_not_called()

    @pytest.mark.asyncio
    async def test_all_resources_no_llm_calls(self):
        """Test that ALL resources make ZERO LLM API calls."""
        with patch(
            "specify_cli.security.triage.classifiers.base.LLMClient"
        ) as mock_llm:
            # Test findings list
            await mcp_server.list_findings()

            # Test finding by ID
            await mcp_server.get_finding(id="SEMGREP-001")

            # Test status
            await mcp_server.get_status()

            # Test config
            await mcp_server.get_config()

            # Verify ZERO LLM calls
            mock_llm.assert_not_called()


class TestPathValidation:
    """Tests for path traversal protection."""

    def test_validate_path_accepts_relative_path(self, tmp_path: Path):
        """Test that relative paths within base are accepted."""
        # Create a target directory
        target = tmp_path / "subdir"
        target.mkdir()

        result = mcp_server._validate_path("subdir", tmp_path)
        assert result == target.resolve()
        # Verify path is actually contained within base directory
        assert result.is_relative_to(tmp_path.resolve())

    def test_validate_path_rejects_absolute_path(self, tmp_path: Path):
        """Test that absolute paths are rejected."""
        with pytest.raises(ValueError, match="Absolute paths not allowed"):
            mcp_server._validate_path("/etc/passwd", tmp_path)

    def test_validate_path_rejects_path_traversal(self, tmp_path: Path):
        """Test that path traversal attempts are rejected."""
        with pytest.raises(ValueError, match="Path traversal detected"):
            mcp_server._validate_path("../../../etc/passwd", tmp_path)

    def test_validate_path_rejects_double_traversal(self, tmp_path: Path):
        """Test that double dot traversal is rejected."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        with pytest.raises(ValueError, match="Path traversal detected"):
            mcp_server._validate_path("subdir/../../etc", tmp_path)


class TestInputValidation:
    """Tests for input validation functions."""

    def test_validate_scanners_accepts_valid(self):
        """Test valid scanner names are accepted."""
        result = mcp_server._validate_scanners(
            ["semgrep", "trivy"], ["semgrep", "trivy", "bandit"]
        )
        assert result == ["semgrep", "trivy"]

    def test_validate_scanners_rejects_invalid(self):
        """Test invalid scanner names are rejected."""
        with pytest.raises(ValueError, match="Invalid scanner names"):
            mcp_server._validate_scanners(["semgrep", "evil_scanner"], ["semgrep"])

    def test_validate_scanners_rejects_unavailable(self):
        """Test unavailable scanner names are rejected."""
        with pytest.raises(ValueError, match="Scanners not available"):
            mcp_server._validate_scanners(
                ["semgrep", "trivy"],
                ["semgrep"],  # trivy not available
            )

    def test_validate_scanners_returns_available_on_none(self):
        """Test None returns all available scanners from orchestrator.

        Note: This tests the _validate_scanners helper directly.
        Integration with orchestrator.list_scanners() is tested in
        TestSecurityScanTool.test_security_scan_success.
        """
        available = ["semgrep", "trivy"]
        result = mcp_server._validate_scanners(None, available)
        assert result == available

    def test_validate_severities_accepts_valid(self):
        """Test valid severity levels are accepted."""
        result = mcp_server._validate_severities(["critical", "high"])
        assert result == ["critical", "high"]

    def test_validate_severities_rejects_invalid(self):
        """Test invalid severity levels are rejected."""
        with pytest.raises(ValueError, match="Invalid severities"):
            mcp_server._validate_severities(["critical", "extreme"])

    def test_validate_severities_returns_default_on_none(self):
        """Test None returns default severities."""
        result = mcp_server._validate_severities(None)
        assert result == ["critical", "high"]


class TestSecurityScanValidation:
    """Tests for security scan input validation."""

    @pytest.fixture
    def mock_orchestrator_with_path(self, tmp_path: Path):
        """Mock scanner orchestrator with temp path."""
        # Set PROJECT_ROOT to tmp_path
        original_root = mcp_server.PROJECT_ROOT
        mcp_server.PROJECT_ROOT = tmp_path

        # Create target directory
        target = tmp_path / "src"
        target.mkdir()

        with patch.object(mcp_server, "_get_orchestrator") as mock:
            orchestrator = Mock()
            orchestrator.list_scanners.return_value = ["semgrep"]
            orchestrator.scan.return_value = []
            mock.return_value = orchestrator
            yield tmp_path

        # Restore original
        mcp_server.PROJECT_ROOT = original_root

    @pytest.mark.asyncio
    async def test_scan_rejects_path_traversal(self, mock_orchestrator_with_path):
        """Test scan rejects path traversal attempts."""
        result = await mcp_server.security_scan(target="../../../etc")

        assert "error" in result
        assert "Invalid target path" in result["error"]
        assert result["findings_count"] == 0

    @pytest.mark.asyncio
    async def test_scan_rejects_absolute_path(self, mock_orchestrator_with_path):
        """Test scan rejects absolute paths."""
        result = await mcp_server.security_scan(target="/etc/passwd")

        assert "error" in result
        assert "Invalid target path" in result["error"]
        assert result["findings_count"] == 0

    @pytest.mark.asyncio
    async def test_scan_rejects_invalid_scanner(self, mock_orchestrator_with_path):
        """Test scan rejects invalid scanner names."""
        result = await mcp_server.security_scan(target="src", scanners=["evil_scanner"])

        assert "error" in result
        assert "Invalid scanners" in result["error"]

    @pytest.mark.asyncio
    async def test_scan_rejects_nonexistent_target(self, mock_orchestrator_with_path):
        """Test scan handles nonexistent target."""
        result = await mcp_server.security_scan(target="nonexistent")

        assert "error" in result
        assert "does not exist" in result["error"]
