"""PRD (Product Requirements Document) requirement gate validator.

This module implements validation for PRD artifacts before workflow
transitions to the "Specified" state.

PRD Format: Standard product requirements document with required sections:
- Executive Summary
- Problem Statement
- User Stories
- Functional Requirements
- Non-Functional Requirements
- Success Metrics
- All Needed Context (includes Examples, Gotchas, External Systems)

Example:
    >>> from flowspec_cli.workflow.prd_validator import PRDValidator
    >>> validator = PRDValidator()
    >>> result = validator.validate_prd(Path("./docs/prd/auth.md"))
    >>> if result.is_valid:
    ...     print("PRD is valid")
    ... else:
    ...     for error in result.errors:
    ...         print(f"Error: {error}")
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Required sections in a PRD (case-insensitive matching)
REQUIRED_PRD_SECTIONS = [
    "executive summary",
    "problem statement",
    "user stories",
    "functional requirements",
    "non-functional requirements",
    "success metrics",
    "all needed context",  # Includes Examples, Gotchas, External Systems
]

# Optional but recommended sections
RECOMMENDED_PRD_SECTIONS = [
    "dependencies",
    "risks and mitigations",
    "out of scope",
]

# PRD filename pattern: {feature-slug}.md
PRD_FILENAME_PATTERN = re.compile(r"^[\w-]+\.md$")

# User story pattern: As a [user], I want [goal] so that [benefit]
USER_STORY_PATTERN = re.compile(
    r"(?:US\d+:?\s*)?[Aa]s (?:a|an) .+?,\s*I want .+?\s*(?:so that|in order to) .+",
    re.IGNORECASE,
)

# Acceptance criterion pattern: AC# or - [ ]
AC_PATTERN = re.compile(r"(?:AC\d+:?|[-*]\s*\[[ x]\])\s*.+", re.IGNORECASE)

# Example reference pattern: table row with examples/ path
# Matches rows like: | Example Name | `examples/path` | Description |
# Excludes placeholder rows with curly braces like: | {Example name} | examples/{path} |
EXAMPLE_REFERENCE_PATTERN = re.compile(
    r"^\s*\|\s*[^|]+\s*\|\s*`?examples/[^|`{}]+`?\s*\|\s*[^|]+\s*\|",
    re.MULTILINE,
)


@dataclass
class PRDValidationResult:
    """Result of PRD validation.

    Attributes:
        is_valid: Whether the PRD passes validation.
        errors: List of validation errors (blocking).
        warnings: List of validation warnings (non-blocking).
        prd_path: Path to the validated PRD file.
        feature_name: Extracted feature name from filename.
        sections_found: List of sections found in the PRD.
        user_story_count: Number of user stories found.
        ac_count: Number of acceptance criteria found.
        example_count: Number of example references found.
    """

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    prd_path: Path | None = None
    feature_name: str | None = None
    sections_found: list[str] = field(default_factory=list)
    user_story_count: int = 0
    ac_count: int = 0
    example_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "prd_path": str(self.prd_path) if self.prd_path else None,
            "feature_name": self.feature_name,
            "sections_found": self.sections_found,
            "user_story_count": self.user_story_count,
            "ac_count": self.ac_count,
            "example_count": self.example_count,
        }


class PRDValidator:
    """Validator for Product Requirements Documents.

    Validates PRD files for:
    1. Correct filename format ({feature-slug}.md)
    2. Required sections present
    3. At least one user story with acceptance criteria
    4. Non-empty required sections

    Example:
        >>> validator = PRDValidator()
        >>> result = validator.validate_prd(Path("./docs/prd/auth.md"))
        >>> print(f"Valid: {result.is_valid}")
    """

    def __init__(self, strict: bool = False) -> None:
        """Initialize PRD validator.

        Args:
            strict: If True, treat warnings as errors.
        """
        self.strict = strict

    def validate_prd(self, prd_path: Path) -> PRDValidationResult:
        """Validate a single PRD file.

        Args:
            prd_path: Path to the PRD file.

        Returns:
            PRDValidationResult with validation details.
        """
        errors: list[str] = []
        warnings: list[str] = []
        sections_found: list[str] = []
        feature_name: str | None = None
        user_story_count: int = 0
        ac_count: int = 0
        example_count: int = 0

        # Check file exists
        if not prd_path.exists():
            return PRDValidationResult(
                is_valid=False,
                errors=[f"PRD file not found: {prd_path}"],
                prd_path=prd_path,
            )

        # Validate filename format
        filename_match = PRD_FILENAME_PATTERN.match(prd_path.name)
        if not filename_match:
            errors.append(
                f"Invalid PRD filename format: '{prd_path.name}'. "
                "Expected: {feature-slug}.md (e.g., user-authentication.md)"
            )
        else:
            feature_name = prd_path.stem.replace("-", " ").replace("_", " ").title()

        # Read and parse PRD content
        try:
            content = prd_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            return PRDValidationResult(
                is_valid=False,
                errors=[f"Failed to read PRD file: {e}"],
                prd_path=prd_path,
            )

        # Find sections (## headers)
        sections_found = self._find_sections(content)
        sections_lower = [s.lower() for s in sections_found]

        # Check required sections
        for required in REQUIRED_PRD_SECTIONS:
            if required.lower() not in sections_lower:
                errors.append(f"Missing required section: '## {required.title()}'")

        # Check recommended sections
        for recommended in RECOMMENDED_PRD_SECTIONS:
            if recommended.lower() not in sections_lower:
                warnings.append(
                    f"Recommended section missing: '## {recommended.title()}'"
                )

        # Count user stories
        user_story_count = len(USER_STORY_PATTERN.findall(content))
        if user_story_count == 0:
            errors.append(
                "No user stories found. Expected format: "
                "'As a [user], I want [goal] so that [benefit]'"
            )

        # Count acceptance criteria
        ac_count = len(AC_PATTERN.findall(content))
        if ac_count == 0 and user_story_count > 0:
            warnings.append(
                "No acceptance criteria found for user stories. "
                "Consider adding AC1, AC2, etc."
            )

        # Count example references (expected in All Needed Context section)
        example_count = len(EXAMPLE_REFERENCE_PATTERN.findall(content))
        if example_count == 0:
            errors.append(
                "No example references found. Expected at least one table row with "
                "an examples/ path in the 'All Needed Context' section."
            )

        # Check for empty sections
        empty_sections = self._find_empty_sections(content, REQUIRED_PRD_SECTIONS)
        for empty_section in empty_sections:
            errors.append(f"Section '## {empty_section}' appears to be empty")

        # In strict mode, warnings become errors
        if self.strict:
            errors.extend(warnings)
            warnings = []

        return PRDValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            prd_path=prd_path,
            feature_name=feature_name,
            sections_found=sections_found,
            user_story_count=user_story_count,
            ac_count=ac_count,
            example_count=example_count,
        )

    def validate_for_feature(
        self,
        prd_dir: Path,
        feature: str,
    ) -> PRDValidationResult:
        """Validate PRD for a specific feature.

        Args:
            prd_dir: Directory containing PRD files.
            feature: Feature name (will be slugified).

        Returns:
            PRDValidationResult for the feature's PRD.
        """
        # Slugify feature name
        feature_slug = feature.lower().replace(" ", "-").replace("_", "-")
        prd_path = prd_dir / f"{feature_slug}.md"

        return self.validate_prd(prd_path)

    def _find_sections(self, content: str) -> list[str]:
        """Extract all ## section headers from content.

        Args:
            content: PRD file content.

        Returns:
            List of section names (without ##).
        """
        sections: list[str] = []
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("## "):
                section_name = line[3:].strip()
                sections.append(section_name)
        return sections

    def _find_empty_sections(
        self,
        content: str,
        sections_to_check: list[str],
    ) -> list[str]:
        """Find sections that appear to be empty.

        Args:
            content: PRD file content.
            sections_to_check: List of section names to check.

        Returns:
            List of section names that appear empty.
        """
        empty_sections: list[str] = []
        lines = content.split("\n")
        sections_lower = [s.lower() for s in sections_to_check]

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check if this is a section we care about
            if line.startswith("## "):
                section_name = line[3:].strip()
                if section_name.lower() in sections_lower:
                    # Check if next meaningful content is another section or EOF
                    j = i + 1
                    has_content = False

                    while j < len(lines):
                        next_line = lines[j].strip()
                        if next_line.startswith("## "):
                            # Hit next section without finding content
                            break
                        if next_line and not next_line.startswith("#"):
                            has_content = True
                            break
                        j += 1

                    if not has_content:
                        empty_sections.append(section_name)

            i += 1

        return empty_sections


def validate_prd_for_transition(
    prd_dir: Path,
    feature: str,
) -> PRDValidationResult:
    """Convenience function to validate PRD for transition gate.

    Args:
        prd_dir: Directory containing PRD files.
        feature: Feature name.

    Returns:
        PRDValidationResult indicating if transition can proceed.
    """
    validator = PRDValidator()
    return validator.validate_for_feature(prd_dir, feature)
