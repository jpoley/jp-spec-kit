"""
Validation agents module for integrating QA and Security agents.

This module provides orchestration for Quality Guardian and Secure-by-Design
agents to perform comprehensive validation of task implementations.
"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, TypedDict


class Severity(str, Enum):
    """Issue severity levels for validation reports."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ValidationStatus(str, Enum):
    """Validation outcome status."""

    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


class QAIssue(TypedDict, total=False):
    """Structure for QA report issues.

    Fields:
        severity: Issue severity level (critical|high|medium|low)
        category: Issue category (functional|performance|security|usability)
        description: Description of the issue
        recommendation: How to fix the issue
    """

    severity: str
    category: str
    description: str
    recommendation: str


class SecurityVulnerability(TypedDict, total=False):
    """Structure for security vulnerabilities.

    Fields:
        severity: Vulnerability severity (critical|high|medium|low)
        category: Vulnerability category (injection|xss|auth|crypto|config|dependency)
        description: Description of the vulnerability
        location: File path and line number or component name
        cve: CVE identifier if applicable (e.g., CVE-2024-12345)
        remediation: How to fix the vulnerability
        exploitability: How easy to exploit (easy|moderate|difficult)
    """

    severity: str
    category: str
    description: str
    location: str
    cve: str
    remediation: str
    exploitability: str


def extract_json_from_response(
    response: str, fallback: dict[str, Any]
) -> dict[str, Any]:
    """
    Extract JSON from agent response, supporting both markdown-wrapped and plain JSON.

    Args:
        response: Raw agent response text
        fallback: Default dictionary to return if JSON parsing fails

    Returns:
        Parsed JSON dictionary or fallback if parsing fails
    """
    # Try to extract JSON from markdown code block
    json_match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to parse entire response as JSON
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return fallback


@dataclass
class QAReport:
    """Quality assurance validation report."""

    functional_test_status: str
    integration_test_status: str
    edge_case_coverage: str
    risk_assessment: str
    issues: list[dict[str, Any]] = field(default_factory=list)
    test_results: dict[str, Any] = field(default_factory=dict)
    quality_metrics: dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityReport:
    """Security validation report."""

    vulnerabilities: list[dict[str, Any]] = field(default_factory=list)
    compliance_status: str = ""
    security_gate: str = ""  # "pass" or "fail"
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0


@dataclass
class ValidationReport:
    """Combined validation report from QA and Security agents."""

    qa_report: QAReport
    security_report: SecurityReport
    validation_status: ValidationStatus
    summary: str = ""
    timestamp: str = ""


