# Galway Docker Specifications

**Status**: Platform Design
**Owner**: Platform Engineer
**Last Updated**: 2025-12-04

## Executive Summary

This document defines Docker containerization standards for galway host tasks, focusing on security, reproducibility, and build performance.

## Container Strategy

### When to Containerize

**Containerize** these components:
- **Security scanner** (task-254): Reproducible scan environment
- **CI/CD tooling**: Consistent build environment across runners
- **Agent Updates Collector** (task-296, if Rust service exists): Isolated runtime

**Don't containerize** these:
- **CLI tools** (specify-cli): Python package via pip/uv
- **Git hooks**: Native bash scripts
- **Local dev workflows**: Direct uv execution faster

## Base Image Selection

### Python Services

**Recommended Base**: `python:3.11-slim`

**Rationale**:
- **Size**: ~45MB vs. 300MB+ for full Python image
- **Security**: Minimal attack surface, fewer CVEs
- **Performance**: Faster pull and startup times
- **Official**: Maintained by Docker + Python community

**Alternative**: `python:3.11-alpine`
- **Pros**: Even smaller (~15MB)
- **Cons**: musl libc incompatibilities, harder to build native extensions

**Decision**: Use `python:3.11-slim` for compatibility and simplicity

### Rust Services (if applicable)

**Recommended Base**: `rust:1.75-slim` (build) → `debian:bookworm-slim` (runtime)

**Multi-stage Build**:
```dockerfile
FROM rust:1.75-slim as builder
# Build static binary

FROM debian:bookworm-slim
# Copy binary only
```

## Dockerfile Best Practices

### Multi-stage Builds

**Pattern**:
```dockerfile
# Stage 1: Build environment
FROM python:3.11-slim as builder
WORKDIR /build
# Install build dependencies, compile, etc.

# Stage 2: Runtime environment
FROM python:3.11-slim
WORKDIR /app
# Copy only runtime artifacts from builder
COPY --from=builder /build/install /usr/local
```

**Benefits**:
- **Size**: Runtime image excludes build tools (gcc, make, headers)
- **Security**: Fewer packages = fewer vulnerabilities
- **Clarity**: Separation of build vs. runtime concerns

### Layer Optimization

**Good** (cached layers):
```dockerfile
# 1. Base image (rarely changes)
FROM python:3.11-slim

# 2. System dependencies (rarely change)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 3. Python dependencies (change occasionally)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Application code (changes frequently)
COPY src/ /app/src/
```

**Bad** (uncached layers):
```dockerfile
FROM python:3.11-slim
COPY . /app/  # Everything in one layer - no caching!
RUN apt-get update && pip install -r requirements.txt
```

### Security Hardening

**Non-root User**:
```dockerfile
# Create dedicated user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser
```

**Read-only Filesystem**:
```dockerfile
# Mark as read-only where possible
VOLUME /tmp
RUN chmod -R 555 /app  # Read + execute only
```

**Minimal Privileges**:
```dockerfile
# Drop all capabilities except required
RUN setcap cap_net_bind_service=+ep /usr/local/bin/server
```

**No Secrets in Images**:
```dockerfile
# ❌ BAD
ENV API_KEY=secret123

# ✅ GOOD
# Pass secrets at runtime via:
# - Environment variables: docker run -e API_KEY=...
# - Secrets management: docker secret create
# - Mounted files: docker run -v /secure/api-key:/etc/api-key:ro
```

## Security Scanner Image (task-254)

**Location**: `docker/Dockerfile.security-scanner`

**Design** (see full implementation in `galway-devsecops-design.md`):
```dockerfile
FROM python:3.11-slim as builder
# Install security tools: semgrep, bandit, pip-audit, cyclonedx-bom

FROM python:3.11-slim
# Copy tools, add non-root user, configure entrypoint
```

**Usage**:
```bash
docker run --rm \
  -v $(pwd):/scan:ro \
  -v $(pwd)/results:/scan/results:rw \
  ghcr.io/jpoley/jp-spec-kit-security:0.0.250
```

**Build and Publish**:
```yaml
# .github/workflows/build-security-scanner.yml
name: Build Security Scanner Image

on:
  push:
    branches: [main]
    paths:
      - 'docker/Dockerfile.security-scanner'
      - 'scripts/security/**'

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/jpoley/jp-spec-kit-security
          tags: |
            type=semver,pattern={{version}}
            type=sha,prefix={{branch}}-
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: docker/Dockerfile.security-scanner
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64
```

## Agent Updates Collector Image (task-296, if exists)

