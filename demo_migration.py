#!/usr/bin/env python3
"""Demo script showing task schema migration usage."""

from pathlib import Path
from specify_cli.satellite.migration import migrate_tasks_cli, TaskMigrator

def demo_single_file():
    """Demo migrating a single file."""
    print("=" * 60)
    print("Demo: Single File Migration")
    print("=" * 60)

    # Create a temporary test file
    demo_dir = Path("demo_tasks")
    demo_dir.mkdir(exist_ok=True)

    task_file = demo_dir / "task-001 - Example.md"
    task_file.write_text("""---
id: task-001
title: Example migration task
status: To Do
assignee:
  - '@user'
labels:
  - backend
created_date: '2025-11-24'
---

## Description

This is a sample v1 task that will be migrated to v2.

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 First criterion
- [ ] #2 Second criterion
<!-- AC:END -->
""")

    print("\nOriginal file content:")
    print("-" * 60)
    print(task_file.read_text())

    # Migrate the file
    migrator = TaskMigrator()
    result = migrator.migrate(task_file)

    print(f"\nMigration result: {'SUCCESS' if result else 'SKIPPED'}")

    print("\nMigrated file content:")
    print("-" * 60)
    print(task_file.read_text())

    # Cleanup
    import shutil
    shutil.rmtree(demo_dir)
    print("\n" + "=" * 60)


def demo_bulk_migration():
    """Demo bulk migration with dry-run."""
    print("\n" * 2)
    print("=" * 60)
    print("Demo: Bulk Migration with Dry-Run")
    print("=" * 60)

    # Create temporary test files
    demo_dir = Path("demo_bulk_tasks")
    demo_dir.mkdir(exist_ok=True)

    # Create multiple v1 tasks
    for i in range(1, 6):
        task_file = demo_dir / f"task-{i:03d} - Test-Task-{i}.md"
        task_file.write_text(f"""---
id: task-{i:03d}
title: Test task {i}
status: To Do
labels:
  - test
---

## Description
Task {i} description
""")

    # Create one v2 task (should be skipped)
    v2_task = demo_dir / "task-006 - Already-V2.md"
    v2_task.write_text("""---
id: task-006
title: Already migrated
status: Done
schema_version: '2'
---

This is already v2.
""")

    print(f"\nCreated {len(list(demo_dir.glob('task-*.md')))} task files")

    # Dry-run first
    print("\n--- DRY RUN ---")
    exit_code = migrate_tasks_cli(demo_dir, dry_run=True, verbose=True)

    print(f"\nDry-run exit code: {exit_code}")

    # Actual migration
    print("\n--- ACTUAL MIGRATION ---")
    exit_code = migrate_tasks_cli(demo_dir, verbose=True, cleanup=True)

    print(f"\nMigration exit code: {exit_code}")

    # Verify
    migrated = sum(1 for f in demo_dir.glob("task-*.md") if "schema_version: '2'" in f.read_text())
    print(f"\nTotal tasks with schema v2: {migrated}/6")

    # Cleanup
    import shutil
    shutil.rmtree(demo_dir)
    print("\n" + "=" * 60)


def demo_error_handling():
    """Demo error handling and backup restoration."""
    print("\n" * 2)
    print("=" * 60)
    print("Demo: Error Handling")
    print("=" * 60)

    demo_dir = Path("demo_error_tasks")
    demo_dir.mkdir(exist_ok=True)

    # Create a file with invalid YAML
    invalid_task = demo_dir / "task-invalid.md"
    invalid_task.write_text("""---
id: task-001
title: [broken yaml syntax
status: To Do
---

Body
""")

    print("\nAttempting to migrate file with invalid YAML...")

    migrator = TaskMigrator()
    try:
        migrator.migrate(invalid_task)
        print("ERROR: Should have raised MigrationError!")
    except Exception as e:
        print(f"Correctly caught error: {type(e).__name__}: {e}")

    # Cleanup
    import shutil
    shutil.rmtree(demo_dir)
    print("\n" + "=" * 60)


if __name__ == "__main__":
    demo_single_file()
    demo_bulk_migration()
    demo_error_handling()

    print("\n\nAll demos completed successfully!")
