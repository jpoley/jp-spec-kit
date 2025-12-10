#!/usr/bin/env python3
"""
release.py - One-command release script for jp-spec-kit

Usage:
    ./scripts/release.py                    # Auto-increment patch (0.2.343 → 0.2.344)
    ./scripts/release.py 0.3.0              # Specific version
    ./scripts/release.py --minor            # Bump minor (0.2.343 → 0.3.0)
    ./scripts/release.py --major            # Bump major (0.2.343 → 1.0.0)
    ./scripts/release.py --dry-run          # Show what would happen
    ./scripts/release.py --push             # Auto-push without confirmation

This script:
1. Determines the new version (auto-increment or specified)
2. Updates pyproject.toml and src/specify_cli/__init__.py
3. Commits the version bump
4. Creates a git tag
5. Pushes to origin (with confirmation)
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a command and optionally capture output."""
    print(f"  $ {' '.join(cmd)}")
    return subprocess.run(
        cmd,
        check=check,
        capture_output=capture,
        text=True,
    )


def get_current_version() -> str:
    """Read current version from pyproject.toml."""
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        print("Error: pyproject.toml not found. Run from project root.")
        sys.exit(1)

    content = pyproject.read_text()
    match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
    if not match:
        print("Error: Could not find version in pyproject.toml")
        sys.exit(1)

    return match.group(1)


