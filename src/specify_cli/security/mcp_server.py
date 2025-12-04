"""Security Scanner MCP Server for JP Spec Kit.

This MCP server exposes security scanning capabilities through the
Model Context Protocol, enabling AI agents, IDEs, and dashboards
to query security findings and trigger scans.

CRITICAL: This server exposes data and orchestrates tools via subprocess.
It does NOT make LLM API calls. Skills are invoked by AI tools consuming
the MCP server.

Architecture:
    - Tools: Actions that can be invoked (scan, triage, fix)
    - Resources: Queryable data (findings, status, config)
    - NO LLM CALLS: Server returns data and skill invocation instructions

Reference: ADR-008 Security Scanner MCP Server Architecture
"""

import json
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from specify_cli.security.models import Finding, Severity
from specify_cli.security.orchestrator import ScannerOrchestrator
from specify_cli.security.adapters.semgrep import SemgrepAdapter
from specify_cli.security.adapters.discovery import ToolDiscovery

# Global project root (can be overridden for testing)
PROJECT_ROOT = Path.cwd()

# Initialize MCP server
mcp = FastMCP("jpspec-security") if MCP_AVAILABLE else None

# Initialize scanner orchestrator
_orchestrator = None


def _get_orchestrator() -> ScannerOrchestrator:
    """Get or create the scanner orchestrator (lazy initialization)."""
    global _orchestrator
    if _orchestrator is None:
        discovery = ToolDiscovery()
        adapters = []

        # Add available scanner adapters
        semgrep_adapter = SemgrepAdapter(discovery)
        if semgrep_adapter.is_available():
            adapters.append(semgrep_adapter)

        _orchestrator = ScannerOrchestrator(adapters)

    return _orchestrator


def _get_findings_dir() -> Path:
    """Get the findings directory, creating it if necessary."""
    findings_dir = PROJECT_ROOT / "docs" / "security"
    findings_dir.mkdir(parents=True, exist_ok=True)
    return findings_dir


# ============================================================================
# TOOLS (Actions that can be invoked)
# ============================================================================


