# GitHub Actions CI/CD Templates

This directory contains GitHub Actions workflow templates for different tech stacks. These templates implement the **Outer Loop** principles defined in `docs/reference/outer-loop.md`.

## Purpose

These templates can be used to generate CI/CD pipelines specific to the project's tech stack. Each template follows the outer-loop principles:

- **Build once** in dev/CI, promote everywhere else
- **SBOM generation** for supply chain security
- **Artifact attestation** (SLSA provenance)
- **Security scanning** (SAST, DAST, SCA)
- **Environment-agnostic artifacts** with externalized configuration
- **Automated deployment** with GitOps

## Available Templates

### CI/CD Pipeline Templates

| Stack | Template File | Description | Build Tool |
|-------|--------------|-------------|------------|
| **Node.js/TypeScript** | `nodejs-ci-cd.yml` | npm/yarn/pnpm, TypeScript, React/Next.js, etc. | npm/yarn/pnpm |
| **Python** | `python-ci-cd.yml` | pip/poetry/uv, Django/Flask/FastAPI, etc. | pip/poetry/uv |
| **.NET** | `dotnet-ci-cd.yml` | C#, ASP.NET Core, Blazor, etc. | dotnet CLI |
| **Go** | `go-ci-cd.yml` | Go applications and services | **Mage** |

### Security Scanning Templates

| Template | Description | Use Case |
|----------|-------------|----------|
| `security-scan.yml` | Reusable security scanning workflow | Standard scanning for most projects |
| `security.yml` | Entry point for security scans | Triggers scans on PRs and schedule |
| `security-parallel.yml` | Parallel component scanning | Large codebases (>500K LOC) for 3x speedup |
| `security-config.yml` | Security configuration file | Configure scan behavior, severity thresholds |

**Quick Start (Security):**
```bash
# Copy templates to your project
cp templates/github-actions/security-scan.yml .github/workflows/
cp templates/github-actions/security.yml .github/workflows/
cp templates/github-actions/security-config.yml .github/

# Replace {{PROJECT_NAME}} with your project name
sed -i 's/{{PROJECT_NAME}}/my-project/g' .github/workflows/security-scan.yml
```

**See:** [Security CI/CD Setup Guide](../../docs/guides/security-cicd-setup.md) for complete documentation.

### Go Template (Uses Mage)

The Go template uses **[Mage](https://magefile.org/)** as its build automation tool instead of Make or direct `go` commands.

**Why Mage?**
- Written in Go (no new syntax to learn)
- Cross-platform (Windows, macOS, Linux)
- Type-safe build definitions
- Better IDE support and autocomplete
- Explicit dependency management between build targets

**Getting Started:**
1. Copy `templates/github-actions/magefile.go` to your project root
2. Copy `templates/github-actions/go-ci-cd.yml` to `.github/workflows/ci.yml`
3. Replace template variables:
   - `{{GO_VERSION}}` - Your Go version (e.g., "1.21")
   - `{{PROJECT_NAME}}` - Your project name (e.g., "my-api")
   - `{{MODULE_PATH}}` - Your Go module path (e.g., "github.com/user/project")
4. Customize `magefile.go` for your project structure

**Mage Targets Available:**
- `mage build` - Build binary with version embedding
- `mage buildrelease` - Build optimized production binary
- `mage test` - Run tests with coverage
- `mage lint` - Run golangci-lint
- `mage security` - Run SAST (gosec) and SCA (govulncheck)
- `mage sbom` - Generate CycloneDX SBOM (JSON + XML)
- `mage clean` - Remove build artifacts
- `mage ci` - Run all CI checks

**Features:**
- Go 1.21+ support
- golangci-lint comprehensive linting
- Race detector in tests
- gosec SAST scanning
- govulncheck SCA scanning
- CycloneDX SBOM generation
- Version embedding with git describe
- Binary digest calculation (SHA256)
- Optional container builds with Docker
- Optional SLSA provenance attestation

## Template Structure

Each template follows this structure:

1. **Build** - Compile/bundle application, run tests
2. **Security Scan** - SAST, SCA, dependency scanning
3. **SBOM Generation** - Create Software Bill of Materials
4. **Artifact Creation** - Build container or package
5. **Attestation** - Sign and attest build provenance (SLSA)
6. **Promotion** - Deploy to staging/production

## Usage by SRE Agent

The SRE engineer uses these templates to:

1. Detect the project's tech stack
2. Select the appropriate template
3. Customize it based on project requirements
4. Generate `.github/workflows/` files in the user's project

## Customization Variables

Templates use these placeholders for customization:

- `{{PROJECT_NAME}}` - Project name
- `{{NODE_VERSION}}` - Node.js version (e.g., "20")
- `{{PYTHON_VERSION}}` - Python version (e.g., "3.11")
- `{{DOTNET_VERSION}}` - .NET version (e.g., "8.0")
- `{{GO_VERSION}}` - Go version (e.g., "1.21")
- `{{PACKAGE_MANAGER}}` - npm, yarn, pnpm, pip, poetry, uv, etc.
- `{{BUILD_COMMAND}}` - Stack-specific build command
- `{{TEST_COMMAND}}` - Stack-specific test command
- `{{ARTIFACT_PATH}}` - Path to built artifacts

## Outer Loop Compliance

All templates enforce:

### Critical Requirements
- ✅ **Build once in CI** - Never rebuild for other environments
- ✅ **Immutable artifacts** - Use content-addressable digests
- ✅ **SBOM generation** - Track all dependencies
- ✅ **Provenance attestation** - SLSA build provenance
- ✅ **Security scanning** - Automated vulnerability detection
- ✅ **No secrets in artifacts** - Externalized configuration

### Anti-Patterns Prevented
- ❌ Never rebuild for staging/production
- ❌ Never embed environment config in artifacts
- ❌ Never skip security scans
- ❌ Never deploy unsigned artifacts

## Integration with Inner Loop

These outer-loop templates complement the inner-loop scripts:

| Inner Loop (Local) | Outer Loop (CI/CD) |
|-------------------|-------------------|
| `scripts/bash/run-local-ci.sh` | GitHub Actions workflows |
| Pre-commit hooks | PR validation |
| Local testing | Multi-environment testing |
| Fast iteration | Comprehensive validation |

## Adding New Stack Templates

To add a new stack:

1. Create `templates/github-actions/{stack}-ci-cd.yml`
2. Follow the template structure above
3. Include all outer-loop requirements
4. Add to this README
5. Update `sre-agent` detection logic in `.claude/commands/flow/operate.md`

## References

- [Outer Loop Principles](../../docs/reference/outer-loop.md)
- [Inner Loop Principles](../../docs/reference/inner-loop.md)
- [Agent Loop Classification](../../docs/reference/agent-loop-classification.md)
- [SRE Agent Command](../../.claude/commands/flow/operate.md)
