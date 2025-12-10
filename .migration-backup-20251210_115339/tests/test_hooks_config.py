"""Tests for hook configuration parser and loader.

Tests YAML loading, validation, security checks, and error handling.
"""

from textwrap import dedent

import pytest

from specify_cli.hooks.config import (
    HooksConfigError,
    HooksConfigValidationError,
    HooksSecurityError,
    load_hooks_config,
    validate_hooks_config_file,
)
from specify_cli.hooks.events import Event
from specify_cli.hooks.schema import EventMatcher, HookDefinition, HooksConfig


class TestLoadHooksConfig:
    """Test load_hooks_config function."""

    def test_load_empty_config_if_not_found(self, tmp_path):
        """Test returns empty config if hooks.yaml not found."""
        config = load_hooks_config(project_root=tmp_path)
        assert config.version == "1.0"
        assert len(config.hooks) == 0

    def test_load_minimal_config(self, tmp_path):
        """Test loading minimal valid config."""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        config_yaml = dedent(
            """
            version: "1.0"
            hooks:
              - name: "test-hook"
                events:
                  - type: "spec.created"
                script: "test.sh"
            """
        )
        (hooks_dir / "hooks.yaml").write_text(config_yaml)

        config = load_hooks_config(project_root=tmp_path)
        assert config.version == "1.0"
        assert len(config.hooks) == 1
        assert config.hooks[0].name == "test-hook"

    def test_load_config_with_defaults(self, tmp_path):
        """Test loading config with defaults section."""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        config_yaml = dedent(
            """
            version: "1.0"
            defaults:
              timeout: 60
              fail_mode: "stop"
            hooks:
              - name: "test-hook"
                events:
                  - type: "spec.created"
                script: "test.sh"
            """
        )
        (hooks_dir / "hooks.yaml").write_text(config_yaml)

        config = load_hooks_config(project_root=tmp_path)
        assert config.hooks[0].timeout == 60
        assert config.hooks[0].fail_mode == "stop"

    def test_load_config_with_filters(self, tmp_path):
        """Test loading config with event filters."""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        config_yaml = dedent(
            """
            version: "1.0"
            hooks:
              - name: "test-hook"
                events:
                  - type: "task.completed"
                    filter:
                      priority: ["high", "critical"]
                      labels_any: ["backend", "frontend"]
                script: "test.sh"
            """
        )
        (hooks_dir / "hooks.yaml").write_text(config_yaml)

        config = load_hooks_config(project_root=tmp_path)
        hook = config.hooks[0]
        assert len(hook.events) == 1
        assert hook.events[0].filter["priority"] == ["high", "critical"]

    def test_invalid_yaml(self, tmp_path):
        """Test error on invalid YAML."""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        (hooks_dir / "hooks.yaml").write_text("invalid: yaml: syntax:")

        with pytest.raises(HooksConfigError, match="Failed to parse YAML"):
            load_hooks_config(project_root=tmp_path)

    def test_missing_required_field(self, tmp_path):
        """Test error on missing required field."""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        config_yaml = dedent(
            """
            version: "1.0"
            hooks:
              - name: "test-hook"
                # Missing events field
                script: "test.sh"
            """
        )
        (hooks_dir / "hooks.yaml").write_text(config_yaml)

        # Should fail during parsing, not schema validation
        with pytest.raises((HooksConfigError, HooksConfigValidationError, KeyError)):
            load_hooks_config(project_root=tmp_path)


class TestSecurityValidation:
    """Test security validation."""

    def test_path_traversal_blocked(self, tmp_path):
        """Test path traversal in script path is blocked."""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        config_yaml = dedent(
            """
            version: "1.0"
            hooks:
              - name: "evil-hook"
                events:
                  - type: "spec.created"
                script: "../../etc/passwd"
            """
        )
        (hooks_dir / "hooks.yaml").write_text(config_yaml)

        with pytest.raises(HooksSecurityError, match="path traversal"):
            load_hooks_config(project_root=tmp_path, validate_security=True)

    def test_shell_metacharacters_blocked(self, tmp_path):
        """Test shell metacharacters in env vars are blocked."""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        config_yaml = dedent(
            """
            version: "1.0"
            hooks:
              - name: "injection-hook"
                events:
                  - type: "spec.created"
                script: "test.sh"
                env:
                  CMD: "echo 'test'; rm -rf /"
            """
        )
        (hooks_dir / "hooks.yaml").write_text(config_yaml)

        with pytest.raises(HooksSecurityError, match="shell metacharacter"):
            load_hooks_config(project_root=tmp_path, validate_security=True)

    def test_timeout_limits_enforced(self, tmp_path):
        """Test timeout limits are enforced by JSON schema."""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        config_yaml = dedent(
            """
            version: "1.0"
            hooks:
              - name: "long-hook"
                events:
                  - type: "spec.created"
                script: "test.sh"
                timeout: 9999
            """
        )
        (hooks_dir / "hooks.yaml").write_text(config_yaml)

        # JSON schema validation catches this before security validation
        with pytest.raises(HooksConfigValidationError, match="timeout"):
            load_hooks_config(project_root=tmp_path, validate_security=True)

    def test_security_validation_can_be_skipped(self, tmp_path):
        """Test security validation can be disabled."""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        config_yaml = dedent(
            """
            version: "1.0"
            hooks:
              - name: "test-hook"
                events:
                  - type: "spec.created"
                script: "../../dangerous.sh"
            """
        )
        (hooks_dir / "hooks.yaml").write_text(config_yaml)

        # Should succeed when security validation disabled
        config = load_hooks_config(project_root=tmp_path, validate_security=False)
        assert len(config.hooks) == 1


