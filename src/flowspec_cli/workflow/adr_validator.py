"""ADR (Architecture Decision Record) requirement gate validator.

This module implements validation for ADR artifacts before workflow
transitions to the "Planned" state.

ADR Format: Michael Nygard's classic ADR format with required sections:
- Title with ADR number
- Status
- Context
- Decision
- Consequences

Example:
    >>> from flowspec_cli.workflow.adr_validator import ADRValidator
    >>> validator = ADRValidator()
    >>> result = validator.validate_adr(Path("./docs/adr/ADR-001-auth.md"))
    >>> if result.is_valid:
    ...     print("ADR is valid")
    ... else:
    ...     for error in result.errors:
    ...         print(f"Error: {error}")
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Required sections in an ADR (case-insensitive matching)
REQUIRED_ADR_SECTIONS = [
    "status",
    "context",
    "decision",
    "consequences",
]

# Optional but recommended sections
RECOMMENDED_ADR_SECTIONS = [
    "alternatives considered",
]

# Valid ADR status values
VALID_ADR_STATUSES = [
    "proposed",
    "accepted",
    "deprecated",
    "superseded",
]

# ADR filename pattern: ADR-{NNN}-{slug}.md
ADR_FILENAME_PATTERN = re.compile(r"^ADR-(\d{3})-(.+)\.md$")


@dataclass
class ADRValidationResult:
    """Result of ADR validation.

    Attributes:
        is_valid: Whether the ADR passes validation.
        errors: List of validation errors (blocking).
        warnings: List of validation warnings (non-blocking).
        adr_path: Path to the validated ADR file.
        adr_number: Extracted ADR number (e.g., 1, 2, 3).
        adr_title: Extracted ADR title from filename slug.
        sections_found: List of sections found in the ADR.
        status: ADR status value if found.
    """

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    adr_path: Path | None = None
    adr_number: int | None = None
    adr_title: str | None = None
    sections_found: list[str] = field(default_factory=list)
    status: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "adr_path": str(self.adr_path) if self.adr_path else None,
            "adr_number": self.adr_number,
            "adr_title": self.adr_title,
            "sections_found": self.sections_found,
            "status": self.status,
        }


class ADRValidator:
    """Validator for Architecture Decision Records.

    Validates ADR files for:
    1. Correct filename format (ADR-{NNN}-{slug}.md)
    2. Required sections present (Status, Context, Decision, Consequences)
    3. Valid status value
    4. Non-empty required sections

    Example:
        >>> validator = ADRValidator()
        >>> result = validator.validate_adr(Path("./docs/adr/ADR-001-auth.md"))
        >>> print(f"Valid: {result.is_valid}")
    """

    def __init__(self, strict: bool = False) -> None:
        """Initialize ADR validator.

        Args:
            strict: If True, treat warnings as errors.
        """
        self.strict = strict

    def validate_adr(self, adr_path: Path) -> ADRValidationResult:
        """Validate a single ADR file.

        Args:
            adr_path: Path to the ADR file.

        Returns:
            ADRValidationResult with validation details.
        """
        errors: list[str] = []
        warnings: list[str] = []
        sections_found: list[str] = []
        adr_number: int | None = None
        adr_title: str | None = None
        status: str | None = None

        # Check file exists
        if not adr_path.exists():
            return ADRValidationResult(
                is_valid=False,
                errors=[f"ADR file not found: {adr_path}"],
                adr_path=adr_path,
            )

        # Validate filename format
        filename_match = ADR_FILENAME_PATTERN.match(adr_path.name)
        if not filename_match:
            errors.append(
                f"Invalid ADR filename format: '{adr_path.name}'. "
                "Expected: ADR-{NNN}-{slug}.md (e.g., ADR-001-auth-strategy.md)"
            )
        else:
            adr_number = int(filename_match.group(1))
            adr_title = filename_match.group(2).replace("-", " ").title()

        # Read and parse ADR content
        try:
            content = adr_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            return ADRValidationResult(
                is_valid=False,
                errors=[f"Failed to read ADR file: {e}"],
                adr_path=adr_path,
            )

        # Find sections (## headers)
        sections_found = self._find_sections(content)
        sections_lower = [s.lower() for s in sections_found]

        # Check required sections
        for required in REQUIRED_ADR_SECTIONS:
            if required.lower() not in sections_lower:
                errors.append(f"Missing required section: '## {required.title()}'")

        # Check recommended sections
        for recommended in RECOMMENDED_ADR_SECTIONS:
            if recommended.lower() not in sections_lower:
                warnings.append(
                    f"Recommended section missing: '## {recommended.title()}'"
                )

        # Validate status value
        status = self._extract_status(content)
        if status:
            status_lower = status.lower()
            # Handle "superseded by ADR-XXX" format
            if status_lower.startswith("superseded"):
                if not re.match(r"superseded by adr-\d{3}", status_lower):
                    warnings.append(
                        f"Superseded status should reference ADR number: "
                        f"'Superseded by ADR-XXX' (found: '{status}')"
                    )
            elif status_lower not in VALID_ADR_STATUSES:
                errors.append(
                    f"Invalid status: '{status}'. "
                    f"Valid values: {', '.join(VALID_ADR_STATUSES)} "
                    f"or 'Superseded by ADR-XXX'"
                )
        else:
            if "status" in sections_lower:
                warnings.append("Status section found but no status value detected")

        # Check for empty sections
        empty_sections = self._find_empty_sections(content, REQUIRED_ADR_SECTIONS)
        for empty_section in empty_sections:
            errors.append(f"Section '## {empty_section}' appears to be empty")

        # In strict mode, warnings become errors
        if self.strict:
            errors.extend(warnings)
            warnings = []

        return ADRValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            adr_path=adr_path,
            adr_number=adr_number,
            adr_title=adr_title,
            sections_found=sections_found,
            status=status,
        )

    def validate_directory(
        self,
        adr_dir: Path,
        feature: str | None = None,
        min_count: int = 1,
    ) -> ADRValidationResult:
        """Validate all ADRs in a directory.

        Args:
            adr_dir: Directory containing ADR files.
            feature: Optional feature name to filter ADRs.
            min_count: Minimum number of ADRs required.

        Returns:
            Combined ADRValidationResult for all ADRs.
        """
        errors: list[str] = []
        warnings: list[str] = []

        if not adr_dir.exists():
            return ADRValidationResult(
                is_valid=False,
                errors=[f"ADR directory not found: {adr_dir}"],
            )

        # Find ADR files
        adr_files = sorted(adr_dir.glob("ADR-*.md"))

        if not adr_files:
            return ADRValidationResult(
                is_valid=False,
                errors=[f"No ADR files found in {adr_dir}"],
            )

        if len(adr_files) < min_count:
            errors.append(
                f"Expected at least {min_count} ADR(s), found {len(adr_files)}"
            )

        # Validate each ADR
        adr_numbers_seen: set[int] = set()
        all_sections: list[str] = []

        for adr_file in adr_files:
            result = self.validate_adr(adr_file)

            if result.errors:
                errors.extend(result.errors)
            if result.warnings:
                warnings.extend(result.warnings)
            if result.sections_found:
                all_sections.extend(result.sections_found)

            # Check for duplicate ADR numbers
            if result.adr_number is not None:
                if result.adr_number in adr_numbers_seen:
                    errors.append(f"Duplicate ADR number: {result.adr_number:03d}")
                adr_numbers_seen.add(result.adr_number)

        # In strict mode, warnings become errors
        if self.strict:
            errors.extend(warnings)
            warnings = []

        return ADRValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            adr_path=adr_dir,
            sections_found=list(set(all_sections)),
        )

    def get_next_adr_number(self, adr_dir: Path) -> int:
        """Get the next available ADR number.

        Args:
            adr_dir: Directory containing ADR files.

        Returns:
            Next available ADR number (1 if no ADRs exist).
        """
        if not adr_dir.exists():
            return 1

        max_number = 0
        for adr_file in adr_dir.glob("ADR-*.md"):
            match = ADR_FILENAME_PATTERN.match(adr_file.name)
            if match:
                number = int(match.group(1))
                max_number = max(max_number, number)

        return max_number + 1

    def _find_sections(self, content: str) -> list[str]:
        """Extract all ## section headers from content.

        Args:
            content: ADR file content.

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

    def _extract_status(self, content: str) -> str | None:
        """Extract ADR status value from content.

        Looks for status in two formats:
        1. ## Status section with content on next line
        2. Status: value in the document

        Args:
            content: ADR file content.

        Returns:
            Status value if found, None otherwise.
        """
        lines = content.split("\n")
        in_status_section = False

        for line in lines:
            stripped = line.strip()

            # Check for ## Status section
            if stripped.lower() == "## status":
                in_status_section = True
                continue

            # If in status section, next non-empty line is the status
            if in_status_section and stripped:
                # Stop if we hit another section
                if stripped.startswith("## "):
                    return None
                return stripped

            # Check for inline "Status: value" format
            if stripped.lower().startswith("status:"):
                return stripped.split(":", 1)[1].strip()

        return None

    def _find_empty_sections(
        self,
        content: str,
        sections_to_check: list[str],
    ) -> list[str]:
        """Find sections that appear to be empty.

        Args:
            content: ADR file content.
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


def validate_adr_for_transition(
    adr_dir: Path,
    feature: str | None = None,
) -> ADRValidationResult:
    """Convenience function to validate ADRs for transition gate.

    Args:
        adr_dir: Directory containing ADR files.
        feature: Optional feature name.

    Returns:
        ADRValidationResult indicating if transition can proceed.
    """
    validator = ADRValidator()
    return validator.validate_directory(adr_dir, feature=feature)
