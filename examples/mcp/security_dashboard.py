#!/usr/bin/env python3
"""Example: Cross-Repository Security Dashboard using MCP Server.

This example demonstrates how to aggregate security findings across
multiple repositories using the JP Spec Kit MCP server.

Use cases:
- Security team monitoring multiple projects
- Organization-wide security posture tracking
- Compliance reporting across repos
- Identifying security debt hotspots

CRITICAL ARCHITECTURE:
- Each project runs its own MCP server instance
- Dashboard aggregates data from multiple MCP servers
- NO LLM API calls are made (pure data aggregation)
- Can be extended with AI-powered insights using Claude

Usage:
    python examples/mcp/security_dashboard.py

Requirements:
    pip install mcp rich tabulate

Configuration:
    Update PROJECTS list with your repositories

Reference: docs/guides/security-mcp-guide.md
"""

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from mcp.client import Client
    from mcp.client.stdio import stdio_client, StdioServerParameters

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


@dataclass
class ProjectSecurity:
    """Security posture for a single project."""

    name: str
    path: Path
    total_findings: int
    critical: int
    high: int
    medium: int
    low: int
    posture: str
    triage_status: str
    true_positives: int = 0
    false_positives: int = 0


class SecurityDashboard:
    """Cross-repository security monitoring dashboard."""

    def __init__(self, projects: list[Path]):
        """Initialize the dashboard.

        Args:
            projects: List of project root directories to monitor.
        """
        self.projects = projects
        self.console = Console() if RICH_AVAILABLE else None

    async def generate_dashboard(self) -> list[ProjectSecurity]:
        """Generate security dashboard for all projects.

        Returns:
            List of project security status.
        """
        results = []

        for project_path in self.projects:
            try:
                status = await self._get_project_status(project_path)
                results.append(status)
            except Exception as e:
                # Handle projects where MCP server is not available
                if self.console:
                    self.console.print(
                        f"[yellow]Warning: Could not scan {project_path.name}: {e}[/yellow]"
                    )
                else:
                    print(f"Warning: Could not scan {project_path.name}: {e}")

        return results

    async def _get_project_status(self, project_path: Path) -> ProjectSecurity:
        """Get security status for a single project.

        Args:
            project_path: Path to project root.

        Returns:
            Security status for the project.
        """
        # Connect to MCP server for this project
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "specify_cli.security.mcp_server"],
            env={"PROJECT_ROOT": str(project_path)},
        )

        async with stdio_client(server_params) as (read, write):
            async with Client(read, write) as client:
                # Get security status resource
                status_response = await client.read_resource("security://status")
                status_data = json.loads(status_response.text)

                # Build ProjectSecurity object
                return ProjectSecurity(
                    name=project_path.name,
                    path=project_path,
                    total_findings=status_data.get("total_findings", 0),
                    critical=status_data.get("by_severity", {}).get("critical", 0),
                    high=status_data.get("by_severity", {}).get("high", 0),
                    medium=status_data.get("by_severity", {}).get("medium", 0),
                    low=status_data.get("by_severity", {}).get("low", 0),
                    posture=status_data.get("security_posture", "unknown"),
                    triage_status=status_data.get("triage_status", "not_run"),
                    true_positives=status_data.get("true_positives", 0),
                    false_positives=status_data.get("false_positives", 0),
                )

    def display_dashboard(self, results: list[ProjectSecurity]) -> None:
        """Display the security dashboard.

        Args:
            results: List of project security status.
        """
        if RICH_AVAILABLE:
            self._display_rich(results)
        else:
            self._display_plain(results)

    def _display_rich(self, results: list[ProjectSecurity]) -> None:
        """Display dashboard using Rich library.

        Args:
            results: List of project security status.
        """
        # Create table
        table = Table(title="Security Dashboard", show_header=True)
        table.add_column("Project", style="cyan", no_wrap=True)
        table.add_column("Posture", style="bold")
        table.add_column("Total", justify="right")
        table.add_column("Critical", justify="right", style="red")
        table.add_column("High", justify="right", style="yellow")
        table.add_column("Medium", justify="right", style="blue")
        table.add_column("Low", justify="right", style="green")
        table.add_column("Triage", style="magenta")

        # Add rows
        for project in sorted(results, key=lambda p: p.critical, reverse=True):
            # Color posture
            posture_style = {
                "critical": "[red bold]CRITICAL[/red bold]",
                "high_risk": "[yellow]HIGH RISK[/yellow]",
                "medium_risk": "[blue]MEDIUM RISK[/blue]",
                "good": "[green]GOOD[/green]",
                "unknown": "[dim]UNKNOWN[/dim]",
            }.get(project.posture, project.posture.upper())

            table.add_row(
                project.name,
                posture_style,
                str(project.total_findings),
                str(project.critical),
                str(project.high),
                str(project.medium),
                str(project.low),
                project.triage_status,
            )

        self.console.print(table)

        # Summary statistics
        total_critical = sum(p.critical for p in results)
        total_high = sum(p.high for p in results)
        total_findings = sum(p.total_findings for p in results)

        summary = Panel(
            f"[bold]Total Projects:[/bold] {len(results)}\n"
            f"[bold]Total Findings:[/bold] {total_findings}\n"
            f"[bold red]Critical:[/bold red] {total_critical}\n"
            f"[bold yellow]High:[/bold yellow] {total_high}\n"
            f"[bold]Projects at Risk:[/bold] {sum(1 for p in results if p.posture in ['critical', 'high_risk'])}",
            title="Summary",
            border_style="green",
        )
        self.console.print(summary)

    def _display_plain(self, results: list[ProjectSecurity]) -> None:
        """Display dashboard in plain text.

        Args:
            results: List of project security status.
        """
        print("\n=== Security Dashboard ===\n")
        print(
            f"{'Project':<20} | {'Posture':<12} | {'Total':>6} | {'C':>3} | {'H':>3} | {'M':>3} | {'L':>3} | {'Triage':<10}"
        )
        print("-" * 90)

        for project in sorted(results, key=lambda p: p.critical, reverse=True):
            print(
                f"{project.name:<20} | {project.posture.upper():<12} | "
                f"{project.total_findings:>6} | {project.critical:>3} | "
                f"{project.high:>3} | {project.medium:>3} | {project.low:>3} | "
                f"{project.triage_status:<10}"
            )

        # Summary
        total_critical = sum(p.critical for p in results)
        total_high = sum(p.high for p in results)
        total_findings = sum(p.total_findings for p in results)
        at_risk = sum(1 for p in results if p.posture in ["critical", "high_risk"])

        print("\n=== Summary ===")
        print(f"Total Projects: {len(results)}")
        print(f"Total Findings: {total_findings}")
        print(f"Critical: {total_critical}")
        print(f"High: {total_high}")
        print(f"Projects at Risk: {at_risk}")

    async def get_critical_findings(self) -> list[dict[str, Any]]:
        """Get all critical findings across all projects.

        Returns:
            List of critical findings with project context.
        """
        critical_findings = []

        for project_path in self.projects:
            try:
                server_params = StdioServerParameters(
                    command="python",
                    args=["-m", "specify_cli.security.mcp_server"],
                    env={"PROJECT_ROOT": str(project_path)},
                )

                async with stdio_client(server_params) as (read, write):
                    async with Client(read, write) as client:
                        # Get all findings
                        findings_response = await client.read_resource(
                            "security://findings"
                        )
                        findings = json.loads(findings_response.text)

                        # Filter for critical
                        for finding in findings:
                            if finding.get("severity") == "critical":
                                finding["project"] = project_path.name
                                critical_findings.append(finding)

            except Exception:
                continue

        return critical_findings

    def export_json(self, results: list[ProjectSecurity], output_path: Path) -> None:
        """Export dashboard data to JSON.

        Args:
            results: List of project security status.
            output_path: Path to output JSON file.
        """
        export_data = {
            "timestamp": "2025-12-04",  # Use datetime.now().isoformat() in production
            "total_projects": len(results),
            "total_findings": sum(p.total_findings for p in results),
            "critical_count": sum(p.critical for p in results),
            "high_count": sum(p.high for p in results),
            "projects": [
                {
                    "name": p.name,
                    "path": str(p.path),
                    "total_findings": p.total_findings,
                    "by_severity": {
                        "critical": p.critical,
                        "high": p.high,
                        "medium": p.medium,
                        "low": p.low,
                    },
                    "posture": p.posture,
                    "triage_status": p.triage_status,
                    "true_positives": p.true_positives,
                    "false_positives": p.false_positives,
                }
                for p in results
            ],
        }

        with output_path.open("w") as f:
            json.dump(export_data, f, indent=2)

        print(f"\n✓ Dashboard exported to {output_path}")


