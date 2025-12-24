"""Tests for skill deployment functionality in flowspec init command.

Tests cover:
- Skills deployment from templates/skills/ to .claude/skills/
- --skip-skills flag functionality
- --force flag for overwriting existing skills
- Proper SKILL.md directory structure preservation
- Handling of symlinks in templates/skills/
"""

import re
from unittest.mock import patch

from typer.testing import CliRunner

from flowspec_cli import app
from flowspec_cli.skills import deploy_skills


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text.

    CI output may include color codes that break substring matching.
    """
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


runner = CliRunner()


class TestSkillsDeployFunction:
    """Tests for the deploy_skills function."""

    def test_deploy_skills_creates_directory(self, tmp_path):
        """Test that deploy_skills creates .claude/skills/ directory."""
        # Create mock templates/skills/ directory
        templates_skills = tmp_path / "templates" / "skills"
        templates_skills.mkdir(parents=True)

        # Create a mock skill
        skill_dir = templates_skills / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Test Skill\nTest content")

        # Create project root
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Mock _find_templates_skills_dir to return our test templates
        with patch(
            "flowspec_cli.skills.scaffold._find_templates_skills_dir",
            return_value=templates_skills,
        ):
            deployed = deploy_skills(project_root)

        # Verify skill was deployed
        assert len(deployed) == 1
        deployed_skill = project_root / ".claude" / "skills" / "test-skill" / "SKILL.md"
        assert deployed_skill.exists()
        assert "Test Skill" in deployed_skill.read_text()

    def test_deploy_skills_skips_symlinks(self, tmp_path):
        """Test that deploy_skills skips symlinks in templates/skills/."""
        templates_skills = tmp_path / "templates" / "skills"
        templates_skills.mkdir(parents=True)

        # Create a real skill
        skill_dir = templates_skills / "real-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Real Skill")

        # Create a symlink (simulating context-extractor symlink)
        symlink_target = tmp_path / "elsewhere" / "symlink-target"
        symlink_target.mkdir(parents=True)
        (symlink_target / "SKILL.md").write_text("# Symlink Skill")

        symlink_dir = templates_skills / "symlink-skill"
        symlink_dir.symlink_to(symlink_target)

        # Verify symlink exists
        assert symlink_dir.is_symlink()

        # Deploy skills should skip symlinks
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Mock _find_templates_skills_dir to return our test templates
        with patch(
            "flowspec_cli.skills.scaffold._find_templates_skills_dir",
            return_value=templates_skills,
        ):
            deployed = deploy_skills(project_root)

        # Verify: only real skill was deployed (symlink skipped)
        assert len(deployed) == 1
        skills_dest = project_root / ".claude" / "skills"
        assert (skills_dest / "real-skill" / "SKILL.md").exists()
        assert not (skills_dest / "symlink-skill").exists()

    def test_deploy_skills_skip_flag(self, tmp_path):
        """Test that skip_skills=True skips deployment."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        # Call deploy_skills with skip_skills=True
        deployed = deploy_skills(project_root, skip_skills=True)

        # Should return empty list
        assert deployed == []

        # .claude/skills/ should not be created
        skills_dir = project_root / ".claude" / "skills"
        assert not skills_dir.exists()

    def test_deploy_skills_no_overwrite_without_force(self, tmp_path):
        """Test that existing skills are not overwritten without force flag."""
        templates_skills = tmp_path / "templates" / "skills"
        templates_skills.mkdir(parents=True)

        # Create mock skill in templates
        skill_dir = templates_skills / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# New Version")

        # Create existing skill in project
        project_root = tmp_path / "project"
        skills_dest = project_root / ".claude" / "skills" / "test-skill"
        skills_dest.mkdir(parents=True)
        existing_skill = skills_dest / "SKILL.md"
        existing_skill.write_text("# Old Version")

        # Mock _find_templates_skills_dir and deploy without force
        with patch(
            "flowspec_cli.skills.scaffold._find_templates_skills_dir",
            return_value=templates_skills,
        ):
            deployed = deploy_skills(project_root, force=False)

        # Should not overwrite - returns empty list
        assert deployed == []
        # Old version should remain unchanged
        assert "Old Version" in existing_skill.read_text()
        assert "New Version" not in existing_skill.read_text()

    def test_deploy_skills_overwrites_with_force(self, tmp_path):
        """Test that force=True overwrites existing skills."""
        templates_skills = tmp_path / "templates" / "skills"
        templates_skills.mkdir(parents=True)

        # Create mock skill in templates
        skill_dir = templates_skills / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# New Version")

        # Create existing skill in project
        project_root = tmp_path / "project"
        skills_dest = project_root / ".claude" / "skills" / "test-skill"
        skills_dest.mkdir(parents=True)
        existing_skill = skills_dest / "SKILL.md"
        existing_skill.write_text("# Old Version")

        # Mock _find_templates_skills_dir and deploy with force
        with patch(
            "flowspec_cli.skills.scaffold._find_templates_skills_dir",
            return_value=templates_skills,
        ):
            deployed = deploy_skills(project_root, force=True)

        # Should overwrite - returns the deployed path
        assert len(deployed) == 1
        # New version should replace old
        assert "New Version" in existing_skill.read_text()
        assert "Old Version" not in existing_skill.read_text()


