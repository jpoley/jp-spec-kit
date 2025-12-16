#!/usr/bin/env bash
# sync-copilot-agents.sh - Convert Claude Code commands to VS Code Copilot agents
#
# This script synchronizes .claude/commands/ and templates/commands/ to .github/agents/ by:
# - Resolving {{INCLUDE:path}} directives
# - Transforming frontmatter to Copilot format (name, description, tools, handoffs)
# - Adding role metadata from flowspec_workflow.yml
# - Supporting role-based filtering (--role dev, --role qa, etc.)
# - Renaming files to {role}-{command}.agent.md or {namespace}-{command}.agent.md
#
# Usage:
#   sync-copilot-agents.sh [OPTIONS]
#
# Options:
#   --dry-run           Show what would be generated without writing
#   --validate          Check if .github/agents/ matches expected output (exit 2 if drift)
#   --force             Overwrite files without confirmation
#   --verbose           Show detailed processing information
#   --role ROLE         Generate only agents for specified role (dev, pm, qa, sec, arch, ops, all)
#   --with-vscode       Generate .vscode/settings.json with agent pinning
#   --help              Show usage

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMMANDS_DIR="$PROJECT_ROOT/.claude/commands"
TEMPLATES_COMMANDS_DIR="$PROJECT_ROOT/templates/commands"
AGENTS_DIR="$PROJECT_ROOT/.github/agents"
WORKFLOW_CONFIG="$PROJECT_ROOT/flowspec_workflow.yml"

# Force UTF-8 encoding for Python (Windows compatibility)
# Windows uses charmap/cp1252 by default which can't handle Unicode like ✓, →, ❌
export PYTHONIOENCODING=utf-8

# Determine Python command - prefer uv venv if available (for CI compatibility)
# This handles CI environments where yaml is only in the uv-managed venv
if [[ -f "$PROJECT_ROOT/.venv/bin/python" ]]; then
    PYTHON_CMD="$PROJECT_ROOT/.venv/bin/python"
elif command -v uv &> /dev/null && [[ -f "$PROJECT_ROOT/pyproject.toml" ]]; then
    PYTHON_CMD="uv run python"
else
    PYTHON_CMD="python3"
fi

# Flags
DRY_RUN=false
VALIDATE=false
FORCE=false
VERBOSE=false
ROLE_FILTER=""
WITH_VSCODE=false

# Counters
TOTAL_FILES=0
PROCESSED_FILES=0
ERRORS=0

# Cache for role metadata (using temp files for bash 3.2 compatibility - no associative arrays)
ROLE_METADATA_DIR=""
ROLE_METADATA_LOADED=false

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

Convert Claude Code commands to VS Code Copilot agents with role-based metadata.

Options:
  --dry-run           Show what would be generated without writing
  --validate          Check if .github/agents/ matches expected output (exit 2 if drift)
  --force             Overwrite files without confirmation
  --verbose           Show detailed processing information
  --role ROLE         Generate only agents for specified role (dev, pm, qa, sec, arch, ops, all)
  --with-vscode       Generate .vscode/settings.json with agent pinning
  --help              Show this help message

