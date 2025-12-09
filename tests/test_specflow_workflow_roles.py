"""Tests for Specflow Workflow v2.0 with roles configuration.

Tests cover:
- Loading specflow_workflow.yml with roles section
- Validating role definitions (pm, arch, dev, sec, qa, ops, all)
- Verifying role properties (display_name, icon, commands, agents)
- Schema validation for roles section
- Backwards compatibility with jpspec_workflow.yml
"""

import json
from pathlib import Path

import pytest
import yaml

from specify_cli.workflow import (
    WorkflowConfig,
    WorkflowConfigValidationError,
)


@pytest.fixture
def specflow_config_path(tmp_path: Path) -> Path:
    """Create a test specflow_workflow.yml v2.0 with roles."""
    config_data = {
        "version": "2.0",
        "roles": {
            "primary": "dev",
            "show_all_commands": False,
            "definitions": {
                "pm": {
                    "display_name": "Product Manager",
                    "icon": "📋",
                    "commands": ["assess", "define", "discover"],
                    "agents": [
                        "@product-requirements-manager",
                        "@workflow-assessor",
                    ],
                },
                "arch": {
                    "display_name": "Architect",
                    "icon": "🏗️",
                    "commands": ["design", "decide", "model"],
                    "agents": ["@software-architect", "@platform-engineer"],
                },
                "dev": {
                    "display_name": "Developer",
                    "icon": "💻",
                    "commands": ["build", "debug", "refactor"],
                    "agents": [
                        "@frontend-engineer",
                        "@backend-engineer",
                        "@ai-ml-engineer",
                    ],
                },
                "sec": {
                    "display_name": "Security Engineer",
                    "icon": "🔒",
                    "commands": ["scan", "triage", "fix", "audit"],
                    "agents": ["@secure-by-design-engineer"],
                },
                "qa": {
                    "display_name": "QA Engineer",
                    "icon": "✅",
                    "commands": ["test", "verify", "review"],
                    "agents": ["@quality-guardian", "@release-manager"],
                },
                "ops": {
                    "display_name": "SRE/DevOps",
                    "icon": "🚀",
                    "commands": ["deploy", "monitor", "respond", "scale"],
                    "agents": ["@sre-agent"],
                },
                "all": {
                    "display_name": "All Roles",
                    "icon": "🌐",
                    "commands": [],
                    "agents": [],
                },
            },
        },
        "states": ["To Do", "In Progress", "Done"],
        "workflows": {
            "implement": {
                "command": "/jpspec:implement",
                "agents": ["backend-engineer"],
                "input_states": ["In Progress"],
                "output_state": "Done",
            }
        },
        "transitions": [
            {"from": "To Do", "to": "In Progress", "via": "implement"},
            {"from": "In Progress", "to": "Done", "via": "manual"},
        ],
    }

    config_path = tmp_path / "specflow_workflow.yml"
    with open(config_path, "w") as f:
        yaml.dump(config_data, f)

    return config_path


