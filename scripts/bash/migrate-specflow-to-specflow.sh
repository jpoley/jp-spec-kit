#!/usr/bin/env bash
# migrate-specflow-to-specflow.sh
# Comprehensive migration script to rename /specflow to /specflow across the entire codebase
#
# This script performs:
# 1. Pre-migration validation and backup
# 2. Directory renames
# 3. File renames
# 4. Content replacements
# 5. Post-migration verification
# 6. Rollback capability if needed

set -euo pipefail

# Source common functions
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "$SCRIPT_DIR/common.sh"

REPO_ROOT=$(get_repo_root)
BACKUP_DIR="$REPO_ROOT/.migration-backup-$(date +%Y%m%d_%H%M%S)"
DRY_RUN="${DRY_RUN:-false}"
FORCE="${FORCE:-false}"
VERBOSE="${VERBOSE:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo -e "${BLUE}[VERBOSE]${NC} $*"
    fi
}

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Migrate all /specflow references to /specflow across the codebase.

OPTIONS:
    --dry-run           Show what would be changed without making changes
    --force             Skip confirmation prompts
    --verbose           Enable verbose output
    --help              Show this help message

ENVIRONMENT:
    DRY_RUN=true        Same as --dry-run
    FORCE=true          Same as --force
    VERBOSE=true        Same as --verbose

EXAMPLES:
    # Preview changes
    ./scripts/bash/migrate-specflow-to-specflow.sh --dry-run

    # Execute migration with confirmation
    ./scripts/bash/migrate-specflow-to-specflow.sh

    # Execute migration without prompts
    ./scripts/bash/migrate-specflow-to-specflow.sh --force

EXIT CODES:
    0   Success
    1   Migration failed
    2   Pre-migration validation failed
    3   User cancelled

EOF
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Pre-migration validation
validate_preconditions() {
    log_info "Running pre-migration validation..."

    # Check we're in the right directory
    if [[ ! -f "$REPO_ROOT/pyproject.toml" ]] || [[ ! -d "$REPO_ROOT/.claude" ]]; then
        log_error "Not in jp-spec-kit repository root"
        return 1
    fi

    # Check for uncommitted changes
    if [[ "$FORCE" != "true" ]] && git diff --quiet && git diff --cached --quiet; then
        : # Clean working directory
    elif [[ "$FORCE" != "true" ]]; then
        log_warn "You have uncommitted changes. This migration will modify many files."
        read -r -p "Continue anyway? (y/N) " response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            log_error "Migration cancelled by user"
            exit 3
        fi
    fi

    # Check for required tools
    local missing_tools=()
    for tool in git sed find; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        return 1
    fi

    log_success "Pre-migration validation passed"
    return 0
}

# Create backup of repository state
create_backup() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "DRY-RUN: Would create backup at $BACKUP_DIR"
        return 0
    fi

    log_info "Creating backup at $BACKUP_DIR..."
    mkdir -p "$BACKUP_DIR"

    # Backup critical files and directories
    local backup_paths=(
        "specflow_workflow.yml"
        "specflow_workflow.yml"
        "templates/commands/specflow"
        ".claude/commands/specflow"
        "memory/specflow_workflow.yml"
        "memory/specflow_workflow.schema.json"
        ".github/agents"
        "docs"
        "tests"
    )

    for path in "${backup_paths[@]}"; do
        local full_path="$REPO_ROOT/$path"
        if [[ -e "$full_path" ]]; then
            log_verbose "Backing up: $path"
            # Preserve directory structure in backup
            local backup_target="$BACKUP_DIR/$path"
            mkdir -p "$(dirname "$backup_target")"
            cp -r "$full_path" "$backup_target"
        fi
    done

    # Create git stash as additional safety measure
    if git diff --quiet && git diff --cached --quiet; then
        log_verbose "No changes to stash"
    else
        git stash push -m "Pre-migration backup $(date +%Y%m%d_%H%M%S)" || true
        log_info "Created git stash as additional backup"
    fi

    log_success "Backup created at $BACKUP_DIR"
}

# Rename directories
rename_directories() {
    log_info "Renaming directories..."

    local dir_renames=(
        "templates/commands/specflow:templates/commands/specflow"
        ".claude/commands/specflow:.claude/commands/specflow"
    )

    for rename_pair in "${dir_renames[@]}"; do
        local src="${rename_pair%%:*}"
        local dst="${rename_pair##*:}"
        local src_path="$REPO_ROOT/$src"
        local dst_path="$REPO_ROOT/$dst"

        if [[ ! -d "$src_path" ]]; then
            log_warn "Source directory not found: $src"
            continue
        fi

        if [[ -d "$dst_path" ]]; then
            log_warn "Destination already exists: $dst (skipping)"
            continue
        fi

        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "DRY-RUN: Would rename: $src -> $dst"
        else
            log_verbose "Renaming: $src -> $dst"
            mv "$src_path" "$dst_path"
            log_success "Renamed: $src -> $dst"
        fi
    done
}

