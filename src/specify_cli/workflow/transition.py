"""Workflow transition validation schema.

This module defines the schema for workflow transitions including:
- Input/output artifact definitions
- Validation mode types (NONE, KEYWORD, PULL_REQUEST)
- Transition validation logic

Every workflow transition MUST define:
1. Input artifacts - What must exist before transition
2. Output artifacts - What is produced by the workflow
3. Validation mode - NONE, KEYWORD["..."], or PULL_REQUEST

Example:
    >>> from specify_cli.workflow.transition import (
    ...     TransitionSchema, ValidationMode, Artifact
    ... )
    >>> schema = TransitionSchema(
    ...     name="specify",
    ...     from_state="Assessed",
    ...     to_state="Specified",
    ...     input_artifacts=[Artifact(type="assessment_report", path="./docs/assess/{feature}.md")],
    ...     output_artifacts=[Artifact(type="prd", path="./docs/prd/{feature}.md")],
    ...     validation=ValidationMode.NONE,
    ... )
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ValidationMode(Enum):
    """Validation mode for workflow transitions.

    Determines how a transition is gated before proceeding.

    Attributes:
        NONE: No gate - transition proceeds automatically after artifacts created.
        KEYWORD: User must type exact keyword to proceed (e.g., "APPROVED").
        PULL_REQUEST: Transition blocked until PR containing artifact is merged.
    """

    NONE = "NONE"
    KEYWORD = "KEYWORD"
    PULL_REQUEST = "PULL_REQUEST"


@dataclass
class Artifact:
    """Definition of an artifact in the workflow.

    Artifacts are files or directories produced or consumed by workflow transitions.
    Path patterns support variables: {feature}, {NNN}, {slug}.

    Attributes:
        type: Artifact type identifier (e.g., "prd", "adr", "assessment_report").
        path: File path pattern with optional variables.
        required: Whether this artifact must exist for transition (default: True).
        multiple: Whether multiple files of this type are expected (default: False).

    Path Pattern Variables:
        - {feature}: Feature name slug (e.g., "user-authentication")
        - {NNN}: Zero-padded number (e.g., "001", "002")
        - {slug}: Title slug derived from feature name

    Example:
        >>> artifact = Artifact(
        ...     type="adr",
        ...     path="./docs/adr/ADR-{NNN}-{slug}.md",
        ...     multiple=True,
        ... )
    """

    type: str
    path: str = ""
    required: bool = True
    multiple: bool = False

    def __post_init__(self) -> None:
        """Validate artifact definition."""
        if not self.type:
            raise ValueError("Artifact type cannot be empty")

    def resolve_path(
        self,
        feature: str = "",
        number: int = 1,
        slug: str = "",
    ) -> str:
        """Resolve path pattern with actual values.

        Args:
            feature: Feature name for {feature} variable.
            number: Number for {NNN} variable (zero-padded to 3 digits).
            slug: Slug for {slug} variable (defaults to feature if not provided).

        Returns:
            Resolved path with variables substituted.

        Example:
            >>> artifact = Artifact(type="adr", path="./docs/adr/ADR-{NNN}-{slug}.md")
            >>> artifact.resolve_path(feature="auth", number=1, slug="oauth-strategy")
            './docs/adr/ADR-001-oauth-strategy.md'
        """
        if not self.path:
            return ""

        resolved = self.path
        if feature:
            resolved = resolved.replace("{feature}", feature)
        if slug or feature:
            resolved = resolved.replace("{slug}", slug or feature)
        resolved = resolved.replace("{NNN}", f"{number:03d}")

        return resolved

    def matches_pattern(self, file_path: str) -> bool:
        """Check if a file path matches this artifact's pattern.

        Args:
            file_path: Actual file path to check.

        Returns:
            True if the file path matches the pattern.
        """
        if not self.path:
            return False

        # Convert glob pattern to regex
        pattern = self.path
        pattern = pattern.replace(".", r"\.")
        pattern = pattern.replace("*", ".*")
        pattern = pattern.replace("{feature}", r"[\w-]+")
        pattern = pattern.replace("{NNN}", r"\d{3}")
        pattern = pattern.replace("{slug}", r"[\w-]+")
        pattern = f"^{pattern}$"

        return bool(re.match(pattern, file_path))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Artifact:
        """Create Artifact from dictionary representation.

        Args:
            data: Dictionary with artifact fields.

        Returns:
            Artifact instance.
        """
        return cls(
            type=data.get("type", ""),
            path=data.get("path", ""),
            required=data.get("required", True),
            multiple=data.get("multiple", False),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with artifact fields.
        """
        result: dict[str, Any] = {"type": self.type}
        if self.path:
            result["path"] = self.path
        if not self.required:
            result["required"] = False
        if self.multiple:
            result["multiple"] = True
        return result


