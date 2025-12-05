"""Tests for dev-setup and init command equivalence.

Tests verify that dev-setup (symlinks) and init (copies) produce equivalent
command sets with consistent subdirectory structure.

Validation Rules:
- R6: dev-setup creates same file set as init would copy
- R7: Subdirectory structure matches (jpspec/, speckit/)

References:
- docs/architecture/command-single-source-of-truth.md
- docs/architecture/adr-001-single-source-of-truth.md
"""

from pathlib import Path

import pytest


@pytest.fixture
def source_repo_root() -> Path:
    """Return path to jp-spec-kit source repository root."""
    return Path(__file__).parent.parent


@pytest.fixture
def templates_dir(source_repo_root: Path) -> Path:
    """Return path to templates/commands directory."""
    return source_repo_root / "templates" / "commands"


@pytest.fixture
def claude_commands_dir(source_repo_root: Path) -> Path:
    """Return path to .claude/commands directory."""
    return source_repo_root / ".claude" / "commands"


class TestDevSetupInitEquivalence:
    """Verify dev-setup symlinks match what init would copy.

    R6: dev-setup creates same file set as init would copy
    """

    def test_jpspec_symlinks_match_templates(
        self, claude_commands_dir: Path, templates_dir: Path
    ) -> None:
        """Test dev-setup creates jpspec symlinks for all jpspec templates."""
        jpspec_templates_dir = templates_dir / "jpspec"
        jpspec_commands_dir = claude_commands_dir / "jpspec"

        if not jpspec_templates_dir.exists():
            pytest.skip("No templates/commands/jpspec directory")
        if not jpspec_commands_dir.exists():
            pytest.skip("No .claude/commands/jpspec directory")

        template_files = {
            f.name for f in jpspec_templates_dir.glob("*.md") if f.is_file()
        }
        symlink_files = {
            f.name for f in jpspec_commands_dir.glob("*.md") if f.is_symlink()
        }

        assert template_files == symlink_files, (
            f"Jpspec symlink mismatch.\n"
            f"Templates only: {sorted(template_files - symlink_files)}\n"
            f"Symlinks only: {sorted(symlink_files - template_files)}"
        )

    def test_speckit_symlinks_match_templates(
        self, claude_commands_dir: Path, templates_dir: Path
    ) -> None:
        """Test dev-setup creates speckit symlinks for all speckit templates."""
        speckit_templates_dir = templates_dir / "speckit"
        speckit_commands_dir = claude_commands_dir / "speckit"

        if not speckit_templates_dir.exists():
            pytest.skip("No templates/commands/speckit directory")
        if not speckit_commands_dir.exists():
            pytest.skip("No .claude/commands/speckit directory")

        template_files = {
            f.name for f in speckit_templates_dir.glob("*.md") if f.is_file()
        }
        symlink_files = {
            f.name for f in speckit_commands_dir.glob("*.md") if f.is_symlink()
        }

        assert template_files == symlink_files, (
            f"Speckit symlink mismatch.\n"
            f"Templates only: {sorted(template_files - symlink_files)}\n"
            f"Symlinks only: {sorted(symlink_files - template_files)}"
        )

    def test_init_would_copy_same_files(
        self, claude_commands_dir: Path, templates_dir: Path
    ) -> None:
        """Test that init would copy the same files dev-setup links to (R6)."""
        dev_setup_files: set[str] = set()
        init_files: set[str] = set()

        # Collect dev-setup symlinks
        jpspec_commands = claude_commands_dir / "jpspec"
        if jpspec_commands.exists():
            for symlink in jpspec_commands.glob("*.md"):
                if symlink.is_symlink():
                    dev_setup_files.add(f"jpspec/{symlink.name}")

        speckit_commands = claude_commands_dir / "speckit"
        if speckit_commands.exists():
            for symlink in speckit_commands.glob("*.md"):
                if symlink.is_symlink():
                    dev_setup_files.add(f"speckit/{symlink.name}")

        # Collect init templates
        jpspec_templates = templates_dir / "jpspec"
        if jpspec_templates.exists():
            for template in jpspec_templates.glob("*.md"):
                if template.is_file():
                    init_files.add(f"jpspec/{template.name}")

        speckit_templates = templates_dir / "speckit"
        if speckit_templates.exists():
            for template in speckit_templates.glob("*.md"):
                if template.is_file():
                    init_files.add(f"speckit/{template.name}")

        assert dev_setup_files == init_files, (
            f"File set mismatch between dev-setup and init.\n"
            f"Dev-setup only: {sorted(dev_setup_files - init_files)}\n"
            f"Init only: {sorted(init_files - dev_setup_files)}"
        )


