# Flowspec / flowspec Agents Development Container
# Published to Docker Hub: jpoley/flowspec-agents
#
# This Dockerfile builds a pre-configured development environment with:
# - Python 3.13 + uv package manager (Alpine-based, zero vulnerabilities)
# - Node.js 20 + pnpm
# - AI coding assistant CLIs (Claude Code, Codex, Gemini, GitHub Copilot)
# - Task management (backlog.md)
# - Common development tools
#
# Usage:
#   docker pull jpoley/flowspec-agents:latest
#   Or reference in devcontainer.json: "image": "jpoley/flowspec-agents:latest"

FROM python:3.13-alpine

# Install system dependencies
# - bash: required for scripts and shell compatibility
# - git: version control
# - curl: downloads and health checks
# - nodejs/npm: for AI CLI tools
# - build-base: compilation tools for native extensions
# - linux-headers: kernel headers for some Python packages
# - libffi-dev: for cffi (used by many Python packages)
# - openssl-dev: for cryptography packages
# - zsh: developer-friendly shell
# - shadow: for usermod/groupmod
# - sudo: for privilege escalation
RUN apk add --no-cache \
    bash \
    git \
    curl \
    nodejs \
    npm \
    build-base \
    linux-headers \
    libffi-dev \
    openssl-dev \
    zsh \
    shadow \
    sudo

# Install pnpm globally
RUN npm install -g pnpm

# Fix npm vulnerabilities by upgrading vulnerable packages globally
# - CVE-2025-64756: glob@11.0.3 -> 11.1.0 (command injection vulnerability)
# - CVE-2022-25883: semver@7.0.0 -> 7.5.4 (ReDoS vulnerability, fix >= 7.5.2)
RUN npm install -g glob@11.1.0 semver@7.5.4 \
    && npm cache clean --force

# Install GitHub CLI
RUN apk add --no-cache github-cli

# Create vscode user (matching devcontainer convention)
RUN addgroup -g 1000 vscode \
    && adduser -u 1000 -G vscode -h /home/vscode -s /bin/zsh -D vscode \
    && echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/vscode \
    && chmod 0440 /etc/sudoers.d/vscode

# Switch to vscode user for remaining setup
USER vscode
WORKDIR /home/vscode

# Set up environment variables
ENV PNPM_HOME="/home/vscode/.local/share/pnpm"
ENV PATH="/home/vscode/.local/bin:${PNPM_HOME}:${PATH}"

# Install uv (installs to ~/.local/bin)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Configure pnpm global bin directory
RUN mkdir -p "$PNPM_HOME" && pnpm config set global-bin-dir "$PNPM_HOME"

# Install AI coding assistant CLIs
# Note: These are best-effort installs; some may not be available in all regions
RUN pnpm install -g @anthropic-ai/claude-code || echo "claude-code install skipped" \
    && pnpm install -g @githubnext/github-copilot-cli || echo "copilot-cli install skipped" \
    && pnpm install -g @openai/codex || echo "codex install skipped" \
    && pnpm install -g @google/gemini-cli || echo "gemini-cli install skipped"

# Install task management tools
RUN pnpm install -g backlog.md || echo "backlog.md install skipped"

# Install Python development tools via uv
RUN /home/vscode/.local/bin/uv tool install ruff \
    && /home/vscode/.local/bin/uv tool install pytest

# Create shell configuration for PATH
RUN mkdir -p /home/vscode/.config/claude \
    && echo '# flowspec Agents PATH setup' > /home/vscode/.zshenv \
    && echo 'export PNPM_HOME="/home/vscode/.local/share/pnpm"' >> /home/vscode/.zshenv \
    && echo 'export PATH="/home/vscode/.local/bin:$PNPM_HOME:$PATH"' >> /home/vscode/.zshenv

# Create .zshrc with YOLO aliases (commented out by default for safety)
RUN touch /home/vscode/.zshrc \
    && echo '' >> /home/vscode/.zshrc \
    && echo '# AI coding agent YOLO aliases (uncomment at your own risk)' >> /home/vscode/.zshrc \
    && echo '# alias claude-yolo="claude --dangerously-skip-permissions"' >> /home/vscode/.zshrc \
    && echo '# alias codex-yolo="codex --dangerously-bypass-approvals-and-sandbox"' >> /home/vscode/.zshrc \
    && echo '# alias gemini-yolo="gemini --yolo"' >> /home/vscode/.zshrc

# Labels for Docker Hub
LABEL org.opencontainers.image.title="flowspec Agents"
LABEL org.opencontainers.image.description="Development container with AI coding assistants (Claude Code, Codex, Gemini, GitHub Copilot) and task management tools"
LABEL org.opencontainers.image.source="https://github.com/jpoley/flowspec"
LABEL org.opencontainers.image.vendor="jpoley"
LABEL org.opencontainers.image.licenses="MIT"

# Verify installations
RUN echo "=== Installation Verification ===" \
    && echo "Python: $(python --version)" \
    && echo "Node: $(node --version)" \
    && echo "pnpm: $(pnpm --version)" \
    && echo "uv: $(/home/vscode/.local/bin/uv --version)" \
    && echo "gh: $(gh --version | head -1)" \
    && echo "PATH: $PATH"

# Default command
CMD ["zsh"]
