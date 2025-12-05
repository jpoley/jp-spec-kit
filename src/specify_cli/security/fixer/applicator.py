"""Patch application workflow for security fixes.

This module provides functionality to apply generated patches to source code files,
with confirmation workflows and rollback capability.
"""

import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Protocol

from specify_cli.security.fixer.models import FixResult, Patch


class ApplyStatus(Enum):
    """Status of patch application."""

    SUCCESS = "success"  # Patch applied successfully
    FAILED = "failed"  # Patch application failed
    SKIPPED = "skipped"  # User skipped the patch
    CONFLICT = "conflict"  # Patch has conflicts


@dataclass
class ApplyResult:
    """Result of applying a patch to a file."""

    finding_id: str
    file_path: Path
    status: ApplyStatus
    message: str
    backup_path: Path | None = None
    applied_at: datetime = field(default_factory=datetime.now)

    @property
    def is_successful(self) -> bool:
        """Returns True if patch was applied successfully."""
        return self.status == ApplyStatus.SUCCESS

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "finding_id": self.finding_id,
            "file_path": str(self.file_path),
            "status": self.status.value,
            "message": self.message,
            "backup_path": str(self.backup_path) if self.backup_path else None,
            "applied_at": self.applied_at.isoformat(),
        }


class ConfirmationHandler(Protocol):
    """Protocol for user confirmation interactions."""

    def confirm_patch(self, patch: Patch, confidence: float) -> bool:
        """Ask user to confirm applying a patch.

        Args:
            patch: The patch to apply.
            confidence: Confidence score (0.0-1.0).

        Returns:
            True if user confirms, False otherwise.
        """
        ...


class DefaultConfirmationHandler:
    """Default confirmation handler using console input."""

    def confirm_patch(self, patch: Patch, confidence: float) -> bool:
        """Ask user to confirm via console."""
        print("\n" + "=" * 80)
        print(f"Fix for: {patch.file_path}")
        print(f"Lines: {patch.line_start}-{patch.line_end}")
        print(f"Confidence: {confidence:.0%}")
        print("=" * 80)
        print("\nOriginal code:")
        print("-" * 80)
        print(patch.original_code)
        print("\nFixed code:")
        print("-" * 80)
        print(patch.fixed_code)
        print("\nUnified diff:")
        print("-" * 80)
        print(patch.unified_diff)
        print("=" * 80)

        while True:
            response = input("\nApply this patch? (y/n/s=skip): ").lower().strip()
            if response in ("y", "yes"):
                return True
            elif response in ("n", "no", "s", "skip"):
                return False
            print("Please enter 'y' for yes or 'n' for no/skip")


