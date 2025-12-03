"""Path Traversal classifier (CWE-22).

Specialized classifier for path traversal vulnerabilities. Analyzes
file path construction and validation patterns.
"""

from specify_cli.security.models import Finding
from specify_cli.security.triage.models import Classification
from specify_cli.security.triage.classifiers.base import (
    FindingClassifier,
    ClassificationResult,
)


class PathTraversalClassifier(FindingClassifier):
    """Specialized classifier for path traversal vulnerabilities."""

    @property
    def supported_cwes(self) -> list[str]:
        """CWEs related to path traversal."""
        return ["CWE-22", "CWE-23", "CWE-36", "CWE-73"]

    def classify(self, finding: Finding) -> ClassificationResult:
        """Classify path traversal finding."""
        if self.llm is None:
            return self._heuristic_classify(finding)

        return self._ai_classify(finding)

    def _heuristic_classify(self, finding: Finding) -> ClassificationResult:
        """Heuristic-based path traversal classification."""
        code = finding.location.code_snippet or ""
        code_lower = code.lower()

        # Check for path validation (likely FP)
        safe_patterns = [
            "realpath",
            "abspath",
            "normpath",
            "resolve()",
            ".startswith(",
            "is_relative_to",
            "secure_filename",
            "path.join",  # Often safe when combined with validation
        ]

        validation_found = False
        for pattern in safe_patterns:
            if pattern in code_lower:
                validation_found = True
                break

        # Check for dangerous patterns
        dangerous_patterns = [
            "open(",
            "read(",
            "readfile",
            "file_get_contents",
            "include(",
            "require(",
            "send_file",
            "sendfile",
        ]

        has_file_op = any(p in code_lower for p in dangerous_patterns)

        if validation_found and has_file_op:
            return ClassificationResult(
                classification=Classification.NEEDS_INVESTIGATION,
                confidence=0.6,
                reasoning=(
                    "Found file operation with some path validation. "
                    "Verify validation is applied before file access."
                ),
            )

        if validation_found:
            return ClassificationResult(
                classification=Classification.FALSE_POSITIVE,
                confidence=0.7,
                reasoning="Path validation detected. Likely safe.",
            )

        if has_file_op:
            return ClassificationResult(
                classification=Classification.TRUE_POSITIVE,
                confidence=0.7,
                reasoning=(
                    "File operation without visible path validation. "
                    "May be vulnerable to path traversal."
                ),
            )

        return ClassificationResult(
            classification=Classification.NEEDS_INVESTIGATION,
            confidence=0.5,
            reasoning="Could not determine path validation status.",
        )

    def _ai_classify(self, finding: Finding) -> ClassificationResult:
        """AI-powered path traversal classification."""
        context = self.get_code_context(finding, context_lines=10)

        prompt = f"""Analyze this potential path traversal vulnerability:

**Finding:**
- Title: {finding.title}
- CWE: CWE-22 (Path Traversal)
- File: {finding.location.file}:{finding.location.line_start}

**Code Context:**
```
{context}
```

**Path Traversal Analysis Checklist:**
1. Is user input used to construct a file path?
2. Is the path validated against a base directory?
3. Are "../" sequences filtered or blocked?
4. Is the path canonicalized (realpath, abspath) before use?
5. Could an attacker access files outside the intended directory?

**Classification:**
- TP: User input in file path without proper validation
- FP: Proper path validation, sandboxed directory, or no user input
- NI: Cannot determine from context alone

Respond in JSON format:
{{
    "classification": "TP" | "FP" | "NI",
    "confidence": 0.0-1.0,
    "reasoning": "explanation including what files could be accessed if TP"
}}
"""
        response = self.llm.complete(prompt)
        return self._parse_llm_response(response)
