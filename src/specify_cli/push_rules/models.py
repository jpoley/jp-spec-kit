"""Pydantic models for push-rules.md configuration validation.

This module defines the schema for push-rules.md files using Pydantic models.
These models validate the YAML frontmatter and provide type-safe access to
configuration values.

Example:
    >>> config = PushRulesConfig(
    ...     version="1.0",
    ...     enabled=True,
    ...     rebase_policy=RebasePolicy(enforcement="strict", base_branch="main"),
    ...     lint=ValidationCommand(required=True, command="ruff check ."),
    ...     test=ValidationCommand(required=True, command="pytest tests/"),
    ... )
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class RebaseEnforcement(str, Enum):
    """Rebase enforcement levels.

    Attributes:
        STRICT: Block push if merge commits detected (default).
        WARN: Warn but allow push with merge commits.
        DISABLED: No rebase checking.
    """

    STRICT = "strict"
    WARN = "warn"
    DISABLED = "disabled"


class RebasePolicy(BaseModel):
    """Configuration for rebase enforcement.

    Attributes:
        enforcement: Level of rebase enforcement (strict, warn, disabled).
        base_branch: Branch to rebase against (default: main).
        allow_merge_commits: Whether to allow merge commits (default: False).
    """

    enforcement: RebaseEnforcement = Field(
        default=RebaseEnforcement.STRICT,
        description="Level of rebase enforcement",
    )
    base_branch: str = Field(
        default="main",
        description="Branch to rebase against",
        min_length=1,
    )
    allow_merge_commits: bool = Field(
        default=False,
        description="Whether to allow merge commits in branch history",
    )

    @field_validator("base_branch")
    @classmethod
    def validate_branch_name(cls, v: str) -> str:
        """Validate branch name is a valid git ref."""
        if not v or not v.strip():
            raise ValueError("base_branch cannot be empty")
        # Basic git ref validation
        if v.startswith("-") or v.endswith(".") or ".." in v:
            raise ValueError(f"Invalid branch name: {v}")
        return v.strip()


class ValidationCommand(BaseModel):
    """Configuration for a validation command (lint or test).

    Attributes:
        required: Whether this validation must pass before push.
        command: Shell command to execute for validation.
        allow_warnings: Whether to allow warnings (non-zero but non-fatal exit).
        timeout: Maximum seconds to wait for command completion.
    """

    required: bool = Field(
        default=True,
        description="Whether this validation must pass",
    )
    command: str = Field(
        description="Shell command to execute",
        min_length=1,
    )
    allow_warnings: bool = Field(
        default=False,
        description="Whether to allow warnings",
    )
    timeout: int = Field(
        default=300,
        description="Maximum seconds to wait for command",
        ge=1,
        le=3600,
    )

    @field_validator("command")
    @classmethod
    def validate_command(cls, v: str) -> str:
        """Validate command is not empty and doesn't contain dangerous patterns."""
        if not v or not v.strip():
            raise ValueError("command cannot be empty")

        stripped = v.strip()

        # Basic safety checks (not comprehensive security, just sanity checks).
        # This does NOT guarantee safety; it only blocks some common dangerous patterns.
        # For production use, consider a dedicated sandbox or allowlist approach.
        dangerous_regexes = [
            re.compile(
                r"\brm\s+-rf\s+/(\s|$)", re.IGNORECASE
            ),  # rm -rf / with flexible whitespace
            re.compile(
                r"\brm\s+-rf\s+/\*(\s|$)", re.IGNORECASE
            ),  # rm -rf /* with flexible whitespace
            re.compile(r">\s*/dev/sda", re.IGNORECASE),  # overwrite disk device
            re.compile(
                r":\s*\(\s*\)\s*{\s*:.*\|.*:.*&\s*};\s*:", re.IGNORECASE
            ),  # fork bomb
        ]
        for regex in dangerous_regexes:
            if regex.search(stripped):
                raise ValueError("Potentially dangerous command pattern detected")

        return stripped


