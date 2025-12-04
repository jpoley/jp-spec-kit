---
description: Analyze repository structure and customize the constitution template with project-specific details
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Execution Instructions

This command analyzes the repository structure and customizes the constitution template at `memory/constitution.md` with detected project-specific details. It identifies languages, frameworks, CI/CD systems, testing tools, linting configurations, and security tools, then updates the constitution's SECTION markers and creates a repository facts document.

### Overview

The `/speckit:constitution` command:
1. Scans repository for technology stack indicators
2. Detects languages, frameworks, tooling, and practices
3. Updates constitution SECTION markers with detected values
4. Creates `memory/repo-facts.md` with structured findings
5. Adds NEEDS_VALIDATION markers where human review is required
6. Reports analysis results and next steps

### Step 1: Repository Structure Analysis

Perform a comprehensive repository scan to detect:

#### Languages & Frameworks

**Detection patterns**:
- **Node.js/TypeScript**: `package.json`, `tsconfig.json`, `bun.lockb`, `pnpm-lock.yaml`, `yarn.lock`
  - Frameworks: Check `package.json` dependencies for Next.js, React, Vue, Express, Fastify, NestJS
- **Python**: `pyproject.toml`, `requirements.txt`, `setup.py`, `Pipfile`, `uv.lock`
  - Frameworks: Check for FastAPI, Django, Flask, SQLAlchemy in dependencies
- **Go**: `go.mod`, `go.sum`
  - Frameworks: Check imports for Chi, Gin, Echo, Fiber
- **Rust**: `Cargo.toml`, `Cargo.lock`
  - Frameworks: Check for Actix, Rocket, Axum, Tokio
- **Java**: `pom.xml`, `build.gradle`, `build.gradle.kts`
  - Frameworks: Check for Spring Boot, Quarkus, Micronaut
- **Ruby**: `Gemfile`, `Gemfile.lock`
  - Frameworks: Rails, Sinatra

**Analysis approach**:
```bash
# Use Read tool to check for presence of these files
# For each found file, parse to extract framework dependencies
# Determine primary language (most prevalent) and secondary languages
```

#### CI/CD Systems

**Detection patterns**:
- **GitHub Actions**: `.github/workflows/*.yml`
- **GitLab CI**: `.gitlab-ci.yml`
- **CircleCI**: `.circleci/config.yml`
- **Jenkins**: `Jenkinsfile`, `jenkins/`
- **Azure Pipelines**: `azure-pipelines.yml`, `.azure/`
- **Buildkite**: `.buildkite/`

**Analysis approach**:
- Check for workflow/pipeline configuration files
- Identify primary CI/CD platform
- Note if multiple platforms are in use

#### Testing Infrastructure

**Detection patterns**:
- **Test directories**: `tests/`, `test/`, `__tests__/`, `spec/`, `e2e/`
- **Python**: `pytest.ini`, `tox.ini`, presence of `pytest` in dependencies
- **JavaScript/TypeScript**: `jest.config.js`, `vitest.config.ts`, `playwright.config.ts`
- **Go**: `*_test.go` files
- **Rust**: `tests/` directory, `#[cfg(test)]` in source
- **Java**: `src/test/`, JUnit in dependencies

**Analysis approach**:
- Identify test framework(s) in use
- Check for coverage configuration (`.coveragerc`, `coverage.xml`, etc.)
- Determine test types present (unit, integration, e2e)

#### Linting & Formatting

**Detection patterns**:
- **Python**: `ruff.toml`, `pyproject.toml` [tool.ruff], `.flake8`, `.pylintrc`, `mypy.ini`
- **JavaScript/TypeScript**: `.eslintrc*`, `eslint.config.js`, `prettier.config.*`, `.prettierrc*`
- **Go**: `.golangci.yml`, `.golangci.yaml`
- **Rust**: `rustfmt.toml`, `clippy.toml`
- **Java**: `checkstyle.xml`, `pmd.xml`, `spotbugs.xml`

