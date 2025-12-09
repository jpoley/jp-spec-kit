# Docker Hub Devcontainer Image Architecture

**Feature**: Reusable AI Coding Agents Devcontainer Image for Docker Hub
**Status**: Design Phase
**Date**: 2025-12-08
**Authors**: Enterprise Software Architect, Platform Engineer

---

## Executive Summary

This document defines the architecture for publishing a **reusable AI Coding Agents devcontainer image** to Docker Hub that enables any project to instantly get a pre-configured AI coding environment with Claude Code, GitHub Copilot, OpenAI Codex, Google Gemini, and backlog.md task management.

### Vision

```
Current: Each project manually installs AI CLIs (2-5 minutes per container build)
Future:  Reference jpoley/specflow-agents:latest → Ready in 30 seconds
```

### Key Benefits

| Metric | Before (Runtime Install) | After (Pre-built Image) | Improvement |
|--------|-------------------------|-------------------------|-------------|
| Container startup | 2-5 minutes | 30 seconds | 75-90% reduction |
| Network dependency | High (npm, pnpm) | Low (only base layers) | Resilient to npm outages |
| Image caching | Poor (install scripts) | Excellent (pre-built layers) | Faster rebuilds |
| User experience | Configure in every project | Single line in devcontainer.json | Trivial adoption |
| Version consistency | Manual pinning | Docker tags | Guaranteed reproducibility |

---

## 1. Image Architecture

### 1.1 Base Image Selection

**Decision**: Use `mcr.microsoft.com/devcontainers/python:3.11-bullseye` as base

**Rationale**:
- Official Microsoft devcontainer base (trusted, maintained)
- Python 3.11+ required for many AI tools
- Debian bullseye: stable, wide package availability
- Multi-arch support (amd64, arm64)
- Includes common dev tools (git, curl, wget, zsh)

**Trade-offs**:
- Larger base (~500MB) vs Alpine (~50MB)
- **Acceptable**: Development images prioritize compatibility over size

### 1.2 Layer Structure (Optimal Caching)

Multi-stage Dockerfile with strategic layer ordering:

```dockerfile
# ============================================================================
# Stage 1: Base with System Dependencies
# ============================================================================
FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye AS base

# Set non-interactive to prevent apt prompts
ENV DEBIAN_FRONTEND=noninteractive

# Layer 1: System packages (rarely change)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    gnupg \
    openssh-client \
    zsh \
    && rm -rf /var/lib/apt/lists/*

# Layer 2: Node.js setup (rarely change)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get update && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Layer 3: pnpm (rarely change)
RUN npm install -g pnpm@latest

# ============================================================================
# Stage 2: AI Coding Tools (Change Occasionally)
# ============================================================================
FROM base AS ai-tools

# Set pnpm global directory
ENV PNPM_HOME=/usr/local/share/pnpm
ENV PATH=$PNPM_HOME:$PATH

# Configure pnpm
RUN pnpm config set global-bin-dir $PNPM_HOME

# Layer 4: Claude Code CLI
RUN pnpm install -g @anthropic-ai/claude-code

# Layer 5: GitHub Copilot CLI
RUN pnpm install -g @githubnext/github-copilot-cli

# Layer 6: OpenAI Codex CLI
RUN pnpm install -g @openai/codex || echo "Codex CLI unavailable"

# Layer 7: Google Gemini CLI
RUN pnpm install -g @google/gemini-cli || echo "Gemini CLI unavailable"

# Layer 8: backlog.md task management
RUN pnpm install -g backlog.md

# ============================================================================
# Stage 3: Python Tooling (Change Occasionally)
# ============================================================================
FROM ai-tools AS python-tools

# Layer 9: uv (fast Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Layer 10: Common Python tools
RUN pip install --no-cache-dir \
    ruff \
    pytest \
    pytest-cov

# ============================================================================
# Stage 4: Final Runtime Image
# ============================================================================
FROM python-tools AS runtime

# Set up non-root user (vscode user already exists in base)
USER vscode

# Configure PATH for vscode user
ENV PATH=/home/vscode/.cargo/bin:/home/vscode/.local/bin:$PNPM_HOME:$PATH
ENV PNPM_HOME=/usr/local/share/pnpm

# Set shell to zsh
SHELL ["/bin/zsh", "-c"]

# Create standard directories
RUN mkdir -p /home/vscode/.config/claude \
    /home/vscode/.config/github-copilot \
    /home/vscode/.ssh \
    /home/vscode/.claude

# Default working directory
WORKDIR /workspace

# Health check (verify critical tools)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD command -v claude && command -v backlog && command -v uv || exit 1

# Metadata
LABEL org.opencontainers.image.title="AI Coding Agents Devcontainer" \
      org.opencontainers.image.description="Pre-configured devcontainer with Claude Code, Copilot, Codex, Gemini, and backlog.md" \
      org.opencontainers.image.vendor="JP Spec Kit" \
      org.opencontainers.image.source="https://github.com/jpoley/jp-spec-kit" \
      org.opencontainers.image.licenses="MIT"

CMD ["/bin/zsh"]
```

