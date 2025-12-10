"""Unit tests for jpspec_workflow.schema.json validation."""

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft7Validator, ValidationError, validate

# Path to the schema file
SCHEMA_PATH = Path(__file__).parent.parent / "memory" / "jpspec_workflow.schema.json"


@pytest.fixture
def schema():
    """Load the JSON schema."""
    with open(SCHEMA_PATH) as f:
        return json.load(f)


@pytest.fixture
def valid_config():
    """A minimal valid workflow configuration."""
    return {
        "version": "1.0",
        "states": [
            {"name": "Specified", "description": "Feature specification created"},
            {"name": "Planned", "description": "Technical plan created"},
        ],
        "workflows": {
            "specify": {
                "command": "/jpspec:specify",
                "agents": ["product-requirements-manager"],
                "input_states": ["To Do"],
                "output_state": "Specified",
                "description": "Create feature specification",
                "optional": False,
            },
            "plan": {
                "command": "/jpspec:plan",
                "agents": ["software-architect"],
                "input_states": ["Specified"],
                "output_state": "Planned",
            },
        },
        "transitions": [
            {"from": "To Do", "to": "Specified", "via": "specify"},
            {"from": "Specified", "to": "Planned", "via": "plan"},
        ],
    }


@pytest.fixture
def full_config():
    """A complete workflow configuration matching WORKFLOW_DESIGN_SPEC.md."""
    return {
        "version": "1.0",
        "description": "Default JP Spec Kit specification-driven development workflow",
        "states": [
            {"name": "Specified", "description": "Feature specification created"},
            {"name": "Researched", "description": "Business viability researched"},
            {"name": "Planned", "description": "Technical plan created"},
            {"name": "In Implementation", "description": "Feature being implemented"},
            {"name": "Validated", "description": "Feature validated"},
            {"name": "Deployed", "description": "Feature deployed"},
        ],
        "workflows": {
            "specify": {
                "command": "/jpspec:specify",
                "agents": ["product-requirements-manager"],
                "input_states": ["To Do"],
                "output_state": "Specified",
                "description": "Create feature specification",
                "optional": False,
            },
            "research": {
                "command": "/jpspec:research",
                "agents": ["researcher", "business-validator"],
                "input_states": ["Specified"],
                "output_state": "Researched",
                "description": "Validate business viability",
                "optional": False,
            },
            "plan": {
                "command": "/jpspec:plan",
                "agents": ["software-architect", "platform-engineer"],
                "input_states": ["Researched"],
                "output_state": "Planned",
                "description": "Create technical plan",
                "optional": False,
            },
            "implement": {
                "command": "/jpspec:implement",
                "agents": ["frontend-engineer", "backend-engineer", "code-reviewer"],
                "input_states": ["Planned"],
                "output_state": "In Implementation",
                "description": "Implement feature",
                "optional": False,
            },
            "validate": {
                "command": "/jpspec:validate",
                "agents": [
                    "quality-guardian",
                    "secure-by-design-engineer",
                    "tech-writer",
                    "release-manager",
                ],
                "input_states": ["In Implementation"],
                "output_state": "Validated",
                "description": "Validate implementation",
                "optional": False,
            },
            "operate": {
                "command": "/jpspec:operate",
                "agents": ["sre-agent"],
                "input_states": ["Validated"],
                "output_state": "Deployed",
                "description": "Deploy to production",
                "optional": True,
            },
        },
        "transitions": [
            {"from": "To Do", "to": "Specified", "via": "specify"},
            {"from": "Specified", "to": "Researched", "via": "research"},
            {"from": "Researched", "to": "Planned", "via": "plan"},
            {"from": "Planned", "to": "In Implementation", "via": "implement"},
            {"from": "In Implementation", "to": "Validated", "via": "validate"},
            {"from": "Validated", "to": "Deployed", "via": "operate"},
            {"from": "Deployed", "to": "Done", "via": "completion"},
        ],
        "agent_loops": {
            "inner_loop": [
                "product-requirements-manager",
                "software-architect",
                "platform-engineer",
                "researcher",
                "business-validator",
                "frontend-engineer",
                "backend-engineer",
                "quality-guardian",
                "secure-by-design-engineer",
                "tech-writer",
            ],
            "outer_loop": ["sre-agent", "release-manager"],
        },
    }


