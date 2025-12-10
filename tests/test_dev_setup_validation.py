"""Tests for dev-setup validation system.

Tests validate that .claude/commands/ contains ONLY symlinks pointing to
templates/commands/, ensuring single-source-of-truth architecture.

Validation Rules:
- R1: .claude/commands/**/*.md contains ONLY symlinks
- R2: All symlinks resolve to existing files
- R3: All symlinks point to templates/commands/
- R4: Every active template has corresponding symlink
- R5: No orphan symlinks (target exists in templates)
- R7: Subdirectory structure matches expected command namespaces

Note:
- R6 ("dev-setup creates same file set as init would copy") is tested in
  test_dev_setup_init_equivalence.py and is out of scope for this file.
References:
- docs/architecture/command-single-source-of-truth.md
- docs/architecture/adr-001-single-source-of-truth.md
- docs/adr/ADR-role-based-command-namespaces.md
"""

from pathlib import Path

import pytest

# Role-based command namespace directories (from specflow_workflow.yml)
# These are the expected subdirectories in .claude/commands/
# NOTE: PM role removed - PM work is done via /specflow workflow commands
EXPECTED_COMMAND_NAMESPACES = {
    "specflow",
    "speckit",
    "arch",
    "dev",
    "ops",
    "qa",
    "sec",
}


def _is_active_template(filename: str) -> bool:
    """Check if a template file is an active command (not deprecated)."""
    return not filename.startswith("_DEPRECATED_")


