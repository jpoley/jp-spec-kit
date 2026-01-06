"""Tests for skill sync functionality in flowspec upgrade-repo command.

Tests cover:
- sync_skills_directory function
- compare_skills_after_extraction function
- SkillSyncResult dataclass
- Backup mechanism for updated skills
- Reporting of added/updated/unchanged skills
"""

from flowspec_cli.skills import (
    SkillSyncResult,
    compare_skills_after_extraction,
    sync_skills_directory,
)


class TestSkillSyncResult:
    """Tests for SkillSyncResult dataclass."""

    def test_empty_result(self):
        """Test that empty result has expected properties."""
        result = SkillSyncResult()
        assert result.added == []
        assert result.updated == []
        assert result.unchanged == []
        assert result.errors == []
        assert result.backup_dir is None
        assert result.total_synced == 0
        assert not result.has_changes
        assert result.summary() == "no skills found"

    def test_added_skills(self):
        """Test result with added skills."""
        result = SkillSyncResult(added=["skill-a", "skill-b"])
        assert result.total_synced == 2
        assert result.has_changes
        assert "2 added" in result.summary()

    def test_updated_skills(self):
        """Test result with updated skills."""
        result = SkillSyncResult(updated=["skill-x"])
        assert result.total_synced == 1
        assert result.has_changes
        assert "1 updated" in result.summary()

    def test_unchanged_skills(self):
        """Test result with unchanged skills."""
        result = SkillSyncResult(unchanged=["skill-1", "skill-2", "skill-3"])
        assert result.total_synced == 0
        assert not result.has_changes
        assert "3 unchanged" in result.summary()

    def test_mixed_result(self):
        """Test result with mixed changes."""
        result = SkillSyncResult(
            added=["new-skill"],
            updated=["changed-skill"],
            unchanged=["same-skill"],
        )
        assert result.total_synced == 2
        assert result.has_changes
        summary = result.summary()
        assert "1 added" in summary
        assert "1 updated" in summary
        assert "1 unchanged" in summary

    def test_errors_in_result(self):
        """Test result with errors."""
        result = SkillSyncResult(
            added=["skill-a"],
            errors=["Failed to sync skill-b"],
        )
        assert "1 added" in result.summary()
        assert "1 errors" in result.summary()


