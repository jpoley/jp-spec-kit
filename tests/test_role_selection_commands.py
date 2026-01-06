"""Tests for role selection in init and configure commands.

This module tests that:
- /spec:init command includes role selection prompts
- /spec:configure command includes role selection prompts
- Both commands document FLOWSPEC_PRIMARY_ROLE environment variable
- Both commands support --role flag for non-interactive use
- Command templates have all 7 role options with correct icons
"""

from pathlib import Path

import pytest


class TestRoleSelectionCommandTemplates:
    """Tests for role selection in command templates."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def init_template_path(self, project_root: Path) -> Path:
        """Get path to init.md template."""
        return project_root / "templates" / "commands" / "spec" / "init.md"

    @pytest.fixture
    def configure_template_path(self, project_root: Path) -> Path:
        """Get path to configure.md template."""
        return project_root / "templates" / "commands" / "spec" / "configure.md"

    def test_init_template_exists(self, init_template_path: Path):
        """Test that init.md template exists."""
        assert init_template_path.exists(), (
            f"Init template not found at {init_template_path}"
        )
        assert init_template_path.is_file()

    def test_configure_template_exists(self, configure_template_path: Path):
        """Test that configure.md template exists."""
        assert configure_template_path.exists(), (
            f"Configure template not found at {configure_template_path}"
        )
        assert configure_template_path.is_file()

    def test_init_has_role_selection_prompt(self, init_template_path: Path):
        """Test that init.md includes role selection interactive prompt."""
        content = init_template_path.read_text()

        # Check for role selection section header
        assert "Select Your Primary Role" in content, "Missing role selection header"

        # Check for all 7 roles with their icons
        expected_roles = [
            ("📋", "Product Manager", "PM"),
            ("🏗️", "Architect", "Arch"),
            ("💻", "Developer", "Dev"),
            ("🔒", "Security Engineer", "Sec"),
            ("✅", "QA Engineer", "QA"),
            ("🚀", "SRE/DevOps", "Ops"),
            ("🌐", "All Roles", "All"),
        ]

        for icon, display_name, abbrev in expected_roles:
            assert icon in content, f"Missing icon {icon} for {display_name}"
            assert display_name in content, f"Missing role name {display_name}"

        # Check for input prompt
        assert "Enter selection [1-7]" in content, "Missing selection prompt"

    def test_configure_has_role_selection_prompt(self, configure_template_path: Path):
        """Test that configure.md includes role selection interactive prompt."""
        content = configure_template_path.read_text()

        # Check for role selection section header
        assert "Select Your Primary Role" in content, "Missing role selection header"

        # Check for all 7 roles with their icons
        expected_roles = [
            ("📋", "Product Manager", "PM"),
            ("🏗️", "Architect", "Arch"),
            ("💻", "Developer", "Dev"),
            ("🔒", "Security Engineer", "Sec"),
            ("✅", "QA Engineer", "QA"),
            ("🚀", "SRE/DevOps", "Ops"),
            ("🌐", "All Roles", "All"),
        ]

        for icon, display_name, abbrev in expected_roles:
            assert icon in content, f"Missing icon {icon} for {display_name}"
            assert display_name in content, f"Missing role name {display_name}"

        # Check for input prompt (configure has 8 options: 7 roles + keep current)
        assert "Enter selection [1-8]" in content, "Missing selection prompt"

    def test_init_documents_role_flag(self, init_template_path: Path):
        """Test that init.md documents --role flag for non-interactive use."""
        content = init_template_path.read_text()

        assert "--role" in content, "Missing --role flag documentation"
        # Check for role options (may have backslash escapes in markdown)
        assert "pm" in content and "arch" in content and "dev" in content, (
            "Missing role options"
        )
        assert "sec" in content and "qa" in content and "ops" in content, (
            "Missing role options"
        )

    def test_configure_documents_role_flag(self, configure_template_path: Path):
        """Test that configure.md documents --role flag for non-interactive use."""
        content = configure_template_path.read_text()

        assert "--role" in content, "Missing --role flag documentation"
        # Check for role options (may have backslash escapes in markdown)
        assert "pm" in content and "arch" in content and "dev" in content, (
            "Missing role options"
        )
        assert "sec" in content and "qa" in content and "ops" in content, (
            "Missing role options"
        )

    def test_init_documents_env_var(self, init_template_path: Path):
        """Test that init.md documents FLOWSPEC_PRIMARY_ROLE environment variable."""
        content = init_template_path.read_text()

        assert "FLOWSPEC_PRIMARY_ROLE" in content, (
            "Missing FLOWSPEC_PRIMARY_ROLE env var"
        )
        assert "environment variable" in content.lower(), (
            "Missing env var documentation"
        )

    def test_configure_documents_env_var(self, configure_template_path: Path):
        """Test that configure.md documents FLOWSPEC_PRIMARY_ROLE environment variable."""
        content = configure_template_path.read_text()

        assert "FLOWSPEC_PRIMARY_ROLE" in content, (
            "Missing FLOWSPEC_PRIMARY_ROLE env var"
        )
        assert "environment variable" in content.lower(), (
            "Missing env var documentation"
        )

    def test_init_has_role_to_workflow_yml_update(self, init_template_path: Path):
        """Test that init.md includes instructions to update flowspec_workflow.yml."""
        content = init_template_path.read_text()

        assert "flowspec_workflow.yml" in content, (
            "Missing workflow config file reference"
        )
        assert "roles.primary" in content or "roles:" in content, (
            "Missing roles section reference"
        )

    def test_configure_has_role_to_workflow_yml_update(
        self, configure_template_path: Path
    ):
        """Test that configure.md includes instructions to update flowspec_workflow.yml."""
        content = configure_template_path.read_text()

        assert "flowspec_workflow.yml" in content, (
            "Missing workflow config file reference"
        )
        assert "roles.primary" in content or "roles:" in content, (
            "Missing roles section reference"
        )

    def test_init_shows_role_mapping(self, init_template_path: Path):
        """Test that init.md shows mapping from input numbers to role IDs."""
        content = init_template_path.read_text()

        # Check for role ID mappings (e.g., "Input 1 → 'pm'")
        expected_mappings = [
            "pm",
            "arch",
            "dev",
            "sec",
            "qa",
            "ops",
            "all",
        ]

        for role_id in expected_mappings:
            assert f'"{role_id}"' in content or f"'{role_id}'" in content, (
                f"Missing role ID {role_id}"
            )

    def test_configure_shows_role_mapping(self, configure_template_path: Path):
        """Test that configure.md shows mapping from input numbers to role IDs."""
        content = configure_template_path.read_text()

        # Check for role ID mappings
        expected_mappings = [
            "pm",
            "arch",
            "dev",
            "sec",
            "qa",
            "ops",
            "all",
        ]

        for role_id in expected_mappings:
            assert f'"{role_id}"' in content or f"'{role_id}'" in content, (
                f"Missing role ID {role_id}"
            )

    def test_init_has_precedence_order(self, init_template_path: Path):
        """Test that init.md documents precedence order for role selection."""
        content = init_template_path.read_text()

        # Check for precedence documentation
        assert "precedence" in content.lower(), "Missing precedence documentation"
        assert "environment variable" in content.lower(), "Missing env var precedence"
        assert "--role" in content, "Missing flag precedence"

    def test_configure_has_precedence_order(self, configure_template_path: Path):
        """Test that configure.md documents precedence order for role selection."""
        content = configure_template_path.read_text()

        # Check for precedence documentation
        assert "precedence" in content.lower(), "Missing precedence documentation"
        assert "environment variable" in content.lower(), "Missing env var precedence"
        assert "--role" in content, "Missing flag precedence"

    def test_init_has_summary_with_role_info(self, init_template_path: Path):
        """Test that init.md includes role info in completion summary."""
        content = init_template_path.read_text()

        # Check for role section in summary
        assert "ROLE CONFIGURATION" in content, "Missing role configuration summary"
        assert "Selected Role:" in content, "Missing selected role display"
        assert "{icon}" in content, "Missing icon placeholder"
        assert "{display_name}" in content, "Missing display name placeholder"

    def test_configure_has_summary_with_role_info(self, configure_template_path: Path):
        """Test that configure.md includes role info in completion summary."""
        content = configure_template_path.read_text()

        # Check for role section in summary
        assert "ROLE CONFIGURATION" in content, "Missing role configuration summary"
        assert "Role:" in content or "Selected Role:" in content, "Missing role display"

    def test_command_files_exist(self, project_root: Path):
        """Test that command files exist in .claude/commands/spec/."""
        spec_dir = project_root / ".claude" / "commands" / "spec"
        init_file = spec_dir / "init.md"
        configure_file = spec_dir / "configure.md"

        assert init_file.exists(), f"init.md not found at {init_file}"
        assert configure_file.exists(), f"configure.md not found at {configure_file}"

        # Verify they are files
        assert init_file.is_file(), "init.md should be a file"
        assert configure_file.is_file(), "configure.md should be a file"


class TestRoleSelectionIntegration:
    """Integration tests for role selection workflow."""

    def test_all_role_ids_match_flowspec_workflow_yml(self):
        """Test that role IDs in commands match those in flowspec_workflow.yml."""
        project_root = Path(__file__).parent.parent
        workflow_config = project_root / "flowspec_workflow.yml"

        if not workflow_config.exists():
            pytest.skip("flowspec_workflow.yml not found (test environment)")

        import yaml

        with open(workflow_config) as f:
            config = yaml.safe_load(f)

        # Get role definitions from config
        role_definitions = config.get("roles", {}).get("definitions", {})
        config_role_ids = set(role_definitions.keys())

        # Expected role IDs (pm removed - PM work is done via /flowspec workflow commands)
        expected_role_ids = {"arch", "dev", "sec", "qa", "ops", "all"}

        assert config_role_ids == expected_role_ids, (
            f"Role IDs mismatch. Expected: {expected_role_ids}, "
            f"Found in config: {config_role_ids}"
        )

    def test_init_and_configure_have_consistent_role_lists(self):
        """Test that init.md and configure.md have consistent role definitions."""
        project_root = Path(__file__).parent.parent
        init_path = project_root / "templates" / "commands" / "spec" / "init.md"
        configure_path = (
            project_root / "templates" / "commands" / "spec" / "configure.md"
        )

        init_content = init_path.read_text()
        configure_content = configure_path.read_text()

        # Check that both have the same role icons
        expected_role_icons = ["📋", "🏗️", "💻", "🔒", "✅", "🚀", "🌐"]

        for icon in expected_role_icons:
            assert icon in init_content, f"Init missing icon {icon}"
            assert icon in configure_content, f"Configure missing icon {icon}"