@pytest.fixture
def project_root() -> Path:
    """Return path to project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def claude_commands_dir(project_root: Path) -> Path:
    """Return path to .claude/commands directory."""
    return project_root / ".claude" / "commands"


@pytest.fixture
def templates_commands_dir(project_root: Path) -> Path:
    """Return path to templates/commands directory."""
    return project_root / "templates" / "commands"


def _is_under_directory(path: Path, parent: Path) -> bool:
    """Check if path is under parent directory using proper path comparison.

    Uses Path.relative_to() for robust path comparison instead of string
    startswith() which can have false positives with similarly-named directories.
    """
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


class TestSymlinkOnlyRule:
    """Test R1: .claude/commands/**/*.md contains ONLY symlinks.

    Validates that no regular files exist in .claude/commands/, preventing
    accidental direct file creation that would violate single-source-of-truth.
    """

    def test_all_md_files_are_symlinks(self, claude_commands_dir: Path) -> None:
        """Verify every .md file in .claude/commands/ is a symlink (R1)."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory - dev-setup not initialized")

        md_files = list(claude_commands_dir.rglob("*.md"))
        if not md_files:
            pytest.skip("No .md files found in .claude/commands/")

        non_symlinks: list[Path] = [f for f in md_files if not f.is_symlink()]

        assert not non_symlinks, (
            f"Found {len(non_symlinks)} non-symlink .md file(s):\n"
            + "\n".join(
                f"  - {f.relative_to(claude_commands_dir)}" for f in non_symlinks
            )
            + "\n\nAll .md files must be symlinks to templates/commands/\n"
            "\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )


class TestSymlinkResolution:
    """Test R2 & R3: Symlinks resolve and point to templates/commands/.

    Validates that all symlinks are not broken and correctly point to the
    templates directory, not to other locations.
    """

    def test_all_symlinks_resolve(self, claude_commands_dir: Path) -> None:
        """Verify all symlinks in .claude/commands/ resolve to existing files (R2)."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory - dev-setup not initialized")

        broken_symlinks: list[tuple[Path, str]] = []
        for symlink in claude_commands_dir.rglob("*.md"):
            if symlink.is_symlink():
                try:
                    symlink.resolve(strict=True)
                except (OSError, RuntimeError) as e:
                    broken_symlinks.append((symlink, str(e)))

        assert not broken_symlinks, (
            f"Found {len(broken_symlinks)} broken symlink(s):\n"
            + "\n".join(
                f"  - {s.relative_to(claude_commands_dir)} ({t})"
                for s, t in broken_symlinks
            )
            + "\n\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )

    def test_all_symlinks_point_to_templates(
        self, claude_commands_dir: Path, templates_commands_dir: Path
    ) -> None:
        """Verify all symlinks point to templates/commands/ directory (R3)."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory - dev-setup not initialized")

        mispointed_symlinks: list[tuple[Path, Path]] = []
        for symlink in claude_commands_dir.rglob("*.md"):
            if symlink.is_symlink():
                try:
                    target = symlink.resolve(strict=True)
                    if not _is_under_directory(target, templates_commands_dir):
                        mispointed_symlinks.append((symlink, target))
                except (OSError, RuntimeError):
                    # Broken symlinks are caught by test_all_symlinks_resolve
                    pass

        assert not mispointed_symlinks, (
            f"Found {len(mispointed_symlinks)} symlink(s) pointing outside templates/commands/:\n"
            + "\n".join(
                f"  - {s.relative_to(claude_commands_dir)} -> {t}"
                for s, t in mispointed_symlinks
            )
            + f"\n\nAll symlinks must point to {templates_commands_dir}\n"
            "\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )


class TestTemplateCoverage:
    """Test R4 & R5: Template and symlink coverage.

    Validates that all templates are properly linked from .claude/commands/
    and no orphan symlinks exist.
    """

    def test_specflow_templates_have_symlinks(
        self, claude_commands_dir: Path, templates_commands_dir: Path
    ) -> None:
        """Verify every active specflow template has a corresponding symlink (R4).

        Note: Deprecated templates (_DEPRECATED_*.md) are excluded as they are
        documentation artifacts, not active commands.
        """
        specflow_templates_dir = templates_commands_dir / "specflow"
        if not specflow_templates_dir.exists():
            pytest.skip("No templates/commands/specflow directory")

        claude_specflow_dir = claude_commands_dir / "specflow"
        if not claude_specflow_dir.exists():
            pytest.skip(
                "No .claude/commands/specflow directory - dev-setup not initialized"
            )

        # Only check active templates (exclude deprecated)
        template_files = {
            f.name
            for f in specflow_templates_dir.glob("*.md")
            if _is_active_template(f.name)
        }
        symlink_files = {f.name for f in claude_specflow_dir.glob("*.md")}

        missing_symlinks = template_files - symlink_files

        assert not missing_symlinks, (
            f"Found {len(missing_symlinks)} specflow template(s) without symlinks:\n"
            + "\n".join(f"  - {t}" for t in sorted(missing_symlinks))
            + "\n\nEvery active template must have a corresponding symlink\n"
            "\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )

    def test_speckit_templates_have_symlinks(
        self, claude_commands_dir: Path, templates_commands_dir: Path
    ) -> None:
        """Verify every speckit template has a corresponding symlink (R4)."""
        speckit_templates_dir = templates_commands_dir / "speckit"
        speckit_templates = (
            {f.name for f in speckit_templates_dir.glob("*.md")}
            if speckit_templates_dir.exists()
            else set()
        )

        if not speckit_templates:
            pytest.skip("No speckit templates found")

        claude_speckit_dir = claude_commands_dir / "speckit"
        if not claude_speckit_dir.exists():
            pytest.skip(
                "No .claude/commands/speckit directory - dev-setup not initialized"
            )

        symlink_files = {f.name for f in claude_speckit_dir.glob("*.md")}

        missing_symlinks = speckit_templates - symlink_files

        assert not missing_symlinks, (
            f"Found {len(missing_symlinks)} speckit template(s) without symlinks:\n"
            + "\n".join(f"  - {t}" for t in sorted(missing_symlinks))
            + "\n\nEvery template must have a corresponding symlink\n"
            "\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )

    def test_no_orphan_symlinks_in_specflow(
        self, claude_commands_dir: Path, templates_commands_dir: Path
    ) -> None:
        """Verify no orphan symlinks exist in specflow directory (R5)."""
        specflow_templates_dir = templates_commands_dir / "specflow"
        claude_specflow_dir = claude_commands_dir / "specflow"

        if not claude_specflow_dir.exists():
            pytest.skip("No .claude/commands/specflow directory")

        template_files = {f.name for f in specflow_templates_dir.glob("*.md")}
        symlink_files = {f.name for f in claude_specflow_dir.glob("*.md")}

        orphan_symlinks = symlink_files - template_files

        assert not orphan_symlinks, (
            f"Found {len(orphan_symlinks)} orphan symlink(s) in specflow:\n"
            + "\n".join(
                f"  - {s} (no matching template)" for s in sorted(orphan_symlinks)
            )
            + "\n\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )

    def test_no_orphan_symlinks_in_speckit(
        self, claude_commands_dir: Path, templates_commands_dir: Path
    ) -> None:
        """Verify no orphan symlinks exist in speckit directory (R5)."""
        claude_speckit_dir = claude_commands_dir / "speckit"

        if not claude_speckit_dir.exists():
            pytest.skip("No .claude/commands/speckit directory")

        speckit_templates_dir = templates_commands_dir / "speckit"
        template_files = (
            {f.name for f in speckit_templates_dir.glob("*.md")}
            if speckit_templates_dir.exists()
            else set()
        )
        symlink_files = {f.name for f in claude_speckit_dir.glob("*.md")}

        orphan_symlinks = symlink_files - template_files

        assert not orphan_symlinks, (
            f"Found {len(orphan_symlinks)} orphan symlink(s) in speckit:\n"
            + "\n".join(
                f"  - {s} (no matching template)" for s in sorted(orphan_symlinks)
            )
            + "\n\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )


class TestSubdirectoryStructure:
    """Test R7: Subdirectory structure matches expected layout.

    Validates that .claude/commands/ maintains proper subdirectory structure
    (specflow/ and speckit/) matching the dev-setup architecture.
    """

    def test_expected_subdirectories_exist(self, claude_commands_dir: Path) -> None:
        """Verify expected subdirectories exist in .claude/commands/ (R7)."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory - dev-setup not initialized")

        expected_dirs = {"specflow", "speckit"}
        missing_dirs = {
            d for d in expected_dirs if not (claude_commands_dir / d).exists()
        }

        assert not missing_dirs, (
            "Missing expected subdirectories in .claude/commands/:\n"
            + "\n".join(f"  - {d}/" for d in sorted(missing_dirs))
            + "\n\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )

    def test_no_unexpected_subdirectories(self, claude_commands_dir: Path) -> None:
        """Verify no unexpected subdirectories exist in .claude/commands/ (R7).

        Expected namespaces include specflow, speckit, and role-based directories
        (arch, dev, ops, qa, sec) as defined in specflow_workflow.yml.
        """
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory - dev-setup not initialized")

        actual_dirs = {d.name for d in claude_commands_dir.iterdir() if d.is_dir()}

        unexpected_dirs = actual_dirs - EXPECTED_COMMAND_NAMESPACES

        assert not unexpected_dirs, (
            "Found unexpected subdirectories in .claude/commands/:\n"
            + "\n".join(f"  - {d}/" for d in sorted(unexpected_dirs))
            + f"\n\nExpected: {sorted(EXPECTED_COMMAND_NAMESPACES)}\n"
            "\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )

    def test_no_md_files_at_root_level(self, claude_commands_dir: Path) -> None:
        """Verify no .md files exist at .claude/commands/ root level (R7)."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory - dev-setup not initialized")

        root_md_files = list(claude_commands_dir.glob("*.md"))

        assert not root_md_files, (
            "Found .md files at .claude/commands/ root (should be in subdirectories):\n"
            + "\n".join(f"  - {f.name}" for f in root_md_files)
            + "\n\nAll .md files must be in specflow/ or speckit/ subdirectories\n"
            "\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )


class TestDevSetupDirectoryStructure:
    """Integration tests for complete dev-setup validation."""

    def test_dev_setup_directory_structure_complete(self, project_root: Path) -> None:
        """Verify complete dev-setup directory structure exists."""
        required_paths = [
            ".claude/commands",
            ".claude/commands/specflow",
            ".claude/commands/speckit",
            "templates/commands",
            "templates/commands/specflow",
        ]

        missing_paths = [p for p in required_paths if not (project_root / p).exists()]

        assert not missing_paths, (
            "Missing required dev-setup directories:\n"
            + "\n".join(f"  - {p}" for p in missing_paths)
            + "\n\nTo initialize dev-setup:\n"
            "  uv run specify dev-setup\n"
        )
