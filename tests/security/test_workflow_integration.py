"""Tests for security workflow integration."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from specify_cli.security.integrations.workflow import (
    SecurityGateResult,
    SecurityWorkflowIntegration,
    create_security_gate,
)
from specify_cli.security.models import (
    Confidence,
    Finding,
    Location,
    Severity,
)


@pytest.fixture
def sample_findings():
    """Create sample security findings for testing."""
    return [
        Finding(
            id="FIND-001",
            scanner="semgrep",
            severity=Severity.CRITICAL,
            confidence=Confidence.HIGH,
            title="SQL Injection in Authentication",
            description="User input directly concatenated into SQL query.",
            location=Location(
                file=Path("src/auth/login.py"),
                line_start=42,
                line_end=44,
                code_snippet="query = f\"SELECT * FROM users WHERE username = '{username}'\"",
            ),
            cwe_id="CWE-89",
            remediation="Use parameterized queries",
            references=[
                "https://cwe.mitre.org/data/definitions/89.html",
                "https://owasp.org/www-community/attacks/SQL_Injection",
            ],
        ),
        Finding(
            id="FIND-002",
            scanner="semgrep",
            severity=Severity.HIGH,
            confidence=Confidence.HIGH,
            title="XSS in User Profile",
            description="User-controlled data rendered without escaping.",
            location=Location(
                file=Path("src/web/profile.py"),
                line_start=67,
                line_end=68,
                code_snippet="return f'<div>{user.bio}</div>'",
            ),
            cwe_id="CWE-79",
            remediation="Use template engine with auto-escaping",
            references=["https://cwe.mitre.org/data/definitions/79.html"],
        ),
        Finding(
            id="FIND-003",
            scanner="bandit",
            severity=Severity.MEDIUM,
            confidence=Confidence.MEDIUM,
            title="Hardcoded Secret",
            description="API key hardcoded in source code.",
            location=Location(
                file=Path("src/config/settings.py"),
                line_start=12,
                line_end=12,
                code_snippet='API_KEY = "sk_test_1234567890"',
            ),
            cwe_id="CWE-798",
            remediation="Move secret to environment variable",
            references=["https://cwe.mitre.org/data/definitions/798.html"],
        ),
    ]


class TestSecurityGateResult:
    """Test SecurityGateResult dataclass."""

    def test_security_gate_result_creation(self, sample_findings):
        """Test creating SecurityGateResult."""
        result = SecurityGateResult(
            passed=False,
            findings_count=3,
            critical_count=1,
            high_count=1,
            blocking_findings=[sample_findings[0]],
            message="Security gate failed: 1 blocking findings",
        )

        assert result.passed is False
        assert result.findings_count == 3
        assert result.critical_count == 1
        assert result.high_count == 1
        assert len(result.blocking_findings) == 1
        assert "Security gate failed" in result.message

    def test_security_gate_result_passed(self):
        """Test SecurityGateResult for passing gate."""
        result = SecurityGateResult(
            passed=True,
            findings_count=0,
            critical_count=0,
            high_count=0,
            blocking_findings=[],
            message="Security gate passed",
        )

        assert result.passed is True
        assert result.findings_count == 0
        assert len(result.blocking_findings) == 0


class TestSecurityWorkflowIntegration:
    """Test SecurityWorkflowIntegration class."""

    def test_init(self, tmp_path):
        """Test SecurityWorkflowIntegration initialization."""
        integration = SecurityWorkflowIntegration(
            backlog_cli="backlog",
            hooks_cli="specify",
            project_root=tmp_path,
        )

        assert integration.backlog_cli == "backlog"
        assert integration.hooks_cli == "specify"
        assert integration.project_root == tmp_path

    def test_init_defaults(self):
        """Test SecurityWorkflowIntegration with default values."""
        integration = SecurityWorkflowIntegration()

        assert integration.backlog_cli == "backlog"
        assert integration.hooks_cli == "specify"
        assert isinstance(integration.project_root, Path)

    def test_run_security_gate_fail_on_critical(self, sample_findings):
        """Test security gate fails on critical findings."""
        integration = SecurityWorkflowIntegration()
        result = integration.run_security_gate(
            findings=sample_findings, fail_on=["critical"]
        )

        assert result.passed is False
        assert result.findings_count == 3
        assert result.critical_count == 1
        assert result.high_count == 1
        assert len(result.blocking_findings) == 1
        assert result.blocking_findings[0].severity == Severity.CRITICAL
        assert "Security gate failed" in result.message

    def test_run_security_gate_fail_on_critical_and_high(self, sample_findings):
        """Test security gate fails on critical and high findings."""
        integration = SecurityWorkflowIntegration()
        result = integration.run_security_gate(
            findings=sample_findings, fail_on=["critical", "high"]
        )

        assert result.passed is False
        assert result.findings_count == 3
        assert result.critical_count == 1
        assert result.high_count == 1
        assert len(result.blocking_findings) == 2
        assert "Security gate failed" in result.message

    def test_run_security_gate_pass_no_blocking_findings(self, sample_findings):
        """Test security gate passes when no blocking findings."""
        # Remove critical and high findings
        medium_only = [f for f in sample_findings if f.severity == Severity.MEDIUM]

        integration = SecurityWorkflowIntegration()
        result = integration.run_security_gate(
            findings=medium_only, fail_on=["critical", "high"]
        )

        assert result.passed is True
        assert result.findings_count == 1
        assert result.critical_count == 0
        assert result.high_count == 0
        assert len(result.blocking_findings) == 0
        assert "Security gate passed" in result.message

    def test_run_security_gate_default_fail_on(self, sample_findings):
        """Test security gate with default fail_on (critical only)."""
        integration = SecurityWorkflowIntegration()
        result = integration.run_security_gate(findings=sample_findings)

        # Default should be fail_on=["critical"]
        assert result.passed is False
        assert len(result.blocking_findings) == 1
        assert result.blocking_findings[0].severity == Severity.CRITICAL

    def test_run_security_gate_empty_findings(self):
        """Test security gate with no findings."""
        integration = SecurityWorkflowIntegration()
        result = integration.run_security_gate(findings=[], fail_on=["critical"])

        assert result.passed is True
        assert result.findings_count == 0
        assert len(result.blocking_findings) == 0

    @patch("subprocess.run")
    def test_create_remediation_tasks(self, mock_run, sample_findings, tmp_path):
        """Test creating remediation tasks."""
        # Mock subprocess.run to simulate backlog CLI
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Created task task-301\n", stderr=""
        )

        integration = SecurityWorkflowIntegration(project_root=tmp_path)
        task_ids = integration.create_remediation_tasks(
            findings=sample_findings[:1],  # Just critical finding
            feature_id="auth-system",
            auto_assign="@security-team",
        )

        # Verify subprocess was called correctly
        assert mock_run.called
        call_args = mock_run.call_args

        # Check command structure
        cmd = call_args[0][0]
        assert cmd[0] == "backlog"
        assert cmd[1] == "task"
        assert cmd[2] == "create"
        assert "Fix CRITICAL CWE-89" in cmd[3]
        assert "-p" in cmd
        assert "high" in cmd  # Critical maps to high priority
        assert "-a" in cmd
        assert "@security-team" in cmd

        # Verify task IDs returned
        assert len(task_ids) == 1
        assert task_ids[0] == "task-301"

    @patch("subprocess.run")
    def test_create_remediation_tasks_with_priority_map(
        self, mock_run, sample_findings, tmp_path
    ):
        """Test creating remediation tasks with custom priority map."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Created task task-302\n", stderr=""
        )

        custom_priority = {
            "critical": "critical",
            "high": "high",
            "medium": "low",
            "low": "low",
        }

        integration = SecurityWorkflowIntegration(project_root=tmp_path)
        task_ids = integration.create_remediation_tasks(
            findings=[sample_findings[2]],  # Medium severity
            priority_map=custom_priority,
        )

        # Verify priority mapping
        cmd = mock_run.call_args[0][0]
        priority_idx = cmd.index("-p")
        assert cmd[priority_idx + 1] == "low"

        assert len(task_ids) == 1

    @patch("subprocess.run")
    @patch("builtins.print")
    def test_create_remediation_tasks_handle_error(
        self, mock_print, mock_run, sample_findings, tmp_path
    ):
        """Test handling errors when creating tasks."""
        # Simulate backlog CLI failure for second finding
        from subprocess import CalledProcessError

        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="Created task task-301\n", stderr=""),
            CalledProcessError(
                returncode=1, cmd=["backlog"], stderr="Task creation failed"
            ),
        ]

        integration = SecurityWorkflowIntegration(project_root=tmp_path)
        task_ids = integration.create_remediation_tasks(
            findings=sample_findings[:2],  # Two findings
        )

        # Should still return successful task IDs
        assert len(task_ids) == 1
        assert task_ids[0] == "task-301"

        # Check warning was printed
        mock_print.assert_called()
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Warning: Failed to create task" in call for call in print_calls)

    @patch("subprocess.run")
    def test_emit_security_event(self, mock_run, tmp_path):
        """Test emitting security event."""
        integration = SecurityWorkflowIntegration(project_root=tmp_path)
        integration.emit_security_event(
            event_type="scan.completed",
            feature_id="auth-system",
            task_id="task-216",
        )

        # Verify subprocess was called
        assert mock_run.called
        call_args = mock_run.call_args

        # Check command structure
        cmd = call_args[0][0]
        assert cmd[0] == "specify"
        assert cmd[1] == "hooks"
        assert cmd[2] == "emit"
        assert cmd[3] == "security.scan.completed"
        assert "--spec-id" in cmd
        assert "auth-system" in cmd
        assert "--task-id" in cmd
        assert "task-216" in cmd

    @patch("subprocess.run")
    def test_emit_security_event_without_optional_params(self, mock_run, tmp_path):
        """Test emitting event without optional parameters."""
        integration = SecurityWorkflowIntegration(project_root=tmp_path)
        integration.emit_security_event(event_type="gate.passed")

        # Verify subprocess was called with minimal args
        assert mock_run.called
        cmd = mock_run.call_args[0][0]
        assert "security.gate.passed" in cmd
        assert "--spec-id" not in cmd
        assert "--task-id" not in cmd

    @patch("subprocess.run")
    def test_emit_security_event_handle_error(self, mock_run, tmp_path, capsys):
        """Test handling errors when emitting events."""
        # Simulate hooks CLI failure
        mock_run.side_effect = Exception("Hooks not configured")

        integration = SecurityWorkflowIntegration(project_root=tmp_path)
        # Should not raise exception
        integration.emit_security_event(event_type="scan.completed")

        # Check warning was printed
        captured = capsys.readouterr()
        assert "Warning: Failed to emit security event" in captured.out

    def test_build_task_description(self, sample_findings):
        """Test building task description from finding."""
        integration = SecurityWorkflowIntegration()
        finding = sample_findings[0]  # SQL Injection finding

        description = integration._build_task_description(finding)

        # Verify description contains key elements
        assert "Security Finding: SQL Injection in Authentication" in description
        assert "CRITICAL" in description
        assert "CWE-89" in description
        assert "semgrep" in description
        assert "src/auth/login.py:42-44" in description
        assert "User input directly concatenated" in description
        assert "Use parameterized queries" in description
        assert "https://cwe.mitre.org/data/definitions/89.html" in description

    def test_build_task_description_without_optional_fields(self):
        """Test building description for finding without optional fields."""
        finding = Finding(
            id="FIND-004",
            scanner="test",
            severity=Severity.LOW,
            confidence=Confidence.LOW,
            title="Test Finding",
            description="Test description",
            location=Location(
                file=Path("test.py"),
                line_start=1,
                line_end=1,
                code_snippet="# test",
            ),
            cwe_id=None,
            remediation=None,
            references=[],
        )

        integration = SecurityWorkflowIntegration()
        description = integration._build_task_description(finding)

        # Should handle None values gracefully
        assert "Test Finding" in description
        assert "CWE:** N/A" in description
        assert "Remediation Guidance" not in description
        assert "References" not in description


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    def test_create_security_gate(self, sample_findings):
        """Test create_security_gate convenience function."""
        result = create_security_gate(
            findings=sample_findings, fail_on=["critical", "high"]
        )

        assert isinstance(result, SecurityGateResult)
        assert result.passed is False
        assert result.findings_count == 3
        assert len(result.blocking_findings) == 2

    def test_create_security_gate_default_fail_on(self, sample_findings):
        """Test create_security_gate with default fail_on."""
        result = create_security_gate(findings=sample_findings)

        # Default should be fail_on=["critical"]
        assert isinstance(result, SecurityGateResult)
        assert result.passed is False
        assert len(result.blocking_findings) == 1
        assert result.blocking_findings[0].severity == Severity.CRITICAL


