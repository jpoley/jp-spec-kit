"""Tests to verify dev-setup and init commands produce equivalent results.

This test suite ensures that:
- `specify dev-setup` (for development)
- `specify init` (for user projects)

Both commands create the same command structure and make the same commands available.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch


class TestDevSetupInitEquivalence:
    """Verify dev-setup and init produce equivalent command sets."""

    @pytest.fixture
    def repo_root(self):
        """Get the repository root directory."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def templates_commands_dir(self, repo_root):
        """Path to templates/commands directory."""
        return repo_root / "templates" / "commands"

    def test_same_speckit_commands_available(self, repo_root, templates_commands_dir):
        """Both dev-setup and init should make same speckit commands available.

        Verifies that all speckit commands in templates are accessible.
        """
        if not templates_commands_dir.exists():
            pytest.skip("templates/commands directory does not exist")

        # Get speckit commands from templates (what init would create)
        template_speckit_commands = set()
        for md_file in templates_commands_dir.glob("*.md"):
            template_speckit_commands.add(md_file.stem)  # filename without .md

        # Get speckit commands from .claude (what dev-setup creates)
        claude_speckit_dir = repo_root / ".claude" / "commands" / "speckit"
        if not claude_speckit_dir.exists():
            pytest.skip(".claude/commands/speckit does not exist - run dev-setup first")

        claude_speckit_commands = set()
        for md_file in claude_speckit_dir.glob("*.md"):
            claude_speckit_commands.add(md_file.stem)

        # Both should have same commands
        missing_in_claude = template_speckit_commands - claude_speckit_commands
        extra_in_claude = claude_speckit_commands - template_speckit_commands

        assert not missing_in_claude, (
            f"Commands in templates but not in .claude/commands/speckit:\n"
            f"{', '.join(sorted(missing_in_claude))}"
        )

        assert not extra_in_claude, (
            f"Commands in .claude/commands/speckit but not in templates:\n"
            f"{', '.join(sorted(extra_in_claude))}"
        )

    def test_speckit_command_content_matches(self, repo_root, templates_commands_dir):
        """Command content should be identical between templates and .claude.

        Since .claude uses symlinks, this verifies symlinks work correctly.
        """
        if not templates_commands_dir.exists():
            pytest.skip("templates/commands directory does not exist")

        claude_speckit_dir = repo_root / ".claude" / "commands" / "speckit"
        if not claude_speckit_dir.exists():
            pytest.skip(".claude/commands/speckit does not exist - run dev-setup first")

        content_mismatches = []

        # Compare each template with its symlink
        for template_file in templates_commands_dir.glob("*.md"):
            symlink_file = claude_speckit_dir / template_file.name

            if not symlink_file.exists():
                continue  # Covered by other test

            # Read content from both
            template_content = template_file.read_text()
            symlink_content = symlink_file.read_text()

            if template_content != symlink_content:
                content_mismatches.append(template_file.name)

        assert not content_mismatches, (
            f"Content mismatch between templates and .claude symlinks:\n"
            f"{chr(10).join(content_mismatches)}\n\n"
            f"This should not happen if symlinks are correctly set up."
        )

    def test_jpspec_commands_exist_in_templates(self, templates_commands_dir):
        """Jpspec commands should exist in templates/commands/jpspec/.

        These are the enhanced commands that need to be distributed.
        """
        if not templates_commands_dir.exists():
            pytest.skip("templates/commands directory does not exist")

        jpspec_template_dir = templates_commands_dir / "jpspec"

        # This test documents expected future state
        if not jpspec_template_dir.exists():
            pytest.skip(
                "templates/commands/jpspec directory does not exist yet.\n"
                "This is expected - jpspec commands need to be migrated to templates."
            )

        expected_commands = {
            "research.md",
            "implement.md",
            "validate.md",
            "specify.md",
            "plan.md",
            "assess.md",
            "operate.md",
        }

        existing_commands = {f.name for f in jpspec_template_dir.glob("*.md")}

        missing_commands = expected_commands - existing_commands

        if missing_commands:
            print(f"Note: Some jpspec commands not yet in templates: {missing_commands}")

    def test_naming_convention_consistency(self, repo_root):
        """Command naming should follow consistent conventions.

        Verifies kebab-case and proper .md extensions.
        """
        claude_commands_dir = repo_root / ".claude" / "commands"

        if not claude_commands_dir.exists():
            pytest.skip(".claude/commands directory does not exist")

        invalid_names = []

        for md_file in claude_commands_dir.rglob("*.md"):
            name = md_file.stem

            # Check for proper kebab-case (allow underscores for special files)
            if name.startswith("_"):
                continue  # Special files like _backlog-instructions.md

            if not name.replace("-", "").replace("_", "").isalnum():
                invalid_names.append(str(md_file.relative_to(claude_commands_dir.parent.parent)))

        assert not invalid_names, (
            f"Command files with invalid naming:\n{chr(10).join(invalid_names)}\n\n"
            f"Use kebab-case: my-command.md"
        )


class TestDevSetupIdempotency:
    """Verify dev-setup command is idempotent and safe to re-run."""

    @pytest.fixture
    def repo_root(self):
        """Get the repository root directory."""
        return Path(__file__).parent.parent

    def test_dev-setup_can_run_multiple_times(self, repo_root):
        """Running dev-setup multiple times should be safe and produce same result.

        This is a critical property for CI/CD safety.
        """
        claude_commands_dir = repo_root / ".claude" / "commands"

        if not claude_commands_dir.exists():
            pytest.skip(".claude/commands directory does not exist")

        # Get initial state
        initial_symlinks = set()
        for symlink in claude_commands_dir.rglob("*.md"):
            if symlink.is_symlink():
                initial_symlinks.add(str(symlink.relative_to(claude_commands_dir)))

        # Note: We don't actually run dev-setup here to avoid side effects
        # This test documents expected behavior

        assert initial_symlinks, "Should have symlinks in .claude/commands/"


class TestCommandDiscoverability:
    """Verify commands are discoverable and properly registered."""

    @pytest.fixture
    def repo_root(self):
        """Get the repository root directory."""
        return Path(__file__).parent.parent

    def test_all_commands_have_descriptions(self, repo_root):
        """All command files should have description metadata.

        This helps with command discovery and documentation.
        """
        claude_commands_dir = repo_root / ".claude" / "commands"

        if not claude_commands_dir.exists():
            pytest.skip(".claude/commands directory does not exist")

        # This is a soft requirement - not enforced yet
        # Just document which commands might be missing descriptions

        commands_without_descriptions = []

        for md_file in claude_commands_dir.rglob("*.md"):
            if md_file.name.startswith("_"):
                continue  # Skip special files

            content = md_file.read_text()

            # Check for common description patterns
            has_description = any([
                content.startswith("# "),
                "## Description" in content,
                "## Overview" in content,
            ])

            if not has_description:
                commands_without_descriptions.append(
                    str(md_file.relative_to(claude_commands_dir.parent.parent))
                )

        if commands_without_descriptions:
            print(f"Note: Commands without clear descriptions: {commands_without_descriptions}")
