#!/usr/bin/env python3
"""Demonstration of Unified Finding Format (UFFormat).

This script shows how to:
1. Create security findings
2. Merge findings from multiple scanners
3. Export to different formats (JSON, SARIF, Markdown)

Run with: python examples/ufformat_demo.py
"""

import json
from pathlib import Path

from specify_cli.security.exporters import (
    JSONExporter,
    MarkdownExporter,
    SARIFExporter,
)
from specify_cli.security.models import Confidence, Finding, Location, Severity


def create_sample_findings() -> list[Finding]:
    """Create sample security findings for demonstration."""
    # Finding 1: SQL Injection from Semgrep
    sql_injection_semgrep = Finding(
        id="SEMGREP-CWE-89-001",
        scanner="semgrep",
        severity=Severity.CRITICAL,
        title="SQL Injection",
        description="User input is passed directly to SQL query without sanitization",
        location=Location(
            file=Path("src/app.py"),
            line_start=42,
            line_end=45,
            column_start=10,
            column_end=55,
            code_snippet="query = 'SELECT * FROM users WHERE id=' + user_id",
        ),
        cwe_id="CWE-89",
        cvss_score=9.8,
        confidence=Confidence.MEDIUM,
        remediation="Use parameterized queries instead of string concatenation",
        references=[
            "https://cwe.mitre.org/data/definitions/89.html",
            "https://owasp.org/www-community/attacks/SQL_Injection",
        ],
    )

    # Finding 2: Same SQL Injection from CodeQL (will merge)
    sql_injection_codeql = Finding(
        id="CODEQL-SQL-001",
        scanner="codeql",
        severity=Severity.HIGH,
        title="SQL Injection",
        description="SQL injection vulnerability detected",
        location=Location(
            file=Path("src/app.py"),
            line_start=42,
            line_end=45,
            code_snippet="query = 'SELECT * FROM users WHERE id=' + user_id",
        ),
        cwe_id="CWE-89",
        confidence=Confidence.MEDIUM,
        references=["https://codeql.github.com/sql-injection"],
    )

    # Finding 3: XSS from Semgrep
    xss_finding = Finding(
        id="SEMGREP-CWE-79-002",
        scanner="semgrep",
        severity=Severity.HIGH,
        title="Cross-Site Scripting (XSS)",
        description="User input is rendered without HTML escaping",
        location=Location(
            file=Path("src/templates.py"),
            line_start=20,
            line_end=22,
            code_snippet='return f"<h1>Hello {username}</h1>"',
        ),
        cwe_id="CWE-79",
        cvss_score=7.5,
        confidence=Confidence.HIGH,
        remediation="Use template engine with automatic HTML escaping",
        references=["https://owasp.org/www-community/attacks/xss/"],
    )

    # Finding 4: Path Traversal from Trivy
    path_traversal = Finding(
        id="TRIVY-CWE-22-003",
        scanner="trivy",
        severity=Severity.MEDIUM,
        title="Path Traversal",
        description="User-controlled file path without validation",
        location=Location(
            file=Path("src/utils.py"),
            line_start=30,
            line_end=32,
            code_snippet="with open(user_file, 'r') as f:",
        ),
        cwe_id="CWE-22",
        cvss_score=5.5,
        confidence=Confidence.MEDIUM,
        remediation="Validate file paths and use Path.resolve() to prevent traversal",
        references=["https://cwe.mitre.org/data/definitions/22.html"],
    )

    return [sql_injection_semgrep, sql_injection_codeql, xss_finding, path_traversal]


def demonstrate_fingerprinting(findings: list[Finding]) -> None:
    """Show how fingerprinting works for deduplication."""
    print("=== Fingerprinting Demo ===\n")

    for finding in findings:
        fp = finding.fingerprint()
        print(f"{finding.scanner:10} | {finding.id:20} | Fingerprint: {fp}")

    print(
        "\nNotice: Semgrep and CodeQL have the SAME fingerprint for the SQL injection."
    )
    print("This allows us to detect that they found the same vulnerability.\n")


def demonstrate_merging(findings: list[Finding]) -> list[Finding]:
    """Show how to merge findings from multiple scanners."""
    print("=== Merging Demo ===\n")

    # Build fingerprint index
    by_fingerprint: dict[str, Finding] = {}

    for finding in findings:
        fp = finding.fingerprint()

        if fp not in by_fingerprint:
            by_fingerprint[fp] = finding
            print(f"New finding: {finding.scanner} - {finding.title}")
        else:
            print(f"Merging: {finding.scanner} - {finding.title}")
            existing = by_fingerprint[fp]
            print(
                f"  Before merge: severity={existing.severity.value}, confidence={existing.confidence.value}"
            )
            existing.merge(finding)
            print(
                f"  After merge:  severity={existing.severity.value}, confidence={existing.confidence.value}"
            )

    merged_findings = list(by_fingerprint.values())
    print(f"\nResult: {len(findings)} findings merged to {len(merged_findings)}\n")

    return merged_findings


def demonstrate_json_export(findings: list[Finding]) -> None:
    """Show JSON export."""
    print("=== JSON Export Demo ===\n")

    exporter = JSONExporter(pretty=True)
    json_output = exporter.export(findings)

    # Show first 500 chars
    preview = json_output[:500] + "..." if len(json_output) > 500 else json_output
    print(preview)
    print()


def demonstrate_sarif_export(findings: list[Finding]) -> None:
    """Show SARIF export."""
    print("=== SARIF Export Demo ===\n")

    exporter = SARIFExporter(tool_name="jpspec-demo", tool_version="1.0.0")
    sarif_doc = exporter.export(findings)

    print(f"SARIF Version: {sarif_doc['version']}")
    print(f"Number of runs: {len(sarif_doc['runs'])}")

    for run in sarif_doc["runs"]:
        scanner = run["tool"]["driver"]["name"]
        result_count = len(run["results"])
        rule_count = len(run["tool"]["driver"]["rules"])
        print(f"  - {scanner}: {result_count} results, {rule_count} rules")

    print("\nSARIF Preview (first result):")
    if sarif_doc["runs"]:
        first_result = sarif_doc["runs"][0]["results"][0]
        print(json.dumps(first_result, indent=2)[:400] + "...")

    print()


def demonstrate_markdown_export(findings: list[Finding]) -> None:
    """Show Markdown export."""
    print("=== Markdown Export Demo ===\n")

    exporter = MarkdownExporter()
    markdown = exporter.export(findings)

    # Show first 800 chars
    preview = markdown[:800] + "\n..." if len(markdown) > 800 else markdown
    print(preview)
    print()


def main() -> None:
    """Run all demonstrations."""
    print("Unified Finding Format (UFFormat) Demonstration\n")
    print("=" * 60)
    print()

    # Create sample findings
    findings = create_sample_findings()
    print(f"Created {len(findings)} sample findings\n")

    # Show fingerprinting
    demonstrate_fingerprinting(findings)

    # Show merging
    merged_findings = demonstrate_merging(findings)

    # Show exports
    demonstrate_json_export(merged_findings)
    demonstrate_sarif_export(merged_findings)
    demonstrate_markdown_export(merged_findings)

    print("=" * 60)
    print("\nDemo complete! UFFormat provides:")
    print("  ✓ Scanner-agnostic data model")
    print("  ✓ Automatic deduplication via fingerprinting")
    print("  ✓ Intelligent merging (severity escalation, confidence boosting)")
    print("  ✓ Multiple export formats (JSON, SARIF 2.1.0, Markdown)")
    print("  ✓ Full type safety with Python dataclasses")


if __name__ == "__main__":
    main()
