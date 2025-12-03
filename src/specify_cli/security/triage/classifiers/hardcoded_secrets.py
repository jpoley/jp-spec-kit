"""Hardcoded Secrets classifier (CWE-798).

Specialized classifier for hardcoded credential vulnerabilities.
Analyzes secret patterns and determines if they're real secrets.
"""

import math
import re
from collections import Counter

from specify_cli.security.models import Finding
from specify_cli.security.triage.models import Classification
from specify_cli.security.triage.classifiers.base import (
    FindingClassifier,
    ClassificationResult,
)


class HardcodedSecretsClassifier(FindingClassifier):
    """Specialized classifier for hardcoded secret vulnerabilities."""

    # Patterns that indicate dummy/test values
    DUMMY_PATTERNS = [
        r"^xxx+$",
        r"^test",
        r"^demo",
        r"^example",
        r"^placeholder",
        r"^dummy",
        r"^fake",
        r"^changeme",
        r"^password123?$",
        r"^admin$",
        r"^secret$",
        r"^\*+$",
        r"^your[-_]",
        r"^<.*>$",  # Placeholder like <YOUR_API_KEY>
        r"^\$\{.*\}$",  # Environment variable placeholder
    ]

    # High-entropy patterns that suggest real secrets
    ENTROPY_THRESHOLD = 3.5  # Bits per character

    @property
    def supported_cwes(self) -> list[str]:
        """CWEs related to hardcoded secrets."""
        return ["CWE-798", "CWE-259", "CWE-321", "CWE-522"]

    def classify(self, finding: Finding) -> ClassificationResult:
        """Classify hardcoded secret finding."""
        if self.llm is None:
            return self._heuristic_classify(finding)

        return self._ai_classify(finding)

    def _heuristic_classify(self, finding: Finding) -> ClassificationResult:
        """Heuristic-based secret classification."""
        code = finding.location.code_snippet or ""

        # Extract potential secret value
        secret_value = self._extract_secret_value(code)

        if not secret_value:
            return ClassificationResult(
                classification=Classification.NEEDS_INVESTIGATION,
                confidence=0.5,
                reasoning="Could not extract secret value from code.",
            )

        # Check for dummy patterns
        for pattern in self.DUMMY_PATTERNS:
            if re.match(pattern, secret_value.lower()):
                return ClassificationResult(
                    classification=Classification.FALSE_POSITIVE,
                    confidence=0.85,
                    reasoning=(
                        f"Secret matches dummy pattern: {pattern}. "
                        "This appears to be a placeholder or test value."
                    ),
                )

        # Check entropy
        entropy = self._calculate_entropy(secret_value)
        if entropy < self.ENTROPY_THRESHOLD:
            return ClassificationResult(
                classification=Classification.FALSE_POSITIVE,
                confidence=0.7,
                reasoning=(
                    f"Low entropy ({entropy:.2f} bits/char). Likely not a real secret."
                ),
            )

        # Check file context
        file_path = str(finding.location.file).lower()
        if any(x in file_path for x in ["test", "mock", "fixture", "example"]):
            return ClassificationResult(
                classification=Classification.FALSE_POSITIVE,
                confidence=0.8,
                reasoning="Secret found in test/example file. Likely not production.",
            )

        # High entropy in production code = likely real
        return ClassificationResult(
            classification=Classification.TRUE_POSITIVE,
            confidence=0.8,
            reasoning=(
                f"High entropy ({entropy:.2f} bits/char) secret in production code. "
                "This appears to be a real hardcoded credential."
            ),
        )

    def _extract_secret_value(self, code: str) -> str | None:
        """Extract the secret value from code snippet.

        Uses specific patterns to find secret assignment values,
        not just any quoted string.
        """
        # More specific patterns for secret assignment
        # Look for common secret variable names followed by assignment
        patterns = [
            # Matches: KEY = "value" or KEY = 'value' (with common secret names)
            r"(?i)\b(?:key|secret|token|password|pwd|pass|api[_-]?key|"
            r"access[_-]?key|auth[_-]?token|credentials?)\b\s*[=:]\s*"
            r'["\']([^"\']+)["\']',
            # Matches: "key": "value" in JSON/dict
            r'(?i)["\'](?:key|secret|token|password|pwd|pass|api[_-]?key|'
            r'access[_-]?key|auth[_-]?token|credentials?)["\']'
            r'\s*:\s*["\']([^"\']+)["\']',
            # Fallback: quoted string (less specific)
            r'["\']([^"\']{8,})["\']',  # At least 8 chars
        ]

        for pattern in patterns:
            match = re.search(pattern, code)
            if match:
                return match.group(1)

        return None

    def _calculate_entropy(self, value: str) -> float:
        """Calculate Shannon entropy of a string (bits per character)."""
        if not value:
            return 0.0

        counts = Counter(value)
        length = len(value)
        entropy = 0.0

        for count in counts.values():
            probability = count / length
            entropy -= probability * math.log2(probability)

        return entropy

    def _ai_classify(self, finding: Finding) -> ClassificationResult:
        """AI-powered secret classification."""
        context = self.get_code_context(finding, context_lines=5)

        prompt = f"""Analyze this potential hardcoded secret:

**Finding:**
- Title: {finding.title}
- CWE: CWE-798 (Hardcoded Credentials)
- File: {finding.location.file}:{finding.location.line_start}

**Code Context:**
```
{context}
```

**Secret Analysis Checklist:**
1. Is this a real secret or a placeholder/example?
2. Is this in test code, fixtures, or documentation?
3. Does the value have high entropy (looks random)?
4. Is the secret used in production code paths?
5. Could this be an environment variable default?

**Common False Positives:**
- Placeholder values: "your-api-key-here", "<SECRET>"
- Test fixtures: "test_password", "dummy_token"
- Documentation examples
- Default/fallback values that are overridden

**Classification:**
- TP: Real secret that could be exploited
- FP: Placeholder, test value, or documentation
- NI: Cannot determine if real secret

Respond in JSON format:
{{
    "classification": "TP" | "FP" | "NI",
    "confidence": 0.0-1.0,
    "reasoning": "explanation of why this is or isn't a real secret"
}}
"""
        response = self.llm.complete(prompt)
        return self._parse_llm_response(response)