### 1.3 What Goes in Image vs Runtime

| Component | Image (Pre-built) | Runtime (User Provides) | Rationale |
|-----------|------------------|------------------------|-----------|
| **AI CLIs** | Yes | No | Static, version-controlled |
| **Python 3.11** | Yes | No | Base requirement |
| **Node.js 20** | Yes | No | Required for npm CLIs |
| **uv** | Yes | No | Common across projects |
| **ruff, pytest** | Yes | No | Common Python tools |
| **backlog.md** | Yes | No | Task management standard |
| **Project deps** | No | Yes (uv sync) | Project-specific |
| **specify CLI** | No | Yes (uv tool install) | Project-specific |
| **Credentials** | No | Yes (volume mount) | Security: never bake secrets |
| **Git config** | No | Yes (volume mount) | User-specific |
| **SSH keys** | No | Yes (volume mount) | Security: never bake secrets |
| **API keys** | No | Yes (env vars) | Security: never bake secrets |

**Design Principle**: Image contains **tools**, runtime provides **configuration and credentials**.

### 1.4 Multi-Stage Build Rationale

**Benefits**:
1. **Layer caching**: Each stage can be cached independently
2. **Build optimization**: Only rebuild changed stages
3. **Size reduction**: Exclude build tools from final image
4. **Security**: Minimize attack surface in runtime image

**Example**: Updating Claude Code version only rebuilds from Stage 2 onward, reusing Stages 0-1 from cache.

---

## 2. Distribution Strategy

### 2.1 Docker Hub Namespace and Repository

**Namespace**: `jpoley` (personal Docker Hub account)
**Repository**: `specflow-agents`
**Full image name**: `jpoley/specflow-agents`

> **Note:** The repository name `ai-coding-agents` was considered during design, but `specflow-agents` was chosen for consistency with the Spec-Driven Development (SDD) workflow branding.

**Alternative consideration**: Create organization `jpspeckit` → `jpspeckit/specflow-agents`
- **Pros**: Professional, supports team collaboration
- **Cons**: Requires Docker Hub paid plan for private repos
- **Decision**: Start with `jpoley`, migrate to org if adoption grows

### 2.2 Tagging Strategy

Semantic versioning with multiple tag formats for flexibility:

| Tag | Purpose | Example | Update Frequency |
|-----|---------|---------|------------------|
| `latest` | Latest stable release | `jpoley/specflow-agents:latest` | Every release |
| `{major}.{minor}.{patch}` | Exact version pin | `jpoley/specflow-agents:1.2.3` | Once per release |
| `{major}.{minor}` | Minor version track | `jpoley/specflow-agents:1.2` | Updated with patches |
| `{major}` | Major version track | `jpoley/specflow-agents:1` | Updated with minors |
| `edge` | Bleeding edge (main branch) | `jpoley/specflow-agents:edge` | Every commit to main |
| `dev` | Development builds | `jpoley/specflow-agents:dev` | Manual/testing |
| `{feature}-{sha}` | Feature branch testing | `jpoley/specflow-agents:copilot-fix-a1b2c3d` | Per feature branch |

**Version bumping rules**:
- **Patch** (1.2.3 → 1.2.4): Bug fixes, tool version updates
- **Minor** (1.2.0 → 1.3.0): New AI CLI added, feature addition
- **Major** (1.0.0 → 2.0.0): Breaking changes (base image change, removed tools)

**User guidance**:
- **Production**: Use exact version (`1.2.3`) for reproducibility
- **Development**: Use minor version (`1.2`) for automatic patches
- **Experimental**: Use `latest` or `edge`

### 2.3 Image Variants

Provide multiple variants for different use cases:

#### Variant 1: Full (Default)
**Tag**: `jpoley/specflow-agents:latest`
**Contents**: All AI CLIs + Python + Node.js + backlog.md
**Size**: ~1.2GB
**Use case**: Complete AI coding environment

