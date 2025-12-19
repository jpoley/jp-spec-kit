# Flowspec / flowspec Agents Development Container
# Published to Docker Hub: jpoley/flowspec-agents
#
# This Dockerfile builds a pre-configured development environment with:
# - Python 3.13 + uv package manager (Alpine-based)
# - Node.js 20 + pnpm
# - AI coding assistant CLIs (Claude Code, Codex, Gemini, GitHub Copilot)
# - Task management (backlog.md)
# - Common development tools
#
# Usage:
#   docker pull jpoley/flowspec-agents:latest
#   Or reference in devcontainer.json: "image": "jpoley/flowspec-agents:latest"
#
# Security: This image is built with SBOM and SLSA provenance attestations
# Using Docker Hardened Image (DHI) for 95%+ CVE reduction vs standard images
# DHI dev images include build tools: gcc, make, libc-dev, libffi-dev,
# linux-headers, openssl-dev, git, and more (see DHI catalog for full list)
# DHI provides SLSA Level 3 provenance and signed attestations for supply chain security
# See: https://github.com/docker-hardened-images/catalog
FROM dhi.io/python:3.13-alpine3.22-dev

# Install additional system dependencies not in DHI or needed explicitly
# DHI dev image provides: gcc, make, libc-dev, libffi-dev, linux-headers,
# openssl-dev, git, and other build essentials
# We add: nodejs/npm for AI CLI tools, shell utilities
RUN apk add --no-cache \
    bash \
    git \
    curl \
    nodejs \
    npm \
    zsh \
    shadow \
    sudo \
    jq \
    tar \
    gzip

# Upgrade npm to latest version to fix vulnerabilities in npm's internal dependencies
# - CVE-2025-64756: glob@11.0.3 -> 11.1.0 (command injection in npm's bundled glob)
# This upgrades npm itself, not just global packages
RUN npm install -g npm@latest \
    && npm cache clean --force

# Install pnpm globally (after npm upgrade to use patched npm)
RUN npm install -g pnpm

# Install GitHub CLI from official releases (not Alpine package)
# Alpine's github-cli package has outdated dependencies including:
# - CVE-2025-66564: sigstore/timestamp-authority@1.2.9 -> 2.0.3 (memory exhaustion)
# Download latest release directly from GitHub for security updates
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

# Install AI coding assistant CLIs
# Note: These are best-effort installs; some may not be available in all regions
RUN pnpm install -g @anthropic-ai/claude-code || echo "claude-code install skipped" \
    && pnpm install -g @githubnext/github-copilot-cli || echo "copilot-cli install skipped" \
    && pnpm install -g @openai/codex || echo "codex install skipped" \
    && pnpm install -g @google/gemini-cli || echo "gemini-cli install skipped"

# Install task management tools
RUN pnpm install -g backlog.md || echo "backlog.md install skipped"

# Fix pnpm package vulnerabilities by forcing semver upgrade
# - CVE-2022-25883: semver@7.0.0 -> 7.5.4 (ReDoS vulnerability)
# This updates semver in pnpm's global store for all installed packages
RUN cd "${PNPM_HOME}" && pnpm update semver --latest 2>/dev/null || echo "pnpm semver update skipped" \
    && pnpm store prune 2>/dev/null || true

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

# Labels for Docker Hub
LABEL org.opencontainers.image.title="flowspec Agents"
LABEL org.opencontainers.image.description="Development container with AI coding assistants (Claude Code, Codex, Gemini, GitHub Copilot) and task management tools"
LABEL org.opencontainers.image.source="https://github.com/jpoley/flowspec"
LABEL org.opencontainers.image.vendor="jpoley"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.base.name="dhi.io/python:3.13-alpine3.22-dev"
LABEL org.opencontainers.image.base.vendor="Docker Hardened Images"

# Verify installations and print versions for debugging
RUN echo "=== Installation Verification ===" \
    && echo "Python: $(python --version)" \
    && echo "Node: $(node --version)" \
    && echo "npm: $(npm --version)" \
    && echo "pnpm: $(pnpm --version)" \
    && echo "uv: $(/home/vscode/.local/bin/uv --version)" \
    && echo "gh: $(gh --version | head -1)" \
    && echo "PATH: $PATH"

# Default command
CMD ["zsh"]
