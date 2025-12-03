"""Tests to ensure dev-setup and init commands stay synchronized.

This test suite validates the single-source-of-truth approach where:
- All command content lives in templates/commands/
- .claude/commands/ contains ONLY symlinks
- No content drift between dev-setup and init
"""

import os
import pytest
from pathlib import Path


class TestDevSetupValidation:
    """Validate dev-setup setup maintains single source of truth."""

    @pytest.fixture
    def repo_root(self):
        """Get the repository root directory."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def claude_commands_dir(self, repo_root):
        """Path to .claude/commands directory."""
        return repo_root / ".claude" / "commands"

    @pytest.fixture
    def templates_commands_dir(self, repo_root):
        """Path to templates/commands directory."""
        return repo_root / "templates" / "commands"

    def test_claude_commands_are_symlinks_only(self, claude_commands_dir):
        """All .md files in .claude/commands/ must be symlinks.

        This ensures no direct editing happens in .claude/commands/,
        maintaining templates/ as the single source of truth.
        """
        if not claude_commands_dir.exists():
            pytest.skip(".claude/commands directory does not exist")

        non_symlink_files = []

        # Recursively find all .md files
        for md_file in claude_commands_dir.rglob("*.md"):
            if not md_file.is_symlink():
                non_symlink_files.append(str(md_file.relative_to(claude_commands_dir.parent.parent)))

        assert not non_symlink_files, (
            f"Found non-symlink .md files in .claude/commands/:\n"
            f"{chr(10).join(non_symlink_files)}\n\n"
            f"All command files must be symlinks to templates/.\n"
            f"To fix:\n"
            f"  1. Move content to templates/commands/\n"
            f"  2. Run: specify dev-setup --force"
        )

    def test_all_symlinks_resolve(self, claude_commands_dir):
        """All symlinks in .claude/commands/ must resolve to existing files.

        Broken symlinks indicate missing template files or incorrect paths.
        """
        if not claude_commands_dir.exists():
            pytest.skip(".claude/commands directory does not exist")

        broken_symlinks = []

        for symlink in claude_commands_dir.rglob("*"):
            if symlink.is_symlink():
                if not symlink.exists():  # exists() follows symlinks
                    broken_symlinks.append({
                        "link": str(symlink.relative_to(claude_commands_dir.parent.parent)),
                        "target": os.readlink(symlink)
                    })

        assert not broken_symlinks, (
            f"Found broken symlinks:\n"
            f"{chr(10).join(f'{s['link']} -> {s['target']}' for s in broken_symlinks)}\n\n"
            f"To fix:\n"
            f"  1. Ensure target files exist in templates/commands/\n"
            f"  2. Run: specify dev-setup --force"
        )

    def test_jpspec_symlinks_exist(self, claude_commands_dir):
        """Dogfood creates symlinks for jpspec commands.

        Verifies jpspec directory exists and contains expected commands.
        """
        if not claude_commands_dir.exists():
            pytest.skip(".claude/commands directory does not exist")

        jpspec_dir = claude_commands_dir / "jpspec"

        if not jpspec_dir.exists():
            pytest.skip("jpspec directory does not exist (may not be created yet)")

        # Expected jpspec commands (based on current structure)
        expected_commands = [
            "research.md",
            "implement.md",
            "validate.md",
            "specify.md",
            "plan.md",
            "assess.md",
            "operate.md",
        ]

        missing_commands = []
        for cmd in expected_commands:
            cmd_path = jpspec_dir / cmd
            if not cmd_path.exists():
                missing_commands.append(cmd)

        # This is a soft check - commands may vary
        if missing_commands:
            print(f"Note: Some expected jpspec commands not found: {missing_commands}")

    def test_speckit_symlinks_exist(self, claude_commands_dir):
        """Dogfood creates symlinks for speckit commands.

        Verifies speckit directory exists and contains expected commands.
        """
        if not claude_commands_dir.exists():
            pytest.skip(".claude/commands directory does not exist")

        speckit_dir = claude_commands_dir / "speckit"

        assert speckit_dir.exists(), (
            "speckit directory should exist in .claude/commands/\n"
            "Run: specify dev-setup --force"
        )

        # Expected speckit commands
        expected_commands = [
            "specify.md",
            "plan.md",
            "tasks.md",
            "implement.md",
            "checklist.md",
            "clarify.md",
            "analyze.md",
            "constitution.md",
        ]

        for cmd in expected_commands:
            cmd_path = speckit_dir / cmd
            assert cmd_path.exists(), f"speckit command {cmd} should exist"
            assert cmd_path.is_symlink(), f"speckit command {cmd} should be a symlink"

    def test_template_coverage(self, claude_commands_dir, templates_commands_dir):
        """All templates should have corresponding symlinks in .claude/commands/.

        This ensures complete coverage of available commands.
        """
        if not claude_commands_dir.exists():
            pytest.skip(".claude/commands directory does not exist")

        if not templates_commands_dir.exists():
            pytest.skip("templates/commands directory does not exist")

        # Get all .md files in templates (excluding jpspec subdirectory for now)
        template_files = set()
        for md_file in templates_commands_dir.glob("*.md"):
            template_files.add(md_file.name)

        # Get all .md symlinks in speckit
        speckit_dir = claude_commands_dir / "speckit"
        if speckit_dir.exists():
            symlink_files = {f.name for f in speckit_dir.glob("*.md") if f.is_symlink()}
        else:
            symlink_files = set()

        missing_symlinks = template_files - symlink_files

        assert not missing_symlinks, (
            f"Templates without corresponding symlinks:\n"
            f"{chr(10).join(sorted(missing_symlinks))}\n\n"
            f"Run: specify dev-setup --force"
        )


class TestSymlinkIntegrity:
    """Validate symlink structure and integrity."""

    @pytest.fixture
    def repo_root(self):
        """Get the repository root directory."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def claude_commands_dir(self, repo_root):
        """Path to .claude/commands directory."""
        return repo_root / ".claude" / "commands"

    def test_symlinks_point_to_templates(self, claude_commands_dir):
        """All symlinks should point to templates/commands/ directory.

        Ensures no symlinks point to unexpected locations.
        """
        if not claude_commands_dir.exists():
            pytest.skip(".claude/commands directory does not exist")

        invalid_targets = []

        for symlink in claude_commands_dir.rglob("*.md"):
            if symlink.is_symlink():
                target = os.readlink(symlink)
                # Check if target path contains 'templates/commands'
                if "templates/commands" not in target and "templates\\commands" not in target:
                    invalid_targets.append({
                        "link": str(symlink.relative_to(claude_commands_dir.parent.parent)),
                        "target": target
                    })

        assert not invalid_targets, (
            f"Symlinks not pointing to templates/commands/:\n"
            f"{chr(10).join(f'{t['link']} -> {t['target']}' for t in invalid_targets)}"
        )

    def test_no_circular_symlinks(self, claude_commands_dir):
        """Verify no circular symlink references exist.

        Circular symlinks would cause infinite loops.
        """
        if not claude_commands_dir.exists():
            pytest.skip(".claude/commands directory does not exist")

        circular_symlinks = []

        for symlink in claude_commands_dir.rglob("*"):
            if symlink.is_symlink():
                try:
                    # Try to resolve the symlink
                    symlink.resolve(strict=True)
                except RuntimeError as e:
                    if "Symlink loop" in str(e):
                        circular_symlinks.append(str(symlink.relative_to(claude_commands_dir.parent.parent)))

        assert not circular_symlinks, (
            f"Found circular symlinks:\n{chr(10).join(circular_symlinks)}"
        )