@dataclass
class KeywordValidation:
    """KEYWORD validation mode configuration.

    Requires user to type an exact keyword to approve the transition.

    Attributes:
        keyword: The exact keyword the user must type (case-sensitive).

    Example:
        >>> validation = KeywordValidation(keyword="PRD_APPROVED")
    """

    keyword: str

    def __post_init__(self) -> None:
        """Validate keyword configuration."""
        if not self.keyword:
            raise ValueError("Keyword cannot be empty for KEYWORD validation mode")

    def __str__(self) -> str:
        """Return YAML-compatible string representation."""
        return f'KEYWORD["{self.keyword}"]'


def parse_validation_mode(value: str | None) -> tuple[ValidationMode, str | None]:
    """Parse validation mode from string representation.

    Supports the following formats:
    - "NONE" -> (ValidationMode.NONE, None)
    - 'KEYWORD["APPROVED"]' -> (ValidationMode.KEYWORD, "APPROVED")
    - "PULL_REQUEST" -> (ValidationMode.PULL_REQUEST, None)

    Args:
        value: String representation of validation mode.

    Returns:
        Tuple of (ValidationMode, optional keyword string).

    Raises:
        ValueError: If the format is invalid.

    Example:
        >>> parse_validation_mode('KEYWORD["APPROVED"]')
        (ValidationMode.KEYWORD, 'APPROVED')
        >>> parse_validation_mode("NONE")
        (ValidationMode.NONE, None)
    """
    if not value or value.upper() == "NONE":
        return (ValidationMode.NONE, None)

    if value.upper() == "PULL_REQUEST":
        return (ValidationMode.PULL_REQUEST, None)

    # Parse KEYWORD["..."] format
    keyword_match = re.match(r'KEYWORD\["([^"]+)"\]', value, re.IGNORECASE)
    if keyword_match:
        return (ValidationMode.KEYWORD, keyword_match.group(1))

    raise ValueError(
        f"Invalid validation mode: '{value}'. "
        'Expected NONE, KEYWORD["<string>"], or PULL_REQUEST'
    )


def format_validation_mode(mode: ValidationMode, keyword: str | None = None) -> str:
    """Format validation mode to string representation.

    Args:
        mode: The validation mode enum value.
        keyword: Optional keyword for KEYWORD mode.

    Returns:
        String representation for YAML.

    Raises:
        ValueError: If KEYWORD mode is used without a keyword.
    """
    if mode == ValidationMode.NONE:
        return "NONE"
    if mode == ValidationMode.PULL_REQUEST:
        return "PULL_REQUEST"
    if mode == ValidationMode.KEYWORD:
        if not keyword:
            raise ValueError("KEYWORD validation mode requires a keyword")
        return f'KEYWORD["{keyword}"]'
    return "NONE"