class TestSchemaStructure:
    """Test that the schema itself is valid."""

    def test_schema_is_valid_json(self, schema):
        """Test schema file is valid JSON."""
        assert schema is not None
        assert "$schema" in schema

    def test_schema_is_valid_draft7(self, schema):
        """Test schema conforms to JSON Schema Draft-07."""
        # This will raise if the schema itself is invalid
        Draft7Validator.check_schema(schema)

    def test_schema_has_required_defs(self, schema):
        """Test schema has all required definitions."""
        assert "$defs" in schema
        defs = schema["$defs"]
        assert "state" in defs
        assert "workflow" in defs
        assert "transition" in defs

    def test_schema_has_required_properties(self, schema):
        """Test schema defines all required top-level properties."""
        props = schema["properties"]
        assert "version" in props
        assert "states" in props
        assert "workflows" in props
        assert "transitions" in props
        assert "agent_loops" in props


class TestValidConfig:
    """Test valid configurations pass validation."""

    def test_minimal_valid_config(self, schema, valid_config):
        """Test minimal valid config passes validation."""
        validate(instance=valid_config, schema=schema)

    def test_full_valid_config(self, schema, full_config):
        """Test complete config from design spec passes validation."""
        validate(instance=full_config, schema=schema)

    def test_config_without_agent_loops(self, schema, valid_config):
        """Test config without optional agent_loops passes."""
        # agent_loops is not in required
        assert "agent_loops" not in valid_config
        validate(instance=valid_config, schema=schema)

    def test_config_with_description(self, schema, valid_config):
        """Test config with optional description passes."""
        valid_config["description"] = "Test workflow"
        validate(instance=valid_config, schema=schema)


class TestVersionValidation:
    """Test version field validation."""

    def test_valid_version_1_0(self, schema, valid_config):
        """Test version '1.0' is valid."""
        valid_config["version"] = "1.0"
        validate(instance=valid_config, schema=schema)

    def test_valid_version_2_0(self, schema, valid_config):
        """Test version '2.0' is valid."""
        valid_config["version"] = "2.0"
        validate(instance=valid_config, schema=schema)

    def test_valid_version_10_5(self, schema, valid_config):
        """Test version '10.5' is valid."""
        valid_config["version"] = "10.5"
        validate(instance=valid_config, schema=schema)

    def test_invalid_version_no_dot(self, schema, valid_config):
        """Test version without dot fails."""
        valid_config["version"] = "10"
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "version" in str(exc_info.value.absolute_path) or "pattern" in str(
            exc_info.value.message
        )

    def test_invalid_version_three_parts(self, schema, valid_config):
        """Test version with three parts fails."""
        valid_config["version"] = "1.0.0"
        with pytest.raises(ValidationError):
            validate(instance=valid_config, schema=schema)

    def test_invalid_version_text(self, schema, valid_config):
        """Test version with text fails."""
        valid_config["version"] = "v1.0"
        with pytest.raises(ValidationError):
            validate(instance=valid_config, schema=schema)

    def test_missing_version(self, schema, valid_config):
        """Test missing version fails."""
        del valid_config["version"]
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "version" in str(exc_info.value.message)


class TestStatesValidation:
    """Test states field validation."""

    def test_valid_states_array(self, schema, valid_config):
        """Test valid states array passes."""
        validate(instance=valid_config, schema=schema)

    def test_empty_states_fails(self, schema, valid_config):
        """Test empty states array fails."""
        valid_config["states"] = []
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        # Error message varies by jsonschema version
        msg = str(exc_info.value.message).lower()
        assert "too short" in msg or "non-empty" in msg or "minitems" in msg

    def test_missing_states_fails(self, schema, valid_config):
        """Test missing states fails."""
        del valid_config["states"]
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "states" in str(exc_info.value.message)

    def test_state_without_name_fails(self, schema, valid_config):
        """Test state without name fails."""
        valid_config["states"] = [{"description": "Missing name"}]
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "name" in str(exc_info.value.message)

    def test_state_with_empty_name_fails(self, schema, valid_config):
        """Test state with empty name fails."""
        valid_config["states"] = [{"name": ""}]
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        # Error message varies by jsonschema version
        msg = str(exc_info.value.message).lower()
        assert "minlength" in msg or "non-empty" in msg or "too short" in msg

    def test_state_extra_property_fails(self, schema, valid_config):
        """Test state with extra property fails (additionalProperties: false)."""
        valid_config["states"] = [
            {"name": "Test", "description": "Valid", "extra": "invalid"}
        ]
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "additional" in str(exc_info.value.message).lower()


