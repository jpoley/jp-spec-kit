"""Tests for WorkflowConfig class.

Tests cover:
- Loading valid configuration
- Handling missing files
- Handling invalid YAML
- Schema validation
- Query methods (get_agents, get_next_state, etc.)
- Caching behavior
- Reload functionality
- Error messages
"""

import json
from pathlib import Path

import pytest
import yaml

from specify_cli.workflow import (
    WorkflowConfig,
    WorkflowConfigError,
    WorkflowConfigNotFoundError,
    WorkflowConfigValidationError,
    WorkflowNotFoundError,
    WorkflowStateError,
)


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures" / "workflow"


@pytest.fixture
def valid_config_path(fixtures_dir: Path) -> Path:
    """Return path to valid config fixture."""
    return fixtures_dir / "valid_config.yml"


@pytest.fixture
def minimal_config_path(fixtures_dir: Path) -> Path:
    """Return path to minimal valid config fixture."""
    return fixtures_dir / "minimal_config.yml"


@pytest.fixture
def invalid_yaml_path(fixtures_dir: Path) -> Path:
    """Return path to invalid YAML fixture."""
    return fixtures_dir / "invalid_yaml.yml"


@pytest.fixture
def missing_version_path(fixtures_dir: Path) -> Path:
    """Return path to config missing version field."""
    return fixtures_dir / "missing_version.yml"


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear WorkflowConfig cache before and after each test."""
    WorkflowConfig.clear_cache()
    yield
    WorkflowConfig.clear_cache()


@pytest.fixture
def schema_path(tmp_path: Path) -> Path:
    """Create a test schema file."""
    schema = {
        "$schema": "https://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["version", "states", "workflows", "transitions"],
        "properties": {
            "version": {"type": "string", "pattern": "^\\d+\\.\\d+$"},
            "description": {"type": "string"},
            "states": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                    },
                },
            },
            "workflows": {
                "type": "object",
                "minProperties": 1,
                "additionalProperties": {
                    "type": "object",
                    "required": ["command", "agents", "input_states", "output_state"],
                    "properties": {
                        "command": {"type": "string"},
                        "agents": {"type": "array", "items": {"type": "string"}},
                        "input_states": {"type": "array", "items": {"type": "string"}},
                        "output_state": {"type": "string"},
                        "description": {"type": "string"},
                        "optional": {"type": "boolean"},
                    },
                },
            },
            "transitions": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["from", "to", "via"],
                    "properties": {
                        "from": {"type": "string"},
                        "to": {"type": "string"},
                        "via": {"type": "string"},
                    },
                },
            },
            "agent_loops": {
                "type": "object",
                "properties": {
                    "inner_loop": {"type": "array", "items": {"type": "string"}},
                    "outer_loop": {"type": "array", "items": {"type": "string"}},
                },
            },
        },
    }
    schema_file = tmp_path / "memory" / "flowspec_workflow.schema.json"
    schema_file.parent.mkdir(parents=True, exist_ok=True)
    with open(schema_file, "w") as f:
        json.dump(schema, f)
    return schema_file


class TestWorkflowConfigLoading:
    """Tests for config loading functionality."""

    def test_load_valid_config(self, valid_config_path: Path):
        """Test loading a valid configuration file."""
        config = WorkflowConfig.load(valid_config_path, validate=False)

        assert config is not None
        assert config.version == "1.0"
        assert config.description == "Test workflow configuration"
        assert len(config.states) == 3
        assert len(config.workflows) == 3

    def test_load_minimal_config(self, minimal_config_path: Path):
        """Test loading a minimal valid configuration."""
        config = WorkflowConfig.load(minimal_config_path, validate=False)

        assert config.version == "1.0"
        assert len(config.states) == 1
        assert len(config.workflows) == 1

    def test_load_nonexistent_file_raises_error(self, tmp_path: Path):
        """Test that loading nonexistent file raises WorkflowConfigNotFoundError."""
        nonexistent = tmp_path / "nonexistent.yml"

        with pytest.raises(WorkflowConfigNotFoundError) as exc_info:
            WorkflowConfig.load(nonexistent)

        assert str(nonexistent) in str(exc_info.value)
        assert exc_info.value.path == str(nonexistent)

    def test_load_invalid_yaml_raises_error(self, invalid_yaml_path: Path):
        """Test that invalid YAML raises WorkflowConfigError."""
        with pytest.raises(WorkflowConfigError) as exc_info:
            WorkflowConfig.load(invalid_yaml_path, validate=False)

        assert "Failed to parse YAML" in str(exc_info.value)

    def test_load_with_schema_validation(
        self, valid_config_path: Path, schema_path: Path
    ):
        """Test loading config with schema validation."""
        config = WorkflowConfig.load(
            valid_config_path, schema_path=schema_path, validate=True
        )

        assert config is not None
        assert config.version == "1.0"

    def test_load_missing_version_fails_validation(
        self, missing_version_path: Path, schema_path: Path
    ):
        """Test that missing required field fails validation."""
        with pytest.raises(WorkflowConfigValidationError) as exc_info:
            WorkflowConfig.load(
                missing_version_path, schema_path=schema_path, validate=True
            )

        assert "version" in str(exc_info.value).lower()
        assert len(exc_info.value.errors) > 0

    def test_load_skip_validation(self, missing_version_path: Path):
        """Test that validation can be skipped."""
        # Should not raise even with missing required fields
        config = WorkflowConfig.load(missing_version_path, validate=False)
        assert config is not None

    def test_load_from_cwd(self, tmp_path: Path, monkeypatch):
        """Test loading config from current working directory."""
        # Create config in tmp_path
        config_file = tmp_path / "flowspec_workflow.yml"
        config_data = {
            "version": "1.0",
            "states": [{"name": "Test"}],
            "workflows": {
                "test": {
                    "command": "/flow:test",
                    "agents": ["agent"],
                    "input_states": ["To Do"],
                    "output_state": "Test",
                }
            },
            "transitions": [{"from": "To Do", "to": "Test", "via": "test"}],
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Change to tmp_path
        monkeypatch.chdir(tmp_path)

        config = WorkflowConfig.load(validate=False)
        assert config.version == "1.0"


class TestWorkflowConfigCaching:
    """Tests for config caching functionality."""

    def test_caching_returns_same_instance(self, valid_config_path: Path):
        """Test that caching returns the same instance."""
        config1 = WorkflowConfig.load(valid_config_path, validate=False)
        config2 = WorkflowConfig.load(valid_config_path, validate=False)

        assert config1 is config2

    def test_get_cached_returns_instance(self, valid_config_path: Path):
        """Test get_cached returns loaded instance."""
        assert WorkflowConfig.get_cached() is None

        config = WorkflowConfig.load(valid_config_path, validate=False)
        cached = WorkflowConfig.get_cached()

        assert cached is config

    def test_clear_cache_removes_instance(self, valid_config_path: Path):
        """Test clear_cache removes cached instance."""
        WorkflowConfig.load(valid_config_path, validate=False)
        assert WorkflowConfig.get_cached() is not None

        WorkflowConfig.clear_cache()
        assert WorkflowConfig.get_cached() is None

    def test_cache_disabled_returns_new_instance(self, valid_config_path: Path):
        """Test that disabling cache returns new instances."""
        config1 = WorkflowConfig.load(valid_config_path, validate=False, cache=False)
        config2 = WorkflowConfig.load(valid_config_path, validate=False, cache=False)

        assert config1 is not config2

    def test_reload_clears_and_reloads(self, tmp_path: Path):
        """Test reload clears cache and reloads from file."""
        # Create initial config
        config_file = tmp_path / "flowspec_workflow.yml"
        initial_data = {
            "version": "1.0",
            "description": "Initial",
            "states": [{"name": "Test"}],
            "workflows": {
                "test": {
                    "command": "/flow:test",
                    "agents": ["agent"],
                    "input_states": ["To Do"],
                    "output_state": "Test",
                }
            },
            "transitions": [{"from": "To Do", "to": "Test", "via": "test"}],
        }
        with open(config_file, "w") as f:
            yaml.dump(initial_data, f)

        config = WorkflowConfig.load(config_file, validate=False)
        assert config.description == "Initial"

        # Modify file
        initial_data["description"] = "Modified"
        with open(config_file, "w") as f:
            yaml.dump(initial_data, f)

        # Reload
        new_config = config.reload()
        assert new_config.description == "Modified"
        assert new_config is not config

    def test_reload_without_path_raises_error(self):
        """Test reload without config path raises error."""
        config = WorkflowConfig({}, None)

        with pytest.raises(WorkflowConfigError) as exc_info:
            config.reload()

        assert "Cannot reload" in str(exc_info.value)


class TestWorkflowConfigQueries:
    """Tests for config query methods."""

    @pytest.fixture
    def config(self, valid_config_path: Path) -> WorkflowConfig:
        """Load config for query tests."""
        return WorkflowConfig.load(valid_config_path, validate=False)

    def test_get_agents(self, config: WorkflowConfig):
        """Test get_agents returns correct agents."""
        agents = config.get_agents("specify")
        assert agents == ["product-requirements-manager"]

        agents = config.get_agents("plan")
        assert agents == ["software-architect", "platform-engineer"]

    def test_get_agents_nonexistent_workflow(self, config: WorkflowConfig):
        """Test get_agents raises error for unknown workflow."""
        with pytest.raises(WorkflowNotFoundError) as exc_info:
            config.get_agents("nonexistent")

        assert exc_info.value.workflow == "nonexistent"
        assert "specify" in exc_info.value.valid_workflows

    def test_get_next_state(self, config: WorkflowConfig):
        """Test get_next_state returns correct state."""
        next_state = config.get_next_state("To Do", "specify")
        assert next_state == "Specified"

        next_state = config.get_next_state("Specified", "plan")
        assert next_state == "Planned"

    def test_get_next_state_invalid_input_state(self, config: WorkflowConfig):
        """Test get_next_state raises error for invalid input state."""
        with pytest.raises(WorkflowStateError) as exc_info:
            config.get_next_state("Planned", "specify")

        assert "To Do" in exc_info.value.valid_states

    def test_get_next_state_nonexistent_workflow(self, config: WorkflowConfig):
        """Test get_next_state raises error for unknown workflow."""
        with pytest.raises(WorkflowNotFoundError):
            config.get_next_state("To Do", "nonexistent")

    def test_get_input_states(self, config: WorkflowConfig):
        """Test get_input_states returns correct states."""
        input_states = config.get_input_states("specify")
        assert input_states == ["To Do"]

        input_states = config.get_input_states("plan")
        assert input_states == ["Specified"]

    def test_get_transitions(self, config: WorkflowConfig):
        """Test get_transitions returns all transitions."""
        transitions = config.get_transitions()

        assert len(transitions) == 4
        assert {"from": "To Do", "to": "Specified", "via": "specify"} in transitions
        assert {"from": "Specified", "to": "Planned", "via": "plan"} in transitions

    def test_get_valid_workflows(self, config: WorkflowConfig):
        """Test get_valid_workflows returns workflows for state."""
        workflows = config.get_valid_workflows("To Do")
        assert workflows == ["specify"]

        workflows = config.get_valid_workflows("Specified")
        assert workflows == ["plan"]

        workflows = config.get_valid_workflows("Planned")
        assert workflows == ["implement"]

    def test_get_valid_workflows_no_match(self, config: WorkflowConfig):
        """Test get_valid_workflows returns empty for unknown state."""
        workflows = config.get_valid_workflows("Unknown State")
        assert workflows == []

    def test_is_valid_transition(self, config: WorkflowConfig):
        """Test is_valid_transition checks transition validity."""
        assert config.is_valid_transition("To Do", "Specified") is True
        assert config.is_valid_transition("Specified", "Planned") is True
        assert config.is_valid_transition("To Do", "Planned") is False
        assert config.is_valid_transition("Unknown", "State") is False

    def test_get_workflow_for_transition(self, config: WorkflowConfig):
        """Test get_workflow_for_transition returns workflow name."""
        workflow = config.get_workflow_for_transition("To Do", "Specified")
        assert workflow == "specify"

        workflow = config.get_workflow_for_transition("Specified", "Planned")
        assert workflow == "plan"

        workflow = config.get_workflow_for_transition("To Do", "Planned")
        assert workflow is None

    def test_is_workflow_optional(self, config: WorkflowConfig):
        """Test is_workflow_optional returns correct value."""
        assert config.is_workflow_optional("specify") is False
        assert config.is_workflow_optional("plan") is False
        assert config.is_workflow_optional("implement") is True

    def test_get_agent_loop(self, config: WorkflowConfig):
        """Test get_agent_loop returns correct loop classification."""
        assert config.get_agent_loop("frontend-engineer") == "inner_loop"
        assert config.get_agent_loop("backend-engineer") == "inner_loop"
        assert config.get_agent_loop("product-requirements-manager") == "outer_loop"
        assert config.get_agent_loop("software-architect") == "outer_loop"
        assert config.get_agent_loop("sre-agent") == "outer_loop"
        assert config.get_agent_loop("unknown-agent") is None

    def test_get_agent_loops(self, config: WorkflowConfig):
        """Test get_agent_loops returns full agent loop dict."""
        loops = config.get_agent_loops()
        assert isinstance(loops, dict)
        assert "inner_loop" in loops
        assert "outer_loop" in loops
        assert isinstance(loops["inner_loop"], list)
        assert isinstance(loops["outer_loop"], list)
        assert "frontend-engineer" in loops["inner_loop"]
        assert "product-requirements-manager" in loops["outer_loop"]
        assert "sre-agent" in loops["outer_loop"]


class TestWorkflowConfigProperties:
    """Tests for config property accessors."""

    @pytest.fixture
    def config(self, valid_config_path: Path) -> WorkflowConfig:
        """Load config for property tests."""
        return WorkflowConfig.load(valid_config_path, validate=False)

    def test_states_property(self, config: WorkflowConfig):
        """Test states property returns state names."""
        states = config.states
        assert "Specified" in states
        assert "Planned" in states
        assert "In Implementation" in states

    def test_all_states_includes_todo_and_done(self, config: WorkflowConfig):
        """Test all_states includes To Do and Done."""
        all_states = config.all_states
        assert "To Do" in all_states
        assert "Done" in all_states
        assert all_states[0] == "To Do"
        assert all_states[-1] == "Done"

    def test_workflows_property(self, config: WorkflowConfig):
        """Test workflows property returns workflow definitions."""
        workflows = config.workflows
        assert "specify" in workflows
        assert "plan" in workflows
        assert "implement" in workflows

        specify = workflows["specify"]
        assert specify["command"] == "/flow:specify"
        assert specify["agents"] == ["product-requirements-manager"]

    def test_version_property(self, config: WorkflowConfig):
        """Test version property returns version string."""
        assert config.version == "1.0"

    def test_description_property(self, config: WorkflowConfig):
        """Test description property returns description."""
        assert config.description == "Test workflow configuration"

    def test_config_path_property(
        self, config: WorkflowConfig, valid_config_path: Path
    ):
        """Test config_path property returns path."""
        assert config.config_path == valid_config_path


class TestWorkflowConfigExceptions:
    """Tests for exception classes."""

    def test_workflow_config_error_str(self):
        """Test WorkflowConfigError string representation."""
        error = WorkflowConfigError("Test error", {"key": "value"})
        assert "Test error" in str(error)
        assert "key='value'" in str(error)

    def test_workflow_config_error_no_details(self):
        """Test WorkflowConfigError without details."""
        error = WorkflowConfigError("Test error")
        assert str(error) == "Test error"

    def test_workflow_config_not_found_error(self):
        """Test WorkflowConfigNotFoundError."""
        error = WorkflowConfigNotFoundError(
            "/path/to/config.yml", searched_paths=["/a", "/b"]
        )
        assert "/path/to/config.yml" in str(error)
        assert error.path == "/path/to/config.yml"
        assert error.searched_paths == ["/a", "/b"]

    def test_workflow_config_validation_error(self):
        """Test WorkflowConfigValidationError."""
        error = WorkflowConfigValidationError(
            "Validation failed", errors=["Error 1", "Error 2"]
        )
        assert "Validation failed" in str(error)
        assert "Error 1" in str(error)
        assert "Error 2" in str(error)
        assert error.errors == ["Error 1", "Error 2"]

    def test_workflow_state_error(self):
        """Test WorkflowStateError."""
        error = WorkflowStateError("InvalidState", valid_states=["To Do", "Done"])
        assert "InvalidState" in str(error)
        assert "To Do" in str(error)
        assert error.state == "InvalidState"
        assert error.valid_states == ["To Do", "Done"]

    def test_workflow_not_found_error(self):
        """Test WorkflowNotFoundError."""
        error = WorkflowNotFoundError(
            "nonexistent", valid_workflows=["specify", "plan"]
        )
        assert "nonexistent" in str(error)
        assert "specify" in str(error)
        assert error.workflow == "nonexistent"
        assert error.valid_workflows == ["specify", "plan"]


class TestWorkflowConfigEdgeCases:
    """Tests for edge cases and defensive coding."""

    def test_empty_agents_list(self, tmp_path: Path):
        """Test handling of empty agents list (should fail validation)."""
        config_file = tmp_path / "config.yml"
        config_data = {
            "version": "1.0",
            "states": [{"name": "Test"}],
            "workflows": {
                "test": {
                    "command": "/flow:test",
                    "agents": [],  # Empty list
                    "input_states": ["To Do"],
                    "output_state": "Test",
                }
            },
            "transitions": [{"from": "To Do", "to": "Test", "via": "test"}],
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Without validation, this should work
        config = WorkflowConfig.load(config_file, validate=False)
        assert config.get_agents("test") == []

    def test_missing_output_state(self, tmp_path: Path):
        """Test handling of missing output_state."""
        config_file = tmp_path / "config.yml"
        config_data = {
            "version": "1.0",
            "states": [{"name": "Test"}],
            "workflows": {
                "test": {
                    "command": "/flow:test",
                    "agents": ["agent"],
                    "input_states": ["To Do"],
                    # output_state missing
                }
            },
            "transitions": [{"from": "To Do", "to": "Test", "via": "test"}],
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = WorkflowConfig.load(config_file, validate=False)

        with pytest.raises(WorkflowConfigError) as exc_info:
            config.get_next_state("To Do", "test")

        assert "output_state" in str(exc_info.value)

    def test_init_with_invalid_type(self):
        """Test __init__ with non-dict data."""
        with pytest.raises(WorkflowConfigError) as exc_info:
            WorkflowConfig("not a dict", None)  # type: ignore

        assert "dictionary" in str(exc_info.value).lower()

    def test_empty_config(self, tmp_path: Path):
        """Test handling of empty YAML file."""
        config_file = tmp_path / "empty.yml"
        config_file.write_text("")

        with pytest.raises(WorkflowConfigError) as exc_info:
            WorkflowConfig.load(config_file, validate=False)

        assert "Invalid config format" in str(exc_info.value)

    def test_non_object_yaml(self, tmp_path: Path):
        """Test handling of non-object YAML."""
        config_file = tmp_path / "array.yml"
        config_file.write_text("- item1\n- item2\n")

        with pytest.raises(WorkflowConfigError) as exc_info:
            WorkflowConfig.load(config_file, validate=False)

        assert "expected object" in str(exc_info.value).lower()

    def test_state_as_string(self, tmp_path: Path):
        """Test handling of states defined as strings instead of objects."""
        config_file = tmp_path / "config.yml"
        config_data = {
            "version": "1.0",
            "states": ["Specified", "Planned"],  # Strings instead of objects
            "workflows": {
                "test": {
                    "command": "/flow:test",
                    "agents": ["agent"],
                    "input_states": ["To Do"],
                    "output_state": "Specified",
                }
            },
            "transitions": [{"from": "To Do", "to": "Specified", "via": "test"}],
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = WorkflowConfig.load(config_file, validate=False)
        assert "Specified" in config.states
        assert "Planned" in config.states

    def test_missing_agent_loops(self, tmp_path: Path):
        """Test handling of missing agent_loops section."""
        config_file = tmp_path / "config.yml"
        config_data = {
            "version": "1.0",
            "states": [{"name": "Test"}],
            "workflows": {
                "test": {
                    "command": "/flow:test",
                    "agents": ["agent"],
                    "input_states": ["To Do"],
                    "output_state": "Test",
                }
            },
            "transitions": [{"from": "To Do", "to": "Test", "via": "test"}],
            # No agent_loops
        }
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = WorkflowConfig.load(config_file, validate=False)
        assert config.get_agent_loop("agent") is None

    def test_transitions_returns_copy(self, valid_config_path: Path):
        """Test that get_transitions returns a copy."""
        config = WorkflowConfig.load(valid_config_path, validate=False)
        transitions1 = config.get_transitions()
        transitions2 = config.get_transitions()

        # Should be equal but not the same object
        assert transitions1 == transitions2
        assert transitions1 is not transitions2

        # Modifying one should not affect the other
        transitions1[0]["from"] = "Modified"
        assert transitions2[0]["from"] != "Modified"