#### Variant 2: Minimal
**Tag**: `jpoley/specflow-agents:minimal`
**Contents**: Claude Code + backlog.md only
**Size**: ~800MB
**Use case**: Projects that only need Claude

#### Variant 3: Python-Optimized
**Tag**: `jpoley/specflow-agents:python`
**Contents**: Full + additional Python tools (mypy, black, bandit)
**Size**: ~1.3GB
**Use case**: Python-heavy projects

#### Variant 4: Node-Optimized
**Tag**: `jpoley/specflow-agents:node`
**Contents**: Full + additional Node tools (eslint, prettier, vitest)
**Size**: ~1.3GB
**Use case**: Node/TypeScript projects

**Implementation**:
```dockerfile
# Minimal variant
FROM base AS minimal
RUN pnpm install -g @anthropic-ai/claude-code backlog.md

# Python variant
FROM runtime AS python
RUN pip install --no-cache-dir mypy black bandit

# Node variant
FROM runtime AS node
RUN pnpm install -g eslint prettier vitest
```

Build all variants in single Dockerfile using `--target` flag:
```bash
docker build --target runtime -t jpoley/specflow-agents:latest .
docker build --target minimal -t jpoley/specflow-agents:minimal .
docker build --target python -t jpoley/specflow-agents:python .
```

### 2.4 Multi-Platform Support

Build for both amd64 (Intel/AMD) and arm64 (Apple Silicon, ARM servers):

```yaml
# GitHub Actions example
- name: Build and push multi-platform
  uses: docker/build-push-action@v5
  with:
    platforms: linux/amd64,linux/arm64
    tags: jpoley/specflow-agents:latest
    push: true
```

**Testing matrix**: Verify image works on:
- [x] Ubuntu 22.04 (amd64)
- [x] macOS (arm64 - Apple Silicon)
- [x] macOS (amd64 - Intel)
- [x] Windows + WSL2 (amd64)

---

## 3. User Experience Design

### 3.1 User Reference Pattern

**Goal**: Users add **one line** to their devcontainer.json to get the full AI environment.

#### Option A: Direct Image Reference (Simplest)
```json
{
  "name": "My Project",
  "image": "jpoley/specflow-agents:1.2",

  "mounts": [
    "source=${localEnv:HOME}/.claude,target=/home/vscode/.claude,type=bind",
    "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,readonly",
    "source=${localEnv:HOME}/.gitconfig,target=/home/vscode/.gitconfig,type=bind,readonly"
  ],

  "remoteEnv": {
    "GITHUB_TOKEN": "${localEnv:GITHUB_TOKEN}",
    "OPENAI_API_KEY": "${localEnv:OPENAI_API_KEY}"
  },

  "postCreateCommand": "uv sync && uv tool install ."
}
```

**Pros**:
- Minimal configuration
- Clear, obvious what's happening
- Easy to customize

**Cons**:
- Requires user to configure mounts manually
- Repetitive across projects

#### Option B: Devcontainer Feature (Best UX)
```json
{
  "name": "My Project",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",

  "features": {
    "ghcr.io/jpoley/devcontainer-features/ai-coding-agents:1": {}
  }
}
```

**Pros**:
- **Best UX**: Automatic mount configuration
- Composable with other features
- Standard devcontainer pattern
- Automatic credential detection

**Cons**:
- Requires publishing devcontainer feature (separate repo)
- More complex to maintain
- Two artifacts to version (image + feature)

**Decision**: Provide **both options**:
1. **Immediate**: Publish Docker image (Option A) for quick adoption
2. **Future**: Publish devcontainer feature (Option B) for best UX

### 3.2 Template devcontainer.json for Users

Provide copy-paste template in repo README and Docker Hub:

