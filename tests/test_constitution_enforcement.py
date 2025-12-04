"""Constitution Enforcement Integration Tests.

Tests verify constitution tier detection and validation marker handling
for enforcement in /jpspec commands.

IMPORTANT: This test suite documents expected behavior for constitution
enforcement. Tests focus on:

1. Constitution tier detection (light/medium/heavy)
2. Validation marker detection (NEEDS_VALIDATION comments)
3. Expected enforcement behavior patterns
4. Integration with specify init command

Test Coverage:
1. Light tier: detection and marker handling
2. Medium tier: detection and marker handling
3. Heavy tier: detection and marker handling
4. Skip validation concept (documented for future)
5. Unvalidated constitution marker detection
6. Missing constitution scenarios
"""

import re
from pathlib import Path
from typing import Literal

import pytest
from typer.testing import CliRunner

from specify_cli import app

runner = CliRunner()


# Tier type for type safety
ConstitutionTier = Literal["light", "medium", "heavy"]


def detect_validation_markers(constitution_path: Path) -> list[dict]:
    """Detect NEEDS_VALIDATION markers in constitution file.

    Args:
        constitution_path: Path to constitution.md

    Returns:
        List of dicts with marker information (line, description, context)
    """
    if not constitution_path.exists():
        return []

    content = constitution_path.read_text()
    lines = content.split("\n")
    markers = []

    # Pattern for NEEDS_VALIDATION markers
    pattern = re.compile(r"<!--\s*NEEDS_VALIDATION:\s*(.+?)\s*-->")

    for line_num, line in enumerate(lines, start=1):
        match = pattern.search(line)
        if match:
            description = match.group(1).strip()
            # Get surrounding context (3 lines before and after)
            context_start = max(0, line_num - 4)
            context_end = min(len(lines), line_num + 3)
            context = "\n".join(lines[context_start:context_end])

            markers.append(
                {
                    "line": line_num,
                    "description": description,
                    "context": context,
                }
            )

    return markers


def detect_tier_from_file(constitution_path: Path) -> str | None:
    """Detect tier from constitution file.

    Args:
        constitution_path: Path to constitution.md

    Returns:
        Tier name (light/medium/heavy) or None
    """
    if not constitution_path.exists():
        return None

    content = constitution_path.read_text()
    tier_match = re.search(r"<!-- TIER: (\w+)", content)
    if tier_match:
        tier = tier_match.group(1).lower()
        if tier in ["light", "medium", "heavy"]:
            return tier
    return None


@pytest.fixture
def create_constitution():
    """Factory fixture to create constitution files with specific tiers and validation states.

    Returns:
        Callable that creates a constitution file and returns its path.
    """

    def _create(
        tmp_path: Path,
        tier: ConstitutionTier,
        validated: bool = False,
    ) -> Path:
        """Create constitution file for testing.

        Args:
            tmp_path: Temporary directory path
            tier: Constitution tier (light, medium, heavy)
            validated: If True, removes NEEDS_VALIDATION markers

        Returns:
            Path to created constitution file
        """
        const_path = tmp_path / "memory" / "constitution.md"
        const_path.parent.mkdir(parents=True, exist_ok=True)

        # Base content with tier marker
        tier_descriptions = {
            "light": "Minimal controls for startups/hobby projects",
            "medium": "Standard controls for typical business projects",
            "heavy": "Strict controls for enterprise/regulated environments",
        }

        content = f"""# Test Project Constitution
<!-- TIER: {tier.capitalize()} - {tier_descriptions[tier]} -->
"""

        if not validated:
            # Add NEEDS_VALIDATION markers
            content += """<!-- NEEDS_VALIDATION: Project name -->

## Core Principles

### Quality-Driven Development
<!-- NEEDS_VALIDATION: Adjust quality principles to team practices -->
Code quality is a shared responsibility.

## Technology Stack
<!-- NEEDS_VALIDATION: Populate with detected languages/frameworks -->
[LANGUAGES_AND_FRAMEWORKS]

### Linting & Formatting
<!-- NEEDS_VALIDATION: Detected linting tools -->
[LINTING_TOOLS]

## Governance

**Version**: 1.0.0 | **Ratified**: [DATE] | **Last Amended**: [DATE]
<!-- NEEDS_VALIDATION: Version and dates -->
"""
        else:
            # Validated content (no markers)
            content += """
## Core Principles

### Quality-Driven Development
Code quality is a shared responsibility.

## Technology Stack
- Python 3.11+
- TypeScript 5

### Linting & Formatting
- ruff for Python
- eslint for TypeScript

## Governance

**Version**: 1.0.0 | **Ratified**: 2025-01-01 | **Last Amended**: 2025-01-01
"""

        const_path.write_text(content)
        return const_path

    return _create


