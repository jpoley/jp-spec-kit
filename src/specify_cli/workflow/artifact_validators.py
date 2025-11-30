"""Artifact validation for workflow transitions.

This module provides validation logic for workflow artifacts to ensure
they meet structural and content requirements before transitions can proceed.

Validators check:
- File existence
- Required sections present
- Content completeness
- Structural integrity

Each artifact type (PRD, ADR, etc.) has its own validator class.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class ValidationResult:
    """Result of artifact validation.

    Attributes:
        valid: Whether the artifact passes validation.
        errors: List of validation error messages.
        warnings: List of validation warning messages.
        artifact_path: Path to the validated artifact.
    """

    valid: bool
    errors: list[str]
    warnings: list[str]
    artifact_path: str

    def __bool__(self) -> bool:
        """Allow using result in boolean context."""
        return self.valid

    def add_error(self, message: str) -> None:
        """Add an error and mark validation as failed."""
        self.errors.append(message)
        self.valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning (doesn't fail validation)."""
        self.warnings.append(message)


class ArtifactValidator(Protocol):
    """Protocol for artifact validators.

    All artifact validators must implement this protocol.
    """

    def validate(self, artifact_path: Path) -> ValidationResult:
        """Validate an artifact file.

        Args:
            artifact_path: Path to the artifact file.

        Returns:
            ValidationResult with validation status and messages.
        """
        ...


