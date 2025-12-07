"""Unit tests for push_rules module.

Tests cover:
- Pydantic model validation
- YAML frontmatter parsing
- push-rules.md loading and validation
- Edge cases and error handling
"""

from pathlib import Path
from textwrap import dedent

import pytest

from specify_cli.push_rules import (
    JanitorSettings,
    PushRulesConfig,
    PushRulesNotFoundError,
    PushRulesParseError,
    PushRulesValidationError,
    RebaseEnforcement,
    RebasePolicy,
    ValidationCommand,
    load_push_rules,
    validate_push_rules,
)
from specify_cli.push_rules.parser import (
    extract_yaml_frontmatter,
    normalize_yaml_keys,
    parse_markdown_config,
)


class TestRebasePolicy:
    """Tests for RebasePolicy model."""

    def test_defaults(self) -> None:
        """Test default values."""
        policy = RebasePolicy()
        assert policy.enforcement == RebaseEnforcement.STRICT
        assert policy.base_branch == "main"
        assert policy.allow_merge_commits is False

    def test_custom_values(self) -> None:
        """Test custom configuration."""
        policy = RebasePolicy(
            enforcement=RebaseEnforcement.WARN,
            base_branch="develop",
            allow_merge_commits=True,
        )
        assert policy.enforcement == RebaseEnforcement.WARN
        assert policy.base_branch == "develop"
        assert policy.allow_merge_commits is True

    def test_invalid_branch_name_empty(self) -> None:
        """Test that empty branch name is rejected."""
        with pytest.raises(ValueError, match="at least 1 character"):
            RebasePolicy(base_branch="")

    def test_invalid_branch_name_whitespace(self) -> None:
        """Test that whitespace-only branch name is rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            RebasePolicy(base_branch="   ")

    def test_invalid_branch_name_leading_dash(self) -> None:
        """Test that branch names starting with dash are rejected."""
        with pytest.raises(ValueError, match="Invalid branch name"):
            RebasePolicy(base_branch="-invalid")

    def test_invalid_branch_name_double_dot(self) -> None:
        """Test that branch names with .. are rejected."""
        with pytest.raises(ValueError, match="Invalid branch name"):
            RebasePolicy(base_branch="feature..test")


class TestValidationCommand:
    """Tests for ValidationCommand model."""

    def test_required_command(self) -> None:
        """Test that command is required."""
        with pytest.raises(ValueError):
            ValidationCommand()

    def test_valid_command(self) -> None:
        """Test valid command configuration."""
        cmd = ValidationCommand(command="ruff check .")
        assert cmd.required is True
        assert cmd.command == "ruff check ."
        assert cmd.allow_warnings is False
        assert cmd.timeout == 300

    def test_custom_timeout(self) -> None:
        """Test custom timeout value."""
        cmd = ValidationCommand(command="pytest tests/", timeout=600)
        assert cmd.timeout == 600

    def test_timeout_bounds(self) -> None:
        """Test timeout validation bounds."""
        with pytest.raises(ValueError):
            ValidationCommand(command="test", timeout=0)

        with pytest.raises(ValueError):
            ValidationCommand(command="test", timeout=3601)

    def test_empty_command_rejected(self) -> None:
        """Test that empty command is rejected."""
        with pytest.raises(ValueError):
            ValidationCommand(command="")

    def test_whitespace_command_rejected(self) -> None:
        """Test that whitespace-only command is rejected."""
        with pytest.raises(ValueError):
            ValidationCommand(command="   ")


class TestJanitorSettings:
    """Tests for JanitorSettings model."""

    def test_defaults(self) -> None:
        """Test default values."""
        settings = JanitorSettings()
        assert settings.run_after_validation is True
        assert settings.prune_merged_branches is True
        assert settings.clean_stale_worktrees is True
        assert "main" in settings.protected_branches
        assert "master" in settings.protected_branches
        assert "develop" in settings.protected_branches

    def test_custom_protected_branches(self) -> None:
        """Test custom protected branches list."""
        settings = JanitorSettings(protected_branches=["main", "staging"])
        assert settings.protected_branches == ["main", "staging"]

    def test_empty_protected_branches(self) -> None:
        """Test empty protected branches list is allowed."""
        settings = JanitorSettings(protected_branches=[])
        assert settings.protected_branches == []

    def test_protected_branches_validation(self) -> None:
        """Test that invalid branch names in protected list are rejected."""
        with pytest.raises(ValueError, match="Invalid branch name"):
            JanitorSettings(protected_branches=["main", "-invalid"])


class TestPushRulesConfig:
    """Tests for PushRulesConfig model."""

    def test_minimal_config(self) -> None:
        """Test configuration with only defaults."""
        config = PushRulesConfig()
        assert config.version == "1.0"
        assert config.enabled is True
        assert config.bypass_flag == "--skip-push-rules"

    def test_full_config(self) -> None:
        """Test fully specified configuration."""
        config = PushRulesConfig(
            version="1.0",
            enabled=True,
            bypass_flag="--no-validate",
            rebase_policy=RebasePolicy(enforcement=RebaseEnforcement.STRICT),
            lint=ValidationCommand(command="ruff check ."),
            test=ValidationCommand(command="pytest tests/"),
            branch_naming_pattern=r"^feature/.*$",
            enforce_branch_naming=True,
        )
        assert config.is_lint_required() is True
        assert config.is_test_required() is True
        assert config.is_branch_naming_enforced() is True

    def test_invalid_version_format(self) -> None:
        """Test that invalid version format is rejected."""
        with pytest.raises(ValueError):
            PushRulesConfig(version="v1.0")

        with pytest.raises(ValueError):
            PushRulesConfig(version="1")

    def test_invalid_bypass_flag(self) -> None:
        """Test that bypass flag must start with dash."""
        with pytest.raises(ValueError, match="must start with a dash"):
            PushRulesConfig(bypass_flag="skip")

    def test_invalid_regex_pattern(self) -> None:
        """Test that invalid regex patterns are rejected."""
        with pytest.raises(ValueError, match="Invalid regex pattern"):
            PushRulesConfig(branch_naming_pattern="[invalid")

    def test_validate_branch_name_matches(self) -> None:
        """Test branch name validation when pattern matches."""
        config = PushRulesConfig(
            branch_naming_pattern=r"^(feature|fix)/[a-z0-9-]+$",
            enforce_branch_naming=True,
        )
        assert config.validate_branch_name("feature/add-tests") is True
        assert config.validate_branch_name("fix/bug-123") is True

    def test_validate_branch_name_no_match(self) -> None:
        """Test branch name validation when pattern doesn't match."""
        config = PushRulesConfig(
            branch_naming_pattern=r"^(feature|fix)/[a-z0-9-]+$",
            enforce_branch_naming=True,
        )
        assert config.validate_branch_name("my-branch") is False
        assert config.validate_branch_name("Feature/Add-Tests") is False

    def test_validate_branch_name_not_enforced(self) -> None:
        """Test that branch validation passes when not enforced."""
        config = PushRulesConfig(
            branch_naming_pattern=r"^feature/.*$",
            enforce_branch_naming=False,
        )
        assert config.validate_branch_name("any-branch-name") is True