@dataclass
class TransitionSchema:
    """Schema definition for a workflow transition.

    Defines the complete specification for transitioning between workflow states,
    including required input artifacts, produced output artifacts, and validation mode.

    Attributes:
        name: Unique transition name (e.g., "specify", "plan", "implement").
        from_state: Source state for the transition.
        to_state: Destination state for the transition.
        via: Workflow command that triggers this transition.
        input_artifacts: Artifacts required before transition can proceed.
        output_artifacts: Artifacts produced by this transition.
        validation: Validation mode (NONE, KEYWORD, PULL_REQUEST).
        validation_keyword: Keyword for KEYWORD validation mode.
        description: Human-readable description of the transition.

    Example:
        >>> schema = TransitionSchema(
        ...     name="specify",
        ...     from_state="Assessed",
        ...     to_state="Specified",
        ...     via="specify",
        ...     input_artifacts=[
        ...         Artifact(type="assessment_report", path="./docs/assess/{feature}.md"),
        ...     ],
        ...     output_artifacts=[
        ...         Artifact(type="prd", path="./docs/prd/{feature}.md"),
        ...         Artifact(type="backlog_tasks", path="./backlog/tasks/*.md"),
        ...     ],
        ...     validation=ValidationMode.NONE,
        ... )
    """

    name: str
    from_state: str | list[str]
    to_state: str
    via: str = ""
    input_artifacts: list[Artifact] = field(default_factory=list)
    output_artifacts: list[Artifact] = field(default_factory=list)
    validation: ValidationMode = ValidationMode.NONE
    validation_keyword: str | None = None
    description: str = ""

    def __post_init__(self) -> None:
        """Validate transition schema."""
        if not self.name:
            raise ValueError("Transition name cannot be empty")
        if not self.from_state:
            raise ValueError("Transition from_state cannot be empty")
        if not self.to_state:
            raise ValueError("Transition to_state cannot be empty")

        # Set via to name if not provided
        if not self.via:
            self.via = self.name

        # Validate KEYWORD mode has keyword
        if self.validation == ValidationMode.KEYWORD and not self.validation_keyword:
            raise ValueError("KEYWORD validation mode requires validation_keyword")

    @property
    def from_states(self) -> list[str]:
        """Get from_state as a list (handles both single state and list)."""
        if isinstance(self.from_state, list):
            return self.from_state
        return [self.from_state]

    def get_required_input_artifacts(self) -> list[Artifact]:
        """Get only required input artifacts."""
        return [a for a in self.input_artifacts if a.required]

    def get_required_output_artifacts(self) -> list[Artifact]:
        """Get only required output artifacts."""
        return [a for a in self.output_artifacts if a.required]

    def get_validation_string(self) -> str:
        """Get validation mode as string representation."""
        return format_validation_mode(self.validation, self.validation_keyword)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TransitionSchema:
        """Create TransitionSchema from dictionary representation.

        Args:
            data: Dictionary with transition fields.

        Returns:
            TransitionSchema instance.
        """
        # Parse validation mode
        validation_str = data.get("validation", "NONE")
        validation_mode, keyword = parse_validation_mode(validation_str)

        # Parse artifacts
        input_artifacts = [
            Artifact.from_dict(a) if isinstance(a, dict) else Artifact(type=str(a))
            for a in data.get("input_artifacts", [])
        ]
        output_artifacts = [
            Artifact.from_dict(a) if isinstance(a, dict) else Artifact(type=str(a))
            for a in data.get("output_artifacts", [])
        ]

        return cls(
            name=data.get("name", ""),
            from_state=data.get("from", data.get("from_state", "")),
            to_state=data.get("to", data.get("to_state", "")),
            via=data.get("via", data.get("name", "")),
            input_artifacts=input_artifacts,
            output_artifacts=output_artifacts,
            validation=validation_mode,
            validation_keyword=keyword,
            description=data.get("description", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation for YAML serialization.

        Returns:
            Dictionary with transition fields.
        """
        result: dict[str, Any] = {
            "name": self.name,
            "from": self.from_state,
            "to": self.to_state,
            "via": self.via,
        }

        if self.input_artifacts:
            result["input_artifacts"] = [a.to_dict() for a in self.input_artifacts]

        if self.output_artifacts:
            result["output_artifacts"] = [a.to_dict() for a in self.output_artifacts]

        result["validation"] = self.get_validation_string()

        if self.description:
            result["description"] = self.description

        return result


# Standard workflow transitions with artifact definitions
WORKFLOW_TRANSITIONS: list[TransitionSchema] = [
    # Entry transition: assess
    TransitionSchema(
        name="assess",
        from_state="To Do",
        to_state="Assessed",
        via="assess",
        input_artifacts=[],  # Entry point - no inputs required
        output_artifacts=[
            Artifact(
                type="assessment_report",
                path="./docs/assess/{feature}-assessment.md",
            ),
        ],
        validation=ValidationMode.NONE,
        description="Evaluate SDD workflow suitability (Full/Light/Skip)",
    ),
    # Specify transition
    TransitionSchema(
        name="specify",
        from_state="Assessed",
        to_state="Specified",
        via="specify",
        input_artifacts=[
            Artifact(
                type="assessment_report",
                path="./docs/assess/{feature}-assessment.md",
                required=True,
            ),
        ],
        output_artifacts=[
            Artifact(
                type="prd",
                path="./docs/prd/{feature}.md",
                required=True,
            ),
            Artifact(
                type="backlog_tasks",
                path="./backlog/tasks/*.md",
                required=True,
                multiple=True,
            ),
        ],
        validation=ValidationMode.NONE,
        description="Create PRD with user stories and acceptance criteria",
    ),
    # Research transition (optional)
    TransitionSchema(
        name="research",
        from_state="Specified",
        to_state="Researched",
        via="research",
        input_artifacts=[
            Artifact(
                type="prd",
                path="./docs/prd/{feature}.md",
                required=True,
            ),
        ],
        output_artifacts=[
            Artifact(
                type="research_report",
                path="./docs/research/{feature}-research.md",
            ),
            Artifact(
                type="business_validation",
                path="./docs/research/{feature}-validation.md",
            ),
        ],
        validation=ValidationMode.NONE,
        description="Technical and business research completed",
    ),
    # Plan transition (can come from Specified or Researched)
    TransitionSchema(
        name="plan",
        from_state=["Specified", "Researched"],
        to_state="Planned",
        via="plan",
        input_artifacts=[
            Artifact(
                type="prd",
                path="./docs/prd/{feature}.md",
                required=True,
            ),
        ],
        output_artifacts=[
            Artifact(
                type="adr",
                path="./docs/adr/ADR-{NNN}-{slug}.md",
                required=True,
                multiple=True,
            ),
            Artifact(
                type="platform_design",
                path="./docs/platform/{feature}-platform.md",
                required=False,
            ),
        ],
        validation=ValidationMode.NONE,
        description="Architecture planned with ADRs",
    ),
    # Implement transition
    TransitionSchema(
        name="implement",
        from_state="Planned",
        to_state="In Implementation",
        via="implement",
        input_artifacts=[
            Artifact(
                type="adr",
                path="./docs/adr/ADR-*.md",
                required=True,
            ),
        ],
        output_artifacts=[
            Artifact(
                type="source_code",
                path="./src/",
            ),
            Artifact(
                type="tests",
                path="./tests/",
                required=True,
            ),
            Artifact(
                type="ac_coverage",
                path="./tests/ac-coverage.json",
                required=True,
            ),
        ],
        validation=ValidationMode.NONE,
        description="Implementation work with tests and AC coverage",
    ),
    # Validate transition
    TransitionSchema(
        name="validate",
        from_state="In Implementation",
        to_state="Validated",
        via="validate",
        input_artifacts=[
            Artifact(type="tests", required=True),
            Artifact(type="ac_coverage", required=True),
        ],
        output_artifacts=[
            Artifact(
                type="qa_report",
                path="./docs/qa/{feature}-qa-report.md",
            ),
            Artifact(
                type="security_report",
                path="./docs/security/{feature}-security.md",
            ),
        ],
        validation=ValidationMode.NONE,
        description="QA, security, and documentation validated",
    ),
    # Operate transition
    TransitionSchema(
        name="operate",
        from_state="Validated",
        to_state="Deployed",
        via="operate",
        input_artifacts=[
            Artifact(type="qa_report"),
            Artifact(type="security_report"),
        ],
        output_artifacts=[
            Artifact(
                type="deployment_manifest",
                path="./deploy/",
            ),
        ],
        validation=ValidationMode.NONE,
        description="Deployed to production",
    ),
    # Complete transition (manual)
    TransitionSchema(
        name="complete",
        from_state="Deployed",
        to_state="Done",
        via="manual",
        input_artifacts=[],
        output_artifacts=[],
        validation=ValidationMode.NONE,
        description="Production deployment confirmed successful",
    ),
]


def get_transition_by_name(name: str) -> TransitionSchema | None:
    """Get a standard workflow transition by name.

    Args:
        name: Transition name (e.g., "specify", "plan").

    Returns:
        TransitionSchema if found, None otherwise.
    """
    for transition in WORKFLOW_TRANSITIONS:
        if transition.name == name:
            return transition
    return None


def get_transitions_from_state(state: str) -> list[TransitionSchema]:
    """Get all transitions that can proceed from a given state.

    Args:
        state: Source state name.

    Returns:
        List of transitions available from this state.
    """
    return [t for t in WORKFLOW_TRANSITIONS if state in t.from_states]


def validate_transition_schema(schema: TransitionSchema) -> list[str]:
    """Validate a transition schema for completeness.

    Args:
        schema: TransitionSchema to validate.

    Returns:
        List of validation error messages (empty if valid).
    """
    errors: list[str] = []

    # Check required fields
    if not schema.name:
        errors.append("Transition name is required")
    if not schema.from_state:
        errors.append("Transition from_state is required")
    if not schema.to_state:
        errors.append("Transition to_state is required")

    # Check KEYWORD validation has keyword
    if schema.validation == ValidationMode.KEYWORD and not schema.validation_keyword:
        errors.append("KEYWORD validation mode requires a keyword")

    return errors