class TestSubdirectoryStructure:
    """Verify subdirectory structure matches between dev-setup and init.

    R7: Subdirectory structure matches (jpspec/, speckit/)
    """

    def test_jpspec_subdirectory_exists(self, claude_commands_dir: Path) -> None:
        """Test jpspec subdirectory exists in .claude/commands/."""
        jpspec_dir = claude_commands_dir / "jpspec"
        assert jpspec_dir.exists(), "jpspec subdirectory does not exist"
        assert jpspec_dir.is_dir(), "jpspec is not a directory"

    def test_speckit_subdirectory_exists(self, claude_commands_dir: Path) -> None:
        """Test speckit subdirectory exists in .claude/commands/."""
        speckit_dir = claude_commands_dir / "speckit"
        assert speckit_dir.exists(), "speckit subdirectory does not exist"
        assert speckit_dir.is_dir(), "speckit is not a directory"

    def test_no_extra_subdirectories(self, claude_commands_dir: Path) -> None:
        """Test only jpspec and speckit subdirectories exist."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory")

        subdirs = {d.name for d in claude_commands_dir.iterdir() if d.is_dir()}
        expected_subdirs = {"jpspec", "speckit"}

        assert subdirs == expected_subdirs, (
            f"Unexpected subdirectory structure.\n"
            f"Expected: {sorted(expected_subdirs)}\n"
            f"Found: {sorted(subdirs)}\n"
            f"Extra: {sorted(subdirs - expected_subdirs)}\n"
            f"Missing: {sorted(expected_subdirs - subdirs)}"
        )

    def test_templates_subdirectory_structure_matches(
        self, templates_dir: Path
    ) -> None:
        """Test templates directory has matching jpspec and speckit subdirectories."""
        jpspec_templates = templates_dir / "jpspec"
        assert jpspec_templates.exists(), "templates/commands/jpspec does not exist"
        assert jpspec_templates.is_dir(), "templates/commands/jpspec is not a directory"

        jpspec_files = list(jpspec_templates.glob("*.md"))
        assert len(jpspec_files) > 0, "No jpspec template files found"

        speckit_templates = templates_dir / "speckit"
        assert speckit_templates.exists(), "templates/commands/speckit does not exist"
        assert speckit_templates.is_dir(), (
            "templates/commands/speckit is not a directory"
        )

        speckit_files = list(speckit_templates.glob("*.md"))
        assert len(speckit_files) > 0, "No speckit template files found"

    def test_no_direct_files_in_commands_root(self, claude_commands_dir: Path) -> None:
        """Test no direct .md files exist in .claude/commands/ root."""
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory")

        direct_files = [f.name for f in claude_commands_dir.glob("*.md") if f.is_file()]

        assert len(direct_files) == 0, (
            f"Direct .md files found in .claude/commands/ root:\n"
            f"{', '.join(direct_files)}"
        )


class TestDevSetupSymlinkValidation:
    """Validate dev-setup creates only symlinks, no direct files.

    R1: .claude/commands/**/*.md contains ONLY symlinks
    R2: All symlinks resolve to existing files
    R3: All symlinks point to templates/commands/
    """

    def test_jpspec_contains_only_symlinks(self, claude_commands_dir: Path) -> None:
        """Test jpspec directory contains only symlinks, no direct files."""
        jpspec_dir = claude_commands_dir / "jpspec"
        if not jpspec_dir.exists():
            pytest.skip("No .claude/commands/jpspec directory")

        all_md_files = list(jpspec_dir.glob("*.md"))
        direct_files = [f for f in all_md_files if not f.is_symlink()]

        assert len(direct_files) == 0, (
            f"Direct .md files found in jpspec/:\n"
            f"{', '.join(f.name for f in direct_files)}"
        )

    def test_speckit_contains_only_symlinks(self, claude_commands_dir: Path) -> None:
        """Test speckit directory contains only symlinks, no direct files."""
        speckit_dir = claude_commands_dir / "speckit"
        if not speckit_dir.exists():
            pytest.skip("No .claude/commands/speckit directory")

        all_md_files = list(speckit_dir.glob("*.md"))
        direct_files = [f for f in all_md_files if not f.is_symlink()]

        assert len(direct_files) == 0, (
            f"Direct .md files found in speckit/:\n"
            f"{', '.join(f.name for f in direct_files)}"
        )

    def test_all_symlinks_resolve_correctly(self, claude_commands_dir: Path) -> None:
        """Test all symlinks resolve to existing files (R2)."""
        broken_symlinks: list[str] = []

        for subdir in ["jpspec", "speckit"]:
            subdir_path = claude_commands_dir / subdir
            if not subdir_path.exists():
                continue

            for symlink in subdir_path.glob("*.md"):
                if symlink.is_symlink():
                    try:
                        symlink.resolve(strict=True)
                    except (OSError, RuntimeError):
                        broken_symlinks.append(f"{subdir}/{symlink.name}")

        assert len(broken_symlinks) == 0, (
            f"Broken symlinks found:\n{', '.join(broken_symlinks)}"
        )

    def test_all_symlinks_point_to_templates(
        self, claude_commands_dir: Path, templates_dir: Path
    ) -> None:
        """Test all symlinks point to templates/commands/ directory (R3)."""
        invalid_targets: list[str] = []

        jpspec_dir = claude_commands_dir / "jpspec"
        jpspec_templates = templates_dir / "jpspec"
        if jpspec_dir.exists():
            for symlink in jpspec_dir.glob("*.md"):
                if symlink.is_symlink():
                    target = symlink.resolve()
                    try:
                        target.relative_to(jpspec_templates)
                    except ValueError:
                        invalid_targets.append(
                            f"jpspec/{symlink.name} -> {target} (expected under {jpspec_templates})"
                        )

        speckit_dir = claude_commands_dir / "speckit"
        speckit_templates = templates_dir / "speckit"
        if speckit_dir.exists():
            for symlink in speckit_dir.glob("*.md"):
                if symlink.is_symlink():
                    target = symlink.resolve()
                    try:
                        target.relative_to(speckit_templates)
                    except ValueError:
                        invalid_targets.append(
                            f"speckit/{symlink.name} -> {target} (expected under {speckit_templates})"
                        )

        assert len(invalid_targets) == 0, (
            "Symlinks with invalid targets:\n" + "\n".join(invalid_targets)
        )


class TestDevSetupIdempotency:
    """Verify running dev-setup multiple times is safe."""

    def test_symlink_count_stable(self, claude_commands_dir: Path) -> None:
        """Test symlink count is stable (dev-setup was already run)."""
        jpspec_dir = claude_commands_dir / "jpspec"
        speckit_dir = claude_commands_dir / "speckit"

        if not jpspec_dir.exists() or not speckit_dir.exists():
            pytest.skip("dev-setup not initialized")

        jpspec_symlinks = [f for f in jpspec_dir.glob("*.md") if f.is_symlink()]
        speckit_symlinks = [f for f in speckit_dir.glob("*.md") if f.is_symlink()]

        assert len(jpspec_symlinks) > 0, "No jpspec symlinks found"
        assert len(speckit_symlinks) > 0, "No speckit symlinks found"

    def test_no_duplicate_symlinks(self, claude_commands_dir: Path) -> None:
        """Test no duplicate symlink names exist."""
        for subdir in ["jpspec", "speckit"]:
            subdir_path = claude_commands_dir / subdir
            if not subdir_path.exists():
                continue

            names = [f.name for f in subdir_path.glob("*.md") if f.is_symlink()]
            assert len(names) == len(set(names)), (
                f"Duplicate {subdir} symlinks: {names}"
            )

    def test_symlinks_are_relative_not_absolute(
        self, claude_commands_dir: Path
    ) -> None:
        """Test symlinks use relative paths for portability."""
        absolute_symlinks: list[str] = []

        for subdir in ["jpspec", "speckit"]:
            subdir_path = claude_commands_dir / subdir
            if not subdir_path.exists():
                continue

            for symlink in subdir_path.glob("*.md"):
                if symlink.is_symlink():
                    target = symlink.readlink()
                    if target.is_absolute():
                        absolute_symlinks.append(f"{subdir}/{symlink.name} -> {target}")

        assert len(absolute_symlinks) == 0, (
            "Absolute path symlinks found (should be relative):\n"
            + "\n".join(absolute_symlinks)
        )


class TestTemplateCompleteness:
    """Verify template directory completeness.

    R4: Every template has corresponding symlink
    R5: No orphan symlinks
    """

    def test_all_jpspec_templates_have_symlinks(
        self, templates_dir: Path, claude_commands_dir: Path
    ) -> None:
        """Test every jpspec template has a corresponding symlink (R4)."""
        jpspec_templates = templates_dir / "jpspec"
        jpspec_commands = claude_commands_dir / "jpspec"

        if not jpspec_templates.exists() or not jpspec_commands.exists():
            pytest.skip("jpspec directories not found")

        template_files = {f.name for f in jpspec_templates.glob("*.md")}
        symlink_files = {f.name for f in jpspec_commands.glob("*.md")}

        orphan_templates = template_files - symlink_files

        assert len(orphan_templates) == 0, (
            f"Jpspec templates without symlinks:\n{', '.join(sorted(orphan_templates))}"
        )

    def test_all_speckit_templates_have_symlinks(
        self, templates_dir: Path, claude_commands_dir: Path
    ) -> None:
        """Test every speckit template has a corresponding symlink (R4)."""
        speckit_templates = templates_dir / "speckit"
        speckit_commands = claude_commands_dir / "speckit"

        if not speckit_templates.exists() or not speckit_commands.exists():
            pytest.skip("speckit directories not found")

        template_files = {f.name for f in speckit_templates.glob("*.md")}
        symlink_files = {f.name for f in speckit_commands.glob("*.md")}

        orphan_templates = template_files - symlink_files

        assert len(orphan_templates) == 0, (
            f"Speckit templates without symlinks:\n{', '.join(sorted(orphan_templates))}"
        )

    def test_no_orphan_symlinks(
        self, templates_dir: Path, claude_commands_dir: Path
    ) -> None:
        """Test no symlinks exist without corresponding templates (R5)."""
        orphan_symlinks: list[str] = []

        # Check jpspec
        jpspec_templates = templates_dir / "jpspec"
        jpspec_commands = claude_commands_dir / "jpspec"
        if jpspec_templates.exists() and jpspec_commands.exists():
            template_files = {f.name for f in jpspec_templates.glob("*.md")}
            symlink_files = {f.name for f in jpspec_commands.glob("*.md")}
            orphan_symlinks.extend(
                f"jpspec/{n}" for n in symlink_files - template_files
            )

        # Check speckit
        speckit_templates = templates_dir / "speckit"
        speckit_commands = claude_commands_dir / "speckit"
        if speckit_templates.exists() and speckit_commands.exists():
            template_files = {f.name for f in speckit_templates.glob("*.md")}
            symlink_files = {f.name for f in speckit_commands.glob("*.md")}
            orphan_symlinks.extend(
                f"speckit/{n}" for n in symlink_files - template_files
            )

        assert len(orphan_symlinks) == 0, (
            f"Orphan symlinks found:\n{', '.join(sorted(orphan_symlinks))}"
        )
