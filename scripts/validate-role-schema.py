#!/usr/bin/env python3
"""Validate role-based command structure in flowspec_workflow.yml.

This script performs comprehensive validation of role-based command architecture:
- Role definitions (all required roles present)
- Command-to-role mappings
- Agent-to-role assignments
- Command file existence
- Backwards-compatible alias support

Usage:
    python scripts/validate-role-schema.py [workflow_file]

    If not specified:
    - workflow_file defaults to: flowspec_workflow.yml

Examples:
    # Validate default workflow config
    python scripts/validate-role-schema.py

    # Validate custom workflow config
    python scripts/validate-role-schema.py custom_workflow.yml

Exit codes:
    0 - Validation passed
    1 - Validation errors found
    2 - File not found or YAML parsing error
"""

import sys
from pathlib import Path

import yaml


class RoleValidator:
    """Validator for role-based command structure.

    NOTE: PM role removed - PM work is done via /flowspec workflow commands.
    """

    REQUIRED_ROLES = {"arch", "dev", "sec", "qa", "ops", "all"}

    def __init__(self, config: dict):
        """Initialize validator with workflow config."""
        self.config = config
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self) -> bool:
        """Run all validations. Returns True if valid."""
        self.validate_roles_section()
        self.validate_role_definitions()
        self.validate_command_files()
        self.validate_agent_mappings()
        self.validate_command_naming()

        return len(self.errors) == 0

    def validate_roles_section(self) -> None:
        """Validate roles section exists and has required structure."""
        if "roles" not in self.config:
            self.errors.append("Missing 'roles' section in workflow config")
            return

        roles = self.config["roles"]

        # Check required keys
        if "primary" not in roles:
            self.errors.append("Missing 'roles.primary' key")

        if "show_all_commands" not in roles:
            self.errors.append("Missing 'roles.show_all_commands' key")

        if "definitions" not in roles:
            self.errors.append("Missing 'roles.definitions' key")
            return

        # Validate primary role value
        primary = roles.get("primary")
        if primary and primary not in self.REQUIRED_ROLES:
            self.errors.append(
                f"Invalid primary role '{primary}'. Must be one of: {self.REQUIRED_ROLES}"
            )

    def validate_role_definitions(self) -> None:
        """Validate each role definition has required fields."""
        roles = self.config.get("roles", {}).get("definitions", {})

        # Check all required roles are present
        missing_roles = self.REQUIRED_ROLES - set(roles.keys())
        if missing_roles:
            self.errors.append(f"Missing required roles: {missing_roles}")
            return

        # Validate each role
        for role_name, role_data in roles.items():
            if not isinstance(role_data, dict):
                self.errors.append(f"Role '{role_name}' is not a dictionary")
                continue

            # Check required fields
            required_fields = {"display_name", "icon", "commands", "agents"}
            missing_fields = required_fields - set(role_data.keys())
            if missing_fields:
                self.errors.append(
                    f"Role '{role_name}' missing fields: {missing_fields}"
                )

            # Validate commands is a list
            if "commands" in role_data and not isinstance(role_data["commands"], list):
                self.errors.append(
                    f"Role '{role_name}' commands must be a list, got {type(role_data['commands']).__name__}"
                )

            # Validate agents is a list
            if "agents" in role_data and not isinstance(role_data["agents"], list):
                self.errors.append(
                    f"Role '{role_name}' agents must be a list, got {type(role_data['agents']).__name__}"
                )

            # Validate agents have @ prefix
            if "agents" in role_data:
                for agent in role_data["agents"]:
                    if not agent.startswith("@"):
                        self.errors.append(
                            f"Role '{role_name}' agent '{agent}' must start with @"
                        )

    def validate_command_files(self) -> None:
        """Validate command files exist for each role's commands."""
        roles = self.config.get("roles", {}).get("definitions", {})

        for role_name, role_data in roles.items():
            if role_name == "all":
                # 'all' role has no commands
                continue

            commands = role_data.get("commands", [])
            for command in commands:
                # Check in templates/commands/{role}/{command}.md
                command_path = Path(f"templates/commands/{role_name}/{command}.md")

                if not command_path.exists():
                    self.errors.append(
                        f"Missing command file for {role_name}/{command}: {command_path}"
                    )

    def validate_agent_mappings(self) -> None:
        """Validate agent-to-role mappings are consistent."""
        # Extract all agents from workflows
        workflow_agents = set()
        workflows = self.config.get("workflows", {})

        for workflow_name, workflow in workflows.items():
            for agent in workflow.get("agents", []):
                if isinstance(agent, dict):
                    agent_name = agent.get("name")
                else:
                    agent_name = agent

                if agent_name:
                    workflow_agents.add(agent_name)

        # Extract all agents from roles
        role_agents = set()
        roles = self.config.get("roles", {}).get("definitions", {})

        for role_name, role_data in roles.items():
            for agent in role_data.get("agents", []):
                # Remove @ prefix
                agent_name = agent.lstrip("@")
                role_agents.add(agent_name)

        # Check for workflow agents not assigned to any role
        unassigned = workflow_agents - role_agents
        if unassigned:
            self.warnings.append(
                f"Agents in workflows but not assigned to roles: {sorted(unassigned)}"
            )

        # Check for role agents not used in any workflow
        unused = role_agents - workflow_agents
        if unused:
            self.warnings.append(
                f"Agents assigned to roles but not used in workflows: {sorted(unused)}"
            )

    def validate_command_naming(self) -> None:
        """Validate command file naming conventions."""
        templates_dir = Path("templates/commands")

        if not templates_dir.exists():
            self.warnings.append(f"Templates directory not found: {templates_dir}")
            return

        # Check all .md files (excluding partials starting with _)
        for command_file in templates_dir.rglob("*.md"):
            # Skip partials
            if command_file.name.startswith("_"):
                continue

            basename = command_file.stem  # filename without .md

            # Command names should be lowercase with hyphens
            if not basename.replace("-", "").replace("_", "").isalnum():
                self.errors.append(
                    f"Invalid command name '{basename}': must be lowercase alphanumeric with hyphens/underscores"
                )
            elif basename != basename.lower():
                self.errors.append(
                    f"Invalid command name '{basename}': must be lowercase"
                )

    def print_results(self) -> None:
        """Print validation results."""
        if self.errors:
            print(f"\n❌ Found {len(self.errors)} error(s):\n")
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
            print()

        if self.warnings:
            print(f"\n⚠ Found {len(self.warnings)} warning(s):\n")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. {warning}")
            print()

        if not self.errors and not self.warnings:
            print("✅ Role schema validation PASSED")
            print()
            print("All validations passed:")
            print("  • Roles section structure")
            print("  • Role definitions (all required roles)")
            print("  • Command file existence")
            print("  • Agent-to-role mappings")
            print("  • Command naming conventions")
        elif not self.errors:
            print("✅ Role schema validation PASSED (with warnings)")
        else:
            print("❌ Role schema validation FAILED")


def load_yaml(path: Path) -> dict:
    """Load YAML file."""
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found - {path}")
        sys.exit(2)
    except yaml.YAMLError as e:
        print(f"❌ Error: Invalid YAML - {e}")
        sys.exit(2)


def main() -> int:
    """Main entry point."""
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0

    workflow_file = args[0] if len(args) > 0 else "flowspec_workflow.yml"
    workflow_path = Path(workflow_file)

    # Print validation info
    print("=" * 70)
    print("Role-Based Command Structure Validation")
    print("=" * 70)
    print(f"Workflow config: {workflow_path}")
    print()

    # Load and validate
    config = load_yaml(workflow_path)
    validator = RoleValidator(config)
    is_valid = validator.validate()
    validator.print_results()

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
