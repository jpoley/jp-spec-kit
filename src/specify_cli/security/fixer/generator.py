"""AI-powered fix generator for security vulnerabilities.

This module generates code patches to fix security findings.
It uses LLM for intelligent fix generation and pattern library
for common vulnerability fixes.
"""

import difflib
import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from specify_cli.security.models import Finding
from specify_cli.security.fixer.models import (
    FixResult,
    FixStatus,
    Patch,
)
from specify_cli.security.fixer.patterns import (
    FixPatternLibrary,
    DEFAULT_PATTERN_LIBRARY,
)


class LLMClient(Protocol):
    """Protocol for LLM client implementations."""

    def complete(self, prompt: str) -> str:
        """Send prompt to LLM and return response."""
        ...


@dataclass
class FixGeneratorConfig:
    """Configuration for fix generation."""

    context_lines: int = 10  # Lines of context around vulnerability
    validate_syntax: bool = True  # Validate generated code syntax


class FixGenerator:
    """AI-powered vulnerability fix generator.

    Generates code patches to fix security findings using:
    1. Pattern library for common fixes
    2. LLM for intelligent fix generation
    3. Syntax validation for generated code

    Example:
        >>> generator = FixGenerator(llm_client)
        >>> result = generator.generate_fix(finding)
        >>> if result.is_successful:
        ...     print(result.patch.unified_diff)
    """

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        pattern_library: FixPatternLibrary | None = None,
        config: FixGeneratorConfig | None = None,
    ):
        """Initialize fix generator.

        Args:
            llm_client: LLM client for AI-powered fix generation.
            pattern_library: Library of fix patterns for common vulnerabilities.
            config: Generator configuration options.
        """
        self.llm = llm_client
        self.patterns = pattern_library or DEFAULT_PATTERN_LIBRARY
        self.config = config or FixGeneratorConfig()

    def generate_fix(self, finding: Finding) -> FixResult:
        """Generate a fix for a security finding.

        Args:
            finding: Security finding to fix.

        Returns:
            FixResult with patch and status.
        """
        # Get code context
        original_code = self._get_code_context(finding)
        if not original_code:
            return FixResult(
                finding_id=finding.id,
                status=FixStatus.FAILED,
                patch=None,
                explanation="Could not read source file",
                confidence=0.0,
            )

        # Try LLM-based fix first, fall back to pattern-based
        if self.llm:
            result = self._generate_ai_fix(finding, original_code)
            if result.is_successful:
                return result

        # Fall back to pattern-based fix
        return self._generate_pattern_fix(finding, original_code)

    def generate_fixes(self, findings: list[Finding]) -> list[FixResult]:
        """Generate fixes for multiple findings.

        Args:
            findings: List of security findings.

        Returns:
            List of FixResults.
        """
        return [self.generate_fix(finding) for finding in findings]

    def _get_code_context(self, finding: Finding) -> str | None:
        """Get code context around the vulnerability."""
        file_path = Path(finding.location.file)
        if not file_path.exists():
            return None

        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            start = max(0, finding.location.line_start - self.config.context_lines - 1)
            end = min(len(lines), finding.location.line_end + self.config.context_lines)

            return "".join(lines[start:end])
        except OSError:
            return None

    def _generate_ai_fix(self, finding: Finding, original_code: str) -> FixResult:
        """Generate fix using LLM."""
        pattern = self.patterns.get_pattern(finding.cwe_id or "")
        pattern_guidance = ""
        if pattern:
            pattern_guidance = f"""
**Fix Pattern Guidance:**
{pattern.description}

{pattern.fix_template}

**Examples:**
"""
            for example in pattern.examples[:2]:
                pattern_guidance += f"""
Before: {example["before"]}
After:  {example["after"]}
"""

        prompt = f"""Generate a security fix for this vulnerability.

**Vulnerability:**
- Type: {finding.title}
- CWE: {finding.cwe_id or "Unknown"}
- File: {finding.location.file}
- Line: {finding.location.line_start}
- Description: {finding.description}

**Original Code:**
```
{original_code}
```

{pattern_guidance}

**Requirements:**
1. Generate the FIXED code that replaces the vulnerable code
2. Preserve the original code structure and style
3. Only change what's necessary to fix the vulnerability
4. Include any necessary imports

Respond in JSON format:
{{
    "fixed_code": "the complete fixed code snippet",
    "explanation": "why this fix works",
    "confidence": 0.0-1.0,
    "warnings": ["any warnings about the fix"]
}}
"""
        try:
            response = self.llm.complete(prompt)
            return self._parse_ai_response(finding, original_code, response)
        except Exception as e:
            return FixResult(
                finding_id=finding.id,
                status=FixStatus.FAILED,
                patch=None,
                explanation=f"LLM error: {e}",
                confidence=0.0,
            )

    def _parse_ai_response(
        self, finding: Finding, original_code: str, response: str
    ) -> FixResult:
        """Parse LLM response into FixResult."""
        try:
            # Extract JSON from response
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
            fixed_code = data.get("fixed_code", "")
            explanation = data.get("explanation", "")
            confidence = float(data.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))  # Clamp to [0.0, 1.0]
            warnings = data.get("warnings", [])

            if not fixed_code:
                return FixResult(
                    finding_id=finding.id,
                    status=FixStatus.FAILED,
                    patch=None,
                    explanation="No fixed code generated",
                    confidence=0.0,
                )

            # Generate unified diff
            unified_diff = self._generate_diff(original_code, fixed_code)

            # Validate syntax if enabled
            if self.config.validate_syntax:
                is_valid, syntax_error = self._validate_syntax(
                    fixed_code, str(finding.location.file)
                )
                if not is_valid:
                    warnings.append(f"Syntax validation warning: {syntax_error}")
                    confidence *= 0.7  # Reduce confidence
                    confidence = max(0.0, min(1.0, confidence))

            patch = Patch(
                file_path=Path(finding.location.file),
                original_code=original_code,
                fixed_code=fixed_code,
                unified_diff=unified_diff,
                line_start=finding.location.line_start,
                line_end=finding.location.line_end,
            )

            status = FixStatus.SUCCESS if confidence >= 0.7 else FixStatus.PARTIAL

            return FixResult(
                finding_id=finding.id,
                status=status,
                patch=patch,
                explanation=explanation,
                confidence=confidence,
                warnings=warnings,
                ai_reasoning=response,
            )

        except (json.JSONDecodeError, ValueError) as e:
            return FixResult(
                finding_id=finding.id,
                status=FixStatus.FAILED,
                patch=None,
                explanation=f"Failed to parse AI response: {e}",
                confidence=0.0,
            )

    def _generate_pattern_fix(self, finding: Finding, original_code: str) -> FixResult:
        """Generate fix using pattern library."""
        pattern = self.patterns.get_pattern(finding.cwe_id or "")

        if not pattern:
            return FixResult(
                finding_id=finding.id,
                status=FixStatus.FAILED,
                patch=None,
                explanation=f"No fix pattern available for {finding.cwe_id}",
                confidence=0.0,
            )

        # Find matching example
        for example in pattern.examples:
            if example["before"] in original_code:
                fixed_code = original_code.replace(
                    example["before"], example["after"], 1
                )

                unified_diff = self._generate_diff(original_code, fixed_code)

                patch = Patch(
                    file_path=Path(finding.location.file),
                    original_code=original_code,
                    fixed_code=fixed_code,
                    unified_diff=unified_diff,
                    line_start=finding.location.line_start,
                    line_end=finding.location.line_end,
                )

                return FixResult(
                    finding_id=finding.id,
                    status=FixStatus.PARTIAL,
                    patch=patch,
                    explanation=pattern.description,
                    confidence=0.6,
                    warnings=["Pattern-based fix - manual review recommended"],
                )

        # No exact match, provide guidance only
        return FixResult(
            finding_id=finding.id,
            status=FixStatus.PARTIAL,
            patch=None,
            explanation=f"Guidance: {pattern.description}\n\n{pattern.fix_template}",
            confidence=0.3,
            warnings=["No exact pattern match - manual fix required"],
        )

    def _generate_diff(self, original: str, fixed: str) -> str:
        """Generate unified diff between original and fixed code."""
        original_lines = original.splitlines(keepends=True)
        fixed_lines = fixed.splitlines(keepends=True)

        diff = difflib.unified_diff(
            original_lines,
            fixed_lines,
            fromfile="original",
            tofile="fixed",
            lineterm="",
        )

        return "".join(diff)

    def _validate_syntax(self, code: str, file_path: str) -> tuple[bool, str]:
        """Validate syntax of generated code.

        Returns:
            Tuple of (is_valid, error_message).
        """
        # Detect language from file extension
        ext = Path(file_path).suffix.lower()

        if ext == ".py":
            return self._validate_python_syntax(code)
        elif ext in (".js", ".ts", ".jsx", ".tsx"):
            return self._validate_js_syntax(code)
        else:
            # Skip validation for unknown languages
            return True, ""

    def _validate_python_syntax(self, code: str) -> tuple[bool, str]:
        """Validate Python syntax."""
        try:
            compile(code, "<string>", "exec")
            return True, ""
        except SyntaxError as e:
            return False, str(e)

    def _validate_js_syntax(self, code: str) -> tuple[bool, str]:
        """Validate JavaScript syntax using Node.js."""
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".js", delete=False, encoding="utf-8"
            ) as f:
                f.write(code)
                temp_path = f.name

            try:
                result = subprocess.run(
                    ["node", "--check", temp_path],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.returncode == 0:
                    return True, ""
                return False, result.stderr
            finally:
                Path(temp_path).unlink(missing_ok=True)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Node.js not available, skip validation
            return True, ""