class TestExtractYamlFrontmatter:
    """Tests for YAML frontmatter extraction."""

    def test_valid_frontmatter(self) -> None:
        """Test extraction of valid frontmatter."""
        content = dedent("""
            ---
            version: "1.0"
            enabled: true
            ---

            # Git Push Rules
            """).strip()

        data, end_line = extract_yaml_frontmatter(content)
        assert data == {"version": "1.0", "enabled": True}
        assert end_line == 4

    def test_missing_opening_delimiter(self) -> None:
        """Test error when frontmatter is missing."""
        content = "# No frontmatter here"

        with pytest.raises(PushRulesParseError, match="must start with YAML"):
            extract_yaml_frontmatter(content)

    def test_missing_closing_delimiter(self) -> None:
        """Test error when closing delimiter is missing."""
        content = dedent("""
            ---
            version: "1.0"
            enabled: true
            # No closing delimiter
            """).strip()

        with pytest.raises(PushRulesParseError, match="not closed"):
            extract_yaml_frontmatter(content)

    def test_empty_frontmatter(self) -> None:
        """Test that empty frontmatter returns empty dict."""
        content = dedent("""
            ---
            ---
            # Content
            """).strip()

        data, _ = extract_yaml_frontmatter(content)
        assert data == {}

    def test_invalid_yaml(self) -> None:
        """Test error on invalid YAML content."""
        content = dedent("""
            ---
            invalid: [unclosed
            ---
            """).strip()

        with pytest.raises(PushRulesParseError, match="Invalid YAML"):
            extract_yaml_frontmatter(content)


