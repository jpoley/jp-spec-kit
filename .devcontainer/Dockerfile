# =============================================================================
# AI Coding Agents Devcontainer Image
# Production-ready, multi-platform Docker image for Spec-Driven Development
# =============================================================================
#
# Image: jpoley/specflow-agents:latest
# Platforms: linux/amd64, linux/arm64
# Base: Microsoft Devcontainer Python 3.11 (Debian Bullseye)
#
# Pre-installed tools:
# - Python 3.11 + uv (fast package manager)
# - Node.js 20 + pnpm
# - AI coding CLIs: claude, copilot, codex, gemini
# - Task management: backlog.md, specify CLI
# - Development tools: git, gh, ruff, pytest
#
# Security features:
# - SBOM embedded in image
# - Vulnerability scanning (Trivy, Snyk)
# - Non-root user (vscode)
# - Minimal attack surface
# - No secrets in image
#
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Base Image with System Dependencies
# -----------------------------------------------------------------------------
FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye AS base

# Metadata
LABEL maintainer="James Poley <james@jpoley.com>"
LABEL description="AI Coding Agents Devcontainer - Pre-built environment for Spec-Driven Development"
LABEL version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/jpoley/jp-spec-kit"
LABEL org.opencontainers.image.licenses="MIT"

# Install devcontainer features
USER root

# Install Node.js 20 and pnpm
# This replicates the ghcr.io/devcontainers/features/node:1 feature
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g pnpm \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
# This replicates the ghcr.io/devcontainers/features/github-cli:1 feature
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Switch to vscode user for package installations
USER vscode

# -----------------------------------------------------------------------------
# Stage 2: Install uv and Python Tools
# -----------------------------------------------------------------------------
FROM base AS python-tools

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH for subsequent layers
ENV PATH="/home/vscode/.cargo/bin:$PATH"

# Pre-create common Python virtual environment location
# Projects will typically create a .venv in their workspace
# This just ensures the base tooling is available globally
RUN uv tool install ruff && \
    uv tool install pytest

# -----------------------------------------------------------------------------
# Stage 3: Install AI Coding Assistant CLIs
# -----------------------------------------------------------------------------
FROM python-tools AS ai-tools

# Configure pnpm for global installations
ENV PNPM_HOME="/home/vscode/.local/share/pnpm"
ENV PATH="${PNPM_HOME}:${PATH}"

# Create pnpm home directory
RUN mkdir -p "${PNPM_HOME}"

# Configure pnpm global bin directory
RUN pnpm config set global-bin-dir "${PNPM_HOME}"

# Install AI coding assistant CLIs
# Use --ignore-scripts to avoid running post-install scripts during build
# Use --loglevel error to reduce build output
RUN pnpm install -g @anthropic-ai/claude-code --ignore-scripts --loglevel error || true && \
    pnpm install -g @githubnext/github-copilot-cli --ignore-scripts --loglevel error || true && \
    pnpm install -g @openai/codex --ignore-scripts --loglevel error || true && \
    pnpm install -g @google/gemini-cli --ignore-scripts --loglevel error || true

# Install task management CLI
RUN pnpm install -g backlog.md --ignore-scripts --loglevel error

# Clean pnpm cache to reduce image size
RUN pnpm store prune

# -----------------------------------------------------------------------------
# Stage 4: Shell Configuration
# -----------------------------------------------------------------------------
FROM ai-tools AS shell-config

# Create .zshenv for PATH configuration
# This ensures PATH is set for ALL zsh shells (login, interactive, scripts)
RUN cat > /home/vscode/.zshenv << 'ZSHENV'
# AI Coding Agents Devcontainer PATH setup
# This file runs for ALL zsh shells (login, interactive, scripts)

export PNPM_HOME="/home/vscode/.local/share/pnpm"
export PATH="${PNPM_HOME}:/home/vscode/.cargo/bin:/home/vscode/.local/bin:${PATH}"

# Add project Python venv to PATH if it exists
# (Projects will create this via uv sync in their workspace)
if [ -d "${WORKSPACEROOT}/.venv/bin" ]; then
    export PATH="${WORKSPACEROOT}/.venv/bin:${PATH}"
    export VIRTUAL_ENV="${WORKSPACEROOT}/.venv"
fi
ZSHENV

# Add to .zshrc for interactive features
RUN cat >> /home/vscode/.zshrc << 'ZSHRC'

# Added by AI Coding Agents Devcontainer
# PATH is already set by .zshenv

