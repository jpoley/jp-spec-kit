"""Patch application and rollback functionality.

This module handles applying security fix patches to source files,
with support for dry-run validation, backup creation, and rollback.
"""

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from flowspec_cli.security.fixer.models import Patch, FixResult


class ApplyStatus(Enum):
    """Status of patch application."""

    SUCCESS = "success"  # Patch applied successfully
    FAILED = "failed"  # Patch failed to apply
    CONFLICT = "conflict"  # Patch has merge conflicts
    SKIPPED = "skipped"  # Patch was skipped (dry-run or user declined)


@dataclass
class ApplyResult:
    """Result of applying a single patch."""

    patch: Patch
    status: ApplyStatus
    message: str = ""
    backup_path: Path | None = None

    @property
    def is_successful(self) -> bool:
        """Returns True if patch was applied successfully."""
        return self.status == ApplyStatus.SUCCESS

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "file_path": str(self.patch.file_path),
            "status": self.status.value,
            "message": self.message,
            "backup_path": str(self.backup_path) if self.backup_path else None,
        }


@dataclass
class BatchApplyResult:
    """Result of applying multiple patches."""

    results: list[ApplyResult] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def successful_count(self) -> int:
        """Count of successfully applied patches."""
        return sum(1 for r in self.results if r.is_successful)

    @property
    def failed_count(self) -> int:
        """Count of failed patches."""
        return sum(1 for r in self.results if not r.is_successful)

    @property
    def all_successful(self) -> bool:
        """Returns True if all patches were applied successfully."""
        return all(r.is_successful for r in self.results)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "timestamp": self.timestamp,
            "total": len(self.results),
            "successful": self.successful_count,
            "failed": self.failed_count,
            "results": [r.to_dict() for r in self.results],
        }


@dataclass
class PatchApplicatorConfig:
    """Configuration for patch application."""

    backup_dir: Path | None = None  # Directory for backups (default: .flowspec/backups)
    create_backups: bool = True  # Create backups before applying
    use_git_apply: bool = True  # Use git apply (vs manual file modification)


