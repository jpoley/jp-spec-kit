"""AI-powered vulnerability triage engine.

This module provides the core TriageEngine that orchestrates:
1. Classification (TP/FP/NI) using specialized classifiers
2. Risk scoring using the Raptor formula
3. Finding clustering by root cause
4. Plain-English explanation generation

See ADR-006 for architectural design.
"""

import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from specify_cli.security.models import Finding
from specify_cli.security.triage.models import (
    Classification,
    ClusterType,
    Explanation,
    TriageResult,
)
from specify_cli.security.triage.risk_scorer import RiskScorer
from specify_cli.security.triage.classifiers.base import (
    FindingClassifier,
    ClassificationResult,
    LLMClient,
)
from specify_cli.security.triage.classifiers.default import DefaultClassifier
from specify_cli.security.triage.classifiers.sql_injection import (
    SQLInjectionClassifier,
)
from specify_cli.security.triage.classifiers.xss import XSSClassifier
from specify_cli.security.triage.classifiers.path_traversal import (
    PathTraversalClassifier,
)
from specify_cli.security.triage.classifiers.hardcoded_secrets import (
    HardcodedSecretsClassifier,
)
from specify_cli.security.triage.classifiers.weak_crypto import WeakCryptoClassifier

logger = logging.getLogger(__name__)


@dataclass
class TriageConfig:
    """Configuration for the triage engine."""

    min_cluster_size: int = 3  # Minimum findings to form a CWE cluster
    min_file_cluster_size: int = 2  # Minimum findings to form a file cluster
    explanation_max_length: int = 500  # Max chars for explanation sections


