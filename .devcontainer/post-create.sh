#!/bin/bash
# JP Spec Kit Devcontainer Post-Create Script
# This script runs once when the container is first created
set -e

echo "========================================"
echo "JP Spec Kit Devcontainer Setup"
echo "========================================"
echo ""

# Ensure uv is in PATH (installed by onCreateCommand)
export PATH="/home/vscode/.cargo/bin:$PATH"

# -----------------------------------------------------------------------------
# 1. Python Environment Setup
# -----------------------------------------------------------------------------
echo "1. Setting up Python environment..."

echo "   Installing Python dependencies with uv..."
uv sync --all-extras
echo "   Done."

echo "   Installing specify CLI..."
uv tool install . --force
echo "   Done."

# -----------------------------------------------------------------------------
# 2. AI Coding Assistant CLIs
# -----------------------------------------------------------------------------
echo ""
echo "2. Installing AI Coding Assistant CLIs..."

echo "   Installing Claude Code CLI..."
pnpm install -g @anthropic-ai/claude-code || echo "   Warning: claude-code install failed (may need auth)"

echo "   Installing GitHub Copilot CLI..."
pnpm install -g @github/copilot || echo "   Warning: copilot install failed"

echo "   Installing OpenAI Codex CLI..."
pnpm install -g @openai/codex || echo "   Warning: codex install failed"

echo "   Installing Google Gemini CLI..."
pnpm install -g @google/gemini-cli || echo "   Warning: gemini-cli install failed"

echo "   Installing Cursor..."
curl https://cursor.com/install -fsSL | bash || echo "   Warning: cursor install failed"

echo "   Done."

# -----------------------------------------------------------------------------
# 3. Task Management
# -----------------------------------------------------------------------------
echo ""
echo "3. Installing Task Management Tools..."

echo "   Installing backlog.md CLI..."
pnpm install -g backlog.md || echo "   Warning: backlog.md install failed"
echo "   Done."

# -----------------------------------------------------------------------------
# 4. MCP Server Configuration
# -----------------------------------------------------------------------------
echo ""
echo "4. Setting up MCP server configuration..."

mkdir -p ~/.config/claude

cat > ~/.config/claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "backlog": {
      "command": "npx",
      "args": ["-y", "backlog.md"],
      "env": {
        "BACKLOG_DIR": "/workspaces/jp-spec-kit/backlog"
      }
    }
  }
}
EOF

echo "   MCP configuration created at ~/.config/claude/claude_desktop_config.json"

# -----------------------------------------------------------------------------
# 5. Git Hooks (if available)
# -----------------------------------------------------------------------------
echo ""
echo "5. Setting up git hooks..."

if [ -f ".claude/hooks/install-hooks.sh" ]; then
    bash .claude/hooks/install-hooks.sh || echo "   Warning: hook installation failed"
else
    echo "   No hooks to install."
fi

# -----------------------------------------------------------------------------
# 6. Make scripts executable
# -----------------------------------------------------------------------------
echo ""
echo "6. Making scripts executable..."

if [ -d "scripts/bash" ]; then
    chmod +x scripts/bash/*.sh 2>/dev/null || true
    echo "   Done."
else
    echo "   No scripts directory found."
fi

# -----------------------------------------------------------------------------
# 7. Verification
# -----------------------------------------------------------------------------
echo ""
echo "========================================"
echo "Verification"
echo "========================================"
echo ""
echo "Python version:    $(python --version 2>&1)"
echo "uv version:        $(uv --version 2>&1)"
echo "Node version:      $(node --version 2>&1)"
echo "pnpm version:      $(pnpm --version 2>&1)"
echo "gh version:        $(gh --version 2>&1 | head -1)"
echo ""

# Check for installed tools
echo "Installed CLI tools:"
command -v specify >/dev/null 2>&1 && echo "  - specify:     $(specify --version 2>&1 || echo 'installed')" || echo "  - specify:     NOT FOUND (try: source ~/.bashrc)"
command -v claude >/dev/null 2>&1 && echo "  - claude:      installed" || echo "  - claude:      NOT FOUND"
command -v copilot >/dev/null 2>&1 && echo "  - copilot:     installed" || echo "  - copilot:     NOT FOUND"
command -v codex >/dev/null 2>&1 && echo "  - codex:       installed" || echo "  - codex:       NOT FOUND"
command -v gemini >/dev/null 2>&1 && echo "  - gemini:      installed" || echo "  - gemini:       NOT FOUND"
command -v cursor >/dev/null 2>&1 && echo "  - cursor:      installed" || echo "  - cursor:      NOT FOUND"
command -v backlog >/dev/null 2>&1 && echo "  - backlog:     installed" || echo "  - backlog:     NOT FOUND"

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Quick start commands:"
echo "  pytest tests/           - Run test suite"
echo "  ruff check . --fix      - Lint and fix code"
echo "  ruff format .           - Format code"
echo "  backlog task list       - List backlog tasks"
echo "  specify --help          - JP Spec Kit CLI"
echo ""
echo "Documentation:"
echo "  README.md               - Project overview"
echo "  docs/                   - Full documentation"
echo "  CLAUDE.md               - Development standards"
echo ""