**Rust Service Container** (`src/agent-updates-collector/Dockerfile`):
```dockerfile
# Stage 1: Build
FROM rust:1.75-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Cache dependencies separately from source
COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release
RUN rm -rf src

# Build actual source
COPY src ./src
RUN touch src/main.rs  # Force rebuild
RUN cargo build --release

# Stage 2: Runtime
FROM debian:bookworm-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 agent-collector

WORKDIR /app

# Copy binary from builder
COPY --from=builder /build/target/release/agent-updates-collector /usr/local/bin/

# Copy configuration templates
COPY config/ /app/config/

# Set ownership
RUN chown -R agent-collector:agent-collector /app

USER agent-collector

# Expose ports
EXPOSE 8080  # HTTP API
EXPOSE 9090  # Metrics

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["/usr/local/bin/agent-updates-collector", "health"]

ENTRYPOINT ["/usr/local/bin/agent-updates-collector"]
CMD ["serve"]
```

**Build Script**:
```bash
#!/bin/bash
# scripts/docker/build-agent-collector.sh

set -euo pipefail

VERSION=${VERSION:-0.1.0}
REGISTRY=${REGISTRY:-ghcr.io/jpoley}

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag "$REGISTRY/agent-updates-collector:$VERSION" \
  --tag "$REGISTRY/agent-updates-collector:latest" \
  --push \
  -f src/agent-updates-collector/Dockerfile \
  src/agent-updates-collector/
```

## CI/CD Build Environment Image

**Purpose**: Consistent CI environment for all runners

**Image** (`docker/Dockerfile.ci`):
```dockerfile
FROM ubuntu:22.04

# Install CI dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    jq \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Pre-install common tools
RUN pip install --no-cache-dir \
    ruff \
    pytest \
    pytest-cov

# Configure git
RUN git config --global user.name "CI Bot" && \
    git config --global user.email "ci@peregrinesummit.com"

WORKDIR /workspace
```

## Image Tagging Strategy

### Semantic Versioning

**Format**: `MAJOR.MINOR.PATCH`

**Examples**:
- `jp-spec-kit-security:0.0.250` - Specific version
- `jp-spec-kit-security:0.0` - Latest patch (e.g., 0.0.250)
- `jp-spec-kit-security:0` - Latest minor (e.g., 0.0.x)
- `jp-spec-kit-security:latest` - Bleeding edge (main branch)

### Git-based Tags

**Commit SHA**:
```
jp-spec-kit-security:main-abc1234  # Branch + short SHA
```

**Branch Name**:
```
jp-spec-kit-security:feature-new-scanner  # Branch name
```

### Immutable References (Production)

**Use SHA256 Digests**:
```yaml
# ✅ GOOD - Immutable reference
image: ghcr.io/jpoley/jp-spec-kit-security@sha256:abc123...

# ❌ BAD - Mutable tag
image: ghcr.io/jpoley/jp-spec-kit-security:latest
```

**How to Get Digest**:
```bash
docker inspect --format='{{index .RepoDigests 0}}' jp-spec-kit-security:0.0.250
# Output: ghcr.io/jpoley/jp-spec-kit-security@sha256:abc123...
```

## Registry Configuration

### GitHub Container Registry (GHCR)

**Authentication**:
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u jpoley --password-stdin
```

**Publish**:
```bash
docker tag jp-spec-kit-security:latest ghcr.io/jpoley/jp-spec-kit-security:0.0.250
docker push ghcr.io/jpoley/jp-spec-kit-security:0.0.250
```

**Public vs. Private**:
- **Public**: Security scanner (open-source project)
- **Private**: Proprietary services (if any)

**Configuration** (set in GitHub repo settings):
```
Settings → Packages → jp-spec-kit-security → Change visibility → Public
```

## Build Optimization

### BuildKit Cache

**Enable BuildKit**:
```bash
export DOCKER_BUILDKIT=1
```

**Cache Mounts**:
```dockerfile
# Cache pip downloads
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Cache cargo registry
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    cargo build --release
```

### Multi-platform Builds

**Buildx Setup**:
```bash
docker buildx create --name multiplatform --use
docker buildx inspect --bootstrap
```

**Build for Multiple Architectures**:
```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag ghcr.io/jpoley/jp-spec-kit-security:0.0.250 \
  --push \
  .
```

**Benefits**:
- Works on Apple Silicon (M1/M2) developers
- Works on ARM-based CI runners (cheaper)
- Future-proof for ARM server adoption

## Container Security

### Vulnerability Scanning

**Trivy Integration**:
```yaml
# .github/workflows/container-security.yml
- name: Scan image with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ghcr.io/jpoley/jp-spec-kit-security:${{ github.sha }}
    format: 'sarif'
    output: 'trivy-results.sarif'

- name: Upload Trivy results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: 'trivy-results.sarif'
```

**Fail on High/Critical**:
```yaml
- name: Scan and fail on vulnerabilities
  run: |
    trivy image \
      --severity HIGH,CRITICAL \
      --exit-code 1 \
      ghcr.io/jpoley/jp-spec-kit-security:${{ github.sha }}
```

### Image Signing (Cosign)

**Sign Image**:
```bash
# Generate key pair (one-time)
cosign generate-key-pair