class QAAgentDispatcher:
    """Dispatcher for Quality Guardian agent."""

    def __init__(self, agent_definition_path: Optional[Path] = None):
        """
        Initialize QA agent dispatcher.

        Args:
            agent_definition_path: Path to quality-guardian.md agent definition.
                                  Defaults to .agents/quality-guardian.md
        """
        if agent_definition_path is None:
            # Try to find .agents/quality-guardian.md relative to project root
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent
            agent_definition_path = project_root / ".agents" / "quality-guardian.md"

        self.agent_definition_path = agent_definition_path

    def build_prompt(
        self,
        task_id: str,
        task_title: str,
        task_description: str,
        acceptance_criteria: list[str],
        implementation_artifacts: dict[str, Any],
    ) -> str:
        """
        Build QA agent prompt with task context and acceptance criteria.

        Args:
            task_id: Task identifier
            task_title: Task title
            task_description: Task description
            acceptance_criteria: List of acceptance criteria to validate
            implementation_artifacts: Dict containing code, tests, configs, etc.

        Returns:
            Formatted prompt for Quality Guardian agent
        """
        # Format acceptance criteria
        ac_text = "\n".join(
            f"{i + 1}. {ac}" for i, ac in enumerate(acceptance_criteria)
        )

        # Format implementation artifacts
        artifacts_text = ""
        if "code_files" in implementation_artifacts:
            artifacts_text += "\n### Code Files:\n"
            for file_path, content in implementation_artifacts["code_files"].items():
                artifacts_text += f"\n**{file_path}**:\n```\n{content}\n```\n"

        if "test_files" in implementation_artifacts:
            artifacts_text += "\n### Test Files:\n"
            for file_path, content in implementation_artifacts["test_files"].items():
                artifacts_text += f"\n**{file_path}**:\n```\n{content}\n```\n"

        if "test_results" in implementation_artifacts:
            artifacts_text += f"\n### Test Results:\n```\n{implementation_artifacts['test_results']}\n```\n"

        prompt = f"""# AGENT CONTEXT: Quality Guardian

You are the Quality Guardian, a vigilant protector of system integrity, user trust, and organizational reputation. You are the constructive skeptic who sees failure modes others miss, anticipates edge cases others ignore, and champions excellence as the minimum acceptable standard.

## Core Philosophy
- **Constructive Skepticism**: Question everything with intent to improve
- **Risk Intelligence**: See potential failures as opportunities for resilience
- **User-Centric**: Champion end user experience above all else
- **Long-Term Thinking**: Consider maintenance, evolution, technical debt from day one
- **Security-First**: Every feature is a potential vulnerability until proven otherwise

## Analysis Framework
1. **Failure Imagination Exercise**: List failure modes, assess impact/likelihood, plan detection/recovery
2. **Edge Case Exploration**: Test at zero, infinity, malformed input, extreme load, hostile users
3. **Three-Layer Critique**: Acknowledge value → Identify risk → Suggest mitigation
4. **Risk Classification**: Critical, High, Medium, Low

## Risk Dimensions
- Technical: Scalability, performance, reliability, concurrency
- Security: Vulnerabilities, attack surfaces, data exposure
- Business: Cost overruns, market timing, operational complexity
- User: Usability issues, adoption barriers, accessibility
- Operational: Maintenance burden, monitoring, debugging

# TASK: Conduct comprehensive quality validation

## Task Details
- **ID**: {task_id}
- **Title**: {task_title}
- **Description**: {task_description}

## Acceptance Criteria to Validate
{ac_text}

## Implementation Artifacts
{artifacts_text}

## Validation Requirements

1. **Functional Testing**
   - Verify all acceptance criteria met
   - Test user workflows end-to-end
   - Validate edge cases and boundary conditions
   - Test error handling and recovery

2. **Integration Testing**
   - Frontend-backend integration (if applicable)
   - Third-party service integration
   - Database integration
   - Message queue/event processing

3. **Performance Considerations**
   - Expected load handling
   - Resource utilization
   - Latency concerns
   - Scalability validation

4. **Risk Analysis**
   - Identify failure modes
   - Assess impact and likelihood
   - Validate monitoring and alerting needs
   - Verify rollback procedures

5. **Edge Case Analysis**
   - Zero/null/empty inputs
   - Maximum values
   - Malformed data
   - Concurrent access
   - Error conditions

## Required Output Format

Deliver a comprehensive test report in JSON format:

```json
{{
  "functional_test_status": "pass|fail|warning",
  "integration_test_status": "pass|fail|warning",
  "edge_case_coverage": "excellent|good|fair|poor",
  "risk_assessment": "low|medium|high|critical",
  "issues": [
    {{
      "severity": "critical|high|medium|low",
      "category": "functional|performance|security|usability",
      "description": "Issue description",
      "recommendation": "How to fix"
    }}
  ],
  "test_results": {{
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0
  }},
  "quality_metrics": {{
    "code_coverage": "percentage",
    "complexity": "low|medium|high",
    "maintainability": "excellent|good|fair|poor"
  }},
  "summary": "Overall assessment and recommendations"
}}
```

Focus on validating that all acceptance criteria are met and identifying any critical issues that would prevent production deployment.
"""
        return prompt

    def parse_response(self, agent_response: str) -> QAReport:
        """
        Parse Quality Guardian agent response into structured QAReport.

        Args:
            agent_response: Raw response from agent

        Returns:
            Structured QAReport
        """
        # Fallback values if parsing fails
        fallback = {
            "functional_test_status": "unknown",
            "integration_test_status": "unknown",
            "edge_case_coverage": "unknown",
            "risk_assessment": "unknown",
            "issues": [],
            "test_results": {},
            "quality_metrics": {},
        }

        report_data = extract_json_from_response(agent_response, fallback)

        return QAReport(
            functional_test_status=report_data.get("functional_test_status", "unknown"),
            integration_test_status=report_data.get(
                "integration_test_status", "unknown"
            ),
            edge_case_coverage=report_data.get("edge_case_coverage", "unknown"),
            risk_assessment=report_data.get("risk_assessment", "unknown"),
            issues=report_data.get("issues", []),
            test_results=report_data.get("test_results", {}),
            quality_metrics=report_data.get("quality_metrics", {}),
        )