**Analysis approach**:
- Check for linter configuration files
- Identify formatters (Prettier, Black, rustfmt, gofmt)
- Note any type checkers (mypy, TypeScript strict mode)

#### Security Tools

**Detection patterns**:
- **Dependency scanning**: `.snyk`, `dependabot.yml`, `.github/dependabot.yml`, `renovate.json`
- **SAST tools**: `bandit.yaml`, `gosec.yaml`, `.semgrep.yml`, `sonar-project.properties`
- **Container scanning**: `trivy.yaml`, `.trivyignore`
- **Secret scanning**: `.gitleaks.toml`, `trufflehog.yaml`

**Analysis approach**:
- Identify security scanning tools in CI/CD workflows
- Check for security tool configurations
- Note any pre-commit hooks for security

#### Build & Package Management

**Detection patterns**:
- **Docker**: `Dockerfile`, `docker-compose.yml`, `.dockerignore`
- **Kubernetes**: `k8s/`, `kubernetes/`, `*.yaml` manifests
- **Makefiles**: `Makefile`, `mage.go`
- **Task runners**: `Taskfile.yml`, `justfile`

### Step 2: Constitution Updates

Load the current constitution from `memory/constitution.md` and update SECTION markers with detected information:

#### SECTION:TECH_STACK Updates

Replace placeholder tokens with detected values:

```markdown
<!-- SECTION:TECH_STACK:BEGIN -->
- **Primary Language**: Python 3.11+
- **Framework**: FastAPI 0.104+
- **Package Manager**: uv
- **Secondary Languages**: TypeScript (frontend tooling)
<!-- SECTION:TECH_STACK:END -->
```

#### SECTION:TESTING Updates

Update testing requirements based on detected infrastructure:

```markdown
<!-- SECTION:TESTING:BEGIN -->
- **Test Framework**: pytest with pytest-asyncio
- **Coverage Tool**: pytest-cov
- **Minimum Coverage**: 70% (NEEDS_VALIDATION)
- **Test Types**: Unit tests required, integration tests for API endpoints
<!-- SECTION:TESTING:END -->
```

#### SECTION:CODE_QUALITY Updates

Update linting and formatting standards:

```markdown
<!-- SECTION:CODE_QUALITY:BEGIN -->
- **Linter**: ruff (replaces flake8, isort, pyupgrade)
- **Formatter**: ruff format
- **Type Checking**: mypy in strict mode
- **Pre-commit hooks**: Enabled via `.pre-commit-config.yaml`
<!-- SECTION:CODE_QUALITY:END -->
```

#### SECTION:SECURITY Updates

Update security practices based on detected tools:

```markdown
<!-- SECTION:SECURITY:BEGIN -->
- **Dependency Scanning**: Dependabot (GitHub)
- **SAST**: bandit for Python security analysis
- **Secret Scanning**: GitHub secret scanning enabled
- **Container Scanning**: trivy for Docker images
- **Vulnerability Management**: Fix critical/high within 7 days
<!-- SECTION:SECURITY:END -->
```

#### SECTION:CICD Updates

Update CI/CD configuration:

```markdown
<!-- SECTION:CICD:BEGIN -->
- **Platform**: GitHub Actions
- **Workflow Files**: `.github/workflows/test.yml`, `.github/workflows/release.yml`
- **Required Checks**: Tests, linting, security scans must pass
- **Deployment**: Automated to staging on main branch
<!-- SECTION:CICD:END -->
```

#### NEEDS_VALIDATION Markers

Add `<!-- NEEDS_VALIDATION: reason -->` comments for values that require human review:

- Coverage targets (default to 70%, but may need adjustment)
- Security vulnerability SLA (default to 7 days for critical/high)
- Deployment strategy details
- Branch protection rules
- Code review requirements (1 reviewer vs 2)

### Step 3: Create Repository Facts Document

Write findings to `memory/repo-facts.md` with YAML frontmatter and structured content:

