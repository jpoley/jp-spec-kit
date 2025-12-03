"""Data models for fix generation.

This module defines the core data structures for vulnerability fixes:
- FixStatus: Success/failure status of fix generation
- Patch: Unified diff representation
- FixResult: Complete fix output for a finding
- FixPattern: Template for common vulnerability fixes
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class FixStatus(Enum):
    """Status of fix generation."""

    SUCCESS = "success"  # Fix generated successfully
    PARTIAL = "partial"  # Fix generated but may need review
    FAILED = "failed"  # Could not generate fix
    SKIPPED = "skipped"  # Finding doesn't need fix (FP)


@dataclass
class Patch:
    """Unified diff patch for a code change.

    Represents a patch that can be applied to fix a vulnerability.
    """

    file_path: Path
    original_code: str
    fixed_code: str
    unified_diff: str
    line_start: int
    line_end: int

    def to_patch_file(self) -> str:
        """Generate .patch file content."""
        header = f"--- a/{self.file_path}\n+++ b/{self.file_path}\n"
        return header + self.unified_diff

    def save_patch(self, output_path: Path) -> None:
        """Save patch to a file."""
        output_path.write_text(self.to_patch_file(), encoding="utf-8")

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "file_path": str(self.file_path),
            "original_code": self.original_code,
            "fixed_code": self.fixed_code,
            "unified_diff": self.unified_diff,
            "line_start": self.line_start,
            "line_end": self.line_end,
        }


@dataclass
class FixResult:
    """Result of fix generation for a security finding.

    Contains the generated patch, status, and explanation.
    """

    finding_id: str
    status: FixStatus
    patch: Patch | None
    explanation: str  # Why this fix works
    confidence: float  # 0.0-1.0 confidence in fix quality
    ai_reasoning: str = ""  # LLM's reasoning
    warnings: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    @property
    def is_successful(self) -> bool:
        """Returns True if fix was generated successfully."""
        return self.status in (FixStatus.SUCCESS, FixStatus.PARTIAL)

    @property
    def needs_review(self) -> bool:
        """Returns True if fix should be reviewed before applying."""
        return self.status == FixStatus.PARTIAL or self.confidence < 0.8

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "finding_id": self.finding_id,
            "status": self.status.value,
            "patch": self.patch.to_dict() if self.patch else None,
            "explanation": self.explanation,
            "confidence": self.confidence,
            "ai_reasoning": self.ai_reasoning,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


@dataclass
class FixPattern:
    """Template pattern for fixing common vulnerabilities.

    Each pattern provides guidance for fixing a specific CWE.
    """

    cwe_id: str
    name: str
    description: str
    vulnerable_pattern: str  # Regex or code pattern to match
    fix_template: str  # Template for the fix
    examples: list[dict] = field(default_factory=list)  # Before/after examples

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "cwe_id": self.cwe_id,
            "name": self.name,
            "description": self.description,
            "vulnerable_pattern": self.vulnerable_pattern,
            "fix_template": self.fix_template,
            "examples": self.examples,
        }
