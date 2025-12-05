#!/usr/bin/env python3
"""Example: Claude agent using the security scanner MCP server.

This example demonstrates how to:
1. Connect to the jpspec-security MCP server
2. Run security scans
3. Triage findings with AI (via skill invocation)
4. Generate fix suggestions (via skill invocation)

Requirements:
    - JP Spec Kit installed: uv tool install . --force
    - MCP SDK installed: uv add mcp
    - Security scanners available: pip install semgrep

Usage:
    python examples/mcp/claude_security_agent.py --target ./src
    python examples/mcp/claude_security_agent.py --target . --scanners semgrep
"""

import argparse
import asyncio
import json
import sys
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


async def run_security_workflow(target: str, scanners: list[str] | None = None) -> None:
    """Execute complete security workflow using MCP server.

    Args:
        target: Directory to scan (relative to project root)
        scanners: List of scanners to use (default: all available)
    """
    # Server parameters for jpspec-security MCP server
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "specify_cli.security.mcp_server"],
        env={},
    )

    print("Connecting to jpspec-security MCP server...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()

            print(f"\nStep 1: Running security scan on '{target}'...")
            print("-" * 60)

            # Call security_scan tool
            scan_args = {"target": target}
            if scanners:
                scan_args["scanners"] = scanners

            scan_result = await session.call_tool("security_scan", arguments=scan_args)

            # Parse scan results
            scan_data = json.loads(scan_result.content[0].text)
            print("\nScan completed:")
            print(f"  Total findings: {scan_data['findings_count']}")
            print("  By severity:")
            for severity, count in scan_data["by_severity"].items():
                if count > 0:
                    print(f"    {severity.upper()}: {count}")

            if scan_data["should_fail"]:
                print(
                    f"\n  WARNING: Scan failed due to {scan_data['fail_on']} severity findings"
                )

            print(f"\n  Findings saved to: {scan_data['findings_file']}")

            # If no findings, exit early
            if scan_data["findings_count"] == 0:
                print("\nNo vulnerabilities found. Excellent security posture!")
                return

            # Step 2: Get triage instruction
            print("\nStep 2: Getting triage instruction...")
            print("-" * 60)

            triage_result = await session.call_tool("security_triage", arguments={})
            triage_data = json.loads(triage_result.content[0].text)

            if "error" in triage_data:
                print(f"Error: {triage_data['error']}")
                print(f"Suggestion: {triage_data['suggestion']}")
                return

            print("\nTriage instruction received:")
            print(f"  Action: {triage_data['action']}")
            print(f"  Skill: {triage_data['skill']}")
            print(f"  Input: {triage_data['input_file']}")
            print(f"  Output: {triage_data['output_file']}")
            print(f"\n  {triage_data['instruction']}")

            print("\n  NOTE: In a real Claude agent, the AI would now invoke")
            print(f"        the {triage_data['skill']} skill to perform triage.")
            print("        This example demonstrates the workflow, not actual triage.")

            # Step 3: Get fix instruction
            print("\nStep 3: Getting fix generation instruction...")
            print("-" * 60)

            # For demo purposes, assume triage was completed
            # In a real scenario, the AI would have invoked the triage skill first
            fix_result = await session.call_tool("security_fix", arguments={})
            fix_data = json.loads(fix_result.content[0].text)

            if "error" in fix_data:
                print(f"Error: {fix_data['error']}")
                print(f"Suggestion: {fix_data['suggestion']}")
                print(f"\n  NOTE: Run triage first by invoking {triage_data['skill']}")
                return

            print("\nFix generation instruction received:")
            print(f"  Action: {fix_data['action']}")
            print(f"  Skill: {fix_data['skill']}")
            print(f"  Input: {fix_data['input_file']}")
            print(f"  Output: {fix_data['output_file']}")
            print(f"\n  {fix_data['instruction']}")

            if "filter" in fix_data:
                print(f"  Filter: {fix_data['filter']}")

            print("\n  NOTE: In a real Claude agent, the AI would now invoke")
            print(f"        the {fix_data['skill']} skill to generate fixes.")

            # Step 4: Query security status
            print("\nStep 4: Querying security status...")
            print("-" * 60)

            status_response = await session.read_resource("security://status")
            status_data = json.loads(status_response.contents[0].text)

            print("\nSecurity Status:")
            print(f"  Total findings: {status_data['total_findings']}")
            print(f"  Security posture: {status_data['security_posture'].upper()}")
            print(f"  Triage status: {status_data['triage_status']}")

            if status_data.get("true_positives"):
                print(f"  True positives: {status_data['true_positives']}")
                print(f"  False positives: {status_data['false_positives']}")

            # Step 5: Query specific findings (example)
            print("\nStep 5: Querying all findings...")
            print("-" * 60)

            findings_response = await session.read_resource("security://findings")
            findings_data = json.loads(findings_response.contents[0].text)

            if findings_data:
                print(f"\nShowing first 3 findings (of {len(findings_data)}):\n")
                for i, finding in enumerate(findings_data[:3], 1):
                    print(f"  {i}. {finding['title']}")
                    print(f"     ID: {finding['id']}")
                    print(f"     Severity: {finding['severity'].upper()}")
                    print(
                        f"     Location: {finding['location']['file']}:{finding['location']['line_start']}"
                    )
                    print(f"     Scanner: {finding['scanner']}")
                    if finding.get("cwe_id"):
                        print(f"     CWE: {finding['cwe_id']}")
                    print()

            # Summary
            print("\n" + "=" * 60)
            print("WORKFLOW SUMMARY")
            print("=" * 60)
            print(f"1. Scanned: {target}")
            print(f"2. Found: {scan_data['findings_count']} vulnerabilities")
            print(f"3. Posture: {status_data['security_posture'].upper()}")
            print("\nNext steps for a real Claude agent:")
            print(f"  - Invoke {triage_data['skill']} to classify findings")
            print(f"  - Invoke {fix_data['skill']} to generate fixes")
            print("  - Review and apply fixes with human approval")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Claude Security Agent - MCP Server Example"
    )
    parser.add_argument(
        "--target",
        type=str,
        default=".",
        help="Directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--scanners",
        type=str,
        nargs="+",
        help="Scanners to use (default: all available)",
    )

    args = parser.parse_args()

    # Verify target exists
    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target directory does not exist: {args.target}", file=sys.stderr)
        sys.exit(1)

    # Run workflow
    try:
        asyncio.run(run_security_workflow(args.target, args.scanners))
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