class TestWorkflowsValidation:
    """Test workflows field validation."""

    def test_valid_workflow(self, schema, valid_config):
        """Test valid workflow passes."""
        validate(instance=valid_config, schema=schema)

    def test_empty_workflows_fails(self, schema, valid_config):
        """Test empty workflows object fails."""
        valid_config["workflows"] = {}
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        # Error message varies by jsonschema version
        msg = str(exc_info.value.message).lower()
        assert "minproperties" in msg or "non-empty" in msg or "too short" in msg

    def test_workflow_invalid_name_uppercase(self, schema, valid_config):
        """Test workflow name with uppercase fails."""
        valid_config["workflows"]["Specify"] = valid_config["workflows"].pop("specify")
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        # Error message varies by jsonschema version
        msg = str(exc_info.value.message).lower()
        assert "pattern" in msg or "match" in msg or "does not match" in msg

    def test_workflow_invalid_name_starts_with_number(self, schema, valid_config):
        """Test workflow name starting with number fails."""
        valid_config["workflows"]["1specify"] = valid_config["workflows"].pop("specify")
        with pytest.raises(ValidationError):
            validate(instance=valid_config, schema=schema)

    def test_workflow_missing_command_fails(self, schema, valid_config):
        """Test workflow without command fails."""
        del valid_config["workflows"]["specify"]["command"]
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "command" in str(exc_info.value.message)

    def test_workflow_missing_agents_fails(self, schema, valid_config):
        """Test workflow without agents fails."""
        del valid_config["workflows"]["specify"]["agents"]
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "agents" in str(exc_info.value.message)

    def test_workflow_missing_input_states_fails(self, schema, valid_config):
        """Test workflow without input_states fails."""
        del valid_config["workflows"]["specify"]["input_states"]
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "input_states" in str(exc_info.value.message)

    def test_workflow_missing_output_state_fails(self, schema, valid_config):
        """Test workflow without output_state fails."""
        del valid_config["workflows"]["specify"]["output_state"]
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "output_state" in str(exc_info.value.message)

    def test_workflow_empty_agents_fails(self, schema, valid_config):
        """Test workflow with empty agents array fails."""
        valid_config["workflows"]["specify"]["agents"] = []
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        # Error message varies by jsonschema version
        msg = str(exc_info.value.message).lower()
        assert "minitems" in msg or "non-empty" in msg or "too short" in msg

    def test_workflow_empty_input_states_fails(self, schema, valid_config):
        """Test workflow with empty input_states array fails."""
        valid_config["workflows"]["specify"]["input_states"] = []
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        # Error message varies by jsonschema version
        msg = str(exc_info.value.message).lower()
        assert "minitems" in msg or "non-empty" in msg or "too short" in msg


class TestCommandPatternValidation:
    """Test /jpspec command pattern validation."""

    def test_valid_command_specify(self, schema, valid_config):
        """Test /jpspec:specify is valid."""
        valid_config["workflows"]["specify"]["command"] = "/jpspec:specify"
        validate(instance=valid_config, schema=schema)

    def test_valid_command_implement(self, schema, valid_config):
        """Test /jpspec:implement is valid."""
        valid_config["workflows"]["specify"]["command"] = "/jpspec:implement"
        validate(instance=valid_config, schema=schema)

    def test_valid_command_with_underscore(self, schema, valid_config):
        """Test /jpspec:security_audit is valid."""
        valid_config["workflows"]["specify"]["command"] = "/jpspec:security_audit"
        validate(instance=valid_config, schema=schema)

    def test_invalid_command_no_slash(self, schema, valid_config):
        """Test command without leading slash fails."""
        valid_config["workflows"]["specify"]["command"] = "jpspec:specify"
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        # Error message varies by jsonschema version
        msg = str(exc_info.value.message).lower()
        assert "pattern" in msg or "match" in msg

    def test_invalid_command_wrong_prefix(self, schema, valid_config):
        """Test command with wrong prefix fails."""
        valid_config["workflows"]["specify"]["command"] = "/speckit:specify"
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        # Error message varies by jsonschema version
        msg = str(exc_info.value.message).lower()
        assert "pattern" in msg or "match" in msg

    def test_invalid_command_uppercase(self, schema, valid_config):
        """Test command with uppercase fails."""
        valid_config["workflows"]["specify"]["command"] = "/jpspec:Specify"
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        # Error message varies by jsonschema version
        msg = str(exc_info.value.message).lower()
        assert "pattern" in msg or "match" in msg

    def test_invalid_command_empty_action(self, schema, valid_config):
        """Test command without action fails."""
        valid_config["workflows"]["specify"]["command"] = "/jpspec:"
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        # Error message varies by jsonschema version
        msg = str(exc_info.value.message).lower()
        assert "pattern" in msg or "match" in msg