class TestNormalizeYamlKeys:
    """Tests for key normalization."""

    def test_spaces_to_underscores(self) -> None:
        """Test that spaces become underscores."""
        data = {"Allow Merge Commits": True}
        result = normalize_yaml_keys(data)
        assert result == {"allow_merge_commits": True}

    def test_hyphens_to_underscores(self) -> None:
        """Test that hyphens become underscores."""
        data = {"base-branch": "main"}
        result = normalize_yaml_keys(data)
        assert result == {"base_branch": "main"}

    def test_nested_dicts(self) -> None:
        """Test normalization of nested dicts."""
        data = {
            "Rebase Policy": {
                "Base Branch": "main",
                "Allow Merge Commits": False,
            }
        }
        result = normalize_yaml_keys(data)
        assert result == {
            "rebase_policy": {
                "base_branch": "main",
                "allow_merge_commits": False,
            }
        }


class TestParseMarkdownConfig:
    """Tests for markdown body config extraction."""

    def test_extract_simple_values(self) -> None:
        """Test extraction of simple key-value pairs."""
        content = dedent("""
            ## Section

            - **Enforcement**: strict
            - **Base Branch**: main
            - **Required**: true
            """)

        result = parse_markdown_config(content)
        assert result["Enforcement"] == "strict"
        assert result["Base Branch"] == "main"
        assert result["Required"] is True

    def test_extract_code_values(self) -> None:
        """Test extraction of backtick-wrapped values."""
        content = "- **Command**: `ruff check .`"
        result = parse_markdown_config(content)
        assert result["Command"] == "ruff check ."

    def test_numeric_values(self) -> None:
        """Test extraction of numeric values."""
        content = "- **Timeout**: 300"
        result = parse_markdown_config(content)
        assert result["Timeout"] == 300

    def test_boolean_values(self) -> None:
        """Test extraction of boolean values."""
        content = dedent("""
            - **Enabled**: true
            - **Disabled**: false
            - **Yes**: yes
            - **No**: no
            """)

        result = parse_markdown_config(content)
        assert result["Enabled"] is True
        assert result["Disabled"] is False
        assert result["Yes"] is True
        assert result["No"] is False


class TestLoadPushRules:
    """Tests for loading push-rules.md files."""

    def test_load_valid_file(self, tmp_path: Path) -> None:
        """Test loading a valid push-rules.md file."""
        push_rules = tmp_path / "push-rules.md"
        push_rules.write_text(
            dedent("""
                ---
                version: "1.0"
                enabled: true
                rebase_policy:
                  enforcement: strict
                  base_branch: main
                lint:
                  command: "ruff check ."
                  required: true
                test:
                  command: "pytest tests/"
                  required: true
                ---

                # Git Push Rules
                """).strip()
        )

        config = load_push_rules(push_rules)
        assert config.version == "1.0"
        assert config.enabled is True
        assert config.rebase_policy.enforcement == RebaseEnforcement.STRICT
        assert config.lint is not None
        assert config.lint.command == "ruff check ."

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        """Test error when file doesn't exist."""
        with pytest.raises(PushRulesNotFoundError) as exc_info:
            load_push_rules(tmp_path / "nonexistent.md")

        assert "not found" in str(exc_info.value)

    def test_load_empty_file(self, tmp_path: Path) -> None:
        """Test error when file is empty."""
        push_rules = tmp_path / "push-rules.md"
        push_rules.write_text("")

        with pytest.raises(PushRulesParseError, match="empty"):
            load_push_rules(push_rules)

    def test_load_invalid_frontmatter(self, tmp_path: Path) -> None:
        """Test error when frontmatter is invalid."""
        push_rules = tmp_path / "push-rules.md"
        push_rules.write_text("# No frontmatter")

        with pytest.raises(PushRulesParseError, match="must start with YAML"):
            load_push_rules(push_rules)

    def test_load_validation_error(self, tmp_path: Path) -> None:
        """Test error when config fails validation."""
        push_rules = tmp_path / "push-rules.md"
        push_rules.write_text(
            dedent("""
                ---
                version: "invalid"
                ---
                """).strip()
        )

        with pytest.raises(PushRulesValidationError) as exc_info:
            load_push_rules(push_rules)

        assert "Invalid push-rules.md" in str(exc_info.value)


