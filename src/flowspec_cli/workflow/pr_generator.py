"""Pull request generator with human approval workflow.

This module provides the PRGenerator class for creating GitHub pull requests
from completed tasks with human approval and comprehensive PR body generation.
"""

from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PRGenerationResult:
    """Result of PR generation attempt.

    Attributes:
        success: Whether PR was successfully created
        pr_url: URL of created PR (if successful)
        error_message: Error message (if failed)
    """

    success: bool
    pr_url: str | None = None
    error_message: str | None = None


class PRGeneratorError(Exception):
    """Raised when PR generation fails."""

    pass


class PRGenerator:
    """Generates pull requests from completed tasks with human approval.

    The PR generator creates well-formatted pull requests with:
    - Conventional commit-style titles
    - Comprehensive PR bodies with Summary, ACs, Test Plan
    - Human approval workflow before creation
    - Graceful error handling

    Example:
        >>> generator = PRGenerator("task-123")
        >>> result = generator.generate(
        ...     task_title="Add user authentication",
        ...     acceptance_criteria=[...],
        ...     test_plan="...",
        ...     validation_results={},
        ... )
        >>> if result.success:
        ...     print(f"PR created: {result.pr_url}")
    """

    def __init__(self, task_id: str) -> None:
        """Initialize the PR generator.

        Args:
            task_id: The ID of the task to create a PR for
        """
        self.task_id = task_id

    def generate(
        self,
        task_title: str,
        acceptance_criteria: list[dict[str, Any]] | list[str],
        test_plan: str,
        implementation_notes: str | None = None,
        validation_results: dict[str, Any] | None = None,
        scope: str | None = None,
        pr_type: str = "feat",
        require_approval: bool = True,
    ) -> PRGenerationResult:
        """Generate a pull request with human approval.

        This method:
        1. Generates PR title from task title
        2. Generates comprehensive PR body
        3. Presents PR preview to user
        4. Requests explicit human approval
        5. Creates PR via gh CLI
        6. Returns PR URL on success

        Args:
            task_title: Title of the task
            acceptance_criteria: List of acceptance criteria (checked)
            test_plan: Test plan description
            implementation_notes: Optional implementation notes
            validation_results: Optional validation results
            scope: Optional scope for conventional commit (e.g., "auth", "api")
            pr_type: Type of PR (feat, fix, docs, refactor, etc.)
            require_approval: Whether to require human approval (default: True)

        Returns:
            PRGenerationResult with success status and PR URL or error

        Raises:
            PRGeneratorError: If generation fails critically
        """
        # AC #1: Generate PR title
        pr_title = self._generate_pr_title(task_title, scope, pr_type)

        # AC #2, #3, #4: Generate PR body
        pr_body = self._generate_pr_body(
            acceptance_criteria=acceptance_criteria,
            test_plan=test_plan,
            implementation_notes=implementation_notes,
            validation_results=validation_results,
        )

        # AC #4: Present PR preview
        self._present_pr_preview(pr_title, pr_body)

        # AC #5: Request human approval
        if require_approval:
            if not self._request_approval():
                logger.info("PR creation cancelled by user")
                return PRGenerationResult(
                    success=False,
                    error_message="PR creation cancelled by user",
                )

        # AC #7: Check if branch is pushed
        if not self._is_branch_pushed():
            logger.warning("Branch not pushed to remote")
            print("\n⚠️  Warning: Current branch is not pushed to remote.")
            print("Please push your branch first:")
            print("  git push -u origin $(git branch --show-current)")
            return PRGenerationResult(
                success=False,
                error_message="Branch not pushed to remote. Please push first.",
            )

        # AC #6: Create PR using gh CLI
        try:
            pr_url = self._create_pr(pr_title, pr_body)
            logger.info(f"PR created successfully: {pr_url}")
            return PRGenerationResult(success=True, pr_url=pr_url)
        except PRGeneratorError as e:
            # AC #8: Handle gh CLI errors gracefully
            logger.error(f"Failed to create PR: {e}")
            return PRGenerationResult(
                success=False,
                error_message=str(e),
            )

    def _generate_pr_title(
        self, task_title: str, scope: str | None, pr_type: str
    ) -> str:
        """Generate PR title in conventional commit format.

        Args:
            task_title: The task title
            scope: Optional scope (e.g., "auth", "api")
            pr_type: Type of change (feat, fix, docs, etc.)

        Returns:
            Formatted PR title (e.g., "feat(auth): task-title")
        """
        # Clean up task title: remove task ID prefix if present
        title = re.sub(r"^task-\d+\s*[-:]\s*", "", task_title, flags=re.IGNORECASE)
        title = title.strip()

        # Convert to lowercase for conventional commit style
        title_lower = title[0].lower() + title[1:] if title else title

        if scope:
            return f"{pr_type}({scope}): {title_lower}"
        else:
            return f"{pr_type}: {title_lower}"

    def _generate_pr_body(
        self,
        acceptance_criteria: list[dict[str, Any]] | list[str],
        test_plan: str,
        implementation_notes: str | None = None,
        validation_results: dict[str, Any] | None = None,
    ) -> str:
        """Generate comprehensive PR body.

        Args:
            acceptance_criteria: List of acceptance criteria
            test_plan: Test plan description
            implementation_notes: Optional implementation notes
            validation_results: Optional validation results

        Returns:
            Formatted PR body in markdown
        """
        body_parts = []

        # Summary section
        body_parts.append("## Summary")
        body_parts.append(f"Completes task: {self.task_id}")
        body_parts.append("")

        if implementation_notes:
            body_parts.append(implementation_notes.strip())
            body_parts.append("")

        # Acceptance Criteria section
        body_parts.append("## Acceptance Criteria")
        body_parts.append("")
        if acceptance_criteria:
            for i, ac in enumerate(acceptance_criteria, start=1):
                if isinstance(ac, dict):
                    ac_text = ac.get("text", "")
                    checked = ac.get("checked", False)
                    checkbox = "[x]" if checked else "[ ]"
                elif isinstance(ac, str):
                    ac_text = ac
                    checkbox = "[x]"  # Assume checked if plain string
                else:
                    continue

                body_parts.append(f"{i}. {checkbox} {ac_text}")
        else:
            body_parts.append("No acceptance criteria defined.")

        body_parts.append("")

        # Test Plan section
        body_parts.append("## Test Plan")
        body_parts.append("")
        body_parts.append(test_plan.strip())
        body_parts.append("")

        # Validation Results section (if provided)
        if validation_results:
            body_parts.append("## Validation Results")
            body_parts.append("")
            for key, value in validation_results.items():
                if isinstance(value, bool):
                    status = "✅ Pass" if value else "❌ Fail"
                    body_parts.append(f"- **{key}**: {status}")
                else:
                    body_parts.append(f"- **{key}**: {value}")
            body_parts.append("")

        return "\n".join(body_parts)

    def _present_pr_preview(self, title: str, body: str) -> None:
        """Present PR preview to user.

        Args:
            title: PR title
            body: PR body
        """
        print("\n" + "=" * 80)
        print("PR PREVIEW")
        print("=" * 80)
        print(f"\nTitle: {title}\n")
        print("Body:")
        print("-" * 80)
        print(body)
        print("-" * 80)

    def _request_approval(self) -> bool:
        """Request explicit human approval for PR creation.

        Returns:
            True if approved, False if rejected
        """
        print("\n")
        response = input("Create this pull request? [y/N]: ").strip().lower()
        return response in ("y", "yes")

    def _is_branch_pushed(self) -> bool:
        """Check if current branch is pushed to remote.

        Returns:
            True if branch is pushed and up-to-date, False otherwise
        """
        try:
            # Check if branch has upstream
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                # No upstream configured
                return False

            # Check if local and remote are in sync
            result = subprocess.run(
                ["git", "status", "--porcelain", "--branch"],
                capture_output=True,
                text=True,
                check=True,
            )

            # Look for "ahead" or "behind" indicators
            for line in result.stdout.split("\n"):
                if line.startswith("##"):
                    if "[ahead" in line or "[behind" in line:
                        # Branch has diverged or has unpushed commits
                        if "[ahead" in line:
                            return False
                    break

            return True
        except subprocess.CalledProcessError:
            return False

    def _create_pr(self, title: str, body: str) -> str:
        """Create PR using gh CLI.

        Args:
            title: PR title
            body: PR body

        Returns:
            PR URL

        Raises:
            PRGeneratorError: If gh CLI command fails
        """
        try:
            result = subprocess.run(
                ["gh", "pr", "create", "--title", title, "--body", body],
                capture_output=True,
                text=True,
                check=True,
            )

            pr_url = result.stdout.strip()

            # Extract URL from output (gh CLI sometimes includes extra text)
            url_match = re.search(r"https://github\.com/[^\s]+", pr_url)
            if url_match:
                pr_url = url_match.group(0)

            return pr_url

        except FileNotFoundError as e:
            raise PRGeneratorError(
                "gh CLI not found. Please install GitHub CLI: https://cli.github.com/"
            ) from e
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else str(e)
            raise PRGeneratorError(f"Failed to create PR: {error_msg}") from e
