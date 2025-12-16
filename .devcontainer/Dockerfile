# Flowspec / flowspec Agents Development Container
# Published to Docker Hub: jpoley/flowspec-agents
#
# This Dockerfile builds a pre-configured development environment with:
# - Python 3.13 + uv package manager (Alpine-based)
# - Node.js 20 + pnpm (npm removed from final image)
# - AI coding assistant CLIs (Claude Code, Codex, Gemini)
# - Task management (backlog.md)
# - Common development tools
#
# Security Notes:
# - npm is used only during build, then removed to eliminate CVE-2025-64756 (glob)
# - @githubnext/github-copilot-cli removed to eliminate CVE-2022-25883 (semver)
# - gh CLI has CVE-2025-66564 - awaiting upstream fix (PR cli/cli#12299)
#
# Usage:
#   docker pull jpoley/flowspec-agents:latest
#   Or reference in devcontainer.json: "image": "jpoley/flowspec-agents:latest"
#
# Security: This image is built with SBOM and SLSA provenance attestations
# Pin base image with digest for reproducibility and security scanning
FROM python:3.13-alpine@sha256:51b5354ed44df6e1a3b3faf6d3a3d40da129621046b6d5a707b7c1f44d258ed6

# Install system dependencies
# - bash: required for scripts and shell compatibility
# - git: version control
# - curl: downloads and health checks
# - nodejs: for AI CLI tools (npm installed temporarily, removed later)
# - build-base: compilation tools for native extensions
# - linux-headers: kernel headers for some Python packages
# - libffi-dev: for cffi (used by many Python packages)
# - openssl-dev: for cryptography packages
# - zsh: developer-friendly shell
# - shadow: for usermod/groupmod
# - sudo: for privilege escalation
# - jq: for JSON processing in scripts
# - tar/gzip: for extracting downloads
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
    sudo \
    jq \
    tar \
    gzip

# Install pnpm globally using npm (npm will be removed later)
RUN npm install -g pnpm

# Install GitHub CLI from official releases
# NOTE: gh v2.83.2 has CVE-2025-66564 (sigstore/timestamp-authority@1.2.9)
# Upstream fix: PR cli/cli#12299 updates sigstore-go to 1.1.4
# Risk acceptance: Memory exhaustion vuln requires attacker-controlled timestamp server
# Low exploitability in dev container context. Will update when gh releases fix.
ARG GH_VERSION=2.83.2
ARG TARGETARCH
RUN case "${TARGETARCH}" in \
        "amd64") GH_ARCH="linux_amd64" ;; \
        "arm64") GH_ARCH="linux_arm64" ;; \
        *) echo "Unsupported arch: ${TARGETARCH}" && exit 1 ;; \
    esac \
    && curl -sL "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_${GH_ARCH}.tar.gz" -o /tmp/gh.tar.gz \
    && tar -xzf /tmp/gh.tar.gz -C /tmp \
    && mv "/tmp/gh_${GH_VERSION}_${GH_ARCH}/bin/gh" /usr/local/bin/gh \
    && chmod +x /usr/local/bin/gh \
    && rm -rf /tmp/gh* \
    && gh --version

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
ENV PATH="/home/vscode/.local/bin:${PNPM_HOME}:/usr/local/bin:${PATH}"

# Install uv (installs to ~/.local/bin)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Configure pnpm global bin directory
RUN mkdir -p "$PNPM_HOME" && pnpm config set global-bin-dir "$PNPM_HOME"

# Install AI coding assistant CLIs using pnpm
# NOTE: @githubnext/github-copilot-cli INTENTIONALLY EXCLUDED
# Reason: CVE-2022-25883 - ships semver@7.0.0 via simple-update-notifier
# Upstream issue: https://github.com/alexbrazier/simple-update-notifier/issues/30
# Maintainer unresponsive since Sep 2024. Package removed to eliminate vulnerability.
RUN pnpm install -g @anthropic-ai/claude-code || echo "claude-code install skipped" \
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
    && echo 'export PATH="/home/vscode/.local/bin:$PNPM_HOME:/usr/local/bin:$PATH"' >> /home/vscode/.zshenv

# Create .zshrc with YOLO aliases (commented out by default for safety)
RUN touch /home/vscode/.zshrc \
    && echo '' >> /home/vscode/.zshrc \
    && echo '# AI coding agent YOLO aliases (uncomment at your own risk)' >> /home/vscode/.zshrc \
    && echo '# alias claude-yolo="claude --dangerously-skip-permissions"' >> /home/vscode/.zshrc \
    && echo '# alias codex-yolo="codex --dangerously-bypass-approvals-and-sandbox"' >> /home/vscode/.zshrc \
    && echo '# alias gemini-yolo="gemini --yolo"' >> /home/vscode/.zshrc

# Switch back to root to remove npm
USER root

# SECURITY FIX: Remove npm from final image
# This eliminates CVE-2025-64756 (glob@11.0.3 bundled in npm)
# pnpm is standalone and does not require npm at runtime
RUN apk del npm \
    && rm -rf /root/.npm /tmp/npm* 2>/dev/null || true

# Switch back to vscode user
USER vscode

# Labels for Docker Hub
LABEL org.opencontainers.image.title="flowspec Agents"
LABEL org.opencontainers.image.description="Development container with AI coding assistants (Claude Code, Codex, Gemini) and task management tools"
LABEL org.opencontainers.image.source="https://github.com/jpoley/flowspec"
LABEL org.opencontainers.image.vendor="jpoley"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.base.name="python:3.13-alpine"
LABEL org.opencontainers.image.base.digest="sha256:51b5354ed44df6e1a3b3faf6d3a3d40da129621046b6d5a707b7c1f44d258ed6"

# Verify installations and print versions for debugging
RUN echo "=== Installation Verification ===" \
    && echo "Python: $(python --version)" \
    && echo "Node: $(node --version)" \
    && echo "pnpm: $(pnpm --version)" \
    && echo "uv: $(/home/vscode/.local/bin/uv --version)" \
    && echo "gh: $(gh --version | head -1)" \
    && echo "npm: $(npm --version 2>&1 || echo 'REMOVED - security fix')" \
    && echo "PATH: $PATH"

# Default command
CMD ["zsh"]
