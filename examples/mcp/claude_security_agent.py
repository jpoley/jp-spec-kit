#!/usr/bin/env python3
"""Example: Claude agent using the security scanner MCP server.

This example demonstrates the MCP server workflow for security scanning.
It shows how to:
1. Connect to the jpspec-security MCP server
2. Run security scans
3. Get triage instructions (skill invocation pattern)
4. Get fix generation instructions (skill invocation pattern)
5. Query security status and findings

IMPORTANT: This example demonstrates the request/response flow but does NOT:
- Actually invoke Claude skills (requires Claude Desktop/API)
- Perform real triage or fix generation (separate tools)
- Make any LLM API calls

For production usage, see docs/guides/security-mcp-integration.md

Requirements:
    - JP Spec Kit installed: uv tool install . --force
    - MCP SDK installed: uv add mcp
    - Security scanners available: pip install semgrep

Usage:
    python examples/mcp/claude_security_agent.py --target ./src
    python examples/mcp/claude_security_agent.py --target . --scanners semgrep
    python examples/mcp/claude_security_agent.py --target . --preview-count 5
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from typing import TYPE_CHECKING, Any

from mcp_utils import (
    DEFAULT_FINDINGS_PREVIEW_COUNT,
    DEFAULT_MCP_TIMEOUT,
    SEPARATOR_LONG,
    SEPARATOR_WIDTH,
    MCPConnectionError,
    MCPResponseError,
    connect_to_security_mcp,
    parse_mcp_response,
    validate_finding,
    validate_scan_response,
    validate_target_directory,
)

if TYPE_CHECKING:
    from mcp import ClientSession

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SecurityWorkflowError(Exception):
    """Error during security workflow execution."""

    pass


async def _run_workflow_with_session(
    session: ClientSession,
    target: str,
    scanners: list[str] | None,
    preview_count: int,
    verbose: bool,
) -> None:
    """Internal workflow implementation using MCP session.

    Args:
        session: Initialized MCP client session
        target: Directory to scan
        scanners: List of scanners to use
        preview_count: Number of findings to preview
        verbose: Show verbose output

    Raises:
        SecurityWorkflowError: If workflow fails
    """
    # Step 1: Run security scan
    print(f"\nStep 1: Running security scan on '{target}'...")
    print(f"{'-' * SEPARATOR_WIDTH}")

    scan_args: dict[str, str | list[str]] = {"target": target}
    if scanners:
        scan_args["scanners"] = scanners

    scan_result = await session.call_tool("security_scan", arguments=scan_args)
    scan_data = parse_mcp_response(scan_result)

    if not validate_scan_response(scan_data):
        raise SecurityWorkflowError("Invalid scan response format")

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

    # Store triage_data and fix_data for later reference
    triage_data: dict[str, Any] | None = None
    fix_data: dict[str, Any] | None = None

    # Step 2: Get triage instruction
    print("\nStep 2: Getting triage instruction...")
    print(f"{'-' * SEPARATOR_WIDTH}")

    triage_result = await session.call_tool("security_triage", arguments={})
    triage_data = parse_mcp_response(triage_result)

    if "error" in triage_data:
        print(f"Error: {triage_data['error']}")
        print(f"Suggestion: {triage_data.get('suggestion', 'No suggestion available')}")
        return

    print("\nTriage instruction received:")
    print(f"  Action: {triage_data['action']}")
    print(f"  Skill: {triage_data['skill']}")
    print(f"  Input: {triage_data['input_file']}")
    print(f"  Output: {triage_data['output_file']}")
    print(f"\n  {triage_data['instruction']}")

    if verbose:
        print(f"\n[INFO] Next step: AI would invoke {triage_data['skill']}")

    # Step 3: Get fix instruction
    print("\nStep 3: Getting fix generation instruction...")
    print(f"{'-' * SEPARATOR_WIDTH}")

    fix_result = await session.call_tool("security_fix", arguments={})
    fix_data = parse_mcp_response(fix_result)

    if "error" in fix_data:
        print(f"Error: {fix_data['error']}")
        print(f"Suggestion: {fix_data.get('suggestion', 'No suggestion available')}")
        if triage_data:
            print(f"\nRun triage first by invoking {triage_data['skill']}")
        return

    print("\nFix generation instruction received:")
    print(f"  Action: {fix_data['action']}")
    print(f"  Skill: {fix_data['skill']}")
    print(f"  Input: {fix_data['input_file']}")
    print(f"  Output: {fix_data['output_file']}")
    print(f"\n  {fix_data['instruction']}")

    if fix_data.get("filter"):
        print(f"  Filter: {fix_data['filter']}")

    if verbose:
        print(f"\n[INFO] Next step: AI would invoke {fix_data['skill']}")

    # Step 4: Query security status
    print("\nStep 4: Querying security status...")
    print(f"{'-' * SEPARATOR_WIDTH}")

    status_response = await session.read_resource("security://status")
    status_data = parse_mcp_response(status_response)

    print("\nSecurity Status:")
    print(f"  Total findings: {status_data.get('total_findings', 0)}")
    print(
        f"  Security posture: {status_data.get('security_posture', 'unknown').upper()}"
    )
    print(f"  Triage status: {status_data.get('triage_status', 'unknown')}")

    if status_data.get("true_positives"):
        print(f"  True positives: {status_data['true_positives']}")
        print(f"  False positives: {status_data.get('false_positives', 0)}")

    # Step 5: Query specific findings
    print("\nStep 5: Querying all findings...")
    print(f"{'-' * SEPARATOR_WIDTH}")

    findings_response = await session.read_resource("security://findings")
    findings_data = parse_mcp_response(findings_response)

    if findings_data:
        print(f"\nShowing first {preview_count} findings (of {len(findings_data)}):\n")
        for i, finding in enumerate(findings_data[:preview_count], 1):
            try:
                validate_finding(finding)
                print(f"  {i}. {finding['title']}")
                print(f"     ID: {finding['id']}")
                print(f"     Severity: {finding['severity'].upper()}")
                location = finding["location"]
                print(f"     Location: {location['file']}:{location['line_start']}")
                print(f"     Scanner: {finding['scanner']}")
                if cwe_id := finding.get("cwe_id"):
                    print(f"     CWE: {cwe_id}")
                print()
            except ValueError as e:
                logger.warning(f"Skipping malformed finding: {e}")
                continue

    # Summary
    print(f"\n{'=' * SEPARATOR_LONG}")
    print("WORKFLOW SUMMARY")
    print(f"{'=' * SEPARATOR_LONG}")
    print(f"1. Scanned: {target}")
    print(f"2. Found: {scan_data['findings_count']} vulnerabilities")
    print(f"3. Posture: {status_data.get('security_posture', 'unknown').upper()}")
    print("\nNext steps for a real Claude agent:")
    if triage_data:
        print(f"  - Invoke {triage_data['skill']} to classify findings")
    if fix_data:
        print(f"  - Invoke {fix_data['skill']} to generate fixes")
    print("  - Review and apply fixes with human approval")


async def run_security_workflow(
    target: str,
    scanners: list[str] | None = None,
    preview_count: int = DEFAULT_FINDINGS_PREVIEW_COUNT,
    timeout: int = DEFAULT_MCP_TIMEOUT,
    verbose: bool = False,
) -> None:
    """Execute complete security workflow using MCP server.

    Args:
        target: Directory to scan (relative to project root)
        scanners: List of scanners to use (default: all available)
        preview_count: Number of findings to preview in output
        timeout: Connection timeout in seconds
        verbose: Show verbose output

    Raises:
        SecurityWorkflowError: If workflow fails
        MCPConnectionError: If MCP connection fails
        MCPResponseError: If MCP response is invalid
    """
    print("Connecting to jpspec-security MCP server...")

    async with connect_to_security_mcp(timeout=timeout) as session:
        await _run_workflow_with_session(
            session, target, scanners, preview_count, verbose
        )


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Claude Security Agent - MCP Server Example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --target ./src
  %(prog)s --target . --scanners semgrep
  %(prog)s --target . --preview-count 10 --verbose
        """,
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
    parser.add_argument(
        "--preview-count",
        type=int,
        default=DEFAULT_FINDINGS_PREVIEW_COUNT,
        help=f"Number of findings to preview (default: {DEFAULT_FINDINGS_PREVIEW_COUNT})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_MCP_TIMEOUT,
        help=f"Connection timeout in seconds (default: {DEFAULT_MCP_TIMEOUT})",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output",
    )

    args = parser.parse_args()

    # Validate target exists
    try:
        validate_target_directory(args.target)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Run workflow with proper error handling
    try:
        asyncio.run(
            run_security_workflow(
                args.target,
                args.scanners,
                args.preview_count,
                args.timeout,
                args.verbose,
            )
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        sys.exit(130)  # Standard UNIX signal exit code for SIGINT
    except MCPConnectionError as e:
        print(f"\nConnection error: {e}", file=sys.stderr)
        sys.exit(1)
    except MCPResponseError as e:
        print(f"\nResponse error: {e}", file=sys.stderr)
        sys.exit(1)
    except SecurityWorkflowError as e:
        print(f"\nWorkflow error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Log full details securely
        logger.exception("Unexpected error in security workflow")
        # Generic message to user
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        print("See logs for details.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