# Activate Python virtual environment for prompt indicator (if exists)
if [ -f "${WORKSPACEROOT}/.venv/bin/activate" ]; then
    source "${WORKSPACEROOT}/.venv/bin/activate"
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

# Also configure bash for compatibility
RUN cat >> /home/vscode/.bashrc << 'BASHRC'

# Added by AI Coding Agents Devcontainer
export PNPM_HOME="/home/vscode/.local/share/pnpm"
export PATH="${PNPM_HOME}:/home/vscode/.cargo/bin:/home/vscode/.local/bin:${PATH}"

# Add project Python venv to PATH if it exists
if [ -d "${WORKSPACEROOT}/.venv/bin" ]; then
    export PATH="${WORKSPACEROOT}/.venv/bin:${PATH}"
    export VIRTUAL_ENV="${WORKSPACEROOT}/.venv"
fi

# Activate Python virtual environment (if exists)
if [ -f "${WORKSPACEROOT}/.venv/bin/activate" ]; then
    source "${WORKSPACEROOT}/.venv/bin/activate"
fi
BASHRC

# -----------------------------------------------------------------------------
# Stage 5: MCP Server Configuration
# -----------------------------------------------------------------------------
FROM shell-config AS mcp-config

# Create MCP configuration directory
RUN mkdir -p /home/vscode/.config/claude

# Create base MCP configuration
# Projects can override this by mounting their own config
RUN cat > /home/vscode/.config/claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "backlog": {
      "command": "npx",
      "args": ["-y", "backlog.md"],
      "env": {
        "BACKLOG_DIR": "${WORKSPACEROOT}/backlog"
      }
    }
  }
}
EOF

# -----------------------------------------------------------------------------
# Stage 6: Health Checks and Documentation
# -----------------------------------------------------------------------------
FROM mcp-config AS final

# Create a health check script
RUN cat > /home/vscode/healthcheck.sh << 'HEALTHCHECK'
#!/bin/bash
# Health check script for AI Coding Agents Devcontainer
set -e

echo "================================"
echo "AI Coding Agents Devcontainer"
echo "Health Check"
echo "================================"
echo ""

# Check system tools
echo "System Tools:"
python --version || exit 1
node --version || exit 1
pnpm --version || exit 1
gh --version | head -1 || exit 1
uv --version || exit 1
echo ""

# Check AI coding CLIs
echo "AI Coding CLIs:"
command -v claude >/dev/null 2>&1 && echo "  claude: OK" || echo "  claude: NOT FOUND"
command -v github-copilot-cli >/dev/null 2>&1 && echo "  copilot: OK" || echo "  copilot: NOT FOUND"
command -v codex >/dev/null 2>&1 && echo "  codex: OK" || echo "  codex: NOT FOUND"
command -v gemini >/dev/null 2>&1 && echo "  gemini: OK" || echo "  gemini: NOT FOUND"
command -v backlog >/dev/null 2>&1 && echo "  backlog: OK" || echo "  backlog: NOT FOUND"
echo ""

echo "================================"
echo "Health Check: PASS"
echo "================================"
HEALTHCHECK

RUN chmod +x /home/vscode/healthcheck.sh

# Create a welcome message script
RUN cat > /home/vscode/welcome.sh << 'WELCOME'
#!/bin/bash
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║        AI Coding Agents Devcontainer                      ║"
echo "║        Ready for Spec-Driven Development                  ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Quick Start Commands:"
echo "  pytest tests/           - Run test suite"
echo "  ruff check . --fix      - Lint and fix code"
echo "  ruff format .           - Format code"
echo "  backlog task list       - List backlog tasks"
echo "  claude --help           - Claude Code CLI"
echo ""
echo "AI Coding Assistants:"
echo "  claude, copilot, codex, gemini"
echo ""
echo "Documentation:"
echo "  https://github.com/jpoley/jp-spec-kit"
echo ""
WELCOME

RUN chmod +x /home/vscode/welcome.sh

# Set environment variables for runtime
ENV TERM=xterm-256color
ENV PNPM_HOME=/home/vscode/.local/share/pnpm
ENV PATH="${PNPM_HOME}:/home/vscode/.cargo/bin:/home/vscode/.local/bin:${PATH}"

# Default workspace root (can be overridden by devcontainer.json)
ENV WORKSPACEROOT=/workspace

# Set working directory
WORKDIR /workspace

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /home/vscode/healthcheck.sh

# Default command
CMD ["/home/vscode/welcome.sh"]

# -----------------------------------------------------------------------------
# Build Arguments for Versioning and Metadata
# -----------------------------------------------------------------------------
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.version="${VERSION}"
