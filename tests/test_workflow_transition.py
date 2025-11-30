"""Tests for workflow transition schema.

Tests cover:
- ValidationMode enum
- Artifact creation and path resolution
- TransitionSchema creation and validation
- Parsing and formatting validation modes
- Standard workflow transitions (WORKFLOW_TRANSITIONS)
"""

import pytest

from specify_cli.workflow.transition import (
    WORKFLOW_TRANSITIONS,
    Artifact,
    KeywordValidation,
    TransitionSchema,
    ValidationMode,
    format_validation_mode,
    get_transition_by_name,
    get_transitions_from_state,
    parse_validation_mode,
    validate_transition_schema,
)


class TestValidationMode:
    """Tests for ValidationMode enum."""

    def test_validation_mode_values(self):
        """AC3: Validation mode enum has NONE, KEYWORD, PULL_REQUEST."""
        assert ValidationMode.NONE.value == "NONE"
        assert ValidationMode.KEYWORD.value == "KEYWORD"
        assert ValidationMode.PULL_REQUEST.value == "PULL_REQUEST"

    def test_validation_mode_count(self):
        """Exactly 3 validation modes exist."""
        assert len(ValidationMode) == 3


class TestArtifact:
    """Tests for Artifact dataclass."""

    def test_artifact_creation_minimal(self):
        """Artifact can be created with just type."""
        artifact = Artifact(type="prd")
        assert artifact.type == "prd"
        assert artifact.path == ""
        assert artifact.required is True
        assert artifact.multiple is False

    def test_artifact_creation_full(self):
        """Artifact can be created with all fields."""
        artifact = Artifact(
            type="adr",
            path="./docs/adr/ADR-{NNN}-{slug}.md",
            required=True,
            multiple=True,
        )
        assert artifact.type == "adr"
        assert artifact.path == "./docs/adr/ADR-{NNN}-{slug}.md"
        assert artifact.required is True
        assert artifact.multiple is True

    def test_artifact_empty_type_raises(self):
        """Artifact with empty type raises ValueError."""
        with pytest.raises(ValueError, match="Artifact type cannot be empty"):
            Artifact(type="")

    def test_artifact_resolve_path_feature(self):
        """AC7: Path pattern resolves {feature} variable."""
        artifact = Artifact(type="prd", path="./docs/prd/{feature}.md")
        resolved = artifact.resolve_path(feature="user-auth")
        assert resolved == "./docs/prd/user-auth.md"

    def test_artifact_resolve_path_nnn(self):
        """AC7: Path pattern resolves {NNN} variable with zero-padding."""
        artifact = Artifact(type="adr", path="./docs/adr/ADR-{NNN}-auth.md")
        assert artifact.resolve_path(number=1) == "./docs/adr/ADR-001-auth.md"
        assert artifact.resolve_path(number=42) == "./docs/adr/ADR-042-auth.md"
        assert artifact.resolve_path(number=999) == "./docs/adr/ADR-999-auth.md"

    def test_artifact_resolve_path_slug(self):
        """AC7: Path pattern resolves {slug} variable."""
        artifact = Artifact(type="adr", path="./docs/adr/ADR-001-{slug}.md")
        resolved = artifact.resolve_path(slug="oauth-strategy")
        assert resolved == "./docs/adr/ADR-001-oauth-strategy.md"

    def test_artifact_resolve_path_all_variables(self):
        """AC7: Path pattern resolves all variables together."""
        artifact = Artifact(type="adr", path="./docs/adr/{feature}/ADR-{NNN}-{slug}.md")
        resolved = artifact.resolve_path(feature="auth", number=2, slug="jwt-tokens")
        assert resolved == "./docs/adr/auth/ADR-002-jwt-tokens.md"

    def test_artifact_resolve_path_slug_defaults_to_feature(self):
        """Slug defaults to feature if not provided."""
        artifact = Artifact(type="test", path="./docs/{slug}-test.md")
        resolved = artifact.resolve_path(feature="my-feature")
        assert resolved == "./docs/my-feature-test.md"

    def test_artifact_matches_pattern_exact(self):
        """Pattern matching works for exact paths."""
        artifact = Artifact(type="prd", path="./docs/prd/user-auth.md")
        assert artifact.matches_pattern("./docs/prd/user-auth.md")
        assert not artifact.matches_pattern("./docs/prd/other.md")

    def test_artifact_matches_pattern_with_variables(self):
        """Pattern matching works with path variables."""
        artifact = Artifact(type="prd", path="./docs/prd/{feature}.md")
        assert artifact.matches_pattern("./docs/prd/user-auth.md")
        assert artifact.matches_pattern("./docs/prd/my-feature.md")
        assert not artifact.matches_pattern("./docs/other/user-auth.md")

    def test_artifact_matches_pattern_with_wildcard(self):
        """Pattern matching works with wildcards."""
        artifact = Artifact(type="adr", path="./docs/adr/ADR-*.md")
        assert artifact.matches_pattern("./docs/adr/ADR-001-auth.md")
        assert artifact.matches_pattern("./docs/adr/ADR-anything.md")

    def test_artifact_from_dict(self):
        """Artifact can be created from dictionary."""
        data = {
            "type": "prd",
            "path": "./docs/prd/{feature}.md",
            "required": True,
            "multiple": False,
        }
        artifact = Artifact.from_dict(data)
        assert artifact.type == "prd"
        assert artifact.path == "./docs/prd/{feature}.md"
        assert artifact.required is True
        assert artifact.multiple is False

    def test_artifact_to_dict(self):
        """Artifact can be serialized to dictionary."""
        artifact = Artifact(
            type="adr",
            path="./docs/adr/ADR-{NNN}-{slug}.md",
            required=True,
            multiple=True,
        )
        data = artifact.to_dict()
        assert data["type"] == "adr"
        assert data["path"] == "./docs/adr/ADR-{NNN}-{slug}.md"
        assert "required" not in data  # True is default, not serialized
        assert data["multiple"] is True


