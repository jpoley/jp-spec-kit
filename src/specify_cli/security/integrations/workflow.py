"""Workflow integration for security scanning.

This module integrates security scanning with the jpspec workflow system,
providing security gates, event emission, and backlog task creation.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from specify_cli.security.models import Finding, Severity


@dataclass
class SecurityGateResult:
    """Result from security gate evaluation.

    Attributes:
        passed: Whether security gate passed (no blocking findings).
        findings_count: Total number of findings.
        critical_count: Number of critical severity findings.
        high_count: Number of high severity findings.
        blocking_findings: List of findings that caused gate to fail.
        message: Human-readable result message.
    """

    passed: bool
    findings_count: int
    critical_count: int
    high_count: int
    blocking_findings: list[Finding]
    message: str


class SecurityWorkflowIntegration:
    """Integrates security scanning with jpspec workflow system.

    This class provides:
    - Security gate evaluation (pass/fail based on severity threshold)
    - Automatic backlog task creation from findings
    - Event emission for workflow integration
    - CI/CD integration helpers

    Example:
        >>> integration = SecurityWorkflowIntegration()
        >>> result = integration.run_security_gate(
        ...     findings=findings,
        ...     fail_on=["critical", "high"]
        ... )
        >>> if not result.passed:
        ...     print(f"Security gate failed: {result.message}")
        >>> integration.emit_security_event(
        ...     event_type="scan.completed",
        ...     feature_id="auth-system"
        ... )
    """

    def __init__(
        self,
        backlog_cli: str = "backlog",
        hooks_cli: str = "specify",
        project_root: Path | None = None,
    ):
        """Initialize workflow integration.

        Args:
            backlog_cli: Command to invoke backlog CLI (default: "backlog").
            hooks_cli: Command to invoke hooks/events CLI (default: "specify").
            project_root: Project root directory (default: current directory).
        """
        self.backlog_cli = backlog_cli
        self.hooks_cli = hooks_cli
        self.project_root = project_root or Path.cwd()

    def run_security_gate(
        self,
        findings: list[Finding],
        fail_on: list[str] | None = None,
    ) -> SecurityGateResult:
        """Evaluate security gate criteria.

        Args:
            findings: List of security findings from scan.
            fail_on: Severity levels that cause gate to fail
                (e.g., ["critical"], ["critical", "high"]).
                Default: ["critical"].

        Returns:
            SecurityGateResult with pass/fail status and details.

        Example:
            >>> result = integration.run_security_gate(
            ...     findings=findings,
            ...     fail_on=["critical", "high"]
            ... )
            >>> if not result.passed:
            ...     print(f"Gate failed: {result.blocking_findings}")
        """
        fail_on = fail_on or ["critical"]
        fail_severities = {s.lower() for s in fail_on}

        # Count findings by severity
        critical_count = sum(1 for f in findings if f.severity == Severity.CRITICAL)
        high_count = sum(1 for f in findings if f.severity == Severity.HIGH)

        # Find blocking findings
        blocking_findings = [
            f for f in findings if f.severity.value.lower() in fail_severities
        ]

        # Determine pass/fail
        passed = len(blocking_findings) == 0

        if passed:
            message = (
                f"Security gate passed: {len(findings)} findings, "
                f"none at {'/'.join(fail_on)} severity"
            )
        else:
            message = (
                f"Security gate failed: {len(blocking_findings)} blocking findings "
                f"at {'/'.join(fail_on)} severity"
            )

        return SecurityGateResult(
            passed=passed,
            findings_count=len(findings),
            critical_count=critical_count,
            high_count=high_count,
            blocking_findings=blocking_findings,
            message=message,
        )

    def create_remediation_tasks(
        self,
        findings: list[Finding],
        feature_id: str | None = None,
        auto_assign: str | None = None,
        priority_map: dict[str, str] | None = None,
    ) -> list[str]:
        """Create backlog tasks for security findings.

        Creates one task per finding with appropriate metadata:
        - Title: "Fix [severity] [CWE]: [title]"
        - Description: Full finding details with AI explanation
        - Labels: security, severity, CWE, scanner
        - Priority: Based on severity
        - Acceptance Criteria: Fix, verify, test

        Args:
            findings: List of security findings.
            feature_id: Optional feature/spec ID to associate.
            auto_assign: Optional assignee for all tasks (e.g., "@security-team").
            priority_map: Custom severity->priority mapping
                (default: critical/high->high, medium->medium, low->low).

        Returns:
            List of created task IDs.

        Example:
            >>> task_ids = integration.create_remediation_tasks(
            ...     findings=findings,
            ...     feature_id="auth-system",
            ...     auto_assign="@security-team"
            ... )
            >>> print(f"Created {len(task_ids)} remediation tasks")
        """
        if priority_map is None:
            priority_map = {
                "critical": "high",
                "high": "high",
                "medium": "medium",
                "low": "low",
                "info": "low",
            }

        task_ids = []

        for finding in findings:
            # Build task title
            cwe_part = f" {finding.cwe_id}" if finding.cwe_id else ""
            title = f"Fix {finding.severity.value.upper()}{cwe_part}: {finding.title}"

            # Build description with all details
            description = self._build_task_description(finding)

            # Build labels
            labels = ["security", finding.severity.value]
            if finding.cwe_id:
                labels.append(finding.cwe_id.lower().replace("-", ""))
            labels.append(finding.scanner)
            if feature_id:
                labels.append(feature_id)

            # Build acceptance criteria
            ac_list = [
                f"Fix vulnerability at {finding.location.file}:{finding.location.line_start}",
                "Re-run security scan to verify fix",
                "Add test to prevent regression",
            ]
            if finding.severity in [Severity.CRITICAL, Severity.HIGH]:
                ac_list.append("Security code review completed")

            # Build backlog CLI command
            cmd = [
                self.backlog_cli,
                "task",
                "create",
                title,
                "-d",
                description,
                "-p",
                priority_map.get(finding.severity.value, "medium"),
            ]

            # Add labels
            for label in labels:
                cmd.extend(["-l", label])

            # Add acceptance criteria
            for ac in ac_list:
                cmd.extend(["--ac", ac])

            # Add assignee if specified
            if auto_assign:
                cmd.extend(["-a", auto_assign])

            # Execute command
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    cwd=self.project_root,
                )

                # Parse task ID from output (format: "Created task task-123")
                output = result.stdout.strip()
                if "task-" in output:
                    # Extract task ID using simple string parsing
                    parts = output.split()
                    for part in parts:
                        if part.startswith("task-"):
                            task_ids.append(part.rstrip(".,:;"))
                            break

            except subprocess.CalledProcessError as e:
                # Log error but continue with other findings
                print(
                    f"Warning: Failed to create task for finding {finding.id}: {e.stderr}"
                )

        return task_ids

    def emit_security_event(
        self,
        event_type: str,
        feature_id: str | None = None,
        task_id: str | None = None,
    ) -> None:
        """Emit workflow event for security operation.

        Integrates with the specify hooks system to emit events that
        can trigger additional workflow actions (notifications, gates, etc.).

        Note:
            The hooks emit command does not currently support passing arbitrary
            event data via CLI. Hooks can access finding data from security
            report files (e.g., .security/reports/*.json).

        Args:
            event_type: Event type (e.g., "scan.completed", "triage.completed").
                Will be prefixed with "security." automatically.
            feature_id: Optional feature/spec ID.
            task_id: Optional task ID.

        Example:
            >>> integration.emit_security_event(
            ...     event_type="scan.completed",
            ...     feature_id="auth-system"
            ... )
        """
        # Build command
        cmd = [
            self.hooks_cli,
            "hooks",
            "emit",
            f"security.{event_type}",
        ]

        # Add feature ID if provided
        if feature_id:
            cmd.extend(["--spec-id", feature_id])

        # Add task ID if provided
        if task_id:
            cmd.extend(["--task-id", task_id])

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,  # Don't fail if hooks not configured
                cwd=self.project_root,
            )
        except Exception as e:
            # Log but don't fail - hooks are optional
            print(f"Warning: Failed to emit security event: {e}")

    def _build_task_description(self, finding: Finding) -> str:
        """Build comprehensive task description from finding.

        Args:
            finding: Security finding.

        Returns:
            Markdown-formatted task description.
        """
        desc = f"""## Security Finding: {finding.title}

**Severity:** {finding.severity.value.upper()}
**CWE:** {finding.cwe_id or "N/A"}
**Scanner:** {finding.scanner}
**Confidence:** {finding.confidence.value}

### Location

`{finding.location.file}:{finding.location.line_start}-{finding.location.line_end}`

### Code

```
{finding.location.code_snippet}
```

### Description

{finding.description}
"""

        if finding.remediation:
            desc += f"""
### Remediation Guidance

{finding.remediation}
"""

        if finding.references:
            desc += """
### References

"""
            for ref in finding.references:
                desc += f"- {ref}\n"

        return desc


def create_security_gate(
    findings: list[Finding],
    fail_on: list[str] | None = None,
) -> SecurityGateResult:
    """Convenience function to evaluate security gate.

    Args:
        findings: List of security findings.
        fail_on: Severity levels that cause gate to fail.

    Returns:
        SecurityGateResult.

    Example:
        >>> result = create_security_gate(findings, fail_on=["critical"])
        >>> if not result.passed:
        ...     raise SystemExit(f"Security gate failed: {result.message}")
    """
    integration = SecurityWorkflowIntegration()
    return integration.run_security_gate(findings, fail_on)