def get_latest_tag() -> str | None:
    """Get the latest git tag."""
    result = run(
        ["git", "tag", "-l", "v*", "--sort=-v:refname"],
        capture=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return result.stdout.strip().split("\n")[0]


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse a version string into (major, minor, patch)."""
    version = version.lstrip("v")
    parts = version.split(".")
    if len(parts) != 3:
        print(f"Error: Invalid version format: {version}")
        sys.exit(1)
    try:
        return int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        print(f"Error: Invalid version numbers: {version}")
        sys.exit(1)


def bump_version(current: str, bump_type: str) -> str:
    """Bump version based on type: patch, minor, or major."""
    major, minor, patch = parse_version(current)

    if bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "major":
        return f"{major + 1}.0.0"
    else:
        print(f"Error: Unknown bump type: {bump_type}")
        sys.exit(1)


def update_version_files(new_version: str, dry_run: bool = False) -> None:
    """Update version in pyproject.toml and __init__.py."""
    files = [
        ("pyproject.toml", r'^version\s*=\s*"[^"]+"', f'version = "{new_version}"'),
        (
            "src/specify_cli/__init__.py",
            r'__version__\s*=\s*"[^"]+"',
            f'__version__ = "{new_version}"',
        ),
    ]

    for filepath, pattern, replacement in files:
        path = Path(filepath)
        if not path.exists():
            print(f"  Warning: {filepath} not found, skipping")
            continue

        content = path.read_text()
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        if content == new_content:
            print(f"  {filepath}: no change needed")
        elif dry_run:
            print(f"  {filepath}: would update to {new_version}")
        else:
            path.write_text(new_content)
            print(f"  {filepath}: updated to {new_version}")


def check_git_status() -> bool:
    """Check if working directory is clean (except version files)."""
    result = run(["git", "status", "--porcelain"], capture=True)
    if result.returncode != 0:
        return False

    # Allow only version file changes
    allowed_files = {"pyproject.toml", "src/specify_cli/__init__.py"}
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        # Parse git status output (e.g., " M pyproject.toml")
        filepath = line[3:].strip()
        if filepath not in allowed_files:
            print(f"  Warning: Uncommitted changes in {filepath}")
            return False
    return True


def check_on_main_branch() -> bool:
    """Verify we're on main branch."""
    result = run(["git", "branch", "--show-current"], capture=True)
    branch = result.stdout.strip()
    if branch != "main":
        print(f"  Warning: Not on main branch (currently on: {branch})")
        return False
    return True


def tag_exists(tag: str) -> bool:
    """Check if a tag already exists."""
    result = run(["git", "tag", "-l", tag], capture=True, check=False)
    return bool(result.stdout.strip())


def main():
    parser = argparse.ArgumentParser(
        description="Create a new release with version bump, commit, and tag",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    Auto-increment patch version
  %(prog)s 1.0.0              Set specific version
  %(prog)s --minor            Bump minor version
  %(prog)s --major            Bump major version
  %(prog)s --dry-run          Preview changes without making them
  %(prog)s --push             Skip confirmation and push immediately
        """,
    )
    parser.add_argument("version", nargs="?", help="Specific version to release (e.g., 1.0.0)")
    parser.add_argument("--major", action="store_true", help="Bump major version (X.0.0)")
    parser.add_argument("--minor", action="store_true", help="Bump minor version (0.X.0)")
    parser.add_argument("--patch", action="store_true", help="Bump patch version (0.0.X) [default]")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--push", action="store_true", help="Push without confirmation")
    parser.add_argument("--force", action="store_true", help="Skip safety checks")

    args = parser.parse_args()

    # Determine bump type
    if sum([args.major, args.minor, args.patch]) > 1:
        print("Error: Can only specify one of --major, --minor, --patch")
        sys.exit(1)

    print("\n🚀 JP Spec Kit Release Script\n")
    print("=" * 50)

    # Get current version
    print("\n📋 Current state:")
    current_version = get_current_version()
    print(f"  Version in pyproject.toml: {current_version}")

    latest_tag = get_latest_tag()
    if latest_tag:
        print(f"  Latest git tag: {latest_tag}")

    # Determine new version
    if args.version:
        new_version = args.version.lstrip("v")
    elif args.major:
        new_version = bump_version(current_version, "major")
    elif args.minor:
        new_version = bump_version(current_version, "minor")
    else:
        new_version = bump_version(current_version, "patch")

    tag_name = f"v{new_version}"
    print(f"\n📦 New version: {new_version}")
    print(f"   Tag name: {tag_name}")

    # Safety checks
    print("\n🔍 Safety checks:")
    if not args.force:
        if not check_on_main_branch():
            print("\n❌ Not on main branch. Use --force to override.")
            sys.exit(1)

        if tag_exists(tag_name):
            print(f"\n❌ Tag {tag_name} already exists!")
            sys.exit(1)
        print(f"  ✓ Tag {tag_name} does not exist")

        if not check_git_status():
            print("\n❌ Working directory has uncommitted changes. Commit or stash first.")
            sys.exit(1)
        print("  ✓ Working directory is clean")
    else:
        print("  ⚠️  Safety checks skipped (--force)")

    # Dry run stops here
    if args.dry_run:
        print("\n🔍 Dry run - would perform these actions:")
        print(f"  1. Update pyproject.toml: version = \"{new_version}\"")
        print(f"  2. Update __init__.py: __version__ = \"{new_version}\"")
        print(f"  3. Commit: \"chore: release v{new_version}\"")
        print(f"  4. Create tag: {tag_name}")
        print(f"  5. Push: git push origin main --tags")
        print("\nNo changes made.")
        sys.exit(0)

    # Confirm
    if not args.push:
        print(f"\n⚠️  This will release v{new_version}")
        response = input("   Continue? [y/N]: ").strip().lower()
        if response != "y":
            print("\n❌ Aborted.")
            sys.exit(1)

    # Update files
    print("\n📝 Updating version files:")
    update_version_files(new_version)

    # Git operations
    print("\n📦 Creating commit and tag:")
    run(["git", "add", "pyproject.toml", "src/specify_cli/__init__.py"])
    run(["git", "commit", "-m", f"chore: release v{new_version}"])
    run(["git", "tag", tag_name])

    # Push
    print("\n🚀 Pushing to origin:")
    if not args.push:
        response = input("   Push now? [Y/n]: ").strip().lower()
        if response == "n":
            print(f"\n✅ Release v{new_version} created locally.")
            print(f"   To push: git push origin main --tags")
            print(f"   To undo: git reset --hard HEAD~1 && git tag -d {tag_name}")
            sys.exit(0)

    run(["git", "push", "origin", "main", "--tags"])

    print(f"\n✅ Successfully released v{new_version}!")
    print(f"   GitHub Actions will create the release automatically.")
    print(f"   View at: https://github.com/jpoley/jp-spec-kit/releases/tag/{tag_name}")


if __name__ == "__main__":
    main()