class SecurityAgentDispatcher:
    """Dispatcher for Secure-by-Design agent."""

    def __init__(self, agent_definition_path: Optional[Path] = None):
        """
        Initialize Security agent dispatcher.

        Args:
            agent_definition_path: Path to secure-by-design-engineer.md agent definition.
                                  Defaults to .agents/secure-by-design-engineer.md
        """
        if agent_definition_path is None:
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent
            agent_definition_path = (
                project_root / ".agents" / "secure-by-design-engineer.md"
            )

        self.agent_definition_path = agent_definition_path

    def build_prompt(
        self,
        task_id: str,
        task_title: str,
        task_description: str,
        acceptance_criteria: list[str],
        implementation_artifacts: dict[str, Any],
    ) -> str:
        """
        Build Security agent prompt with task context and acceptance criteria.

        Args:
            task_id: Task identifier
            task_title: Task title
            task_description: Task description
            acceptance_criteria: List of acceptance criteria to validate
            implementation_artifacts: Dict containing code, tests, configs, etc.

        Returns:
            Formatted prompt for Secure-by-Design agent
        """
        # Format acceptance criteria
        ac_text = "\n".join(
            f"{i + 1}. {ac}" for i, ac in enumerate(acceptance_criteria)
        )

        # Format implementation artifacts
        artifacts_text = ""
        if "code_files" in implementation_artifacts:
            artifacts_text += "\n### Code Files:\n"
            for file_path, content in implementation_artifacts["code_files"].items():
                artifacts_text += f"\n**{file_path}**:\n```\n{content}\n```\n"

        if "dependencies" in implementation_artifacts:
            artifacts_text += f"\n### Dependencies:\n```\n{implementation_artifacts['dependencies']}\n```\n"

        if "configs" in implementation_artifacts:
            artifacts_text += "\n### Configuration Files:\n"
            for file_path, content in implementation_artifacts["configs"].items():
                artifacts_text += f"\n**{file_path}**:\n```\n{content}\n```\n"

        prompt = f"""# AGENT CONTEXT: Secure-by-Design Engineer

You are a Secure-by-Design Engineer, an experienced security specialist focused on building security into the development lifecycle from the ground up. Security is not a feature to be added later, but a fundamental quality built into every aspect of the system from the beginning.

## Core Principles
- **Assume Breach**: Design as if systems will be compromised
- **Defense in Depth**: Multiple security layers
- **Principle of Least Privilege**: Minimum necessary access
- **Fail Securely**: Failures don't compromise security
- **Security by Default**: Secure out of the box

## Security Analysis Process
1. **Risk Assessment**: Identify assets, threats, business impact
2. **Threat Modeling**: Assets, threats, attack vectors
3. **Architecture Analysis**: Security weaknesses in design
4. **Code Review**: Vulnerability patterns (SQL injection, XSS, etc.)
5. **Access Control Review**: Authentication, authorization, privilege management
6. **Data Flow Analysis**: Sensitive information handling
7. **Dependency Security**: Third-party vulnerabilities
8. **Incident Response**: Monitoring and detection capabilities

## Severity Classification
- **Critical**: Authentication bypass, SQL injection, RCE
- **High**: XSS, privilege escalation, data exposure
- **Medium**: Information disclosure, DoS, weak crypto
- **Low**: Config issues, missing headers

# TASK: Conduct comprehensive security assessment

## Task Details
- **ID**: {task_id}
- **Title**: {task_title}
- **Description**: {task_description}

## Acceptance Criteria to Validate
{ac_text}

## Implementation Artifacts
{artifacts_text}

## Security Validation Requirements

1. **Code Security Review**
   - Authentication and authorization implementation
   - Input validation and sanitization
   - SQL/NoSQL injection prevention
   - XSS/CSRF prevention
   - Secure error handling (no sensitive data exposure)

2. **Dependency Security**
   - Scan for known vulnerabilities (CVEs)
   - Check dependency licenses
   - Validate supply chain security

3. **Infrastructure Security** (if applicable)
   - Secrets management validation
   - Network security configuration
   - Access controls and IAM
   - Encryption at rest and in transit

4. **Compliance** (if applicable)
   - GDPR compliance (if handling EU data)
   - SOC2 requirements
   - Data privacy requirements

5. **Threat Modeling**
   - Identify attack vectors
   - Assess exploitability
   - Validate security controls

## Required Output Format

Deliver a comprehensive security report in JSON format:

```json
{{
  "vulnerabilities": [
    {{
      "severity": "critical|high|medium|low",
      "category": "injection|xss|auth|crypto|config|dependency",
      "description": "Vulnerability description",
      "location": "File/line or component",
      "cve": "CVE-XXXX-XXXXX (if applicable)",
      "remediation": "How to fix",
      "exploitability": "easy|moderate|difficult"
    }}
  ],
  "compliance_status": "compliant|non-compliant|partial",
  "security_gate": "pass|fail",
  "critical_count": 0,
  "high_count": 0,
  "medium_count": 0,
  "low_count": 0,
  "summary": "Overall security assessment"
}}
```

**SECURITY GATE CRITERIA**: Automatically FAIL if any critical vulnerabilities are found. PASS only if no critical or high severity issues exist.
"""
        return prompt

    def parse_response(self, agent_response: str) -> SecurityReport:
        """
        Parse Secure-by-Design agent response into structured SecurityReport.

        Args:
            agent_response: Raw response from agent

        Returns:
            Structured SecurityReport
        """
        # Fallback values with fail-safe defaults (security_gate="fail")
        fallback = {
            "vulnerabilities": [],
            "compliance_status": "unknown",
            "security_gate": "fail",
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0,
        }

        report_data = extract_json_from_response(agent_response, fallback)

        return SecurityReport(
            vulnerabilities=report_data.get("vulnerabilities", []),
            compliance_status=report_data.get("compliance_status", "unknown"),
            security_gate=report_data.get("security_gate", "fail"),
            critical_count=report_data.get("critical_count", 0),
            high_count=report_data.get("high_count", 0),
            medium_count=report_data.get("medium_count", 0),
            low_count=report_data.get("low_count", 0),
        )