class PatchApplicator:
    """Applies security fix patches to source code files.

    Provides interactive confirmation workflow and automatic rollback capability.

    Example:
        >>> applicator = PatchApplicator()
        >>> result = applicator.apply(patch)
        >>> if result.is_successful:
        ...     print(f"Applied to {result.file_path}")
    """

    def __init__(
        self,
        confirmation_handler: ConfirmationHandler | None = None,
        create_backups: bool = True,
        dry_run: bool = False,
    ):
        """Initialize patch applicator.

        Args:
            confirmation_handler: Handler for user confirmations.
            create_backups: Whether to create .orig backup files.
            dry_run: If True, don't actually modify files.
        """
        self.confirmation_handler = confirmation_handler or DefaultConfirmationHandler()
        self.create_backups = create_backups
        self.dry_run = dry_run

    def apply_fix(self, fix_result: FixResult, confirm: bool = True) -> ApplyResult:
        """Apply a fix result to the source code.

        Args:
            fix_result: The fix result containing patch.
            confirm: Whether to ask for user confirmation.

        Returns:
            ApplyResult with status and details.
        """
        if not fix_result.patch:
            return ApplyResult(
                finding_id=fix_result.finding_id,
                file_path=Path(""),
                status=ApplyStatus.FAILED,
                message="No patch available to apply",
            )

        # Get user confirmation if required
        if confirm and not self.dry_run:
            if not self.confirmation_handler.confirm_patch(
                fix_result.patch, fix_result.confidence
            ):
                return ApplyResult(
                    finding_id=fix_result.finding_id,
                    file_path=fix_result.patch.file_path,
                    status=ApplyStatus.SKIPPED,
                    message="User skipped patch",
                )

        return self.apply_patch(fix_result.patch, fix_result.finding_id)

    def apply_patch(self, patch: Patch, finding_id: str) -> ApplyResult:
        """Apply a patch to a file.

        Args:
            patch: The patch to apply.
            finding_id: ID of the security finding.

        Returns:
            ApplyResult with status and details.
        """
        file_path = patch.file_path

        # Verify file exists
        if not file_path.exists():
            return ApplyResult(
                finding_id=finding_id,
                file_path=file_path,
                status=ApplyStatus.FAILED,
                message=f"File not found: {file_path}",
            )

        # Create backup if enabled
        backup_path = None
        if self.create_backups and not self.dry_run:
            backup_path = Path(f"{file_path}.orig")
            try:
                shutil.copy2(file_path, backup_path)
            except OSError as e:
                return ApplyResult(
                    finding_id=finding_id,
                    file_path=file_path,
                    status=ApplyStatus.FAILED,
                    message=f"Failed to create backup: {e}",
                )

        if self.dry_run:
            return ApplyResult(
                finding_id=finding_id,
                file_path=file_path,
                status=ApplyStatus.SUCCESS,
                message="Dry run - patch not actually applied",
                backup_path=backup_path,
            )

        # Try to apply the patch
        try:
            # Read current file content
            with open(file_path, encoding="utf-8") as f:
                current_content = f.read()

            # Try to find and replace the vulnerable code
            if patch.original_code in current_content:
                # Simple string replacement
                fixed_content = current_content.replace(
                    patch.original_code, patch.fixed_code, 1
                )

                # Write the fixed content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)

                return ApplyResult(
                    finding_id=finding_id,
                    file_path=file_path,
                    status=ApplyStatus.SUCCESS,
                    message="Patch applied successfully",
                    backup_path=backup_path,
                )
            else:
                # Code has changed - conflict
                return ApplyResult(
                    finding_id=finding_id,
                    file_path=file_path,
                    status=ApplyStatus.CONFLICT,
                    message="Original code not found in file - possible conflict",
                    backup_path=backup_path,
                )

        except OSError as e:
            # Restore backup on failure
            if backup_path and backup_path.exists():
                shutil.copy2(backup_path, file_path)

            return ApplyResult(
                finding_id=finding_id,
                file_path=file_path,
                status=ApplyStatus.FAILED,
                message=f"Failed to apply patch: {e}",
                backup_path=backup_path,
            )

    def apply_multiple(
        self, fix_results: list[FixResult], confirm: bool = True
    ) -> list[ApplyResult]:
        """Apply multiple fix results.

        Args:
            fix_results: List of fix results to apply.
            confirm: Whether to ask for confirmation for each patch.

        Returns:
            List of ApplyResults.
        """
        results = []
        for fix_result in fix_results:
            result = self.apply_fix(fix_result, confirm=confirm)
            results.append(result)

            # Print summary after each application
            if result.is_successful:
                print(f"✓ Applied fix to {result.file_path}")
            elif result.status == ApplyStatus.SKIPPED:
                print(f"⊘ Skipped {result.file_path}")
            else:
                print(f"✗ Failed to apply fix to {result.file_path}: {result.message}")

        return results

    def rollback(self, apply_result: ApplyResult) -> bool:
        """Rollback a previously applied patch.

        Args:
            apply_result: The result of a previous patch application.

        Returns:
            True if rollback succeeded, False otherwise.
        """
        if not apply_result.backup_path or not apply_result.backup_path.exists():
            return False

        try:
            shutil.copy2(apply_result.backup_path, apply_result.file_path)
            return True
        except OSError:
            return False

    def save_patch_file(self, patch: Patch, output_dir: Path, finding_id: str) -> Path:
        """Save a patch to a .patch file.

        Args:
            patch: The patch to save.
            output_dir: Directory to save patch files.
            finding_id: ID of the security finding.

        Returns:
            Path to the saved patch file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create filename from finding ID and file path
        safe_filename = (
            f"{finding_id}_{patch.file_path.name}".replace("/", "_")
            .replace(" ", "_")
            .replace("..", "")
        )
        patch_file = output_dir / f"{safe_filename}.patch"

        # Save the patch
        patch.save_patch(patch_file)

        return patch_file

    def save_patches(
        self, fix_results: list[FixResult], output_dir: Path
    ) -> list[Path]:
        """Save multiple patches to .patch files.

        Args:
            fix_results: List of fix results with patches.
            output_dir: Directory to save patch files.

        Returns:
            List of paths to saved patch files.
        """
        patch_files = []

        for result in fix_results:
            if result.patch:
                patch_file = self.save_patch_file(
                    result.patch, output_dir, result.finding_id
                )
                patch_files.append(patch_file)

        return patch_files