```markdown
---
detected_at: YYYY-MM-DD
analysis_version: 1.0.0
languages:
  - python
  - typescript
frameworks:
  - fastapi
  - react
ci_cd: github-actions
test_framework: pytest
linter: ruff
formatter: ruff
security_tools:
  - bandit
  - dependabot
  - trivy
build_tools:
  - docker
  - uv
---

# Repository Facts

**Generated**: YYYY-MM-DD by `/speckit:constitution` command

This document contains automatically detected repository characteristics used to customize the constitution.

## Languages & Frameworks

### Primary Language
- **Python 3.11+**
- Detected via: `pyproject.toml`, `src/` directory structure
- Package manager: `uv` (modern pip replacement)

### Secondary Languages
- **TypeScript**
- Detected via: `package.json`, `tsconfig.json`
- Used for: Frontend tooling, testing infrastructure

### Frameworks
- **FastAPI 0.104+**: REST API framework
- **React 18**: UI components (if applicable)

## Build & Package Management

### Python
- **uv**: Fast Python package installer
- **pyproject.toml**: Project configuration
- Virtual environment: `.venv/`

### Node.js (if applicable)
- **pnpm**: Package manager
- **bun**: Alternative runtime (if detected)

## Testing Infrastructure

### Test Framework
- **pytest**: Python testing framework
- **pytest-cov**: Coverage reporting
- **pytest-asyncio**: Async test support

### Test Organization
- Unit tests: `tests/unit/`
- Integration tests: `tests/integration/`
- E2E tests: `tests/e2e/`

### Coverage
- Tool: pytest-cov
- Config: `.coveragerc` or `pyproject.toml [tool.coverage]`
- Target: 70% (NEEDS_VALIDATION)

## Code Quality

### Linting
- **ruff**: Fast Python linter
- Config: `ruff.toml` or `pyproject.toml [tool.ruff]`
- Replaces: flake8, isort, pyupgrade, pydocstyle

### Formatting
- **ruff format**: Code formatter
- Compatible with Black formatting style

### Type Checking
- **mypy**: Static type checker
- Mode: Strict (if `mypy.ini` or pyproject.toml config found)

### Pre-commit Hooks
- File: `.pre-commit-config.yaml`
- Hooks: ruff, mypy, trailing whitespace, end-of-file-fixer

## CI/CD

### Platform
- **GitHub Actions**

### Workflows
- `.github/workflows/test.yml`: Run tests on PR
- `.github/workflows/release.yml`: Build and release
- `.github/workflows/security.yml`: Security scans (if present)

### Required Checks
- All tests pass
- Linting passes (ruff)
- Type checking passes (mypy)
- Security scans pass (bandit, trivy)

## Security

### Tools Detected
- **Dependabot**: Dependency vulnerability scanning
  - Config: `.github/dependabot.yml`
  - Frequency: Weekly
- **bandit**: Python SAST tool
  - Config: `.bandit` or `pyproject.toml [tool.bandit]`
- **trivy**: Container image scanning
  - Config: `trivy.yaml` or CI workflow

### Practices
- No secrets in code (enforced by git-secrets or similar)
- Automated dependency updates
- Security scan in CI pipeline

## Docker

- **Dockerfile**: Multi-stage build
- **docker-compose.yml**: Local development environment
- Base images: Official Python slim images

## Notes

- This document is auto-generated and should be reviewed for accuracy
- Update constitution sections marked with NEEDS_VALIDATION
- Re-run `/speckit:constitution` after major tooling changes
```

### Step 4: Validation Rules

Before finalizing updates, validate:

1. **No duplicate SECTION markers**: Each section should appear once
2. **Balanced BEGIN/END markers**: Every BEGIN has matching END
3. **Consistent tool naming**: Use official tool names (e.g., "ruff" not "Ruff")
4. **Version specificity**: Include version numbers where relevant (Python 3.11+, FastAPI 0.104+)
5. **NEEDS_VALIDATION placement**: Add for subjective values (coverage %, SLA days)

### Step 5: Report Results

Generate a comprehensive summary using rich formatting:

