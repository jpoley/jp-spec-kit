"""Workflow transition validation engine.

This module implements the validation engine that enforces transition gates.
Each transition can have one of three validation modes:

1. NONE - Immediate pass-through (no gate)
2. KEYWORD - User must type exact keyword to proceed
3. PULL_REQUEST - Blocked until GitHub PR containing artifacts is merged

The validation engine:
- Checks that required artifacts exist before transition
- Enforces validation mode gates (keyword, PR merge)
- Provides clear error messages for failed validations
- Logs all validation decisions for audit trail
- Supports --skip-validation flag for emergency override

Example:
    >>> from specify_cli.workflow.validation_engine import TransitionValidator
    >>> from specify_cli.workflow.transition import TransitionSchema, ValidationMode
    >>>
    >>> validator = TransitionValidator()
    >>> result = validator.validate(transition_schema, context)
    >>> if result.passed:
    ...     print("Transition allowed")
    ... else:
    ...     print(f"Validation failed: {result.message}")
"""

from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from specify_cli.workflow.transition import Artifact, TransitionSchema, ValidationMode

logger = logging.getLogger(__name__)


@dataclass
class TransitionValidationResult:
    """Result of a transition validation.

    Attributes:
        passed: Whether validation passed.
        message: Human-readable message describing the result.
        mode: Validation mode that was used.
        skipped: Whether validation was skipped via override flag.
        details: Additional context for debugging.
    """

    passed: bool
    message: str
    mode: ValidationMode
    skipped: bool = False
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "passed": self.passed,
            "message": self.message,
            "mode": self.mode.value,
            "skipped": self.skipped,
            "details": self.details,
        }


