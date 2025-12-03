"""SARIF 2.1.0 exporter for security findings.

SARIF (Static Analysis Results Interchange Format) is the industry standard
for static analysis results. This exporter produces SARIF 2.1.0 documents
that can be consumed by:
    - GitHub Code Scanning
    - Azure DevOps
    - GitLab Security Dashboard
    - Many other security platforms

Reference: https://docs.oasis-open.org/sarif/sarif/v2.1.0/
"""

from collections import defaultdict
from typing import Any

from specify_cli.security.exporters.base import BaseExporter
from specify_cli.security.models import Finding


class SARIFExporter(BaseExporter):
    """Export findings to SARIF 2.1.0 format.

    SARIF is the industry-standard format for static analysis results.
    It's designed for interoperability between security tools and platforms.

    This exporter creates a complete SARIF document with:
        - Schema reference
        - Version information
        - One or more "runs" (one per scanner)
        - Tool metadata
        - Results (findings)
        - Rules (vulnerability types)
    """

    def __init__(
        self,
        tool_name: str = "jpspec-security",
        tool_version: str = "1.0.0",
    ) -> None:
        """Initialize SARIF exporter.

        Args:
            tool_name: Name of the tool generating the SARIF document
            tool_version: Version of the tool
        """
        self.tool_name = tool_name
        self.tool_version = tool_version

    def export(self, findings: list[Finding]) -> dict[str, Any]:
        """Export findings to SARIF 2.1.0 document.

        Each scanner gets its own "run" in the SARIF document, as per
        the SARIF specification. This ensures proper attribution of
        results to their source tools.

        Args:
            findings: List of security findings

        Returns:
            SARIF 2.1.0 document as a dictionary (JSON-serializable)

        Example:
            >>> exporter = SARIFExporter()
            >>> sarif_doc = exporter.export(findings)
            >>> import json
            >>> print(json.dumps(sarif_doc, indent=2))
        """
        # Group findings by scanner (SARIF has one run per tool)
        by_scanner: dict[str, list[Finding]] = defaultdict(list)
        for finding in findings:
            by_scanner[finding.scanner].append(finding)

        # Create a run for each scanner
        runs = []
        for scanner, scanner_findings in by_scanner.items():
            run = self._create_run(scanner, scanner_findings)
            runs.append(run)

        return {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": runs,
        }

    def _create_run(self, scanner: str, findings: list[Finding]) -> dict[str, Any]:
        """Create a SARIF run object for one scanner.

        A "run" represents the results from a single analysis tool.
        It includes:
            - Tool metadata (driver name, version, etc.)
            - Rules (vulnerability types found)
            - Results (individual findings)

        Args:
            scanner: Name of the scanner (e.g., "semgrep", "codeql")
            findings: Findings from this scanner

        Returns:
            SARIF run object
        """
        # Extract unique rules (CWE IDs or finding IDs)
        rules = {}
        for finding in findings:
            rule_id = finding.cwe_id or finding.id
            if rule_id not in rules:
                rules[rule_id] = self._create_rule(finding)

        return {
            "tool": {
                "driver": {
                    "name": scanner,
                    "version": self.tool_version,
                    "informationUri": f"https://specify-cli.dev/security/{scanner}",
                    "rules": list(rules.values()),
                }
            },
            "results": [f.to_sarif() for f in findings],
        }

    def _create_rule(self, finding: Finding) -> dict[str, Any]:
        """Create a SARIF rule object from a finding.

        Rules describe the vulnerability types that can be detected.
        Multiple findings can reference the same rule (e.g., multiple
        SQL injection findings all reference the CWE-89 rule).

        Args:
            finding: Finding to extract rule information from

        Returns:
            SARIF rule object
        """
        rule_id = finding.cwe_id or finding.id

        rule: dict[str, Any] = {
            "id": rule_id,
            "name": finding.title,
            "shortDescription": {
                "text": finding.title,
            },
            "fullDescription": {
                "text": finding.description,
            },
            "help": {
                "text": finding.remediation or "No remediation guidance available.",
            },
        }

        # Add properties if available
        properties = {}
        if finding.cwe_id:
            properties["cwe"] = finding.cwe_id
        if finding.cvss_score is not None:
            properties["cvss"] = finding.cvss_score

        if properties:
            rule["properties"] = properties

        return rule