class TestKeywordValidation:
    """Tests for KeywordValidation dataclass."""

    def test_keyword_validation_creation(self):
        """KeywordValidation stores keyword."""
        validation = KeywordValidation(keyword="APPROVED")
        assert validation.keyword == "APPROVED"

    def test_keyword_validation_empty_raises(self):
        """Empty keyword raises ValueError."""
        with pytest.raises(ValueError, match="Keyword cannot be empty"):
            KeywordValidation(keyword="")

    def test_keyword_validation_str(self):
        """String representation is YAML-compatible."""
        validation = KeywordValidation(keyword="PRD_APPROVED")
        assert str(validation) == 'KEYWORD["PRD_APPROVED"]'


class TestParseValidationMode:
    """Tests for parse_validation_mode function."""

    def test_parse_none(self):
        """AC3: Parse NONE mode."""
        mode, keyword = parse_validation_mode("NONE")
        assert mode == ValidationMode.NONE
        assert keyword is None

    def test_parse_none_lowercase(self):
        """Parse NONE is case-insensitive."""
        mode, keyword = parse_validation_mode("none")
        assert mode == ValidationMode.NONE

    def test_parse_none_default(self):
        """Empty/None value defaults to NONE."""
        mode, keyword = parse_validation_mode(None)
        assert mode == ValidationMode.NONE
        mode, keyword = parse_validation_mode("")
        assert mode == ValidationMode.NONE

    def test_parse_pull_request(self):
        """AC3: Parse PULL_REQUEST mode."""
        mode, keyword = parse_validation_mode("PULL_REQUEST")
        assert mode == ValidationMode.PULL_REQUEST
        assert keyword is None

    def test_parse_keyword(self):
        """AC3: Parse KEYWORD mode with string."""
        mode, keyword = parse_validation_mode('KEYWORD["APPROVED"]')
        assert mode == ValidationMode.KEYWORD
        assert keyword == "APPROVED"

    def test_parse_keyword_different_values(self):
        """Parse KEYWORD with various keywords."""
        mode, keyword = parse_validation_mode('KEYWORD["PRD_READY"]')
        assert keyword == "PRD_READY"

        mode, keyword = parse_validation_mode('KEYWORD["LGTM"]')
        assert keyword == "LGTM"

    def test_parse_invalid_raises(self):
        """Invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid validation mode"):
            parse_validation_mode("INVALID")


class TestFormatValidationMode:
    """Tests for format_validation_mode function."""

    def test_format_none(self):
        """Format NONE mode."""
        assert format_validation_mode(ValidationMode.NONE) == "NONE"

    def test_format_pull_request(self):
        """Format PULL_REQUEST mode."""
        assert format_validation_mode(ValidationMode.PULL_REQUEST) == "PULL_REQUEST"

    def test_format_keyword(self):
        """Format KEYWORD mode with keyword."""
        result = format_validation_mode(ValidationMode.KEYWORD, "APPROVED")
        assert result == 'KEYWORD["APPROVED"]'

    def test_format_keyword_missing_raises(self):
        """KEYWORD mode without keyword raises ValueError."""
        with pytest.raises(ValueError, match="requires a keyword"):
            format_validation_mode(ValidationMode.KEYWORD)


class TestTransitionSchema:
    """Tests for TransitionSchema dataclass."""

    def test_transition_creation_minimal(self):
        """AC1: Transition with required fields."""
        schema = TransitionSchema(
            name="specify",
            from_state="Assessed",
            to_state="Specified",
        )
        assert schema.name == "specify"
        assert schema.from_state == "Assessed"
        assert schema.to_state == "Specified"
        assert schema.via == "specify"  # Defaults to name
        assert schema.validation == ValidationMode.NONE
        assert schema.input_artifacts == []
        assert schema.output_artifacts == []

    def test_transition_creation_full(self):
        """AC1: Transition with all fields including artifacts and validation."""
        schema = TransitionSchema(
            name="specify",
            from_state="Assessed",
            to_state="Specified",
            via="specify",
            input_artifacts=[
                Artifact(type="assessment_report", path="./docs/assess/{feature}.md"),
            ],
            output_artifacts=[
                Artifact(type="prd", path="./docs/prd/{feature}.md"),
            ],
            validation=ValidationMode.KEYWORD,
            validation_keyword="PRD_APPROVED",
            description="Create PRD from assessment",
        )
        assert len(schema.input_artifacts) == 1
        assert len(schema.output_artifacts) == 1
        assert schema.validation == ValidationMode.KEYWORD
        assert schema.validation_keyword == "PRD_APPROVED"

    def test_transition_empty_name_raises(self):
        """Transition with empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            TransitionSchema(name="", from_state="A", to_state="B")

    def test_transition_empty_from_state_raises(self):
        """Transition with empty from_state raises ValueError."""
        with pytest.raises(ValueError, match="from_state cannot be empty"):
            TransitionSchema(name="test", from_state="", to_state="B")

    def test_transition_keyword_without_keyword_raises(self):
        """KEYWORD validation without keyword raises ValueError."""
        with pytest.raises(ValueError, match="requires validation_keyword"):
            TransitionSchema(
                name="test",
                from_state="A",
                to_state="B",
                validation=ValidationMode.KEYWORD,
            )

    def test_transition_from_states_list(self):
        """from_states property handles list of states."""
        schema = TransitionSchema(
            name="plan",
            from_state=["Specified", "Researched"],
            to_state="Planned",
        )
        assert schema.from_states == ["Specified", "Researched"]

    def test_transition_from_states_single(self):
        """from_states property handles single state."""
        schema = TransitionSchema(
            name="specify",
            from_state="Assessed",
            to_state="Specified",
        )
        assert schema.from_states == ["Assessed"]

    def test_transition_get_required_artifacts(self):
        """Get only required input/output artifacts."""
        schema = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            input_artifacts=[
                Artifact(type="required", required=True),
                Artifact(type="optional", required=False),
            ],
            output_artifacts=[
                Artifact(type="required_out", required=True),
                Artifact(type="optional_out", required=False),
            ],
        )
        required_in = schema.get_required_input_artifacts()
        required_out = schema.get_required_output_artifacts()

        assert len(required_in) == 1
        assert required_in[0].type == "required"
        assert len(required_out) == 1
        assert required_out[0].type == "required_out"

    def test_transition_get_validation_string(self):
        """Get validation mode as string."""
        schema_none = TransitionSchema(
            name="test", from_state="A", to_state="B", validation=ValidationMode.NONE
        )
        assert schema_none.get_validation_string() == "NONE"

        schema_keyword = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.KEYWORD,
            validation_keyword="APPROVED",
        )
        assert schema_keyword.get_validation_string() == 'KEYWORD["APPROVED"]'

    def test_transition_from_dict(self):
        """Transition can be created from dictionary."""
        data = {
            "name": "specify",
            "from": "Assessed",
            "to": "Specified",
            "via": "specify",
            "input_artifacts": [
                {"type": "assessment_report", "path": "./docs/assess/{feature}.md"}
            ],
            "output_artifacts": [{"type": "prd", "path": "./docs/prd/{feature}.md"}],
            "validation": 'KEYWORD["PRD_APPROVED"]',
            "description": "Create PRD",
        }
        schema = TransitionSchema.from_dict(data)
        assert schema.name == "specify"
        assert schema.from_state == "Assessed"
        assert schema.to_state == "Specified"
        assert len(schema.input_artifacts) == 1
        assert schema.validation == ValidationMode.KEYWORD
        assert schema.validation_keyword == "PRD_APPROVED"

    def test_transition_to_dict(self):
        """Transition can be serialized to dictionary."""
        schema = TransitionSchema(
            name="specify",
            from_state="Assessed",
            to_state="Specified",
            via="specify",
            input_artifacts=[Artifact(type="assessment_report")],
            output_artifacts=[Artifact(type="prd", path="./docs/prd/{feature}.md")],
            validation=ValidationMode.NONE,
            description="Create PRD",
        )
        data = schema.to_dict()
        assert data["name"] == "specify"
        assert data["from"] == "Assessed"
        assert data["to"] == "Specified"
        assert data["validation"] == "NONE"
        assert len(data["input_artifacts"]) == 1
        assert len(data["output_artifacts"]) == 1