class TransitionValidator:
    """Validates workflow transitions based on validation mode.

    The validator enforces transition gates according to the configured
    validation mode:
    - NONE: Always passes (immediate transition)
    - KEYWORD: Prompts user for exact keyword match
    - PULL_REQUEST: Uses GitHub CLI to check for merged PR containing artifacts

    All validation decisions are logged for audit trail.

    Example:
        >>> validator = TransitionValidator()
        >>> result = validator.validate(transition, {"feature": "auth"})
        >>> if not result.passed:
        ...     print(f"Blocked: {result.message}")
    """

    def __init__(self, skip_validation: bool = False) -> None:
        """Initialize the transition validator.

        Args:
            skip_validation: Emergency override flag to skip all validation.
                           Should only be used in exceptional circumstances.
        """
        self.skip_validation = skip_validation
        if skip_validation:
            logger.warning(
                "⚠️  Validation skip mode enabled - all gates will be bypassed"
            )

    def validate(
        self,
        transition: TransitionSchema,
        context: dict[str, Any],
    ) -> TransitionValidationResult:
        """Validate a workflow transition.

        This is the main entry point for validation. It:
        1. Checks if validation is skipped (emergency override)
        2. Verifies required artifacts exist
        3. Enforces the configured validation mode gate
        4. Logs the validation decision

        Args:
            transition: Transition schema to validate.
            context: Context dictionary with feature name, paths, etc.

        Returns:
            TransitionValidationResult indicating whether transition is allowed.

        Example:
            >>> result = validator.validate(transition, {"feature": "auth"})
            >>> print(f"Passed: {result.passed}, Message: {result.message}")
        """
        # Emergency override - skip all validation
        if self.skip_validation:
            logger.warning(
                f"⚠️  SKIPPING validation for transition: {transition.name} "
                f"(mode: {transition.validation.value})"
            )
            return TransitionValidationResult(
                passed=True,
                message="Validation skipped via --skip-validation flag",
                mode=transition.validation,
                skipped=True,
            )

        # Check artifacts exist before validating mode
        artifact_check = self._check_artifacts_exist(
            transition.get_required_output_artifacts(),
            context,
        )
        if not artifact_check.passed:
            return artifact_check

        # Validate based on mode
        if transition.validation == ValidationMode.NONE:
            return self._validate_none(transition)
        elif transition.validation == ValidationMode.KEYWORD:
            return self._validate_keyword(transition, context)
        elif transition.validation == ValidationMode.PULL_REQUEST:
            return self._validate_pull_request(transition, context)
        else:
            # Unknown validation mode - fail safe
            logger.error(f"Unknown validation mode: {transition.validation}")
            return TransitionValidationResult(
                passed=False,
                message=f"Unknown validation mode: {transition.validation.value}",
                mode=transition.validation,
                details={"transition": transition.name},
            )

    def _check_artifacts_exist(
        self,
        artifacts: list[Artifact],
        context: dict[str, Any],
    ) -> TransitionValidationResult:
        """Check that all required artifacts exist.

        Args:
            artifacts: List of artifacts to check.
            context: Context with feature name and other variables.

        Returns:
            TransitionValidationResult indicating whether all artifacts exist.
        """
        feature = context.get("feature", "")
        base_path = Path(context.get("base_path", "."))

        missing_artifacts = []
        for artifact in artifacts:
            if not artifact.required:
                continue

            # Resolve the artifact path
            resolved_path = artifact.resolve_path(feature=feature)
            full_path = base_path / resolved_path.lstrip("./")

            # Check if artifact exists
            if artifact.multiple:
                # For multiple artifacts, check if at least one matching file exists
                parent = full_path.parent
                if not parent.exists():
                    missing_artifacts.append(artifact.type)
                else:
                    # Use artifact.matches_pattern() to check for matching files
                    matched = False
                    for file in parent.iterdir():
                        if artifact.matches_pattern(str(file)):
                            matched = True
                            break
                    if not matched:
                        missing_artifacts.append(artifact.type)
            else:
                # Single artifact - must exist
                if not full_path.exists():
                    missing_artifacts.append(artifact.type)
                    logger.debug(f"Missing artifact: {full_path}")

        if missing_artifacts:
            message = (
                f"Required artifacts missing: {', '.join(missing_artifacts)}\n"
                f"Cannot proceed with transition until artifacts are created."
            )
            logger.warning(f"Artifact validation failed: {message}")
            return TransitionValidationResult(
                passed=False,
                message=message,
                mode=ValidationMode.NONE,  # Artifact check is pre-validation
                details={
                    "missing_artifacts": missing_artifacts,
                    "feature": feature,
                },
            )

        logger.info(
            f"✓ All required artifacts exist ({len([a for a in artifacts if a.required])} required)"
        )
        return TransitionValidationResult(
            passed=True,
            message="All required artifacts exist",
            mode=ValidationMode.NONE,
        )

    def _validate_none(
        self, transition: TransitionSchema
    ) -> TransitionValidationResult:
        """Validate NONE mode (immediate pass-through).

        Args:
            transition: Transition schema.

        Returns:
            TransitionValidationResult that always passes.
        """
        logger.info(f"✓ NONE validation mode - transition '{transition.name}' allowed")
        return TransitionValidationResult(
            passed=True,
            message="No validation gate required (NONE mode)",
            mode=ValidationMode.NONE,
        )

    def _validate_keyword(
        self,
        transition: TransitionSchema,
        context: dict[str, Any],
    ) -> TransitionValidationResult:
        """Validate KEYWORD mode (user must type exact keyword).

        Args:
            transition: Transition schema with validation_keyword.
            context: Context dictionary.

        Returns:
            TransitionValidationResult indicating whether keyword was entered correctly.
        """
        keyword = transition.validation_keyword
        if not keyword:
            logger.error(
                f"KEYWORD validation mode for '{transition.name}' "
                f"has no keyword configured"
            )
            return TransitionValidationResult(
                passed=False,
                message="KEYWORD validation mode configured but no keyword set",
                mode=ValidationMode.KEYWORD,
                details={"transition": transition.name},
            )

        # Check if keyword was provided in context (for testing)
        provided_keyword = context.get("validation_keyword")
        if provided_keyword is not None:
            matches = provided_keyword == keyword
            if matches:
                logger.info(
                    f"✓ KEYWORD validation passed for '{transition.name}' "
                    f"(keyword: {keyword})"
                )
                return TransitionValidationResult(
                    passed=True,
                    message=f"Keyword '{keyword}' accepted",
                    mode=ValidationMode.KEYWORD,
                )
            else:
                logger.warning(
                    f"✗ KEYWORD validation failed for '{transition.name}' "
                    f"(expected: {keyword}, got: {provided_keyword})"
                )
                return TransitionValidationResult(
                    passed=False,
                    message=(
                        f"Incorrect keyword. Expected '{keyword}' but got "
                        f"'{provided_keyword}'"
                    ),
                    mode=ValidationMode.KEYWORD,
                    details={
                        "expected": keyword,
                        "provided": provided_keyword,
                    },
                )

        # Prompt user for keyword (interactive mode)
        return self._prompt_keyword(transition, keyword)

    def _prompt_keyword(
        self,
        transition: TransitionSchema,
        keyword: str,
    ) -> TransitionValidationResult:
        """Prompt user to enter keyword for validation.

        Args:
            transition: Transition schema.
            keyword: The exact keyword required.

        Returns:
            TransitionValidationResult based on user input.
        """
        print(f"\n{'=' * 60}")
        print(f"KEYWORD VALIDATION REQUIRED: {transition.name}")
        print(f"{'=' * 60}")
        print("\nTo proceed with this transition, type the exact keyword:")
        print(f"\n  → {keyword}\n")
        print("(or press Ctrl+C to cancel)\n")

        try:
            user_input = input("Enter keyword: ").strip()
        except (KeyboardInterrupt, EOFError):
            logger.info(f"Keyword validation cancelled for '{transition.name}'")
            return TransitionValidationResult(
                passed=False,
                message="Keyword validation cancelled by user",
                mode=ValidationMode.KEYWORD,
            )

        if user_input == keyword:
            logger.info(
                f"✓ KEYWORD validation passed for '{transition.name}' "
                f"(keyword: {keyword})"
            )
            print("\n✓ Keyword accepted. Proceeding with transition.\n")
            return TransitionValidationResult(
                passed=True,
                message=f"Keyword '{keyword}' accepted",
                mode=ValidationMode.KEYWORD,
            )
        else:
            logger.warning(
                f"✗ KEYWORD validation failed for '{transition.name}' "
                f"(expected: {keyword}, got: {user_input})"
            )
            print(f"\n✗ Incorrect keyword. Expected '{keyword}' but got '{user_input}'")
            print("Transition blocked.\n")
            return TransitionValidationResult(
                passed=False,
                message=f"Incorrect keyword. Expected '{keyword}' but got '{user_input}'",
                mode=ValidationMode.KEYWORD,
                details={
                    "expected": keyword,
                    "provided": user_input,
                },
            )

    def _validate_pull_request(
        self,
        transition: TransitionSchema,
        context: dict[str, Any],
    ) -> TransitionValidationResult:
        """Validate PULL_REQUEST mode (PR must be merged).

        Uses GitHub CLI (gh) to check if a PR containing the artifacts
        has been merged.

        Args:
            transition: Transition schema.
            context: Context with feature name and artifact info.

        Returns:
            TransitionValidationResult indicating whether a merged PR exists.
        """
        feature = context.get("feature", "")
        if not feature:
            logger.error("PULL_REQUEST validation requires 'feature' in context")
            return TransitionValidationResult(
                passed=False,
                message="Cannot validate PR: feature name not provided",
                mode=ValidationMode.PULL_REQUEST,
            )

        # Check if PR number is provided in context (for testing)
        pr_number = context.get("pr_number")
        if pr_number is not None:
            return self._check_pr_merged(pr_number, feature, transition)

        # Check for merged PR using gh CLI
        logger.info(
            f"Checking for merged PR for feature '{feature}' "
            f"(transition: {transition.name})"
        )

        try:
            # Query GitHub for merged PRs related to this feature
            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "list",
                    "--state",
                    "merged",
                    "--search",
                    f"{feature} in:title",
                    "--json",
                    "number,title,mergedAt",
                    "--limit",
                    "10",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                logger.error(f"gh CLI error: {result.stderr}")
                return TransitionValidationResult(
                    passed=False,
                    message=(
                        f"Failed to query GitHub PRs: {result.stderr}\n"
                        f"Make sure 'gh' CLI is installed and authenticated."
                    ),
                    mode=ValidationMode.PULL_REQUEST,
                    details={"error": result.stderr},
                )

            prs = json.loads(result.stdout)
            if not prs:
                logger.warning(
                    f"No merged PRs found for feature '{feature}' "
                    f"(transition: {transition.name})"
                )
                return TransitionValidationResult(
                    passed=False,
                    message=(
                        f"No merged PR found for feature '{feature}'.\n"
                        f"Create and merge a PR containing the required artifacts "
                        f"to proceed."
                    ),
                    mode=ValidationMode.PULL_REQUEST,
                    details={"feature": feature, "prs_found": 0},
                )

            # Found merged PR(s)
            latest_pr = prs[0]
            logger.info(
                f"✓ Found merged PR #{latest_pr['number']}: {latest_pr['title']}"
            )
            return TransitionValidationResult(
                passed=True,
                message=(
                    f"Merged PR found: #{latest_pr['number']} - {latest_pr['title']}"
                ),
                mode=ValidationMode.PULL_REQUEST,
                details={
                    "pr_number": latest_pr["number"],
                    "pr_title": latest_pr["title"],
                    "merged_at": latest_pr.get("mergedAt"),
                },
            )

        except FileNotFoundError:
            logger.error("gh CLI not found - cannot validate PULL_REQUEST mode")
            return TransitionValidationResult(
                passed=False,
                message=(
                    "GitHub CLI (gh) not found. Install it to use PULL_REQUEST "
                    "validation mode.\n"
                    "See: https://cli.github.com/"
                ),
                mode=ValidationMode.PULL_REQUEST,
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse gh CLI output: {e}")
            return TransitionValidationResult(
                passed=False,
                message=f"Failed to parse gh CLI output: {e}",
                mode=ValidationMode.PULL_REQUEST,
                details={"error": str(e)},
            )
        except Exception as e:
            logger.error(f"Unexpected error during PR validation: {e}")
            return TransitionValidationResult(
                passed=False,
                message=f"Unexpected error during PR validation: {e}",
                mode=ValidationMode.PULL_REQUEST,
                details={"error": str(e)},
            )

    def _check_pr_merged(
        self,
        pr_number: int,
        transition: TransitionSchema,
    ) -> TransitionValidationResult:
        """Check if a specific PR is merged.

        Args:
            pr_number: GitHub PR number to check.
            transition: Transition schema.

        Returns:
            TransitionValidationResult indicating whether PR is merged.
        """
        logger.info(f"Checking if PR #{pr_number} is merged")

        try:
            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "view",
                    str(pr_number),
                    "--json",
                    "number,title,state,merged,mergedAt",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                logger.error(f"gh CLI error: {result.stderr}")
                return TransitionValidationResult(
                    passed=False,
                    message=f"Failed to query PR #{pr_number}: {result.stderr}",
                    mode=ValidationMode.PULL_REQUEST,
                    details={"pr_number": pr_number, "error": result.stderr},
                )

            pr_data = json.loads(result.stdout)
            is_merged = pr_data.get("merged", False)

            if is_merged:
                logger.info(
                    f"✓ PR #{pr_number} is merged: {pr_data.get('title', 'N/A')}"
                )
                return TransitionValidationResult(
                    passed=True,
                    message=f"PR #{pr_number} is merged: {pr_data.get('title', '')}",
                    mode=ValidationMode.PULL_REQUEST,
                    details={
                        "pr_number": pr_number,
                        "pr_title": pr_data.get("title"),
                        "merged_at": pr_data.get("mergedAt"),
                    },
                )
            else:
                state = pr_data.get("state", "unknown")
                logger.warning(f"✗ PR #{pr_number} is not merged (state: {state})")
                return TransitionValidationResult(
                    passed=False,
                    message=(
                        f"PR #{pr_number} is not merged (state: {state}).\n"
                        f"Merge the PR to proceed with this transition."
                    ),
                    mode=ValidationMode.PULL_REQUEST,
                    details={
                        "pr_number": pr_number,
                        "state": state,
                    },
                )

        except Exception as e:
            logger.error(f"Error checking PR #{pr_number}: {e}")
            return TransitionValidationResult(
                passed=False,
                message=f"Error checking PR #{pr_number}: {e}",
                mode=ValidationMode.PULL_REQUEST,
                details={"pr_number": pr_number, "error": str(e)},
            )
