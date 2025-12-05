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
    python examples/mcp/security_dashboard.py --repos . ../other-project
"""

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print(
        "Error: mcp package not installed. Install with: uv add mcp",
        file=sys.stderr,
    )
    sys.exit(1)


@dataclass
class RepositoryStatus:
    """Security status for a single repository."""

    name: str
    path: str
    total_findings: int
    critical: int
    high: int
    medium: int
    low: int
    info: int
    posture: str
    triage_status: str
    true_positives: int
    false_positives: int


async def get_repo_status(repo_path: Path) -> RepositoryStatus | None:
    """Query security status for a single repository.

    Args:
        repo_path: Path to repository

    Returns:
        RepositoryStatus or None if MCP server unavailable
    """
    # Server parameters for jpspec-security MCP server
    # Note: We need to run the server in the context of each repo
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "specify_cli.security.mcp_server"],
        env={"PROJECT_ROOT": str(repo_path.absolute())},
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()

                # Query security status
                status_response = await session.read_resource("security://status")
                status_data = json.loads(status_response.contents[0].text)

                return RepositoryStatus(
                    name=repo_path.name,
                    path=str(repo_path),
                    total_findings=status_data.get("total_findings", 0),
                    critical=status_data.get("by_severity", {}).get("critical", 0),
                    high=status_data.get("by_severity", {}).get("high", 0),
                    medium=status_data.get("by_severity", {}).get("medium", 0),
                    low=status_data.get("by_severity", {}).get("low", 0),
                    info=status_data.get("by_severity", {}).get("info", 0),
                    posture=status_data.get("security_posture", "unknown"),
                    triage_status=status_data.get("triage_status", "not_run"),
                    true_positives=status_data.get("true_positives", 0),
                    false_positives=status_data.get("false_positives", 0),
                )

    except Exception as e:
        print(f"Warning: Could not connect to MCP server for {repo_path}: {e}")
        return None


async def query_specific_findings(
    repo_path: Path, severity_filter: str | None = None
) -> list[dict]:
    """Query specific findings from a repository.

    Args:
        repo_path: Path to repository
        severity_filter: Optional severity to filter by (e.g., "critical")

    Returns:
        List of findings matching filter
    """
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "specify_cli.security.mcp_server"],
        env={"PROJECT_ROOT": str(repo_path.absolute())},
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # Query all findings
                findings_response = await session.read_resource("security://findings")
                findings_data = json.loads(findings_response.contents[0].text)

                # Apply client-side filtering (MCP server doesn't support server-side filtering)
                if severity_filter:
                    findings_data = [
                        f for f in findings_data if f.get("severity") == severity_filter
                    ]

                return findings_data

    except Exception as e:
        print(f"Warning: Could not query findings from {repo_path}: {e}")
        return []


def print_dashboard(repos_status: list[RepositoryStatus]) -> None:
    """Print security dashboard to console.

    Args:
        repos_status: List of repository status objects
    """
    print("\n" + "=" * 100)
    print(" " * 35 + "SECURITY DASHBOARD")
    print("=" * 100 + "\n")

    # Header
    print(
        f"{'Repository':<25} | {'Posture':<12} | {'Total':<6} | {'C':<3} | {'H':<3} | {'M':<3} | {'L':<3} | {'Triage':<12}"
    )
    print("-" * 100)

    # Rows
    for repo in repos_status:
        posture_color = {
            "critical": "CRITICAL",
            "high_risk": "HIGH RISK",
            "medium_risk": "MEDIUM",
            "good": "GOOD",
            "unknown": "UNKNOWN",
        }

        posture_display = posture_color.get(repo.posture, repo.posture).upper()

        triage_display = (
            f"{repo.true_positives}TP/{repo.false_positives}FP"
            if repo.triage_status == "completed"
            else repo.triage_status.upper()
        )

        print(
            f"{repo.name:<25} | {posture_display:<12} | {repo.total_findings:<6} | "
            f"{repo.critical:<3} | {repo.high:<3} | {repo.medium:<3} | {repo.low:<3} | "
            f"{triage_display:<12}"
        )

    print("-" * 100)

    # Summary statistics
    total_repos = len(repos_status)
    total_findings = sum(r.total_findings for r in repos_status)
    total_critical = sum(r.critical for r in repos_status)
    total_high = sum(r.high for r in repos_status)

    critical_repos = sum(1 for r in repos_status if r.posture == "critical")
    high_risk_repos = sum(1 for r in repos_status if r.posture == "high_risk")
    good_repos = sum(1 for r in repos_status if r.posture == "good")

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

    print("\n" + "=" * 100 + "\n")


async def show_critical_findings(repos: list[Path]) -> None:
    """Show all critical findings across repositories.

    Args:
        repos: List of repository paths
    """
    print("\n" + "=" * 100)
    print(" " * 35 + "CRITICAL FINDINGS")
    print("=" * 100 + "\n")

    total_critical = 0

    for repo_path in repos:
        critical_findings = await query_specific_findings(repo_path, "critical")

        if critical_findings:
            print(f"\n{repo_path.name}:")
            print("-" * 80)

            for i, finding in enumerate(critical_findings, 1):
                total_critical += 1
                print(f"\n  {i}. {finding['title']}")
                print(f"     ID: {finding['id']}")
                print(
                    f"     Location: {finding['location']['file']}:{finding['location']['line_start']}"
                )
                print(f"     Scanner: {finding['scanner']}")
                if finding.get("cwe_id"):
                    print(f"     CWE: {finding['cwe_id']}")
                if finding.get("description"):
                    desc = finding["description"][:100]
                    print(f"     Description: {desc}...")

    if total_critical == 0:
        print("No critical findings found across all repositories!")
    else:
        print(f"\n\nTotal critical findings: {total_critical}")

    print("\n" + "=" * 100 + "\n")


async def run_dashboard(repo_paths: list[Path], show_critical: bool = False) -> None:
    """Run security dashboard across multiple repositories.

    Args:
        repo_paths: List of repository paths to analyze
        show_critical: If True, show detailed critical findings
    """
    print(f"\nQuerying security status for {len(repo_paths)} repositories...\n")

    # Query status for all repos concurrently
    tasks = [get_repo_status(repo_path) for repo_path in repo_paths]
    results = await asyncio.gather(*tasks)

    # Filter out None results (failed connections)
    repos_status = [r for r in results if r is not None]

    if not repos_status:
        print("Error: Could not connect to any MCP servers.", file=sys.stderr)
        print(
            "\nMake sure each repository has:",
            file=sys.stderr,
        )
        print("  1. JP Spec Kit installed", file=sys.stderr)
        print("  2. Security scan has been run at least once", file=sys.stderr)
        print("  3. MCP server is configured in .mcp.json", file=sys.stderr)
        sys.exit(1)

    # Print dashboard
    print_dashboard(repos_status)

    # Show critical findings if requested
    if show_critical:
        await show_critical_findings(repo_paths)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Security Dashboard - Cross-Repo MCP Example"
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

    args = parser.parse_args()

    # Validate repo paths
    repo_paths = []
    for repo in args.repos:
        repo_path = Path(repo).resolve()
        if not repo_path.exists():
            print(f"Error: Repository does not exist: {repo}", file=sys.stderr)
            sys.exit(1)
        if not repo_path.is_dir():
            print(f"Error: Not a directory: {repo}", file=sys.stderr)
            sys.exit(1)
        repo_paths.append(repo_path)

    # Run dashboard
    try:
        asyncio.run(run_dashboard(repo_paths, args.show_critical))
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