class TestWorkflowTransitions:
    """Tests for standard WORKFLOW_TRANSITIONS."""

    def test_all_transitions_defined(self):
        """AC2: All 7+ workflow transitions are defined."""
        # Should have: assess, specify, research, plan, implement, validate, operate, complete
        assert len(WORKFLOW_TRANSITIONS) >= 7
        names = [t.name for t in WORKFLOW_TRANSITIONS]
        assert "assess" in names
        assert "specify" in names
        assert "research" in names
        assert "plan" in names
        assert "implement" in names
        assert "validate" in names
        assert "operate" in names

    def test_all_transitions_have_validation_none(self):
        """AC4: All transitions default to validation: NONE."""
        for transition in WORKFLOW_TRANSITIONS:
            assert transition.validation == ValidationMode.NONE, (
                f"Transition '{transition.name}' should have NONE validation"
            )

    def test_assess_transition(self):
        """AC2: Assess transition is properly defined."""
        assess = get_transition_by_name("assess")
        assert assess is not None
        assert assess.from_state == "To Do"
        assert assess.to_state == "Assessed"
        assert len(assess.input_artifacts) == 0  # Entry point
        assert len(assess.output_artifacts) >= 1
        assert any(a.type == "assessment_report" for a in assess.output_artifacts)

    def test_specify_transition(self):
        """AC2: Specify transition is properly defined."""
        specify = get_transition_by_name("specify")
        assert specify is not None
        assert specify.from_state == "Assessed"
        assert specify.to_state == "Specified"
        assert any(a.type == "prd" for a in specify.output_artifacts)
        assert any(a.type == "backlog_tasks" for a in specify.output_artifacts)

    def test_plan_transition_multiple_from_states(self):
        """AC2: Plan transition accepts multiple from states."""
        plan = get_transition_by_name("plan")
        assert plan is not None
        assert "Specified" in plan.from_states
        assert "Researched" in plan.from_states
        assert any(a.type == "adr" for a in plan.output_artifacts)

    def test_implement_transition(self):
        """AC2: Implement transition is properly defined."""
        implement = get_transition_by_name("implement")
        assert implement is not None
        assert implement.from_state == "Planned"
        assert implement.to_state == "In Implementation"
        assert any(a.type == "tests" for a in implement.output_artifacts)
        assert any(a.type == "ac_coverage" for a in implement.output_artifacts)

    def test_all_transitions_have_required_fields(self):
        """AC6: All transitions have name, from, to, validation."""
        for transition in WORKFLOW_TRANSITIONS:
            assert transition.name, "Transition missing name"
            assert transition.from_state, (
                f"Transition {transition.name} missing from_state"
            )
            assert transition.to_state, f"Transition {transition.name} missing to_state"
            assert transition.validation is not None, (
                f"Transition {transition.name} missing validation"
            )


