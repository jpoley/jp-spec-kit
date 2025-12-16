"""VS Code settings generator for role-based agent pinning.

This module generates .vscode/settings.json configurations that integrate
with VS Code Copilot to provide role-appropriate agent suggestions and
command visibility.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..workflow.config import WorkflowConfig
from ..workflow.exceptions import WorkflowConfigError


class VSCodeSettingsGenerator:
    """Generate VS Code settings for role-based agent integration.

    This class generates .vscode/settings.json files that configure VS Code
    Copilot to respect the user's selected role by:
    - Pinning role-appropriate agents to the top of suggestions
    - Configuring handoff priorities based on role workflow
    - Setting up prompt files for chat context

    Example:
        >>> generator = VSCodeSettingsGenerator()
        >>> settings = generator.generate()
        >>> generator.write_settings("/path/to/project/.vscode/settings.json")
    """

    def __init__(
        self,
        workflow_config: WorkflowConfig | None = None,
        primary_role: str | None = None,
    ) -> None:
        """Initialize the settings generator.

        Args:
            workflow_config: WorkflowConfig instance. If None, loads from default location.
            primary_role: Override primary role from config. If None, reads from workflow config.
        """
        self.workflow_config = workflow_config or WorkflowConfig.load()
        self._primary_role = primary_role

    @property
    def primary_role(self) -> str:
        """Get the primary role for this configuration.

        Returns:
            Primary role name (e.g., "dev", "pm", "qa").

        Raises:
            WorkflowConfigError: If role configuration is missing or invalid.
        """
        if self._primary_role:
            return self._primary_role

        roles_config = self.workflow_config._data.get("roles", {})
        if not roles_config:
            raise WorkflowConfigError(
                "No 'roles' section found in workflow configuration. "
                "Please run 'specify init' to configure roles."
            )

        primary = roles_config.get("primary")
        if not primary:
            raise WorkflowConfigError(
                "No 'primary' role set in workflow configuration. "
                "Please run 'specify init' to select your role."
            )

        return primary

    def get_role_agents(self, role: str | None = None) -> list[str]:
        """Get agents associated with a specific role.

        Args:
            role: Role name (e.g., "dev"). If None, uses primary role.

        Returns:
            List of agent identities (e.g., ["@frontend-engineer", "@backend-engineer"]).

        Raises:
            WorkflowConfigError: If role is not defined in configuration.
        """
        role = role or self.primary_role

        roles_config = self.workflow_config._data.get("roles", {})
        role_definitions = roles_config.get("definitions", {})

        if role not in role_definitions:
            raise WorkflowConfigError(
                f"Role '{role}' not found in workflow configuration. "
                f"Available roles: {list(role_definitions.keys())}"
            )

        role_def = role_definitions[role]
        return role_def.get("agents", [])

    def get_all_agents(self) -> list[str]:
        """Get all agents defined across all roles.

        Returns:
            List of all unique agent identities.
        """
        roles_config = self.workflow_config._data.get("roles", {})
        role_definitions = roles_config.get("definitions", {})

        all_agents = set()
        for role_def in role_definitions.values():
            agents = role_def.get("agents", [])
            all_agents.update(agents)

        return sorted(all_agents)

    def get_agent_order(self, role: str | None = None) -> list[str]:
        """Get agent ordering with primary role agents first.

        Args:
            role: Role name. If None, uses primary role.

        Returns:
            List of agent identities ordered by priority (role agents first).
        """
        role = role or self.primary_role

        primary_agents = self.get_role_agents(role)
        all_agents = self.get_all_agents()

        # Primary role agents first, then others
        ordered = list(primary_agents)
        for agent in all_agents:
            if agent not in ordered:
                ordered.append(agent)

        return ordered

    def generate(
        self,
        role: str | None = None,
        merge_existing: bool = True,
        existing_settings: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate VS Code settings for the specified role.

        Args:
            role: Role name. If None, uses primary role.
            merge_existing: Whether to merge with existing settings.
            existing_settings: Existing settings dict to merge with. If None and
                merge_existing is True, reads from .vscode/settings.json.

        Returns:
            Complete VS Code settings dictionary with role-based configuration.
        """
        role = role or self.primary_role

        # Start with existing settings if requested
        if merge_existing:
            if existing_settings is None:
                existing_settings = self._read_existing_settings()
            settings = existing_settings.copy() if existing_settings else {}
        else:
            settings = {}

        # Get role-specific data
        roles_config = self.workflow_config._data.get("roles", {})
        role_definitions = roles_config.get("definitions", {})
        role_def = role_definitions.get(role, {})

        # Get ordered agents for pinning
        pinned_agents = self.get_agent_order(role)

        # Configure GitHub Copilot agents
        settings["github.copilot.chat.agents"] = {
            "enabled": True,
            "pinnedAgents": pinned_agents[:6],  # Pin top 6 agents for the role
        }

        # Configure prompt files
        settings["github.copilot.chat.promptFiles"] = {"enabled": True}

        # Configure Flowspec-specific settings
        settings["flowspec"] = {
            "primaryRole": role,
            "displayName": role_def.get("display_name", role.title()),
            "icon": role_def.get("icon", ""),
            "commands": role_def.get("commands", []),
            "agentOrder": pinned_agents,
            "version": self.workflow_config.version,
        }

        # Add recommended extensions
        if "extensions" not in settings:
            settings["extensions"] = {}
        if "recommendations" not in settings["extensions"]:
            settings["extensions"]["recommendations"] = []

        # Merge in Copilot extensions if not already present
        copilot_extensions = ["github.copilot", "github.copilot-chat"]
        for ext in copilot_extensions:
            if ext not in settings["extensions"]["recommendations"]:
                settings["extensions"]["recommendations"].append(ext)

        return settings

    def write_settings(
        self,
        output_path: Path | str,
        role: str | None = None,
        force: bool = False,
        merge_existing: bool = True,
    ) -> Path:
        """Write VS Code settings to file.

        Args:
            output_path: Path to .vscode/settings.json file.
            role: Role name. If None, uses primary role.
            force: If True, overwrite existing file without merging.
            merge_existing: If True, merge with existing settings.

        Returns:
            Path to the written settings file.

        Raises:
            FileExistsError: If file exists and force=False and merge_existing=False.
        """
        output_path = Path(output_path)

        # Check if file exists
        if output_path.exists() and not force and not merge_existing:
            raise FileExistsError(
                f"Settings file already exists: {output_path}. "
                "Use --force to overwrite or merge_existing=True to merge."
            )

        # Create parent directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate settings
        if not merge_existing or force:
            existing = None
        else:
            existing = self._read_existing_settings(output_path)

        settings = self.generate(
            role=role, merge_existing=merge_existing, existing_settings=existing
        )

        # Write to file with nice formatting
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
            f.write("\n")  # Add trailing newline

        return output_path

    def _read_existing_settings(self, path: Path | str | None = None) -> dict[str, Any]:
        """Read existing VS Code settings from file.

        Args:
            path: Path to settings.json. If None, uses .vscode/settings.json in cwd.

        Returns:
            Parsed settings dictionary, or empty dict if file doesn't exist.
        """
        if path is None:
            path = Path.cwd() / ".vscode" / "settings.json"
        else:
            path = Path(path)

        if not path.exists():
            return {}

        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    @staticmethod
    def get_default_settings_path() -> Path:
        """Get the default path for VS Code settings.

        Returns:
            Path to .vscode/settings.json in current working directory.
        """
        return Path.cwd() / ".vscode" / "settings.json"
