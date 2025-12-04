---
id: task-254
title: Build and Publish Security Scanner Docker Image
status: To Do
assignee:
  - '@muckross'
created_date: '2025-12-03 02:26'
updated_date: '2025-12-04 16:32'
labels:
  - 'workflow:Planned'
dependencies: []
priority: low
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create Docker image with Semgrep and specify-cli for air-gapped and highly controlled environments. Optimize for size (<200MB) and publish to GHCR.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create Dockerfile with Python 3.11, Semgrep, uv, specify-cli
- [ ] #2 Optimize image size (<200MB using slim base and multi-stage build)
- [ ] #3 Publish to GHCR (ghcr.io/yourusername/jpspeckit-security-scanner:version)
- [ ] #4 Add image usage to CI/CD pipeline as alternative scan method
- [ ] #5 Document usage for air-gapped environments in docs/platform/
- [ ] #6 Test image in isolated environment (no network access)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Implementation Plan: Build and Publish Security Scanner Docker Image

### Overview
Create an optimized Docker image containing Semgrep and specify-cli for air-gapped and highly controlled environments.

### Step-by-Step Implementation

#### Step 1: Create Dockerfile
**File**: `docker/security-scanner.Dockerfile`
**Duration**: 2 hours

1. Create multi-stage Dockerfile:
   ```dockerfile
   # Stage 1: Builder
   FROM python:3.11-slim as builder
   
   # Install build dependencies
   RUN apt-get update && apt-get install -y \
       git \
       curl \
       && rm -rf /var/lib/apt/lists/*
   
   # Install uv for faster Python installs
   RUN pip install --no-cache-dir uv
   
   # Install specify-cli and semgrep
   WORKDIR /build
   COPY pyproject.toml README.md ./
   COPY src ./src
   RUN uv pip install --system . semgrep==1.50.0
   
   # Stage 2: Runtime
   FROM python:3.11-slim
   
   LABEL org.opencontainers.image.title="JP Spec Kit Security Scanner"
   LABEL org.opencontainers.image.description="Security scanning tools for JP Spec Kit"
   LABEL org.opencontainers.image.version="1.0.0"
   LABEL org.opencontainers.image.source="https://github.com/yourusername/jp-spec-kit"
   
   # Install runtime dependencies
   RUN apt-get update && apt-get install -y \
       git \
       && rm -rf /var/lib/apt/lists/*
   
   # Copy installed packages from builder
   COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
   COPY --from=builder /usr/local/bin/specify /usr/local/bin/specify
   COPY --from=builder /usr/local/bin/semgrep /usr/local/bin/semgrep
   
   # Create working directory
   WORKDIR /src
   
   # Create non-root user
   RUN useradd -m -u 1000 scanner && chown -R scanner:scanner /src
   USER scanner
   
   # Health check
   HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
       CMD specify --version || exit 1
   
   # Default command
   ENTRYPOINT ["specify", "security", "scan"]
   CMD ["--help"]
   ```

2. Optimize image size:
   - Use slim base image
   - Multi-stage build to exclude build tools
   - Remove apt cache
   - Use .dockerignore for build context

#### Step 2: Create .dockerignore
**File**: `docker/.dockerignore`
**Duration**: 30 minutes

1. Exclude unnecessary files:
   ```
   # Development files
   .git
   .gitignore
   .venv
   __pycache__
   *.pyc
   *.pyo
   .pytest_cache
   .ruff_cache
   
   # Documentation
   docs/
   *.md
   
   # Tests
   tests/
   
   # Build artifacts
   dist/
   build/
   *.egg-info
   
   # IDE
   .vscode
   .idea
   
   # Large files
   *.log
   *.tar
   *.zip
   ```

#### Step 3: Build and Test Image Locally
**Duration**: 2 hours

1. Create build script:
   ```bash
   #!/bin/bash
   # scripts/bash/build-security-scanner-image.sh
   
   set -e
   
   VERSION=${1:-latest}
   IMAGE_NAME="jpspeckit/security-scanner"
   
   echo "Building security scanner Docker image v${VERSION}..."
   
   # Build image
   docker build \
     -f docker/security-scanner.Dockerfile \
     -t ${IMAGE_NAME}:${VERSION} \
     -t ${IMAGE_NAME}:latest \
     .
   
   # Show image size
   docker images ${IMAGE_NAME}:${VERSION}
   
   # Verify size target (<200MB)
   SIZE=$(docker images ${IMAGE_NAME}:${VERSION} --format "{{.Size}}")
   echo "Image size: ${SIZE}"
   
   # Test image
   echo "Testing image..."
   docker run --rm ${IMAGE_NAME}:${VERSION} --version
   
   echo "✅ Build complete: ${IMAGE_NAME}:${VERSION}"
   ```

2. Test image functionality:
   ```bash
   # Test 1: Help command
   docker run --rm jpspeckit/security-scanner:latest --help
   
   # Test 2: Scan current directory
   docker run --rm -v $(pwd):/src jpspeckit/security-scanner:latest
   
   # Test 3: Scan with specific flags
   docker run --rm -v $(pwd):/src jpspeckit/security-scanner:latest \
     --format json --output /src/results.json
   
   # Test 4: Check image size
   docker images jpspeckit/security-scanner:latest --format "{{.Size}}"
   # Target: <200MB
   ```

3. Verify image meets size target:
   - Baseline: python:3.11-slim ~125MB
   - With specify-cli + semgrep: target <200MB
   - If exceeds 200MB, investigate and optimize