@pytest.mark.integration
class TestWorkflowIntegrationEndToEnd:
    """End-to-end integration tests for workflow integration."""

    @patch("subprocess.run")
    def test_full_security_workflow(self, mock_run, sample_findings, tmp_path):
        """Test complete security workflow integration."""
        # Mock subprocess calls
        task_creation_response = MagicMock(
            returncode=0, stdout="Created task task-301\n", stderr=""
        )
        event_emission_response = MagicMock(returncode=0, stdout="", stderr="")

        mock_run.side_effect = [
            task_creation_response,
            event_emission_response,
        ]

        integration = SecurityWorkflowIntegration(project_root=tmp_path)

        # Step 1: Run security gate
        gate_result = integration.run_security_gate(
            findings=sample_findings, fail_on=["critical"]
        )

        assert gate_result.passed is False

        # Step 2: Create remediation tasks for blocking findings
        task_ids = integration.create_remediation_tasks(
            findings=gate_result.blocking_findings,
            feature_id="auth-system",
            auto_assign="@security-team",
        )

        assert len(task_ids) == 1
        assert task_ids[0] == "task-301"

        # Step 3: Emit security event
        integration.emit_security_event(
            event_type="gate.failed",
            feature_id="auth-system",
        )

        # Verify all subprocess calls were made
        assert mock_run.call_count == 2
