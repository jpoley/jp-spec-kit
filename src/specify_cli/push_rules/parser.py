"""Parser for push-rules.md files with YAML frontmatter.

This module handles loading and parsing push-rules.md files, extracting
the YAML frontmatter and validating it against the PushRulesConfig schema.

Example:
    >>> from pathlib import Path
    >>> config = load_push_rules(Path("push-rules.md"))
    >>> print(config.rebase_policy.base_branch)
    'main'
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .models import PushRulesConfig


class PushRulesError(Exception):
    """Base exception for push rules errors."""

    pass


class PushRulesNotFoundError(PushRulesError):
    """Raised when push-rules.md file is not found."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(
            f"push-rules.md not found at: {path}\n"
            f"Run 'specify init' to generate this file, or create it manually."
        )


class PushRulesParseError(PushRulesError):
    """Raised when push-rules.md cannot be parsed."""

    def __init__(self, path: Path, message: str, line: int | None = None) -> None:
        self.path = path
        self.line = line
        location = f" at line {line}" if line else ""
        super().__init__(f"Failed to parse {path}{location}: {message}")


class PushRulesValidationError(PushRulesError):
    """Raised when push-rules.md fails schema validation."""

    def __init__(self, path: Path, errors: list[dict[str, Any]]) -> None:
        self.path = path
        self.errors = errors
        error_messages = self._format_errors(errors)
        super().__init__(
            f"Invalid push-rules.md configuration at {path}:\n{error_messages}"
        )

    @staticmethod
    def _format_errors(errors: list[dict[str, Any]]) -> str:
        """Format Pydantic validation errors for display."""
        lines = []
        for error in errors:
            loc = ".".join(str(x) for x in error.get("loc", []))
            msg = error.get("msg", "Unknown error")
            lines.append(f"  - {loc}: {msg}")
        return "\n".join(lines)


def extract_yaml_frontmatter(content: str) -> tuple[dict[str, Any], int]:
    """Extract YAML frontmatter from markdown content.

    The frontmatter must be at the start of the file, delimited by --- lines.

    Args:
        content: The full markdown file content.

    Returns:
        Tuple of (parsed YAML dict, end line number of frontmatter).

    Raises:
        PushRulesParseError: If frontmatter is missing or invalid.
    """
    # Check for frontmatter delimiter
    if not content.startswith("---"):
        raise PushRulesParseError(
            Path("push-rules.md"),
            "File must start with YAML frontmatter (---)",
            line=1,
        )

    # Find the closing delimiter
    lines = content.split("\n")
    end_line = None
    for i, line in enumerate(lines[1:], start=2):  # Start from line 2
        if line.strip() == "---":
            end_line = i
            break

    if end_line is None:
        raise PushRulesParseError(
            Path("push-rules.md"),
            "YAML frontmatter not closed (missing closing ---)",
            line=1,
        )

    # Extract and parse YAML content
    yaml_content = "\n".join(lines[1 : end_line - 1])

    try:
        parsed = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        # Try to extract line number from YAML error
        line_num = None
        if hasattr(e, "problem_mark") and e.problem_mark is not None:
            line_num = e.problem_mark.line + 2  # +2 for 0-index and opening ---
        raise PushRulesParseError(
            Path("push-rules.md"),
            f"Invalid YAML: {e}",
            line=line_num,
        )

    if parsed is None:
        parsed = {}

    if not isinstance(parsed, dict):
        raise PushRulesParseError(
            Path("push-rules.md"),
            f"YAML frontmatter must be a mapping, got {type(parsed).__name__}",
            line=1,
        )

    return parsed, end_line


def normalize_yaml_keys(data: dict[str, Any]) -> dict[str, Any]:
    """Normalize YAML keys to match Pydantic model field names.

    Converts human-friendly markdown field names to Python snake_case.
    For example, "Allow Merge Commits" becomes "allow_merge_commits".

    Args:
        data: Raw parsed YAML dict.

    Returns:
        Dict with normalized keys.
    """

    def to_snake_case(s: str) -> str:
        """Convert a string to snake_case."""
        # Replace spaces and hyphens with underscores
        s = re.sub(r"[\s-]+", "_", s)
        # Handle camelCase
        s = re.sub(r"([a-z])([A-Z])", r"\1_\2", s)
        return s.lower()

    def normalize_dict(d: dict[str, Any]) -> dict[str, Any]:
        """Recursively normalize dict keys."""
        result = {}
        for key, value in d.items():
            normalized_key = to_snake_case(key)
            if isinstance(value, dict):
                result[normalized_key] = normalize_dict(value)
            elif isinstance(value, list):
                result[normalized_key] = [
                    normalize_dict(v) if isinstance(v, dict) else v for v in value
                ]
            else:
                result[normalized_key] = value
        return result

    return normalize_dict(data)


