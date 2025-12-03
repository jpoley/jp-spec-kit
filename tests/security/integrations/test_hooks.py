"""Tests for pre-commit hooks integration."""

import yaml


from specify_cli.security.integrations.hooks import (
    PreCommitConfig,
    generate_precommit_config,
    generate_husky_config,
    generate_lefthook_config,
)


class TestPreCommitConfig:
    """Tests for PreCommitConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = PreCommitConfig()

        assert "semgrep" in config.enabled_scanners
        assert "bandit" in config.enabled_scanners
        assert config.fail_on_severity == "high"

    def test_to_yaml_structure(self):
        """Test YAML output structure."""
        config = PreCommitConfig()
        yaml_str = config.to_yaml()
        data = yaml.safe_load(yaml_str)

        assert "repos" in data
        assert len(data["repos"]) > 0
        assert "hooks" in data["repos"][0]

    def test_to_yaml_includes_semgrep(self):
        """Test YAML includes Semgrep hook."""
        config = PreCommitConfig(enabled_scanners=["semgrep"])
        yaml_str = config.to_yaml()
        data = yaml.safe_load(yaml_str)

        hooks = data["repos"][0]["hooks"]
        semgrep_hook = next((h for h in hooks if h["id"] == "semgrep"), None)

        assert semgrep_hook is not None
        assert "semgrep scan" in semgrep_hook["entry"]

    def test_to_yaml_includes_bandit(self):
        """Test YAML includes Bandit hook."""
        config = PreCommitConfig(enabled_scanners=["bandit"])
        yaml_str = config.to_yaml()
        data = yaml.safe_load(yaml_str)

        hooks = data["repos"][0]["hooks"]
        bandit_hook = next((h for h in hooks if h["id"] == "bandit"), None)

        assert bandit_hook is not None
        assert "bandit" in bandit_hook["entry"]

    def test_to_yaml_includes_jpspec(self):
        """Test YAML includes jpspec security hook."""
        config = PreCommitConfig()
        yaml_str = config.to_yaml()
        data = yaml.safe_load(yaml_str)

        hooks = data["repos"][0]["hooks"]
        jpspec_hook = next((h for h in hooks if h["id"] == "jpspec-security"), None)

        assert jpspec_hook is not None
        assert "specify security scan" in jpspec_hook["entry"]
        assert "--fail-on high" in jpspec_hook["entry"]

    def test_fail_on_severity_in_config(self):
        """Test fail_on severity is included."""
        config = PreCommitConfig(fail_on_severity="critical")
        yaml_str = config.to_yaml()

        assert "--fail-on critical" in yaml_str

    def test_exclude_patterns(self):
        """Test exclude patterns are included."""
        config = PreCommitConfig(exclude_patterns=["node_modules/*", "*.test.py"])
        yaml_str = config.to_yaml()
        data = yaml.safe_load(yaml_str)

        assert "exclude" in data
        assert "node_modules" in data["exclude"]

    def test_additional_args(self):
        """Test additional args are passed to scanners."""
        config = PreCommitConfig(additional_args={"semgrep": ["--verbose", "--json"]})
        yaml_str = config.to_yaml()

        assert "--verbose" in yaml_str
        assert "--json" in yaml_str

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = PreCommitConfig(
            enabled_scanners=["semgrep"],
            fail_on_severity="medium",
        )
        data = config.to_dict()

        assert data["enabled_scanners"] == ["semgrep"]
        assert data["fail_on_severity"] == "medium"


class TestGeneratePrecommitConfig:
    """Tests for generate_precommit_config function."""

    def test_basic_usage(self):
        """Test basic configuration generation."""
        config = generate_precommit_config()

        assert "repos:" in config
        assert "hooks:" in config

    def test_custom_scanners(self):
        """Test custom scanner selection."""
        config = generate_precommit_config(scanners=["semgrep"])

        assert "semgrep" in config
        # Should still have jpspec-security
        assert "jpspec-security" in config

    def test_custom_fail_on(self):
        """Test custom fail_on threshold."""
        config = generate_precommit_config(fail_on="critical")

        assert "--fail-on critical" in config

    def test_exclude_patterns(self):
        """Test exclude patterns."""
        config = generate_precommit_config(exclude=["*.min.js"])
        data = yaml.safe_load(config)

        assert "exclude" in data


class TestGenerateHuskyConfig:
    """Tests for generate_husky_config function."""

    def test_generates_shell_script(self):
        """Test generates valid shell script."""
        config = generate_husky_config()

        assert "#!/usr/bin/env sh" in config
        assert "specify security scan" in config
        assert "--fail-on high" in config

    def test_includes_exit_code(self):
        """Test script exits with scan's exit code."""
        config = generate_husky_config()

        assert "exit $?" in config


class TestGenerateLefthookConfig:
    """Tests for generate_lefthook_config function."""

    def test_generates_valid_yaml(self):
        """Test generates valid YAML."""
        config = generate_lefthook_config()
        data = yaml.safe_load(config)

        assert "pre-commit" in data
        assert "commands" in data["pre-commit"]

    def test_includes_security_scan_command(self):
        """Test includes security scan command."""
        config = generate_lefthook_config()
        data = yaml.safe_load(config)

        commands = data["pre-commit"]["commands"]
        assert "security-scan" in commands
        assert "specify security scan" in commands["security-scan"]["run"]
