"""Weak Cryptography classifier (CWE-327).

Specialized classifier for weak cryptography vulnerabilities.
Analyzes cryptographic algorithm usage and key management.
"""

from specify_cli.security.models import Finding
from specify_cli.security.triage.models import Classification
from specify_cli.security.triage.classifiers.base import (
    FindingClassifier,
    ClassificationResult,
)


class WeakCryptoClassifier(FindingClassifier):
    """Specialized classifier for weak cryptography vulnerabilities."""

    # Known weak algorithms
    WEAK_ALGORITHMS = {
        "md5": "MD5 is cryptographically broken",
        "sha1": "SHA-1 has known collision attacks",
        "des": "DES uses insufficient key length (56-bit)",
        "3des": "Triple DES is deprecated",
        "rc2": "RC2 is considered weak",
        "rc4": "RC4 has known biases",
        "blowfish": "Blowfish has 64-bit block size vulnerability",
    }

    # Safe algorithms
    SAFE_ALGORITHMS = {
        "sha256",
        "sha384",
        "sha512",
        "sha3",
        "aes",
        "aes-256",
        "aes-128",
        "chacha20",
        "poly1305",
        "argon2",
        "bcrypt",
        "scrypt",
        "pbkdf2",
    }

    @property
    def supported_cwes(self) -> list[str]:
        """CWEs related to weak cryptography."""
        return ["CWE-327", "CWE-328", "CWE-326", "CWE-916"]

    def classify(self, finding: Finding) -> ClassificationResult:
        """Classify weak crypto finding."""
        if self.llm is None:
            return self._heuristic_classify(finding)

        return self._ai_classify(finding)

    def _heuristic_classify(self, finding: Finding) -> ClassificationResult:
        """Heuristic-based weak crypto classification."""
        code = finding.location.code_snippet or ""
        code_lower = code.lower()

        # Check for weak algorithms
        for algo, reason in self.WEAK_ALGORITHMS.items():
            if algo in code_lower:
                # Check context - is it for security or just checksums?
                # More precise detection: look for algorithm + context in same line
                is_checksum = self._is_checksum_context(code_lower, algo)

                if is_checksum and algo in ("md5", "sha1"):
                    return ClassificationResult(
                        classification=Classification.FALSE_POSITIVE,
                        confidence=0.75,
                        reasoning=(
                            f"{algo.upper()} used for checksums/integrity, not security. "
                            "This is an acceptable use case."
                        ),
                    )

                # Check for password/security context (definitely TP)
                security_contexts = ["password", "credential", "auth", "encrypt"]
                is_security = any(ctx in code_lower for ctx in security_contexts)

                if is_security:
                    return ClassificationResult(
                        classification=Classification.TRUE_POSITIVE,
                        confidence=0.9,
                        reasoning=(
                            f"Weak algorithm {algo.upper()} used in security context. "
                            f"{reason}."
                        ),
                    )

                return ClassificationResult(
                    classification=Classification.TRUE_POSITIVE,
                    confidence=0.85,
                    reasoning=f"Weak algorithm detected: {algo.upper()}. {reason}.",
                )

        # Check for safe algorithms (likely FP if present)
        for algo in self.SAFE_ALGORITHMS:
            if algo in code_lower:
                return ClassificationResult(
                    classification=Classification.FALSE_POSITIVE,
                    confidence=0.7,
                    reasoning=f"Safe algorithm detected: {algo}.",
                )

        return ClassificationResult(
            classification=Classification.NEEDS_INVESTIGATION,
            confidence=0.5,
            reasoning="Could not identify cryptographic algorithm in use.",
        )

    def _is_checksum_context(self, code_lower: str, algo: str) -> bool:
        """Check if algorithm is used in checksum/integrity context.

        More precise than simple substring matching:
        - Analyzes line by line
        - Skips comments
        - Looks for algorithm + context on same line
        - Excludes security contexts (password, credential, etc.)
        """
        # Checksum/integrity context patterns (standalone words)
        checksum_patterns = [
            "checksum",
            "file_hash",
            "hash_file",
            "etag",
            "integrity",
            "verify_file",
            "compare_hash",
        ]

        # Security contexts that should NOT be treated as checksum
        security_patterns = [
            "password",
            "credential",
            "auth",
            "secret",
            "token",
            "key",
        ]

        # Split into lines for more precise analysis
        for line in code_lower.splitlines():
            # Skip comment lines
            stripped = line.strip()
            if stripped.startswith(("#", "//", "*", "/*")):
                continue

            # If algorithm is on this line
            if algo in line:
                # First check for security context - if found, NOT checksum
                for sec in security_patterns:
                    if sec in line:
                        return False

                # Then check for checksum context
                for ctx in checksum_patterns:
                    if ctx in line:
                        return True

                # Check for naming patterns like md5_checksum, file_md5
                if f"file_{algo}" in line or f"{algo}_file" in line:
                    return True

        return False

    def _ai_classify(self, finding: Finding) -> ClassificationResult:
        """AI-powered weak crypto classification."""
        context = self.get_code_context(finding, context_lines=10)

        prompt = f"""Analyze this potential weak cryptography vulnerability:

**Finding:**
- Title: {finding.title}
- CWE: CWE-327 (Weak Cryptography)
- File: {finding.location.file}:{finding.location.line_start}

**Code Context:**
```
{context}
```

**Cryptography Analysis Checklist:**
1. What cryptographic algorithm is being used?
2. Is it being used for security (passwords, encryption) or just checksums/hashing?
3. Is the key/salt generation secure?
4. What is the key length?

**Known Weak Algorithms (for security purposes):**
- MD5: Collision attacks, should not be used for passwords or signatures
- SHA-1: Collision attacks demonstrated
- DES: 56-bit key is too short
- RC4: Known biases
- ECB mode: Pattern leakage

**Acceptable Uses of Weak Algorithms:**
- MD5/SHA-1 for file checksums or cache keys (non-security)
- Legacy system compatibility with migration plan
- Test/example code

**Classification:**
- TP: Weak algorithm used for security-critical operation
- FP: Weak algorithm used for non-security purpose, or strong algorithm
- NI: Cannot determine usage context

Respond in JSON format:
{{
    "classification": "TP" | "FP" | "NI",
    "confidence": 0.0-1.0,
    "reasoning": "explanation including what algorithm is used and for what purpose"
}}
"""
        response = self.llm.complete(prompt)
        return self._parse_llm_response(response)
