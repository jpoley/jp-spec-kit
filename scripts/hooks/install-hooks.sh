#!/bin/bash
# Install git hooks for jp-spec-kit
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

echo ""
echo "Git hooks installed successfully!"
echo "The pre-commit hook will validate that task files have acceptance criteria."