class ValidationOrchestrator:
    """Orchestrates parallel execution of QA and Security agents."""

    def __init__(self):
        """Initialize validation orchestrator."""
        self.qa_dispatcher = QAAgentDispatcher()
        self.security_dispatcher = SecurityAgentDispatcher()

    def validate(
        self,
        task_id: str,
        task_title: str,
        task_description: str,
        acceptance_criteria: list[str],
        implementation_artifacts: dict[str, Any],
    ) -> ValidationReport:
        """
        Execute validation using QA and Security agents in parallel.

        Args:
            task_id: Task identifier
            task_title: Task title
            task_description: Task description
            acceptance_criteria: List of acceptance criteria
            implementation_artifacts: Implementation code, tests, configs, etc.

        Returns:
            Combined ValidationReport with results from both agents
        """
        # Build prompts for both agents
        # Note: Prompts are built but not currently used in this mock implementation.
        # In actual workflow integration, these would be passed to parallel Task tool
        # invocations for real agent execution.
        _ = self.qa_dispatcher.build_prompt(
            task_id=task_id,
            task_title=task_title,
            task_description=task_description,
            acceptance_criteria=acceptance_criteria,
            implementation_artifacts=implementation_artifacts,
        )

        _ = self.security_dispatcher.build_prompt(
            task_id=task_id,
            task_title=task_title,
            task_description=task_description,
            acceptance_criteria=acceptance_criteria,
            implementation_artifacts=implementation_artifacts,
        )

        # TODO: In actual implementation, dispatch both agents in parallel using Task tool
        # For now, return structure showing what would happen
        # This will be integrated with the actual Task tool invocation in the workflow

        # Placeholder for parallel execution
        # qa_response = await dispatch_task_agent(qa_prompt)
        # security_response = await dispatch_task_agent(security_prompt)

        # For testing purposes, create mock report instances directly
        qa_report = QAReport(
            functional_test_status="pass",
            integration_test_status="pass",
            edge_case_coverage="good",
            risk_assessment="low",
            issues=[],
            test_results={},
            quality_metrics={},
        )

        security_report = SecurityReport(
            vulnerabilities=[],
            compliance_status="compliant",
            security_gate="pass",
            critical_count=0,
            high_count=0,
            medium_count=0,
            low_count=0,
        )

        # Determine validation outcome
        validation_status = determine_validation_outcome(qa_report, security_report)

        # Generate summary
        summary = f"QA Status: {qa_report.functional_test_status}, Security Gate: {security_report.security_gate}"

        return ValidationReport(
            qa_report=qa_report,
            security_report=security_report,
            validation_status=validation_status,
            summary=summary,
        )


def determine_validation_outcome(
    qa_report: QAReport, security_report: SecurityReport
) -> ValidationStatus:
    """
    Determine overall validation outcome based on QA and Security reports.

    Validation FAILS if:
    - Critical security vulnerabilities found
    - Critical functional issues identified
    - Security gate is "fail"

    Args:
        qa_report: Quality assurance report
        security_report: Security validation report

    Returns:
        ValidationStatus (PASS, FAIL, or WARNING)
    """
    # Check for critical security issues
    if security_report.critical_count > 0:
        return ValidationStatus.FAIL

    if security_report.security_gate == "fail":
        return ValidationStatus.FAIL

    # Check for critical QA issues using Severity enum
    critical_qa_issues = [
        issue
        for issue in qa_report.issues
        if issue.get("severity") == Severity.CRITICAL.value
    ]
    if critical_qa_issues:
        return ValidationStatus.FAIL

    # Check for high severity issues (warning) using Severity enum
    if security_report.high_count > 0 or any(
        issue.get("severity") == Severity.HIGH.value for issue in qa_report.issues
    ):
        return ValidationStatus.WARNING

    # All checks passed
    return ValidationStatus.PASS
