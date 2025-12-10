# Docker Hub Devcontainer Architecture

## Overview

This document describes the architecture for publishing the JP Spec Kit devcontainer to Docker Hub as `jpoley/specflow-agents`, enabling reuse across any project.

## Architecture Decision Records

### ADR-001: Docker Hub as Distribution Registry

**Status**: Accepted

**Context**: Need to distribute the devcontainer image for easy adoption by external projects.

**Decision**: Use Docker Hub (`docker.io/jpoley/specflow-agents`) as the primary registry.

**Consequences**:
- Familiar pull experience for developers
- Free tier supports public images
- Requires Docker Hub account and access token for CI/CD

### ADR-002: Multi-Platform Build Strategy

**Status**: Accepted

**Context**: Developers use both Intel/AMD (amd64) and Apple Silicon (arm64) machines.

**Decision**: Build multi-platform images using `docker buildx` with QEMU emulation.

**Consequences**:
- Supports both amd64 and arm64 architectures
- Longer build times due to cross-compilation
- Manifest lists enable automatic platform selection

### ADR-003: Tag Strategy

**Status**: Accepted

**Context**: Need versioning strategy that supports both latest and specific versions.

**Decision**: Use three tag types:
- `latest` - Always points to latest main branch build
- `sha-<commit>` - Specific commit for reproducibility
- `<branch>` - Branch name for development builds

**Consequences**:
- Users can pin to specific commits for reproducibility
- Latest tag provides easy adoption
- Branch tags enable testing pre-release builds

### ADR-004: AI CLI Installation Strategy

**Status**: Accepted

**Context**: AI coding CLIs may fail to install due to regional restrictions or package availability.

**Decision**: Use best-effort installation with `|| echo "skipped"` fallback.

**Consequences**:
- Build never fails due to optional tools
- Users may need to manually install unavailable tools
- Image always builds successfully

### ADR-005: Security Scanning Integration

**Status**: Accepted

**Context**: Need to identify vulnerabilities in the published image.

**Decision**: Integrate Trivy scanner in CI/CD with SARIF output to GitHub Security.

**Consequences**:
- Automated vulnerability detection
- Results visible in GitHub Security tab
- Non-blocking (continue-on-error) to prevent build failures

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Hub Registry                       │
│                  jpoley/specflow-agents                      │
├─────────────────────────────────────────────────────────────┤
│  Tags: latest, sha-<commit>, main                           │
│  Platforms: linux/amd64, linux/arm64                        │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ push
                              │
┌─────────────────────────────────────────────────────────────┐
│                   GitHub Actions CI/CD                       │
│               .github/workflows/docker-publish.yml           │
├─────────────────────────────────────────────────────────────┤
│  Triggers: push to main (Dockerfile changes), manual         │
│  Jobs: build-and-push, verify                               │
│  Security: Trivy scan → GitHub Security                      │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ build
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Source Files                             │
│                  .devcontainer/Dockerfile                    │
├─────────────────────────────────────────────────────────────┤
│  Base: mcr.microsoft.com/devcontainers/python:3.11-bullseye │
│  + Node.js 20 + pnpm                                        │
│  + GitHub CLI                                                │
│  + uv (Python package manager)                              │
│  + AI CLIs (Claude Code, Codex, Gemini, GitHub Copilot)     │
│  + backlog.md                                                │
└─────────────────────────────────────────────────────────────┘
```

## User Adoption Flow

```
User Project                        Docker Hub
    │                                   │
    │ 1. Copy template                  │
    │    devcontainer.json              │
    ▼                                   │
.devcontainer/                          │
devcontainer.json ─────────────────────►│
    │                     2. Pull image │
    │◄──────────────────────────────────│
    │   jpoley/specflow-agents:latest   │
    │                                   │
    ▼                                   │
Container starts with:                  │
- All AI CLIs pre-installed             │
- Development tools ready               │
- Shell configured                      │
```

## Required Secrets

| Secret | Purpose | Where to Create |
|--------|---------|-----------------|
| `DOCKERHUB_USER` | Docker Hub login | GitHub repo → Settings → Secrets |
| `DOCKERHUB_SECRET` | Docker Hub access token | Docker Hub → Account Settings → Security |

## File Structure

```
jp-spec-kit/
├── .devcontainer/
│   ├── Dockerfile              # Image definition
│   ├── devcontainer.json       # Local development config
│   └── post-create.sh          # Local setup script
├── .github/workflows/
│   └── docker-publish.yml      # CI/CD pipeline
├── templates/devcontainer/
│   ├── devcontainer.json       # User template
│   └── README.md               # Adoption guide
└── docs/platform/
    └── dockerhub-devcontainer-architecture.md  # This file
```

## Maintenance

### Updating the Image

1. Modify `.devcontainer/Dockerfile`
2. Push to main branch
3. CI/CD automatically builds and publishes

### Manual Rebuild

Use GitHub Actions → Docker Publish → Run workflow → force_build: true

### Monitoring

- Docker Hub: View pull counts and image details
- GitHub Security: Review Trivy scan results
- GitHub Actions: Monitor build status