if MCP_AVAILABLE:

    @mcp.tool()
    async def security_scan(
        target: str = ".",
        scanners: list[str] | None = None,
        fail_on: list[str] | None = None,
    ) -> dict[str, Any]:
        """Run security scan on target directory.

        This tool orchestrates scanner execution via subprocess.
        NO LLM API CALLS.

        Args:
            target: Directory to scan (default: current directory)
            scanners: List of scanners to run (default: all available)
            fail_on: Severity levels that cause failure (default: ["critical", "high"])

        Returns:
            Scan results with findings count and output file location.
        """
        target_path = PROJECT_ROOT / target
        orchestrator = _get_orchestrator()
        scanners = scanners or orchestrator.list_scanners()
        fail_on = fail_on or ["critical", "high"]

        # Run scan via orchestrator (subprocess execution)
        findings = orchestrator.scan(
            target=target_path,
            scanners=scanners,
            parallel=True,
            deduplicate=True,
        )

        # Save findings to JSON
        findings_dir = _get_findings_dir()
        findings_file = findings_dir / "scan-results.json"
        findings_data = [f.to_dict() for f in findings]

        with findings_file.open("w") as f:
            json.dump(
                {
                    "findings": findings_data,
                    "metadata": {
                        "scanners_used": scanners,
                        "total_count": len(findings),
                    },
                },
                f,
                indent=2,
            )

        # Count by severity
        by_severity = {
            "critical": sum(1 for f in findings if f.severity == Severity.CRITICAL),
            "high": sum(1 for f in findings if f.severity == Severity.HIGH),
            "medium": sum(1 for f in findings if f.severity == Severity.MEDIUM),
            "low": sum(1 for f in findings if f.severity == Severity.LOW),
            "info": sum(1 for f in findings if f.severity == Severity.INFO),
        }

        # Determine if scan should fail based on fail_on severities
        should_fail = any(by_severity.get(sev, 0) > 0 for sev in fail_on)

        return {
            "findings_count": len(findings),
            "by_severity": by_severity,
            "should_fail": should_fail,
            "fail_on": fail_on,
            "findings_file": str(findings_file.relative_to(PROJECT_ROOT)),
            "metadata": {
                "scanners_used": scanners,
                "target": target,
            },
        }

    @mcp.tool()
    async def security_triage(
        findings_file: str | None = None,
    ) -> dict[str, Any]:
        """Return skill invocation instruction for AI-powered triage.

        CRITICAL: This does NOT call LLMs. It returns instructions for
        the AI tool to invoke the security-triage skill.

        Args:
            findings_file: Path to findings JSON (default: latest scan results)

        Returns:
            Skill invocation instruction for AI tool to execute.
        """
        findings_dir = _get_findings_dir()

        if findings_file is None:
            findings_file = str(findings_dir / "scan-results.json")
        else:
            findings_file = str(PROJECT_ROOT / findings_file)

        # Verify findings file exists
        if not Path(findings_file).exists():
            return {
                "error": f"Findings file not found: {findings_file}",
                "suggestion": "Run security_scan first to generate findings",
            }

        return {
            "action": "invoke_skill",
            "skill": ".claude/skills/security-triage.md",
            "input_file": findings_file,
            "output_file": str(findings_dir / "triage-results.json"),
            "instruction": (
                "Invoke the security-triage skill to classify findings. "
                "The skill will analyze each finding and classify it as "
                "TRUE_POSITIVE, FALSE_POSITIVE, or NEEDS_INVESTIGATION."
            ),
        }

    @mcp.tool()
    async def security_fix(
        finding_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Return skill invocation instruction for fix generation.

        CRITICAL: This does NOT call LLMs. It returns instructions for
        the AI tool to invoke the security-fix skill.

        Args:
            finding_ids: Specific findings to fix (default: all true positives)

        Returns:
            Skill invocation instruction for AI tool to execute.
        """
        findings_dir = _get_findings_dir()
        triage_file = findings_dir / "triage-results.json"

        if not triage_file.exists():
            return {
                "error": "Triage results not found",
                "suggestion": "Run security_triage first to classify findings",
            }

        result = {
            "action": "invoke_skill",
            "skill": ".claude/skills/security-fix.md",
            "input_file": str(triage_file),
            "output_file": str(findings_dir / "fix-suggestions.json"),
            "instruction": (
                "Invoke the security-fix skill to generate remediation patches. "
                "The skill will analyze true positive findings and generate code fixes."
            ),
        }

        if finding_ids:
            result["filter"] = {"finding_ids": finding_ids}

        return result


# ============================================================================
# RESOURCES (Queryable data)
# ============================================================================


if MCP_AVAILABLE:

    @mcp.resource("security://findings")
    async def list_findings() -> str:
        """List all security findings.

        Returns:
            JSON string with list of findings.

        Note: Filtering and limiting should be done by the client
        after fetching all findings.
        """
        findings_dir = _get_findings_dir()
        findings_file = findings_dir / "scan-results.json"

        if not findings_file.exists():
            return json.dumps([])

        with findings_file.open() as f:
            data = json.load(f)

        findings = [Finding.from_dict(f) for f in data.get("findings", [])]

        return json.dumps([f.to_dict() for f in findings], indent=2)

    @mcp.resource("security://findings/{id}")
    async def get_finding(id: str) -> str:
        """Get specific finding by ID.

        Args:
            id: Finding ID (e.g., "SEMGREP-CWE-89-001")

        Returns:
            JSON string with finding details.
        """
        findings_dir = _get_findings_dir()
        findings_file = findings_dir / "scan-results.json"

        if not findings_file.exists():
            return json.dumps({"error": "Findings file not found"})

        with findings_file.open() as f:
            data = json.load(f)

        # Find matching finding
        for finding_data in data.get("findings", []):
            if finding_data["id"] == id:
                return json.dumps(finding_data, indent=2)

        return json.dumps({"error": f"Finding {id} not found"})

    @mcp.resource("security://status")
    async def get_status() -> str:
        """Get overall security posture.

        Returns:
            JSON string with security status summary.
        """
        findings_dir = _get_findings_dir()
        findings_file = findings_dir / "scan-results.json"
        triage_file = findings_dir / "triage-results.json"

        status = {
            "total_findings": 0,
            "by_severity": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            },
            "triage_status": "not_run",
            "security_posture": "unknown",
        }

        if findings_file.exists():
            with findings_file.open() as f:
                data = json.load(f)

            findings = [Finding.from_dict(f) for f in data.get("findings", [])]
            status["total_findings"] = len(findings)

            for finding in findings:
                status["by_severity"][finding.severity.value] += 1

            # Calculate posture
            critical_count = status["by_severity"]["critical"]
            high_count = status["by_severity"]["high"]

            if critical_count > 0:
                status["security_posture"] = "critical"
            elif high_count > 5:
                status["security_posture"] = "high_risk"
            elif high_count > 0:
                status["security_posture"] = "medium_risk"
            else:
                status["security_posture"] = "good"

        if triage_file.exists():
            status["triage_status"] = "completed"
            with triage_file.open() as f:
                triage_data = json.load(f)
                status["true_positives"] = triage_data.get("true_positives", 0)
                status["false_positives"] = triage_data.get("false_positives", 0)

        return json.dumps(status, indent=2)

    @mcp.resource("security://config")
    async def get_config() -> str:
        """Get scanner configuration.

        Returns:
            JSON string with current configuration.
        """
        orchestrator = _get_orchestrator()
        available_scanners = orchestrator.list_scanners()
        findings_dir = _get_findings_dir()

        config = {
            "available_scanners": available_scanners,
            "default_scanners": available_scanners[:1] if available_scanners else [],
            "fail_on": ["critical", "high"],
            "findings_directory": str(findings_dir.relative_to(PROJECT_ROOT)),
        }

        return json.dumps(config, indent=2)


def main() -> None:
    """Entry point for MCP server."""
    import sys

    if not MCP_AVAILABLE:
        print(
            "Error: mcp package not installed. Install with: uv add mcp",
            file=sys.stderr,
        )
        sys.exit(1)

    # Run server with stdio
    mcp.run()


if __name__ == "__main__":
    main()
