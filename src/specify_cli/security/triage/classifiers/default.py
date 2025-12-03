"""Default classifier for generic vulnerability types.

This classifier handles vulnerabilities that don't have a specialized
classifier. It uses generic prompts to analyze the finding.
"""

from specify_cli.security.models import Finding
from specify_cli.security.triage.models import Classification
from specify_cli.security.triage.classifiers.base import (
    FindingClassifier,
    ClassificationResult,
)


class DefaultClassifier(FindingClassifier):
    """Generic classifier for unspecialized vulnerability types."""

    @property
    def supported_cwes(self) -> list[str]:
        """Default classifier handles any CWE."""
        return ["*"]  # Wildcard - handles any

    def classify(self, finding: Finding) -> ClassificationResult:
        """Classify finding using generic analysis."""
        if self.llm is None:
            return self._heuristic_classify(finding)

        return self._ai_classify(finding)

    def _heuristic_classify(self, finding: Finding) -> ClassificationResult:
        """Heuristic-based classification when LLM is unavailable.

        Uses severity and common patterns to estimate classification.
        """
        severity = finding.severity.value.lower()

        # High/Critical severity are usually real issues
        if severity in ("critical", "high"):
            return ClassificationResult(
                classification=Classification.NEEDS_INVESTIGATION,
                confidence=0.6,
                reasoning=(
                    f"High severity ({severity}) finding requires investigation. "
                    "No AI analysis available."
                ),
            )

        # Low/Info often have high false positive rates
        if severity in ("low", "info"):
            return ClassificationResult(
                classification=Classification.NEEDS_INVESTIGATION,
                confidence=0.4,
                reasoning=(
                    f"Low severity ({severity}) finding. "
                    "May be false positive but requires verification."
                ),
            )

        # Medium severity - uncertain
        return ClassificationResult(
            classification=Classification.NEEDS_INVESTIGATION,
            confidence=0.5,
            reasoning="Medium severity finding requires human review.",
        )

    def _ai_classify(self, finding: Finding) -> ClassificationResult:
        """AI-powered classification using LLM."""
        context = self.get_code_context(finding)

        prompt = f"""Analyze this security finding and classify it:

**Finding:**
- Title: {finding.title}
- Severity: {finding.severity.value}
- CWE: {finding.cwe_id or "Unknown"}
- Description: {finding.description}

**Location:**
- File: {finding.location.file}
- Line: {finding.location.line_start}

**Code Context:**
```
{context}
```

**Classification Criteria:**
- TRUE POSITIVE (TP): Real security vulnerability that should be fixed
- FALSE POSITIVE (FP): Not a real vulnerability (scanner noise, sanitized input, test code)
- NEEDS INVESTIGATION (NI): Uncertain, requires human review

**Analysis Required:**
1. Is there actually vulnerable code at this location?
2. Is user input involved and unsanitized?
3. Could an attacker exploit this?
4. Are there mitigating factors (input validation, sandboxing)?

Respond in JSON format:
{{
    "classification": "TP" | "FP" | "NI",
    "confidence": 0.0-1.0,
    "reasoning": "explanation of your decision"
}}
"""
        response = self.llm.complete(prompt)
        return self._parse_llm_response(response)
