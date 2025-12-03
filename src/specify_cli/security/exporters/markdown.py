"""Markdown exporter for security findings.

Human-readable Markdown reports for documentation, code reviews, and
security reviews.
"""

from collections import defaultdict
from datetime import datetime, timezone

from specify_cli.security.exporters.base import BaseExporter
from specify_cli.security.models import Finding, Severity


class MarkdownExporter(BaseExporter):
    """Export findings to Markdown report format.

    This exporter generates human-readable Markdown reports suitable for:
        - Security review documentation
        - Code review comments
        - Developer documentation
        - Executive summaries

    The report includes:
        - Summary table by severity
        - Detailed findings grouped by severity
        - Code snippets and remediation guidance
    """

    def export(self, findings: list[Finding]) -> str:
        """Generate Markdown report from findings.

        Args:
            findings: List of security findings

        Returns:
            Markdown-formatted report as a string

        Example:
            >>> exporter = MarkdownExporter()
            >>> markdown = exporter.export(findings)
            >>> with open("security-report.md", "w") as f:
            ...     f.write(markdown)
        """
        lines = [
            "# Security Scan Results",
            "",
            f"**Date:** {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Total Findings:** {len(findings)}",
            "",
        ]

        # Summary by severity
        by_severity: dict[Severity, list[Finding]] = defaultdict(list)
        for finding in findings:
            by_severity[finding.severity].append(finding)

        lines.append("## Summary")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("|----------|-------|")
        for severity in Severity:
            count = len(by_severity[severity])
            if count > 0:
                emoji = self._severity_emoji(severity)
                lines.append(f"| {emoji} {severity.value.title()} | {count} |")
        lines.append("")

        # Findings by severity (critical to info)
        for severity in Severity:
            findings_at_severity = by_severity[severity]
            if not findings_at_severity:
                continue

            lines.append(f"## {severity.value.title()} Severity Findings")
            lines.append("")

            for i, finding in enumerate(findings_at_severity, 1):
                lines.extend(self._format_finding(i, finding))

        return "\n".join(lines)

    def _format_finding(self, number: int, finding: Finding) -> list[str]:
        """Format a single finding as Markdown.

        Args:
            number: Finding number within severity group
            finding: Finding to format

        Returns:
            List of Markdown lines
        """
        lines = [
            f"### {number}. {finding.title}",
            "",
            f"**Location:** `{finding.location.file}:{finding.location.line_start}`",
            f"**CWE:** {finding.cwe_id or 'N/A'}",
            f"**Scanner:** {finding.scanner}",
            f"**Confidence:** {finding.confidence.value}",
            "",
        ]

        # Description
        lines.append(finding.description)
        lines.append("")

        # Code snippet
        if finding.location.code_snippet:
            lines.append("**Vulnerable Code:**")
            lines.append("```")
            lines.append(finding.location.code_snippet)
            lines.append("```")
            lines.append("")

        # Remediation
        if finding.remediation:
            lines.append("**Remediation:**")
            lines.append(finding.remediation)
            lines.append("")

        # References
        if finding.references:
            lines.append("**References:**")
            for ref in finding.references:
                lines.append(f"- {ref}")
            lines.append("")

        return lines

    def _severity_emoji(self, severity: Severity) -> str:
        """Get emoji for severity level.

        Args:
            severity: Severity level

        Returns:
            Emoji character
        """
        mapping = {
            Severity.CRITICAL: "🔴",
            Severity.HIGH: "🟠",
            Severity.MEDIUM: "🟡",
            Severity.LOW: "🔵",
            Severity.INFO: "⚪",
        }
        return mapping[severity]
