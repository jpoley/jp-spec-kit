"""Tests for validation_agents module."""

import json
from pathlib import Path


from specify_cli.validation_agents import (
    QAAgentDispatcher,
    QAReport,
    SecurityAgentDispatcher,
    SecurityReport,
    ValidationOrchestrator,
    ValidationStatus,
    determine_validation_outcome,
)


class TestQAAgentDispatcher:
    """Tests for QAAgentDispatcher."""

    def test_init_default_path(self):
        """Test QAAgentDispatcher initialization with default path."""
        dispatcher = QAAgentDispatcher()
        assert dispatcher.agent_definition_path.name == "quality-guardian.md"
        assert ".agents" in str(dispatcher.agent_definition_path)

    def test_init_custom_path(self):
        """Test QAAgentDispatcher initialization with custom path."""
        custom_path = Path("/tmp/custom-qa.md")
        dispatcher = QAAgentDispatcher(agent_definition_path=custom_path)
        assert dispatcher.agent_definition_path == custom_path

    def test_build_prompt_includes_task_context(self):
        """Test that build_prompt includes all task context."""
        dispatcher = QAAgentDispatcher()
        prompt = dispatcher.build_prompt(
            task_id="task-123",
            task_title="Test Feature",
            task_description="Implement test feature",
            acceptance_criteria=["AC1: Feature works", "AC2: Tests pass"],
            implementation_artifacts={
                "code_files": {"src/test.py": "def test(): pass"},
                "test_files": {"tests/test_test.py": "def test_test(): assert True"},
                "test_results": "All tests passed",
            },
        )

        # Verify task context is included
        assert "task-123" in prompt
        assert "Test Feature" in prompt
        assert "Implement test feature" in prompt
        assert "AC1: Feature works" in prompt
        assert "AC2: Tests pass" in prompt

        # Verify artifacts are included
        assert "src/test.py" in prompt
        assert "tests/test_test.py" in prompt
        assert "All tests passed" in prompt

        # Verify agent context is included
        assert "Quality Guardian" in prompt
        assert "Constructive Skepticism" in prompt

    def test_build_prompt_formats_acceptance_criteria(self):
        """Test that acceptance criteria are properly formatted."""
        dispatcher = QAAgentDispatcher()
        prompt = dispatcher.build_prompt(
            task_id="task-1",
            task_title="Test",
            task_description="Test",
            acceptance_criteria=["First AC", "Second AC", "Third AC"],
            implementation_artifacts={},
        )

        assert "1. First AC" in prompt
        assert "2. Second AC" in prompt
        assert "3. Third AC" in prompt

    def test_parse_response_json_format(self):
        """Test parsing QA agent response in JSON format."""
        dispatcher = QAAgentDispatcher()
        response = """
Here is the report:

```json
{
  "functional_test_status": "pass",
  "integration_test_status": "pass",
  "edge_case_coverage": "excellent",
  "risk_assessment": "low",
  "issues": [
    {
      "severity": "low",
      "category": "usability",
      "description": "Minor UI issue",
      "recommendation": "Fix button alignment"
    }
  ],
  "test_results": {
    "total_tests": 10,
    "passed": 10,
    "failed": 0,
    "skipped": 0
  },
  "quality_metrics": {
    "code_coverage": "95%",
    "complexity": "low",
    "maintainability": "excellent"
  }
}
```
        """

        report = dispatcher.parse_response(response)

        assert isinstance(report, QAReport)
        assert report.functional_test_status == "pass"
        assert report.integration_test_status == "pass"
        assert report.edge_case_coverage == "excellent"
        assert report.risk_assessment == "low"
        assert len(report.issues) == 1
        assert report.issues[0]["severity"] == "low"
        assert report.test_results["total_tests"] == 10
        assert report.quality_metrics["code_coverage"] == "95%"

    def test_parse_response_plain_json(self):
        """Test parsing plain JSON response without markdown."""
        dispatcher = QAAgentDispatcher()
        response = json.dumps(
            {
                "functional_test_status": "fail",
                "integration_test_status": "pass",
                "edge_case_coverage": "poor",
                "risk_assessment": "high",
                "issues": [],
                "test_results": {},
                "quality_metrics": {},
            }
        )

        report = dispatcher.parse_response(response)

        assert report.functional_test_status == "fail"
        assert report.integration_test_status == "pass"
        assert report.edge_case_coverage == "poor"
        assert report.risk_assessment == "high"

    def test_parse_response_invalid_json_fallback(self):
        """Test fallback handling for invalid JSON response."""
        dispatcher = QAAgentDispatcher()
        response = "This is not valid JSON at all"

        report = dispatcher.parse_response(response)

        # Should return default values
        assert report.functional_test_status == "unknown"
        assert report.integration_test_status == "unknown"
        assert report.edge_case_coverage == "unknown"
        assert report.risk_assessment == "unknown"
        assert report.issues == []


