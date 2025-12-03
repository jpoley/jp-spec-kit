"""Security audit report generator.

This module generates comprehensive security audit reports from
scan and triage results in multiple output formats.
"""

import html
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from specify_cli.security.models import Finding
from specify_cli.security.reporter.models import (
    AuditReport,
    FindingSummary,
    Remediation,
    SecurityPosture,
)
from specify_cli.security.reporter.owasp import check_owasp_compliance


@dataclass
class ReportConfig:
    """Configuration for report generation."""

    project_name: str = "Security Audit"
    include_false_positives: bool = False
    max_remediations: int = 10


class ReportGenerator:
    """Security audit report generator.

    Generates comprehensive reports from scan and triage results.

    Example:
        >>> generator = ReportGenerator()
        >>> report = generator.generate(findings, triage_results)
        >>> markdown = generator.to_markdown(report)
    """

    def __init__(self, config: ReportConfig | None = None):
        """Initialize report generator."""
        self.config = config or ReportConfig()

    def generate(
        self,
        findings: list[Finding],
        triage_results: list | None = None,
        scanners: list[str] | None = None,
        files_scanned: int = 0,
    ) -> AuditReport:
        """Generate audit report from findings and triage results.

        Args:
            findings: List of security findings from scanners.
            triage_results: Optional list of triage results.
            scanners: List of scanner names used.
            files_scanned: Number of files scanned.

        Returns:
            Complete AuditReport.
        """
        # Build triage lookup
        triage_map = {}
        if triage_results:
            for result in triage_results:
                triage_map[result.finding_id] = result

        # Calculate summary
        summary = self._calculate_summary(findings, triage_map)

        # Check OWASP compliance
        owasp_compliance = check_owasp_compliance(findings, triage_results)

        # Generate remediations
        remediations = self._generate_remediations(findings, triage_map)

        # Determine security posture
        posture = self._determine_posture(summary, owasp_compliance)

        return AuditReport(
            project_name=self.config.project_name,
            scan_date=datetime.now(),
            posture=posture,
            summary=summary,
            owasp_compliance=owasp_compliance,
            remediations=remediations,
            scanners_used=scanners or [],
            files_scanned=files_scanned,
        )

    def _calculate_summary(
        self, findings: list[Finding], triage_map: dict
    ) -> FindingSummary:
        """Calculate findings summary."""
        total = len(findings)

        # Count by severity
        critical = sum(1 for f in findings if f.severity.value == "critical")
        high = sum(1 for f in findings if f.severity.value == "high")
        medium = sum(1 for f in findings if f.severity.value == "medium")
        low = sum(1 for f in findings if f.severity.value == "low")
        info = sum(1 for f in findings if f.severity.value == "info")

        # Count by triage status
        true_positives = 0
        false_positives = 0
        needs_investigation = 0

        for finding in findings:
            triage = triage_map.get(finding.id)
            if triage:
                if triage.classification.value == "TP":
                    true_positives += 1
                elif triage.classification.value == "FP":
                    false_positives += 1
                else:
                    needs_investigation += 1
            else:
                needs_investigation += 1  # Untriaged = needs investigation

        return FindingSummary(
            total=total,
            critical=critical,
            high=high,
            medium=medium,
            low=low,
            info=info,
            true_positives=true_positives,
            false_positives=false_positives,
            needs_investigation=needs_investigation,
        )

    def _determine_posture(
        self, summary: FindingSummary, owasp_compliance: list
    ) -> SecurityPosture:
        """Determine overall security posture."""
        # At Risk: Any critical findings or multiple non-compliant categories
        if summary.critical > 0:
            return SecurityPosture.AT_RISK

        non_compliant = sum(
            1 for c in owasp_compliance if c.status.value == "non_compliant"
        )
        if non_compliant >= 3:
            return SecurityPosture.AT_RISK

        # Conditional: High findings or some non-compliance
        if summary.high > 5 or non_compliant > 0:
            return SecurityPosture.CONDITIONAL

        # Secure: No critical/high and mostly compliant
        if summary.high == 0 and non_compliant == 0:
            return SecurityPosture.SECURE

        return SecurityPosture.CONDITIONAL

    def _generate_remediations(
        self, findings: list[Finding], triage_map: dict
    ) -> list[Remediation]:
        """Generate prioritized remediation recommendations."""
        remediations = []
        priority = 1

        # Sort findings by severity (critical first)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        sorted_findings = sorted(
            findings, key=lambda f: severity_order.get(f.severity.value, 5)
        )

        for finding in sorted_findings:
            # Skip false positives unless explicitly included via config
            triage = triage_map.get(finding.id)
            if triage and triage.classification.value == "FP":
                if not self.config.include_false_positives:
                    continue

            # Estimate effort based on severity
            effort_map = {
                "critical": "4-8 hours",
                "high": "2-4 hours",
                "medium": "1-2 hours",
                "low": "30 min - 1 hour",
                "info": "15-30 min",
            }

            remediation = Remediation(
                finding_id=finding.id,
                priority=priority,
                title=finding.title,
                description=finding.description,
                fix_guidance=finding.remediation or "Review and fix the vulnerability",
                estimated_effort=effort_map.get(finding.severity.value, "1 hour"),
                cwe_id=finding.cwe_id,
            )

            remediations.append(remediation)
            priority += 1

            if len(remediations) >= self.config.max_remediations:
                break

        return remediations

    def to_markdown(self, report: AuditReport) -> str:
        """Generate markdown report."""
        posture_emoji = {
            SecurityPosture.SECURE: "🟢",
            SecurityPosture.CONDITIONAL: "🟡",
            SecurityPosture.AT_RISK: "🔴",
        }

        md = f"""# Security Audit Report

**Project:** {report.project_name}
**Date:** {report.scan_date.strftime("%Y-%m-%d %H:%M")}
**Posture:** {posture_emoji.get(report.posture, "")} {report.posture.value.replace("_", " ").title()}
**Compliance Score:** {report.compliance_score}%

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Findings | {report.summary.total} |
| Critical | {report.summary.critical} |
| High | {report.summary.high} |
| Medium | {report.summary.medium} |
| Low | {report.summary.low} |
| True Positives | {report.summary.true_positives} |
| False Positives | {report.summary.false_positives} |
| Files Scanned | {report.files_scanned} |

## OWASP Top 10 Compliance

| Category | Status | Findings | Critical |
|----------|--------|----------|----------|
"""
        for cat in report.owasp_compliance:
            status_icon = {
                "compliant": "✅",
                "partial": "⚠️",
                "non_compliant": "❌",
            }
            md += f"| {cat.id} - {cat.name} | {status_icon.get(cat.status.value, '')} | {cat.finding_count} | {cat.critical_count} |\n"

        md += """
## Top Remediation Priorities

"""
        for i, rem in enumerate(report.top_remediations, 1):
            md += f"""### {i}. {rem.title}

**Priority:** P{rem.priority} | **CWE:** {rem.cwe_id or "N/A"} | **Effort:** {rem.estimated_effort}

{rem.description}

**Fix Guidance:** {rem.fix_guidance}

---

"""

        md += f"""
## Scanners Used

{", ".join(report.scanners_used) if report.scanners_used else "None specified"}

---

*Report generated by JP Spec Kit Security Audit*
"""

        return md

    def to_html(self, report: AuditReport) -> str:
        """Generate HTML report with proper markdown conversion."""
        markdown_content = self.to_markdown(report)

        # Convert markdown to HTML
        html_content = self._markdown_to_html(markdown_content)

        # HTML wrapper with styling
        html_output = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Audit Report - {report.project_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 2rem;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{ color: #1a1a2e; border-bottom: 2px solid #4a4e69; padding-bottom: 0.5rem; }}
        h2 {{ color: #4a4e69; margin-top: 2rem; }}
        h3 {{ color: #22223b; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{ background-color: #f8f9fa; font-weight: 600; }}
        tr:hover {{ background-color: #f5f5f5; }}
        code {{ background-color: #f4f4f4; padding: 0.2rem 0.4rem; border-radius: 3px; }}
        .posture-secure {{ color: #28a745; }}
        .posture-conditional {{ color: #ffc107; }}
        .posture-at-risk {{ color: #dc3545; }}
        hr {{ border: 0; border-top: 1px solid #eee; margin: 2rem 0; }}
        strong {{ font-weight: 600; }}
    </style>
</head>
<body>
    <div class="content">
{html_content}
    </div>
</body>
</html>
"""
        return html_output

    def _markdown_to_html(self, md: str) -> str:
        """Convert markdown to HTML.

        Handles the specific markdown patterns used in security reports:
        - Headers (h1, h2, h3)
        - Tables
        - Bold text
        - Horizontal rules
        - Paragraphs
        """
        lines = md.split("\n")
        html_lines = []
        in_table = False
        in_table_header = False

        for line in lines:
            # Escape HTML entities first (except for our formatting)
            escaped = html.escape(line)

            # Headers
            if escaped.startswith("### "):
                html_lines.append(f"<h3>{escaped[4:]}</h3>")
            elif escaped.startswith("## "):
                html_lines.append(f"<h2>{escaped[3:]}</h2>")
            elif escaped.startswith("# "):
                html_lines.append(f"<h1>{escaped[2:]}</h1>")
            # Horizontal rule
            elif escaped.strip() == "---":
                html_lines.append("<hr>")
            # Table rows
            elif escaped.startswith("|"):
                if not in_table:
                    html_lines.append("<table>")
                    in_table = True
                    in_table_header = True

                # Skip separator rows (|---|---|)
                if re.match(r"^\|[\s\-:|]+\|$", escaped):
                    continue

                cells = [c.strip() for c in escaped.split("|")[1:-1]]
                if in_table_header:
                    row = "<tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr>"
                    in_table_header = False
                else:
                    row = "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"
                html_lines.append(row)
            else:
                # Close table if we were in one
                if in_table:
                    html_lines.append("</table>")
                    in_table = False

                # Bold text (**text**)
                escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)

                # Non-empty paragraph
                if escaped.strip():
                    html_lines.append(f"<p>{escaped}</p>")

        # Close any open table
        if in_table:
            html_lines.append("</table>")

        return "\n".join(html_lines)

    def to_json(self, report: AuditReport) -> str:
        """Generate JSON report."""
        return json.dumps(report.to_dict(), indent=2, default=str)

    def save_report(
        self, report: AuditReport, output_path: Path, format: str = "markdown"
    ) -> None:
        """Save report to file.

        Args:
            report: The audit report to save.
            output_path: Path to save the report.
            format: Output format (markdown, html, json).
        """
        if format == "markdown":
            content = self.to_markdown(report)
        elif format == "html":
            content = self.to_html(report)
        elif format == "json":
            content = self.to_json(report)
        else:
            raise ValueError(f"Unsupported format: {format}")

        output_path.write_text(content)
