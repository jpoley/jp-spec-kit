#!/bin/bash
#
# Setup script for Flowspec security pre-commit hooks
#
# This script installs the security scanning pre-commit hook in your project.
# It can be run on new projects or to add security hooks to existing projects.
#
# Usage:
#   ./scripts/bash/setup-security-hooks.sh [options]
#
# Options:
#   --force     Overwrite existing configuration
#   --uninstall Remove security hooks
#   --check     Check current installation status
#   --help      Show this help message
#

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/../.."

# Colors (respect NO_COLOR)
if [[ -z "${NO_COLOR:-}" ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    BOLD=''
    NC=''
fi

# Logging functions
log() {
    echo -e "${BLUE}[setup]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[setup]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[setup]${NC} $*"
}

log_error() {
    echo -e "${RED}[setup]${NC} $*"
}

# Show help message
show_help() {
    cat << 'EOF'
Flowspec Security Hook Setup

USAGE:
    ./scripts/bash/setup-security-hooks.sh [options]

OPTIONS:
    --force     Overwrite existing configuration
    --uninstall Remove security hooks from project
    --check     Check current installation status
    --help      Show this help message

DESCRIPTION:
    This script sets up the security scanning pre-commit hook for your project.
    The hook runs fast security scans on staged files before each commit,
    blocking commits with critical vulnerabilities.

REQUIREMENTS:
    - Git repository
    - Python 3.11+
    - pre-commit (will be installed if missing)

EXAMPLES:
    # Install security hooks
    ./scripts/bash/setup-security-hooks.sh

    # Check installation status
    ./scripts/bash/setup-security-hooks.sh --check

    # Remove security hooks
    ./scripts/bash/setup-security-hooks.sh --uninstall

CONFIGURATION:
    Environment variables to customize behavior:
    - FLOWSPEC_SECURITY_FAIL_ON: Severity threshold (default: critical)
    - FLOWSPEC_SECURITY_TIMEOUT: Scan timeout in seconds (default: 30)
    - FLOWSPEC_SECURITY_BYPASS: Set to "1" to skip scanning (logged)

EOF
}

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir &>/dev/null; then
        log_error "Not a git repository. Please run from a git project root."
        exit 1
    fi
}

# Check Python version
check_python() {
    local python_cmd=""

    if command -v python3 &>/dev/null; then
        python_cmd="python3"
    elif command -v python &>/dev/null; then
        python_cmd="python"
    else
        log_error "Python not found. Please install Python 3.11+"
        exit 1
    fi

    local version
    version=$($python_cmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

    if [[ $(echo "$version < 3.11" | bc -l 2>/dev/null || echo "1") == "1" ]]; then
        log_warn "Python $version detected. Recommended: 3.11+"
    fi
}

# Install pre-commit if not present
install_precommit() {
    if command -v pre-commit &>/dev/null; then
        log "pre-commit already installed"
        return 0
    fi

    log "Installing pre-commit..."

    if command -v pip &>/dev/null; then
        pip install pre-commit
    elif command -v pip3 &>/dev/null; then
        pip3 install pre-commit
    elif command -v uv &>/dev/null; then
        uv pip install pre-commit
    else
        log_error "pip not found. Please install pre-commit manually:"
        log_error "  pip install pre-commit"
        exit 1
    fi

    log_success "pre-commit installed successfully"
}

# Check if security hook is already configured
is_hook_configured() {
    if [[ ! -f .pre-commit-config.yaml ]]; then
        return 1
    fi

    grep -q "flowspec-security-scan\|pre-commit-security-scan" .pre-commit-config.yaml 2>/dev/null
}

# Add security hook to .pre-commit-config.yaml
add_hook_to_config() {
    local force="${1:-false}"

    if [[ ! -f .pre-commit-config.yaml ]]; then
        log "Creating .pre-commit-config.yaml..."
        cat > .pre-commit-config.yaml << 'EOF'
# Pre-commit hook configuration
# See https://pre-commit.com for more information

repos:
  # Flowspec Security Scanning
  - repo: local
    hooks:
      - id: flowspec-security-scan
        name: Flowspec Security Scan
        entry: scripts/bash/pre-commit-security-scan.sh
        language: script
        pass_filenames: false
        stages: [commit]
        description: Fast security scan on staged files
EOF
        return 0
    fi

    if is_hook_configured; then
        if [[ "$force" == "true" ]]; then
            log_warn "Removing existing security hook configuration..."
            # Remove existing hook block (basic removal)
            sed -i '/flowspec-security-scan/,/description:.*security/d' .pre-commit-config.yaml
        else
            log "Security hook already configured in .pre-commit-config.yaml"
            return 0
        fi
    fi

    log "Adding security hook to .pre-commit-config.yaml..."

    # Append security hook to existing config
    cat >> .pre-commit-config.yaml << 'EOF'

  # Flowspec Security Scanning
  - repo: local
    hooks:
      - id: flowspec-security-scan
        name: Flowspec Security Scan
        entry: scripts/bash/pre-commit-security-scan.sh
        language: script
        pass_filenames: false
        stages: [commit]
        description: Fast security scan on staged files
EOF

    log_success "Security hook added to configuration"
}

# Copy hook script to project
copy_hook_script() {
    local target_dir="scripts/bash"
    local target_file="$target_dir/pre-commit-security-scan.sh"

    # Create directory if needed
    mkdir -p "$target_dir"

    # Check if script already exists
    if [[ -f "$target_file" ]]; then
        log "Hook script already exists at $target_file"
        return 0
    fi

    # Copy from template if available
    if [[ -f "${PROJECT_ROOT}/scripts/bash/pre-commit-security-scan.sh" ]]; then
        cp "${PROJECT_ROOT}/scripts/bash/pre-commit-security-scan.sh" "$target_file"
        chmod +x "$target_file"
        log_success "Hook script installed at $target_file"
    else
        log_error "Hook script template not found"
        exit 1
    fi
}

# Install git hooks via pre-commit
install_git_hooks() {
    log "Installing git hooks..."
    pre-commit install

    log_success "Git hooks installed"
}

# Uninstall security hooks
uninstall_hooks() {
    log "Uninstalling security hooks..."

    # Remove from pre-commit config
    if is_hook_configured; then
        log "Removing security hook from .pre-commit-config.yaml..."
        # Simple removal - may need manual cleanup
        sed -i '/# Flowspec Security Scanning/,/description:.*security/d' .pre-commit-config.yaml
        log_success "Security hook removed from configuration"
    else
        log "Security hook not found in configuration"
    fi

    # Reinstall remaining hooks
    if [[ -f .pre-commit-config.yaml ]]; then
        pre-commit install
    fi

    log_success "Security hooks uninstalled"
}

# Check installation status
check_status() {
    echo -e "${BOLD}Flowspec Security Hook Status${NC}"
    echo ""

    # Check pre-commit
    if command -v pre-commit &>/dev/null; then
        local version
        version=$(pre-commit --version 2>/dev/null || echo "unknown")
        echo -e "  pre-commit: ${GREEN}installed${NC} ($version)"
    else
        echo -e "  pre-commit: ${RED}not installed${NC}"
    fi

    # Check configuration
    if [[ -f .pre-commit-config.yaml ]]; then
        echo -e "  .pre-commit-config.yaml: ${GREEN}exists${NC}"

        if is_hook_configured; then
            echo -e "  Security hook: ${GREEN}configured${NC}"
        else
            echo -e "  Security hook: ${YELLOW}not configured${NC}"
        fi
    else
        echo -e "  .pre-commit-config.yaml: ${YELLOW}not found${NC}"
    fi

    # Check hook script
    if [[ -f scripts/bash/pre-commit-security-scan.sh ]]; then
        if [[ -x scripts/bash/pre-commit-security-scan.sh ]]; then
            echo -e "  Hook script: ${GREEN}installed and executable${NC}"
        else
            echo -e "  Hook script: ${YELLOW}installed but not executable${NC}"
        fi
    else
        echo -e "  Hook script: ${RED}not installed${NC}"
    fi

    # Check git hooks
    if [[ -f .git/hooks/pre-commit ]]; then
        echo -e "  Git pre-commit hook: ${GREEN}installed${NC}"
    else
        echo -e "  Git pre-commit hook: ${YELLOW}not installed${NC}"
    fi

    # Check bypass log
    if [[ -f .flowspec/security-bypass.log ]]; then
        local bypass_count
        bypass_count=$(wc -l < .flowspec/security-bypass.log 2>/dev/null || echo "0")
        echo -e "  Bypass log: ${YELLOW}${bypass_count} entries${NC}"
    else
        echo -e "  Bypass log: ${GREEN}no bypasses recorded${NC}"
    fi

    echo ""
}

# Main installation
main_install() {
    local force="${1:-false}"

    log "Setting up Flowspec security hooks..."
    echo ""

    check_git_repo
    check_python
    install_precommit
    add_hook_to_config "$force"
    install_git_hooks

    echo ""
    log_success "Security hooks setup complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Test the hook: pre-commit run --all-files"
    echo "  2. Make a commit to verify the hook runs"
    echo ""
    echo "Configuration:"
    echo "  - Bypass: FLOWSPEC_SECURITY_BYPASS=1 git commit"
    echo "  - Skip once: git commit --no-verify"
    echo "  - Adjust severity: FLOWSPEC_SECURITY_FAIL_ON=high"
    echo ""
}

# Parse arguments
main() {
    local force=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --force)
                force=true
                shift
                ;;
            --uninstall)
                check_git_repo
                uninstall_hooks
                exit 0
                ;;
            --check)
                check_status
                exit 0
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    main_install "$force"
}

# Run main
main "$@"
