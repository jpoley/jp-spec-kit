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

# Role-based command namespace directories (from flowspec_workflow.yml)
# These are the expected subdirectories in .claude/commands/
# NOTE: PM role removed - PM work is done via /flowspec workflow commands
EXPECTED_COMMAND_NAMESPACES = {
    "flow",
    "spec",
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
    """Return path to flowspec source repository root."""
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

    def test_flowspec_symlinks_match_templates(
        self, claude_commands_dir: Path, templates_dir: Path
    ) -> None:
        """Test dev-setup creates flowspec symlinks for all active flowspec templates.

        Note: Deprecated templates (_DEPRECATED_*.md) are excluded as they are
        documentation artifacts, not active commands.

        Supports two symlink strategies:
        1. Directory-level symlink: .claude/commands/flow -> templates/commands/flow
        2. File-level symlinks: individual files are symlinks to template files
        """
        flowspec_templates_dir = templates_dir / "flow"
        flowspec_commands_dir = claude_commands_dir / "flow"

        if not flowspec_templates_dir.exists():
            pytest.skip("No templates/commands/flow directory")
        if not flowspec_commands_dir.exists():
            pytest.skip("No .claude/commands/flow directory")

        # Only check active templates (exclude deprecated)
        template_files = {
            f.name
            for f in flowspec_templates_dir.glob("*.md")
            if f.is_file() and _is_active_template(f.name)
        }

        # Check if directory itself is a symlink (directory-level strategy)
        if flowspec_commands_dir.is_symlink():
            # Directory-level symlink - files inside match templates
            command_files = {
                f.name
                for f in flowspec_commands_dir.glob("*.md")
                if f.is_file() and _is_active_template(f.name)
            }
        else:
            # File-level symlinks - check individual symlinks
            command_files = {
                f.name
                for f in flowspec_commands_dir.glob("*.md")
                if f.is_symlink() and _is_active_template(f.name)
            }

        assert template_files == command_files, (
            f"Flowspec symlink mismatch.\n"
            f"Templates only: {sorted(template_files - command_files)}\n"
            f"Commands only: {sorted(command_files - template_files)}"
        )

    def test_spec_symlinks_match_templates(
        self, claude_commands_dir: Path, templates_dir: Path
    ) -> None:
        """Test dev-setup creates spec symlinks for all spec templates.

        Supports two symlink strategies:
        1. Directory-level symlink: .claude/commands/spec -> templates/commands/spec
        2. File-level symlinks: individual files are symlinks to template files
        """
        spec_templates_dir = templates_dir / "spec"
        spec_commands_dir = claude_commands_dir / "spec"

        if not spec_templates_dir.exists():
            pytest.skip("No templates/commands/spec directory")
        if not spec_commands_dir.exists():
            pytest.skip("No .claude/commands/spec directory")

        template_files = {
            f.name for f in spec_templates_dir.glob("*.md") if f.is_file()
        }

        # Check if directory itself is a symlink (directory-level strategy)
        if spec_commands_dir.is_symlink():
            # Directory-level symlink - files inside match templates
            command_files = {
                f.name for f in spec_commands_dir.glob("*.md") if f.is_file()
            }
        else:
            # File-level symlinks - check individual symlinks
            command_files = {
                f.name for f in spec_commands_dir.glob("*.md") if f.is_symlink()
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
        flowspec_commands = claude_commands_dir / "flow"
        if flowspec_commands.exists():
            is_dir_symlink = flowspec_commands.is_symlink()
            for f in flowspec_commands.glob("*.md"):
                # If directory is symlink, check is_file; otherwise check is_symlink
                if is_dir_symlink:
                    if f.is_file() and _is_active_template(f.name):
                        dev_setup_files.add(f"flowspec/{f.name}")
                elif f.is_symlink() and _is_active_template(f.name):
                    dev_setup_files.add(f"flowspec/{f.name}")

        spec_commands = claude_commands_dir / "spec"
        if spec_commands.exists():
            is_dir_symlink = spec_commands.is_symlink()
            for f in spec_commands.glob("*.md"):
                if is_dir_symlink:
                    if f.is_file() and _is_active_template(f.name):
                        dev_setup_files.add(f"spec/{f.name}")
                elif f.is_symlink() and _is_active_template(f.name):
                    dev_setup_files.add(f"spec/{f.name}")

        # Collect active init templates (exclude deprecated)
        flowspec_templates = templates_dir / "flow"
        if flowspec_templates.exists():
            for template in flowspec_templates.glob("*.md"):
                if template.is_file() and _is_active_template(template.name):
                    init_files.add(f"flowspec/{template.name}")

        spec_templates = templates_dir / "spec"
        if spec_templates.exists():
            for template in spec_templates.glob("*.md"):
                if template.is_file() and _is_active_template(template.name):
                    init_files.add(f"spec/{template.name}")

        assert dev_setup_files == init_files, (
            f"File set mismatch between dev-setup and init.\n"
            f"Dev-setup only: {sorted(dev_setup_files - init_files)}\n"
            f"Init only: {sorted(init_files - dev_setup_files)}"
        )


class TestSubdirectoryStructure:
    """Verify subdirectory structure matches between dev-setup and init.

    R7: Subdirectory structure matches expected command namespaces
    (flowspec/, spec/, and role-based namespaces: arch/, dev/, ops/, pm/, qa/, sec/)
    """

    def test_flowspec_subdirectory_exists(self, claude_commands_dir: Path) -> None:
        """Test flowspec subdirectory exists in .claude/commands/."""
        flowspec_dir = claude_commands_dir / "flow"
        assert flowspec_dir.exists(), "flowspec subdirectory does not exist"
        assert flowspec_dir.is_dir(), "flowspec is not a directory"

    def test_spec_subdirectory_exists(self, claude_commands_dir: Path) -> None:
        """Test spec subdirectory exists in .claude/commands/."""
        spec_dir = claude_commands_dir / "spec"
        assert spec_dir.exists(), "spec subdirectory does not exist"
        assert spec_dir.is_dir(), "spec is not a directory"

    def test_no_extra_subdirectories(self, claude_commands_dir: Path) -> None:
        """Test only expected command namespace subdirectories exist.

        Expected namespaces include flowspec, spec, and role-based directories
        (arch, dev, ops, qa, sec) as defined in flowspec_workflow.yml.
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
        """Test templates directory has matching flowspec and spec subdirectories."""
        flowspec_templates = templates_dir / "flow"
        assert flowspec_templates.exists(), "templates/commands/flow does not exist"
        assert flowspec_templates.is_dir(), "templates/commands/flow is not a directory"

        flowspec_files = list(flowspec_templates.glob("*.md"))
        assert len(flowspec_files) > 0, "No flowspec template files found"

        spec_templates = templates_dir / "spec"
        assert spec_templates.exists(), "templates/commands/spec does not exist"
        assert spec_templates.is_dir(), "templates/commands/spec is not a directory"

        spec_files = list(spec_templates.glob("*.md"))
        assert len(spec_files) > 0, "No spec template files found"

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

    def test_flowspec_contains_only_symlinks(self, claude_commands_dir: Path) -> None:
        """Test flowspec directory contains only symlinks, no direct files.

        Supports two strategies:
        1. Directory-level symlink: .claude/commands/flow -> templates/commands/flow
        2. File-level symlinks: individual files are symlinks to template files
        """
        flowspec_dir = claude_commands_dir / "flow"
        if not flowspec_dir.exists():
            pytest.skip("No .claude/commands/flow directory")

        # Directory-level symlink is valid
        if flowspec_dir.is_symlink():
            return  # Pass - directory itself is a symlink to templates

        # Otherwise, check for file-level symlinks
        all_md_files = list(flowspec_dir.glob("*.md"))
        direct_files = [f for f in all_md_files if not f.is_symlink()]

        assert len(direct_files) == 0, (
            f"Direct .md files found in flowspec/:\n"
            f"{', '.join(f.name for f in direct_files)}"
        )

    def test_spec_contains_only_symlinks(self, claude_commands_dir: Path) -> None:
        """Test spec directory contains only symlinks, no direct files.

        Supports two strategies:
        1. Directory-level symlink: .claude/commands/spec -> templates/commands/spec
        2. File-level symlinks: individual files are symlinks to template files
        """
        spec_dir = claude_commands_dir / "spec"
        if not spec_dir.exists():
            pytest.skip("No .claude/commands/spec directory")

        # Directory-level symlink is valid
        if spec_dir.is_symlink():
            return  # Pass - directory itself is a symlink to templates

        # Otherwise, check for file-level symlinks
        all_md_files = list(spec_dir.glob("*.md"))
        direct_files = [f for f in all_md_files if not f.is_symlink()]

        assert len(direct_files) == 0, (
            f"Direct .md files found in spec/:\n"
            f"{', '.join(f.name for f in direct_files)}"
        )

    def test_all_symlinks_resolve_correctly(self, claude_commands_dir: Path) -> None:
        """Test all symlinks resolve to existing files (R2)."""
        broken_symlinks: list[str] = []

        for subdir in ["flow", "spec"]:
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

        flowspec_dir = claude_commands_dir / "flow"
        flowspec_templates = templates_dir / "flow"
        if flowspec_dir.exists():
            for symlink in flowspec_dir.glob("*.md"):
                if symlink.is_symlink():
                    target = symlink.resolve()
                    try:
                        target.relative_to(flowspec_templates)
                    except ValueError:
                        invalid_targets.append(
                            f"flowspec/{symlink.name} -> {target} (expected under {flowspec_templates})"
                        )

        spec_dir = claude_commands_dir / "spec"
        spec_templates = templates_dir / "spec"
        if spec_dir.exists():
            for symlink in spec_dir.glob("*.md"):
                if symlink.is_symlink():
                    target = symlink.resolve()
                    try:
                        target.relative_to(spec_templates)
                    except ValueError:
                        invalid_targets.append(
                            f"spec/{symlink.name} -> {target} (expected under {spec_templates})"
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
        flowspec_dir = claude_commands_dir / "flow"
        spec_dir = claude_commands_dir / "spec"

        if not flowspec_dir.exists() or not spec_dir.exists():
            pytest.skip("dev-setup not initialized")

        # For directory-level symlinks, check the directory is symlinked
        # For file-level symlinks, count individual file symlinks
        if flowspec_dir.is_symlink():
            flowspec_count = len(list(flowspec_dir.glob("*.md")))
        else:
            flowspec_count = len(
                [f for f in flowspec_dir.glob("*.md") if f.is_symlink()]
            )

        if spec_dir.is_symlink():
            spec_count = len(list(spec_dir.glob("*.md")))
        else:
            spec_count = len([f for f in spec_dir.glob("*.md") if f.is_symlink()])

        assert flowspec_count > 0, "No flowspec commands found"
        assert spec_count > 0, "No spec commands found"

    def test_no_duplicate_symlinks(self, claude_commands_dir: Path) -> None:
        """Test no duplicate symlink names exist."""
        for subdir in ["flow", "spec"]:
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

        for subdir in ["flow", "spec"]:
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

    def test_all_flowspec_templates_have_symlinks(
        self, templates_dir: Path, claude_commands_dir: Path
    ) -> None:
        """Test every active flowspec template has a corresponding symlink (R4)."""
        flowspec_templates = templates_dir / "flow"
        flowspec_commands = claude_commands_dir / "flow"

        if not flowspec_templates.exists() or not flowspec_commands.exists():
            pytest.skip("flowspec directories not found")

        # Only check active templates (exclude deprecated)
        template_files = {
            f.name
            for f in flowspec_templates.glob("*.md")
            if _is_active_template(f.name)
        }
        symlink_files = {f.name for f in flowspec_commands.glob("*.md")}

        orphan_templates = template_files - symlink_files

        assert len(orphan_templates) == 0, (
            f"Flowspec templates without symlinks:\n{', '.join(sorted(orphan_templates))}"
        )

    def test_all_spec_templates_have_symlinks(
        self, templates_dir: Path, claude_commands_dir: Path
    ) -> None:
        """Test every spec template has a corresponding symlink (R4)."""
        spec_templates = templates_dir / "spec"
        spec_commands = claude_commands_dir / "spec"

        if not spec_templates.exists() or not spec_commands.exists():
            pytest.skip("spec directories not found")

        template_files = {f.name for f in spec_templates.glob("*.md")}
        symlink_files = {f.name for f in spec_commands.glob("*.md")}

        orphan_templates = template_files - symlink_files

        assert len(orphan_templates) == 0, (
            f"Speckit templates without symlinks:\n{', '.join(sorted(orphan_templates))}"
        )

    def test_no_orphan_symlinks(
        self, templates_dir: Path, claude_commands_dir: Path
    ) -> None:
        """Test no symlinks exist without corresponding templates (R5)."""
        orphan_symlinks: list[str] = []

        # Check flowspec
        flowspec_templates = templates_dir / "flow"
        flowspec_commands = claude_commands_dir / "flow"
        if flowspec_templates.exists() and flowspec_commands.exists():
            template_files = {f.name for f in flowspec_templates.glob("*.md")}
            symlink_files = {f.name for f in flowspec_commands.glob("*.md")}
            orphan_symlinks.extend(
                f"flowspec/{n}" for n in symlink_files - template_files
            )

        # Check spec
        spec_templates = templates_dir / "spec"
        spec_commands = claude_commands_dir / "spec"
        if spec_templates.exists() and spec_commands.exists():
            template_files = {f.name for f in spec_templates.glob("*.md")}
            symlink_files = {f.name for f in spec_commands.glob("*.md")}
            orphan_symlinks.extend(f"spec/{n}" for n in symlink_files - template_files)

        assert len(orphan_symlinks) == 0, (
            f"Orphan symlinks found:\n{', '.join(sorted(orphan_symlinks))}"
        )