class TestSecurityAgentDispatcher:
    """Tests for SecurityAgentDispatcher."""

    def test_init_default_path(self):
        """Test SecurityAgentDispatcher initialization with default path."""
        dispatcher = SecurityAgentDispatcher()
        assert dispatcher.agent_definition_path.name == "secure-by-design-engineer.md"
        assert ".agents" in str(dispatcher.agent_definition_path)

    def test_init_custom_path(self):
        """Test SecurityAgentDispatcher initialization with custom path."""
        custom_path = Path("/tmp/custom-security.md")
        dispatcher = SecurityAgentDispatcher(agent_definition_path=custom_path)
        assert dispatcher.agent_definition_path == custom_path

    def test_build_prompt_includes_task_context(self):
        """Test that build_prompt includes all task context."""
        dispatcher = SecurityAgentDispatcher()
        prompt = dispatcher.build_prompt(
            task_id="task-456",
            task_title="Security Feature",
            task_description="Implement authentication",
            acceptance_criteria=["AC1: Secure auth", "AC2: No SQL injection"],
            implementation_artifacts={
                "code_files": {"src/auth.py": "def authenticate(): pass"},
                "dependencies": "fastapi==0.100.0\npyJWT==2.8.0",
                "configs": {"config.yml": "secret_key: ${SECRET_KEY}"},
            },
        )

        # Verify task context
        assert "task-456" in prompt
        assert "Security Feature" in prompt
        assert "Implement authentication" in prompt
        assert "AC1: Secure auth" in prompt
        assert "AC2: No SQL injection" in prompt

        # Verify artifacts
        assert "src/auth.py" in prompt
        assert "fastapi==0.100.0" in prompt
        assert "config.yml" in prompt

        # Verify agent context
        assert "Secure-by-Design Engineer" in prompt
        assert "Assume Breach" in prompt

    def test_build_prompt_includes_security_gate_criteria(self):
        """Test that prompt includes security gate pass/fail criteria."""
        dispatcher = SecurityAgentDispatcher()
        prompt = dispatcher.build_prompt(
            task_id="task-1",
            task_title="Test",
            task_description="Test",
            acceptance_criteria=[],
            implementation_artifacts={},
        )

        assert "SECURITY GATE CRITERIA" in prompt
        assert "FAIL if any critical vulnerabilities" in prompt

    def test_parse_response_json_format(self):
        """Test parsing Security agent response in JSON format."""
        dispatcher = SecurityAgentDispatcher()
        response = """
Security Assessment:

```json
{
  "vulnerabilities": [
    {
      "severity": "high",
      "category": "injection",
      "description": "Potential SQL injection",
      "location": "src/db.py:42",
      "cve": "N/A",
      "remediation": "Use parameterized queries",
      "exploitability": "moderate"
    }
  ],
  "compliance_status": "partial",
  "security_gate": "fail",
  "critical_count": 0,
  "high_count": 1,
  "medium_count": 2,
  "low_count": 3,
  "summary": "Found 1 high severity issue"
}
```
        """

        report = dispatcher.parse_response(response)

        assert isinstance(report, SecurityReport)
        assert len(report.vulnerabilities) == 1
        assert report.vulnerabilities[0]["severity"] == "high"
        assert report.compliance_status == "partial"
        assert report.security_gate == "fail"
        assert report.critical_count == 0
        assert report.high_count == 1
        assert report.medium_count == 2
        assert report.low_count == 3

    def test_parse_response_critical_vulnerabilities(self):
        """Test parsing response with critical vulnerabilities."""
        dispatcher = SecurityAgentDispatcher()
        response = json.dumps(
            {
                "vulnerabilities": [
                    {
                        "severity": "critical",
                        "category": "auth",
                        "description": "Authentication bypass",
                        "location": "src/auth.py:10",
                        "remediation": "Fix auth logic",
                    }
                ],
                "compliance_status": "non-compliant",
                "security_gate": "fail",
                "critical_count": 1,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
            }
        )

        report = dispatcher.parse_response(response)

        assert report.critical_count == 1
        assert report.security_gate == "fail"

    def test_parse_response_invalid_json_fallback(self):
        """Test fallback handling for invalid JSON response."""
        dispatcher = SecurityAgentDispatcher()
        response = "Not valid JSON"

        report = dispatcher.parse_response(response)

        # Should return safe defaults
        assert report.security_gate == "fail"  # Fail-safe default
        assert report.compliance_status == "unknown"


