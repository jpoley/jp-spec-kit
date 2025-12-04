"""Integration tests for constitution template system.

Tests cover the complete workflow of constitution creation, detection, and validation
across different project scenarios.

Test Categories:
1. specify init with --constitution flag tests
2. Empty repo detection and tier prompting
3. Existing project detection without constitution
4. /speckit:constitution command execution (placeholder - requires command implementation)
5. NEEDS_VALIDATION marker handling
6. specify constitution validate command
7. End-to-end workflows
"""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from specify_cli import CONSTITUTION_TIER_CHOICES, app, has_constitution, is_existing_project

runner = CliRunner()


def build_init_args(
    project_path: str | Path,
    *,
    ai: str = "claude",
    constitution: str,
    here: bool = False,
    force: bool = False,
) -> list[str]:
    """Build specify init command arguments for testing.

    Uses --no-layered to avoid GitHub API calls during tests.
    """
    args = ["init"]

    if here:
        args.append("--here")
    else:
        args.append(str(project_path))

    args.extend([
        "--ai", ai,
        "--ignore-agent-tools",
                "--no-layered",
        "--no-layered",  # Avoid GitHub API calls
        "--constitution", constitution,
    ])

    if force:
        args.append("--force")

    return args


class TestSpecifyInitWithConstitutionFlag:
    """Test specify init with --constitution flag variations."""

    def test_init_with_light_constitution(self, tmp_path):
        """Test specify init myproject --constitution light creates light constitution."""
        project_path = tmp_path / "test-light-project"

        result = runner.invoke(
            app,
            build_init_args(project_path, constitution="light"),
            input="n\n",  # Decline backlog-md install
        )

        assert result.exit_code == 0, f"Command failed: {result.stdout}"

        # Verify constitution file created
        constitution_file = project_path / "memory" / "constitution.md"
        assert constitution_file.exists(), "constitution.md not created"

        # Verify content is light tier
        content = constitution_file.read_text()
        assert "TIER: Light" in content, "Light tier marker not found"
        assert "Minimal controls" in content, "Light tier description not found"
        assert len(content) > 100, "Constitution content too short"

    def test_init_with_medium_constitution(self, tmp_path):
        """Test specify init myproject --constitution medium creates medium constitution."""
        project_path = tmp_path / "test-medium-project"

        result = runner.invoke(
            app,
            [
                "init",
                str(project_path),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--no-layered",
                "--constitution",
                "medium",
            ],
            input="n\n",
        )

        assert result.exit_code == 0, f"Command failed: {result.stdout}"

        constitution_file = project_path / "memory" / "constitution.md"
        assert constitution_file.exists()

        content = constitution_file.read_text()
        assert "TIER: Medium" in content, "Medium tier marker not found"
        assert "Standard controls" in content, "Medium tier description not found"

    def test_init_with_heavy_constitution(self, tmp_path):
        """Test specify init myproject --constitution heavy creates heavy constitution."""
        project_path = tmp_path / "test-heavy-project"

        result = runner.invoke(
            app,
            [
                "init",
                str(project_path),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--no-layered",
                "--constitution",
                "heavy",
            ],
            input="n\n",
        )

        assert result.exit_code == 0, f"Command failed: {result.stdout}"

        constitution_file = project_path / "memory" / "constitution.md"
        assert constitution_file.exists()

        content = constitution_file.read_text()
        assert "TIER: Heavy" in content, "Heavy tier marker not found"
        # Check for "Strict controls" which is actual text in template
        assert "Strict controls" in content or "enterprise" in content.lower(), "Heavy tier description not found"

    def test_init_with_invalid_constitution_tier(self, tmp_path):
        """Test invalid constitution tier value shows proper error."""
        project_path = tmp_path / "test-invalid-project"

        result = runner.invoke(
            app,
            [
                "init",
                str(project_path),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--no-layered",
                "--constitution",
                "invalid-tier",
            ],
        )

        # Should fail with error
        assert result.exit_code != 0, "Expected command to fail with invalid tier"

        # Error should mention valid choices
        output_lower = result.stdout.lower()
        assert "invalid" in output_lower or "error" in output_lower
        assert any(tier in output_lower for tier in ["light", "medium", "heavy"])

    def test_init_all_tiers_create_valid_constitutions(self, tmp_path):
        """Test all three tiers create valid, distinct constitutions."""
        tiers = ["light", "medium", "heavy"]
        constitutions = {}

        for tier in tiers:
            project_path = tmp_path / f"project-{tier}"

            result = runner.invoke(
                app,
                [
                    "init",
                    str(project_path),
                    "--ai",
                    "claude",
                    "--ignore-agent-tools",
                "--no-layered",
                    "--constitution",
                    tier,
                ],
                input="n\n",
            )

            assert result.exit_code == 0, f"Failed for tier {tier}"

            constitution_file = project_path / "memory" / "constitution.md"
            assert constitution_file.exists()

            constitutions[tier] = constitution_file.read_text()

        # Verify each constitution is distinct
        assert constitutions["light"] != constitutions["medium"]
        assert constitutions["medium"] != constitutions["heavy"]
        assert constitutions["light"] != constitutions["heavy"]

        # Verify all have NEEDS_VALIDATION markers
        for tier, content in constitutions.items():
            assert "NEEDS_VALIDATION" in content, f"{tier} missing validation markers"