async def main() -> None:
    """Example usage of the Security Dashboard."""
    if not MCP_AVAILABLE:
        print("Error: mcp package not installed. Install with: pip install mcp")
        return

    # Configure projects to monitor
    # Update these paths with your actual projects
    PROJECTS = [
        Path("/home/user/projects/api-service"),
        Path("/home/user/projects/web-app"),
        Path("/home/user/projects/mobile-backend"),
        Path.cwd(),  # Current project
    ]

    # Filter to existing projects
    existing_projects = [p for p in PROJECTS if p.exists()]

    if not existing_projects:
        print("No projects found. Update PROJECTS list with valid directories.")
        return

    print(f"Monitoring {len(existing_projects)} projects...")

    # Initialize dashboard
    dashboard = SecurityDashboard(existing_projects)

    # Generate dashboard
    results = await dashboard.generate_dashboard()

    # Display dashboard
    dashboard.display_dashboard(results)

    # Export to JSON
    output_path = Path("security-dashboard.json")
    dashboard.export_json(results, output_path)

    # Optional: Get critical findings
    print("\n=== Critical Findings ===")
    critical = await dashboard.get_critical_findings()
    if critical:
        print(f"Found {len(critical)} critical vulnerabilities:")
        for finding in critical[:5]:  # Show first 5
            print(
                f"  - {finding['project']}: {finding['title']} "
                f"({finding['location']['file']}:{finding['location']['line_start']})"
            )
        if len(critical) > 5:
            print(f"  ... and {len(critical) - 5} more")
    else:
        print("  ✓ No critical vulnerabilities found!")


if __name__ == "__main__":
    asyncio.run(main())
