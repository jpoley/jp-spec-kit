"""Risk scoring using the Raptor formula.

Formula: risk_score = (Impact × Exploitability) / Detection_Time

This module provides risk scoring for security findings based on:
- Impact: CVSS score (0-10) or AI-estimated severity
- Exploitability: AI-estimated likelihood of successful exploitation
- Detection Time: Days since vulnerable code was written (from git blame)
"""

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from flowspec_cli.security.models import Finding
from flowspec_cli.security.triage.models import RiskComponents


@dataclass
class RiskScorer:
    """Calculates risk scores using the Raptor formula.

    The Raptor formula prioritizes vulnerabilities that are:
    - High impact (if exploited)
    - Easy to exploit
    - Recently introduced (less time for detection)
    """

    def score(self, finding: Finding, llm_client=None) -> RiskComponents:
        """Calculate risk components for a finding.

        Args:
            finding: Security finding to score.
            llm_client: Optional LLM client for AI estimation.

        Returns:
            RiskComponents with impact, exploitability, and detection_time.
        """
        # Impact: Use CVSS if available, else estimate
        impact = self._get_impact(finding, llm_client)

        # Exploitability: AI estimation or heuristic
        exploitability = self._get_exploitability(finding, llm_client)

        # Detection Time: Days since code written
        detection_time = self._get_detection_time(finding)

        return RiskComponents(
            impact=impact,
            exploitability=exploitability,
            detection_time=detection_time,
        )

    def _get_impact(self, finding: Finding, llm_client=None) -> float:
        """Get impact score (0-10 scale).

        Uses CVSS base score if available, otherwise estimates based on
        severity level or AI analysis.
        """
        # Use CVSS if available
        if finding.metadata.get("cvss_score"):
            return float(finding.metadata["cvss_score"])

        # Map severity to impact
        severity_impact = {
            "critical": 9.5,
            "high": 7.5,
            "medium": 5.0,
            "low": 2.5,
            "info": 0.5,
        }

        severity = finding.severity.value.lower()
        return severity_impact.get(severity, 5.0)

    def _get_exploitability(self, finding: Finding, llm_client=None) -> float:
        """Get exploitability score (0-10 scale).

        Factors considered:
        - Is user input involved?
        - Complexity of exploitation
        - Known exploits for this CWE
        """
        # Exploitability Scoring Scale (0-10):
        # 9.0-10.0: Trivial to exploit, well-documented attack patterns, automated tools available
        # 8.0-8.9: Easy to exploit with standard tools, well-known techniques
        # 7.0-7.9: Moderate complexity, requires some expertise or specific conditions
        # 6.0-6.9: Complex exploitation, specific configuration or multi-step process
        # Below 6.0: Difficult to exploit, requires advanced skills or rare conditions
        #
        # CWE-based exploitability heuristics
        high_exploit_cwes = {
            "CWE-78": 9.0,  # OS Command Injection - trivial with shell metacharacters
            "CWE-798": 9.0,  # Hardcoded Credentials - direct access, no exploitation needed
            "CWE-89": 8.5,  # SQL Injection - well-known patterns, common tools (sqlmap)
            "CWE-94": 8.5,  # Code Injection - similar to command injection
            "CWE-79": 8.0,  # XSS - straightforward exploitation, many payloads available
            "CWE-502": 7.5,  # Deserialization - requires payload crafting, language-specific
            "CWE-22": 7.0,  # Path Traversal - needs understanding of file structure
            "CWE-918": 6.5,  # SSRF - requires network access, specific target knowledge
        }

        cwe_id = finding.cwe_id
        if cwe_id and cwe_id in high_exploit_cwes:
            return high_exploit_cwes[cwe_id]

        # Default based on severity
        severity_exploit = {
            "critical": 8.0,
            "high": 6.5,
            "medium": 4.5,
            "low": 2.5,
            "info": 1.0,
        }

        severity = finding.severity.value.lower()
        return severity_exploit.get(severity, 5.0)

    def _get_detection_time(self, finding: Finding) -> int:
        """Get days since vulnerable code was written using git blame.

        Returns:
            Days since last modification (1-365+), or 30 as default.
        """
        file_path = finding.location.file
        line_start = finding.location.line_start

        if not file_path or not line_start:
            return 30  # Default

        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return 30

            # Use absolute path and find git root
            abs_path = file_path_obj.resolve()

            # Find git repository root by looking for .git directory
            # Pass abs_path directly - _find_git_root handles files vs directories
            git_root = self._find_git_root(abs_path)
            if not git_root:
                return 30

            # Get path relative to git root for git blame
            try:
                rel_path = abs_path.relative_to(git_root)
            except ValueError:
                # File is not under git root
                return 30

            result = subprocess.run(
                [
                    "git",
                    "blame",
                    "-L",
                    f"{line_start},{line_start}",
                    "--porcelain",
                    str(rel_path),
                ],
                capture_output=True,
                text=True,
                cwd=str(git_root),
                timeout=5,
            )

            if result.returncode != 0:
                return 30

            # Parse git blame output for committer-time
            for line in result.stdout.split("\n"):
                if line.startswith("committer-time"):
                    parts = line.split()
                    if len(parts) >= 2:
                        timestamp = int(parts[1])
                        commit_date = datetime.fromtimestamp(timestamp)
                        age = (datetime.now() - commit_date).days
                        return max(age, 1)  # At least 1 day

        except (subprocess.TimeoutExpired, ValueError, OSError):
            pass  # git blame failed

        return 30  # Default: 30 days if git unavailable

    def _find_git_root(self, start_path: Path) -> Path | None:
        """Find the git repository root by traversing up the directory tree.

        Handles both files and directories as input. Checks start_path's
        directory first (if file) or start_path itself (if directory).
        """
        # If start_path is a file, start from its parent directory
        current = start_path.parent if start_path.is_file() else start_path

        # Check current directory first, then traverse up
        while True:
            if (current / ".git").exists():
                return current
            parent = current.parent
            if parent == current:
                # Reached filesystem root without finding .git
                return None
            current = parent


def calculate_risk_score(
    impact: float, exploitability: float, detection_time: int
) -> float:
    """Calculate risk score using Raptor formula.

    Formula: (Impact × Exploitability) / Detection_Time

    Args:
        impact: Severity impact (0-10)
        exploitability: Likelihood of exploit (0-10)
        detection_time: Days since code written (1+)

    Returns:
        Risk score (higher = more urgent)
    """
    return round((impact * exploitability) / max(detection_time, 1), 2)
