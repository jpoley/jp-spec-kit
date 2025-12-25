#!/bin/bash
# Flowspec Devcontainer Post-Create Script
# This script runs once when the container is first created
set -e

echo "========================================"
echo "Flowspec Devcontainer Setup"
echo "========================================"
echo ""

# -----------------------------------------------------------------------------
# 0. Setup PATH for this script and future shells
# -----------------------------------------------------------------------------

# pnpm global packages install to PNPM_HOME, but the binaries/shims are created
# in PNPM_HOME itself when global-bin-dir is set to PNPM_HOME (done below)
PNPM_HOME="/home/vscode/.local/share/pnpm"
export PNPM_HOME

# Build the complete PATH we need
export PATH="$PNPM_HOME:/home/vscode/.cargo/bin:/home/vscode/.local/bin:$PATH"

# Create .zshenv for PATH (runs for ALL shells, including non-interactive)
# This ensures PATH is set even for VS Code integrated terminal
cat > /home/vscode/.zshenv << 'ZSHENV'
# Flowspec devcontainer PATH setup
# This file runs for ALL zsh shells (login, interactive, scripts)

export PNPM_HOME="/home/vscode/.local/share/pnpm"
export PATH="$PNPM_HOME:/home/vscode/.cargo/bin:/home/vscode/.local/bin:$PATH"

# Add Python venv to PATH (activation not needed, just PATH)
if [ -d "/workspaces/flowspec/.venv/bin" ]; then
    export PATH="/workspaces/flowspec/.venv/bin:$PATH"
    export VIRTUAL_ENV="/workspaces/flowspec/.venv"
fi
ZSHENV

# Also add to .zshrc for interactive features
cat >> /home/vscode/.zshrc << 'ZSHRC'

# Added by devcontainer setup (interactive shell additions)
# PATH is already set by .zshenv

# Activate Python virtual environment for prompt indicator
if [ -f "/workspaces/flowspec/.venv/bin/activate" ]; then
    source /workspaces/flowspec/.venv/bin/activate
fi

# Aliases for AI coding agents (YOLO modes)
# -----------------------------------------------------------------------------
# WARNING: The following aliases bypass critical security features of AI agents.
# Using these may expose your environment to malicious code execution,
# data exfiltration, or other vulnerabilities. DO NOT enable unless you
# fully understand the risks and are in a safe, isolated environment.
#
# To enable, uncomment the desired alias below.
# -----------------------------------------------------------------------------
# alias claude-yolo='claude --dangerously-skip-permissions'
# alias codex-yolo='codex --dangerously-bypass-approvals-and-sandbox'
# alias gemini-yolo='gemini --yolo'
# alias copilot-yolo='copilot --allow-all-tools'
ZSHRC

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

# Configure pnpm global bin
pnpm config set global-bin-dir "$PNPM_HOME"

echo "   Installing Claude Code CLI..."
pnpm install -g @anthropic-ai/claude-code || echo "   Warning: claude-code install failed"

echo "   Installing GitHub Copilot CLI..."
pnpm install -g @githubnext/github-copilot-cli || echo "   Warning: copilot install failed"

echo "   Installing OpenAI Codex CLI..."
pnpm install -g @openai/codex || echo "   Warning: codex install failed"

echo "   Installing Google Gemini CLI..."
pnpm install -g @google/gemini-cli || echo "   Warning: gemini-cli install failed"

echo "   Done."

# -----------------------------------------------------------------------------
# 2.5. Claude Logging Wrapper Setup
# -----------------------------------------------------------------------------
echo ""
echo "2.5. Setting up Claude logging wrapper..."

# Install node-pty for wrap.mjs (pinned version from package.json)
echo "   Installing node-pty dependency..."
# SECURITY: Use --frozen-lockfile to ensure only audited pinned versions are installed
# Check if pnpm-lock.yaml exists before using --frozen-lockfile to avoid failures in fresh installs
cd /workspaces/flowspec
if [ -f "pnpm-lock.yaml" ]; then
  pnpm install --frozen-lockfile || echo "   Warning: node-pty install failed"
else
  pnpm install || echo "   Warning: node-pty install failed"
fi

# Create claude wrapper script
echo "   Creating claude wrapper..."
cat > /usr/local/bin/claude-wrapped << 'EOF'
#!/bin/bash
if [ "$FLOWSPEC_CAPTURE_TTY" = "true" ]; then
  exec node /workspaces/flowspec/wrap.mjs claude-code "$@"
else
  exec claude-code "$@"
fi
EOF
chmod +x /usr/local/bin/claude-wrapped

# Add alias to shell configs
echo "   Adding claude alias to shell configs..."
if ! grep -q "alias claude=" /home/vscode/.zshrc 2>/dev/null; then
  echo 'alias claude="claude-wrapped"' >> /home/vscode/.zshrc
fi

if ! grep -q "alias claude=" /home/vscode/.bashrc 2>/dev/null; then
  echo 'alias claude="claude-wrapped"' >> /home/vscode/.bashrc
fi

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

mkdir -p /home/vscode/.config/claude

cat > /home/vscode/.config/claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "backlog": {
      "command": "npx",
      "args": ["-y", "backlog.md"],
      "env": {
        "BACKLOG_DIR": "/workspaces/flowspec/backlog"
      }
    }
  }
}
EOF

echo "   MCP configuration created."

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
echo "pnpm global bin:   $PNPM_HOME"
echo "gh version:        $(gh --version 2>&1 | head -1)"
echo ""

# Check for installed tools
echo "Installed CLI tools:"
command -v flowspec >/dev/null 2>&1 && echo "  - specify:     $(flowspec --version 2>&1 || echo 'installed')" || echo "  - specify:     NOT FOUND"
command -v claude >/dev/null 2>&1 && echo "  - claude:      $(claude --version 2>&1 || echo 'installed')" || echo "  - claude:      NOT FOUND"
command -v github-copilot-cli >/dev/null 2>&1 && echo "  - copilot:     installed" || echo "  - copilot:     NOT FOUND"
command -v codex >/dev/null 2>&1 && echo "  - codex:       installed" || echo "  - codex:       NOT FOUND"
command -v gemini >/dev/null 2>&1 && echo "  - gemini:      installed" || echo "  - gemini:      NOT FOUND"
command -v backlog >/dev/null 2>&1 && echo "  - backlog:     $(backlog --version 2>&1 || echo 'installed')" || echo "  - backlog:     NOT FOUND"

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
echo "  flowspec --help          - Flowspec CLI"
echo "  claude                  - Claude Code CLI"
echo ""
echo "NOTE: Open a new terminal for PATH changes to take effect."
echo ""