class TestValidatePushRules:
    """Tests for the validate_push_rules convenience function."""

    def test_accepts_path_object(self, tmp_path: Path) -> None:
        """Test that Path objects are accepted."""
        push_rules = tmp_path / "push-rules.md"
        push_rules.write_text(
            dedent("""
                ---
                version: "1.0"
                enabled: true
                ---
                """).strip()
        )

        config = validate_push_rules(push_rules)
        assert config.version == "1.0"

    def test_accepts_string_path(self, tmp_path: Path) -> None:
        """Test that string paths are accepted."""
        push_rules = tmp_path / "push-rules.md"
        push_rules.write_text(
            dedent("""
                ---
                version: "1.0"
                enabled: true
                ---
                """).strip()
        )

        config = validate_push_rules(str(push_rules))
        assert config.version == "1.0"


class TestTemplateValidation:
    """Tests that verify the template file is valid."""

    def test_template_is_valid(self) -> None:
        """Test that the push-rules template passes validation."""
        template_path = (
            Path(__file__).parent.parent / "templates" / "push-rules-template.md"
        )

        if not template_path.exists():
            pytest.skip("Template file not found")

        # Should not raise any exceptions
        config = load_push_rules(template_path)
        assert config.version == "1.0"
        assert config.enabled is True
        assert config.rebase_policy.enforcement == RebaseEnforcement.STRICT


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_minimal_valid_file(self, tmp_path: Path) -> None:
        """Test minimal valid push-rules.md file."""
        push_rules = tmp_path / "push-rules.md"
        push_rules.write_text("---\n---\n")

        config = load_push_rules(push_rules)
        # Should use all defaults
        assert config.version == "1.0"
        assert config.enabled is True

    def test_whitespace_in_frontmatter(self, tmp_path: Path) -> None:
        """Test handling of extra whitespace."""
        push_rules = tmp_path / "push-rules.md"
        push_rules.write_text(
            dedent("""
                ---

                version: "1.0"

                enabled: true

                ---
                """).strip()
        )

        config = load_push_rules(push_rules)
        assert config.version == "1.0"

    def test_unicode_content(self, tmp_path: Path) -> None:
        """Test handling of unicode content."""
        push_rules = tmp_path / "push-rules.md"
        push_rules.write_text(
            dedent("""
                ---
                version: "1.0"
                enabled: true
                ---

                # Git Push Rules

                Unicode test: \u2705 \u274c
                """).strip()
        )

        config = load_push_rules(push_rules)
        assert config.version == "1.0"

    def test_complex_regex_pattern(self, tmp_path: Path) -> None:
        """Test complex regex patterns in branch naming."""
        push_rules = tmp_path / "push-rules.md"
        push_rules.write_text(
            dedent("""
                ---
                version: "1.0"
                branch_naming_pattern: "^(feature|fix|docs|refactor|test|chore)/[a-z0-9]+(?:-[a-z0-9]+)*$"
                ---
                """).strip()
        )

        config = load_push_rules(push_rules)
        assert config.validate_branch_name("feature/add-new-feature") is True
        assert config.validate_branch_name("Feature/invalid") is False
