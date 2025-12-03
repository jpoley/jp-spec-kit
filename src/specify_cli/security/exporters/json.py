"""JSON exporter for security findings.

Simple JSON export format for APIs, data processing, and storage.
"""

import json
from typing import Any

from specify_cli.security.exporters.base import BaseExporter
from specify_cli.security.models import Finding


class JSONExporter(BaseExporter):
    """Export findings to JSON format.

    This exporter produces a simple JSON representation of findings,
    suitable for:
        - REST API responses
        - Data processing pipelines
        - Storage in databases
        - Interchange between systems

    The output is a JSON object with a top-level "findings" array.
    """

    def __init__(self, *, pretty: bool = True) -> None:
        """Initialize JSON exporter.

        Args:
            pretty: If True, format JSON with indentation for readability
        """
        self.pretty = pretty

    def export(self, findings: list[Finding]) -> str:
        """Export findings to JSON string.

        Args:
            findings: List of security findings

        Returns:
            JSON string representation

        Example:
            >>> exporter = JSONExporter(pretty=True)
            >>> json_output = exporter.export(findings)
            >>> print(json_output)
            {
              "findings": [
                {
                  "id": "SEMGREP-001",
                  "severity": "high",
                  ...
                }
              ]
            }
        """
        data = {
            "findings": [f.to_dict() for f in findings],
        }

        if self.pretty:
            return json.dumps(data, indent=2)
        return json.dumps(data)

    def export_dict(self, findings: list[Finding]) -> dict[str, Any]:
        """Export findings to dictionary (for in-memory use).

        Args:
            findings: List of security findings

        Returns:
            Dictionary representation
        """
        return {
            "findings": [f.to_dict() for f in findings],
        }