```json
{
  "name": "My AI-Powered Project",

  // Option 1: Use full image (recommended for most projects)
  "image": "jpoley/specflow-agents:1.2",

  // Option 2: Use minimal variant (Claude + backlog only)
  // "image": "jpoley/specflow-agents:minimal",

  // Option 3: Use Python-optimized variant
  // "image": "jpoley/specflow-agents:python",

  // Mount user credentials (REQUIRED for AI CLIs)
  // Platform-specific mounts using the 'platform' parameter
  "mounts": [
    // Claude Code config - Linux
    "source=${localEnv:HOME}/.claude,target=/home/vscode/.claude,type=bind,platform=linux",
    // Claude Code config - Windows
    "source=${localEnv:USERPROFILE}/.claude,target=/home/vscode/.claude,type=bind,platform=win32",

    // GitHub Copilot config - Linux
    "source=${localEnv:HOME}/.config/github-copilot,target=/home/vscode/.config/github-copilot,type=bind,platform=linux",
    // GitHub Copilot config - Windows
    "source=${localEnv:USERPROFILE}/.config/github-copilot,target=/home/vscode/.config/github-copilot,type=bind,platform=win32",

    // SSH keys - Linux
    "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,readonly,platform=linux",
    // SSH keys - Windows
    "source=${localEnv:USERPROFILE}/.ssh,target=/home/vscode/.ssh,type=bind,readonly,platform=win32",

    // Git configuration - Linux
    "source=${localEnv:HOME}/.gitconfig,target=/home/vscode/.gitconfig-host,type=bind,readonly,platform=linux",
    // Git configuration - Windows
    "source=${localEnv:USERPROFILE}/.gitconfig,target=/home/vscode/.gitconfig-host,type=bind,readonly,platform=win32"
  ],

  // Forward API keys from host environment (optional)
  "remoteEnv": {
    "GITHUB_TOKEN": "${localEnv:GITHUB_TOKEN}",
    "OPENAI_API_KEY": "${localEnv:OPENAI_API_KEY}",
    "GOOGLE_API_KEY": "${localEnv:GOOGLE_API_KEY}"
  },

  // Project-specific setup (customize for your project)
  "postCreateCommand": "uv sync && uv tool install .",

  // VS Code extensions (customize for your project)
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "charliermarsh.ruff"
      ]
    }
  }
}
```

### 3.3 User Configuration Requirements

Users must provide:

#### Required (For AI CLI Authentication)
1. **OAuth Authentication** (subscription-based tools):
   - Claude Code: Run `claude` in container → Browser OAuth
   - GitHub Copilot: Run `copilot` → `/login` → Browser OAuth
   - Tokens stored in `~/.claude` and `~/.config/github-copilot` (mounted from host)

2. **API Keys** (API-based tools, optional):
   ```bash
   export OPENAI_API_KEY="sk-..."
   export GOOGLE_API_KEY="..."
   ```

#### Optional (For Git Operations)
3. **Git Configuration**:
   - Mount `~/.gitconfig` for user identity
   - Mount `~/.ssh` for SSH keys

#### Automatic (No User Action)
- AI CLIs are pre-installed and in PATH
- backlog.md CLI ready to use
- Python environment with uv, ruff, pytest

### 3.4 Documentation Requirements

Publish comprehensive documentation:

#### Docker Hub README
- Quick start (copy-paste devcontainer.json)
- Authentication guide (OAuth vs API keys)
- Tag reference (version strategy)
- Troubleshooting

#### GitHub Repository
- Full architecture (this document)
- Build instructions for contributors
- Release process
- Security policy

#### Examples Repository
Separate repo with working examples:
```
ai-coding-agents-examples/
├── python-project/
│   └── .devcontainer/devcontainer.json
├── node-project/
│   └── .devcontainer/devcontainer.json
├── monorepo/
│   └── .devcontainer/devcontainer.json
└── minimal-claude-only/
    └── .devcontainer/devcontainer.json
```

---

## 4. CI/CD Architecture

### 4.1 GitHub Actions Workflow

Automated build and publish pipeline:

```yaml
name: Build and Publish Devcontainer Images

on:
  push:
    branches:
      - main
    tags:
      - 'v*.*.*'
  pull_request:
    branches:
      - main
  schedule:
    # Weekly rebuild for security updates
    - cron: '0 6 * * 1'  # Every Monday at 6 AM UTC

permissions:
  contents: read
  packages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        variant: [runtime, minimal, python, node]

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up QEMU (for multi-platform)
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: jpoley/specflow-agents
          tags: |
            # Tag with variant suffix
            type=raw,value=${{ matrix.variant }},enable=${{ matrix.variant != 'runtime' }}
            type=raw,value=latest,enable=${{ matrix.variant == 'runtime' }}

            # Semantic versioning
            type=semver,pattern={{version}},suffix=-${{ matrix.variant }}
            type=semver,pattern={{major}}.{{minor}},suffix=-${{ matrix.variant }}
            type=semver,pattern={{major}},suffix=-${{ matrix.variant }}

            # Edge builds from main
            type=edge,branch=main,suffix=-${{ matrix.variant }}

            # SHA for traceability
            type=sha,prefix=,suffix=-${{ matrix.variant }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: .devcontainer/Dockerfile.hub
          target: ${{ matrix.variant }}
          platforms: linux/amd64,linux/arm64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Generate SBOM (Software Bill of Materials)
        uses: anchore/sbom-action@v0
        with:
          image: jpoley/specflow-agents:${{ matrix.variant }}
          format: spdx-json
          output-file: sbom-${{ matrix.variant }}.spdx.json

      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom-${{ matrix.variant }}
          path: sbom-${{ matrix.variant }}.spdx.json

  security-scan:
    runs-on: ubuntu-latest
    needs: build
    strategy:
      matrix:
        variant: [runtime, minimal, python, node]

    steps:
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: jpoley/specflow-agents:${{ matrix.variant }}
          format: 'sarif'
          output: 'trivy-results-${{ matrix.variant }}.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results-${{ matrix.variant }}.sarif'

      - name: Fail on HIGH/CRITICAL vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: jpoley/specflow-agents:${{ matrix.variant }}
          exit-code: '1'
          severity: 'CRITICAL,HIGH'

  test:
    runs-on: ubuntu-latest
    needs: build
    strategy:
      matrix:
        variant: [runtime, minimal, python, node]

    steps:
      - name: Test image functionality
        run: |
          docker run --rm jpoley/specflow-agents:${{ matrix.variant }} /bin/bash -c "
            command -v claude || exit 1
            command -v backlog || exit 1
            uv --version || exit 1
            python --version || exit 1
          "

      - name: Test variant-specific tools
        if: matrix.variant == 'python'
        run: |
          docker run --rm jpoley/specflow-agents:python /bin/bash -c "
            command -v ruff || exit 1
            command -v pytest || exit 1
          "

  publish-docs:
    runs-on: ubuntu-latest
    needs: [security-scan, test]
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Update Docker Hub description
        uses: peter-evans/dockerhub-description@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
          repository: jpoley/specflow-agents
          readme-filepath: .devcontainer/DOCKER_HUB_README.md
```

### 4.2 Trigger Strategy

| Trigger | Action | Rationale |
|---------|--------|-----------|
| **Push to main** | Build and push `edge` tag | Bleeding edge for early adopters |
| **Git tag `v*`** | Build and push semver tags | Official releases |
| **Pull request** | Build only (no push) | Verify changes don't break build |
| **Weekly schedule** | Rebuild all tags | Security updates from base image |
| **Manual dispatch** | Build specific variant | Ad-hoc testing |

### 4.3 Multi-Platform Build Strategy

Use Docker Buildx with QEMU for cross-platform builds:

```yaml
- name: Set up QEMU
  uses: docker/setup-qemu-action@v3

- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build multi-platform
  uses: docker/build-push-action@v5
  with:
    platforms: linux/amd64,linux/arm64
```

**Build time**: ~15-20 minutes for all platforms and variants

**Optimization**: Use GitHub Actions cache to speed up subsequent builds:
```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

### 4.4 Security Scanning Before Publish

Three-layer security validation:

#### Layer 1: Trivy Vulnerability Scan
```yaml
- name: Scan for vulnerabilities
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: jpoley/specflow-agents:latest
    severity: 'CRITICAL,HIGH'
    exit-code: '1'  # Fail build on HIGH/CRITICAL
```

#### Layer 2: SBOM Generation
```yaml
- name: Generate SBOM
  uses: anchore/sbom-action@v0
  with:
    image: jpoley/specflow-agents:latest
    format: spdx-json
```

#### Layer 3: GitHub Security Tab Integration
```yaml
- name: Upload security results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trivy-results.sarif
```

**Blocking policy**:
- **CRITICAL** vulnerabilities: Block publish, require fix
- **HIGH** vulnerabilities: Block publish, require fix or documented exception
- **MEDIUM/LOW** vulnerabilities: Allow publish, create issue for tracking

### 4.5 Release Process

Automated release workflow:

```bash
# 1. Create release branch
git checkout -b release/v1.2.3

# 2. Update version in metadata
# - .devcontainer/Dockerfile.hub (LABEL version)
# - CHANGELOG.md

# 3. Commit and tag
git commit -m "Release v1.2.3"
git tag -a v1.2.3 -m "Release v1.2.3"

# 4. Push tag (triggers CI/CD)
git push origin v1.2.3