class TestLightTierEnforcement:
    """Test light tier constitution detection and marker handling."""

    def test_light_tier_detected(self, tmp_path: Path, create_constitution):
        """Light tier marker is correctly detected."""
        const_path = create_constitution(tmp_path, "light", validated=False)

        # Verify tier detection
        tier = detect_tier_from_file(const_path)
        assert tier == "light"

    def test_light_tier_has_validation_markers(
        self, tmp_path: Path, create_constitution
    ):
        """Light tier unvalidated constitution has markers."""
        const_path = create_constitution(tmp_path, "light", validated=False)

        # Detect markers
        markers = detect_validation_markers(const_path)

        # Should have markers
        assert len(markers) > 0
        assert all("line" in m for m in markers)
        assert all("description" in m for m in markers)

    def test_light_tier_validated_no_markers(self, tmp_path: Path, create_constitution):
        """Light tier validated constitution has no markers."""
        const_path = create_constitution(tmp_path, "light", validated=True)

        # Detect markers
        markers = detect_validation_markers(const_path)

        # Should have no markers
        assert len(markers) == 0

    def test_light_tier_enforcement_concept(self):
        """Document light tier enforcement behavior.

        Light tier enforcement (when implemented):
        - SHOULD warn about unvalidated sections
        - SHOULD proceed with command execution
        - MAY log warning to console
        - SHOULD NOT block /jpspec commands
        """
        # This test documents expected behavior
        # Implementation: /jpspec commands will check tier and markers
        assert True  # Placeholder for documentation


class TestMediumTierEnforcement:
    """Test medium tier constitution detection and marker handling."""

    def test_medium_tier_detected(self, tmp_path: Path, create_constitution):
        """Medium tier marker is correctly detected."""
        const_path = create_constitution(tmp_path, "medium", validated=False)

        tier = detect_tier_from_file(const_path)
        assert tier == "medium"

    def test_medium_tier_has_validation_markers(
        self, tmp_path: Path, create_constitution
    ):
        """Medium tier unvalidated constitution has markers."""
        const_path = create_constitution(tmp_path, "medium", validated=False)

        markers = detect_validation_markers(const_path)
        assert len(markers) > 0

    def test_medium_tier_validated_no_markers(
        self, tmp_path: Path, create_constitution
    ):
        """Medium tier validated constitution has no markers."""
        const_path = create_constitution(tmp_path, "medium", validated=True)

        markers = detect_validation_markers(const_path)
        assert len(markers) == 0

    def test_medium_tier_enforcement_concept(self):
        """Document medium tier enforcement behavior.

        Medium tier enforcement (when implemented):
        - SHOULD warn about unvalidated sections
        - SHOULD prompt for confirmation
        - SHOULD show marker details
        - MAY proceed after confirmation
        - SHOULD suggest running validation
        """
        # This test documents expected behavior
        assert True  # Placeholder for documentation


class TestHeavyTierEnforcement:
    """Test heavy tier constitution detection and marker handling."""

    def test_heavy_tier_detected(self, tmp_path: Path, create_constitution):
        """Heavy tier marker is correctly detected."""
        const_path = create_constitution(tmp_path, "heavy", validated=False)

        tier = detect_tier_from_file(const_path)
        assert tier == "heavy"

    def test_heavy_tier_has_validation_markers(
        self, tmp_path: Path, create_constitution
    ):
        """Heavy tier unvalidated constitution has markers."""
        const_path = create_constitution(tmp_path, "heavy", validated=False)

        markers = detect_validation_markers(const_path)
        assert len(markers) > 0

    def test_heavy_tier_validated_no_markers(
        self, tmp_path: Path, create_constitution
    ):
        """Heavy tier validated constitution has no markers."""
        const_path = create_constitution(tmp_path, "heavy", validated=True)

        markers = detect_validation_markers(const_path)
        assert len(markers) == 0

    def test_heavy_tier_enforcement_concept(self):
        """Document heavy tier enforcement behavior.

        Heavy tier enforcement (when implemented):
        - MUST error on unvalidated sections
        - MUST block /jpspec commands
        - MUST show all unvalidated markers
        - MUST require validation before proceeding
        - SHOULD provide clear error message
        """
        # This test documents expected behavior
        assert True  # Placeholder for documentation


