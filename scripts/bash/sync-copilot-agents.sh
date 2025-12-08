#!/usr/bin/env bash
# sync-copilot-agents.sh - Convert Claude Code commands to VS Code Copilot agents
#
# This script synchronizes .claude/commands/ to .github/agents/ by:
# - Resolving {{INCLUDE:path}} directives
# - Transforming frontmatter to Copilot format (name, description, tools, handoffs)
# - Renaming files to .agent.md extension
#
# Usage:
#   sync-copilot-agents.sh [OPTIONS]
#
# Options:
#   --dry-run     Show what would be generated without writing
#   --validate    Check if .github/agents/ matches expected output (exit 2 if drift)
#   --force       Overwrite files without confirmation
#   --verbose     Show detailed processing information
#   --help        Show usage

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMMANDS_DIR="$PROJECT_ROOT/.claude/commands"
AGENTS_DIR="$PROJECT_ROOT/.github/agents"
MAX_INCLUDE_DEPTH=3

# Flags
DRY_RUN=false
VALIDATE=false
FORCE=false
VERBOSE=false

# Counters
TOTAL_FILES=0
PROCESSED_FILES=0
ERRORS=0

# Colors (disabled on non-tty)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Print functions
log_info() { echo -e "${BLUE}INFO:${NC} $*"; }
log_success() { echo -e "${GREEN}OK:${NC} $*"; }
log_warn() { echo -e "${YELLOW}WARN:${NC} $*"; }
log_error() { echo -e "${RED}ERROR:${NC} $*" >&2; }
log_verbose() { [[ "$VERBOSE" == true ]] && echo -e "${BLUE}VERBOSE:${NC} $*" || true; }

usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Convert Claude Code commands to VS Code Copilot agents.

Options:
  --dry-run     Show what would be generated without writing
  --validate    Check if .github/agents/ matches expected output (exit 2 if drift)
  --force       Overwrite files without confirmation
  --verbose     Show detailed processing information
  --help        Show this help message