class TestSyncSkillsDirectory:
    """Tests for sync_skills_directory function."""

    def test_sync_new_skills(self, tmp_path):
        """Test syncing skills to empty target directory."""
        # Create source skills
        source_skills = tmp_path / "source" / ".claude" / "skills"
        source_skills.mkdir(parents=True)

        skill_dir = source_skills / "test-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Test Skill\nContent")

        # Create target project (empty)
        project_root = tmp_path / "project"
        project_root.mkdir()

        result = sync_skills_directory(project_root, source_skills)

        assert len(result.added) == 1
        assert "test-skill" in result.added
        assert len(result.updated) == 0
        assert len(result.unchanged) == 0

        # Verify skill was copied
        target_skill = project_root / ".claude" / "skills" / "test-skill" / "SKILL.md"
        assert target_skill.exists()
        assert "Test Skill" in target_skill.read_text()

    def test_sync_unchanged_skills(self, tmp_path):
        """Test that identical skills are reported as unchanged."""
        # Create source skills
        source_skills = tmp_path / "source" / ".claude" / "skills"
        source_skills.mkdir(parents=True)

        skill_dir = source_skills / "existing-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Existing Skill\nSame content")

        # Create target project with same skill
        project_root = tmp_path / "project"
        target_skills = project_root / ".claude" / "skills" / "existing-skill"
        target_skills.mkdir(parents=True)
        (target_skills / "SKILL.md").write_text("# Existing Skill\nSame content")

        result = sync_skills_directory(project_root, source_skills)

        assert len(result.added) == 0
        assert len(result.updated) == 0
        assert len(result.unchanged) == 1
        assert "existing-skill" in result.unchanged

    def test_sync_updated_skills_with_backup(self, tmp_path):
        """Test that differing skills are updated with backup."""
        # Create source skills (new version)
        source_skills = tmp_path / "source" / ".claude" / "skills"
        source_skills.mkdir(parents=True)

        skill_dir = source_skills / "changing-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Updated Skill\nNew content")

        # Create target project with old version
        project_root = tmp_path / "project"
        target_skills = project_root / ".claude" / "skills" / "changing-skill"
        target_skills.mkdir(parents=True)
        (target_skills / "SKILL.md").write_text("# Old Skill\nOld content")

        # Create backup directory
        backup_dir = tmp_path / "backup"
        backup_dir.mkdir()

        result = sync_skills_directory(project_root, source_skills, backup_dir)

        assert len(result.added) == 0
        assert len(result.updated) == 1
        assert "changing-skill" in result.updated
        assert result.backup_dir == backup_dir

        # Verify skill was updated
        target_skill = (
            project_root / ".claude" / "skills" / "changing-skill" / "SKILL.md"
        )
        assert "Updated Skill" in target_skill.read_text()
        assert "New content" in target_skill.read_text()

        # Verify backup was created
        backup_skill = backup_dir / ".claude" / "skills" / "changing-skill" / "SKILL.md"
        assert backup_skill.exists()
        assert "Old Skill" in backup_skill.read_text()

    def test_sync_skips_symlinks(self, tmp_path):
        """Test that symlinks in source are skipped."""
        # Create source skills
        source_skills = tmp_path / "source" / ".claude" / "skills"
        source_skills.mkdir(parents=True)

        # Create a real skill
        skill_dir = source_skills / "real-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("# Real Skill")

        # Create a symlink skill
        symlink_target = tmp_path / "elsewhere"
        symlink_target.mkdir()
        (symlink_target / "SKILL.md").write_text("# Symlink Skill")

        symlink_dir = source_skills / "symlink-skill"
        symlink_dir.symlink_to(symlink_target)

        # Create target project
        project_root = tmp_path / "project"
        project_root.mkdir()

        result = sync_skills_directory(project_root, source_skills)

        # Only real skill should be synced
        assert len(result.added) == 1
        assert "real-skill" in result.added
        assert "symlink-skill" not in result.added

    def test_sync_skips_dirs_without_skill_md(self, tmp_path):
        """Test that directories without SKILL.md are skipped."""
        # Create source skills
        source_skills = tmp_path / "source" / ".claude" / "skills"
        source_skills.mkdir(parents=True)

        # Create a valid skill
        valid_skill = source_skills / "valid-skill"
        valid_skill.mkdir()
        (valid_skill / "SKILL.md").write_text("# Valid Skill")

        # Create an invalid directory (no SKILL.md)
        invalid_dir = source_skills / "not-a-skill"
        invalid_dir.mkdir()
        (invalid_dir / "README.md").write_text("# Not a skill")

        # Create target project
        project_root = tmp_path / "project"
        project_root.mkdir()

        result = sync_skills_directory(project_root, source_skills)

        assert len(result.added) == 1
        assert "valid-skill" in result.added
        assert "not-a-skill" not in result.added

    def test_sync_nonexistent_source(self, tmp_path):
        """Test sync with nonexistent source directory."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        nonexistent = tmp_path / "nonexistent"

        result = sync_skills_directory(project_root, nonexistent)

        assert len(result.added) == 0
        assert len(result.updated) == 0
        assert len(result.unchanged) == 0


class TestCompareSkillsAfterExtraction:
    """Tests for compare_skills_after_extraction function."""

    def test_compare_new_skills(self, tmp_path):
        """Test comparing when new skills are added."""
        # Create project with new skills (after extraction)
        project_root = tmp_path / "project"
        skills_dir = project_root / ".claude" / "skills"
        skills_dir.mkdir(parents=True)

        new_skill = skills_dir / "new-skill"
        new_skill.mkdir()
        (new_skill / "SKILL.md").write_text("# New Skill")

        # Create backup (before extraction - no skills)
        backup_dir = tmp_path / "backup"
        backup_skills = backup_dir / ".claude" / "skills"
        backup_skills.mkdir(parents=True)

        result = compare_skills_after_extraction(project_root, backup_dir)

        assert len(result.added) == 1
        assert "new-skill" in result.added
        assert result.has_changes

    def test_compare_unchanged_skills(self, tmp_path):
        """Test comparing when skills are unchanged."""
        # Create project with skill
        project_root = tmp_path / "project"
        skills_dir = project_root / ".claude" / "skills"
        skills_dir.mkdir(parents=True)

        skill = skills_dir / "same-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("# Same Skill\nSame content")

        # Create backup with identical skill
        backup_dir = tmp_path / "backup"
        backup_skills = backup_dir / ".claude" / "skills"
        backup_skill = backup_skills / "same-skill"
        backup_skill.mkdir(parents=True)
        (backup_skill / "SKILL.md").write_text("# Same Skill\nSame content")

        result = compare_skills_after_extraction(project_root, backup_dir)

        assert len(result.unchanged) == 1
        assert "same-skill" in result.unchanged
        assert not result.has_changes

    def test_compare_updated_skills(self, tmp_path):
        """Test comparing when skills are updated."""
        # Create project with updated skill
        project_root = tmp_path / "project"
        skills_dir = project_root / ".claude" / "skills"
        skills_dir.mkdir(parents=True)

        skill = skills_dir / "updated-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("# Updated Skill\nNew content")

        # Create backup with old version
        backup_dir = tmp_path / "backup"
        backup_skills = backup_dir / ".claude" / "skills"
        backup_skill = backup_skills / "updated-skill"
        backup_skill.mkdir(parents=True)
        (backup_skill / "SKILL.md").write_text("# Old Skill\nOld content")

        result = compare_skills_after_extraction(project_root, backup_dir)

        assert len(result.updated) == 1
        assert "updated-skill" in result.updated
        assert result.has_changes

    def test_compare_mixed_changes(self, tmp_path):
        """Test comparing with mixed add/update/unchanged."""
        # Create project with skills
        project_root = tmp_path / "project"
        skills_dir = project_root / ".claude" / "skills"
        skills_dir.mkdir(parents=True)

        # New skill
        new_skill = skills_dir / "new-skill"
        new_skill.mkdir()
        (new_skill / "SKILL.md").write_text("# New Skill")

        # Updated skill
        updated_skill = skills_dir / "updated-skill"
        updated_skill.mkdir()
        (updated_skill / "SKILL.md").write_text("# Updated Skill\nNew content")

        # Unchanged skill
        unchanged_skill = skills_dir / "unchanged-skill"
        unchanged_skill.mkdir()
        (unchanged_skill / "SKILL.md").write_text("# Unchanged Skill")

        # Create backup
        backup_dir = tmp_path / "backup"
        backup_skills = backup_dir / ".claude" / "skills"
        backup_skills.mkdir(parents=True)

        # Old version of updated skill
        backup_updated = backup_skills / "updated-skill"
        backup_updated.mkdir()
        (backup_updated / "SKILL.md").write_text("# Old Skill\nOld content")

        # Unchanged skill in backup
        backup_unchanged = backup_skills / "unchanged-skill"
        backup_unchanged.mkdir()
        (backup_unchanged / "SKILL.md").write_text("# Unchanged Skill")

        result = compare_skills_after_extraction(project_root, backup_dir)

        assert len(result.added) == 1
        assert len(result.updated) == 1
        assert len(result.unchanged) == 1
        assert "new-skill" in result.added
        assert "updated-skill" in result.updated
        assert "unchanged-skill" in result.unchanged

    def test_compare_no_skills_directory(self, tmp_path):
        """Test comparing when project has no skills directory."""
        project_root = tmp_path / "project"
        project_root.mkdir()

        backup_dir = tmp_path / "backup"
        backup_dir.mkdir()

        result = compare_skills_after_extraction(project_root, backup_dir)

        assert not result.has_changes
        assert len(result.added) == 0
        assert len(result.updated) == 0
        assert len(result.unchanged) == 0

    def test_results_are_sorted(self, tmp_path):
        """Test that results are sorted alphabetically."""
        # Create project with skills in random order
        project_root = tmp_path / "project"
        skills_dir = project_root / ".claude" / "skills"
        skills_dir.mkdir(parents=True)

        for name in ["zebra-skill", "alpha-skill", "beta-skill"]:
            skill = skills_dir / name
            skill.mkdir()
            (skill / "SKILL.md").write_text(f"# {name}")

        # Empty backup
        backup_dir = tmp_path / "backup"
        (backup_dir / ".claude" / "skills").mkdir(parents=True)

        result = compare_skills_after_extraction(project_root, backup_dir)

        assert result.added == ["alpha-skill", "beta-skill", "zebra-skill"]
