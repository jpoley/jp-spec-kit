"""Tests for dev-setup validation system.

Tests validate that .claude/commands/ contains ONLY symlinks pointing to
templates/commands/, ensuring single-source-of-truth architecture.

Validation Rules (from ADR-010):
- R1: .claude/commands/**/*.md contains ONLY symlinks
- R2: All symlinks resolve to existing files
- R3: All symlinks point to templates/commands/
- R4: Every template has corresponding symlink
- R5: No orphan symlinks (target exists in templates)

Reference: docs/adr/ADR-010-dev-setup-validation-architecture.md
"""

from pathlib import Path

import pytest


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


class TestSymlinkOnlyRule:
    """Test R1: .claude/commands/**/*.md contains ONLY symlinks.

    Validates that no regular files exist in .claude/commands/, preventing
    accidental direct file creation that would violate single-source-of-truth.
    """

    def test_no_regular_md_files_in_claude_commands(
        self, claude_commands_dir: Path
    ) -> None:
        """Verify no regular .md files exist in .claude/commands/ tree."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory - dev-setup not initialized")

        # Find all .md files (excluding symlinks)
        regular_files: list[Path] = []
        for md_file in claude_commands_dir.rglob("*.md"):
            if not md_file.is_symlink():
                regular_files.append(md_file)

        # Assert with actionable error message
        assert not regular_files, (
            f"Found {len(regular_files)} regular .md file(s) in .claude/commands/. "
            f"Only symlinks are allowed.\n"
            f"Files found:\n"
            + "\n".join(
                f"  - {f.relative_to(claude_commands_dir)}" for f in regular_files
            )
            + "\n\nTo fix:\n"
            f"  cd {claude_commands_dir.parent.parent}\n"
            "  uv run specify dev-setup --force\n"
        )

    def test_all_md_files_are_symlinks(self, claude_commands_dir: Path) -> None:
        """Verify every .md file in .claude/commands/ is a symlink."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory - dev-setup not initialized")

        md_files = list(claude_commands_dir.rglob("*.md"))
        if not md_files:
            pytest.skip("No .md files found in .claude/commands/")

        non_symlinks: list[Path] = []
        for md_file in md_files:
            if not md_file.is_symlink():
                non_symlinks.append(md_file)

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
        """Verify all symlinks in .claude/commands/ resolve to existing files."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory - dev-setup not initialized")

        broken_symlinks: list[tuple[Path, str]] = []
        for symlink in claude_commands_dir.rglob("*.md"):
            if symlink.is_symlink():
                try:
                    target = symlink.resolve(strict=True)
                    if not target.exists():
                        broken_symlinks.append((symlink, str(target)))
                except (OSError, RuntimeError) as e:
                    broken_symlinks.append((symlink, f"Error: {e}"))

        assert not broken_symlinks, (
            f"Found {len(broken_symlinks)} broken symlink(s):\n"
            + "\n".join(
                f"  - {s.relative_to(claude_commands_dir)} -> {t}"
                for s, t in broken_symlinks
            )
            + "\n\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )

    def test_all_symlinks_point_to_templates(
        self, claude_commands_dir: Path, templates_commands_dir: Path
    ) -> None:
        """Verify all symlinks point to templates/commands/ directory."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory - dev-setup not initialized")

        mispointed_symlinks: list[tuple[Path, Path]] = []
        for symlink in claude_commands_dir.rglob("*.md"):
            if symlink.is_symlink():
                try:
                    target = symlink.resolve(strict=True)
                    # Check if target is under templates/commands/
                    if not str(target).startswith(str(templates_commands_dir)):
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

    def test_symlink_targets_exist(
        self, claude_commands_dir: Path, templates_commands_dir: Path
    ) -> None:
        """Verify symlink targets exist in templates/commands/ (R5: No orphans)."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory - dev-setup not initialized")

        orphaned_symlinks: list[tuple[Path, Path]] = []
        for symlink in claude_commands_dir.rglob("*.md"):
            if symlink.is_symlink():
                try:
                    target = symlink.resolve(strict=True)
                    if not target.exists():
                        orphaned_symlinks.append((symlink, target))
                except (OSError, RuntimeError) as e:
                    # Record error details for orphaned symlinks
                    orphaned_symlinks.append((symlink, Path(str(e))))

        assert not orphaned_symlinks, (
            f"Found {len(orphaned_symlinks)} orphaned symlink(s):\n"
            + "\n".join(
                f"  - {s.relative_to(claude_commands_dir)} -> {t}"
                for s, t in orphaned_symlinks
            )
            + "\n\nSymlink targets must exist in templates/commands/\n"
            "\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
            "  # Or restore missing template:\n"
            "  git checkout main -- templates/commands/FILE\n"
        )


class TestTemplateCoverage:
    """Test R4: Every template has corresponding symlink.

    Validates that all templates are properly linked from .claude/commands/,
    ensuring dev-setup creates complete coverage.
    """

    def test_jpspec_templates_have_symlinks(
        self, claude_commands_dir: Path, templates_commands_dir: Path
    ) -> None:
        """Verify every jpspec template has a corresponding symlink."""
        jpspec_templates_dir = templates_commands_dir / "jpspec"
        if not jpspec_templates_dir.exists():
            pytest.skip("No templates/commands/jpspec directory")

        claude_jpspec_dir = claude_commands_dir / "jpspec"
        if not claude_jpspec_dir.exists():
            pytest.skip(
                "No .claude/commands/jpspec directory - dev-setup not initialized"
            )

        # Get all template files
        template_files = [f.name for f in jpspec_templates_dir.glob("*.md")]

        # Get all symlink names
        symlink_files = [f.name for f in claude_jpspec_dir.glob("*.md")]

        missing_symlinks: list[str] = []
        for template in template_files:
            if template not in symlink_files:
                missing_symlinks.append(template)

        assert not missing_symlinks, (
            f"Found {len(missing_symlinks)} jpspec template(s) without symlinks:\n"
            + "\n".join(f"  - {t}" for t in missing_symlinks)
            + "\n\nEvery template must have a corresponding symlink\n"
            "\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )

    def test_speckit_templates_have_symlinks(
        self, claude_commands_dir: Path, templates_commands_dir: Path
    ) -> None:
        """Verify every speckit template has a corresponding symlink."""
        # Speckit templates are top-level in templates/commands/
        speckit_templates = [f.name for f in templates_commands_dir.glob("*.md")]

        if not speckit_templates:
            pytest.skip("No speckit templates found")

        claude_speckit_dir = claude_commands_dir / "speckit"
        if not claude_speckit_dir.exists():
            pytest.skip(
                "No .claude/commands/speckit directory - dev-setup not initialized"
            )

        # Get all symlink names
        symlink_files = [f.name for f in claude_speckit_dir.glob("*.md")]

        missing_symlinks: list[str] = []
        for template in speckit_templates:
            if template not in symlink_files:
                missing_symlinks.append(template)

        assert not missing_symlinks, (
            f"Found {len(missing_symlinks)} speckit template(s) without symlinks:\n"
            + "\n".join(f"  - {t}" for t in missing_symlinks)
            + "\n\nEvery template must have a corresponding symlink\n"
            "\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )

    def test_no_unexpected_symlinks_in_jpspec(
        self, claude_commands_dir: Path, templates_commands_dir: Path
    ) -> None:
        """Verify no orphan symlinks exist in jpspec directory."""
        jpspec_templates_dir = templates_commands_dir / "jpspec"
        claude_jpspec_dir = claude_commands_dir / "jpspec"

        if not claude_jpspec_dir.exists():
            pytest.skip("No .claude/commands/jpspec directory")

        template_files = {f.name for f in jpspec_templates_dir.glob("*.md")}
        symlink_files = [f for f in claude_jpspec_dir.glob("*.md")]

        unexpected_symlinks: list[Path] = []
        for symlink in symlink_files:
            if symlink.name not in template_files:
                unexpected_symlinks.append(symlink)

        assert not unexpected_symlinks, (
            f"Found {len(unexpected_symlinks)} unexpected symlink(s) in jpspec:\n"
            + "\n".join(
                f"  - {s.name} (no matching template)" for s in unexpected_symlinks
            )
            + "\n\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )

    def test_no_unexpected_symlinks_in_speckit(
        self, claude_commands_dir: Path, templates_commands_dir: Path
    ) -> None:
        """Verify no orphan symlinks exist in speckit directory."""
        claude_speckit_dir = claude_commands_dir / "speckit"

        if not claude_speckit_dir.exists():
            pytest.skip("No .claude/commands/speckit directory")

        # Speckit templates are top-level .md files in templates/commands/
        template_files = {f.name for f in templates_commands_dir.glob("*.md")}
        symlink_files = [f for f in claude_speckit_dir.glob("*.md")]

        unexpected_symlinks: list[Path] = []
        for symlink in symlink_files:
            if symlink.name not in template_files:
                unexpected_symlinks.append(symlink)

        assert not unexpected_symlinks, (
            f"Found {len(unexpected_symlinks)} unexpected symlink(s) in speckit:\n"
            + "\n".join(
                f"  - {s.name} (no matching template)" for s in unexpected_symlinks
            )
            + "\n\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )


class TestSubdirectoryStructure:
    """Test R7: Subdirectory structure matches expected layout.

    Validates that .claude/commands/ maintains proper subdirectory structure
    (jpspec/ and speckit/) matching the dev-setup architecture.
    """

    def test_expected_subdirectories_exist(self, claude_commands_dir: Path) -> None:
        """Verify expected subdirectories exist in .claude/commands/."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory - dev-setup not initialized")

        expected_dirs = ["jpspec", "speckit"]
        missing_dirs: list[str] = []

        for expected_dir in expected_dirs:
            dir_path = claude_commands_dir / expected_dir
            if not dir_path.exists():
                missing_dirs.append(expected_dir)

        assert not missing_dirs, (
            "Missing expected subdirectories in .claude/commands/:\n"
            + "\n".join(f"  - {d}/" for d in missing_dirs)
            + "\n\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )

    def test_no_unexpected_subdirectories(self, claude_commands_dir: Path) -> None:
        """Verify no unexpected subdirectories exist in .claude/commands/."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory - dev-setup not initialized")

        expected_dirs = {"jpspec", "speckit"}
        actual_dirs = {d.name for d in claude_commands_dir.iterdir() if d.is_dir()}

        unexpected_dirs = actual_dirs - expected_dirs

        assert not unexpected_dirs, (
            "Found unexpected subdirectories in .claude/commands/:\n"
            + "\n".join(f"  - {d}/" for d in unexpected_dirs)
            + "\n\nExpected structure: jpspec/, speckit/ only\n"
            "\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )

    def test_no_md_files_at_root_level(self, claude_commands_dir: Path) -> None:
        """Verify no .md files exist at .claude/commands/ root level."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory - dev-setup not initialized")

        root_md_files = [f for f in claude_commands_dir.glob("*.md")]

        assert not root_md_files, (
            "Found .md files at .claude/commands/ root (should be in subdirectories):\n"
            + "\n".join(f"  - {f.name}" for f in root_md_files)
            + "\n\nAll .md files must be in jpspec/ or speckit/ subdirectories\n"
            "\nTo fix:\n"
            "  uv run specify dev-setup --force\n"
        )