class JanitorSettings(BaseModel):
    """Configuration for the github-janitor agent.

    Attributes:
        run_after_validation: Whether janitor runs after /jpspec:validate.
        prune_merged_branches: Whether to delete merged branches.
        clean_stale_worktrees: Whether to remove orphaned worktrees.
        protected_branches: Branches that should never be deleted.
    """

    run_after_validation: bool = Field(
        default=True,
        description="Whether janitor runs after validation",
    )
    prune_merged_branches: bool = Field(
        default=True,
        description="Whether to delete merged branches",
    )
    clean_stale_worktrees: bool = Field(
        default=True,
        description="Whether to remove orphaned worktrees",
    )
    protected_branches: list[str] = Field(
        default_factory=lambda: ["main", "master", "develop"],
        description="Branches that should never be deleted",
    )

    @field_validator("protected_branches")
    @classmethod
    def validate_protected_branches(cls, v: list[str]) -> list[str]:
        """Ensure protected branches list contains valid branch names."""
        validated = []
        for branch in v:
            if not branch or not branch.strip():
                continue
            stripped = branch.strip()
            if stripped.startswith("-") or stripped.endswith(".") or ".." in stripped:
                raise ValueError(f"Invalid branch name in protected_branches: {branch}")
            validated.append(stripped)
        return validated


class PushRulesConfig(BaseModel):
    """Main configuration for push-rules.md.

    This is the top-level schema for the YAML frontmatter in push-rules.md.
    All fields have sensible defaults, allowing minimal configuration files.

    Attributes:
        version: Schema version (for future compatibility).
        enabled: Whether push rules are active (default: True).
        bypass_flag: Flag to skip all validation (default: --skip-push-rules).
        rebase_policy: Rebase enforcement configuration.
        lint: Lint command configuration.
        test: Test command configuration.
        branch_naming_pattern: Regex pattern for valid branch names.
        enforce_branch_naming: Whether to enforce branch naming (default: True).
        janitor_settings: Janitor agent configuration.

    Example:
        >>> config = PushRulesConfig.model_validate({
        ...     "version": "1.0",
        ...     "enabled": True,
        ...     "rebase_policy": {"enforcement": "strict"},
        ...     "lint": {"command": "ruff check ."},
        ...     "test": {"command": "pytest tests/"},
        ... })
    """

    version: str = Field(
        default="1.0",
        description="Schema version",
        pattern=r"^\d+\.\d+$",
    )
    enabled: bool = Field(
        default=True,
        description="Whether push rules are active",
    )
    bypass_flag: str = Field(
        default="--skip-push-rules",
        description="Command-line flag to bypass all validation",
        min_length=1,
    )

    # Validation policies
    rebase_policy: RebasePolicy = Field(
        default_factory=RebasePolicy,
        description="Rebase enforcement configuration",
    )
    lint: Optional[ValidationCommand] = Field(
        default=None,
        description="Lint command configuration",
    )
    test: Optional[ValidationCommand] = Field(
        default=None,
        description="Test command configuration",
    )

    # Branch naming
    branch_naming_pattern: Optional[str] = Field(
        default=r"^(feature|fix|docs|refactor|test|chore)/[a-z0-9-]+$",
        description="Regex pattern for valid branch names",
    )
    enforce_branch_naming: bool = Field(
        default=True,
        description="Whether to enforce branch naming",
    )

    # Janitor settings
    janitor_settings: JanitorSettings = Field(
        default_factory=JanitorSettings,
        description="Janitor agent configuration",
    )

    @field_validator("branch_naming_pattern")
    @classmethod
    def validate_regex_pattern(cls, v: Optional[str]) -> Optional[str]:
        """Validate that the branch naming pattern is a valid regex."""
        if v is None:
            return None
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        return v

    @field_validator("bypass_flag")
    @classmethod
    def validate_bypass_flag(cls, v: str) -> str:
        """Validate bypass flag format."""
        if not v.startswith("-"):
            raise ValueError("bypass_flag must start with a dash")
        return v

    def is_lint_required(self) -> bool:
        """Check if lint validation is required."""
        return self.lint is not None and self.lint.required

    def is_test_required(self) -> bool:
        """Check if test validation is required."""
        return self.test is not None and self.test.required

    def is_branch_naming_enforced(self) -> bool:
        """Check if branch naming validation is enforced."""
        return self.enforce_branch_naming and self.branch_naming_pattern is not None

    def validate_branch_name(self, branch_name: str) -> bool:
        """Check if a branch name matches the naming pattern.

        Args:
            branch_name: The git branch name to validate.

        Returns:
            True if the branch name matches the pattern, False otherwise.
            Always returns True if branch naming is not enforced.
        """
        if not self.is_branch_naming_enforced():
            return True
        if self.branch_naming_pattern is None:
            return True
        return bool(re.match(self.branch_naming_pattern, branch_name))
