"""Tests for dev-setup and init command equivalence.

Tests verify that dev-setup (symlinks) and init (copies) produce equivalent
command sets with consistent subdirectory structure.

Validation Rules:
- R6: dev-setup creates same file set as init would copy
- R7: Subdirectory structure matches expected command namespaces

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

    def test_specflow_symlinks_match_templates(
        self, claude_commands_dir: Path, templates_dir: Path
    ) -> None:
        """Test dev-setup creates specflow symlinks for all active specflow templates.

        Note: Deprecated templates (_DEPRECATED_*.md) are excluded as they are
        documentation artifacts, not active commands.

        Supports two symlink strategies:
        1. Directory-level symlink: .claude/commands/specflow -> templates/commands/specflow
        2. File-level symlinks: individual files are symlinks to template files
        """
        specflow_templates_dir = templates_dir / "specflow"
        specflow_commands_dir = claude_commands_dir / "specflow"

        if not specflow_templates_dir.exists():
            pytest.skip("No templates/commands/specflow directory")
        if not specflow_commands_dir.exists():
            pytest.skip("No .claude/commands/specflow directory")

        # Only check active templates (exclude deprecated)
        template_files = {
            f.name
            for f in specflow_templates_dir.glob("*.md")
            if f.is_file() and _is_active_template(f.name)
        }

        # Check if directory itself is a symlink (directory-level strategy)
        if specflow_commands_dir.is_symlink():
            # Directory-level symlink - files inside match templates
            command_files = {
                f.name
                for f in specflow_commands_dir.glob("*.md")
                if f.is_file() and _is_active_template(f.name)
            }
        else:
            # File-level symlinks - check individual symlinks
            command_files = {
                f.name
                for f in specflow_commands_dir.glob("*.md")
                if f.is_symlink() and _is_active_template(f.name)
            }

        assert template_files == command_files, (
            f"Specflow symlink mismatch.\n"
            f"Templates only: {sorted(template_files - command_files)}\n"
            f"Commands only: {sorted(command_files - template_files)}"
        )

    def test_speckit_symlinks_match_templates(
        self, claude_commands_dir: Path, templates_dir: Path
    ) -> None:
        """Test dev-setup creates speckit symlinks for all speckit templates.

        Supports two symlink strategies:
        1. Directory-level symlink: .claude/commands/speckit -> templates/commands/speckit
        2. File-level symlinks: individual files are symlinks to template files
        """
        speckit_templates_dir = templates_dir / "speckit"
        speckit_commands_dir = claude_commands_dir / "speckit"

        if not speckit_templates_dir.exists():
            pytest.skip("No templates/commands/speckit directory")
        if not speckit_commands_dir.exists():
            pytest.skip("No .claude/commands/speckit directory")

        template_files = {
            f.name for f in speckit_templates_dir.glob("*.md") if f.is_file()
        }

        # Check if directory itself is a symlink (directory-level strategy)
        if speckit_commands_dir.is_symlink():
            # Directory-level symlink - files inside match templates
            command_files = {
                f.name for f in speckit_commands_dir.glob("*.md") if f.is_file()
            }
        else:
            # File-level symlinks - check individual symlinks
            command_files = {
                f.name for f in speckit_commands_dir.glob("*.md") if f.is_symlink()
            }

        assert template_files == command_files, (
            f"Speckit symlink mismatch.\n"
            f"Templates only: {sorted(template_files - command_files)}\n"
            f"Commands only: {sorted(command_files - template_files)}"
        )

    def test_init_would_copy_same_files(
        self, claude_commands_dir: Path, templates_dir: Path
    ) -> None:
        """Test that init would copy the same active files dev-setup links to (R6).

        Note: Deprecated templates (_DEPRECATED_*.md) are excluded as they are
        documentation artifacts, not active commands.

        Supports two symlink strategies:
        1. Directory-level symlink: .claude/commands/<namespace> -> templates/commands/<namespace>
        2. File-level symlinks: individual files are symlinks to template files
        """
        dev_setup_files: set[str] = set()
        init_files: set[str] = set()

        # Collect active dev-setup files (supports directory or file symlinks)
        specflow_commands = claude_commands_dir / "specflow"
        if specflow_commands.exists():
            is_dir_symlink = specflow_commands.is_symlink()
            for f in specflow_commands.glob("*.md"):
                # If directory is symlink, check is_file; otherwise check is_symlink
                if is_dir_symlink:
                    if f.is_file() and _is_active_template(f.name):
                        dev_setup_files.add(f"specflow/{f.name}")
                elif f.is_symlink() and _is_active_template(f.name):
                    dev_setup_files.add(f"specflow/{f.name}")

        speckit_commands = claude_commands_dir / "speckit"
        if speckit_commands.exists():
            is_dir_symlink = speckit_commands.is_symlink()
            for f in speckit_commands.glob("*.md"):
                if is_dir_symlink:
                    if f.is_file() and _is_active_template(f.name):
                        dev_setup_files.add(f"speckit/{f.name}")
                elif f.is_symlink() and _is_active_template(f.name):
                    dev_setup_files.add(f"speckit/{f.name}")

        # Collect active init templates (exclude deprecated)
        specflow_templates = templates_dir / "specflow"
        if specflow_templates.exists():
            for template in specflow_templates.glob("*.md"):
                if template.is_file() and _is_active_template(template.name):
                    init_files.add(f"specflow/{template.name}")

        speckit_templates = templates_dir / "speckit"
        if speckit_templates.exists():
            for template in speckit_templates.glob("*.md"):
                if template.is_file() and _is_active_template(template.name):
                    init_files.add(f"speckit/{template.name}")

        assert dev_setup_files == init_files, (
            f"File set mismatch between dev-setup and init.\n"
            f"Dev-setup only: {sorted(dev_setup_files - init_files)}\n"
            f"Init only: {sorted(init_files - dev_setup_files)}"
        )


class TestSubdirectoryStructure:
    """Verify subdirectory structure matches between dev-setup and init.

    R7: Subdirectory structure matches expected command namespaces
    (specflow/, speckit/, and role-based namespaces: arch/, dev/, ops/, pm/, qa/, sec/)
    """

    def test_specflow_subdirectory_exists(self, claude_commands_dir: Path) -> None:
        """Test specflow subdirectory exists in .claude/commands/."""
        specflow_dir = claude_commands_dir / "specflow"
        assert specflow_dir.exists(), "specflow subdirectory does not exist"
        assert specflow_dir.is_dir(), "specflow is not a directory"

    def test_speckit_subdirectory_exists(self, claude_commands_dir: Path) -> None:
        """Test speckit subdirectory exists in .claude/commands/."""
        speckit_dir = claude_commands_dir / "speckit"
        assert speckit_dir.exists(), "speckit subdirectory does not exist"
        assert speckit_dir.is_dir(), "speckit is not a directory"

    def test_no_extra_subdirectories(self, claude_commands_dir: Path) -> None:
        """Test only expected command namespace subdirectories exist.

        Expected namespaces include specflow, speckit, and role-based directories
        (arch, dev, ops, qa, sec) as defined in specflow_workflow.yml.
        """
        if not claude_commands_dir.exists():
            pytest.skip("No .claude/commands directory")

        subdirs = {d.name for d in claude_commands_dir.iterdir() if d.is_dir()}

        extra_subdirs = subdirs - EXPECTED_COMMAND_NAMESPACES
        assert not extra_subdirs, (
            f"Unexpected subdirectory structure.\n"
            f"Expected: {sorted(EXPECTED_COMMAND_NAMESPACES)}\n"
            f"Found: {sorted(subdirs)}\n"
            f"Extra: {sorted(extra_subdirs)}"
        )

    def test_templates_subdirectory_structure_matches(
        self, templates_dir: Path
    ) -> None:
        """Test templates directory has matching specflow and speckit subdirectories."""
        specflow_templates = templates_dir / "specflow"
        assert specflow_templates.exists(), "templates/commands/specflow does not exist"
        assert specflow_templates.is_dir(), (
            "templates/commands/specflow is not a directory"
        )

        specflow_files = list(specflow_templates.glob("*.md"))
        assert len(specflow_files) > 0, "No specflow template files found"

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

    def test_specflow_contains_only_symlinks(self, claude_commands_dir: Path) -> None:
        """Test specflow directory contains only symlinks, no direct files.

        Supports two strategies:
        1. Directory-level symlink: .claude/commands/specflow -> templates/commands/specflow
        2. File-level symlinks: individual files are symlinks to template files
        """
        specflow_dir = claude_commands_dir / "specflow"
        if not specflow_dir.exists():
            pytest.skip("No .claude/commands/specflow directory")

        # Directory-level symlink is valid
        if specflow_dir.is_symlink():
            return  # Pass - directory itself is a symlink to templates

        # Otherwise, check for file-level symlinks
        all_md_files = list(specflow_dir.glob("*.md"))
        direct_files = [f for f in all_md_files if not f.is_symlink()]

        assert len(direct_files) == 0, (
            f"Direct .md files found in specflow/:\n"
            f"{', '.join(f.name for f in direct_files)}"
        )

    def test_speckit_contains_only_symlinks(self, claude_commands_dir: Path) -> None:
        """Test speckit directory contains only symlinks, no direct files.

        Supports two strategies:
        1. Directory-level symlink: .claude/commands/speckit -> templates/commands/speckit
        2. File-level symlinks: individual files are symlinks to template files
        """
        speckit_dir = claude_commands_dir / "speckit"
        if not speckit_dir.exists():
            pytest.skip("No .claude/commands/speckit directory")

        # Directory-level symlink is valid
        if speckit_dir.is_symlink():
            return  # Pass - directory itself is a symlink to templates

        # Otherwise, check for file-level symlinks
        all_md_files = list(speckit_dir.glob("*.md"))
        direct_files = [f for f in all_md_files if not f.is_symlink()]

        assert len(direct_files) == 0, (
            f"Direct .md files found in speckit/:\n"
            f"{', '.join(f.name for f in direct_files)}"
        )

    def test_all_symlinks_resolve_correctly(self, claude_commands_dir: Path) -> None:
        """Test all symlinks resolve to existing files (R2)."""
        broken_symlinks: list[str] = []

        for subdir in ["specflow", "speckit"]:
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

        specflow_dir = claude_commands_dir / "specflow"
        specflow_templates = templates_dir / "specflow"
        if specflow_dir.exists():
            for symlink in specflow_dir.glob("*.md"):
                if symlink.is_symlink():
                    target = symlink.resolve()
                    try:
                        target.relative_to(specflow_templates)
                    except ValueError:
                        invalid_targets.append(
                            f"specflow/{symlink.name} -> {target} (expected under {specflow_templates})"
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
        """Test symlink count is stable (dev-setup was already run).

        Supports two symlink strategies:
        1. Directory-level symlink: the directory itself is a symlink
        2. File-level symlinks: individual files are symlinks
        """
        specflow_dir = claude_commands_dir / "specflow"
        speckit_dir = claude_commands_dir / "speckit"

        if not specflow_dir.exists() or not speckit_dir.exists():
            pytest.skip("dev-setup not initialized")

        # For directory-level symlinks, check the directory is symlinked
        # For file-level symlinks, count individual file symlinks
        if specflow_dir.is_symlink():
            specflow_count = len(list(specflow_dir.glob("*.md")))
        else:
            specflow_count = len(
                [f for f in specflow_dir.glob("*.md") if f.is_symlink()]
            )

        if speckit_dir.is_symlink():
            speckit_count = len(list(speckit_dir.glob("*.md")))
        else:
            speckit_count = len([f for f in speckit_dir.glob("*.md") if f.is_symlink()])

        assert specflow_count > 0, "No specflow commands found"
        assert speckit_count > 0, "No speckit commands found"

    def test_no_duplicate_symlinks(self, claude_commands_dir: Path) -> None:
        """Test no duplicate symlink names exist."""
        for subdir in ["specflow", "speckit"]:
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

        for subdir in ["specflow", "speckit"]:
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

    R4: Every active template has corresponding symlink
    R5: No orphan symlinks

    Note: Deprecated templates (_DEPRECATED_*.md) are excluded as they are
    documentation artifacts, not active commands.
    """

    def test_all_specflow_templates_have_symlinks(
        self, templates_dir: Path, claude_commands_dir: Path
    ) -> None:
        """Test every active specflow template has a corresponding symlink (R4)."""
        specflow_templates = templates_dir / "specflow"
        specflow_commands = claude_commands_dir / "specflow"

        if not specflow_templates.exists() or not specflow_commands.exists():
            pytest.skip("specflow directories not found")

        # Only check active templates (exclude deprecated)
        template_files = {
            f.name
            for f in specflow_templates.glob("*.md")
            if _is_active_template(f.name)
        }
        symlink_files = {f.name for f in specflow_commands.glob("*.md")}

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

        # Check specflow
        specflow_templates = templates_dir / "specflow"
        specflow_commands = claude_commands_dir / "specflow"
        if specflow_templates.exists() and specflow_commands.exists():
            template_files = {f.name for f in specflow_templates.glob("*.md")}
            symlink_files = {f.name for f in specflow_commands.glob("*.md")}
            orphan_symlinks.extend(
                f"specflow/{n}" for n in symlink_files - template_files
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