class PatchApplicator:
    """Applies security patches to source files.

    Provides functionality for applying patches with backup and rollback
    capabilities. Supports both git-based and manual patch application.

    Example:
        >>> applicator = PatchApplicator()
        >>> result = applicator.apply_patch(patch, dry_run=True)
        >>> if result.status == ApplyStatus.SUCCESS:
        ...     applicator.apply_patch(patch)  # Actually apply
    """

    def __init__(self, config: PatchApplicatorConfig | None = None):
        """Initialize patch applicator.

        Args:
            config: Applicator configuration options.
        """
        self.config = config or PatchApplicatorConfig()
        self._history: list[ApplyResult] = []

    def apply_patch(self, patch: Patch, dry_run: bool = False) -> ApplyResult:
        """Apply a single patch to its target file.

        Args:
            patch: Patch to apply.
            dry_run: If True, validate without applying.

        Returns:
            ApplyResult with status and details.
        """
        # Validate target file exists
        if not patch.file_path.exists():
            return ApplyResult(
                patch=patch,
                status=ApplyStatus.FAILED,
                message=f"Target file does not exist: {patch.file_path}",
            )

        # Dry-run validation
        if dry_run:
            return self._validate_patch(patch)

        # Create backup if enabled
        backup_path = None
        if self.config.create_backups:
            backup_path = self._create_backup(patch.file_path)
            if backup_path is None:
                return ApplyResult(
                    patch=patch,
                    status=ApplyStatus.FAILED,
                    message="Failed to create backup",
                )

        # Apply patch
        if self.config.use_git_apply:
            result = self._apply_with_git(patch)
        else:
            result = self._apply_manually(patch)

        result.backup_path = backup_path

        # Track in history for rollback
        if result.is_successful:
            self._history.append(result)

        return result

    def apply_patches(
        self, patches: list[Patch], dry_run: bool = False
    ) -> BatchApplyResult:
        """Apply multiple patches in sequence.

        Args:
            patches: List of patches to apply.
            dry_run: If True, validate without applying.

        Returns:
            BatchApplyResult with all results.
        """
        batch_result = BatchApplyResult()

        for patch in patches:
            result = self.apply_patch(patch, dry_run=dry_run)
            batch_result.results.append(result)

        return batch_result

    def apply_fix_results(
        self, fix_results: list[FixResult], dry_run: bool = False
    ) -> BatchApplyResult:
        """Apply patches from fix results.

        Extracts patches from FixResults and applies them.

        Args:
            fix_results: List of fix generation results.
            dry_run: If True, validate without applying.

        Returns:
            BatchApplyResult with all results.
        """
        patches = [fr.patch for fr in fix_results if fr.patch is not None]
        return self.apply_patches(patches, dry_run=dry_run)

    def rollback(self, result: ApplyResult) -> bool:
        """Rollback a single applied patch.

        Args:
            result: ApplyResult with backup information.

        Returns:
            True if rollback succeeded.
        """
        if not result.backup_path or not result.backup_path.exists():
            return False

        try:
            shutil.copy2(result.backup_path, result.patch.file_path)
            return True
        except OSError:
            return False

    def rollback_all(self) -> int:
        """Rollback all applied patches in reverse order.

        Returns:
            Number of successfully rolled back patches.
        """
        rolled_back = 0

        for result in reversed(self._history):
            if self.rollback(result):
                rolled_back += 1

        self._history.clear()
        return rolled_back

    def save_history(self, output_path: Path) -> None:
        """Save application history to JSON file.

        Args:
            output_path: Path to write history JSON.
        """
        history_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "applied": [r.to_dict() for r in self._history],
        }
        output_path.write_text(json.dumps(history_data, indent=2), encoding="utf-8")

    def _validate_patch(self, patch: Patch) -> ApplyResult:
        """Validate a patch without applying it."""
        if self.config.use_git_apply:
            return self._validate_with_git(patch)
        return self._validate_manually(patch)

    def _validate_with_git(self, patch: Patch) -> ApplyResult:
        """Validate patch using git apply --check."""
        try:
            # Write patch to temp file
            patch_content = patch.to_patch_file()
            result = subprocess.run(
                ["git", "apply", "--check", "-"],
                input=patch_content,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return ApplyResult(
                    patch=patch,
                    status=ApplyStatus.SKIPPED,
                    message="Dry-run: patch would apply cleanly",
                )
            else:
                # Check for conflict indicators
                if "patch does not apply" in result.stderr:
                    return ApplyResult(
                        patch=patch,
                        status=ApplyStatus.CONFLICT,
                        message=f"Patch conflict: {result.stderr.strip()}",
                    )
                return ApplyResult(
                    patch=patch,
                    status=ApplyStatus.FAILED,
                    message=f"Validation failed: {result.stderr.strip()}",
                )

        except subprocess.TimeoutExpired:
            return ApplyResult(
                patch=patch,
                status=ApplyStatus.FAILED,
                message="Git apply timed out",
            )
        except FileNotFoundError:
            # Git not available, fall back to manual validation
            return self._validate_manually(patch)

    def _validate_manually(self, patch: Patch) -> ApplyResult:
        """Validate patch manually by checking original code exists."""
        try:
            content = patch.file_path.read_text(encoding="utf-8")

            # Check if original code fragment exists in file
            if patch.original_code.strip() in content:
                return ApplyResult(
                    patch=patch,
                    status=ApplyStatus.SKIPPED,
                    message="Dry-run: original code found, patch can be applied",
                )
            else:
                return ApplyResult(
                    patch=patch,
                    status=ApplyStatus.CONFLICT,
                    message="Original code not found in file (may have changed)",
                )

        except OSError as e:
            return ApplyResult(
                patch=patch,
                status=ApplyStatus.FAILED,
                message=f"Failed to read file: {e}",
            )

    def _apply_with_git(self, patch: Patch) -> ApplyResult:
        """Apply patch using git apply."""
        try:
            patch_content = patch.to_patch_file()
            result = subprocess.run(
                ["git", "apply", "-"],
                input=patch_content,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return ApplyResult(
                    patch=patch,
                    status=ApplyStatus.SUCCESS,
                    message="Patch applied successfully via git",
                )
            else:
                if "patch does not apply" in result.stderr:
                    return ApplyResult(
                        patch=patch,
                        status=ApplyStatus.CONFLICT,
                        message=f"Merge conflict: {result.stderr.strip()}",
                    )
                return ApplyResult(
                    patch=patch,
                    status=ApplyStatus.FAILED,
                    message=f"Git apply failed: {result.stderr.strip()}",
                )

        except subprocess.TimeoutExpired:
            return ApplyResult(
                patch=patch,
                status=ApplyStatus.FAILED,
                message="Git apply timed out",
            )
        except FileNotFoundError:
            # Git not available, fall back to manual
            return self._apply_manually(patch)

    def _apply_manually(self, patch: Patch) -> ApplyResult:
        """Apply patch by direct file modification."""
        try:
            content = patch.file_path.read_text(encoding="utf-8")

            # Find and replace original code with fixed code
            if patch.original_code.strip() not in content:
                return ApplyResult(
                    patch=patch,
                    status=ApplyStatus.CONFLICT,
                    message="Original code not found in file",
                )

            new_content = content.replace(
                patch.original_code.strip(),
                patch.fixed_code.strip(),
                1,  # Replace only first occurrence
            )

            patch.file_path.write_text(new_content, encoding="utf-8")

            return ApplyResult(
                patch=patch,
                status=ApplyStatus.SUCCESS,
                message="Patch applied successfully via file modification",
            )

        except OSError as e:
            return ApplyResult(
                patch=patch,
                status=ApplyStatus.FAILED,
                message=f"Failed to modify file: {e}",
            )

    def _create_backup(self, file_path: Path) -> Path | None:
        """Create a backup of a file before patching."""
        backup_dir = self.config.backup_dir or Path(".flowspec/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.{timestamp}.bak"
        backup_path = backup_dir / backup_name

        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except OSError:
            return None