class TestCompleteCoverage:
    """Integration tests for complete validation coverage.

    Validates that all rules work together to ensure a properly configured
    dev-setup environment.
    """

    def test_complete_validation_passes(
        self, claude_commands_dir: Path, templates_commands_dir: Path
    ) -> None:
        """Run complete validation suite - all rules must pass."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory - dev-setup not initialized")

        errors: list[str] = []

        # R1: Only symlinks
        for md_file in claude_commands_dir.rglob("*.md"):
            if not md_file.is_symlink():
                errors.append(
                    f"R1: Regular file found: {md_file.relative_to(claude_commands_dir)}"
                )

        # R2: All symlinks resolve
        for symlink in claude_commands_dir.rglob("*.md"):
            if symlink.is_symlink():
                try:
                    target = symlink.resolve(strict=True)
                    if not target.exists():
                        errors.append(
                            f"R2: Broken symlink: {symlink.relative_to(claude_commands_dir)}"
                        )
                except (OSError, RuntimeError):
                    errors.append(
                        f"R2: Unresolvable symlink: {symlink.relative_to(claude_commands_dir)}"
                    )

        # R3: All symlinks point to templates/
        for symlink in claude_commands_dir.rglob("*.md"):
            if symlink.is_symlink():
                try:
                    target = symlink.resolve(strict=True)
                    if not str(target).startswith(str(templates_commands_dir)):
                        errors.append(
                            f"R3: Symlink points outside templates: "
                            f"{symlink.relative_to(claude_commands_dir)} -> {target}"
                        )
                except (OSError, RuntimeError):
                    pass  # Already caught by R2

        # R7: Proper subdirectory structure
        expected_dirs = {"jpspec", "speckit"}
        actual_dirs = {d.name for d in claude_commands_dir.iterdir() if d.is_dir()}
        unexpected = actual_dirs - expected_dirs
        if unexpected:
            errors.append(f"R7: Unexpected subdirectories: {', '.join(unexpected)}")

        assert not errors, (
            f"Dev-setup validation failed with {len(errors)} error(s):\n"
            + "\n".join(f"  - {e}" for e in errors)
            + "\n\nTo fix all issues:\n"
            "  uv run specify dev-setup --force\n"
        )

    def test_dev_setup_directory_structure_complete(self, project_root: Path) -> None:
        """Verify complete dev-setup directory structure exists."""
        required_paths = [
            ".claude/commands",
            ".claude/commands/jpspec",
            ".claude/commands/speckit",
            "templates/commands",
            "templates/commands/jpspec",
        ]

        missing_paths: list[str] = []
        for path_str in required_paths:
            path = project_root / path_str
            if not path.exists():
                missing_paths.append(path_str)

        assert not missing_paths, (
            "Missing required dev-setup directories:\n"
            + "\n".join(f"  - {p}" for p in missing_paths)
            + "\n\nTo initialize dev-setup:\n"
            "  uv run specify dev-setup\n"
        )
