"""Cross-Site Scripting (XSS) classifier (CWE-79).

Specialized classifier for XSS vulnerabilities. Analyzes output encoding
and input sanitization patterns.
"""

from specify_cli.security.models import Finding
from specify_cli.security.triage.models import Classification
from specify_cli.security.triage.classifiers.base import (
    FindingClassifier,
    ClassificationResult,
)


class XSSClassifier(FindingClassifier):
    """Specialized classifier for XSS vulnerabilities."""

    @property
    def supported_cwes(self) -> list[str]:
        """CWEs related to XSS."""
        return ["CWE-79", "CWE-80"]

    def classify(self, finding: Finding) -> ClassificationResult:
        """Classify XSS finding."""
        if self.llm is None:
            return self._heuristic_classify(finding)

        return self._ai_classify(finding)

    def _heuristic_classify(self, finding: Finding) -> ClassificationResult:
        """Heuristic-based XSS classification."""
        code = finding.location.code_snippet or ""
        code_lower = code.lower()

        # Check for encoding/escaping (likely FP)
        safe_patterns = [
            "escape(",
            "htmlescape",
            "html.escape",
            "sanitize",
            "encode(",
            "encodeuri",
            "textcontent",  # Safe DOM assignment
            "innertext",
            "createtextnode",
        ]

        for pattern in safe_patterns:
            if pattern in code_lower:
                return ClassificationResult(
                    classification=Classification.FALSE_POSITIVE,
                    confidence=0.75,
                    reasoning=(
                        f"Found output encoding pattern: {pattern}. "
                        "Input appears to be properly escaped."
                    ),
                )

        # Check for dangerous sinks (likely TP)
        dangerous_patterns = [
            "innerhtml",
            "outerhtml",
            "document.write",
            "eval(",
            "v-html",  # Vue unescaped
            "dangerouslysetinnerhtml",  # React
            "[innerhtml]",  # Angular
        ]

        for pattern in dangerous_patterns:
            if pattern in code_lower:
                return ClassificationResult(
                    classification=Classification.TRUE_POSITIVE,
                    confidence=0.8,
                    reasoning=(
                        f"Found dangerous sink: {pattern}. "
                        "This pattern is vulnerable to XSS if input is not sanitized."
                    ),
                )

        return ClassificationResult(
            classification=Classification.NEEDS_INVESTIGATION,
            confidence=0.5,
            reasoning="Could not determine if output is properly encoded.",
        )

    def _ai_classify(self, finding: Finding) -> ClassificationResult:
        """AI-powered XSS classification."""
        context = self.get_code_context(finding, context_lines=10)

        prompt = f"""Analyze this potential Cross-Site Scripting (XSS) vulnerability:

**Finding:**
- Title: {finding.title}
- CWE: CWE-79 (XSS)
- File: {finding.location.file}:{finding.location.line_start}

**Code Context:**
```
{context}
```

**XSS Analysis Checklist:**
1. Is user input being rendered in HTML without encoding?
2. Are dangerous sinks used (innerHTML, document.write, eval)?
3. Is framework-provided escaping bypassed (dangerouslySetInnerHTML, v-html)?
4. Is there input validation or output encoding present?
5. Is this server-rendered HTML or client-side DOM manipulation?

**Classification:**
- TP: User input rendered in HTML without proper encoding
- FP: Proper output encoding, Content Security Policy, or no user input
- NI: Cannot determine from context alone

Respond in JSON format:
{{
    "classification": "TP" | "FP" | "NI",
    "confidence": 0.0-1.0,
    "reasoning": "explanation including attack vector if TP"
}}
"""
        response = self.llm.complete(prompt)
        return self._parse_llm_response(response)
