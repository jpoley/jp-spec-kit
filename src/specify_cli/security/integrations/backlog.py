"""Backlog integration for security findings.

This module provides task creation from security findings,
enabling automatic backlog population for remediation tracking.
"""

from dataclasses import dataclass, field
from typing import Any

from specify_cli.security.models import Finding, Severity


@dataclass
class FindingTask:
    """Task representation for a security finding.

    Maps security findings to backlog.md task format with
    all relevant metadata for remediation tracking.
    """

    title: str
    description: str
    severity: str
    cwe_id: str | None
    location: str
    finding_id: str
    priority: str
    labels: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)

    def to_backlog_format(self) -> dict[str, Any]:
        """Convert to backlog.md task format.

        Returns:
            Dictionary in backlog.md task format.
        """
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "labels": self.labels,
            "acceptanceCriteria": self.acceptance_criteria,
        }

    def to_markdown(self) -> str:
        """Generate markdown task content.

        Returns:
            Markdown formatted task description.
        """
        md = f"""## {self.title}

**Severity:** {self.severity}
**CWE:** {self.cwe_id or "N/A"}
**Location:** `{self.location}`
**Finding ID:** `{self.finding_id}`

### Description

{self.description}

### Acceptance Criteria

"""
        for i, criterion in enumerate(self.acceptance_criteria, 1):
            md += f"- [ ] {criterion}\n"

        return md