class PRDValidator:
    """Validator for Product Requirements Document (PRD) artifacts.

    Validates that PRD files contain all required sections and meet
    structural requirements for the transition to "Specified" state.

    Required Sections:
        - Executive Summary
        - Problem Statement
        - User Stories (with acceptance criteria)
        - Functional Requirements
        - Non-Functional Requirements
        - Success Metrics
        - Dependencies
        - Risks and Mitigations
        - Out of Scope
    """

    REQUIRED_SECTIONS = [
        "Executive Summary",
        "Problem Statement",
        "User Stories",
        "Functional Requirements",
        "Non-Functional Requirements",
        "Success Metrics",
        "Dependencies",
        "Risks and Mitigations",
        "Out of Scope",
    ]

    def __init__(self) -> None:
        """Initialize PRD validator."""
        pass

    def validate(self, artifact_path: Path) -> ValidationResult:
        """Validate a PRD file.

        Checks:
        1. File exists and is readable
        2. All required sections are present
        3. User stories have acceptance criteria
        4. Functional requirements are numbered
        5. Success metrics are defined

        Args:
            artifact_path: Path to the PRD file.

        Returns:
            ValidationResult with validation status and detailed messages.
        """
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=[],
            artifact_path=str(artifact_path),
        )

        # Check file existence
        if not artifact_path.exists():
            result.add_error(f"PRD file not found: {artifact_path}")
            return result

        if not artifact_path.is_file():
            result.add_error(f"PRD path is not a file: {artifact_path}")
            return result

        # Read file content
        try:
            content = artifact_path.read_text(encoding="utf-8")
        except Exception as e:
            result.add_error(f"Failed to read PRD file: {e}")
            return result

        # Validate required sections
        missing_sections = self._check_required_sections(content)
        for section in missing_sections:
            result.add_error(f"Missing required section: {section}")

        # Validate user stories have acceptance criteria
        if "User Stories" in content:
            ac_issues = self._check_acceptance_criteria(content)
            for issue in ac_issues:
                result.add_warning(issue)

        # Validate functional requirements are numbered
        if "Functional Requirements" in content:
            fr_issues = self._check_functional_requirements(content)
            for issue in fr_issues:
                result.add_warning(issue)

        # Validate success metrics exist
        if "Success Metrics" in content:
            sm_issues = self._check_success_metrics(content)
            for issue in sm_issues:
                result.add_warning(issue)

        # Check for placeholder content
        placeholder_issues = self._check_placeholders(content)
        for issue in placeholder_issues:
            result.add_warning(issue)

        return result

    def _check_required_sections(self, content: str) -> list[str]:
        """Check for presence of required sections.

        Args:
            content: PRD file content.

        Returns:
            List of missing section names.
        """
        missing = []
        for section in self.REQUIRED_SECTIONS:
            # Look for markdown headers (## or ###) with section name
            pattern = rf"^#{{1,6}}\s+{re.escape(section)}"
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                missing.append(section)
        return missing

    def _check_acceptance_criteria(self, content: str) -> list[str]:
        """Check that user stories have acceptance criteria.

        Args:
            content: PRD file content.

        Returns:
            List of warning messages for missing/incomplete ACs.
        """
        issues = []

        # Find user story sections
        user_story_pattern = r"###\s+User Story \d+"
        user_stories = re.finditer(user_story_pattern, content)

        for match in user_stories:
            story_start = match.end()
            # Find next user story or end of section
            next_story = re.search(user_story_pattern, content[story_start:])
            story_end = story_start + next_story.start() if next_story else len(content)
            story_content = content[story_start:story_end]

            # Check for acceptance criteria
            if "Acceptance Criteria" not in story_content:
                story_title = match.group(0)
                issues.append(f"{story_title} missing 'Acceptance Criteria' section")
            elif not re.search(
                r"\*\*Given\*\*.*\*\*When\*\*.*\*\*Then\*\*", story_content
            ):
                story_title = match.group(0)
                issues.append(
                    f"{story_title} has Acceptance Criteria but no Given-When-Then format"
                )

        return issues

    def _check_functional_requirements(self, content: str) -> list[str]:
        """Check that functional requirements are properly numbered.

        Args:
            content: PRD file content.

        Returns:
            List of warning messages for requirement issues.
        """
        issues = []

        # Extract Functional Requirements section
        fr_match = re.search(
            r"##\s+Functional Requirements(.*?)(?=^##|\Z)",
            content,
            re.MULTILINE | re.DOTALL | re.IGNORECASE,
        )

        if not fr_match:
            return issues

        fr_section = fr_match.group(1)

        # Look for numbered requirements (FR-001, FR-002, etc.)
        requirements = re.findall(r"\*\*FR-\d{3}\*\*:", fr_section)

        if not requirements:
            issues.append(
                "Functional Requirements section has no numbered requirements (FR-001, FR-002, etc.)"
            )
        elif len(requirements) < 3:
            issues.append(
                f"Only {len(requirements)} functional requirements found - consider if more are needed"
            )

        return issues

    def _check_success_metrics(self, content: str) -> list[str]:
        """Check that success metrics are defined.

        Args:
            content: PRD file content.

        Returns:
            List of warning messages for metric issues.
        """
        issues = []

        # Extract Success Metrics section
        sm_match = re.search(
            r"##\s+Success Metrics(.*?)(?=^##|\Z)",
            content,
            re.MULTILINE | re.DOTALL | re.IGNORECASE,
        )

        if not sm_match:
            return issues

        sm_section = sm_match.group(1)

        # Look for numbered metrics (SM-001, SM-002, etc.)
        metrics = re.findall(r"\*\*SM-\d{3}\*\*:", sm_section)

        if not metrics:
            issues.append(
                "Success Metrics section has no numbered metrics (SM-001, SM-002, etc.)"
            )
        elif len(metrics) < 2:
            issues.append(
                f"Only {len(metrics)} success metrics found - consider adding more measurable outcomes"
            )

        return issues

    def _check_placeholders(self, content: str) -> list[str]:
        """Check for placeholder content that should be replaced.

        Args:
            content: PRD file content.

        Returns:
            List of warning messages for placeholder content.
        """
        issues = []

        # Common placeholder patterns
        placeholder_patterns = [
            r"\[FEATURE NAME\]",
            r"\[DATE\]",
            r"\[feature-name\]",
            r"\[Provide a.*?\]",
            r"\[Describe.*?\]",
            r"\[Explain.*?\]",
        ]

        for pattern in placeholder_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                issues.append(
                    f"Found {len(matches)} placeholder(s): {pattern} - should be replaced with actual content"
                )

        return issues