class TestTransitionsValidation:
    """Test transitions field validation."""

    def test_valid_transitions(self, schema, valid_config):
        """Test valid transitions pass."""
        validate(instance=valid_config, schema=schema)

    def test_empty_transitions_fails(self, schema, valid_config):
        """Test empty transitions array fails."""
        valid_config["transitions"] = []
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        # Error message varies by jsonschema version
        msg = str(exc_info.value.message).lower()
        assert "minitems" in msg or "non-empty" in msg or "too short" in msg

    def test_missing_transitions_fails(self, schema, valid_config):
        """Test missing transitions fails."""
        del valid_config["transitions"]
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "transitions" in str(exc_info.value.message)

    def test_transition_missing_from_fails(self, schema, valid_config):
        """Test transition without from fails."""
        valid_config["transitions"] = [{"to": "Done", "via": "complete"}]
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "from" in str(exc_info.value.message)

    def test_transition_missing_to_fails(self, schema, valid_config):
        """Test transition without to fails."""
        valid_config["transitions"] = [{"from": "To Do", "via": "complete"}]
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "to" in str(exc_info.value.message)

    def test_transition_missing_via_fails(self, schema, valid_config):
        """Test transition without via fails."""
        valid_config["transitions"] = [{"from": "To Do", "to": "Done"}]
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "via" in str(exc_info.value.message)

    def test_transition_empty_from_fails(self, schema, valid_config):
        """Test transition with empty from fails."""
        valid_config["transitions"] = [{"from": "", "to": "Done", "via": "complete"}]
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        # Error message varies by jsonschema version
        msg = str(exc_info.value.message).lower()
        assert "minlength" in msg or "non-empty" in msg or "too short" in msg


class TestAgentLoopsValidation:
    """Test agent_loops field validation."""

    def test_valid_agent_loops(self, schema, full_config):
        """Test valid agent_loops passes."""
        validate(instance=full_config, schema=schema)

    def test_agent_loops_inner_only(self, schema, valid_config):
        """Test agent_loops with only inner_loop passes."""
        valid_config["agent_loops"] = {"inner_loop": ["engineer"]}
        validate(instance=valid_config, schema=schema)

    def test_agent_loops_outer_only(self, schema, valid_config):
        """Test agent_loops with only outer_loop passes."""
        valid_config["agent_loops"] = {"outer_loop": ["sre"]}
        validate(instance=valid_config, schema=schema)

    def test_agent_loops_extra_property_fails(self, schema, valid_config):
        """Test agent_loops with extra property fails."""
        valid_config["agent_loops"] = {
            "inner_loop": ["engineer"],
            "middle_loop": ["invalid"],
        }
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "additional" in str(exc_info.value.message).lower()

    def test_agent_loops_empty_agent_name_fails(self, schema, valid_config):
        """Test agent_loops with empty agent name fails."""
        valid_config["agent_loops"] = {"inner_loop": [""]}
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        # Error message varies by jsonschema version
        msg = str(exc_info.value.message).lower()
        assert "minlength" in msg or "non-empty" in msg or "too short" in msg


class TestAdditionalPropertiesRestriction:
    """Test that extra properties are rejected at all levels."""

    def test_extra_top_level_property_fails(self, schema, valid_config):
        """Test extra property at top level fails."""
        valid_config["extra_field"] = "invalid"
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "additional" in str(exc_info.value.message).lower()

    def test_extra_workflow_property_fails(self, schema, valid_config):
        """Test extra property in workflow fails."""
        valid_config["workflows"]["specify"]["extra"] = "invalid"
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "additional" in str(exc_info.value.message).lower()

    def test_extra_transition_property_fails(self, schema, valid_config):
        """Test extra property in transition fails."""
        valid_config["transitions"][0]["extra"] = "invalid"
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "additional" in str(exc_info.value.message).lower()