class TestEmptyRepoDetection:
    """Test empty repository detection and tier prompting."""

    def test_fresh_directory_creates_constitution_with_flag(self, tmp_path):
        """Fresh directory with --constitution flag should create constitution."""
        project_path = tmp_path / "fresh-project"

        result = runner.invoke(
            app,
            [
                "init",
                str(project_path),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--no-layered",
                "--constitution",
                "medium",
            ],
            input="n\n",
        )

        assert result.exit_code == 0

        constitution_file = project_path / "memory" / "constitution.md"
        assert constitution_file.exists()

    def test_empty_directory_helper_function(self, tmp_path):
        """Test is_existing_project() returns False for empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        assert not is_existing_project(empty_dir)

    def test_init_here_in_empty_dir_creates_constitution(self, tmp_path, monkeypatch):
        """Test specify init --here in empty directory creates constitution."""
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            app,
            [
                "init",
                "--here",
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--no-layered",
                "--constitution",
                "light",
                "--force",
            ],
            input="n\n",
        )

        assert result.exit_code == 0

        constitution_file = tmp_path / "memory" / "constitution.md"
        assert constitution_file.exists()


class TestExistingProjectDetection:
    """Test existing project detection and constitution creation."""

    def test_git_project_without_constitution_detected(self, tmp_path):
        """Project with .git but no constitution should be detected."""
        (tmp_path / ".git").mkdir()

        assert is_existing_project(tmp_path)
        assert not has_constitution(tmp_path)

    def test_nodejs_project_without_constitution_detected(self, tmp_path):
        """Project with package.json but no constitution should be detected."""
        (tmp_path / "package.json").write_text("{}")

        assert is_existing_project(tmp_path)
        assert not has_constitution(tmp_path)

    def test_python_project_without_constitution_detected(self, tmp_path):
        """Project with pyproject.toml but no constitution should be detected."""
        (tmp_path / "pyproject.toml").write_text("[tool.poetry]")

        assert is_existing_project(tmp_path)
        assert not has_constitution(tmp_path)

    def test_init_here_on_existing_project_creates_constitution(self, tmp_path, monkeypatch):
        """Test init --here on existing project without constitution creates it."""
        # Create existing project markers
        (tmp_path / ".git").mkdir()
        (tmp_path / "package.json").write_text("{}")

        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            app,
            [
                "init",
                "--here",
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--no-layered",
                "--constitution",
                "medium",
                "--force",
            ],
            input="n\n",
        )

        assert result.exit_code == 0

        constitution_file = tmp_path / "memory" / "constitution.md"
        assert constitution_file.exists()

        content = constitution_file.read_text()
        assert "TIER: Medium" in content

    def test_project_with_constitution_detected(self, tmp_path):
        """Project with existing constitution should be detected."""
        memory_dir = tmp_path / "memory"
        memory_dir.mkdir()
        (memory_dir / "constitution.md").write_text("# Constitution")

        assert has_constitution(tmp_path)

    def test_multiple_project_types_detected(self, tmp_path):
        """Test detection of various project types."""
        project_types = [
            (".git", True),
            ("package.json", "{}"),
            ("pyproject.toml", "[tool]"),
            ("Cargo.toml", "[package]"),
            ("go.mod", "module example"),
            ("pom.xml", "<project></project>"),
        ]

        for marker, content in project_types:
            test_dir = tmp_path / f"project-{marker.replace('.', '-')}"
            test_dir.mkdir()

            if content is True:
                # Directory marker
                (test_dir / marker).mkdir()
            else:
                # File marker
                (test_dir / marker).write_text(content)

            assert is_existing_project(test_dir), f"Failed to detect {marker} project"


class TestNeedsValidationMarkers:
    """Test NEEDS_VALIDATION marker handling across tiers."""

    def test_light_template_has_validation_markers(self, tmp_path):
        """Light template should contain NEEDS_VALIDATION markers."""
        project_path = tmp_path / "light-project"

        result = runner.invoke(
            app,
            [
                "init",
                str(project_path),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--no-layered",
                "--constitution",
                "light",
            ],
            input="n\n",
        )

        assert result.exit_code == 0

        constitution_file = project_path / "memory" / "constitution.md"
        content = constitution_file.read_text()

        # Should have multiple validation markers
        marker_count = content.count("NEEDS_VALIDATION")
        assert marker_count > 0, "No validation markers found"
        assert marker_count >= 3, f"Expected at least 3 markers, found {marker_count}"

    def test_medium_template_has_validation_markers(self, tmp_path):
        """Medium template should contain NEEDS_VALIDATION markers."""
        project_path = tmp_path / "medium-project"

        result = runner.invoke(
            app,
            [
                "init",
                str(project_path),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--no-layered",
                "--constitution",
                "medium",
            ],
            input="n\n",
        )

        assert result.exit_code == 0

        constitution_file = project_path / "memory" / "constitution.md"
        content = constitution_file.read_text()

        marker_count = content.count("NEEDS_VALIDATION")
        assert marker_count > 0

    def test_heavy_template_has_validation_markers(self, tmp_path):
        """Heavy template should contain NEEDS_VALIDATION markers."""
        project_path = tmp_path / "heavy-project"

        result = runner.invoke(
            app,
            [
                "init",
                str(project_path),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--no-layered",
                "--constitution",
                "heavy",
            ],
            input="n\n",
        )

        assert result.exit_code == 0

        constitution_file = project_path / "memory" / "constitution.md"
        content = constitution_file.read_text()

        marker_count = content.count("NEEDS_VALIDATION")
        assert marker_count > 0

    def test_marker_format_is_consistent(self, tmp_path):
        """All markers should follow consistent format."""
        project_path = tmp_path / "format-test"

        result = runner.invoke(
            app,
            [
                "init",
                str(project_path),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--no-layered",
                "--constitution",
                "light",
            ],
            input="n\n",
        )

        assert result.exit_code == 0

        constitution_file = project_path / "memory" / "constitution.md"
        content = constitution_file.read_text()

        # Check for HTML comment format
        assert "<!-- NEEDS_VALIDATION:" in content
        assert "-->" in content

        # Verify each marker is properly formatted
        # Only check lines that are actual markers (lines that start with <!--  after stripping)
        lines = content.split("\n")
        marker_lines = [
            line for line in lines
            if line.strip().startswith("<!-- NEEDS_VALIDATION:")
        ]

        assert len(marker_lines) > 0, "No validation marker lines found"

        for line in marker_lines:
            # Marker should be in HTML comment format
            stripped = line.strip()
            assert stripped.startswith("<!--"), f"Marker should start with <!--: {line}"
            assert stripped.endswith("-->"), f"Marker should end with -->: {line}"
            assert "NEEDS_VALIDATION:" in line, f"Missing colon in marker: {line}"


class TestConstitutionValidateCommand:
    """Test specify constitution validate command.

    NOTE: The constitution validate command is tested in test_constitution_validate.py.
    These integration tests verify marker detection in created constitutions.
    Once the validate command is fully implemented, end-to-end tests below will use it.
    """

    def test_created_constitutions_contain_detectable_markers(self, tmp_path):
        """Test that created constitutions have markers that can be validated."""
        project_path = tmp_path / "validation-test"

        result = runner.invoke(
            app,
            [
                "init",
                str(project_path),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--no-layered",
                "--constitution",
                "light",
            ],
            input="n\n",
        )

        assert result.exit_code == 0

        constitution_file = project_path / "memory" / "constitution.md"
        content = constitution_file.read_text()

        # Verify markers can be detected by counting them (only actual marker lines)
        marker_lines = [
            line for line in content.split("\n")
            if line.strip().startswith("<!-- NEEDS_VALIDATION:")
        ]
        assert len(marker_lines) > 0, "No validation markers found"

        # Verify marker format is parseable
        for line in marker_lines:
            assert "<!--" in line, "Marker not in HTML comment format"
            assert "-->" in line, "Marker not properly closed"
            assert "NEEDS_VALIDATION:" in line, "Marker missing colon separator"

    def test_marker_removal_creates_clean_constitution(self, tmp_path):
        """Test that removing markers creates a validatable constitution."""
        project_path = tmp_path / "clean-test"

        # Create project
        runner.invoke(
            app,
            [
                "init",
                str(project_path),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--no-layered",
                "--constitution",
                "medium",
            ],
            input="n\n",
        )

        constitution_file = project_path / "memory" / "constitution.md"
        content = constitution_file.read_text()

        # Remove all NEEDS_VALIDATION lines
        clean_lines = [line for line in content.split("\n") if "NEEDS_VALIDATION" not in line]
        clean_content = "\n".join(clean_lines)

        # Verify no markers remain
        assert "NEEDS_VALIDATION" not in clean_content
        assert len(clean_content) > 100, "Constitution should still have content"

        # Write back to verify it's a valid constitution
        constitution_file.write_text(clean_content)
        assert constitution_file.exists()
        assert constitution_file.read_text() == clean_content


class TestEndToEndWorkflow:
    """Test complete end-to-end constitution workflows.

    NOTE: These tests focus on init and marker handling. Full validation
    command workflows are tested in test_constitution_validate.py.
    """

    def test_complete_workflow_new_project(self, tmp_path):
        """Test complete workflow from init through marker manipulation."""
        project_path = tmp_path / "e2e-project"

        # Step 1: Initialize project with constitution
        result = runner.invoke(
            app,
            [
                "init",
                str(project_path),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--no-layered",
                "--constitution",
                "medium",
            ],
            input="n\n",
        )
        assert result.exit_code == 0, f"Init failed: {result.stdout}"

        # Step 2: Verify constitution created with markers
        constitution_file = project_path / "memory" / "constitution.md"
        assert constitution_file.exists()

        content = constitution_file.read_text()
        initial_marker_count = content.count("NEEDS_VALIDATION")
        assert initial_marker_count > 0, "Should have validation markers"

        # Step 3: Simulate validation by removing markers
        validated_content = "\n".join(
            line for line in content.split("\n")
            if "NEEDS_VALIDATION" not in line
        )
        constitution_file.write_text(validated_content)

        # Step 4: Verify markers removed
        final_content = constitution_file.read_text()
        assert "NEEDS_VALIDATION" not in final_content
        assert len(final_content) > 100, "Constitution should still have content"

    def test_complete_workflow_existing_project(self, tmp_path, monkeypatch):
        """Test workflow for existing project without constitution."""
        # Create existing project
        (tmp_path / ".git").mkdir()
        (tmp_path / "README.md").write_text("# Existing Project")

        monkeypatch.chdir(tmp_path)

        # Step 1: Init --here adds constitution
        result = runner.invoke(
            app,
            [
                "init",
                "--here",
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--no-layered",
                "--constitution",
                "light",
                "--force",
            ],
            input="n\n",
        )
        assert result.exit_code == 0

        # Step 2: Verify constitution exists with markers
        constitution_file = tmp_path / "memory" / "constitution.md"
        assert constitution_file.exists()

        content = constitution_file.read_text()
        assert "NEEDS_VALIDATION" in content, "Should have validation markers"
        assert "TIER: Light" in content, "Should be light tier"

    def test_all_tiers_create_distinct_constitutions(self, tmp_path):
        """Test that all three tiers create distinct, valid constitutions."""
        tiers = ["light", "medium", "heavy"]
        constitutions = {}

        for tier in tiers:
            project_path = tmp_path / f"tier-{tier}"

            # Create project
            result = runner.invoke(
                app,
                [
                    "init",
                    str(project_path),
                    "--ai",
                    "claude",
                    "--ignore-agent-tools",
                "--no-layered",
                    "--constitution",
                    tier,
                ],
                input="n\n",
            )
            assert result.exit_code == 0, f"Init failed for {tier}. Output: {result.stdout}"

            constitution_file = project_path / "memory" / "constitution.md"
            assert constitution_file.exists()

            content = constitution_file.read_text()
            constitutions[tier] = content

            # Verify has markers
            assert "NEEDS_VALIDATION" in content, f"{tier} should have markers"

            # Verify tier marker
            assert f"TIER: {tier.capitalize()}" in content, f"Missing {tier} tier marker"

        # Verify all are distinct
        assert constitutions["light"] != constitutions["medium"]
        assert constitutions["medium"] != constitutions["heavy"]
        assert constitutions["light"] != constitutions["heavy"]

    def test_marker_cleanup_workflow(self, tmp_path):
        """Test workflow of identifying and cleaning up markers."""
        project_path = tmp_path / "cleanup-test"

        # Create project
        runner.invoke(
            app,
            [
                "init",
                str(project_path),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--no-layered",
                "--constitution",
                "light",
            ],
            input="n\n",
        )

        constitution_file = project_path / "memory" / "constitution.md"
        content = constitution_file.read_text()

        # Count initial markers (only actual marker lines, not text mentioning them)
        lines = content.split("\n")
        marker_lines = [line for line in lines if line.strip().startswith("<!-- NEEDS_VALIDATION:")]
        initial_count = len(marker_lines)

        assert initial_count > 0, "Should have markers"

        # Simulate progressive validation - remove one marker at a time
        for i in range(initial_count):
            current_content = constitution_file.read_text()
            current_lines = current_content.split("\n")

            # Remove first marker line
            remaining_lines = []
            removed_one = False
            for line in current_lines:
                if line.strip().startswith("<!-- NEEDS_VALIDATION:") and not removed_one:
                    removed_one = True
                    continue
                remaining_lines.append(line)

            constitution_file.write_text("\n".join(remaining_lines))

            # Verify one less marker
            new_content = constitution_file.read_text()
            remaining_marker_lines = [
                line for line in new_content.split("\n")
                if line.strip().startswith("<!-- NEEDS_VALIDATION:")
            ]
            expected = initial_count - (i + 1)
            assert len(remaining_marker_lines) == expected, (
                f"Expected {expected} markers, found {len(remaining_marker_lines)}"
            )

        # Final check - no marker lines
        final_content = constitution_file.read_text()
        final_marker_lines = [
            line for line in final_content.split("\n")
            if line.strip().startswith("<!-- NEEDS_VALIDATION:")
        ]
        assert len(final_marker_lines) == 0, "Should have no marker lines"


class TestConstitutionTierChoices:
    """Test CONSTITUTION_TIER_CHOICES constant."""

    def test_all_tiers_defined(self):
        """Verify all expected tiers are defined."""
        assert "light" in CONSTITUTION_TIER_CHOICES
        assert "medium" in CONSTITUTION_TIER_CHOICES
        assert "heavy" in CONSTITUTION_TIER_CHOICES

    def test_tier_count(self):
        """Verify exactly 3 tiers."""
        assert len(CONSTITUTION_TIER_CHOICES) == 3

    def test_tier_descriptions_exist(self):
        """Verify tier descriptions are non-empty."""
        for tier, description in CONSTITUTION_TIER_CHOICES.items():
            assert isinstance(description, str)
            assert len(description) > 0


class TestConstitutionHelp:
    """Test help text and documentation."""

    def test_init_help_mentions_constitution(self):
        """Test init help shows constitution option."""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        assert "constitution" in result.stdout.lower()

    def test_init_help_shows_tiers(self):
        """Test init help mentions all tiers."""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0

        output_lower = result.stdout.lower()
        assert "light" in output_lower
        assert "medium" in output_lower
        assert "heavy" in output_lower

    def test_constitution_commands_available(self):
        """Test constitution commands are available."""
        result = runner.invoke(app, ["constitution", "--help"])
        assert result.exit_code == 0
        assert "constitution" in result.stdout.lower()
        # Version command should be available
        assert "version" in result.stdout.lower()