Source: .claude/commands/{jpspec,speckit}/*.md
Target: .github/agents/{namespace}-{command}.agent.md

Examples:
  $(basename "$0")              # Sync all commands
  $(basename "$0") --dry-run    # Preview changes
  $(basename "$0") --validate   # CI mode: check for drift
EOF
}

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --validate)
                VALIDATE=true
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
            --help|-h)
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
}

# Resolve {{INCLUDE:path}} directives recursively using Python for reliability
# Note: Depth tracking is handled internally by the Python script (max_depth=10)
resolve_includes() {
    local input_file="$1"

    PROJECT_ROOT="$PROJECT_ROOT" INPUT_FILE="$input_file" python3 << 'PYTHON_SCRIPT'
import re
import sys
from pathlib import Path

def resolve_includes(content, project_root, depth=0, max_depth=10):
    """Resolve {{INCLUDE:path}} directives, skipping those inside code blocks."""
    if depth > max_depth:
        raise ValueError(f"Max include depth ({max_depth}) exceeded")

    include_pattern = r'\{\{INCLUDE:([^}]+)\}\}'

    # Process line by line, tracking code block state
    lines = content.split('\n')
    result_lines = []
    in_code_block = False
    code_fence = None
    nested_fence_count = 0  # Track nested fences inside code blocks

    for line in lines:
        # Check for code fence (``` with optional language)
        fence_match = re.match(r'^(\s*)(```+)(\w*)?$', line.rstrip())
        if fence_match:
            fence = fence_match.group(2)
            info_string = fence_match.group(3) or ''
            if not in_code_block:
                # Opening fence can have an info string
                in_code_block = True
                code_fence = fence
                nested_fence_count = 0
            elif info_string:
                # Opening fence inside code block (has info string)
                nested_fence_count += 1
            elif nested_fence_count > 0:
                # Closing fence for a nested fence inside code block
                nested_fence_count -= 1
            elif len(fence) >= len(code_fence):
                # Closing fence for the outer block
                in_code_block = False
                code_fence = None
            result_lines.append(line)
            continue

        if in_code_block:
            # Don't process includes in code blocks
            result_lines.append(line)
        else:
            # Process includes outside code blocks
            def replace_include(match):
                include_path = match.group(1)
                resolved_path = project_root / include_path
                if not resolved_path.exists():
                    raise FileNotFoundError(f"Include not found: {include_path}")
                included_content = resolved_path.read_text()
                # Recursively resolve includes in the included content
                return resolve_includes(included_content, project_root, depth + 1, max_depth)

            processed_line = re.sub(include_pattern, replace_include, line)
            result_lines.append(processed_line)

    return '\n'.join(result_lines)

try:
    import os
    project_root = Path(os.environ.get('PROJECT_ROOT', '.'))
    input_file = Path(os.environ.get('INPUT_FILE', ''))

    # Follow symlink if needed
    if input_file.is_symlink():
        input_file = input_file.resolve()

    content = input_file.read_text()
    resolved = resolve_includes(content, project_root, 0, 10)
    print(resolved, end='')
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_SCRIPT
}

# Extract frontmatter description using Python for reliability
extract_description() {
    local content="$1"

    python3 -c '
import re
import sys

content = sys.stdin.read()

# Try to extract from YAML frontmatter
match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
if match:
    frontmatter = match.group(1)
    desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if desc_match:
        print(desc_match.group(1).strip())
        sys.exit(0)

# No description found
print("")
' <<< "$content"
}

# Get handoff configuration for an agent
get_handoffs() {
    local namespace="$1"
    local command="$2"

    # Only jpspec workflow commands have handoffs
    if [[ "$namespace" != "jpspec" ]]; then
        echo ""
        return
    fi

    case "$command" in
        assess)
            cat << 'HANDOFF'
handoffs:
  - label: "Specify Requirements"
    agent: "jpspec-specify"
    prompt: "The assessment is complete. Based on the assessment, create detailed product requirements."
    send: false
HANDOFF
            ;;
        specify)
            cat << 'HANDOFF'
handoffs:
  - label: "Conduct Research"
    agent: "jpspec-research"
    prompt: "The specification is complete. Conduct research to validate technical feasibility and market fit."
    send: false
  - label: "Create Technical Design"
    agent: "jpspec-plan"
    prompt: "The specification is complete. Create the technical architecture and platform design."
    send: false
HANDOFF
            ;;
        research)
            cat << 'HANDOFF'
handoffs:
  - label: "Create Technical Design"
    agent: "jpspec-plan"
    prompt: "Research is complete. Create the technical architecture and platform design based on findings."
    send: false
HANDOFF
            ;;
        plan)
            cat << 'HANDOFF'
handoffs:
  - label: "Begin Implementation"
    agent: "jpspec-implement"
    prompt: "Planning is complete. Begin implementing the feature according to the technical design."
    send: false
HANDOFF
            ;;
        implement)
            cat << 'HANDOFF'
handoffs:
  - label: "Run Validation"
    agent: "jpspec-validate"
    prompt: "Implementation is complete. Run QA validation, security review, and documentation checks."
    send: false
HANDOFF
            ;;
        validate)
            cat << 'HANDOFF'
handoffs:
  - label: "Deploy to Production"
    agent: "jpspec-operate"
    prompt: "Validation is complete. Deploy the feature to production and configure operations."
    send: false
HANDOFF
            ;;
        operate|init|reset|prune-branch|security_*)
            # Terminal or utility commands - no handoffs
            echo ""
            ;;
        *)
            echo ""
            ;;
    esac
}

# Get tools configuration for an agent
get_tools() {
    local namespace="$1"

    if [[ "$namespace" == "jpspec" ]]; then
        # Full workflow tools
        cat << 'TOOLS'
tools:
  - "Read"
  - "Write"
  - "Edit"
  - "Grep"
  - "Glob"
  - "Bash"
  - "mcp__backlog__*"
  - "mcp__serena__*"
  - "Skill"
TOOLS
    else
        # Utility tools (speckit)
        cat << 'TOOLS'
tools:
  - "Read"
  - "Write"
  - "Grep"
  - "Glob"
  - "mcp__backlog__*"
TOOLS
    fi
}

# Generate Copilot agent frontmatter
generate_frontmatter() {
    local namespace="$1"
    local command="$2"
    local description="$3"

    local name="${namespace}-${command}"
    local handoffs
    local tools

    handoffs=$(get_handoffs "$namespace" "$command")
    tools=$(get_tools "$namespace")

    echo "---"
    echo "name: \"$name\""
    echo "description: \"$description\""
    echo "target: \"chat\""
    echo "$tools"
    if [[ -n "$handoffs" ]]; then
        echo "$handoffs"
    fi
    echo "---"
}

# Process a single command file
process_command() {
    local source_file="$1"
    local namespace="$2"

    # Get command name (filename without .md)
    local command
    command=$(basename "$source_file" .md)

    # Skip partials (files starting with _)
    if [[ "$command" == _* ]]; then
        log_verbose "Skipping partial: $command"
        return 0
    fi

    log_verbose "Processing: $namespace/$command"

    # Resolve includes and get content
    local resolved_content
    if ! resolved_content=$(resolve_includes "$source_file" 2>&1); then
        log_error "Failed to resolve includes for $namespace/$command: $resolved_content"
        ((ERRORS++))
        return 1
    fi

    # Note: Includes inside code blocks are intentionally preserved
    # The Python resolve_includes() function only processes includes outside code blocks
    # If an include outside a code block couldn't be resolved, Python would have errored

    # Extract description from original frontmatter
    local description
    description=$(extract_description "$resolved_content")
    if [[ -z "$description" ]]; then
        description="$namespace $command workflow command"
        log_warn "No description found for $namespace/$command, using default"
    fi

    # Remove original frontmatter and get body
    local body
    body=$(echo "$resolved_content" | python3 -c "
import sys
import re
content = sys.stdin.read()
# Remove YAML frontmatter
body = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, count=1, flags=re.DOTALL)
print(body, end='')
")

    # Generate new frontmatter
    local new_frontmatter
    new_frontmatter=$(generate_frontmatter "$namespace" "$command" "$description")

    # Combine frontmatter and body
    local output="${new_frontmatter}
${body}"

    # Output file path
    local output_file="$AGENTS_DIR/${namespace}-${command}.agent.md"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY-RUN] Would create: ${namespace}-${command}.agent.md"
        if [[ "$VERBOSE" == true ]]; then
            echo "--- Frontmatter Preview ---"
            echo "$new_frontmatter"
            echo "--- End Preview ---"
        fi
    elif [[ "$VALIDATE" == true ]]; then
        # Compare with existing file
        if [[ -f "$output_file" ]]; then
            local existing
            existing=$(cat "$output_file")
            if [[ "$existing" != "$output" ]]; then
                log_error "Drift detected: ${namespace}-${command}.agent.md"
                ((ERRORS++))
                return 1
            fi
            log_verbose "Validated: ${namespace}-${command}.agent.md"
        else
            log_error "Missing: ${namespace}-${command}.agent.md"
            ((ERRORS++))
            return 1
        fi
    else
        # Write output
        mkdir -p "$(dirname "$output_file")"
        echo "$output" > "$output_file"
        log_success "Created: ${namespace}-${command}.agent.md"
    fi

    ((PROCESSED_FILES++))
}

# Process all commands in a namespace
process_namespace() {
    local namespace="$1"
    local namespace_dir="$COMMANDS_DIR/$namespace"

    if [[ ! -d "$namespace_dir" ]]; then
        log_warn "Namespace directory not found: $namespace"
        return 0
    fi

    log_info "Processing namespace: $namespace"

    # Enable nullglob so empty globs expand to nothing instead of literal pattern
    local old_nullglob
    old_nullglob=$(shopt -p nullglob || true)
    shopt -s nullglob

    for file in "$namespace_dir"/*.md; do
        if [[ -f "$file" || -L "$file" ]]; then
            ((TOTAL_FILES++))
            process_command "$file" "$namespace" || true
        fi
    done

    # Restore previous nullglob setting
    $old_nullglob 2>/dev/null || true
}

# Remove stale agent files (old format)
cleanup_stale() {
    if [[ "$DRY_RUN" == true || "$VALIDATE" == true ]]; then
        return 0
    fi

    log_info "Checking for stale agent files..."

    # Remove old-format files (jpspec.*.md and speckit.*.md)
    for old_file in "$AGENTS_DIR"/jpspec.*.md "$AGENTS_DIR"/speckit.*.md; do
        if [[ -f "$old_file" ]]; then
            if [[ "$FORCE" == true ]]; then
                rm "$old_file"
                log_warn "Removed old format: $(basename "$old_file")"
            else
                log_warn "Stale file (old format): $(basename "$old_file") (use --force to remove)"
            fi
        fi
    done

    # Check for agent files without sources
    for agent_file in "$AGENTS_DIR"/*.agent.md; do
        if [[ ! -f "$agent_file" ]]; then
            continue
        fi

        local basename
        basename=$(basename "$agent_file" .agent.md)

        # Parse namespace and command from filename
        local namespace command
        if [[ "$basename" =~ ^(jpspec|speckit)-(.+)$ ]]; then
            namespace="${BASH_REMATCH[1]}"
            command="${BASH_REMATCH[2]}"
        else
            # Unknown format, skip
            continue
        fi

        # Check if source exists
        local source_file="$COMMANDS_DIR/$namespace/$command.md"
        if [[ ! -f "$source_file" && ! -L "$source_file" ]]; then
            if [[ "$FORCE" == true ]]; then
                rm "$agent_file"
                log_warn "Removed stale: $basename.agent.md"
            else
                log_warn "Stale file detected: $basename.agent.md (use --force to remove)"
            fi
        fi
    done
}

# Main execution
main() {
    parse_args "$@"

    local start_time
    start_time=$(python3 -c "import time; print(int(time.time() * 1000))")

    log_info "Syncing Claude Code commands to VS Code Copilot agents"
    log_info "Source: $COMMANDS_DIR"
    log_info "Target: $AGENTS_DIR"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "Mode: DRY-RUN (no files will be written)"
    elif [[ "$VALIDATE" == true ]]; then
        log_info "Mode: VALIDATE (checking for drift)"
    else
        log_info "Mode: SYNC"
    fi

    # Ensure agents directory exists
    if [[ "$DRY_RUN" != true && "$VALIDATE" != true ]]; then
        mkdir -p "$AGENTS_DIR"
    fi

    # Process namespaces
    process_namespace "jpspec"
    process_namespace "speckit"

    # Cleanup stale files
    cleanup_stale

    # Calculate duration
    local end_time duration_ms
    end_time=$(python3 -c "import time; print(int(time.time() * 1000))")
    duration_ms=$((end_time - start_time))

    # Summary
    echo ""
    log_info "Summary:"
    log_info "  Total files scanned: $TOTAL_FILES"
    log_info "  Files processed: $PROCESSED_FILES"
    log_info "  Errors: $ERRORS"
    log_info "  Duration: ${duration_ms}ms"

    if [[ $ERRORS -gt 0 ]]; then
        if [[ "$VALIDATE" == true ]]; then
            log_error "Validation failed: drift detected"
            exit 2
        else
            log_error "Sync completed with errors"
            exit 1
        fi
    fi

    if [[ "$VALIDATE" == true ]]; then
        log_success "Validation passed: no drift detected"
    elif [[ "$DRY_RUN" == true ]]; then
        log_success "Dry-run complete"
    else
        log_success "Sync complete"
    fi
}

main "$@"