#### Step 4: Create GitHub Actions Workflow for Image Build
**File**: `.github/workflows/build-security-image.yml`
**Duration**: 2 hours

1. Create workflow:
   ```yaml
   name: Build Security Scanner Image
   
   on:
     push:
       branches: [main]
       tags: ['v*']
     pull_request:
       branches: [main]
     workflow_dispatch:
   
   env:
     REGISTRY: ghcr.io
     IMAGE_NAME: ${{ github.repository }}/security-scanner
   
   jobs:
     build:
       runs-on: ubuntu-latest
       permissions:
         contents: read
         packages: write
       
       steps:
         - name: Checkout code
           uses: actions/checkout@v4
         
         - name: Set up Docker Buildx
           uses: docker/setup-buildx-action@v3
         
         - name: Log in to GHCR
           if: github.event_name != 'pull_request'
           uses: docker/login-action@v3
           with:
             registry: ${{ env.REGISTRY }}
             username: ${{ github.actor }}
             password: ${{ secrets.GITHUB_TOKEN }}
         
         - name: Extract metadata
           id: meta
           uses: docker/metadata-action@v5
           with:
             images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
             tags: |
               type=ref,event=branch
               type=ref,event=pr
               type=semver,pattern={{version}}
               type=semver,pattern={{major}}.{{minor}}
               type=sha
         
         - name: Build and push
           uses: docker/build-push-action@v5
           with:
             context: .
             file: docker/security-scanner.Dockerfile
             push: ${{ github.event_name != 'pull_request' }}
             tags: ${{ steps.meta.outputs.tags }}
             labels: ${{ steps.meta.outputs.labels }}
             cache-from: type=gha
             cache-to: type=gha,mode=max
         
         - name: Test image
           run: |
             docker run --rm ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:sha-${{ github.sha }} --version
   ```

2. Configure GHCR permissions:
   - Repository Settings → Actions → General
   - Workflow permissions: Read and write permissions

#### Step 5: Document Docker Image Usage
**File**: `docs/platform/security-scanner-docker.md`
**Duration**: 1 hour

1. Create documentation:
   ```markdown
   # Security Scanner Docker Image
   
   ## Quick Start
   
   Pull the latest image:
   ```bash
   docker pull ghcr.io/yourusername/jp-spec-kit/security-scanner:latest
   ```
   
   Scan a project:
   ```bash
   docker run --rm -v $(pwd):/src \
     ghcr.io/yourusername/jp-spec-kit/security-scanner:latest
   ```
   
   ## Usage
   
   ### Basic Scan
   ```bash
   docker run --rm -v /path/to/project:/src \
     ghcr.io/yourusername/jp-spec-kit/security-scanner:latest
   ```
   
   ### Custom Configuration
   ```bash
   docker run --rm \
     -v /path/to/project:/src \
     -v /path/to/.jpspec:/src/.jpspec \
     ghcr.io/yourusername/jp-spec-kit/security-scanner:latest \
     --policy .jpspec/security-policy.yml
   ```
   
   ### Save Results
   ```bash
   docker run --rm -v $(pwd):/src \
     ghcr.io/yourusername/jp-spec-kit/security-scanner:latest \
     --format sarif --output /src/results.sarif
   ```
   
   ## CI/CD Integration
   
   ### GitHub Actions
   ```yaml
   - name: Security Scan
     run: |
       docker run --rm -v ${{ github.workspace }}:/src \
         ghcr.io/yourusername/jp-spec-kit/security-scanner:latest \
         --fail-on critical,high
   ```
   
   ### GitLab CI
   ```yaml
   security-scan:
     image: ghcr.io/yourusername/jp-spec-kit/security-scanner:latest
     script:
       - specify security scan --fail-on critical,high
   ```
   
   ## Air-Gapped Environments
   
   1. Pull image on internet-connected machine:
   ```bash
   docker pull ghcr.io/yourusername/jp-spec-kit/security-scanner:latest
   docker save -o security-scanner.tar ghcr.io/yourusername/jp-spec-kit/security-scanner:latest
   ```
   
   2. Transfer `security-scanner.tar` to air-gapped environment
   
   3. Load image:
   ```bash
   docker load -i security-scanner.tar
   ```
   
   4. Use normally:
   ```bash
   docker run --rm -v $(pwd):/src ghcr.io/yourusername/jp-spec-kit/security-scanner:latest
   ```
   ```

2. Add troubleshooting section
3. Add version compatibility matrix

#### Step 6: Test in Isolated Environment
**Duration**: 2 hours

1. **Air-gapped test**:
   - Save image to tar file
   - Spin up VM with no internet
   - Load image
   - Run scan
   - Verify works without network access

2. **Permission test**:
   - Test as non-root user
   - Test volume mount permissions
   - Test output file ownership

3. **CI/CD test**:
   - Add workflow using Docker image to test project
   - Verify results identical to local install
   - Measure performance difference

### Dependencies
- specify-cli package ready for installation
- Semgrep version pinned in requirements
- GHCR access configured

### Testing Checklist
- [ ] Image builds successfully
- [ ] Image size <200MB
- [ ] specify-cli works in container
- [ ] semgrep works in container
- [ ] Volume mounts work correctly
- [ ] Scan produces valid results
- [ ] Published to GHCR successfully
- [ ] Works in air-gapped environment
- [ ] Documentation is clear and accurate

### Estimated Effort
**Total**: 11 hours (1.4 days)
<!-- SECTION:PLAN:END -->
