"""Hook configuration parser and loader.

This module provides functions to load, parse, and validate hook configurations
from .flowspec/hooks/hooks.yaml. Includes security validation to prevent
path traversal and other attacks.

Example:
    >>> config = load_hooks_config(".flowspec/hooks/hooks.yaml")
    >>> matching = config.get_matching_hooks(event)
    >>> for hook in matching:
    ...     print(f"Running hook: {hook.name}")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .schema import HooksConfig, HOOKS_CONFIG_JSON_SCHEMA

# Default locations to search for hooks.yaml
DEFAULT_HOOKS_CONFIG_PATHS = [
    ".flowspec/hooks/hooks.yaml",
    ".flowspec/hooks/hooks.yml",
]


class HooksConfigError(Exception):
    """Base exception for hook configuration errors."""

    pass


class HooksConfigNotFoundError(HooksConfigError):
    """Raised when hooks.yaml is not found."""

    def __init__(self, searched_paths: list[str]):
        """Initialize with searched paths.

        Args:
            searched_paths: List of paths that were searched.
        """
        self.searched_paths = searched_paths
        message = f"Hooks config not found. Searched: {', '.join(searched_paths)}"
        super().__init__(message)


class HooksConfigValidationError(HooksConfigError):
    """Raised when hooks.yaml fails validation."""

    def __init__(self, message: str, errors: list[str] | None = None):
        """Initialize with validation errors.

        Args:
            message: Summary message.
            errors: List of specific validation errors.
        """
        self.errors = errors or []
        if errors:
            error_list = "\n  - ".join(errors)
            full_message = f"{message}:\n  - {error_list}"
        else:
            full_message = message
        super().__init__(full_message)


class HooksSecurityError(HooksConfigError):
    """Raised when security validation fails."""

    pass


def load_hooks_config(
    config_path: str | Path | None = None,
    project_root: str | Path | None = None,
    validate_schema: bool = True,
    validate_security: bool = True,
) -> HooksConfig:
    """Load hooks configuration from YAML file.

    Searches for hooks.yaml in default locations if path not provided.
    Returns empty config if no hooks.yaml is found (not an error).

    Args:
        config_path: Explicit path to hooks.yaml (optional).
        project_root: Project root directory (default: current directory).
        validate_schema: Whether to validate against JSON schema (default: True).
        validate_security: Whether to run security checks (default: True).

    Returns:
        HooksConfig instance with parsed configuration.

    Raises:
        HooksConfigValidationError: If validation fails.
        HooksSecurityError: If security checks fail.
        HooksConfigError: For other loading errors (invalid YAML, etc.).

    Example:
        >>> config = load_hooks_config()
        >>> config = load_hooks_config(".flowspec/hooks/hooks.yaml")
        >>> config = load_hooks_config(validate_schema=False)
    """
    if project_root is None:
        project_root = Path.cwd()
    else:
        project_root = Path(project_root)

    # Find config file
    if config_path is not None:
        config_file = Path(config_path)
        if not config_file.exists():
            # If explicit path provided but not found, return empty config
            return HooksConfig.empty()
    else:
        config_file = _find_hooks_config(project_root)
        if config_file is None:
            # No hooks.yaml found, return empty config
            return HooksConfig.empty()

    # Load and parse YAML
    config_data = _load_yaml(config_file)

    # Validate against JSON schema
    if validate_schema:
        _validate_json_schema(config_data, config_file)

    # Parse into HooksConfig
    try:
        hooks_config = HooksConfig.from_dict(config_data)
    except (KeyError, ValueError, TypeError) as e:
        raise HooksConfigError(
            f"Failed to parse hooks config from {config_file}: {e}"
        ) from e

    # Security validation
    if validate_security:
        _validate_security(hooks_config, project_root)

    return hooks_config


def _find_hooks_config(project_root: Path) -> Path | None:
    """Find hooks.yaml in default locations.

    Args:
        project_root: Project root directory.

    Returns:
        Path to hooks.yaml or None if not found.
    """
    for rel_path in DEFAULT_HOOKS_CONFIG_PATHS:
        candidate = project_root / rel_path
        if candidate.exists():
            return candidate
    return None


def _load_yaml(config_path: Path) -> dict[str, Any]:
    """Load and parse YAML file.

    Args:
        config_path: Path to YAML file.

    Returns:
        Parsed YAML as dictionary.

    Raises:
        HooksConfigError: If YAML parsing fails.
    """
    try:
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise HooksConfigError(f"Failed to parse YAML in {config_path}: {e}") from e
    except OSError as e:
        raise HooksConfigError(f"Failed to read config file {config_path}: {e}") from e

    if not isinstance(data, dict):
        raise HooksConfigError(
            f"Invalid config format in {config_path}: expected object, "
            f"got {type(data).__name__}"
        )

    return data


def _validate_json_schema(config_data: dict[str, Any], config_path: Path) -> None:
    """Validate config against JSON schema.

    Args:
        config_data: Parsed config data.
        config_path: Path to config file (for error messages).

    Raises:
        HooksConfigValidationError: If validation fails.
    """
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        # jsonschema not installed, skip validation
        return

    validator = Draft7Validator(HOOKS_CONFIG_JSON_SCHEMA)
    errors: list[str] = []

    for error in validator.iter_errors(config_data):
        # Build readable error path
        path = ".".join(str(p) for p in error.absolute_path) or "(root)"
        errors.append(f"{path}: {error.message}")

    if errors:
        raise HooksConfigValidationError(
            f"Hooks config validation failed for {config_path}",
            errors=errors,
        )


def _validate_security(hooks_config: HooksConfig, project_root: Path) -> None:
    """Validate security constraints for all hooks.

    Checks:
    - Script paths are within .flowspec/hooks/ (no path traversal)
    - Timeouts are within allowed range
    - Environment variables don't contain shell metacharacters

    Args:
        hooks_config: Parsed hooks configuration.
        project_root: Project root directory.

    Raises:
        HooksSecurityError: If security validation fails.
    """
    hooks_dir = project_root / ".flowspec" / "hooks"

    for hook in hooks_config.hooks:
        # Validate script path
        if hook.script is not None:
            _validate_script_path(hook.script, hooks_dir, hook.name)

        # Validate timeout
        if hook.timeout < 1 or hook.timeout > 600:
            raise HooksSecurityError(
                f"Hook '{hook.name}' timeout {hook.timeout}s outside allowed range (1-600s)"
            )

        # Validate environment variables
        _validate_env_vars(hook.env, hook.name)

        # Validate working directory
        if hook.working_directory != ".":
            _validate_working_directory(hook.working_directory, project_root, hook.name)


def _validate_script_path(script: str, hooks_dir: Path, hook_name: str) -> None:
    """Validate script path is safe.

    Args:
        script: Script path (relative to hooks_dir).
        hooks_dir: Hooks directory (.flowspec/hooks/).
        hook_name: Hook name (for error messages).

    Raises:
        HooksSecurityError: If path is unsafe.
    """
    # Check for path traversal
    if ".." in script:
        raise HooksSecurityError(
            f"Hook '{hook_name}' script path contains path traversal: {script}"
        )

    # Check for absolute path
    if Path(script).is_absolute():
        raise HooksSecurityError(
            f"Hook '{hook_name}' script must be relative path, got: {script}"
        )

    # Resolve and check path is within hooks directory
    try:
        script_path = (hooks_dir / script).resolve()
        if not script_path.is_relative_to(hooks_dir):
            raise HooksSecurityError(
                f"Hook '{hook_name}' script must be in .flowspec/hooks/, got: {script}"
            )
    except (ValueError, OSError) as e:
        raise HooksSecurityError(
            f"Hook '{hook_name}' invalid script path '{script}': {e}"
        ) from e


def _validate_env_vars(env: dict[str, str], hook_name: str) -> None:
    """Validate environment variables don't contain shell metacharacters.

    Args:
        env: Environment variables.
        hook_name: Hook name (for error messages).

    Raises:
        HooksSecurityError: If env vars contain dangerous characters.
    """
    dangerous_chars = [";", "|", "&", "$", "`", "(", ")", "<", ">"]

    for key, value in env.items():
        for char in dangerous_chars:
            if char in value:
                raise HooksSecurityError(
                    f"Hook '{hook_name}' env var '{key}' contains shell "
                    f"metacharacter '{char}': {value}"
                )


def _validate_working_directory(
    working_dir: str, project_root: Path, hook_name: str
) -> None:
    """Validate working directory is within project.

    Args:
        working_dir: Working directory (relative to project_root).
        project_root: Project root directory.
        hook_name: Hook name (for error messages).

    Raises:
        HooksSecurityError: If working directory is outside project.
    """
    # Check for path traversal
    if ".." in working_dir:
        raise HooksSecurityError(
            f"Hook '{hook_name}' working_directory contains path traversal: "
            f"{working_dir}"
        )

    # Check for absolute path
    if Path(working_dir).is_absolute():
        raise HooksSecurityError(
            f"Hook '{hook_name}' working_directory must be relative, got: {working_dir}"
        )

    # Resolve and check within project
    try:
        wd_path = (project_root / working_dir).resolve()
        if not wd_path.is_relative_to(project_root):
            raise HooksSecurityError(
                f"Hook '{hook_name}' working_directory must be within project, "
                f"got: {working_dir}"
            )
    except (ValueError, OSError) as e:
        raise HooksSecurityError(
            f"Hook '{hook_name}' invalid working_directory '{working_dir}': {e}"
        ) from e


def validate_hooks_config_file(
    config_path: str | Path,
    project_root: str | Path | None = None,
) -> tuple[bool, list[str], list[str]]:
    """Validate hooks.yaml file and return detailed results.

    Args:
        config_path: Path to hooks.yaml file.
        project_root: Project root directory (default: current directory).

    Returns:
        Tuple of (is_valid, errors, warnings):
        - is_valid: True if no errors
        - errors: List of error messages
        - warnings: List of warning messages

    Example:
        >>> valid, errors, warnings = validate_hooks_config_file("hooks.yaml")
        >>> if not valid:
        ...     for error in errors:
        ...         print(f"ERROR: {error}")
    """
    errors: list[str] = []
    warnings: list[str] = []

    if project_root is None:
        project_root = Path.cwd()
    else:
        project_root = Path(project_root)

    config_path = Path(config_path)

    # Check file exists
    if not config_path.exists():
        errors.append(f"Config file not found: {config_path}")
        return (False, errors, warnings)

    # Try to load config
    try:
        hooks_config = load_hooks_config(
            config_path=config_path,
            project_root=project_root,
            validate_schema=True,
            validate_security=True,
        )
    except HooksConfigValidationError as e:
        errors.extend(e.errors)
        return (False, errors, warnings)
    except HooksSecurityError as e:
        errors.append(str(e))
        return (False, errors, warnings)
    except HooksConfigError as e:
        errors.append(str(e))
        return (False, errors, warnings)

    # Check for duplicate hook names
    hook_names = [hook.name for hook in hooks_config.hooks]
    if len(hook_names) != len(set(hook_names)):
        duplicates = [name for name in hook_names if hook_names.count(name) > 1]
        errors.append(f"Duplicate hook names found: {', '.join(set(duplicates))}")

    # Check script files exist
    hooks_dir = project_root / ".flowspec" / "hooks"
    for hook in hooks_config.hooks:
        if hook.script is not None:
            script_path = hooks_dir / hook.script
            if not script_path.exists():
                errors.append(f"Hook '{hook.name}' script not found: {hook.script}")

    # Warnings for high timeouts
    for hook in hooks_config.hooks:
        if hook.timeout > 300:
            warnings.append(
                f"Hook '{hook.name}' has high timeout: {hook.timeout}s (>5 minutes)"
            )

    is_valid = len(errors) == 0
    return (is_valid, errors, warnings)
