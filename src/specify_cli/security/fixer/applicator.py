"""Patch application workflow for security fixes.

This module provides functionality to apply generated patches to source code files,
with confirmation workflows and rollback capability.
"""

import hashlib
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Protocol

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
        >>> result = applicator.apply_patch(patch, finding_id="SEC-001")
        >>> if result.is_successful:
        ...     print(f"Applied to {result.file_path}")
    """

    def __init__(
        self,
        confirmation_handler: ConfirmationHandler | None = None,
        create_backups: bool = True,
        dry_run: bool = False,
        progress_callback: Callable[[str], None] | None = None,
    ):
        """Initialize patch applicator.

        Args:
            confirmation_handler: Handler for user confirmations.
            create_backups: Whether to create .orig backup files.
            dry_run: If True, don't actually modify files.
            progress_callback: Optional callback for progress updates (replaces print).
        """
        self.confirmation_handler = confirmation_handler or DefaultConfirmationHandler()
        self.create_backups = create_backups
        self.dry_run = dry_run
        self.progress_callback = progress_callback

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

    def _get_numbered_backup_path(self, file_path: Path) -> Path:
        """Get a unique numbered backup path.

        Generates paths like file.py.orig, file.py.orig.1, file.py.orig.2, etc.
        to avoid overwriting existing backups.

        Args:
            file_path: The file to back up.

        Returns:
            A unique backup path that doesn't exist.
        """
        backup_path = Path(f"{file_path}.orig")
        if not backup_path.exists():
            return backup_path

        # Find next available number
        counter = 1
        while True:
            numbered_backup = Path(f"{file_path}.orig.{counter}")
            if not numbered_backup.exists():
                return numbered_backup
            counter += 1

    def apply_patch(self, patch: Patch, finding_id: str) -> ApplyResult:
        """Apply a patch to a file.

        Note: This method has a race condition between reading and writing the file.
        If the file is modified between read and write, changes could be lost.
        For concurrent access, use file locking mechanisms.

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

        # Create backup if enabled (with numbered backups to avoid overwriting)
        backup_path = None
        if self.create_backups and not self.dry_run:
            backup_path = self._get_numbered_backup_path(file_path)
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
            # Read current file content with encoding fallback
            encoding_used = "utf-8"
            try:
                current_content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                # Fallback to latin-1 for files with non-UTF-8 encoding
                current_content = file_path.read_text(encoding="latin-1")
                encoding_used = "latin-1"

            # Normalize line endings for comparison (handle CRLF vs LF)
            normalized_content = current_content.replace("\r\n", "\n")
            normalized_original = patch.original_code.replace("\r\n", "\n")

            # Try to find and replace the vulnerable code using line-based replacement
            # This is more precise than simple string replacement
            if normalized_original in normalized_content:
                # Use line-based replacement to avoid matching wrong occurrences
                lines = current_content.splitlines(keepends=True)
                original_lines = patch.original_code.splitlines(keepends=True)

                # Find the line range to replace
                replaced = False
                for i in range(max(0, len(lines) - len(original_lines) + 1)):
                    # Check if this is the matching section
                    if lines[i : i + len(original_lines)] == original_lines:
                        # Replace with fixed code
                        fixed_lines = patch.fixed_code.splitlines(keepends=True)
                        lines[i : i + len(original_lines)] = fixed_lines
                        replaced = True
                        break

                if replaced:
                    fixed_content = "".join(lines)

                    # Write the fixed content (use same encoding as read)
                    file_path.write_text(fixed_content, encoding=encoding_used)

                    return ApplyResult(
                        finding_id=finding_id,
                        file_path=file_path,
                        status=ApplyStatus.SUCCESS,
                        message="Patch applied successfully",
                        backup_path=backup_path,
                    )
                else:
                    # Fallback to simple string replacement (shouldn't happen)
                    fixed_content = current_content.replace(
                        patch.original_code, patch.fixed_code, 1
                    )

                    # Write using same encoding as read
                    file_path.write_text(fixed_content, encoding=encoding_used)

                    return ApplyResult(
                        finding_id=finding_id,
                        file_path=file_path,
                        status=ApplyStatus.SUCCESS,
                        message="Patch applied successfully (string replacement)",
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

        except (OSError, UnicodeDecodeError) as e:
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

    def _report_progress(self, message: str) -> None:
        """Report progress via callback or print.

        Args:
            message: Progress message to report.
        """
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)

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

            # Report progress after each application
            if result.is_successful:
                self._report_progress(f"✓ Applied fix to {result.file_path}")
            elif result.status == ApplyStatus.SKIPPED:
                self._report_progress(f"⊘ Skipped {result.file_path}")
            else:
                self._report_progress(
                    f"✗ Failed to apply fix to {result.file_path}: {result.message}"
                )

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

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal and collision attacks.

        Args:
            filename: The filename to sanitize.

        Returns:
            A safe filename with only alphanumeric, dash, underscore, and dot.
        """
        # Remove all characters except alphanumeric, dash, underscore, and dot
        # This prevents: path separators (/, \), null bytes, "..", special chars
        safe = re.sub(r"[^\w\-.]", "_", filename)

        # Remove leading dots to prevent hidden files
        safe = safe.lstrip(".")

        # Fallback for empty result (e.g., input was "...")
        if not safe:
            safe = "unnamed"

        # Truncate to reasonable length
        if len(safe) > 200:
            safe = safe[:200]

        return safe

    def save_patch_file(self, patch: Patch, output_dir: Path, finding_id: str) -> Path:
        """Save a patch to a .patch file.

        Uses sanitized filenames with hash suffix to prevent collisions and path traversal.

        Args:
            patch: The patch to save.
            output_dir: Directory to save patch files.
            finding_id: ID of the security finding.

        Returns:
            Path to the saved patch file.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize finding ID and filename to prevent path traversal
        safe_finding_id = self._sanitize_filename(finding_id)
        safe_file_name = self._sanitize_filename(patch.file_path.name)

        # Add hash suffix to prevent collisions between similar IDs
        # e.g., "SQL-001" and "SQL_001" would both sanitize to "SQL_001"
        # The hash ensures they get different filenames
        collision_hash = hashlib.sha256(
            f"{finding_id}_{patch.file_path}".encode()
        ).hexdigest()[:8]

        safe_filename = f"{safe_finding_id}_{safe_file_name}_{collision_hash}"
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