@pytest.fixture
def roles_schema_path(tmp_path: Path) -> Path:
    """Create a test schema with roles support."""
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "required": ["version", "states", "workflows", "transitions"],
        "properties": {
            "version": {"type": "string", "pattern": "^\\d+\\.\\d+$"},
            "roles": {
                "type": "object",
                "required": ["primary", "show_all_commands", "definitions"],
                "properties": {
                    "primary": {
                        "type": "string",
                        "enum": ["pm", "arch", "dev", "sec", "qa", "ops", "all"],
                    },
                    "show_all_commands": {"type": "boolean"},
                    "definitions": {
                        "type": "object",
                        "required": ["pm", "arch", "dev", "sec", "qa", "ops", "all"],
                        "additionalProperties": False,
                        "properties": {
                            role: {
                                "type": "object",
                                "required": [
                                    "display_name",
                                    "icon",
                                    "commands",
                                    "agents",
                                ],
                                "properties": {
                                    "display_name": {"type": "string"},
                                    "icon": {"type": "string"},
                                    "commands": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "agents": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "pattern": "^@[a-z][a-z0-9-]*$",
                                        },
                                    },
                                },
                            }
                            for role in ["pm", "arch", "dev", "sec", "qa", "ops", "all"]
                        },
                    },
                },
            },
            "states": {"type": "array", "minItems": 1},
            "workflows": {"type": "object", "minProperties": 1},
            "transitions": {"type": "array", "minItems": 1},
        },
    }

    schema_path = tmp_path / "schema.json"
    with open(schema_path, "w") as f:
        json.dump(schema, f)

    return schema_path


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear WorkflowConfig cache before and after each test."""
    WorkflowConfig.clear_cache()
    yield
    WorkflowConfig.clear_cache()


class TestSpecflowWorkflowRoles:
    """Tests for v2.0 roles configuration."""

    def test_loads_specflow_config_with_roles(
        self, specflow_config_path: Path, roles_schema_path: Path
    ):
        """Test loading specflow_workflow.yml v2.0 with roles section."""
        config = WorkflowConfig.load(
            path=specflow_config_path,
            schema_path=roles_schema_path,
            validate=True,
            cache=False,
        )

        assert config.version == "2.0"
        assert "roles" in config._data

    def test_validates_all_seven_roles_present(
        self, specflow_config_path: Path, roles_schema_path: Path
    ):
        """Test that all 7 required roles are defined."""
        config = WorkflowConfig.load(
            path=specflow_config_path,
            schema_path=roles_schema_path,
            validate=True,
            cache=False,
        )

        roles = config._data["roles"]["definitions"]
        assert "pm" in roles
        assert "arch" in roles
        assert "dev" in roles
        assert "sec" in roles
        assert "qa" in roles
        assert "ops" in roles
        assert "all" in roles

    def test_each_role_has_required_properties(
        self, specflow_config_path: Path, roles_schema_path: Path
    ):
        """Test that each role has display_name, icon, commands, and agents."""
        config = WorkflowConfig.load(
            path=specflow_config_path,
            schema_path=roles_schema_path,
            validate=True,
            cache=False,
        )

        roles = config._data["roles"]["definitions"]
        for role_name, role_def in roles.items():
            assert "display_name" in role_def, f"Role {role_name} missing display_name"
            assert "icon" in role_def, f"Role {role_name} missing icon"
            assert "commands" in role_def, f"Role {role_name} missing commands"
            assert "agents" in role_def, f"Role {role_name} missing agents"

    def test_primary_role_defaults_to_dev(
        self, specflow_config_path: Path, roles_schema_path: Path
    ):
        """Test that primary role is set to 'dev'."""
        config = WorkflowConfig.load(
            path=specflow_config_path,
            schema_path=roles_schema_path,
            validate=True,
            cache=False,
        )

        assert config._data["roles"]["primary"] == "dev"

    def test_show_all_commands_is_boolean(
        self, specflow_config_path: Path, roles_schema_path: Path
    ):
        """Test that show_all_commands is a boolean."""
        config = WorkflowConfig.load(
            path=specflow_config_path,
            schema_path=roles_schema_path,
            validate=True,
            cache=False,
        )

        assert isinstance(config._data["roles"]["show_all_commands"], bool)

    def test_pm_role_has_correct_commands(
        self, specflow_config_path: Path, roles_schema_path: Path
    ):
        """Test PM role has assess, define, discover commands."""
        config = WorkflowConfig.load(
            path=specflow_config_path,
            schema_path=roles_schema_path,
            validate=True,
            cache=False,
        )

        pm_role = config._data["roles"]["definitions"]["pm"]
        assert set(pm_role["commands"]) == {"assess", "define", "discover"}

    def test_dev_role_has_correct_commands(
        self, specflow_config_path: Path, roles_schema_path: Path
    ):
        """Test Developer role has build, debug, refactor commands."""
        config = WorkflowConfig.load(
            path=specflow_config_path,
            schema_path=roles_schema_path,
            validate=True,
            cache=False,
        )

        dev_role = config._data["roles"]["definitions"]["dev"]
        assert set(dev_role["commands"]) == {"build", "debug", "refactor"}

    def test_sec_role_has_security_agents(
        self, specflow_config_path: Path, roles_schema_path: Path
    ):
        """Test Security role has security engineer agent."""
        config = WorkflowConfig.load(
            path=specflow_config_path,
            schema_path=roles_schema_path,
            validate=True,
            cache=False,
        )

        sec_role = config._data["roles"]["definitions"]["sec"]
        assert "@secure-by-design-engineer" in sec_role["agents"]

    def test_all_role_has_empty_commands(
        self, specflow_config_path: Path, roles_schema_path: Path
    ):
        """Test 'all' role has empty commands array."""
        config = WorkflowConfig.load(
            path=specflow_config_path,
            schema_path=roles_schema_path,
            validate=True,
            cache=False,
        )

        all_role = config._data["roles"]["definitions"]["all"]
        assert all_role["commands"] == []
        assert all_role["agents"] == []

    def test_icons_are_emojis(
        self, specflow_config_path: Path, roles_schema_path: Path
    ):
        """Test that role icons are emoji characters."""
        config = WorkflowConfig.load(
            path=specflow_config_path,
            schema_path=roles_schema_path,
            validate=True,
            cache=False,
        )

        expected_icons = {
            "pm": "📋",
            "arch": "🏗️",
            "dev": "💻",
            "sec": "🔒",
            "qa": "✅",
            "ops": "🚀",
            "all": "🌐",
        }

        roles = config._data["roles"]["definitions"]
        for role_name, expected_icon in expected_icons.items():
            assert roles[role_name]["icon"] == expected_icon


class TestRolesSchemaValidation:
    """Tests for schema validation of roles section."""

    def test_rejects_missing_primary_role(
        self, tmp_path: Path, roles_schema_path: Path
    ):
        """Test that missing 'primary' field fails validation."""
        config_data = {
            "version": "2.0",
            "roles": {
                "show_all_commands": False,
                "definitions": {
                    "pm": {
                        "display_name": "PM",
                        "icon": "📋",
                        "commands": [],
                        "agents": [],
                    },
                    "arch": {
                        "display_name": "Arch",
                        "icon": "🏗️",
                        "commands": [],
                        "agents": [],
                    },
                    "dev": {
                        "display_name": "Dev",
                        "icon": "💻",
                        "commands": [],
                        "agents": [],
                    },
                    "sec": {
                        "display_name": "Sec",
                        "icon": "🔒",
                        "commands": [],
                        "agents": [],
                    },
                    "qa": {
                        "display_name": "QA",
                        "icon": "✅",
                        "commands": [],
                        "agents": [],
                    },
                    "ops": {
                        "display_name": "Ops",
                        "icon": "🚀",
                        "commands": [],
                        "agents": [],
                    },
                    "all": {
                        "display_name": "All",
                        "icon": "🌐",
                        "commands": [],
                        "agents": [],
                    },
                },
            },
            "states": ["To Do", "Done"],
            "workflows": {
                "test": {
                    "command": "/test",
                    "agents": ["test"],
                    "input_states": ["To Do"],
                    "output_state": "Done",
                }
            },
            "transitions": [{"from": "To Do", "to": "Done", "via": "test"}],
        }

        config_path = tmp_path / "invalid_config.yml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        with pytest.raises(WorkflowConfigValidationError):
            WorkflowConfig.load(
                path=config_path,
                schema_path=roles_schema_path,
                validate=True,
                cache=False,
            )

    def test_rejects_invalid_role_definition(
        self, tmp_path: Path, roles_schema_path: Path
    ):
        """Test that role missing required properties fails validation."""
        config_data = {
            "version": "2.0",
            "roles": {
                "primary": "dev",
                "show_all_commands": False,
                "definitions": {
                    "pm": {
                        "display_name": "PM",
                        # Missing icon, commands, agents
                    },
                    "arch": {
                        "display_name": "Arch",
                        "icon": "🏗️",
                        "commands": [],
                        "agents": [],
                    },
                    "dev": {
                        "display_name": "Dev",
                        "icon": "💻",
                        "commands": [],
                        "agents": [],
                    },
                    "sec": {
                        "display_name": "Sec",
                        "icon": "🔒",
                        "commands": [],
                        "agents": [],
                    },
                    "qa": {
                        "display_name": "QA",
                        "icon": "✅",
                        "commands": [],
                        "agents": [],
                    },
                    "ops": {
                        "display_name": "Ops",
                        "icon": "🚀",
                        "commands": [],
                        "agents": [],
                    },
                    "all": {
                        "display_name": "All",
                        "icon": "🌐",
                        "commands": [],
                        "agents": [],
                    },
                },
            },
            "states": ["To Do", "Done"],
            "workflows": {
                "test": {
                    "command": "/test",
                    "agents": ["test"],
                    "input_states": ["To Do"],
                    "output_state": "Done",
                }
            },
            "transitions": [{"from": "To Do", "to": "Done", "via": "test"}],
        }

        config_path = tmp_path / "invalid_role.yml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        with pytest.raises(WorkflowConfigValidationError):
            WorkflowConfig.load(
                path=config_path,
                schema_path=roles_schema_path,
                validate=True,
                cache=False,
            )


class TestBackwardsCompatibility:
    """Tests for backwards compatibility with jpspec_workflow.yml v1.x."""

    def test_loads_legacy_jpspec_workflow_without_roles(
        self, tmp_path: Path, roles_schema_path: Path
    ):
        """Test that v1.x jpspec_workflow.yml without roles still loads."""
        config_data = {
            "version": "1.1",
            # No roles section
            "states": ["To Do", "Done"],
            "workflows": {
                "test": {
                    "command": "/jpspec:test",
                    "agents": ["test-agent"],
                    "input_states": ["To Do"],
                    "output_state": "Done",
                }
            },
            "transitions": [{"from": "To Do", "to": "Done", "via": "test"}],
        }

        config_path = tmp_path / "jpspec_workflow.yml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Should load successfully without roles (optional in v1.x)
        config = WorkflowConfig.load(
            path=config_path,
            validate=False,  # Skip schema validation for legacy
            cache=False,
        )

        assert config.version == "1.1"
        assert "roles" not in config._data

    def test_prefers_specflow_over_jpspec(self, tmp_path: Path):
        """Test that specflow_workflow.yml is preferred over jpspec_workflow.yml."""
        # Create both files in same directory
        specflow_config = {
            "version": "2.0",
            "roles": {"primary": "dev", "show_all_commands": False, "definitions": {}},
            "states": ["To Do", "Done"],
            "workflows": {
                "test": {
                    "command": "/test",
                    "agents": ["test"],
                    "input_states": ["To Do"],
                    "output_state": "Done",
                }
            },
            "transitions": [{"from": "To Do", "to": "Done", "via": "test"}],
        }

        jpspec_config = {
            "version": "1.1",
            "states": ["To Do", "Done"],
            "workflows": {
                "test": {
                    "command": "/test",
                    "agents": ["test"],
                    "input_states": ["To Do"],
                    "output_state": "Done",
                }
            },
            "transitions": [{"from": "To Do", "to": "Done", "via": "test"}],
        }

        specflow_path = tmp_path / "specflow_workflow.yml"
        jpspec_path = tmp_path / "jpspec_workflow.yml"

        with open(specflow_path, "w") as f:
            yaml.dump(specflow_config, f)

        with open(jpspec_path, "w") as f:
            yaml.dump(jpspec_config, f)

        # Change to tmp directory and load without explicit path
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            config = WorkflowConfig.load(validate=False, cache=False)

            # Should prefer specflow_workflow.yml (v2.0)
            assert config.version == "2.0"
            assert "roles" in config._data
        finally:
            os.chdir(original_cwd)
