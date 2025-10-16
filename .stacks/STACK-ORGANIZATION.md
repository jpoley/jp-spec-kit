# Stack Organization

## Overview

Each stack in this directory is a **complete, self-contained package** that includes everything needed for that technology stack:

- Stack documentation
- CI/CD workflows (Outer Loop implementation)
- Example configurations
- Deployment manifests
- Testing strategies

## Directory Structure

```
.stacks/
├── react-frontend-go-backend/
│   ├── README.md                    # Stack documentation
│   ├── workflows/
│   │   └── ci-cd.yml                # Complete GitHub Actions workflow
│   └── examples/
│       ├── Dockerfile.frontend
│       ├── Dockerfile.backend
│       ├── docker-compose.yml
│       └── k8s/                     # Kubernetes manifests
│
├── react-frontend-python-backend/
│   ├── README.md
│   ├── workflows/
│   │   └── ci-cd.yml
│   └── examples/
│
├── full-stack-react-typescript/
│   ├── README.md
│   ├── workflows/
│   │   └── ci-cd.yml
│   └── examples/
│
├── mobile-frontend-go-backend/
│   ├── README.md
│   ├── workflows/
│   │   └── ci-cd.yml
│   └── examples/
│
├── mobile-frontend-python-backend/
│   ├── README.md
│   ├── workflows/
│   │   └── ci-cd.yml
│   └── examples/
│
├── data-ml-pipeline-python/
│   ├── README.md
│   ├── workflows/
│   │   └── ci-cd.yml
│   └── examples/
│
├── chrome-extension-typescript/
│   ├── README.md
│   ├── workflows/
│   │   └── ci-cd.yml
│   └── examples/
│
├── vscode-extension-typescript/
│   ├── README.md
│   ├── workflows/
│   │   └── ci-cd.yml
│   └── examples/
│
└── tray-app-cross-platform/
    ├── README.md
    ├── workflows/
    │   └── ci-cd.yml
    └── examples/
```

## Workflow Implementation

### Complete Implementation

**react-frontend-go-backend/workflows/ci-cd.yml** - Complete, production-ready workflow that demonstrates:

✅ **Inner Loop Validation**
- Frontend: Lint, TypeCheck, Unit Tests
- Backend: Lint, Unit Tests, Integration Tests with Postgres + Redis

✅ **Outer Loop Security** (task-004.md requirements)
- SAST with Semgrep
- SCA with Trivy
- Secret scanning with TruffleHog
- Container image scanning

✅ **Build Once, Promote Everywhere**
- Build artifacts once in dev/CI
- Generate SBOM for all artifacts
- Sign artifacts with Cosign
- Promote same immutable artifacts to staging and production

✅ **CD Promotion Workflow**
- Automatic deployment to staging on main branch
- Manual approval required for production
- Health checks and smoke tests
- Kubernetes deployment with rollout status verification

### Reference Templates

All other stacks have reference workflow templates in their `workflows/` directory that need to be:
1. Adapted for stack-specific build tools
2. Configured for stack-specific security scans
3. Updated for stack-specific deployment targets

## How to Use

### For New Projects

1. **Select your stack** from the available options
2. **Copy the stack directory** to your project
3. **Copy workflow** from `<stack>/workflows/ci-cd.yml` to `.github/workflows/`
4. **Customize** the workflow for your specific needs:
   - Update repository names
   - Configure secrets (KUBECONFIG, etc.)
   - Adjust deployment targets
   - Add stack-specific steps

### For Existing Projects

1. **Review** the stack's README.md for architecture guidance
2. **Reference** the workflow in `workflows/ci-cd.yml`
3. **Adapt** security scanning steps for your dependencies
4. **Implement** the build-once-promote-everywhere pattern
5. **Configure** environments in GitHub (staging, production with approvals)

## Outer Loop Requirements (task-004.md)

Each workflow implements the outer loop requirements:

### ✅ MUST HAVES

1. **Complete GitHub Actions CI/CD Process**
   - Build and test all components
   - Security scanning (SAST, DAST, SCA)
   - Generate SBOM
   - Sign artifacts

2. **CD Promotion with Testing + Approvals**
   - Automated deployment to staging
   - Manual approval for production
   - Health checks at each stage
   - Rollback capability

3. **Build Once, Promote Everywhere**
   - Single build in dev/CI
   - Immutable artifacts promoted to all environments
   - Content-addressable artifact identification (digest)
   - No rebuilding for different environments

4. **Stack-Specific Validation**
   - Language-specific linting and testing
   - Framework-specific security scans
   - Platform-specific deployment validation

## Security Best Practices

All workflows follow GitHub Actions security guidelines:

- **No command injection**: All dynamic values use environment variables
- **No untrusted input** in run commands
- **Minimal permissions**: OIDC tokens where possible
- **Secret scanning**: Automated in every build
- **Signed artifacts**: Cosign signatures for verification
- **SBOM generation**: Software Bill of Materials for supply chain security

## Next Steps

To complete workflow implementation for all stacks:

1. Review the complete `react-frontend-go-backend/workflows/ci-cd.yml`
2. Adapt the pattern for each remaining stack's specific technology
3. Add stack-specific build and test commands
4. Configure appropriate security scans
5. Update deployment targets (npm, app stores, k8s, etc.)
6. Test workflows in CI/CD environment
7. Document any stack-specific requirements

## References

- [Task 004](../../TODO/task-004.md) - Original requirements
- [Inner Loop Principles](../../docs/reference/inner-loop.md)
- [Outer Loop Principles](../../docs/reference/outer-loop.md)
- [Agent Loop Classification](../../docs/reference/agent-loop-classification.md)
- [GitHub Actions Security](https://github.blog/security/vulnerability-research/how-to-catch-github-actions-workflow-injections-before-attackers-do/)