# Sign image
cosign sign --key cosign.key ghcr.io/jpoley/jp-spec-kit-security@sha256:abc123...
```

**Verify Image**:
```bash
cosign verify --key cosign.pub ghcr.io/jpoley/jp-spec-kit-security@sha256:abc123...
```

**CI Integration**:
```yaml
- name: Sign image with Cosign
  env:
    COSIGN_PASSWORD: ${{ secrets.COSIGN_PASSWORD }}
  run: |
    cosign sign --key cosign.key \
      ghcr.io/jpoley/jp-spec-kit-security@${{ steps.push.outputs.digest }}
```

## Container Runtime Configuration

### Resource Limits

**CPU and Memory**:
```bash
docker run \
  --cpus=0.5 \
  --memory=512m \
  --memory-swap=512m \
  ghcr.io/jpoley/jp-spec-kit-security:0.0.250
```

**Docker Compose**:
```yaml
services:
  security-scanner:
    image: ghcr.io/jpoley/jp-spec-kit-security:0.0.250
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
```

### Security Options

**Read-only Root Filesystem**:
```bash
docker run --read-only \
  --tmpfs /tmp:rw,noexec,nosuid \
  ghcr.io/jpoley/jp-spec-kit-security:0.0.250
```

**Drop Capabilities**:
```bash
docker run \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  ghcr.io/jpoley/jp-spec-kit-security:0.0.250
```

**Seccomp Profile**:
```bash
docker run \
  --security-opt seccomp=seccomp-profile.json \
  ghcr.io/jpoley/jp-spec-kit-security:0.0.250
```

## Testing Containers

### Container Structure Tests

**Test Spec** (`test/container-structure-test.yaml`):
```yaml
schemaVersion: 2.0.0

fileExistenceTests:
  - name: 'Binary exists'
    path: '/usr/local/bin/semgrep'
    shouldExist: true
  - name: 'Config exists'
    path: '/app/config'
    shouldExist: true

commandTests:
  - name: 'Semgrep version'
    command: 'semgrep'
    args: ['--version']
    exitCode: 0
  - name: 'Bandit version'
    command: 'bandit'
    args: ['--version']
    exitCode: 0

metadataTest:
  labels:
    - key: 'org.opencontainers.image.title'
      value: 'JP Spec Kit Security Scanner'
```

**Run Tests**:
```bash
container-structure-test test \
  --image ghcr.io/jpoley/jp-spec-kit-security:0.0.250 \
  --config test/container-structure-test.yaml
```

## Docker Compose for Local Development

**Example** (`docker-compose.yml`):
```yaml
version: '3.8'

services:
  security-scanner:
    build:
      context: .
      dockerfile: docker/Dockerfile.security-scanner
    volumes:
      - ./:/scan:ro
      - ./results:/scan/results:rw
    environment:
      - SCAN_TYPE=full
      - DEBUG=true

  agent-collector:
    build:
      context: src/agent-updates-collector
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
      - "9090:9090"
    volumes:
      - agent-data:/app/data
    environment:
      - DATABASE_URL=sqlite:///app/data/agent-updates.db
      - LOG_LEVEL=debug

volumes:
  agent-data:
```

**Usage**:
```bash
docker-compose up -d          # Start services
docker-compose logs -f        # Follow logs
docker-compose down           # Stop and remove
```

## Success Metrics

**Build Performance**:
- **Build time**: < 3 minutes with cache, < 10 minutes cold
- **Image size**: < 100MB for Python services, < 50MB for Rust
- **Layer caching**: > 80% cache hit rate

**Security Posture**:
- **Critical CVEs**: 0 in production images
- **High CVEs**: < 5 in production images
- **Signed images**: 100% of production images

**Reliability**:
- **Build success rate**: > 99%
- **Image pull success rate**: > 99.9%

## Related Tasks

| Task ID | Title | Docker Integration |
|---------|-------|-------------------|
| task-254 | Security Scanner Docker | Main containerization target |
| task-296 | Agent Collector CI/CD | Rust service container |
| task-248 | Security Pipeline | Container-based scanning |

## Appendix: Dockerfile Checklist

**Pre-build**:
- [ ] Use official base images (python:3.11-slim, rust:1.75-slim)
- [ ] Pin exact versions of base images
- [ ] Use multi-stage builds to reduce size

**During build**:
- [ ] Layer dependencies before code (better caching)
- [ ] Clean up apt/yum caches (reduce size)
- [ ] Use --no-cache-dir for pip (reduce size)

**Post-build**:
- [ ] Create non-root user (security)
- [ ] Set appropriate file permissions (security)
- [ ] Add HEALTHCHECK instruction (reliability)
- [ ] Label image with metadata (maintainability)

**Testing**:
- [ ] Scan with Trivy (security)
- [ ] Run container-structure-tests (correctness)
- [ ] Test on both amd64 and arm64 (compatibility)

**Publishing**:
- [ ] Tag with semantic version (traceability)
- [ ] Sign with Cosign (integrity)
- [ ] Push to GHCR (availability)