class TestValidationOrchestrator:
    """Tests for ValidationOrchestrator."""

    def test_init(self):
        """Test ValidationOrchestrator initialization."""
        orchestrator = ValidationOrchestrator()
        assert isinstance(orchestrator.qa_dispatcher, QAAgentDispatcher)
        assert isinstance(orchestrator.security_dispatcher, SecurityAgentDispatcher)

    def test_validate_returns_validation_report(self):
        """Test that validate returns a ValidationReport."""
        orchestrator = ValidationOrchestrator()

        report = orchestrator.validate(
            task_id="task-789",
            task_title="Test Task",
            task_description="Test implementation",
            acceptance_criteria=["AC1", "AC2"],
            implementation_artifacts={"code_files": {"test.py": "pass"}},
        )

        assert report is not None
        assert isinstance(report.qa_report, QAReport)
        assert isinstance(report.security_report, SecurityReport)
        assert isinstance(report.validation_status, ValidationStatus)
        assert report.summary != ""

    def test_validate_includes_both_reports(self):
        """Test that validation includes both QA and Security reports."""
        orchestrator = ValidationOrchestrator()

        report = orchestrator.validate(
            task_id="task-100",
            task_title="Feature",
            task_description="Description",
            acceptance_criteria=["AC1"],
            implementation_artifacts={},
        )

        # Verify QA report structure
        assert hasattr(report.qa_report, "functional_test_status")
        assert hasattr(report.qa_report, "integration_test_status")
        assert hasattr(report.qa_report, "edge_case_coverage")
        assert hasattr(report.qa_report, "risk_assessment")

        # Verify Security report structure
        assert hasattr(report.security_report, "vulnerabilities")
        assert hasattr(report.security_report, "compliance_status")
        assert hasattr(report.security_report, "security_gate")
        assert hasattr(report.security_report, "critical_count")


