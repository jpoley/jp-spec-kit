"""Tests for VS Code settings generator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from flowspec_cli.vscode.settings_generator import VSCodeSettingsGenerator
from flowspec_cli.workflow.config import WorkflowConfig
from flowspec_cli.workflow.exceptions import WorkflowConfigError


@pytest.fixture
def mock_workflow_config(tmp_path: Path) -> WorkflowConfig:
    """Create a mock workflow config for testing."""
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
                        "@researcher",
                    ],
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
                "qa": {
                    "display_name": "QA Engineer",
                    "icon": "✅",
                    "commands": ["test", "verify", "review"],
                    "agents": [
                        "@quality-guardian",
                        "@release-manager",
                    ],
                },
            },
        },
        "states": ["To Do", "Planned", "In Implementation", "Done"],
        "workflows": {},
        "transitions": [],
    }

    return WorkflowConfig(config_data)


class TestVSCodeSettingsGenerator:
    """Test suite for VSCodeSettingsGenerator."""

    def test_init_with_config(self, mock_workflow_config: WorkflowConfig) -> None:
        """Test initialization with provided config."""
        generator = VSCodeSettingsGenerator(workflow_config=mock_workflow_config)
        assert generator.workflow_config is mock_workflow_config
        assert generator.primary_role == "dev"

    def test_init_with_role_override(
        self, mock_workflow_config: WorkflowConfig
    ) -> None:
        """Test initialization with role override."""
        generator = VSCodeSettingsGenerator(
            workflow_config=mock_workflow_config,
            primary_role="pm",
        )
        assert generator.primary_role == "pm"

    def test_primary_role_missing_raises_error(self) -> None:
        """Test that missing primary role raises error."""
        config_data = {
            "version": "2.0",
            "roles": {
                "definitions": {},
            },
        }
        config = WorkflowConfig(config_data)
        generator = VSCodeSettingsGenerator(workflow_config=config)

        with pytest.raises(WorkflowConfigError, match="No 'primary' role set"):
            _ = generator.primary_role

    def test_get_role_agents(self, mock_workflow_config: WorkflowConfig) -> None:
        """Test getting agents for a specific role."""
        generator = VSCodeSettingsGenerator(workflow_config=mock_workflow_config)

        dev_agents = generator.get_role_agents("dev")
        assert dev_agents == [
            "@frontend-engineer",
            "@backend-engineer",
            "@ai-ml-engineer",
        ]

        qa_agents = generator.get_role_agents("qa")
        assert qa_agents == [
            "@quality-guardian",
            "@release-manager",
        ]

    def test_get_role_agents_invalid_role(
        self, mock_workflow_config: WorkflowConfig
    ) -> None:
        """Test getting agents for invalid role raises error."""
        generator = VSCodeSettingsGenerator(workflow_config=mock_workflow_config)

        with pytest.raises(WorkflowConfigError, match="Role 'invalid' not found"):
            generator.get_role_agents("invalid")

    def test_get_all_agents(self, mock_workflow_config: WorkflowConfig) -> None:
        """Test getting all agents across all roles."""
        generator = VSCodeSettingsGenerator(workflow_config=mock_workflow_config)

        all_agents = generator.get_all_agents()
        expected = [
            "@ai-ml-engineer",
            "@backend-engineer",
            "@frontend-engineer",
            "@product-requirements-manager",
            "@quality-guardian",
            "@release-manager",
            "@researcher",
            "@workflow-assessor",
        ]
        assert all_agents == expected

    def test_get_agent_order(self, mock_workflow_config: WorkflowConfig) -> None:
        """Test agent ordering with primary role agents first."""
        generator = VSCodeSettingsGenerator(workflow_config=mock_workflow_config)

        # Dev role agents should be first
        agent_order = generator.get_agent_order("dev")
        assert agent_order[:3] == [
            "@frontend-engineer",
            "@backend-engineer",
            "@ai-ml-engineer",
        ]

        # PM role agents should be first
        agent_order = generator.get_agent_order("pm")
        assert agent_order[:3] == [
            "@product-requirements-manager",
            "@workflow-assessor",
            "@researcher",
        ]

    def test_generate_basic_settings(
        self, mock_workflow_config: WorkflowConfig
    ) -> None:
        """Test generating basic VS Code settings."""
        generator = VSCodeSettingsGenerator(workflow_config=mock_workflow_config)

        settings = generator.generate(role="dev", merge_existing=False)

        # Check GitHub Copilot configuration
        assert "github.copilot.chat.agents" in settings
        copilot_config = settings["github.copilot.chat.agents"]
        assert copilot_config["enabled"] is True
        assert len(copilot_config["pinnedAgents"]) <= 6
        assert copilot_config["pinnedAgents"][:3] == [
            "@frontend-engineer",
            "@backend-engineer",
            "@ai-ml-engineer",
        ]

        # Check prompt files configuration
        assert settings["github.copilot.chat.promptFiles"]["enabled"] is True

        # Check Flowspec configuration
        assert "flowspec" in settings
        flowspec_config = settings["flowspec"]
        assert flowspec_config["primaryRole"] == "dev"
        assert flowspec_config["displayName"] == "Developer"
        assert flowspec_config["icon"] == "💻"
        assert flowspec_config["commands"] == ["build", "debug", "refactor"]

        # Check extensions
        assert "extensions" in settings
        assert "github.copilot" in settings["extensions"]["recommendations"]

    def test_generate_merge_existing(
        self, mock_workflow_config: WorkflowConfig
    ) -> None:
        """Test merging with existing settings."""
        generator = VSCodeSettingsGenerator(workflow_config=mock_workflow_config)

        existing = {
            "editor.fontSize": 14,
            "files.autoSave": "afterDelay",
            "extensions": {
                "recommendations": ["ms-python.python"],
            },
        }

        settings = generator.generate(
            role="dev",
            merge_existing=True,
            existing_settings=existing,
        )

        # Existing settings preserved
        assert settings["editor.fontSize"] == 14
        assert settings["files.autoSave"] == "afterDelay"

        # New Flowspec settings added
        assert "flowspec" in settings
        assert settings["flowspec"]["primaryRole"] == "dev"

        # Extensions merged
        recommendations = settings["extensions"]["recommendations"]
        assert "ms-python.python" in recommendations
        assert "github.copilot" in recommendations

    def test_write_settings_creates_directory(
        self,
        mock_workflow_config: WorkflowConfig,
        tmp_path: Path,
    ) -> None:
        """Test that write_settings creates parent directory."""
        generator = VSCodeSettingsGenerator(workflow_config=mock_workflow_config)

        output_path = tmp_path / ".vscode" / "settings.json"
        assert not output_path.parent.exists()

        result = generator.write_settings(output_path, role="dev")

        assert result == output_path
        assert output_path.exists()
        assert output_path.parent.exists()

    def test_write_settings_valid_json(
        self,
        mock_workflow_config: WorkflowConfig,
        tmp_path: Path,
    ) -> None:
        """Test that written settings file is valid JSON."""
        generator = VSCodeSettingsGenerator(workflow_config=mock_workflow_config)

        output_path = tmp_path / ".vscode" / "settings.json"
        generator.write_settings(output_path, role="dev")

        # Should be able to parse as JSON
        with open(output_path, encoding="utf-8") as f:
            settings = json.load(f)

        assert settings["flowspec"]["primaryRole"] == "dev"

    def test_write_settings_force_overwrite(
        self,
        mock_workflow_config: WorkflowConfig,
        tmp_path: Path,
    ) -> None:
        """Test force overwrite of existing file."""
        generator = VSCodeSettingsGenerator(workflow_config=mock_workflow_config)

        output_path = tmp_path / ".vscode" / "settings.json"
        output_path.parent.mkdir(parents=True)

        # Write initial settings
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"existing": "data"}, f)

        # Force overwrite with merge_existing=False
        generator.write_settings(
            output_path, role="pm", force=True, merge_existing=False
        )

        with open(output_path, encoding="utf-8") as f:
            settings = json.load(f)

        # Old data should be gone
        assert "existing" not in settings
        assert settings["flowspec"]["primaryRole"] == "pm"

    def test_write_settings_merge_existing_file(
        self,
        mock_workflow_config: WorkflowConfig,
        tmp_path: Path,
    ) -> None:
        """Test merging with existing settings file."""
        generator = VSCodeSettingsGenerator(workflow_config=mock_workflow_config)

        output_path = tmp_path / ".vscode" / "settings.json"
        output_path.parent.mkdir(parents=True)

        # Write initial settings
        existing = {"editor.fontSize": 16}
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(existing, f)

        # Write with merge
        generator.write_settings(output_path, role="dev", merge_existing=True)

        with open(output_path, encoding="utf-8") as f:
            settings = json.load(f)

        # Existing data preserved
        assert settings["editor.fontSize"] == 16
        # New data added
        assert settings["flowspec"]["primaryRole"] == "dev"

    def test_get_default_settings_path(self) -> None:
        """Test getting default settings path."""
        path = VSCodeSettingsGenerator.get_default_settings_path()
        assert path.name == "settings.json"
        assert path.parent.name == ".vscode"

    def test_agent_pinning_limits_to_six(
        self, mock_workflow_config: WorkflowConfig
    ) -> None:
        """Test that agent pinning limits to 6 agents."""
        generator = VSCodeSettingsGenerator(workflow_config=mock_workflow_config)

        settings = generator.generate(role="dev", merge_existing=False)

        pinned = settings["github.copilot.chat.agents"]["pinnedAgents"]
        assert len(pinned) <= 6

    def test_different_roles_generate_different_settings(
        self, mock_workflow_config: WorkflowConfig
    ) -> None:
        """Test that different roles generate different settings."""
        generator = VSCodeSettingsGenerator(workflow_config=mock_workflow_config)

        dev_settings = generator.generate(role="dev", merge_existing=False)
        pm_settings = generator.generate(role="pm", merge_existing=False)

        # Different primary roles
        assert dev_settings["flowspec"]["primaryRole"] == "dev"
        assert pm_settings["flowspec"]["primaryRole"] == "pm"

        # Different agent orders
        dev_agents = dev_settings["github.copilot.chat.agents"]["pinnedAgents"]
        pm_agents = pm_settings["github.copilot.chat.agents"]["pinnedAgents"]
        assert dev_agents != pm_agents

        # Different commands
        assert dev_settings["flowspec"]["commands"] == ["build", "debug", "refactor"]
        assert pm_settings["flowspec"]["commands"] == ["assess", "define", "discover"]