def parse_markdown_config(content: str) -> dict[str, Any]:
    """Parse configuration from the markdown body (after frontmatter).

    This extracts configuration values from the structured markdown format
    used in push-rules.md, where configuration is written as:
    - **Key**: value

    Args:
        content: The markdown content after the YAML frontmatter.

    Returns:
        Dict of extracted configuration values.
    """
    config: dict[str, Any] = {}

    # Pattern to match "- **Key**: value" format
    pattern = re.compile(r"^\s*-\s*\*\*(.+?)\*\*:\s*(.+)$", re.MULTILINE)

    for match in pattern.finditer(content):
        key = match.group(1).strip()
        value = match.group(2).strip()

        # Convert value to appropriate type
        if value.lower() in ("true", "yes"):
            value = True
        elif value.lower() in ("false", "no"):
            value = False
        elif value.isdigit():
            value = int(value)
        elif value.startswith("`") and value.endswith("`"):
            value = value[1:-1]  # Strip backticks

        config[key] = value

    return config


def merge_configs(
    frontmatter: dict[str, Any], markdown_config: dict[str, Any]
) -> dict[str, Any]:
    """Merge frontmatter and markdown-extracted configuration.

    Frontmatter takes precedence over markdown body values.
    This allows both explicit YAML config and human-readable markdown.

    Args:
        frontmatter: Parsed YAML frontmatter dict.
        markdown_config: Dict extracted from markdown body.

    Returns:
        Merged configuration dict.
    """
    # Normalize markdown config keys
    normalized_md = normalize_yaml_keys(markdown_config)

    # Start with markdown config, override with frontmatter
    result = {}

    # Build nested structure from flat markdown config
    # Maps flat keys to nested paths
    key_mapping = {
        "enforcement": ("rebase_policy", "enforcement"),
        "base_branch": ("rebase_policy", "base_branch"),
        "allow_merge_commits": ("rebase_policy", "allow_merge_commits"),
        "command": ("lint", "command"),  # Handled specially
        "required": ("lint", "required"),
        "allow_warnings": ("lint", "allow_warnings"),
        "timeout": ("lint", "timeout"),
        "minimum_coverage": ("test", "minimum_coverage"),
        "pattern": ("branch_naming_pattern",),
        "enforce": ("enforce_branch_naming",),
        "run_after_validation": ("janitor_settings", "run_after_validation"),
        "prune_merged_branches": ("janitor_settings", "prune_merged_branches"),
        "clean_stale_worktrees": ("janitor_settings", "clean_stale_worktrees"),
        "protected_branches": ("janitor_settings", "protected_branches"),
    }

    # Apply normalized markdown config to nested structure
    for key, value in normalized_md.items():
        if key in key_mapping:
            path = key_mapping[key]
            current = result
            for p in path[:-1]:
                if p not in current:
                    current[p] = {}
                current = current[p]
            current[path[-1]] = value

    # Deep merge frontmatter (takes precedence)
    def deep_merge(base: dict, override: dict) -> dict:
        result = base.copy()
        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    # Normalize frontmatter keys first
    normalized_fm = normalize_yaml_keys(frontmatter)
    return deep_merge(result, normalized_fm)


def load_push_rules(path: Path) -> PushRulesConfig:
    """Load and validate push-rules.md from the given path.

    Args:
        path: Path to the push-rules.md file.

    Returns:
        Validated PushRulesConfig object.

    Raises:
        PushRulesNotFoundError: If the file does not exist.
        PushRulesParseError: If the file cannot be parsed.
        PushRulesValidationError: If the config fails validation.

    Example:
        >>> config = load_push_rules(Path("push-rules.md"))
        >>> print(config.version)
        '1.0'
    """
    if not path.exists():
        raise PushRulesNotFoundError(path)

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        raise PushRulesParseError(path, f"Cannot read file: {e}")

    if not content.strip():
        raise PushRulesParseError(path, "File is empty")

    # Extract YAML frontmatter
    try:
        frontmatter, end_line = extract_yaml_frontmatter(content)
    except PushRulesParseError as e:
        # Update path in error
        raise PushRulesParseError(path, str(e).split(": ", 1)[-1], e.line)

    # Optionally parse markdown body for additional config
    lines = content.split("\n")
    markdown_body = "\n".join(lines[end_line:])
    markdown_config = parse_markdown_config(markdown_body)

    # Merge configurations
    merged_config = merge_configs(frontmatter, markdown_config)

    # Validate against Pydantic model
    try:
        return PushRulesConfig.model_validate(merged_config)
    except ValidationError as e:
        raise PushRulesValidationError(path, e.errors())


def validate_push_rules(path: Path | str) -> PushRulesConfig:
    """Validate push-rules.md and return config if valid.

    This is a convenience wrapper around load_push_rules that accepts
    both Path and str arguments.

    Args:
        path: Path to the push-rules.md file (Path or str).

    Returns:
        Validated PushRulesConfig object.

    Raises:
        PushRulesError: If validation fails for any reason.
    """
    if isinstance(path, str):
        path = Path(path)
    return load_push_rules(path)
