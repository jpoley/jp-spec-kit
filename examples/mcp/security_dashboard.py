#!/usr/bin/env python3
"""Example: Cross-repo security dashboard using MCP.

This example demonstrates how to:
1. Query security findings across multiple repositories
2. Aggregate security status into a unified dashboard
3. Display security posture trends

Requirements:
    - JP Spec Kit installed in each repository
    - MCP SDK installed: uv add mcp
    - Each repo has .mcp.json configured with jpspec-security server

Usage:
    python examples/mcp/security_dashboard.py --repos /path/to/repo1 /path/to/repo2
    python examples/mcp/security_dashboard.py --repos . ../other-project --show-critical
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from mcp_utils import (
    DEFAULT_MCP_TIMEOUT,
    MAX_DESCRIPTION_LENGTH,
    SEPARATOR_LONG,
    SEPARATOR_WIDTH,
    MCPConnectionError,
    MCPResponseError,
    connect_to_security_mcp,
    parse_mcp_response,
    truncate_description,
    validate_target_directory,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Table formatting constants
COL_REPO = 25
COL_POSTURE = 12
COL_TOTAL = 6
COL_SEVERITY = 3  # C, H, M, L columns
COL_TRIAGE = 12


class DashboardError(Exception):
    """Error during dashboard execution."""

    pass


@dataclass
class RepositoryStatus:
    """Security status for a single repository.

    Attributes:
        name: Repository name (directory name)
        path: Full path to repository
        status: Connection status ("healthy" or "error")
        total_findings: Total number of security findings
        critical: Number of critical severity findings
        high: Number of high severity findings
        medium: Number of medium severity findings
        low: Number of low severity findings
        info: Number of info severity findings
        posture: Overall security posture assessment
        triage_status: Status of triage process
        true_positives: Number of confirmed true positive findings
        false_positives: Number of confirmed false positive findings
        error_message: Error details if status is "error"
    """

    name: str
    path: str
    status: Literal["healthy", "error"]

    # These are optional - only present when status="healthy"
    total_findings: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0
    posture: str = "unknown"
    triage_status: str = "not_run"
    true_positives: int = 0
    false_positives: int = 0

    # Error details - only present when status="error"
    error_message: str | None = None

    def is_healthy(self) -> bool:
        """Check if repository connection was successful."""
        return self.status == "healthy"


async def get_repo_status(
    repo_path: Path,
    timeout: int = DEFAULT_MCP_TIMEOUT,
) -> RepositoryStatus:
    """Query security status for a single repository.

    Args:
        repo_path: Path to repository
        timeout: Connection timeout in seconds

    Returns:
        RepositoryStatus with either healthy data or error details
    """
    try:
        async with connect_to_security_mcp(
            project_root=repo_path, timeout=timeout
        ) as session:
            # Query security status
            status_response = await session.read_resource("security://status")
            status_data = parse_mcp_response(status_response)

            by_severity = status_data.get("by_severity", {})

            return RepositoryStatus(
                name=repo_path.name,
                path=str(repo_path),
                status="healthy",
                total_findings=status_data.get("total_findings", 0),
                critical=by_severity.get("critical", 0),
                high=by_severity.get("high", 0),
                medium=by_severity.get("medium", 0),
                low=by_severity.get("low", 0),
                info=by_severity.get("info", 0),
                posture=status_data.get("security_posture", "unknown"),
                triage_status=status_data.get("triage_status", "not_run"),
                true_positives=status_data.get("true_positives", 0),
                false_positives=status_data.get("false_positives", 0),
            )

    except (MCPConnectionError, MCPResponseError) as e:
        logger.warning(f"Could not connect to MCP server for {repo_path}: {e}")
        return RepositoryStatus(
            name=repo_path.name,
            path=str(repo_path),
            status="error",
            error_message=str(e),
        )
    except Exception as e:
        logger.exception(f"Unexpected error querying {repo_path}")
        return RepositoryStatus(
            name=repo_path.name,
            path=str(repo_path),
            status="error",
            error_message=f"Unexpected error: {e}",
        )


async def query_specific_findings(
    repo_path: Path,
    severity_filter: str | None = None,
    timeout: int = DEFAULT_MCP_TIMEOUT,
) -> list[dict[str, Any]]:
    """Query specific findings from a repository.

    Args:
        repo_path: Path to repository
        severity_filter: Optional severity to filter by (e.g., "critical")
        timeout: Connection timeout in seconds

    Returns:
        List of findings matching filter
    """
    try:
        async with connect_to_security_mcp(
            project_root=repo_path, timeout=timeout
        ) as session:
            # Query all findings
            findings_response = await session.read_resource("security://findings")
            findings_data = parse_mcp_response(findings_response)

            # Apply client-side filtering (MCP server doesn't support server-side filtering)
            if severity_filter:
                findings_data = [
                    f for f in findings_data if f.get("severity") == severity_filter
                ]

            return findings_data

    except (MCPConnectionError, MCPResponseError) as e:
        logger.warning(f"Could not query findings from {repo_path}: {e}")
        return []
    except Exception:
        logger.exception(f"Unexpected error querying findings from {repo_path}")
        return []


def print_dashboard(repository_statuses: list[RepositoryStatus]) -> None:
    """Print security dashboard to console.

    Args:
        repository_statuses: List of repository status objects
    """
    # Filter to only healthy connections for display
    healthy_repos = [r for r in repository_statuses if r.is_healthy()]
    error_repos = [r for r in repository_statuses if not r.is_healthy()]

    print(f"\n{'=' * SEPARATOR_LONG}")
    print(f"{' ' * 35}SECURITY DASHBOARD")
    print(f"{'=' * SEPARATOR_LONG}\n")

    if not healthy_repos:
        print("No repositories could be queried successfully.\n")
    else:
        # Header
        print(
            f"{'Repository':<{COL_REPO}} | "
            f"{'Posture':<{COL_POSTURE}} | "
            f"{'Total':<{COL_TOTAL}} | "
            f"{'C':<{COL_SEVERITY}} | "
            f"{'H':<{COL_SEVERITY}} | "
            f"{'M':<{COL_SEVERITY}} | "
            f"{'L':<{COL_SEVERITY}} | "
            f"{'Triage':<{COL_TRIAGE}}"
        )
        print(f"{'-' * SEPARATOR_LONG}")

        # Rows
        posture_display_map = {
            "critical": "CRITICAL",
            "high_risk": "HIGH RISK",
            "medium_risk": "MEDIUM",
            "good": "GOOD",
            "unknown": "UNKNOWN",
        }

        for repo in healthy_repos:
            posture_display = posture_display_map.get(
                repo.posture, repo.posture.upper()
            )

            triage_display = (
                f"{repo.true_positives}TP/{repo.false_positives}FP"
                if repo.triage_status == "completed"
                else repo.triage_status.upper()
            )

            print(
                f"{repo.name:<{COL_REPO}} | "
                f"{posture_display:<{COL_POSTURE}} | "
                f"{repo.total_findings:<{COL_TOTAL}} | "
                f"{repo.critical:<{COL_SEVERITY}} | "
                f"{repo.high:<{COL_SEVERITY}} | "
                f"{repo.medium:<{COL_SEVERITY}} | "
                f"{repo.low:<{COL_SEVERITY}} | "
                f"{triage_display:<{COL_TRIAGE}}"
            )

        print(f"{'-' * SEPARATOR_LONG}")

    # Show errors if any
    if error_repos:
        print("\nConnection Errors:")
        for repo in error_repos:
            print(f"  {repo.name}: {repo.error_message}")

    if healthy_repos:
        # Summary statistics
        total_repos = len(healthy_repos)
        total_findings = sum(r.total_findings for r in healthy_repos)
        total_critical = sum(r.critical for r in healthy_repos)
        total_high = sum(r.high for r in healthy_repos)

        critical_repos = sum(1 for r in healthy_repos if r.posture == "critical")
        high_risk_repos = sum(1 for r in healthy_repos if r.posture == "high_risk")
        good_repos = sum(1 for r in healthy_repos if r.posture == "good")

        print("\nSummary:")
        print(f"  Total Repositories: {total_repos}")
        print(f"  Total Findings: {total_findings}")
        print(f"  Critical Findings: {total_critical}")
        print(f"  High Findings: {total_high}")
        print("\nPosture Distribution:")
        print(f"  Critical: {critical_repos} repos")
        print(f"  High Risk: {high_risk_repos} repos")
        print(f"  Good: {good_repos} repos")

        # Recommendations
        print("\nRecommendations:")
        if critical_repos > 0:
            print(f"  URGENT: {critical_repos} repos have CRITICAL vulnerabilities!")
            print("          Review and fix immediately.")
        if high_risk_repos > 0:
            print(f"  WARNING: {high_risk_repos} repos have HIGH risk issues.")
            print("           Prioritize remediation.")
        if good_repos == total_repos:
            print("  EXCELLENT: All repositories have good security posture!")

    print(f"\n{'=' * SEPARATOR_LONG}\n")


async def show_critical_findings(
    repos: list[Path],
    timeout: int = DEFAULT_MCP_TIMEOUT,
) -> None:
    """Show all critical findings across repositories.

    Args:
        repos: List of repository paths
        timeout: Connection timeout in seconds
    """
    print(f"\n{'=' * SEPARATOR_LONG}")
    print(f"{' ' * 35}CRITICAL FINDINGS")
    print(f"{'=' * SEPARATOR_LONG}\n")

    total_critical = 0

    for repo_path in repos:
        critical_findings = await query_specific_findings(
            repo_path, "critical", timeout
        )

        if critical_findings:
            print(f"\n{repo_path.name}:")
            print(f"{'-' * SEPARATOR_WIDTH}")

            for i, finding in enumerate(critical_findings, 1):
                total_critical += 1
                print(f"\n  {i}. {finding.get('title', 'Unknown')}")
                print(f"     ID: {finding.get('id', 'N/A')}")

                location = finding.get("location", {})
                file_path = location.get("file", "unknown")
                line_start = location.get("line_start", 0)
                print(f"     Location: {file_path}:{line_start}")
                print(f"     Scanner: {finding.get('scanner', 'unknown')}")

                if cwe_id := finding.get("cwe_id"):
                    print(f"     CWE: {cwe_id}")

                if description := finding.get("description"):
                    truncated = truncate_description(
                        description, MAX_DESCRIPTION_LENGTH
                    )
                    print(f"     Description: {truncated}")

    if total_critical == 0:
        print("No critical findings found across all repositories!")
    else:
        print(f"\n\nTotal critical findings: {total_critical}")

    print(f"\n{'=' * SEPARATOR_LONG}\n")


async def run_dashboard(
    repo_paths: list[Path],
    show_critical: bool = False,
    timeout: int = DEFAULT_MCP_TIMEOUT,
) -> None:
    """Run security dashboard across multiple repositories.

    Args:
        repo_paths: List of repository paths to analyze
        show_critical: If True, show detailed critical findings
        timeout: Connection timeout in seconds

    Raises:
        DashboardError: If no repositories could be queried
    """
    print(f"\nQuerying security status for {len(repo_paths)} repositories...\n")

    # Query status for all repos concurrently
    tasks = [get_repo_status(repo_path, timeout) for repo_path in repo_paths]
    repository_statuses = await asyncio.gather(*tasks)

    # Check if any succeeded
    healthy_repos = [r for r in repository_statuses if r.is_healthy()]

    if not healthy_repos:
        error_msg = (
            "Error: Could not connect to any MCP servers.\n\n"
            "Make sure each repository has:\n"
            "  1. JP Spec Kit installed\n"
            "  2. Security scan has been run at least once\n"
            "  3. MCP server is configured in .mcp.json"
        )
        raise DashboardError(error_msg)

    # Print dashboard
    print_dashboard(list(repository_statuses))

    # Show critical findings if requested
    if show_critical:
        await show_critical_findings(repo_paths, timeout)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Security Dashboard - Cross-Repo MCP Example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --repos /path/to/repo1 /path/to/repo2
  %(prog)s --repos . ../other-project --show-critical
  %(prog)s --repos . --timeout 60
        """,
    )
    parser.add_argument(
        "--repos",
        type=str,
        nargs="+",
        required=True,
        help="List of repository paths to analyze",
    )
    parser.add_argument(
        "--show-critical",
        action="store_true",
        help="Show detailed critical findings",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_MCP_TIMEOUT,
        help=f"Connection timeout in seconds (default: {DEFAULT_MCP_TIMEOUT})",
    )

    args = parser.parse_args()

    # Validate repo paths
    repo_paths: list[Path] = []
    for repo in args.repos:
        try:
            validated = validate_target_directory(repo)
            repo_paths.append(validated)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    # Run dashboard with proper error handling
    try:
        asyncio.run(run_dashboard(repo_paths, args.show_critical, args.timeout))
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        sys.exit(130)
    except DashboardError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error in dashboard")
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        print("See logs for details.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