class TestValidateHooksConfigFile:
    """Test validate_hooks_config_file function."""

    def test_valid_config_passes(self, tmp_path):
        """Test valid config passes validation."""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        config_yaml = dedent(
            """
            version: "1.0"
            hooks:
              - name: "test-hook"
                events:
                  - type: "spec.created"
                script: "test.sh"
            """
        )
        config_path = hooks_dir / "hooks.yaml"
        config_path.write_text(config_yaml)

        # Create the script file
        (hooks_dir / "test.sh").write_text("#!/bin/bash\necho 'test'")

        valid, errors, warnings = validate_hooks_config_file(
            config_path, project_root=tmp_path
        )
        assert valid
        assert len(errors) == 0

    def test_missing_file_fails(self, tmp_path):
        """Test validation fails on missing file."""
        config_path = tmp_path / "nonexistent.yaml"
        valid, errors, warnings = validate_hooks_config_file(
            config_path, project_root=tmp_path
        )
        assert not valid
        assert any("not found" in error for error in errors)

    def test_duplicate_hook_names_detected(self, tmp_path):
        """Test duplicate hook names are detected."""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        config_yaml = dedent(
            """
            version: "1.0"
            hooks:
              - name: "duplicate"
                events:
                  - type: "spec.created"
                script: "test1.sh"
              - name: "duplicate"
                events:
                  - type: "plan.created"
                script: "test2.sh"
            """
        )
        config_path = hooks_dir / "hooks.yaml"
        config_path.write_text(config_yaml)

        valid, errors, warnings = validate_hooks_config_file(
            config_path, project_root=tmp_path
        )
        assert not valid
        assert any("Duplicate hook names" in error for error in errors)

    def test_missing_script_detected(self, tmp_path):
        """Test missing script files are detected."""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        config_yaml = dedent(
            """
            version: "1.0"
            hooks:
              - name: "test-hook"
                events:
                  - type: "spec.created"
                script: "nonexistent.sh"
            """
        )
        config_path = hooks_dir / "hooks.yaml"
        config_path.write_text(config_yaml)

        valid, errors, warnings = validate_hooks_config_file(
            config_path, project_root=tmp_path
        )
        assert not valid
        assert any("script not found" in error for error in errors)

    def test_high_timeout_warning(self, tmp_path):
        """Test high timeouts generate warnings."""
        hooks_dir = tmp_path / ".specify" / "hooks"
        hooks_dir.mkdir(parents=True)

        config_yaml = dedent(
            """
            version: "1.0"
            hooks:
              - name: "slow-hook"
                events:
                  - type: "spec.created"
                script: "test.sh"
                timeout: 500
            """
        )
        config_path = hooks_dir / "hooks.yaml"
        config_path.write_text(config_yaml)
        (hooks_dir / "test.sh").write_text("#!/bin/bash")

        valid, errors, warnings = validate_hooks_config_file(
            config_path, project_root=tmp_path
        )
        assert valid  # No errors, just warnings
        assert len(warnings) > 0
        assert any("high timeout" in warning for warning in warnings)


class TestHooksConfig:
    """Test HooksConfig class."""

    def test_get_matching_hooks(self):
        """Test getting hooks that match an event."""
        hook1 = HookDefinition(
            name="hook1",
            events=[EventMatcher(type="spec.created")],
            script="test.sh",
        )
        hook2 = HookDefinition(
            name="hook2",
            events=[EventMatcher(type="task.*")],
            script="test.sh",
        )
        config = HooksConfig(version="1.0", hooks=[hook1, hook2])

        event = Event(event_type="spec.created", project_root="/tmp")
        matching = config.get_matching_hooks(event)
        assert len(matching) == 1
        assert matching[0].name == "hook1"

        event = Event(event_type="task.completed", project_root="/tmp")
        matching = config.get_matching_hooks(event)
        assert len(matching) == 1
        assert matching[0].name == "hook2"

    def test_get_matching_hooks_disabled(self):
        """Test disabled hooks are not matched."""
        hook = HookDefinition(
            name="disabled",
            events=[EventMatcher(type="spec.created")],
            script="test.sh",
            enabled=False,
        )
        config = HooksConfig(version="1.0", hooks=[hook])

        event = Event(event_type="spec.created", project_root="/tmp")
        matching = config.get_matching_hooks(event)
        assert len(matching) == 0

    def test_get_hook_by_name(self):
        """Test getting hook by name."""
        hook = HookDefinition(
            name="test-hook",
            events=[EventMatcher(type="spec.created")],
            script="test.sh",
        )
        config = HooksConfig(version="1.0", hooks=[hook])

        found = config.get_hook_by_name("test-hook")
        assert found is not None
        assert found.name == "test-hook"

        not_found = config.get_hook_by_name("nonexistent")
        assert not_found is None
