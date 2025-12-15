#!/bin/bash
# Install git hooks for flowspec
# Run from repository root: ./scripts/hooks/install-hooks.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "Installing git hooks..."

# Install pre-commit hook
if [ -f "$SCRIPT_DIR/pre-commit" ]; then
    cp "$SCRIPT_DIR/pre-commit" "$HOOKS_DIR/pre-commit"
    chmod +x "$HOOKS_DIR/pre-commit"
    echo "  ✓ pre-commit hook installed"
else
    echo "  ✗ pre-commit hook not found"
    exit 1
fi

# Install pre-push hook
if [ -f "$SCRIPT_DIR/pre-push" ]; then
    cp "$SCRIPT_DIR/pre-push" "$HOOKS_DIR/pre-push"
    chmod +x "$HOOKS_DIR/pre-push"
    echo "  ✓ pre-push hook installed (security scan)"
else
    echo "  ⚠ pre-push hook not found (optional)"
fi

# Install post-commit hook for backlog events
if [ -f "$SCRIPT_DIR/post-commit-backlog-events.sh" ]; then
    cp "$SCRIPT_DIR/post-commit-backlog-events.sh" "$HOOKS_DIR/post-commit"
    chmod +x "$HOOKS_DIR/post-commit"
    echo "  ✓ post-commit hook installed (backlog events)"
else
    echo "  ⚠ post-commit-backlog-events.sh not found (optional)"
fi

echo ""
echo "Git hooks installed successfully!"
echo ""
echo "Hooks installed:"
echo "  - pre-commit: Validates task files have acceptance criteria"
echo "  - pre-push: Runs security scan before pushing (requires semgrep)"
echo "  - post-commit: Emits flowspec events on backlog task changes"