# 5. CI/CD automatically:
#    - Builds all variants
#    - Runs security scans
#    - Publishes to Docker Hub
#    - Creates GitHub release with SBOM
```

**Manual verification**:
```bash
# Pull and test new release
docker pull jpoley/specflow-agents:1.2.3
docker run --rm -it jpoley/specflow-agents:1.2.3 bash
$ claude --version
$ backlog --version
```

---

## 5. Architecture Decision Records (ADRs)

### ADR-001: Base Image Selection

**Status**: Accepted

**Context**:
We need a base image that:
- Supports Python 3.11+
- Is trusted and maintained
- Works on multiple architectures (amd64, arm64)
- Has minimal security vulnerabilities
- Is widely adopted in the devcontainer community

**Alternatives considered**:
1. **Alpine Linux** (`python:3.11-alpine`)
   - **Pros**: Smallest size (~50MB), minimal attack surface
   - **Cons**: musl libc compatibility issues, missing packages, harder debugging
   - **Why rejected**: Too many compatibility issues with AI CLIs

2. **Ubuntu** (`ubuntu:22.04` + manual Python install)
   - **Pros**: Familiar, comprehensive package repository
   - **Cons**: Larger size, not optimized for containers, more configuration needed
   - **Why rejected**: More work than devcontainer base, no clear benefit

3. **Official Python** (`python:3.11-slim-bullseye`)
   - **Pros**: Official, well-maintained, smaller than full Python image
   - **Cons**: Not devcontainer-optimized, missing vscode user and tooling
   - **Why rejected**: Requires recreating devcontainer features

4. **Microsoft Devcontainer Python** (`mcr.microsoft.com/devcontainers/python:3.11-bullseye`) **SELECTED**
   - **Pros**: Purpose-built for VS Code, includes vscode user, git, zsh, multi-arch
   - **Cons**: Larger size (~500MB)
   - **Why chosen**: Best balance of features, compatibility, and maintenance

**Decision**: Use `mcr.microsoft.com/devcontainers/python:3.11-bullseye`

**Consequences**:
- **Positive**: Minimal configuration needed, excellent compatibility, trusted source
- **Negative**: Larger image size (acceptable for dev images)
- **Neutral**: Tied to Microsoft's devcontainer ecosystem (but it's open-source)

### ADR-002: Pre-installed vs Runtime Tools

**Status**: Accepted

**Context**:
Should AI CLIs be pre-installed in the image or installed at runtime (postCreateCommand)?

**Alternatives considered**:
1. **Runtime installation** (current jp-spec-kit approach)
   - **Pros**: Smaller image, always latest versions
   - **Cons**: 2-5 minute startup, network dependency, inconsistent across rebuilds
   - **Why rejected**: Poor UX, defeats purpose of reusable image

2. **Pre-installed in image** **SELECTED**
   - **Pros**: 30-second startup, offline capable (after initial pull), version-locked
   - **Cons**: Larger image, version updates require image rebuild
   - **Why chosen**: Much better UX, reproducibility, resilience

**Decision**: Pre-install AI CLIs in the Docker image

**Consequences**:
- **Positive**: Dramatic startup improvement, guaranteed versions, offline capability
- **Negative**: Image size ~1.2GB (acceptable), must rebuild for updates
- **Neutral**: Tagging strategy becomes critical for version management

### ADR-003: Image Variant Strategy

**Status**: Accepted

**Context**:
Should we publish one monolithic image or multiple variants?

**Alternatives considered**:
1. **Single monolithic image** (everything included)
   - **Pros**: Simplest to maintain, users don't need to choose
   - **Cons**: Largest size, includes tools users may not need
   - **Why rejected**: Wasteful for users who only need Claude

2. **Multiple variants** (`full`, `minimal`, `python`, `node`) **SELECTED**
   - **Pros**: Users choose optimal size, better caching, specialized workflows
   - **Cons**: More builds, more testing, version matrix complexity
   - **Why chosen**: Better user experience, professional offering

3. **Plugin-based composition**
   - **Pros**: Maximum flexibility, users compose exactly what they need
   - **Cons**: Complex UX, poor discoverability, integration testing nightmare
   - **Why rejected**: Over-engineered for current needs

**Decision**: Publish 4 variants: `latest` (full), `minimal`, `python`, `node`

**Consequences**:
- **Positive**: Optimized for different use cases, professional image catalog
- **Negative**: 4x CI/CD time, 4x storage on Docker Hub
- **Neutral**: Requires clear documentation of variant differences

### ADR-004: Credential Management Strategy

**Status**: Accepted

**Context**:
How should users provide credentials (API keys, OAuth tokens, SSH keys) to the container?

**Alternatives considered**:
1. **Environment variables only**
   - **Pros**: Standard Docker pattern, works in CI/CD
   - **Cons**: Doesn't work for OAuth tokens (files), manual token refresh
   - **Why rejected**: Claude Code and Copilot use OAuth (file-based)

2. **Volume mounts from host** **SELECTED**
   - **Pros**: OAuth tokens persist, standard devcontainer pattern, secure
   - **Cons**: Requires user to configure mounts, doesn't work in CI/CD
   - **Why chosen**: Required for OAuth-based CLIs, best security practice

3. **Secrets in image**
   - **Pros**: Zero user configuration
   - **Cons**: MASSIVE security risk, leaks credentials, violates best practices
   - **Why rejected**: Unacceptable security risk

**Decision**: Use volume mounts for credentials, environment variables for API keys

**Consequences**:
- **Positive**: Secure, supports OAuth, tokens persist across rebuilds
- **Negative**: Users must configure mounts (mitigated by templates)
- **Neutral**: CI/CD needs separate credential strategy (environment variables)

### ADR-005: Devcontainer Feature vs Direct Image

**Status**: Proposed (Phased Approach)

**Context**:
Should users reference the Docker image directly or use a devcontainer feature?

**Alternatives considered**:
1. **Direct image reference only**
   - **Pros**: Simple, obvious, one artifact to maintain
   - **Cons**: User must configure mounts manually
   - **Why rejected as sole solution**: Not best UX

2. **Devcontainer feature only**
   - **Pros**: Best UX, automatic configuration, composable
   - **Cons**: Two repos to maintain, more complex
   - **Why rejected as first step**: Delays initial release

3. **Both (phased approach)** **SELECTED**
   - **Phase 1**: Publish Docker image for immediate adoption
   - **Phase 2**: Publish devcontainer feature for best UX
   - **Why chosen**: Fastest time-to-value, migrate to better UX later

**Decision**: Publish Docker image first, devcontainer feature in Phase 2

**Consequences**:
- **Positive**: Quick release, easy migration path, eventual best UX
- **Negative**: Initial UX requires manual mount configuration
- **Neutral**: Two artifacts to maintain long-term (but both valuable)

---

## 6. Implementation Tasks (Backlog)

**Priority**: High
**Labels**: `infrastructure`, `devcontainer`, `docker`

### Task 1: Create Dockerfile.hub for Docker Hub Publishing
**Description**: Create multi-stage Dockerfile optimized for Docker Hub distribution with all AI CLIs pre-installed.

**Acceptance Criteria**:
- [ ] Dockerfile builds successfully for all variants (runtime, minimal, python, node)
- [ ] Multi-arch builds work (amd64, arm64)
- [ ] Layer caching optimized (base layers rarely change)
- [ ] All AI CLIs verified installed: `claude`, `copilot`, `codex`, `gemini`, `backlog`
- [ ] Image size < 1.5GB for full variant, < 900MB for minimal
- [ ] Health check verifies critical tools available

**Dependencies**: None

---

### Task 2: Create GitHub Actions Workflow for Docker Hub Publishing
**Description**: Automated CI/CD pipeline to build, scan, and publish images to Docker Hub.

**Acceptance Criteria**:
- [ ] Workflow builds all 4 variants in matrix
- [ ] Multi-platform builds (amd64, arm64) working
- [ ] Semantic versioning tags automatically generated
- [ ] Trivy security scan blocks on HIGH/CRITICAL vulnerabilities
- [ ] SBOM generated and attached to releases
- [ ] Docker Hub README auto-updated on release
- [ ] Weekly rebuild scheduled for security updates

**Dependencies**: Task 1

---

### Task 3: Create User Documentation and Templates
**Description**: Comprehensive documentation for users to adopt the image.

**Acceptance Criteria**:
- [ ] Docker Hub README with quick start
- [ ] Template devcontainer.json for users to copy
- [ ] Authentication guide (OAuth vs API keys)
- [ ] Troubleshooting section
- [ ] Examples repository with working samples (Python, Node, minimal)
- [ ] Migration guide from runtime install to pre-baked image

**Dependencies**: Task 1

---

### Task 4: Security Scanning and Compliance
**Description**: Implement security scanning and compliance validation.

**Acceptance Criteria**:
- [ ] Trivy vulnerability scanning in CI/CD
- [ ] SBOM generation (SPDX format)
- [ ] GitHub Security tab integration
- [ ] CRITICAL/HIGH vulnerabilities block publish
- [ ] Security policy documented (vulnerability response SLA)
- [ ] Dependabot enabled for base image updates

**Dependencies**: Task 2

---

### Task 5: Testing and Validation
**Description**: Comprehensive testing across platforms and use cases.

**Acceptance Criteria**:
- [ ] Image works on Ubuntu 22.04 (amd64)
- [ ] Image works on macOS Apple Silicon (arm64)
- [ ] Image works on macOS Intel (amd64)
- [ ] Image works on Windows + WSL2
- [ ] All AI CLIs functional (authentication tested)
- [ ] backlog.md integration working
- [ ] Performance benchmarked (startup time, image pull time)

**Dependencies**: Task 1, Task 2

---

### Task 6: Publish Phase 1 Release (v1.0.0)
**Description**: Publish first stable release to Docker Hub.

**Acceptance Criteria**:
- [ ] All variants published to `jpoley/specflow-agents`
- [ ] Tags: `latest`, `1.0.0`, `1.0`, `1`, `minimal`, `python`, `node`
- [ ] Docker Hub README published
- [ ] GitHub release created with SBOM
- [ ] Examples repository public and documented
- [ ] Announcement blog post / README updated in jp-spec-kit

**Dependencies**: Task 3, Task 4, Task 5

---

### Task 7: (Future) Devcontainer Feature for Best UX
**Description**: Create devcontainer feature for one-line adoption.

**Acceptance Criteria**:
- [ ] Feature repository created (`devcontainer-features`)
- [ ] Feature auto-configures credential mounts
- [ ] Feature published to GHCR
- [ ] Feature tested with example projects
- [ ] Documentation updated to recommend feature over direct image

**Dependencies**: Task 6 (Phase 1 released)

---

## 7. Success Metrics

Track adoption and effectiveness:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Docker Hub pulls | 100/month by Month 3 | Docker Hub analytics |
| GitHub stars | 50 by Month 6 | GitHub repo |
| Adoption in jp-spec-kit projects | 100% | All jp-spec-kit projects use image |
| Container startup time | < 30 seconds | CI/CD logs |
| Image pull time | < 2 minutes on 100Mbps | Test on fresh cache |
| Security scan pass rate | 100% (no HIGH/CRITICAL) | CI/CD metrics |
| User-reported issues | < 5/month | GitHub issues |

---

## 8. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **npm registry outage during build** | Low | High | Cache npm packages in image layers, offline fallback |
| **Base image vulnerability** | Medium | High | Weekly rebuilds, Dependabot alerts, automated patching |
| **AI CLI breaking changes** | Medium | Medium | Version pin in Dockerfile, test before updating |
| **Docker Hub rate limits** | Low | Medium | Authenticate pulls, consider GHCR mirror |
| **Large image size adoption barrier** | Medium | Low | Provide minimal variant, document size trade-offs |
| **Multi-arch build failures** | Low | Medium | Test on real hardware, QEMU fallback |

---

## 9. Future Enhancements

**Phase 2** (Post-v1.0.0):
- Devcontainer feature for one-line adoption
- GitHub Container Registry (GHCR) mirror for better rate limits
- Automated tool version updates (Dependabot-style)
- Image scanning dashboard (public vulnerability reports)

**Phase 3** (Advanced):
- Specialized variants (Rust, Go, Java)
- Pre-configured MCP servers (beyond backlog.md)
- Integration with Claude Projects API
- Self-hosted registry support for enterprises

---

## 10. References

- [VS Code Devcontainers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Docker Hub Automated Builds](https://docs.docker.com/docker-hub/builds/)
- [Devcontainer Features Specification](https://containers.dev/implementors/features/)
- [SBOM with Syft/Anchore](https://github.com/anchore/sbom-action)
- [Trivy Vulnerability Scanner](https://aquasecurity.github.io/trivy/)
- [Current jp-spec-kit devcontainer](../../.devcontainer/)

---

## Appendix A: Dockerfile.hub (Full Implementation)

See **Section 1.2** for complete multi-stage Dockerfile with optimal layer caching.

## Appendix B: Example User Projects

**Python Data Science Project**:
```json
{
  "name": "Data Science Project",
  "image": "jpoley/specflow-agents:python",
  "mounts": ["..."],
  "postCreateCommand": "pip install -r requirements.txt"
}
```

**Node.js API Project**:
```json
{
  "name": "API Server",
  "image": "jpoley/specflow-agents:node",
  "mounts": ["..."],
  "postCreateCommand": "npm install"
}
```

**Minimal Claude-Only Project**:
```json
{
  "name": "Documentation Project",
  "image": "jpoley/specflow-agents:minimal",
  "mounts": ["..."],
  "postCreateCommand": "echo 'Ready for AI-assisted writing'"
}
```

---

**Document Version**: 1.0
**Last Updated**: 2025-12-08
**Next Review**: After Phase 1 implementation
