#!/usr/bin/env bash
# Migrate slash commands from flat structure to subdirectory structure
# This script moves flowspec.*.md and spec.*.md files to their respective subdirectories
#
# Usage: ./scripts/bash/migrate-commands-to-subdirs.sh [--dry-run] [--path <directory>]
#
# Options:
#   --dry-run     Show what would be moved without actually moving
#   --path <dir>  Target directory (default: .claude/commands or templates/commands)
#   --help        Show this help message

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DRY_RUN=false
TARGET_PATH=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Migrate slash commands from flat structure to subdirectory structure.

This script moves:
  - flowspec.*.md files to flowspec/ subdirectory (renamed to *.md)
  - spec.*.md files to spec/ subdirectory (renamed to *.md)

OPTIONS:
  --dry-run         Show what would be moved without actually moving
  --path <dir>      Target directory containing the command files
                    Default: tries .claude/commands then templates/commands
  --help, -h        Show this help message

EXAMPLES:
  # Preview changes
  $(basename "$0") --dry-run

  # Migrate commands in .claude/commands/
  $(basename "$0") --path .claude/commands

  # Migrate template commands
  $(basename "$0") --path templates/commands

EXIT CODES:
  0  Success (files migrated or nothing to migrate)
  1  Error during migration
  2  Invalid arguments or target path not found

EOF
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --path)
                if [[ -z "${2:-}" ]]; then
                    log_error "--path requires an argument"
                    exit 2
                fi
                TARGET_PATH="$2"
                shift 2
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 2
                ;;
        esac
    done
}

# Find target directory
find_target_dir() {
    if [[ -n "$TARGET_PATH" ]]; then
        if [[ "$TARGET_PATH" = /* ]]; then
            echo "$TARGET_PATH"
        else
            echo "$REPO_ROOT/$TARGET_PATH"
        fi
        return
    fi

    # Try common locations
    local candidates=(
        "$REPO_ROOT/.claude/commands"
        "$REPO_ROOT/templates/commands"
    )

    for candidate in "${candidates[@]}"; do
        if [[ -d "$candidate" ]]; then
            # Check if it has files to migrate
            if ls "$candidate"/flowspec.*.md "$candidate"/spec.*.md 2>/dev/null | head -1 | grep -q .; then
                echo "$candidate"
                return
            fi
        fi
    done

    # Return first existing directory even if no files to migrate
    for candidate in "${candidates[@]}"; do
        if [[ -d "$candidate" ]]; then
            echo "$candidate"
            return
        fi
    done

    echo ""
}

# Migrate files for a specific prefix (flowspec or spec)
migrate_prefix() {
    local target_dir="$1"
    local prefix="$2"
    local subdir="$target_dir/$prefix"
    local count=0

    # Find all files matching prefix.*.md pattern
    local files=()
    while IFS= read -r -d '' file; do
        files+=("$file")
    done < <(find "$target_dir" -maxdepth 1 -name "${prefix}.*.md" -type f -print0 2>/dev/null || true)

    if [[ ${#files[@]} -eq 0 ]]; then
        log_info "No ${prefix}.*.md files found in flat structure"
        return 0
    fi

    log_info "Found ${#files[@]} ${prefix}.*.md files to migrate"

    # Create subdirectory if needed
    if [[ ! -d "$subdir" ]]; then
        if $DRY_RUN; then
            log_info "Would create directory: $subdir"
        else
            mkdir -p "$subdir"
            log_success "Created directory: $subdir"
        fi
    fi

    # Move each file
    for file in "${files[@]}"; do
        local basename=$(basename "$file")
        # Transform: flowspec.implement.md -> implement.md
        local new_name="${basename#${prefix}.}"
        local new_path="$subdir/$new_name"

        if [[ -e "$new_path" ]]; then
            log_warning "Skipping $basename - target already exists: $new_path"
            continue
        fi

        if $DRY_RUN; then
            echo "  Would move: $basename -> $prefix/$new_name"
        else
            mv "$file" "$new_path"
            echo "  Moved: $basename -> $prefix/$new_name"
            count=$((count + 1))
        fi
    done

    if ! $DRY_RUN && [[ $count -gt 0 ]]; then
        log_success "Migrated $count ${prefix} files"
    fi

    return 0
}

# Check for symlinks that need updating
check_symlinks() {
    local target_dir="$1"
    local broken_count=0

    log_info "Checking for symlinks that may need updating..."

    while IFS= read -r -d '' link; do
        local target=$(readlink "$link")
        if [[ ! -e "$link" ]]; then
            log_warning "Broken symlink: $(basename "$link") -> $target"
            broken_count=$((broken_count + 1))
        fi
    done < <(find "$target_dir" -type l -print0 2>/dev/null || true)

    if [[ $broken_count -gt 0 ]]; then
        echo ""
        log_warning "$broken_count broken symlinks found"
        log_info "If this is .claude/commands/, run 'flowspec dev-setup --force' to recreate symlinks"
    fi
}

main() {
    parse_args "$@"

    echo "=========================================="
    echo "Command Migration: Flat -> Subdirectory"
    echo "=========================================="
    echo ""

    local target_dir=$(find_target_dir)

    if [[ -z "$target_dir" ]]; then
        log_error "No target directory found. Use --path to specify."
        exit 2
    fi

    if [[ ! -d "$target_dir" ]]; then
        log_error "Target directory does not exist: $target_dir"
        exit 2
    fi

    log_info "Target directory: $target_dir"

    if $DRY_RUN; then
        echo ""
        log_warning "DRY RUN MODE - no files will be moved"
    fi

    echo ""

    # Migrate flowspec files
    migrate_prefix "$target_dir" "flowspec"
    echo ""

    # Migrate spec files
    migrate_prefix "$target_dir" "spec"
    echo ""

    # Check for broken symlinks
    check_symlinks "$target_dir"
    echo ""

    if $DRY_RUN; then
        log_info "Dry run complete. Run without --dry-run to apply changes."
    else
        log_success "Migration complete!"
        echo ""
        log_info "Next steps:"
        echo "  1. Review the changes: git status"
        echo "  2. If migrating .claude/commands/, run: flowspec dev-setup --force"
        echo "  3. Commit the changes: git add -A && git commit -m 'Migrate commands to subdirectories'"
    fi
}

main "$@"