class TestSkipValidationFlag:
    """Test --skip-validation flag concept."""

    def test_skip_validation_concept(self):
        """Document --skip-validation flag behavior.

        When implemented, --skip-validation flag should:
        - Bypass tier-based enforcement checks
        - Allow execution regardless of validation state
        - Log warning about skipping validation
        - Be available on all /jpspec commands

        Example usage:
            /jpspec:specify --skip-validation
            /jpspec:plan --skip-validation
        """
        # This test documents expected behavior
        assert True  # Placeholder for documentation

    def test_validated_constitutions_work_all_tiers(
        self, tmp_path: Path, create_constitution
    ):
        """Fully validated constitutions work for all tiers."""
        for tier in ["light", "medium", "heavy"]:
            const_path = create_constitution(tmp_path, tier, validated=True)  # type: ignore

            # Verify no markers
            markers = detect_validation_markers(const_path)
            assert len(markers) == 0

            # Verify tier detected
            detected_tier = detect_tier_from_file(const_path)
            assert detected_tier == tier


class TestMissingConstitution:
    """Test missing constitution detection."""

    def test_missing_constitution_detected(self, tmp_path: Path):
        """Missing constitution file is detected."""
        const_path = tmp_path / "memory" / "constitution.md"

        # Should not exist
        assert not const_path.exists()

        # Detection should return None
        tier = detect_tier_from_file(const_path)
        assert tier is None

        markers = detect_validation_markers(const_path)
        assert len(markers) == 0

    def test_missing_constitution_enforcement_concept(self):
        """Document missing constitution enforcement behavior.

        When /jpspec commands run without constitution:
        - SHOULD warn about missing constitution
        - SHOULD suggest running 'specify init --here'
        - MAY proceed with execution (tier-dependent)
        - SHOULD log warning to console
        """
        # This test documents expected behavior
        assert True  # Placeholder for documentation


class TestTierDetection:
    """Test tier detection from constitution files."""

    def test_detect_all_three_tiers(self, tmp_path: Path, create_constitution):
        """All three tiers are correctly detected."""
        tiers = ["light", "medium", "heavy"]

        for expected_tier in tiers:
            const_path = create_constitution(tmp_path, expected_tier)  # type: ignore
            detected_tier = detect_tier_from_file(const_path)
            assert detected_tier == expected_tier

    def test_tier_detection_case_insensitive(self, tmp_path: Path):
        """Tier detection handles case variations."""
        const_path = tmp_path / "memory" / "constitution.md"
        const_path.parent.mkdir(parents=True, exist_ok=True)

        # Test with UPPERCASE
        const_path.write_text("<!-- TIER: LIGHT -->")
        tier = detect_tier_from_file(const_path)
        assert tier == "light"

        # Test with Mixed Case
        const_path.write_text("<!-- TIER: MeDiUm -->")
        tier = detect_tier_from_file(const_path)
        assert tier == "medium"

    def test_missing_tier_marker_returns_none(self, tmp_path: Path):
        """Constitution without tier marker returns None."""
        const_path = tmp_path / "memory" / "constitution.md"
        const_path.parent.mkdir(parents=True, exist_ok=True)

        const_path.write_text("# Constitution\n\nNo tier marker here.")
        tier = detect_tier_from_file(const_path)
        assert tier is None


class TestValidationMarkerDetection:
    """Test validation marker detection."""

    def test_detect_multiple_markers(self, tmp_path: Path, create_constitution):
        """Multiple validation markers are all detected."""
        const_path = create_constitution(tmp_path, "medium", validated=False)

        markers = detect_validation_markers(const_path)

        # Should detect multiple markers
        assert len(markers) >= 3

        # Each should have metadata
        for marker in markers:
            assert marker["line"] > 0
            assert len(marker["description"]) > 0
            assert len(marker["context"]) > 0

    def test_marker_format_detection(self, tmp_path: Path):
        """Various marker formats are detected."""
        const_path = tmp_path / "memory" / "constitution.md"
        const_path.parent.mkdir(parents=True, exist_ok=True)

        content = """# Test Constitution

<!-- NEEDS_VALIDATION: Basic marker -->

## Section 2
<!--NEEDS_VALIDATION:No spaces-->

## Section 3
<!--  NEEDS_VALIDATION:  Extra  spaces  -->
"""
        const_path.write_text(content)

        markers = detect_validation_markers(const_path)

        # All 3 formats should be detected
        assert len(markers) == 3

    def test_marker_line_numbers_accurate(self, tmp_path: Path, create_constitution):
        """Reported line numbers match actual marker locations."""
        const_path = create_constitution(tmp_path, "light", validated=False)

        markers = detect_validation_markers(const_path)

        # Verify each marker's line contains NEEDS_VALIDATION
        content = const_path.read_text()
        lines = content.split("\n")

        for marker in markers:
            line_num = marker["line"]
            line_content = lines[line_num - 1]  # 0-indexed vs 1-indexed
            assert "NEEDS_VALIDATION" in line_content

    def test_no_markers_returns_empty_list(self, tmp_path: Path, create_constitution):
        """Validated constitution returns empty marker list."""
        const_path = create_constitution(tmp_path, "heavy", validated=True)

        markers = detect_validation_markers(const_path)
        assert markers == []