class BacklogIntegration:
    """Integration between security findings and backlog.md.

    Converts security findings into backlog tasks with appropriate
    severity mapping, labels, and acceptance criteria.

    Example:
        >>> integration = BacklogIntegration()
        >>> tasks = integration.create_tasks(findings)
        >>> for task in tasks:
        ...     print(task.to_backlog_format())
    """

    SEVERITY_PRIORITY_MAP = {
        Severity.CRITICAL: "high",
        Severity.HIGH: "high",
        Severity.MEDIUM: "medium",
        Severity.LOW: "low",
        Severity.INFO: "low",
    }

    def __init__(
        self,
        include_ai_explanation: bool = True,
        group_by_cwe: bool = False,
        max_tasks: int = 50,
    ):
        """Initialize backlog integration.

        Args:
            include_ai_explanation: Include AI triage explanation in tasks.
            group_by_cwe: Group findings by CWE into single tasks.
            max_tasks: Maximum number of tasks to create.
        """
        self.include_ai_explanation = include_ai_explanation
        self.group_by_cwe = group_by_cwe
        self.max_tasks = max_tasks

    def create_tasks(
        self,
        findings: list[Finding],
        triage_results: list | None = None,
    ) -> list[FindingTask]:
        """Create backlog tasks from security findings.

        Args:
            findings: List of security findings.
            triage_results: Optional AI triage results for explanations.

        Returns:
            List of FindingTask objects.
        """
        if self.group_by_cwe:
            return self._create_grouped_tasks(findings, triage_results)
        return self._create_individual_tasks(findings, triage_results)

    def _create_individual_tasks(
        self,
        findings: list[Finding],
        triage_results: list | None = None,
    ) -> list[FindingTask]:
        """Create one task per finding."""
        triage_map = {}
        if triage_results:
            for result in triage_results:
                triage_map[result.finding_id] = result

        tasks = []
        for finding in findings[: self.max_tasks]:
            # Skip false positives if triage available
            triage = triage_map.get(finding.id)
            if triage and hasattr(triage, "classification"):
                if triage.classification.value == "FP":
                    continue

            task = self._finding_to_task(finding, triage)
            tasks.append(task)

        return tasks

    def _create_grouped_tasks(
        self,
        findings: list[Finding],
        triage_results: list | None = None,
    ) -> list[FindingTask]:
        """Create grouped tasks by CWE."""
        from collections import defaultdict

        triage_map = {}
        if triage_results:
            for result in triage_results:
                triage_map[result.finding_id] = result

        # Group by CWE
        by_cwe: dict[str, list[Finding]] = defaultdict(list)
        for finding in findings:
            cwe = finding.cwe_id or "UNKNOWN"
            # Skip false positives
            triage = triage_map.get(finding.id)
            if triage and hasattr(triage, "classification"):
                if triage.classification.value == "FP":
                    continue
            by_cwe[cwe].append(finding)

        tasks = []
        for cwe, cwe_findings in list(by_cwe.items())[: self.max_tasks]:
            task = self._create_grouped_task(cwe, cwe_findings, triage_map)
            tasks.append(task)

        return tasks

    def _finding_to_task(
        self, finding: Finding, triage: Any | None = None
    ) -> FindingTask:
        """Convert a single finding to a task."""
        description = self._build_description(finding, triage)
        acceptance_criteria = self._generate_acceptance_criteria(finding)

        return FindingTask(
            title=f"Fix {finding.severity.value.upper()}: {finding.title}",
            description=description,
            severity=finding.severity.value,
            cwe_id=finding.cwe_id,
            location=f"{finding.location.file}:{finding.location.line_start}",
            finding_id=finding.id,
            priority=self.SEVERITY_PRIORITY_MAP[finding.severity],
            labels=self._generate_labels(finding),
            acceptance_criteria=acceptance_criteria,
        )

    def _create_grouped_task(
        self,
        cwe: str,
        findings: list[Finding],
        triage_map: dict,
    ) -> FindingTask:
        """Create a grouped task for multiple findings with same CWE."""
        # Use highest severity from group
        severities = [f.severity for f in findings]
        highest_severity = min(
            severities,
            key=lambda s: list(Severity).index(s),
        )

        # Build description with all locations
        locations_md = "\n".join(
            f"- `{f.location.file}:{f.location.line_start}` - {f.title}"
            for f in findings
        )

        first = findings[0]
        description = f"""## {cwe} - {first.title}

**{len(findings)} occurrences found**

### Affected Locations

{locations_md}

### Vulnerability Details

{first.description}

### Remediation

{first.remediation or "Apply appropriate fix based on vulnerability type."}
"""

        return FindingTask(
            title=f"Fix {cwe}: {first.title} ({len(findings)} occurrences)",
            description=description,
            severity=highest_severity.value,
            cwe_id=cwe if cwe != "UNKNOWN" else None,
            location=f"{first.location.file}:{first.location.line_start} (+{len(findings) - 1} more)",
            finding_id=findings[0].id,
            priority=self.SEVERITY_PRIORITY_MAP[highest_severity],
            labels=["security", cwe.lower().replace("-", ""), "grouped"],
            acceptance_criteria=[
                f"All {len(findings)} {cwe} findings are remediated",
                "No new findings introduced",
                "Security tests pass",
                "Code review completed",
            ],
        )

    def _build_description(self, finding: Finding, triage: Any | None) -> str:
        """Build task description with all relevant details."""
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

        if self.include_ai_explanation and triage:
            if hasattr(triage, "explanation") and triage.explanation:
                exp = triage.explanation
                desc += f"""
### AI Analysis

**Classification:** {triage.classification.value}
**Risk Score:** {triage.risk_score:.2f}

{exp.summary if hasattr(exp, "summary") else ""}
"""

        if finding.references:
            desc += """
### References

"""
            for ref in finding.references:
                desc += f"- {ref}\n"

        return desc

    def _generate_labels(self, finding: Finding) -> list[str]:
        """Generate labels for the task."""
        labels = ["security", finding.severity.value]

        if finding.cwe_id:
            labels.append(finding.cwe_id.lower().replace("-", ""))

        labels.append(finding.scanner)

        return labels

    def _generate_acceptance_criteria(self, finding: Finding) -> list[str]:
        """Generate acceptance criteria for the task."""
        criteria = [
            f"Vulnerability at {finding.location.file}:{finding.location.line_start} is fixed",
            "No regression in existing functionality",
        ]

        if finding.severity in [Severity.CRITICAL, Severity.HIGH]:
            criteria.append("Security test added to prevent regression")
            criteria.append("Code review by security-aware developer")

        criteria.append("Re-scan shows finding is resolved")

        return criteria


def create_tasks_from_findings(
    findings: list[Finding],
    triage_results: list | None = None,
    group_by_cwe: bool = False,
    max_tasks: int = 50,
) -> list[FindingTask]:
    """Convenience function to create tasks from findings.

    Args:
        findings: List of security findings.
        triage_results: Optional AI triage results.
        group_by_cwe: Group findings by CWE.
        max_tasks: Maximum tasks to create.

    Returns:
        List of FindingTask objects.
    """
    integration = BacklogIntegration(
        group_by_cwe=group_by_cwe,
        max_tasks=max_tasks,
    )
    return integration.create_tasks(findings, triage_results)