class TestDetermineValidationOutcome:
    """Tests for determine_validation_outcome function."""

    def test_pass_when_no_issues(self):
        """Test that validation passes when no issues are found."""
        qa_report = QAReport(
            functional_test_status="pass",
            integration_test_status="pass",
            edge_case_coverage="excellent",
            risk_assessment="low",
            issues=[],
        )
        security_report = SecurityReport(
            vulnerabilities=[],
            compliance_status="compliant",
            security_gate="pass",
            critical_count=0,
            high_count=0,
        )

        status = determine_validation_outcome(qa_report, security_report)
        assert status == ValidationStatus.PASS

    def test_fail_when_critical_security_vulnerabilities(self):
        """Test that validation fails when critical security vulnerabilities found."""
        qa_report = QAReport(
            functional_test_status="pass",
            integration_test_status="pass",
            edge_case_coverage="good",
            risk_assessment="low",
        )
        security_report = SecurityReport(
            vulnerabilities=[{"severity": "critical"}],
            security_gate="fail",
            critical_count=1,
        )

        status = determine_validation_outcome(qa_report, security_report)
        assert status == ValidationStatus.FAIL

    def test_fail_when_security_gate_fails(self):
        """Test that validation fails when security gate is fail."""
        qa_report = QAReport(
            functional_test_status="pass",
            integration_test_status="pass",
            edge_case_coverage="good",
            risk_assessment="low",
        )
        security_report = SecurityReport(
            vulnerabilities=[],
            security_gate="fail",
            critical_count=0,
        )

        status = determine_validation_outcome(qa_report, security_report)
        assert status == ValidationStatus.FAIL

    def test_fail_when_critical_qa_issues(self):
        """Test that validation fails when critical QA issues found."""
        qa_report = QAReport(
            functional_test_status="fail",
            integration_test_status="pass",
            edge_case_coverage="poor",
            risk_assessment="critical",
            issues=[
                {
                    "severity": "critical",
                    "category": "functional",
                    "description": "Core feature broken",
                }
            ],
        )
        security_report = SecurityReport(
            vulnerabilities=[],
            security_gate="pass",
            critical_count=0,
        )

        status = determine_validation_outcome(qa_report, security_report)
        assert status == ValidationStatus.FAIL

    def test_warning_when_high_severity_security_issues(self):
        """Test that validation returns warning for high severity security issues."""
        qa_report = QAReport(
            functional_test_status="pass",
            integration_test_status="pass",
            edge_case_coverage="good",
            risk_assessment="low",
        )
        security_report = SecurityReport(
            vulnerabilities=[{"severity": "high"}],
            security_gate="pass",
            critical_count=0,
            high_count=1,
        )

        status = determine_validation_outcome(qa_report, security_report)
        assert status == ValidationStatus.WARNING

    def test_warning_when_high_severity_qa_issues(self):
        """Test that validation returns warning for high severity QA issues."""
        qa_report = QAReport(
            functional_test_status="pass",
            integration_test_status="pass",
            edge_case_coverage="good",
            risk_assessment="medium",
            issues=[
                {
                    "severity": "high",
                    "category": "performance",
                    "description": "Slow response time",
                }
            ],
        )
        security_report = SecurityReport(
            vulnerabilities=[],
            security_gate="pass",
            critical_count=0,
            high_count=0,
        )

        status = determine_validation_outcome(qa_report, security_report)
        assert status == ValidationStatus.WARNING

    def test_pass_with_low_severity_issues(self):
        """Test that validation passes with only low severity issues."""
        qa_report = QAReport(
            functional_test_status="pass",
            integration_test_status="pass",
            edge_case_coverage="good",
            risk_assessment="low",
            issues=[
                {
                    "severity": "low",
                    "category": "usability",
                    "description": "Minor UI issue",
                }
            ],
        )
        security_report = SecurityReport(
            vulnerabilities=[{"severity": "low"}],
            security_gate="pass",
            critical_count=0,
            high_count=0,
            low_count=1,
        )

        status = determine_validation_outcome(qa_report, security_report)
        assert status == ValidationStatus.PASS


class TestIntegration:
    """Integration tests for validation agents."""

    def test_full_validation_workflow_passing(self):
        """Test complete validation workflow with passing results."""
        orchestrator = ValidationOrchestrator()

        # Simulate a complete implementation
        implementation_artifacts = {
            "code_files": {
                "src/feature.py": "def new_feature():\n    return 'working'",
                "src/utils.py": "def helper():\n    return True",
            },
            "test_files": {
                "tests/test_feature.py": "def test_new_feature():\n    assert new_feature() == 'working'"
            },
            "test_results": "10 passed, 0 failed",
            "dependencies": "requests==2.31.0",
        }

        report = orchestrator.validate(
            task_id="task-999",
            task_title="New Feature",
            task_description="Implement new feature with security",
            acceptance_criteria=[
                "Feature works correctly",
                "All tests pass",
                "No security vulnerabilities",
            ],
            implementation_artifacts=implementation_artifacts,
        )

        # In the mock implementation, this should pass
        assert report.validation_status in [
            ValidationStatus.PASS,
            ValidationStatus.WARNING,
        ]
        assert report.qa_report is not None
        assert report.security_report is not None

    def test_prompt_building_for_parallel_execution(self):
        """Test that both QA and Security prompts can be built for parallel execution."""
        orchestrator = ValidationOrchestrator()

        task_id = "task-123"
        task_title = "Auth Feature"
        task_description = "Implement JWT authentication"
        acceptance_criteria = ["Secure token generation", "Token validation works"]
        artifacts = {"code_files": {"auth.py": "def auth(): pass"}}

        # Build both prompts
        qa_prompt = orchestrator.qa_dispatcher.build_prompt(
            task_id, task_title, task_description, acceptance_criteria, artifacts
        )
        security_prompt = orchestrator.security_dispatcher.build_prompt(
            task_id, task_title, task_description, acceptance_criteria, artifacts
        )

        # Verify both prompts are complete and distinct
        assert len(qa_prompt) > 0
        assert len(security_prompt) > 0
        assert qa_prompt != security_prompt
        assert "Quality Guardian" in qa_prompt
        assert "Secure-by-Design Engineer" in security_prompt