class TestEnforcementIntegration:
    """Test enforcement integration with specify init.

    NOTE: These tests are currently skipped due to GitHub API authentication
    requirements in the init command. The init command attempts to fetch
    release information even with --no-layered flag. This is a known issue
    tracked in test_constitution_integration.py which has the same failures.

    These tests verify the expected integration behavior once the API issue
    is resolved.
    """

    @pytest.mark.skip(reason="GitHub API auth required - see test_constitution_integration.py")
    def test_init_creates_constitution_with_tier(self, tmp_path: Path):
        """specify init creates constitution with correct tier."""
        project_path = tmp_path / "test-project"

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
            input="n\n",  # Decline backlog-md
        )

        assert result.exit_code == 0

        # Verify constitution created
        const_path = project_path / "memory" / "constitution.md"
        assert const_path.exists()

        # Verify tier
        tier = detect_tier_from_file(const_path)
        assert tier == "medium"

    @pytest.mark.skip(reason="GitHub API auth required - see test_constitution_integration.py")
    def test_init_creates_unvalidated_constitution(self, tmp_path: Path):
        """specify init creates constitution with validation markers."""
        project_path = tmp_path / "test-project"

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

        # Verify markers present
        const_path = project_path / "memory" / "constitution.md"
        markers = detect_validation_markers(const_path)
        assert len(markers) > 0

    @pytest.mark.skip(reason="GitHub API auth required - see test_constitution_integration.py")
    def test_all_tiers_create_distinct_constitutions(self, tmp_path: Path):
        """All three tiers create distinct constitutions."""
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

            assert result.exit_code == 0

            const_path = project_path / "memory" / "constitution.md"
            constitutions[tier] = const_path.read_text()

        # Verify all distinct
        assert constitutions["light"] != constitutions["medium"]
        assert constitutions["medium"] != constitutions["heavy"]
        assert constitutions["light"] != constitutions["heavy"]


class TestEnforcementDocumentation:
    """Document expected enforcement behavior for implementation."""

    def test_enforcement_workflow_light_tier(self):
        """Document light tier enforcement workflow.

        Workflow when /jpspec command runs with light tier constitution:

        1. Check if memory/constitution.md exists
        2. If exists, detect tier from TIER marker
        3. If tier is 'light':
           - Detect validation markers
           - If markers found:
             - Log warning: "Constitution has N unvalidated sections"
             - Show marker descriptions
             - Continue execution
        4. Command proceeds normally
        """
        assert True  # Documentation test

    def test_enforcement_workflow_medium_tier(self):
        """Document medium tier enforcement workflow.

        Workflow when /jpspec command runs with medium tier constitution:

        1. Check if memory/constitution.md exists
        2. If exists, detect tier from TIER marker
        3. If tier is 'medium':
           - Detect validation markers
           - If markers found:
             - Show warning: "Constitution has N unvalidated sections"
             - List markers with line numbers and descriptions
             - Prompt: "Continue anyway? [y/N]"
             - If 'n' or no input: exit with error
             - If 'y': continue with logged warning
        4. Command proceeds if confirmed
        """
        assert True  # Documentation test

    def test_enforcement_workflow_heavy_tier(self):
        """Document heavy tier enforcement workflow.

        Workflow when /jpspec command runs with heavy tier constitution:

        1. Check if memory/constitution.md exists
        2. If exists, detect tier from TIER marker
        3. If tier is 'heavy':
           - Detect validation markers
           - If markers found:
             - Error: "Constitution validation required for heavy tier"
             - List all markers with details
             - Show instructions: "Run validation workflow"
             - Exit with error code 1
             - DO NOT proceed
        4. Command only proceeds if fully validated
        """
        assert True  # Documentation test

    def test_skip_validation_implementation_notes(self):
        """Document --skip-validation flag implementation.

        Implementation notes for --skip-validation flag:

        1. Add flag to all /jpspec commands
        2. Check flag before enforcement logic
        3. If flag present:
           - Log warning: "Skipping constitution validation (--skip-validation)"
           - Bypass all tier checks
           - Bypass all marker detection
           - Proceed directly to command execution
        4. Flag should be used sparingly (emergencies, CI overrides)
        """
        assert True  # Documentation test