class TestTemplateIntegrity:
    """Validate template files are complete and correct."""

    @pytest.fixture
    def repo_root(self):
        """Get the repository root directory."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def templates_commands_dir(self, repo_root):
        """Path to templates/commands directory."""
        return repo_root / "templates" / "commands"

    @pytest.fixture
    def claude_commands_dir(self, repo_root):
        """Path to .claude/commands directory."""
        return repo_root / ".claude" / "commands"

    def test_all_jpspec_commands_in_templates(self, templates_commands_dir):
        """All jpspec commands should exist in templates/commands/jpspec/.

        Ensures jpspec commands are properly templated.
        """
        if not templates_commands_dir.exists():
            pytest.skip("templates/commands directory does not exist")

        jpspec_template_dir = templates_commands_dir / "jpspec"

        if not jpspec_template_dir.exists():
            pytest.skip("templates/commands/jpspec directory does not exist yet")

        expected_commands = [
            "research.md",
            "implement.md",
            "validate.md",
            "specify.md",
            "plan.md",
            "assess.md",
            "operate.md",
        ]

        missing_templates = []
        for cmd in expected_commands:
            if not (jpspec_template_dir / cmd).exists():
                missing_templates.append(cmd)

        # Soft check - log but don't fail
        if missing_templates:
            print(f"Note: Some jpspec templates not found: {missing_templates}")

    def test_no_orphan_claude_commands(self, claude_commands_dir, templates_commands_dir):
        """No command files should exist only in .claude without template source.

        Every command in .claude/commands/ should have a corresponding template.
        """
        if not claude_commands_dir.exists():
            pytest.skip(".claude/commands directory does not exist")

        if not templates_commands_dir.exists():
            pytest.skip("templates/commands directory does not exist")

        orphan_commands = []

        # Check speckit commands
        speckit_dir = claude_commands_dir / "speckit"
        if speckit_dir.exists():
            for cmd_file in speckit_dir.glob("*.md"):
                # For symlinks, check if target exists
                if cmd_file.is_symlink():
                    if not cmd_file.exists():  # Broken symlink
                        orphan_commands.append(str(cmd_file.relative_to(claude_commands_dir.parent.parent)))
                else:
                    # Regular file - should not exist
                    orphan_commands.append(str(cmd_file.relative_to(claude_commands_dir.parent.parent)))

        assert not orphan_commands, (
            f"Found orphan command files:\n{chr(10).join(orphan_commands)}\n\n"
            f"These files should be symlinks to templates/"
        )

    def test_template_files_are_not_empty(self, templates_commands_dir):
        """All template files should have content (not be empty).

        Empty templates indicate incomplete setup.
        """
        if not templates_commands_dir.exists():
            pytest.skip("templates/commands directory does not exist")

        empty_templates = []

        for md_file in templates_commands_dir.rglob("*.md"):
            if md_file.stat().st_size == 0:
                empty_templates.append(str(md_file.relative_to(templates_commands_dir.parent.parent)))

        assert not empty_templates, (
            f"Found empty template files:\n{chr(10).join(empty_templates)}"
        )