# Rename individual files
rename_files() {
    log_info "Renaming files..."

    # Find all files with specflow in their name
    local files_to_rename=()
    while IFS= read -r file; do
        files_to_rename+=("$file")
    done < <(find "$REPO_ROOT" -type f -name "*specflow*" \
        ! -path "*/.git/*" \
        ! -path "*/.venv/*" \
        ! -path "*/node_modules/*" \
        ! -path "*/__pycache__/*" \
        ! -path "*/.pytest_cache/*" \
        ! -path "$BACKUP_DIR/*")

    if [[ ${#files_to_rename[@]} -eq 0 ]]; then
        log_info "No files to rename"
        return 0
    fi

    log_info "Found ${#files_to_rename[@]} files to rename"

    for file_path in "${files_to_rename[@]}"; do
        local dir=$(dirname "$file_path")
        local filename=$(basename "$file_path")
        local new_filename="${filename//specflow/specflow}"
        local new_path="$dir/$new_filename"

        if [[ "$file_path" == "$new_path" ]]; then
            continue
        fi

        if [[ -e "$new_path" ]]; then
            log_warn "Target already exists: $new_path (skipping)"
            continue
        fi

        if [[ "$DRY_RUN" == "true" ]]; then
            log_verbose "DRY-RUN: Would rename: $file_path -> $new_path"
        else
            log_verbose "Renaming: $(realpath --relative-to="$REPO_ROOT" "$file_path") -> $(basename "$new_path")"
            mv "$file_path" "$new_path"
        fi
    done

    log_success "File renaming complete"
}

# Perform content replacements
replace_content() {
    log_info "Replacing content in files..."

    # Define replacement patterns (order matters!)
    local replacements=(
        "s|/specflow:|/specflow:|g"
        "s|specflow_workflow|specflow_workflow|g"
        "s|commands/specflow/|commands/specflow/|g"
        "s|specflow-|specflow-|g"
        "s|test_specflow_|test_specflow_|g"
        "s|\.specflow\.|.specflow.|g"
    )

    # File types to process
    local file_patterns=(
        "*.md"
        "*.py"
        "*.yml"
        "*.yaml"
        "*.json"
        "*.sh"
        "*.toml"
        "*.txt"
    )

    # Build find command to match all file patterns
    local find_args=()
    for pattern in "${file_patterns[@]}"; do
        find_args+=(-name "$pattern" -o)
    done
    # Remove trailing -o
    unset 'find_args[-1]'

    # Find all matching files
    local files_to_update=()
    while IFS= read -r file; do
        files_to_update+=("$file")
    done < <(find "$REPO_ROOT" -type f \( "${find_args[@]}" \) \
        ! -path "*/.git/*" \
        ! -path "*/.venv/*" \
        ! -path "*/node_modules/*" \
        ! -path "*/__pycache__/*" \
        ! -path "*/.pytest_cache/*" \
        ! -path "$BACKUP_DIR/*")

    log_info "Found ${#files_to_update[@]} files to update"

    local updated_count=0
    for file_path in "${files_to_update[@]}"; do
        local file_changed=false

        if [[ "$DRY_RUN" == "true" ]]; then
            # Check if file would be modified
            for replacement in "${replacements[@]}"; do
                if sed -n "$replacement" "$file_path" | grep -q "specflow"; then
                    log_verbose "DRY-RUN: Would update: $(realpath --relative-to="$REPO_ROOT" "$file_path")"
                    file_changed=true
                    break
                fi
            done
        else
            # Apply all replacements in-place
            local temp_file=$(mktemp)
            cp "$file_path" "$temp_file"

            for replacement in "${replacements[@]}"; do
                sed -i "$replacement" "$file_path"
            done

            # Check if file actually changed
            if ! cmp -s "$temp_file" "$file_path"; then
                log_verbose "Updated: $(realpath --relative-to="$REPO_ROOT" "$file_path")"
                file_changed=true
            fi

            rm -f "$temp_file"
        fi

        if [[ "$file_changed" == "true" ]]; then
            ((updated_count++))
        fi
    done

    log_success "Updated $updated_count files"
}

# Verify migration results
verify_migration() {
    log_info "Verifying migration..."

    local issues=()

    # Count remaining specflow references (excluding backup and expected locations)
    local remaining_refs=$(grep -r "specflow" "$REPO_ROOT" \
        --exclude-dir=.git \
        --exclude-dir=.venv \
        --exclude-dir=node_modules \
        --exclude-dir=__pycache__ \
        --exclude-dir=.pytest_cache \
        --exclude-dir="$(basename "$BACKUP_DIR")" \
        --exclude="*.pyc" \
        2>/dev/null | wc -l)

    if [[ $remaining_refs -gt 0 ]]; then
        log_warn "Found $remaining_refs remaining 'specflow' references"
        issues+=("$remaining_refs specflow references remain")
    else
        log_success "No remaining specflow references found"
    fi

    # Verify expected directories exist
    local expected_dirs=(
        "templates/commands/specflow"
        ".claude/commands/specflow"
    )

    for dir in "${expected_dirs[@]}"; do
        if [[ ! -d "$REPO_ROOT/$dir" ]]; then
            log_warn "Expected directory not found: $dir"
            issues+=("Missing directory: $dir")
        else
            log_verbose "Verified directory exists: $dir"
        fi
    done

    # Verify expected files exist
    local expected_files=(
        "specflow_workflow.yml"
        "memory/specflow_workflow.yml"
        "memory/specflow_workflow.schema.json"
    )

    for file in "${expected_files[@]}"; do
        if [[ ! -f "$REPO_ROOT/$file" ]]; then
            log_warn "Expected file not found: $file"
            issues+=("Missing file: $file")
        else
            log_verbose "Verified file exists: $file"
        fi
    done

    # Report results
    if [[ ${#issues[@]} -eq 0 ]]; then
        log_success "Migration verification passed!"
        return 0
    else
        log_warn "Migration verification found ${#issues[@]} issue(s):"
        for issue in "${issues[@]}"; do
            log_warn "  - $issue"
        done
        return 1
    fi
}

# Generate migration summary report
generate_report() {
    log_info "Generating migration summary..."

    cat <<EOF

════════════════════════════════════════════════════════════════
                    MIGRATION SUMMARY
════════════════════════════════════════════════════════════════

Backup Location: $BACKUP_DIR

Directories Renamed:
  - templates/commands/specflow → templates/commands/specflow
  - .claude/commands/specflow → .claude/commands/specflow

Files Renamed (examples):
  - specflow_workflow.yml → specflow_workflow.yml
  - memory/specflow_workflow.yml → memory/specflow_workflow.yml
  - memory/specflow_workflow.schema.json → memory/specflow_workflow.schema.json
  - .github/agents/specflow-*.agent.md → .github/agents/specflow-*.agent.md
  - tests/test_specflow_*.py → tests/test_specflow_*.py
  - docs/*specflow* → docs/*specflow*

Content Replacements:
  - /specflow: → /specflow:
  - specflow_workflow → specflow_workflow
  - commands/specflow/ → commands/specflow/
  - specflow- → specflow-
  - test_specflow_ → test_specflow_

Next Steps:
  1. Review changes: git status
  2. Run tests: pytest tests/
  3. Verify CI: ./scripts/bash/run-local-ci.sh
  4. Update documentation site build
  5. Commit changes: git add -A && git commit -m "Rename /specflow to /specflow"

Rollback Instructions (if needed):
  1. Restore from backup: cp -r $BACKUP_DIR/* .
  2. Or use git: git restore . && git clean -fd
  3. Or restore git stash: git stash pop

════════════════════════════════════════════════════════════════

EOF
}

# Rollback function
rollback() {
    log_warn "Rolling back migration..."

    if [[ ! -d "$BACKUP_DIR" ]]; then
        log_error "Backup directory not found: $BACKUP_DIR"
        return 1
    fi

    # Restore from backup
    cp -r "$BACKUP_DIR"/* "$REPO_ROOT/"
    log_success "Restored from backup"

    # Clean up any new files created
    if git diff --name-only | grep -q "specflow"; then
        log_info "Removing new specflow files..."
        git restore .
        git clean -fd
    fi

    log_success "Rollback complete"
}

# Main execution
main() {
    log_info "Starting specflow → specflow migration"
    log_info "Repository: $REPO_ROOT"
    log_info "Mode: $([ "$DRY_RUN" == "true" ] && echo "DRY-RUN" || echo "EXECUTE")"

    # Validate preconditions
    if ! validate_preconditions; then
        log_error "Pre-migration validation failed"
        exit 2
    fi

    # Confirmation prompt (unless --force)
    if [[ "$DRY_RUN" != "true" ]] && [[ "$FORCE" != "true" ]]; then
        echo
        log_warn "This will rename directories, files, and modify content across the entire codebase."
        log_warn "A backup will be created at: $BACKUP_DIR"
        read -r -p "Continue with migration? (y/N) " response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            log_error "Migration cancelled by user"
            exit 3
        fi
    fi

    # Create backup
    create_backup

    # Perform migration steps
    rename_directories
    rename_files
    replace_content

    # Verify results
    if [[ "$DRY_RUN" != "true" ]]; then
        if ! verify_migration; then
            log_warn "Migration completed with warnings"
        fi
    fi

    # Generate report
    generate_report

    log_success "Migration complete!"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "This was a dry-run. No changes were made."
        log_info "Run without --dry-run to execute the migration."
    fi
}

# Trap errors and provide rollback option
trap 'log_error "Migration failed! Run with --help for rollback instructions."; exit 1' ERR

main "$@"
