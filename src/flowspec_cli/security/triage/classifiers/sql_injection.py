"""SQL Injection classifier (CWE-89).

Specialized classifier for SQL injection vulnerabilities. Analyzes
query construction patterns and input sanitization.
"""

import re

from flowspec_cli.security.models import Finding
from flowspec_cli.security.triage.models import Classification
from flowspec_cli.security.triage.classifiers.base import (
    FindingClassifier,
    ClassificationResult,
)


class SQLInjectionClassifier(FindingClassifier):
    """Specialized classifier for SQL injection vulnerabilities."""

    @property
    def supported_cwes(self) -> list[str]:
        """CWEs related to SQL injection."""
        return ["CWE-89", "CWE-564"]

    def classify(self, finding: Finding) -> ClassificationResult:
        """Classify SQL injection finding."""
        if self.llm is None:
            return self._heuristic_classify(finding)

        return self._ai_classify(finding)

    def _heuristic_classify(self, finding: Finding) -> ClassificationResult:
        """Heuristic-based SQL injection classification."""
        code = finding.location.code_snippet or ""
        code_lower = code.lower()

        # Check for parameterized queries (likely FP)
        # Note: bare "?" is too broad - must be in SQL context
        parameterized_patterns = [
            "?, ?",  # Multiple SQL placeholders
            ", ?)",  # SQL placeholder in VALUES
            "(?, ",  # SQL placeholder in VALUES
            "= ?",  # SQL placeholder in WHERE
            "$1",
            "$2",  # PostgreSQL placeholders
            ":param",  # Named parameters
            "prepared",
        ]

        # Check execute() separately - it's context-dependent
        has_execute = "execute(" in code_lower

        for pattern in parameterized_patterns:
            if pattern in code_lower:
                return ClassificationResult(
                    classification=Classification.FALSE_POSITIVE,
                    confidence=0.7,
                    reasoning=(
                        f"Found parameterized query pattern: {pattern}. "
                        "Likely using safe query construction."
                    ),
                )

        # Check for string concatenation (likely TP)
        # Use tuples of (pattern, description) for user-friendly reasoning
        concat_patterns = [
            (r'\+\s*["\']', "+ followed by quote (possible string concatenation)"),
            (r'["\']\s*\+', "quote followed by + (possible string concatenation)"),
            (r'f["\']', "f-string (possible variable interpolation)"),
            (r"\.format\(", ".format() (possible variable interpolation)"),
            (r"%\s*\(", "% formatting (possible variable interpolation)"),
        ]

        for pattern, description in concat_patterns:
            if re.search(pattern, code):
                return ClassificationResult(
                    classification=Classification.TRUE_POSITIVE,
                    confidence=0.8,
                    reasoning=(
                        f"Found string concatenation pattern: {description}. "
                        "Likely vulnerable to SQL injection."
                    ),
                )

        # If execute() is found without concat patterns, it might be using
        # parameterized queries with a params argument
        if has_execute:
            return ClassificationResult(
                classification=Classification.NEEDS_INVESTIGATION,
                confidence=0.6,
                reasoning=(
                    "Found execute() call. Check if query uses parameterized "
                    "queries with params argument or string concatenation."
                ),
            )

        return ClassificationResult(
            classification=Classification.NEEDS_INVESTIGATION,
            confidence=0.5,
            reasoning="Could not determine query construction method.",
        )

    def _ai_classify(self, finding: Finding) -> ClassificationResult:
        """AI-powered SQL injection classification."""
        context = self.get_code_context(finding, context_lines=10)

        prompt = f"""Analyze this potential SQL injection vulnerability:

**Finding:**
- Title: {finding.title}
- CWE: CWE-89 (SQL Injection)
- File: {finding.location.file}:{finding.location.line_start}

**Code Context (10 lines before and after):**
```
{context}
```

**SQL Injection Analysis Checklist:**
1. Is the SQL query constructed using string concatenation with user input?
2. Are parameterized queries or prepared statements used?
3. Is there any input validation or sanitization before the query?
4. Could an attacker inject SQL syntax (e.g., ' OR 1=1 --)?
5. Is this ORM code that might auto-parameterize?

**Classification:**
- TP: String concatenation with user input, no sanitization
- FP: Parameterized queries, ORM, or properly sanitized input
- NI: Cannot determine from context alone

Respond in JSON format:
{{
    "classification": "TP" | "FP" | "NI",
    "confidence": 0.0-1.0,
    "reasoning": "explanation including which checklist items apply"
}}
"""
        response = self.llm.complete(prompt)
        return self._parse_llm_response(response)