Source:
  - .claude/commands/{flow,spec}/*.md (legacy workflow commands)
  - templates/commands/{role}/*.md (role-based commands)
Target: .github/agents/{role}-{command}.agent.md or {namespace}-{command}.agent.md

Role Configuration: flowspec_workflow.yml

Examples:
  $(basename "$0")                    # Sync all commands
  $(basename "$0") --dry-run          # Preview changes
  $(basename "$0") --validate         # CI mode: check for drift
  $(basename "$0") --role dev         # Generate only dev role agents
  $(basename "$0") --with-vscode      # Generate with VS Code settings
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
            --role)
                if [[ -z "${2:-}" ]]; then
                    log_error "--role requires a role name argument"
                    exit 1
                fi
                ROLE_FILTER="$2"
                shift 2
                ;;
            --with-vscode)
                WITH_VSCODE=true
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

# Load role metadata from flowspec_workflow.yml
# Uses temp files for bash 3.2 compatibility (macOS) instead of associative arrays
get_role_metadata() {
    if [[ "$ROLE_METADATA_LOADED" == true ]]; then
        return 0
    fi

    # Create temp directory for metadata files
    ROLE_METADATA_DIR=$(mktemp -d)
    mkdir -p "$ROLE_METADATA_DIR/command_roles"
    mkdir -p "$ROLE_METADATA_DIR/agent_roles"
    mkdir -p "$ROLE_METADATA_DIR/role_agents"

    if [[ ! -f "$WORKFLOW_CONFIG" ]]; then
        log_warn "Workflow config not found: $WORKFLOW_CONFIG"
        ROLE_METADATA_LOADED=true
        return 0
    fi

    log_verbose "Loading role metadata from $WORKFLOW_CONFIG"

    # Use Python to parse YAML and process metadata
    # Explicit UTF-8 encoding for Windows compatibility
    local metadata_output
    if ! metadata_output=$(WORKFLOW_CONFIG="$WORKFLOW_CONFIG" $PYTHON_CMD << 'PYTHON_METADATA'
import yaml
import sys
import os
from pathlib import Path

try:
    config_path = Path(os.environ.get('WORKFLOW_CONFIG', ''))
    # Explicit UTF-8 encoding for Windows compatibility
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    roles = config.get('roles', {}).get('definitions', {})

    # Print role -> commands mapping
    for role, role_data in roles.items():
        commands = role_data.get('commands', [])
        for cmd in commands:
            print(f"COMMAND_ROLE:{cmd}:{role}")

    # Print role -> agents mapping
    for role, role_data in roles.items():
        agents = role_data.get('agents', [])
        for agent in agents:
            # Remove @ prefix if present
            agent_name = agent.lstrip('@')
            print(f"ROLE_AGENT:{role}:{agent_name}")
            print(f"AGENT_ROLE:{agent_name}:{role}")

except FileNotFoundError:
    print(f"ERROR: Config file not found", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Failed to parse YAML: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON_METADATA
2>&1); then
        log_error "Failed to load role metadata: $metadata_output"
        ROLE_METADATA_LOADED=true
        return 1
    fi

    # Parse metadata and store in temp files
    local cmd_count=0
    local agent_count=0
    while IFS=: read -r type key value; do
        case "$type" in
            COMMAND_ROLE)
                echo "$value" > "$ROLE_METADATA_DIR/command_roles/$key"
                cmd_count=$((cmd_count + 1))
                log_verbose "Command '$key' -> role '$value'"
                ;;
            ROLE_AGENT)
                echo "$value" >> "$ROLE_METADATA_DIR/role_agents/$key"
                log_verbose "Role '$key' -> agent '$value'"
                ;;
            AGENT_ROLE)
                echo "$value" > "$ROLE_METADATA_DIR/agent_roles/$key"
                agent_count=$((agent_count + 1))
                log_verbose "Agent '$key' -> role '$value'"
                ;;
        esac
    done <<< "$metadata_output"

    ROLE_METADATA_LOADED=true
    log_verbose "Role metadata loaded: $cmd_count commands, $agent_count agents"
}

# Get role for a command (reads from temp file)
get_command_role() {
    local command="$1"
    local file="$ROLE_METADATA_DIR/command_roles/$command"
    if [[ -f "$file" ]]; then
        cat "$file"
    fi
}

# Get role for an agent (reads from temp file)
get_agent_role() {
    local agent="$1"
    local file="$ROLE_METADATA_DIR/agent_roles/$agent"
    if [[ -f "$file" ]]; then
        cat "$file"
    fi
}

# Cleanup temp files on exit
cleanup_metadata() {
    if [[ -n "$ROLE_METADATA_DIR" && -d "$ROLE_METADATA_DIR" ]]; then
        rm -rf "$ROLE_METADATA_DIR"
    fi
}
trap cleanup_metadata EXIT

# Check if command should be processed based on role filter
should_process_command() {
    local role="$1"

    # No filter = process all
    if [[ -z "$ROLE_FILTER" ]]; then
        return 0
    fi

    # "all" filter = process all
    if [[ "$ROLE_FILTER" == "all" ]]; then
        return 0
    fi

    # Check if role matches filter
    if [[ "$role" == "$ROLE_FILTER" ]]; then
        return 0
    fi

    return 1
}

# Resolve {{INCLUDE:path}} directives recursively using Python for reliability
# Include resolution uses max_depth=10 to prevent circular reference issues
# Code block detection handles nested fences: inner fences with info strings are
# tracked separately to correctly identify the outer block's closing fence
resolve_includes() {
    local input_file="$1"

    PROJECT_ROOT="$PROJECT_ROOT" INPUT_FILE="$input_file" $PYTHON_CMD << 'PYTHON_SCRIPT'
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
        # Check for code fence (``` with optional language/info string)
        # Use (.*) to match any info string including hyphens (e.g., python-repl, c++)
        fence_match = re.match(r'^(\s*)(```+)(.*)$', line.rstrip())
        if fence_match:
            fence = fence_match.group(2)
            info_string = (fence_match.group(3) or '').strip()
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
                # Security: reject absolute paths and path traversal attempts
                # Use Path.parts to check for '..' as a path component (not substring)
                # This allows valid filenames like 'file..md' while blocking '../etc/passwd'
                path_parts = Path(include_path).parts
                if include_path.startswith('/') or '..' in path_parts:
                    raise ValueError(f"Invalid include path (security): {include_path}")
                resolved_path = (project_root / include_path).resolve()
                # Verify resolved path is within project root using path-aware check
                # This prevents prefix attacks (e.g., /proj vs /proj-secret)
                pr = project_root.resolve()
                try:
                    # Python 3.9+ has is_relative_to()
                    if not resolved_path.is_relative_to(pr):
                        raise ValueError(f"Include path escapes project root: {include_path}")
                except AttributeError:
                    # Fallback for Python <3.9: check if project_root is in parents
                    if pr != resolved_path and pr not in resolved_path.parents:
                        raise ValueError(f"Include path escapes project root: {include_path}")
                if not resolved_path.exists():
                    raise FileNotFoundError(f"Include not found: {include_path}")
                # Explicit UTF-8 encoding for Windows compatibility
                included_content = resolved_path.read_text(encoding='utf-8')
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

    # Explicit UTF-8 encoding for Windows compatibility
    content = input_file.read_text(encoding='utf-8')
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

    $PYTHON_CMD -c '
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
    local role="$1"
    local command="$2"

    # Role-based commands use role-specific handoffs
    if [[ -n "$role" && "$role" != "flow" && "$role" != "spec" ]]; then
        # Get next logical command in same role
        case "$role" in
            pm)
                case "$command" in
                    assess)
                        cat << 'HANDOFF'
handoffs:
  - label: "Define Requirements"
    agent: "pm-define"
    prompt: "Assessment complete. Define detailed product requirements."
    send: false
    priority_for_roles: ["pm"]
HANDOFF
                        ;;
                    define)
                        cat << 'HANDOFF'
handoffs:
  - label: "Research and Discover"
    agent: "pm-discover"
    prompt: "Requirements defined. Conduct research and discovery."
    send: false
    priority_for_roles: ["pm"]
  - label: "Create Technical Design"
    agent: "arch-design"
    prompt: "Requirements ready. Hand off to architect for technical design."
    send: false
    priority_for_roles: ["arch"]
HANDOFF
                        ;;
                    discover)
                        cat << 'HANDOFF'
handoffs:
  - label: "Create Technical Design"
    agent: "arch-design"
    prompt: "Discovery complete. Hand off to architect for technical design."
    send: false
    priority_for_roles: ["arch"]
HANDOFF
                        ;;
                esac
                ;;
            arch)
                case "$command" in
                    design)
                        cat << 'HANDOFF'
handoffs:
  - label: "Begin Implementation"
    agent: "dev-build"
    prompt: "Design complete. Hand off to developers for implementation."
    send: false
    priority_for_roles: ["dev"]
HANDOFF
                        ;;
                esac
                ;;
            dev)
                case "$command" in
                    build)
                        cat << 'HANDOFF'
handoffs:
  - label: "Run Tests"
    agent: "qa-test"
    prompt: "Implementation complete. Hand off to QA for testing."
    send: false
    priority_for_roles: ["qa"]
HANDOFF
                        ;;
                esac
                ;;
            qa)
                case "$command" in
                    test)
                        cat << 'HANDOFF'
handoffs:
  - label: "Security Scan"
    agent: "sec-scan"
    prompt: "Tests passing. Hand off to security for scanning."
    send: false
    priority_for_roles: ["sec"]
  - label: "Deploy"
    agent: "ops-deploy"
    prompt: "Tests passing. Hand off to ops for deployment."
    send: false
    priority_for_roles: ["ops"]
HANDOFF
                        ;;
                    verify)
                        cat << 'HANDOFF'
handoffs:
  - label: "Deploy"
    agent: "ops-deploy"
    prompt: "Verification complete. Hand off to ops for deployment."
    send: false
    priority_for_roles: ["ops"]
HANDOFF
                        ;;
                esac
                ;;
            sec)
                case "$command" in
                    scan)
                        cat << 'HANDOFF'
handoffs:
  - label: "Triage Findings"
    agent: "sec-triage"
    prompt: "Scan complete. Triage security findings."
    send: false
    priority_for_roles: ["sec"]
HANDOFF
                        ;;
                    triage)
                        cat << 'HANDOFF'
handoffs:
  - label: "Fix Vulnerabilities"
    agent: "sec-fix"
    prompt: "Triage complete. Fix critical vulnerabilities."
    send: false
    priority_for_roles: ["sec", "dev"]
HANDOFF
                        ;;
                    fix)
                        cat << 'HANDOFF'
handoffs:
  - label: "Re-scan"
    agent: "sec-scan"
    prompt: "Fixes applied. Re-scan to verify."
    send: false
    priority_for_roles: ["sec"]
HANDOFF
                        ;;
                esac
                ;;
            ops)
                case "$command" in
                    deploy)
                        cat << 'HANDOFF'
handoffs:
  - label: "Monitor"
    agent: "ops-monitor"
    prompt: "Deployment complete. Monitor system health."
    send: false
    priority_for_roles: ["ops"]
HANDOFF
                        ;;
                    monitor)
                        cat << 'HANDOFF'
handoffs:
  - label: "Respond to Incident"
    agent: "ops-respond"
    prompt: "Issue detected. Respond to incident."
    send: false
    priority_for_roles: ["ops"]
HANDOFF
                        ;;
                esac
                ;;
        esac
        return
    fi

    # Legacy flow workflow commands
    if [[ "$role" != "flow" ]]; then
        echo ""
        return
    fi

    case "$command" in
        assess)
            cat << 'HANDOFF'
handoffs:
  - label: "Specify Requirements"
    agent: "flow-specify"
    prompt: "The assessment is complete. Based on the assessment, create detailed product requirements."
    send: false
HANDOFF
            ;;
        specify)
            cat << 'HANDOFF'
handoffs:
  - label: "Conduct Research"
    agent: "flow-research"
    prompt: "The specification is complete. Conduct research to validate technical feasibility and market fit."
    send: false
  - label: "Create Technical Design"
    agent: "flow-plan"
    prompt: "The specification is complete. Create the technical architecture and platform design."
    send: false
HANDOFF
            ;;
        research)
            cat << 'HANDOFF'
handoffs:
  - label: "Create Technical Design"
    agent: "flow-plan"
    prompt: "Research is complete. Create the technical architecture and platform design based on findings."
    send: false
HANDOFF
            ;;
        plan)
            cat << 'HANDOFF'
handoffs:
  - label: "Begin Implementation"
    agent: "flow-implement"
    prompt: "Planning is complete. Begin implementing the feature according to the technical design."
    send: false
HANDOFF
            ;;
        implement)
            cat << 'HANDOFF'
handoffs:
  - label: "Run Validation"
    agent: "flow-validate"
    prompt: "Implementation is complete. Run QA validation, security review, and documentation checks."
    send: false
HANDOFF
            ;;
        validate)
            cat << 'HANDOFF'
handoffs:
  - label: "Deploy to Production"
    agent: "flow-operate"
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
    local role="$1"

    # Full workflow tools for flow and role-based commands
    if [[ "$role" == "flow" ]] || [[ "$role" =~ ^(pm|arch|dev|qa|sec|ops)$ ]]; then
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
        # Utility tools (spec)
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

# Generate Copilot agent frontmatter with role metadata
generate_frontmatter() {
    local role="$1"
    local command="$2"
    local description="$3"

    local name="${role}-${command}"
    local handoffs
    local tools

    handoffs=$(get_handoffs "$role" "$command")
    tools=$(get_tools "$role")

    echo "---"
    echo "name: \"$name\""
    echo "description: \"$description\""
    echo "target: \"chat\""
    echo "$tools"

    # Add role metadata for role-based commands
    if [[ "$role" =~ ^(pm|arch|dev|qa|sec|ops)$ ]]; then
        echo ""
        echo "# Role-Based Metadata"
        echo "role: \"$role\""
        echo "priority_for_roles:"
        echo "  - \"$role\""
        echo "visible_to_roles:"
        echo "  - \"$role\""
        echo "  - \"all\""

        # Auto-load for primary workflow commands
        case "$command" in
            assess|define|discover|design|build|test|scan|deploy)
                echo "auto_load_for_roles:"
                echo "  - \"$role\""
                ;;
        esac
    fi

    if [[ -n "$handoffs" ]]; then
        echo ""
        echo "$handoffs"
    fi
    echo "---"
}

# Process a single command file
process_command() {
    local source_file="$1"
    local role="$2"

    # Get command name (filename without .md)
    local command
    command=$(basename "$source_file" .md)

    # Skip partials (files starting with _)
    if [[ "$command" == _* ]]; then
        log_verbose "Skipping partial: $command"
        return 0
    fi

    # Check role filter
    if ! should_process_command "$role"; then
        log_verbose "Skipping $role/$command (filtered by --role $ROLE_FILTER)"
        return 0
    fi

    log_verbose "Processing: $role/$command"

    # Resolve includes and get content
    local resolved_content
    if ! resolved_content=$(resolve_includes "$source_file" 2>&1); then
        log_error "Failed to resolve includes for $role/$command: $resolved_content"
        ERRORS=$((ERRORS + 1))
        return 1
    fi

    # Note: Includes inside code blocks are intentionally preserved
    # The Python resolve_includes() function only processes includes outside code blocks
    # If an include outside a code block couldn't be resolved, Python would have errored

    # Extract description from original frontmatter
    local description
    description=$(extract_description "$resolved_content")
    if [[ -z "$description" ]]; then
        description="$role $command workflow command"
        log_warn "No description found for $role/$command, using default"
    fi

    # Remove original frontmatter and get body
    local body
    body=$(echo "$resolved_content" | $PYTHON_CMD -c "
import sys
import re
content = sys.stdin.read()
# Remove YAML frontmatter
body = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, count=1, flags=re.DOTALL)
print(body, end='')
")

    # Generate new frontmatter
    local new_frontmatter
    new_frontmatter=$(generate_frontmatter "$role" "$command" "$description")

    # Combine frontmatter and body
    local output="${new_frontmatter}
${body}"

    # Output file path
    local output_file="$AGENTS_DIR/${role}-${command}.agent.md"

    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY-RUN] Would create: ${role}-${command}.agent.md"
        if [[ "$VERBOSE" == true ]]; then
            echo "--- Frontmatter Preview ---"
            echo "$new_frontmatter"
            echo "--- End Preview ---"
        fi
    elif [[ "$VALIDATE" == true ]]; then
        # Compare with existing file
        if [[ -f "$output_file" ]]; then
            local existing
            # Normalize line endings and trailing whitespace for cross-platform comparison
            # Windows bash can introduce CRLF differences even with gitattributes eol=lf
            existing=$(cat "$output_file" | tr -d '\r')
            local normalized_output
            normalized_output=$(printf '%s' "$output" | tr -d '\r')
            if [[ "$existing" != "$normalized_output" ]]; then
                log_error "Drift detected: ${role}-${command}.agent.md"
                ERRORS=$((ERRORS + 1))
                return 1
            fi
            log_verbose "Validated: ${role}-${command}.agent.md"
        else
            log_error "Missing: ${role}-${command}.agent.md"
            ERRORS=$((ERRORS + 1))
            return 1
        fi
    else
        # Write output with normalized LF line endings for cross-platform consistency
        mkdir -p "$(dirname "$output_file")"
        printf '%s\n' "$output" | tr -d '\r' > "$output_file"
        log_success "Created: ${role}-${command}.agent.md"
    fi

    PROCESSED_FILES=$((PROCESSED_FILES + 1))
}

# Process all commands in a namespace/role directory
process_namespace() {
    local role="$1"
    local namespace_dir="$2"

    if [[ ! -d "$namespace_dir" ]]; then
        log_verbose "Directory not found: $namespace_dir"
        return 0
    fi

    log_info "Processing role/namespace: $role (from $(basename "$namespace_dir"))"

    # Enable nullglob so empty globs expand to nothing instead of literal pattern
    local old_nullglob
    old_nullglob=$(shopt -p nullglob || true)
    shopt -s nullglob

    log_verbose "Starting file loop for $namespace_dir/*.md"

    # Process both regular files and symlinks
    local file_count=0
    for file in "$namespace_dir"/*.md; do
        file_count=$((file_count + 1))
        log_verbose "File $file_count: $(basename "$file")"
        if [[ -f "$file" || -L "$file" ]]; then
            TOTAL_FILES=$((TOTAL_FILES + 1))
            log_verbose "Processing file: $(basename "$file")"
            if process_command "$file" "$role"; then
                log_verbose "Successfully processed $(basename "$file")"
            else
                log_warn "Failed to process $(basename "$file")"
            fi
        fi
    done
    log_verbose "Completed $file_count files for $role"

    # Restore previous nullglob setting
    $old_nullglob 2>/dev/null || true
}

# Generate VS Code settings.json with agent pinning
generate_vscode_settings() {
    if [[ "$DRY_RUN" == true || "$VALIDATE" == true ]]; then
        return 0
    fi

    log_info "Generating .vscode/settings.json with agent pinning..."

    local vscode_dir="$PROJECT_ROOT/.vscode"
    local settings_file="$vscode_dir/settings.json"

    # Create .vscode directory if needed
    mkdir -p "$vscode_dir"

    # Generate settings with agent visibility based on roles
    cat > "$settings_file" << 'EOF'
{
  "github.copilot.chat.agents": {
    "enabled": true,
    "agentVisibility": {
      "pm-*": {
        "visibleInRoles": ["pm", "all"],
        "autoLoadInRoles": ["pm"]
      },
      "arch-*": {
        "visibleInRoles": ["arch", "all"],
        "autoLoadInRoles": ["arch"]
      },
      "dev-*": {
        "visibleInRoles": ["dev", "all"],
        "autoLoadInRoles": ["dev"]
      },
      "qa-*": {
        "visibleInRoles": ["qa", "all"],
        "autoLoadInRoles": ["qa"]
      },
      "sec-*": {
        "visibleInRoles": ["sec", "all"],
        "autoLoadInRoles": ["sec"]
      },
      "ops-*": {
        "visibleInRoles": ["ops", "all"],
        "autoLoadInRoles": ["ops"]
      },
      "flow-*": {
        "visibleInRoles": ["all"]
      },
      "spec-*": {
        "visibleInRoles": ["all"]
      }
    }
  }
}
EOF

    log_success "Generated: .vscode/settings.json"
}

# Remove stale agent files
cleanup_stale() {
    if [[ "$DRY_RUN" == true || "$VALIDATE" == true ]]; then
        return 0
    fi

    log_info "Checking for stale agent files..."

    # Enable nullglob so empty globs expand to nothing instead of literal pattern
    local old_nullglob
    old_nullglob=$(shopt -p nullglob || true)
    shopt -s nullglob

    # Remove old-format files (flow.*.md and spec.*.md)
    for old_file in "$AGENTS_DIR"/flow.*.md "$AGENTS_DIR"/spec.*.md; do
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

        # Parse role and command from filename
        local role command
        if [[ "$basename" =~ ^(pm|arch|dev|qa|sec|ops|flow|spec)-(.+)$ ]]; then
            role="${BASH_REMATCH[1]}"
            command="${BASH_REMATCH[2]}"
        else
            # Unknown format, skip
            continue
        fi

        # Check if source exists in either location
        local source_exists=false

        # Check legacy locations
        if [[ -f "$COMMANDS_DIR/$role/$command.md" || -L "$COMMANDS_DIR/$role/$command.md" ]]; then
            source_exists=true
        fi

        # Check templates/commands location
        if [[ -f "$TEMPLATES_COMMANDS_DIR/$role/$command.md" || -L "$TEMPLATES_COMMANDS_DIR/$role/$command.md" ]]; then
            source_exists=true
        fi

        if [[ "$source_exists" == false ]]; then
            if [[ "$FORCE" == true ]]; then
                rm "$agent_file"
                log_warn "Removed stale: $basename.agent.md"
            else
                log_warn "Stale file detected: $basename.agent.md (use --force to remove)"
            fi
        fi
    done

    # Restore previous nullglob setting
    $old_nullglob 2>/dev/null || true
}

# Main execution
main() {
    parse_args "$@"

    local start_time
    start_time=$($PYTHON_CMD -c "import time; print(int(time.time() * 1000))")

    log_info "Syncing Claude Code commands to VS Code Copilot agents"
    log_info "Sources:"
    log_info "  - Legacy: $COMMANDS_DIR"
    log_info "  - Role-based: $TEMPLATES_COMMANDS_DIR"
    log_info "Target: $AGENTS_DIR"

    if [[ -n "$ROLE_FILTER" ]]; then
        log_info "Role filter: $ROLE_FILTER"
    fi

    if [[ "$DRY_RUN" == true ]]; then
        log_info "Mode: DRY-RUN (no files will be written)"
    elif [[ "$VALIDATE" == true ]]; then
        log_info "Mode: VALIDATE (checking for drift)"
    else
        log_info "Mode: SYNC"
    fi

    # Load role metadata
    get_role_metadata

    # Ensure agents directory exists
    if [[ "$DRY_RUN" != true && "$VALIDATE" != true ]]; then
        mkdir -p "$AGENTS_DIR"
    fi

    # Process legacy namespaces (if they exist)
    if [[ -d "$COMMANDS_DIR/flow" ]]; then
        process_namespace "flow" "$COMMANDS_DIR/flow"
    fi
    if [[ -d "$COMMANDS_DIR/spec" ]]; then
        process_namespace "spec" "$COMMANDS_DIR/spec"
    fi

    # Process role-based commands from templates/commands/
    for role_dir in "$TEMPLATES_COMMANDS_DIR"/*; do
        if [[ -d "$role_dir" ]]; then
            local role
            role=$(basename "$role_dir")
            process_namespace "$role" "$role_dir"
        fi
    done

    # Generate VS Code settings if requested
    if [[ "$WITH_VSCODE" == true ]]; then
        generate_vscode_settings
    fi

    # Cleanup stale files
    cleanup_stale

    # Calculate duration
    local end_time duration_ms
    end_time=$($PYTHON_CMD -c "import time; print(int(time.time() * 1000))")
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