class TriageEngine:
    """AI-powered vulnerability triage engine.

    Orchestrates classification, risk scoring, clustering, and explanation
    generation for security findings.

    Example:
        >>> engine = TriageEngine(llm_client)
        >>> results = engine.triage(findings)
        >>> for result in results:
        ...     print(f"{result.finding_id}: {result.classification.value}")
    """

    # CWE to classifier mapping
    CWE_CLASSIFIER_MAP = {
        "CWE-89": "sql_injection",
        "CWE-564": "sql_injection",
        "CWE-79": "xss",
        "CWE-80": "xss",
        "CWE-22": "path_traversal",
        "CWE-23": "path_traversal",
        "CWE-36": "path_traversal",
        "CWE-73": "path_traversal",
        "CWE-798": "hardcoded_secrets",
        "CWE-259": "hardcoded_secrets",
        "CWE-321": "hardcoded_secrets",
        "CWE-522": "hardcoded_secrets",
        "CWE-327": "weak_crypto",
        "CWE-328": "weak_crypto",
        "CWE-326": "weak_crypto",
        "CWE-916": "weak_crypto",
    }

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        config: TriageConfig | None = None,
    ):
        """Initialize the triage engine.

        Args:
            llm_client: LLM client for AI-powered analysis. If None,
                       uses heuristic-based classification.
            config: Triage configuration options.
        """
        self.llm = llm_client
        self.config = config or TriageConfig()
        self.risk_scorer = RiskScorer()

        # Initialize classifiers
        self.classifiers: dict[str, FindingClassifier] = {
            "sql_injection": SQLInjectionClassifier(llm_client),
            "xss": XSSClassifier(llm_client),
            "path_traversal": PathTraversalClassifier(llm_client),
            "hardcoded_secrets": HardcodedSecretsClassifier(llm_client),
            "weak_crypto": WeakCryptoClassifier(llm_client),
            "default": DefaultClassifier(llm_client),
        }

    def triage(self, findings: list[Finding]) -> list[TriageResult]:
        """Triage all findings with AI assistance.

        Args:
            findings: List of findings from scanner orchestrator.

        Returns:
            List of triage results, sorted by risk score (highest first).
        """
        results = []

        for finding in findings:
            result = self._triage_single(finding)
            results.append(result)

        # Cluster findings by root cause
        results = self._cluster(results, findings)

        # Sort by risk score (highest first)
        results.sort(key=lambda r: r.risk_score, reverse=True)

        return results

    def _triage_single(self, finding: Finding) -> TriageResult:
        """Triage a single finding.

        Pipeline:
        1. Classify (TP/FP/NI)
        2. Score risk (Raptor formula)
        3. Generate explanation

        Args:
            finding: Security finding to triage.

        Returns:
            TriageResult with classification, score, and explanation.
        """
        # 1. Classify
        classification_result = self._classify(finding)

        # 2. Score risk
        risk_components = self.risk_scorer.score(finding, self.llm)

        # 3. Generate explanation
        explanation = self._generate_explanation(finding, classification_result)

        return TriageResult(
            finding_id=finding.id,
            classification=classification_result.classification,
            confidence=classification_result.confidence,
            risk_score=risk_components.risk_score,
            explanation=explanation,
            ai_reasoning=classification_result.reasoning,
            metadata={
                "impact": risk_components.impact,
                "exploitability": risk_components.exploitability,
                "detection_time": risk_components.detection_time,
            },
        )

    def _classify(self, finding: Finding) -> ClassificationResult:
        """Classify finding using appropriate specialized classifier.

        Uses Strategy Pattern: Select classifier based on CWE.
        """
        cwe_id = finding.cwe_id
        classifier_key = self.CWE_CLASSIFIER_MAP.get(cwe_id, "default")
        classifier = self.classifiers.get(classifier_key, self.classifiers["default"])

        return classifier.classify(finding)

    def _generate_explanation(
        self,
        finding: Finding,
        classification: ClassificationResult,
    ) -> Explanation:
        """Generate plain-English explanation for a finding.

        Follows the What/Why/How format:
        - What: 1-sentence description
        - Why It Matters: Security impact
        - How to Exploit: Attack scenario (for TP only)
        - How to Fix: Remediation approach
        """
        if self.llm is None:
            return self._generate_heuristic_explanation(finding, classification)

        return self._generate_ai_explanation(finding, classification)

    def _generate_heuristic_explanation(
        self,
        finding: Finding,
        classification: ClassificationResult,
    ) -> Explanation:
        """Generate explanation without AI."""
        what = finding.description or finding.title

        # Truncate if needed
        max_len = self.config.explanation_max_length
        if len(what) > max_len:
            what = what[: max_len - 3] + "..."

        why = self._get_cwe_impact(finding.cwe_id)
        how_to_exploit = None

        if classification.classification == Classification.TRUE_POSITIVE:
            how_to_exploit = self._get_cwe_exploit_guidance(finding.cwe_id)

        how_to_fix = self._get_cwe_fix_guidance(finding.cwe_id)

        return Explanation(
            what=what,
            why_it_matters=why,
            how_to_exploit=how_to_exploit,
            how_to_fix=how_to_fix,
        )

    def _generate_ai_explanation(
        self,
        finding: Finding,
        classification: ClassificationResult,
    ) -> Explanation:
        """Generate explanation using AI."""
        prompt = f"""Generate a plain-English explanation for this security finding:

**Finding:**
- Title: {finding.title}
- CWE: {finding.cwe_id or "Unknown"}
- Classification: {classification.classification.value}
- Confidence: {classification.confidence:.0%}

**Description:**
{finding.description}

**Location:**
{finding.location.file}:{finding.location.line_start}

Generate a developer-friendly explanation in JSON format:
{{
    "what": "1-sentence description of the vulnerability",
    "why_it_matters": "Security impact if exploited",
    "how_to_exploit": "Attack scenario (only if TRUE_POSITIVE, else null)",
    "how_to_fix": "Remediation approach"
}}

Keep each section under 200 characters. Use simple language.
"""
        try:
            response = self.llm.complete(prompt)

            # Parse JSON response
            response = response.strip()
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()

            data = json.loads(response)

            return Explanation(
                what=data.get("what", finding.title),
                why_it_matters=data.get("why_it_matters", "Security impact unknown"),
                how_to_exploit=data.get("how_to_exploit"),
                how_to_fix=data.get("how_to_fix", "Review and fix the vulnerability"),
            )
        except Exception:
            # Fallback to heuristic
            return self._generate_heuristic_explanation(finding, classification)

    def _get_cwe_impact(self, cwe_id: str | None) -> str:
        """Get standard impact description for a CWE."""
        impacts = {
            "CWE-89": "SQL injection can lead to data theft, modification, or deletion.",
            "CWE-79": "XSS can steal session cookies or perform actions as the user.",
            "CWE-22": "Path traversal can expose sensitive files on the server.",
            "CWE-798": "Hardcoded secrets can be extracted and used by attackers.",
            "CWE-327": "Weak cryptography can be broken, exposing protected data.",
        }
        return impacts.get(
            cwe_id or "", "This vulnerability could compromise security."
        )

    def _get_cwe_exploit_guidance(self, cwe_id: str | None) -> str:
        """Get example exploit scenario for a CWE."""
        exploits = {
            "CWE-89": "Attacker injects ' OR 1=1 -- to bypass authentication.",
            "CWE-79": "Attacker injects <script>...</script> to steal cookies.",
            "CWE-22": "Attacker uses ../../etc/passwd to read system files.",
            "CWE-798": "Attacker extracts credentials from source code.",
            "CWE-327": "Attacker uses rainbow tables to crack hashed passwords.",
        }
        return exploits.get(cwe_id or "", "Exploitation method depends on context.")

    def _get_cwe_fix_guidance(self, cwe_id: str | None) -> str:
        """Get remediation guidance for a CWE."""
        fixes = {
            "CWE-89": "Use parameterized queries or prepared statements.",
            "CWE-79": "Escape output and use Content Security Policy.",
            "CWE-22": "Validate paths against allowed directories.",
            "CWE-798": "Use environment variables or secret management.",
            "CWE-327": "Use modern algorithms (AES-256, bcrypt, Argon2).",
        }
        return fixes.get(
            cwe_id or "", "Review and apply appropriate security controls."
        )

    def _cluster(
        self,
        results: list[TriageResult],
        findings: list[Finding],
    ) -> list[TriageResult]:
        """Cluster findings by root cause for systemic fix recommendations.

        Clustering strategies:
        1. Same CWE category (e.g., all CWE-89 SQL injections)
        2. Same file/function (e.g., all issues in auth.py)
        """
        # Build finding lookup
        finding_map = {f.id: f for f in findings}

        # 1. Cluster by CWE
        by_cwe: dict[str, list[TriageResult]] = defaultdict(list)
        for result in results:
            finding = finding_map.get(result.finding_id)
            if finding:
                cwe = finding.cwe_id or "unknown"
                by_cwe[cwe].append(result)

        # Assign CWE cluster IDs
        for cwe, cluster in by_cwe.items():
            if len(cluster) >= self.config.min_cluster_size:
                cluster_id = f"CLUSTER-CWE-{cwe}"
                for result in cluster:
                    result.cluster_id = cluster_id
                    result.cluster_type = ClusterType.CWE

        # 2. Cluster by file (if not already clustered)
        by_file: dict[str, list[TriageResult]] = defaultdict(list)
        unclustered = [r for r in results if r.cluster_id is None]

        for result in unclustered:
            finding = finding_map.get(result.finding_id)
            if finding:
                file_path = str(finding.location.file)
                by_file[file_path].append(result)

        for file_path, cluster in by_file.items():
            if len(cluster) >= self.config.min_file_cluster_size:
                cluster_id = f"CLUSTER-FILE-{Path(file_path).stem}"
                for result in cluster:
                    result.cluster_id = cluster_id
                    result.cluster_type = ClusterType.FILE

        return results

    def get_classifier(self, cwe_id: str | None) -> FindingClassifier:
        """Get the appropriate classifier for a CWE.

        Args:
            cwe_id: CWE identifier (e.g., "CWE-89").

        Returns:
            Specialized classifier or default classifier.
        """
        classifier_key = self.CWE_CLASSIFIER_MAP.get(cwe_id or "", "default")
        return self.classifiers.get(classifier_key, self.classifiers["default"])
