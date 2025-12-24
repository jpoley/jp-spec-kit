#!/usr/bin/env python3
"""
release.py - Release workflow via PR for flowspec

Usage:
    ./scripts/release.py                    # Auto-increment patch (0.2.343 → 0.2.344)
    ./scripts/release.py 0.3.0              # Specific version
    ./scripts/release.py --minor            # Bump minor (0.2.343 → 0.3.0)
    ./scripts/release.py --major            # Bump major (0.2.343 → 1.0.0)
    ./scripts/release.py --dry-run          # Show what would happen
    ./scripts/release.py --create-pr        # Auto-create PR without confirmation
    ./scripts/release.py --commit-hash abc123  # Pin release to specific commit

This script:
1. Determines the new version (auto-increment or specified)
2. Creates a release branch (release/vX.Y.Z)
3. Updates pyproject.toml and src/flowspec_cli/__init__.py
4. Commits the version bump
5. Pushes the release branch
6. Creates a PR to main (with confirmation)

When the PR is merged:
- GitHub Actions detects the merge of a release/* branch
- Tags the merge commit (github.sha) - no .release-commit file needed
- Builds packages and creates GitHub Release with all artifacts
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path


def run(
    cmd: list[str], check: bool = True, capture: bool = False
) -> subprocess.CompletedProcess:
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
            "src/flowspec_cli/__init__.py",
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


def check_git_clean() -> bool:
    """Check if working directory is clean."""
    result = run(["git", "status", "--porcelain"], capture=True)
    if result.returncode != 0:
        return False

    if result.stdout.strip():
        print("  Warning: Working directory has uncommitted changes")
        for line in result.stdout.strip().split("\n"):
            print(f"    {line}")
        return False
    return True


def cleanup_internal_dev_logs(dry_run: bool = False) -> list[Path]:
    """Remove internal development logs before release.

    Internal dev logs are stored in .flowspec/logs/ and should not be
    included in releases as they contain developer-specific information.

    Returns:
        List of deleted files.
    """
    internal_logs_dir = Path(".flowspec/logs")
    deleted_files: list[Path] = []

    if not internal_logs_dir.exists():
        print("  No internal logs directory found")
        return deleted_files

    # Find all log files (but preserve .gitkeep files)
    for log_file in internal_logs_dir.rglob("*"):
        if log_file.is_file() and log_file.name != ".gitkeep":
            if dry_run:
                print(f"  Would delete: {log_file}")
            else:
                log_file.unlink()
                print(f"  Deleted: {log_file}")
            deleted_files.append(log_file)

    if not deleted_files:
        print("  No internal logs to clean up")

    return deleted_files


def get_current_branch() -> str:
    """Get current git branch name."""
    result = run(["git", "branch", "--show-current"], capture=True)
    return result.stdout.strip()


def branch_exists(branch: str) -> bool:
    """Check if a branch already exists (local or remote)."""
    # Check local
    result = run(["git", "branch", "--list", branch], capture=True, check=False)
    if result.stdout.strip():
        return True
    # Check remote
    result = run(
        ["git", "ls-remote", "--heads", "origin", branch], capture=True, check=False
    )
    return bool(result.stdout.strip())


def tag_exists(tag: str) -> bool:
    """Check if a tag already exists."""
    result = run(["git", "tag", "-l", tag], capture=True, check=False)
    return bool(result.stdout.strip())


def check_gh_cli() -> bool:
    """Check if GitHub CLI is installed and authenticated."""
    result = run(["gh", "auth", "status"], capture=True, check=False)
    if result.returncode != 0:
        print("  Error: GitHub CLI not authenticated. Run 'gh auth login'")
        return False
    return True


def get_repo_url() -> str:
    """Get the GitHub repository URL for PR links."""
    result = run(["gh", "repo", "view", "--json", "url", "-q", ".url"], capture=True)
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Create a release PR with version bump",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    Auto-increment patch version
  %(prog)s 1.0.0              Set specific version
  %(prog)s --minor            Bump minor version
  %(prog)s --major            Bump major version
  %(prog)s --dry-run          Preview changes without making them
  %(prog)s --create-pr        Skip confirmation and create PR immediately

Workflow:
  1. Run this script to create a release PR
  2. Review the PR and ensure CI passes
  3. Merge the PR to main
  4. GitHub Actions automatically creates the tag and release
        """,
    )
    parser.add_argument(
        "version", nargs="?", help="Specific version to release (e.g., 1.0.0)"
    )
    parser.add_argument(
        "--major", action="store_true", help="Bump major version (X.0.0)"
    )
    parser.add_argument(
        "--minor", action="store_true", help="Bump minor version (0.X.0)"
    )
    parser.add_argument(
        "--patch", action="store_true", help="Bump patch version (0.0.X) [default]"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done"
    )
    parser.add_argument(
        "--create-pr", action="store_true", help="Create PR without confirmation"
    )
    parser.add_argument("--force", action="store_true", help="Skip safety checks")

    args = parser.parse_args()

    # Determine bump type
    if sum([args.major, args.minor, args.patch]) > 1:
        print("Error: Can only specify one of --major, --minor, --patch")
        sys.exit(1)

    print("\n Flowspec Release Script (PR Workflow)\n")
    print("=" * 60)

    # Safety check: Verify we're on main branch
    print("\n Checking prerequisites:")
    current_branch = get_current_branch()
    print(f"  Current branch: {current_branch}")

    if current_branch != "main" and not args.force:
        print(f"\n Warning: Not on main branch (on: {current_branch})")
        print("  Releases should typically start from main branch.")
        response = input("  Continue anyway? [y/N]: ").strip().lower()
        if response != "y":
            print("\n Aborted.")
            sys.exit(1)

    if not args.force and not check_git_clean():
        print("\n Working directory has uncommitted changes.")
        print("  Commit or stash them first, or use --force to override.")
        sys.exit(1)
    print("  Working directory is clean")

    if not args.dry_run and not check_gh_cli():
        sys.exit(1)
    print("  GitHub CLI authenticated")

    # Get current version
    print("\n Current state:")
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
    release_branch = f"release/{tag_name}"
    print(f"\n New version: {new_version}")
    print(f"   Tag name: {tag_name}")
    print(f"   Release branch: {release_branch}")

    # Safety checks
    print("\n Safety checks:")
    if tag_exists(tag_name):
        print(f"\n Tag {tag_name} already exists!")
        sys.exit(1)
    print(f"  Tag {tag_name} does not exist")

    if branch_exists(release_branch):
        print(f"\n Branch {release_branch} already exists!")
        print(f"  Delete it first: git branch -D {release_branch}")
        sys.exit(1)
    print(f"  Branch {release_branch} does not exist")

    # Dry run stops here
    if args.dry_run:
        print("\n Dry run - would perform these actions:")
        print(f"  1. Create branch: {release_branch}")
        print(f'  2. Update pyproject.toml: version = "{new_version}"')
        print(f'  3. Update __init__.py: __version__ = "{new_version}"')
        print("  4. Clean up internal development logs (.flowspec/logs/)")
        cleanup_internal_dev_logs(dry_run=True)
        print(f'  5. Commit: "chore: release v{new_version}"')
        print(f"  6. Push branch: {release_branch}")
        print(f'  7. Create PR: "Release v{new_version}" to main')
        print("\nNo changes made.")
        sys.exit(0)

    # Confirm
    if not args.create_pr:
        print(f"\n This will create a release PR for v{new_version}")
        print("   - Creates release branch")
        print("   - Updates version files")
        print("   - Pushes and opens PR")
        response = input("   Continue? [y/N]: ").strip().lower()
        if response != "y":
            print("\n Aborted.")
            sys.exit(1)

    # Create release branch
    print(f"\n Creating release branch: {release_branch}")
    run(["git", "checkout", "-b", release_branch])

    # Update files
    print("\n Updating version files:")
    update_version_files(new_version)

    # Clean up internal development logs
    print("\n Cleaning up internal development logs:")
    deleted_logs = cleanup_internal_dev_logs()

    # Git operations
    print("\n Creating commit:")
    files_to_stage = [
        "pyproject.toml",
        "src/flowspec_cli/__init__.py",
    ]

    # Stage deleted log files if any were removed
    if deleted_logs:
        files_to_stage.extend(str(f) for f in deleted_logs)

    run(["git", "add"] + files_to_stage)
    run(["git", "commit", "-m", f"chore: release v{new_version}"])

    # Push branch
    print(f"\n Pushing branch: {release_branch}")
    run(["git", "push", "-u", "origin", release_branch])

    # Create PR
    print("\n Creating pull request:")
    pr_title = f"Release v{new_version}"
    pr_body = f"""## Release v{new_version}

This PR releases version **{new_version}** of Flowspec.

### Changes
- Version bump: `{current_version}` → `{new_version}`

### What happens when this PR is merged
1. GitHub Actions detects the merge of the `release/*` branch
2. Tags the **merge commit** as `{tag_name}`
3. Builds template packages for all supported AI assistants
4. Creates GitHub Release with all artifacts

### Checklist
- [ ] Version bump is correct
- [ ] CI checks pass
- [ ] Ready to release

---
*Generated by `./scripts/release.py`*
"""

    result = run(
        [
            "gh",
            "pr",
            "create",
            "--title",
            pr_title,
            "--body",
            pr_body,
            "--base",
            "main",
            "--head",
            release_branch,
            "--label",
            "release",
        ],
        capture=True,
        check=False,
    )

    if result.returncode != 0:
        # Label might not exist, try without it
        print("  Note: Creating PR without 'release' label (may not exist)")
        result = run(
            [
                "gh",
                "pr",
                "create",
                "--title",
                pr_title,
                "--body",
                pr_body,
                "--base",
                "main",
                "--head",
                release_branch,
            ],
            capture=True,
        )

    pr_url = result.stdout.strip()

    print(f"\n Successfully created release PR for v{new_version}!")
    print("")
    print("   Next steps:")
    print(f"   1. Review the PR: {pr_url}")
    print("   2. Ensure CI checks pass")
    print("   3. Merge the PR")
    print("")
    print("   After merge, GitHub Actions will automatically:")
    print(f"   - Create tag {tag_name}")
    print("   - Build and publish the release")
    print("   - Deploy documentation")
    print("")
    print(f"   To cancel: git checkout main && git branch -D {release_branch}")
    print(f"             git push origin --delete {release_branch}")


if __name__ == "__main__":
    main()
