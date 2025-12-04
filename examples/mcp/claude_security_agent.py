#!/usr/bin/env python3
"""Example: Claude Security Agent using MCP Server.

This example demonstrates how to build an AI security agent that:
1. Runs security scans using the MCP server
2. Triages findings with AI-powered classification
3. Generates fix suggestions for vulnerabilities

CRITICAL ARCHITECTURE:
- This script is the MCP CLIENT (consumes the MCP server)
- The MCP server returns data and skill invocation instructions
- NO LLM API calls are made by the MCP server itself
- Skills (.claude/skills/*.md) are invoked by AI agents consuming this client

Usage:
    python examples/mcp/claude_security_agent.py

Requirements:
    pip install mcp anthropic
    export ANTHROPIC_API_KEY="sk-..."

Reference: docs/guides/security-mcp-guide.md
"""

import asyncio
import json
from pathlib import Path
from typing import Any

try:
    from mcp.client import Client
    from mcp.client.stdio import stdio_client, StdioServerParameters

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

try:
    from anthropic import Anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class SecurityAgent:
    """AI security agent that orchestrates MCP server + Claude for security analysis."""

    def __init__(self, project_root: Path):
        """Initialize the security agent.

        Args:
            project_root: Path to the project to analyze.
        """
        self.project_root = project_root
        self.claude_client = Anthropic() if ANTHROPIC_AVAILABLE else None

    async def run_workflow(self) -> dict[str, Any]:
        """Execute complete security workflow: scan → triage → fix.

        Returns:
            Workflow results with findings count, triage results, and fix suggestions.
        """
        # Connect to MCP server
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "specify_cli.security.mcp_server"],
            env={},
        )

        async with stdio_client(server_params) as (read, write):
            async with Client(read, write) as client:
                print("=== Security Agent Workflow ===\n")

                # Step 1: Run security scan
                print("[1/4] Running security scan...")
                scan_result = await self._run_scan(client)
                print(
                    f"  ✓ Found {scan_result['findings_count']} vulnerabilities"
                    f" ({scan_result['by_severity']['critical']} critical, "
                    f"{scan_result['by_severity']['high']} high)"
                )

                if scan_result["findings_count"] == 0:
                    print("\n✓ No vulnerabilities found!")
                    return {"status": "clean", "findings_count": 0}

                # Step 2: Get security status
                print("\n[2/4] Checking security posture...")
                status = await self._get_status(client)
                print(f"  Security Posture: {status['security_posture'].upper()}")

                # Step 3: Triage findings with AI
                print("\n[3/4] Triaging findings with AI...")
                triage_result = await self._triage_findings(client)
                print(
                    f"  ✓ Triage complete: {triage_result.get('true_positives', 0)} true positives"
                )

                # Step 4: Generate fixes for true positives
                print("\n[4/4] Generating fix suggestions...")
                fix_result = await self._generate_fixes(client)
                print(
                    f"  ✓ Generated {fix_result.get('fixes_count', 0)} fix suggestions"
                )

                # Final status
                final_status = await self._get_status(client)

                print("\n=== Workflow Complete ===")
                print(f"Final Posture: {final_status['security_posture'].upper()}")
                print(f"True Positives: {final_status.get('true_positives', 0)}")
                print(f"False Positives: {final_status.get('false_positives', 0)}")

                return {
                    "status": "complete",
                    "scan_result": scan_result,
                    "triage_result": triage_result,
                    "fix_result": fix_result,
                    "final_status": final_status,
                }

    async def _run_scan(self, client: Any) -> dict[str, Any]:
        """Run security scan via MCP server.

        Args:
            client: MCP client instance.

        Returns:
            Scan results with findings count and severity breakdown.
        """
        result = await client.call_tool(
            "security_scan",
            arguments={
                "target": ".",
                "scanners": ["semgrep"],
                "fail_on": ["critical", "high"],
            },
        )
        return result

    async def _get_status(self, client: Any) -> dict[str, Any]:
        """Get security status from MCP server.

        Args:
            client: MCP client instance.

        Returns:
            Security status with posture and statistics.
        """
        status_response = await client.read_resource("security://status")
        return json.loads(status_response.text)

    async def _triage_findings(self, client: Any) -> dict[str, Any]:
        """Triage findings using AI via MCP server skill invocation.

        This method:
        1. Gets triage instruction from MCP server
        2. Invokes the security-triage skill using Claude
        3. Returns triage results

        Args:
            client: MCP client instance.

        Returns:
            Triage results with classification counts.
        """
        # Get triage instruction from MCP server
        instruction = await client.call_tool("security_triage")

        if "error" in instruction:
            print(f"  ! Error: {instruction['error']}")
            return {"error": instruction["error"]}

        # MCP server returns skill invocation instruction (NO LLM calls made by server)
        print(f"  → MCP server suggests: {instruction['action']}")
        print(f"  → Skill to invoke: {instruction['skill']}")

        # Load findings
        findings_file = Path(instruction["input_file"])
        if not findings_file.exists():
            return {"error": f"Findings file not found: {findings_file}"}

        with findings_file.open() as f:
            findings_data = json.load(f)

        # Invoke security-triage skill using Claude
        # NOTE: In production, this would use Claude's native skill invocation
        # For this example, we simulate the skill execution
        print("  → Invoking security-triage skill with Claude...")

        # Simulate triage (in production, Claude would invoke the skill)
        triage_results = self._simulate_triage(findings_data.get("findings", []))

        # Save triage results
        output_file = Path(instruction["output_file"])
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w") as f:
            json.dump(triage_results, f, indent=2)

        # Count results
        tp_count = sum(1 for r in triage_results if r["classification"] == "TP")
        fp_count = sum(1 for r in triage_results if r["classification"] == "FP")

        return {
            "true_positives": tp_count,
            "false_positives": fp_count,
            "total": len(triage_results),
        }

    async def _generate_fixes(self, client: Any) -> dict[str, Any]:
        """Generate fix suggestions using AI via MCP server skill invocation.

        Args:
            client: MCP client instance.

        Returns:
            Fix results with count of suggested fixes.
        """
        # Get fix instruction from MCP server
        instruction = await client.call_tool("security_fix")

        if "error" in instruction:
            print(f"  ! Error: {instruction['error']}")
            return {"error": instruction["error"]}

        print(f"  → MCP server suggests: {instruction['action']}")
        print(f"  → Skill to invoke: {instruction['skill']}")

        # Simulate fix generation (in production, Claude would invoke the skill)
        # Load triage results
        triage_file = Path(instruction["input_file"])
        if not triage_file.exists():
            return {"error": f"Triage file not found: {triage_file}"}

        with triage_file.open() as f:
            triage_data = json.load(f)

        # Generate fixes for true positives
        true_positives = [r for r in triage_data if r["classification"] == "TP"]

        print(f"  → Generating fixes for {len(true_positives)} true positives...")

        # Simulate fix generation
        fixes = self._simulate_fix_generation(true_positives)

        # Save fixes
        output_file = Path(instruction["output_file"])
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open("w") as f:
            json.dump(fixes, f, indent=2)

        return {"fixes_count": len(fixes)}

    def _simulate_triage(self, findings: list[dict]) -> list[dict]:
        """Simulate triage for demonstration.

        In production, this would be done by Claude invoking the skill.

        Args:
            findings: List of findings to triage.

        Returns:
            Triage results with classifications.
        """
        results = []
        for finding in findings:
            # Simple heuristic: classify high/critical as TP, others as FP
            is_tp = finding.get("severity") in ["critical", "high"]

            results.append(
                {
                    "finding_id": finding["id"],
                    "classification": "TP" if is_tp else "FP",
                    "confidence": 0.85,
                    "risk_score": 7.5 if is_tp else 2.0,
                    "explanation": {
                        "what": f"Security issue: {finding['title']}",
                        "why_it_matters": "Could lead to security breach",
                        "how_to_exploit": "Attacker could exploit this vulnerability"
                        if is_tp
                        else "N/A",
                        "how_to_fix": "Apply secure coding practices",
                    },
                    "cluster_id": f"CLUSTER-CWE-{finding.get('cwe_id', 'UNKNOWN')}",
                    "cluster_type": "cwe",
                    "ai_reasoning": "Classified based on severity and context",
                    "metadata": {
                        "impact": 8 if is_tp else 3,
                        "exploitability": 7 if is_tp else 2,
                        "detection_time": 14,
                    },
                }
            )

        return results

    def _simulate_fix_generation(self, triage_results: list[dict]) -> list[dict]:
        """Simulate fix generation for demonstration.

        In production, this would be done by Claude invoking the skill.

        Args:
            triage_results: List of triage results (true positives).

        Returns:
            List of fix suggestions.
        """
        fixes = []
        for result in triage_results:
            fixes.append(
                {
                    "finding_id": result["finding_id"],
                    "fix_type": "code_patch",
                    "description": f"Fix for {result['finding_id']}",
                    "patch": "# Apply secure coding fix\n# (generated by AI)",
                    "confidence": 0.9,
                }
            )

        return fixes


async def main() -> None:
    """Example usage of the Security Agent."""
    if not MCP_AVAILABLE:
        print("Error: mcp package not installed. Install with: pip install mcp")
        return

    if not ANTHROPIC_AVAILABLE:
        print("Warning: anthropic package not installed. Some features disabled.")
        print("Install with: pip install anthropic")

    # Initialize agent
    project_root = Path.cwd()
    agent = SecurityAgent(project_root)

    # Run workflow
    try:
        results = await agent.run_workflow()
        print(f"\n✓ Workflow completed: {results.get('status', 'unknown')}")
    except Exception as e:
        print(f"\n✗ Workflow failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