class ADRValidator:
    """Validator for Architecture Decision Record (ADR) artifacts.

    Validates that ADR files follow the Nygard ADR format with:
    - Title with ADR number
    - Status (Proposed/Accepted/Deprecated/Superseded)
    - Context section
    - Decision section
    - Consequences section (Positive/Negative)
    - Alternatives Considered section
    """

    REQUIRED_SECTIONS = [
        "Status",
        "Context",
        "Decision",
        "Consequences",
        "Alternatives Considered",
    ]

    def validate(self, artifact_path: Path) -> ValidationResult:
        """Validate an ADR file.

        Args:
            artifact_path: Path to the ADR file.

        Returns:
            ValidationResult with validation status.
        """
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=[],
            artifact_path=str(artifact_path),
        )

        # Check file existence
        if not artifact_path.exists():
            result.add_error(f"ADR file not found: {artifact_path}")
            return result

        if not artifact_path.is_file():
            result.add_error(f"ADR path is not a file: {artifact_path}")
            return result

        # Read content
        try:
            content = artifact_path.read_text(encoding="utf-8")
        except Exception as e:
            result.add_error(f"Failed to read ADR file: {e}")
            return result

        # Check for ADR number in filename
        if not re.match(r".*ADR-\d{3}-.*\.md", artifact_path.name):
            result.add_warning(
                f"ADR filename should follow pattern 'ADR-NNN-title.md': {artifact_path.name}"
            )

        # Validate required sections
        missing_sections = self._check_required_sections(content)
        for section in missing_sections:
            result.add_error(f"Missing required section: {section}")

        # Validate status
        status_issues = self._check_status(content)
        for issue in status_issues:
            result.add_warning(issue)

        return result

    def _check_required_sections(self, content: str) -> list[str]:
        """Check for required ADR sections."""
        missing = []
        for section in self.REQUIRED_SECTIONS:
            pattern = rf"^#{{1,6}}\s+{re.escape(section)}"
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                missing.append(section)
        return missing

    def _check_status(self, content: str) -> list[str]:
        """Check ADR status is valid."""
        issues = []
        valid_statuses = ["Proposed", "Accepted", "Deprecated", "Superseded"]

        status_match = re.search(
            r"##\s+Status\s*\n\s*(\w+)", content, re.MULTILINE | re.IGNORECASE
        )

        if status_match:
            status = status_match.group(1)
            if status not in valid_statuses:
                issues.append(
                    f"Invalid status '{status}' - should be one of: {', '.join(valid_statuses)}"
                )

        return issues


def get_next_adr_number(adr_dir: Path = Path("./docs/adr")) -> int:
    """Get the next ADR number by scanning existing ADR files.

    Scans the ADR directory for files matching the pattern ADR-NNN-*.md
    and returns the next available number.

    Args:
        adr_dir: Path to the ADR directory (default: ./docs/adr).

    Returns:
        Next available ADR number (e.g., if ADR-001.md exists, returns 2).
        Returns 1 if no ADRs exist.

    Example:
        >>> get_next_adr_number(Path("./docs/adr"))
        3  # If ADR-001 and ADR-002 exist
    """
    if not adr_dir.exists():
        return 1

    # Find all ADR files matching pattern ADR-NNN-*.md
    adr_pattern = re.compile(r"ADR-(\d{3})-.*\.md")
    max_number = 0

    for file_path in adr_dir.glob("ADR-*.md"):
        match = adr_pattern.match(file_path.name)
        if match:
            number = int(match.group(1))
            max_number = max(max_number, number)

    return max_number + 1


def find_existing_adrs(adr_dir: Path = Path("./docs/adr")) -> list[Path]:
    """Find all existing ADR files in the directory.

    Args:
        adr_dir: Path to the ADR directory (default: ./docs/adr).

    Returns:
        List of Path objects for all ADR files, sorted by number.

    Example:
        >>> adrs = find_existing_adrs(Path("./docs/adr"))
        >>> [adr.name for adr in adrs]
        ['ADR-001-database-choice.md', 'ADR-002-api-framework.md']
    """
    if not adr_dir.exists():
        return []

    adr_pattern = re.compile(r"ADR-(\d{3})-.*\.md")
    adrs: list[tuple[int, Path]] = []

    for file_path in adr_dir.glob("ADR-*.md"):
        match = adr_pattern.match(file_path.name)
        if match:
            number = int(match.group(1))
            adrs.append((number, file_path))

    # Sort by number
    adrs.sort(key=lambda x: x[0])
    return [path for _, path in adrs]


def get_validator(artifact_type: str) -> ArtifactValidator | None:
    """Get the appropriate validator for an artifact type.

    Args:
        artifact_type: Type of artifact (e.g., "prd", "adr").

    Returns:
        Validator instance or None if no validator exists for this type.
    """
    validators: dict[str, type[ArtifactValidator]] = {
        "prd": PRDValidator,
        "adr": ADRValidator,
    }

    validator_class = validators.get(artifact_type.lower())
    if validator_class:
        return validator_class()
    return None