class TestValidateTransitionSchema:
    """Tests for validate_transition_schema function."""

    def test_valid_transition_no_errors(self):
        """AC6: Valid transition passes validation."""
        schema = TransitionSchema(
            name="test",
            from_state="A",
            to_state="B",
            validation=ValidationMode.NONE,
        )
        errors = validate_transition_schema(schema)
        assert len(errors) == 0

    def test_empty_name_returns_error(self):
        """AC6: Empty name returns validation error."""
        # Can't create schema with empty name, so test would fail at creation
        # This validates that our schema enforces the constraint
        with pytest.raises(ValueError):
            TransitionSchema(name="", from_state="A", to_state="B")


class TestGetTransitionByName:
    """Tests for get_transition_by_name function."""

    def test_get_existing_transition(self):
        """Get transition by name returns correct transition."""
        specify = get_transition_by_name("specify")
        assert specify is not None
        assert specify.name == "specify"

    def test_get_nonexistent_transition(self):
        """Get nonexistent transition returns None."""
        result = get_transition_by_name("nonexistent")
        assert result is None


class TestGetTransitionsFromState:
    """Tests for get_transitions_from_state function."""

    def test_get_transitions_from_to_do(self):
        """Get transitions from 'To Do' state."""
        transitions = get_transitions_from_state("To Do")
        assert len(transitions) >= 1
        names = [t.name for t in transitions]
        assert "assess" in names

    def test_get_transitions_from_specified(self):
        """Get transitions from 'Specified' state."""
        transitions = get_transitions_from_state("Specified")
        names = [t.name for t in transitions]
        # Should include research (optional) and plan
        assert "research" in names
        assert "plan" in names

    def test_get_transitions_from_unknown_state(self):
        """Get transitions from unknown state returns empty list."""
        transitions = get_transitions_from_state("Unknown")
        assert transitions == []