class TestYAMLCompatibility:
    """Test schema works with YAML-parsed configurations."""

    def test_yaml_config_validates(self, schema):
        """Test YAML configuration validates correctly."""
        yaml_content = """
version: "1.0"
description: "Test workflow from YAML"
states:
  - name: Specified
    description: Feature spec created
workflows:
  specify:
    command: "/jpspec:specify"
    agents:
      - pm
    input_states:
      - To Do
    output_state: Specified
transitions:
  - from: To Do
    to: Specified
    via: specify
"""
        config = yaml.safe_load(yaml_content)
        validate(instance=config, schema=schema)

    def test_yaml_multiline_description(self, schema):
        """Test YAML with multiline description validates."""
        yaml_content = """
version: "1.0"
description: |
  This is a multiline
  description for the workflow
states:
  - name: Done
workflows:
  complete:
    command: "/jpspec:complete"
    agents:
      - finisher
    input_states:
      - To Do
    output_state: Done
transitions:
  - from: To Do
    to: Done
    via: complete
"""
        config = yaml.safe_load(yaml_content)
        validate(instance=config, schema=schema)


class TestUniqueConstraints:
    """Test unique item constraints."""

    def test_duplicate_states_fails(self, schema, valid_config):
        """Test duplicate state names fail uniqueItems constraint."""
        valid_config["states"] = [
            {"name": "Specified"},
            {"name": "Specified"},  # Duplicate
        ]
        # Note: JSON Schema uniqueItems checks object equality, not just name
        # This test verifies that exact duplicates are rejected
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "unique" in str(exc_info.value.message).lower()

    def test_duplicate_agents_in_workflow_fails(self, schema, valid_config):
        """Test duplicate agents in workflow fail."""
        valid_config["workflows"]["specify"]["agents"] = ["pm", "pm"]  # Duplicate
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "unique" in str(exc_info.value.message).lower()

    def test_duplicate_input_states_fails(self, schema, valid_config):
        """Test duplicate input_states fail."""
        valid_config["workflows"]["specify"]["input_states"] = [
            "To Do",
            "To Do",
        ]  # Duplicate
        with pytest.raises(ValidationError) as exc_info:
            validate(instance=valid_config, schema=schema)
        assert "unique" in str(exc_info.value.message).lower()


class TestDefaultValues:
    """Test default value behavior."""

    def test_workflow_optional_defaults_to_false(self, schema, valid_config):
        """Test workflow without optional field defaults to false."""
        # Remove optional field
        if "optional" in valid_config["workflows"]["specify"]:
            del valid_config["workflows"]["specify"]["optional"]
        # Should still validate
        validate(instance=valid_config, schema=schema)
        # Note: JSON Schema default doesn't modify the document,
        # it's just for documentation and some validators


class TestSchemaValidationTool:
    """Test the schema can be used programmatically."""

    def test_validator_all_errors(self, schema, valid_config):
        """Test validator can collect all errors at once."""
        # Create an invalid config with multiple errors
        invalid_config = {
            "version": "invalid",  # Error 1
            "states": [],  # Error 2
            "workflows": {},  # Error 3
            "transitions": [],  # Error 4
        }

        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(invalid_config))

        # Should have multiple errors
        assert len(errors) >= 4

    def test_validator_error_paths(self, schema):
        """Test validator provides useful error paths."""
        invalid_config = {
            "version": "1.0",
            "states": [{"name": "Test"}],
            "workflows": {
                "bad_workflow": {
                    "command": "invalid",  # Missing /jpspec: prefix
                    "agents": ["pm"],
                    "input_states": ["To Do"],
                    "output_state": "Done",
                }
            },
            "transitions": [{"from": "To Do", "to": "Done", "via": "bad_workflow"}],
        }

        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(invalid_config))

        # Find the command error
        command_errors = [
            e
            for e in errors
            if "command" in str(e.absolute_path) or "pattern" in e.message
        ]
        assert len(command_errors) > 0
