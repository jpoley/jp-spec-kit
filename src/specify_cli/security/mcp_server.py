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

Security:
    - Path traversal protection: All user paths validated against PROJECT_ROOT
    - Input validation: Scanner names and severity levels validated against whitelist
    - Resource limits: Maximum findings count to prevent DoS

Reference: ADR-008 Security Scanner MCP Server Architecture
"""

import json
import os
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

# Global project root (can be overridden via PROJECT_ROOT env var for testing)
PROJECT_ROOT = Path(os.environ.get("PROJECT_ROOT", str(Path.cwd())))

# Resource limits
# Limit findings to 10,000 per scan to prevent DoS attacks and excessive memory usage.
# This value accommodates typical scan sizes for large projects while preventing abuse.
# See module docstring ("Resource limits") and ADR-008 for architecture details.
MAX_FINDINGS = 10000

# Valid values for input validation (whitelist)
VALID_SCANNERS = frozenset({"semgrep", "codeql", "trivy", "bandit", "safety"})
VALID_SEVERITIES = frozenset({"critical", "high", "medium", "low", "info"})

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


def _validate_path(user_path: str, base_dir: Path) -> Path:
    """Validate and resolve path within base directory.

    Prevents path traversal attacks by ensuring the resolved path
    remains within the base directory.

    Args:
        user_path: User-supplied path (must be relative)
        base_dir: Base directory to constrain paths to

    Returns:
        Validated absolute path

    Raises:
        ValueError: If path is absolute or escapes base_dir
    """
    # Reject absolute paths
    if Path(user_path).is_absolute():
        raise ValueError(f"Absolute paths not allowed: {user_path}")

    # Resolve to canonical path
    resolved = (base_dir / user_path).resolve()

    # Verify it's within base_dir (path traversal protection)
    try:
        resolved.relative_to(base_dir.resolve())
    except ValueError:
        raise ValueError(f"Path traversal detected: {user_path}")

    return resolved


def _validate_scanners(scanners: list[str] | None, available: list[str]) -> list[str]:
    """Validate scanner names against whitelist.

    Args:
        scanners: User-provided scanner names
        available: List of available scanners from orchestrator

    Returns:
        Validated list of scanner names

    Raises:
        ValueError: If invalid scanner names provided
    """
    if scanners is None:
        return available

    # Check against whitelist (defense-in-depth)
    invalid = [s for s in scanners if s not in VALID_SCANNERS]
    if invalid:
        raise ValueError(
            f"Invalid scanner names: {invalid}. Valid: {list(VALID_SCANNERS)}"
        )

    # Also check if available
    unavailable = [s for s in scanners if s not in available]
    if unavailable:
        raise ValueError(
            f"Scanners not available: {unavailable}. Available: {available}"
        )

    return scanners


def _validate_severities(severities: list[str] | None) -> list[str]:
    """Validate severity levels against whitelist.

    Args:
        severities: User-provided severity levels

    Returns:
        Validated list of severity levels

    Raises:
        ValueError: If invalid severity levels provided
    """
    if severities is None:
        return ["critical", "high"]

    invalid = [s for s in severities if s not in VALID_SEVERITIES]
    if invalid:
        raise ValueError(
            f"Invalid severities: {invalid}. Valid: {list(VALID_SEVERITIES)}"
        )

    return severities


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
            target: Directory to scan (default: current directory, relative paths only)
            scanners: List of scanners to run (default: all available)
            fail_on: Severity levels that cause failure (default: ["critical", "high"])

        Returns:
            Scan results with findings count and output file location.
        """
        # Validate target path (prevents path traversal)
        try:
            target_path = _validate_path(target, PROJECT_ROOT)
        except ValueError as e:
            return {
                "error": "Invalid target path",
                "detail": str(e),
                "findings_count": 0,
            }

        # Verify target exists
        if not target_path.exists():
            return {
                "error": "Target path does not exist",
                "detail": str(target_path),
                "findings_count": 0,
            }

        orchestrator = _get_orchestrator()
        available_scanners = orchestrator.list_scanners()

        # Validate scanners (defense-in-depth)
        try:
            validated_scanners = _validate_scanners(scanners, available_scanners)
        except ValueError as e:
            return {
                "error": "Invalid scanners",
                "detail": str(e),
                "findings_count": 0,
            }

        # Validate fail_on severities
        try:
            validated_fail_on = _validate_severities(fail_on)
        except ValueError as e:
            return {
                "error": "Invalid severity levels",
                "detail": str(e),
                "findings_count": 0,
            }

        # Run scan via orchestrator (subprocess execution)
        findings = orchestrator.scan(
            target=target_path,
            scanners=validated_scanners,
            parallel=True,
            deduplicate=True,
        )

        # Apply resource limit
        truncated = False
        if len(findings) > MAX_FINDINGS:
            truncated = True
            findings = findings[:MAX_FINDINGS]

        # Save findings to JSON with secure permissions from creation
        # Using os.open with O_CREAT|O_WRONLY|O_TRUNC and mode 0o600 ensures
        # file is created with restrictive permissions atomically, avoiding
        # race condition if chmod is called after file creation.
        findings_dir = _get_findings_dir()
        findings_file = findings_dir / "scan-results.json"
        findings_data = [f.to_dict() for f in findings]

        fd = os.open(
            str(findings_file),
            os.O_CREAT | os.O_WRONLY | os.O_TRUNC,
            0o600,
        )
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(
                    {
                        "findings": findings_data,
                        "metadata": {
                            "scanners_used": validated_scanners,
                            "total_count": len(findings),
                            "truncated": truncated,
                        },
                    },
                    f,
                    indent=2,
                )
        except Exception:
            # fd is closed by os.fdopen even on error, but re-raise
            raise

        # Count by severity
        by_severity = {
            "critical": sum(1 for f in findings if f.severity == Severity.CRITICAL),
            "high": sum(1 for f in findings if f.severity == Severity.HIGH),
            "medium": sum(1 for f in findings if f.severity == Severity.MEDIUM),
            "low": sum(1 for f in findings if f.severity == Severity.LOW),
            "info": sum(1 for f in findings if f.severity == Severity.INFO),
        }

        # Determine if scan should fail based on fail_on severities
        should_fail = any(by_severity.get(sev, 0) > 0 for sev in validated_fail_on)

        return {
            "findings_count": len(findings),
            "by_severity": by_severity,
            "should_fail": should_fail,
            "fail_on": validated_fail_on,
            "findings_file": str(findings_file.relative_to(PROJECT_ROOT)),
            "truncated": truncated,
            "metadata": {
                "scanners_used": validated_scanners,
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
            findings_file: Path to findings JSON (default: latest scan results, relative paths only)

        Returns:
            Skill invocation instruction for AI tool to execute.
        """
        findings_dir = _get_findings_dir()

        if findings_file is None:
            validated_path = findings_dir / "scan-results.json"
        else:
            # Validate user-provided path (prevents path traversal)
            try:
                validated_path = _validate_path(findings_file, PROJECT_ROOT)
            except ValueError as e:
                return {
                    "error": "Invalid findings file path",
                    "detail": str(e),
                    "suggestion": "Use a relative path within the project",
                }

        # Verify findings file exists
        if not validated_path.exists():
            return {
                "error": "Findings file not found",
                "suggestion": "Run security_scan first to generate findings",
            }

        return {
            "action": "invoke_skill",
            "skill": ".claude/skills/security-triage.md",
            "input_file": str(validated_path),
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