```
╔══════════════════════════════════════════════════════════════╗
║         Constitution Customization Complete                  ║
╚══════════════════════════════════════════════════════════════╝

📊 REPOSITORY ANALYSIS SUMMARY

Languages Detected:
  ✓ Python 3.11+ (primary)
  ✓ TypeScript (secondary)

Frameworks:
  ✓ FastAPI 0.104+
  ✓ React 18

Build Tools:
  ✓ uv (Python package manager)
  ✓ pnpm (Node.js package manager)

Testing:
  ✓ pytest (test framework)
  ✓ pytest-cov (coverage)

Code Quality:
  ✓ ruff (linting + formatting)
  ✓ mypy (type checking)

Security:
  ✓ Dependabot
  ✓ bandit (SAST)
  ✓ trivy (container scanning)

CI/CD:
  ✓ GitHub Actions (.github/workflows/)

📝 CONSTITUTION UPDATES

Updated Sections:
  ✓ SECTION:TECH_STACK
  ✓ SECTION:TESTING
  ✓ SECTION:CODE_QUALITY
  ✓ SECTION:SECURITY
  ✓ SECTION:CICD

Files Modified:
  ✓ memory/constitution.md
  ✓ memory/repo-facts.md (created)

⚠️  NEEDS VALIDATION

The following items require human review:
  1. Test coverage target (currently: 70%)
  2. Security vulnerability SLA (currently: 7 days for critical/high)
  3. Code review requirements (currently: 1 reviewer)
  4. Deployment strategy details

🎯 NEXT STEPS

1. Review constitution: memory/constitution.md
2. Validate detected values in: memory/repo-facts.md
3. Update NEEDS_VALIDATION markers
4. Run: specify constitution validate
5. Commit changes:

   git add memory/constitution.md memory/repo-facts.md
   git commit -s -m "docs: customize constitution with detected repo facts

   - Analyze repo structure for languages, frameworks, tooling
   - Update TECH_STACK, TESTING, CODE_QUALITY, SECURITY, CICD sections
   - Create repo-facts.md with structured findings
   - Add NEEDS_VALIDATION markers for manual review

   Generated via /speckit:constitution command"
```

### Step 6: Edge Cases & Error Handling

**Scenario: Constitution file not found**
- Inform user to run `specify init` first to create constitution template
- Exit gracefully with clear instructions

**Scenario: Ambiguous primary language**
- If multiple languages have similar code volume, ask user to specify
- Default to alphabetical order if user input not provided
- Add NEEDS_VALIDATION marker

**Scenario: No CI/CD detected**
- Note absence in repo-facts.md
- Add NEEDS_VALIDATION marker to suggest CI/CD setup
- Recommend GitHub Actions as default for GitHub repos

**Scenario: Mixed package managers**
- Example: Both `requirements.txt` and `pyproject.toml` found
- Detect which is actively used (check for `.venv/` paths, CI workflow references)
- Prefer modern tools (uv > pip, pnpm > npm)

**Scenario: No test framework detected**
- Add NEEDS_VALIDATION marker
- Recommend appropriate framework based on language
- Include in next steps report

## Important Notes

1. **Read-only analysis**: This command analyzes but does not modify code or configs
2. **NEEDS_VALIDATION critical**: Always add these markers for subjective decisions
3. **Version sensitivity**: Include version numbers where relevant (Python 3.11+, not just "Python")
4. **Tool precedence**: Prefer modern tools (ruff > flake8, uv > pip, pnpm > npm)
5. **CI/CD awareness**: Check workflow files for additional tool detection
6. **Multi-language projects**: Clearly distinguish primary vs secondary languages
7. **Framework specificity**: Don't just detect "React", note if it's Next.js, Remix, etc.

## Exclusions

Do NOT modify these during constitution customization:
- Core principles (Quality-Driven Development, Continuous Improvement)
- Git commit requirements (DCO sign-off, branch strategy)
- Task management standards (acceptance criteria, Definition of Done)
- Governance section (team consensus, amendment process)

These sections are constitutional standards, not technology-specific details.