class TestSkillsInInit:
    """Tests for skills deployment in flowspec init command."""

    def test_init_deploys_skills_by_default(self, tmp_path):
        """Test that flowspec init deploys skills by default."""
        result = runner.invoke(
            app,
            [
                "init",
                str(tmp_path / "test-project"),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--constitution",
                "light",
            ],
            input="n\n",  # Answer 'no' to backlog-md install prompt
        )

        # Check exit code
        assert result.exit_code == 0, (
            f"Expected exit code 0, got {result.exit_code}. Output: {result.stdout}"
        )

        # Verify skills directory exists
        skills_dir = tmp_path / "test-project" / ".claude" / "skills"
        assert skills_dir.exists(), ".claude/skills/ should be created"

        # Verify at least one skill was deployed
        deployed_skills = list(skills_dir.iterdir())
        # Filter out any hidden files
        deployed_skills = [s for s in deployed_skills if not s.name.startswith(".")]

        # We should have at least one skill deployed
        # (The actual number depends on templates/skills/ content)
        assert len(deployed_skills) > 0, "At least one skill should be deployed"

        # Verify each deployed skill has SKILL.md
        for skill_path in deployed_skills:
            if skill_path.is_dir():
                skill_md = skill_path / "SKILL.md"
                assert skill_md.exists(), f"{skill_path.name} should have SKILL.md"

    def test_init_skip_skills_flag(self, tmp_path):
        """Test that --skip-skills flag prevents skill deployment."""
        result = runner.invoke(
            app,
            [
                "init",
                str(tmp_path / "test-project"),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--constitution",
                "light",
                "--skip-skills",
            ],
            input="n\n",  # Answer 'no' to backlog-md install prompt
        )

        # Check exit code
        assert result.exit_code == 0, (
            f"Expected exit code 0, got {result.exit_code}. Output: {result.stdout}"
        )

        # Verify skills are NOT deployed when --skip-skills is used
        skills_dir = tmp_path / "test-project" / ".claude" / "skills"
        if skills_dir.exists():
            # Directory may exist but should be empty
            skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]
            assert len(skill_dirs) == 0, (
                f"No skills should be deployed with --skip-skills, but found: {[d.name for d in skill_dirs]}"
            )

    def test_init_force_flag_overwrites_skills(self, tmp_path):
        """Test that --force flag overwrites existing skills."""
        import os

        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        # Pre-create a skill with distinct old content
        skills_dir = project_dir / ".claude" / "skills" / "pm-planner"
        skills_dir.mkdir(parents=True)
        old_skill = skills_dir / "SKILL.md"
        old_content = "# Old PM Planner Skill\nOld content that should be replaced"
        old_skill.write_text(old_content)

        # Change to project directory and run init with --here and --force
        original_cwd = os.getcwd()
        try:
            os.chdir(str(project_dir))
            result = runner.invoke(
                app,
                [
                    "init",
                    "--here",
                    "--ai",
                    "claude",
                    "--ignore-agent-tools",
                    "--constitution",
                    "light",
                    "--force",
                ],
                input="n\n",  # Answer 'no' to backlog-md install prompt
            )
        finally:
            os.chdir(original_cwd)

        # Init with --force should succeed
        assert result.exit_code == 0, (
            f"Expected exit code 0, got {result.exit_code}. Output: {result.stdout}"
        )

        # Skill should be overwritten - verify content changed
        new_content = old_skill.read_text()
        assert new_content != old_content, (
            "Skill content should have changed with --force"
        )
        # The new content should not contain our old marker
        assert "Old content that should be replaced" not in new_content


class TestSkillsHelpText:
    """Tests for --skip-skills flag in CLI help."""

    def test_init_help_shows_skills_options(self):
        """Verify --skip-skills flag and skills-related options appear in init help."""
        result = runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0

        # Check for 'skip-skills' in help
        # Strip ANSI codes that CI output may include (breaks substring matching)
        stdout_lower = strip_ansi(result.stdout).lower()
        assert "skip-skills" in stdout_lower, "Help should mention --skip-skills flag"
        # Also verify "skill" appears (covers help text about skills)
        assert "skill" in stdout_lower, "Help should mention skills"


class TestSkillsStructure:
    """Tests for skill directory structure."""

    def test_deployed_skills_maintain_structure(self, tmp_path):
        """Test that deployed skills maintain SKILL.md directory structure."""
        # This test verifies the structure after deployment
        project_dir = tmp_path / "test-project"

        result = runner.invoke(
            app,
            [
                "init",
                str(project_dir),
                "--ai",
                "claude",
                "--ignore-agent-tools",
                "--constitution",
                "light",
            ],
            input="n\n",
        )

        assert result.exit_code == 0

        skills_dir = project_dir / ".claude" / "skills"
        if skills_dir.exists():
            for skill_path in skills_dir.iterdir():
                if skill_path.is_dir() and not skill_path.name.startswith("."):
                    # Each skill should be a directory with SKILL.md
                    skill_md = skill_path / "SKILL.md"
                    assert skill_md.exists(), (
                        f"Skill {skill_path.name} should have SKILL.md"
                    )

                    # Verify SKILL.md has frontmatter with name and description
                    content = skill_md.read_text()
                    assert "---" in content, "SKILL.md should have YAML frontmatter"
                    assert "name:" in content or "description:" in content, (
                        "SKILL.md should have metadata"
                    )
