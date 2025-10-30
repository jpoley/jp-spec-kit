# JP Spec Kit - Claude Code Configuration

This file provides essential context for Claude Code when working on the JP Spec Kit project. It covers development workflows, testing strategies, and integration with the inner/outer loop processes.

## Project Overview

**JP Spec Kit** is a comprehensive toolkit for implementing Spec-Driven Development (SDD). It includes:
- **Specify CLI**: Command-line tool to bootstrap projects (`specify-cli` package)
- **Templates**: Spec-driven development templates for multiple AI agents
- **Scripts**: Automation scripts for setup, testing, and CI/CD
- **Documentation**: Comprehensive guides for inner/outer loop development

## Quick Reference

### Common Commands

```bash
# Development and Testing
python -m pytest tests/              # Run all tests
python -m pytest tests/ -v          # Run tests with verbose output
python -m pytest tests/ -k "test_name"  # Run specific test

# Linting and Formatting
ruff check .                         # Check code quality
ruff check . --fix                   # Auto-fix issues
ruff format .                        # Format code

# Build and Install
uv build                             # Build the package
uv tool install . --force            # Install locally for testing

# Package Management
uv sync                              # Sync dependencies
uv add <package>                     # Add new dependency
uv remove <package>                  # Remove dependency

# Local CI/CD Testing
./scripts/bash/run-local-ci.sh      # Run full CI simulation locally
./scripts/bash/install-act.sh       # Install act (GitHub Actions local runner)
act -l                               # List available workflows
act -j <job-name>                    # Run specific workflow job locally
```

### Slash Commands (jpspec)

When working on this repository, you have access to specialized workflow commands:

```bash
/jpspec:specify      # Create/update feature specs (PM planner agent)
/jpspec:plan         # Execute planning workflow (architect + platform engineer)
/jpspec:research     # Execute research and validation (researcher + business validator)
/jpspec:implement    # Execute implementation (frontend + backend engineers + code review)
/jpspec:validate     # Execute QA and validation (QA + security + docs + release)
/jpspec:operate      # Execute operations (SRE agent for CI/CD + K8s + DevSecOps)
```

### Headless Mode Usage

Claude Code supports headless mode for non-interactive contexts (CI, pre-commit hooks, automation):

```bash
# Basic headless command
claude -p "Review this code for security issues"

# With specific tools allowed
claude -p "Run tests and report results" --allowedTools Read,Bash

# Stream JSON output for automation
claude -p "Generate SBOM for this project" --output-format stream-json

# Verbose mode for debugging
claude -p "Check code quality" --verbose
```

**Examples for this project:**

```bash
# Automated spec review
claude -p "/jpspec:specify Review and validate spec for feature XYZ"

# Automated code review before commit
claude -p "Review changes in git diff for code quality, security, and best practices"

# CI/CD integration
claude -p "/jpspec:validate Run comprehensive validation checks"
```

## Development Workflow

### Inner Loop (Local Development)

The **inner loop** focuses on fast, local iteration (edit → test → debug → repeat):

**Objectives:**
- Instant feedback (<2s hot reload when applicable)
- Local testing before commit
- Pre-commit validation
- CI simulation locally

**Workflow:**

1. **Setup Development Environment**
   ```bash
   # Clone and setup
   git clone <repo-url>
   cd jp-spec-kit
   uv sync                  # Install dependencies
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/description
   ```

3. **Make Changes and Test Locally**
   ```bash
   # Make your changes

   # Run tests
   pytest tests/

   # Check code quality
   ruff check . --fix
   ruff format .

   # Test CLI locally
   uv tool install . --force
   specify check
   ```

4. **Pre-Commit Validation**
   ```bash
   # Run comprehensive local checks
   ./scripts/bash/run-local-ci.sh    # (Once implemented)

   # Or manually:
   ruff check .
   ruff format .
   pytest tests/
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: description"
   ```

**Key Files for Inner Loop:**
- `pyproject.toml` - Project configuration and dependencies
- `tests/` - Test suite
- `scripts/bash/` - Local development scripts
- `scripts/powershell/` - PowerShell equivalent scripts

### Outer Loop (CI/CD Pipeline)

The **outer loop** handles everything after commit (PR → build → test → package → deploy):

**Objectives:**
- Automated testing on PR
- Build once, promote everywhere
- Security scanning and SBOM generation
- Artifact signing and provenance
- Automated deployment

**GitHub Actions Workflows:**
- `.github/workflows/docs.yml` - Documentation deployment
- `.github/workflows/release.yml` - Release automation
- `.github/workflows/ci.yml` - CI/CD pipeline (to be implemented)
- `.github/workflows/security.yml` - Security scanning (to be implemented)

**Workflow Triggers:**
- Push to `main` branch
- Pull request creation/update
- Manual workflow dispatch
- Release tag creation

## Project Structure

```
jp-spec-kit/
├── .claude/
│   └── commands/jpspec/     # Slash command implementations
├── .github/
│   └── workflows/           # GitHub Actions workflows
├── docs/                    # Documentation
│   ├── reference/
│   │   ├── inner-loop.md   # Inner loop principles
│   │   ├── outer-loop.md   # Outer loop principles
│   │   └── agent-loop-classification.md
│   └── ...
├── memory/                  # Project memory and constitution
│   └── constitution.md
├── scripts/
│   ├── bash/               # Bash scripts for automation
│   └── powershell/         # PowerShell equivalents
├── src/specify_cli/        # CLI source code
├── templates/              # Project templates
│   └── commands/jpspec/    # Command templates
├── tests/                  # Test suite
├── AGENTS.md              # AI agent guidance (this file's purpose)
├── CLAUDE.md              # Claude Code configuration (this file)
├── CONTRIBUTING-AGENTS.md # How to add new agent support to Specify CLI
├── pyproject.toml         # Project configuration
└── README.md              # Project readme
```

## Code Style and Standards

### Python Code Style

- **Formatter**: Ruff (replaces Black)
- **Linter**: Ruff (replaces Flake8, isort, pyupgrade)
- **Type Checking**: Use type hints where appropriate
- **Line Length**: 88 characters (Ruff default)

**Key Conventions:**
- Use descriptive variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and single-purpose
- Prefer composition over inheritance
- Use pathlib for file operations

### Testing Standards

- **Framework**: pytest
- **Coverage Target**: Aim for >80% coverage on core functionality
- **Test Organization**: Mirror source structure in `tests/`
- **Naming**: `test_<functionality>.py` for test files

**Test Types:**
- Unit tests: Test individual functions/classes
- Integration tests: Test CLI commands end-to-end
- Regression tests: Prevent known issues from recurring

### Commit Message Format

Follow conventional commits:

```
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore
Examples:
- feat(cli): add support for new AI agent
- fix(templates): correct template variable substitution
- docs(readme): update installation instructions
- test(cli): add tests for init command
```

## Testing Instructions

### Running Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_cli.py

# Specific test function
pytest tests/test_cli.py::test_init_command

# With coverage
pytest tests/ --cov=src/specify_cli --cov-report=html

# Watch mode (requires pytest-watch)
ptw tests/
```

### Writing Tests

**Test Structure:**
```python
def test_feature_description():
    # Arrange - Setup test data
    input_data = {...}

    # Act - Execute functionality
    result = function_under_test(input_data)

    # Assert - Verify results
    assert result == expected_output
```

**Fixtures:**
Use pytest fixtures for common setup:
```python
@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory for testing."""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    return project_dir
```

## Agent Loop Classification

Per `docs/reference/agent-loop-classification.md`:

### Inner Loop Agents
- product-requirements-manager
- software-architect
- platform-engineer
- researcher, business-validator
- frontend-engineer, backend-engineer, ai-ml-engineer
- frontend-code-reviewer, backend-code-reviewer
- quality-guardian, playwright-* agents
- secure-by-design-engineer
- tech-writer

### Outer Loop Agents
- sre-agent (CI/CD, Kubernetes, DevSecOps, observability)
- release-manager (deployment, promotion workflows)

## Important Notes

### Version Management

When modifying `src/specify_cli/__init__.py`:
- **MUST** update version in `pyproject.toml`
- **MUST** add entry to `CHANGELOG.md`
- Follow semantic versioning (MAJOR.MINOR.PATCH)

### Adding New Agent Support

See `CONTRIBUTING-AGENTS.md` for detailed instructions on:
- Adding agent to `AGENT_CONFIG` in `src/specify_cli/__init__.py`
- Updating CLI help text
- Updating README documentation
- Modifying release package scripts
- Updating agent context scripts

### Pull Request Guidelines

Before creating a PR:
1. Run all tests and ensure they pass
2. Run linting and fix any issues
3. Update documentation if needed
4. Test CLI commands locally
5. Ensure commit messages follow conventions
6. Add entry to CHANGELOG.md if applicable

### CI/CD Requirements

All code must pass:
- Linting (ruff check)
- Formatting (ruff format --check)
- Tests (pytest)
- Type checking (if implemented)
- Security scanning (in CI)

## Testing GitHub Actions Locally with act

### Installing act

**act** is a tool that runs GitHub Actions workflows locally using Docker. This allows you to test workflows before pushing to GitHub.

**Installation:**

```bash
# Using the installation script (recommended)
./scripts/bash/install-act.sh

# Or install manually:
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Windows (PowerShell)
.\scripts\powershell\install-act.ps1
# Or: choco install act-cli
# Or: scoop install act
```

**Prerequisites:**
- Docker must be installed and running
- act uses Docker containers to simulate GitHub Actions runners

### Using act

```bash
# List available workflows and jobs
act -l

# Run all jobs in a workflow
act

# Run a specific job
act -j <job-name>

# Run with specific event
act push
act pull_request

# Dry run (don't execute, just show what would run)
act -n

# Use specific runner image
act -P ubuntu-latest=catthehacker/ubuntu:act-latest

# Run with secrets
act -s GITHUB_JPSPEC=<token>

# Verbose output
act -v
```

**Testing JP Spec Kit CI:**

```bash
# Test the main CI workflow
act -j lint          # Run linting job
act -j test          # Run test suite
act -j build         # Run package build
act -j security      # Run security scanning
```

**Important Notes:**
- ⚠️ **NOT YET TESTED**: The ci.yml workflow has NOT been tested with act yet
- ⚠️ Some GitHub Actions features may not work in act (attestations, OIDC, etc.)
- ⚠️ Multi-platform jobs (macOS, Windows) cannot run in act (Linux only)
- First run will download Docker images (may take several minutes)
- act runs faster than GitHub Actions for quick iterations

**Resources:**
- act documentation: https://github.com/nektos/act
- Docker installation: https://docs.docker.com/get-docker/

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure dependencies are installed
uv sync
```

**CLI Not Found:**
```bash
# Reinstall the tool
uv tool install . --force
```

**Tests Failing:**
```bash
# Check Python version (requires 3.11+)
python --version

# Reinstall dependencies
uv sync --force
```

**Permission Errors:**
```bash
# Make scripts executable
chmod +x scripts/bash/*.sh
```

**act Issues:**
```bash
# Ensure Docker is running
docker ps

# Pull latest runner images
docker pull catthehacker/ubuntu:act-latest

# Clear act cache
rm -rf ~/.actrc

# Check act version
act --version
```

## Resources

- [Inner Loop Principles](docs/reference/inner-loop.md)
- [Outer Loop Principles](docs/reference/outer-loop.md)
- [Agent Loop Classification](docs/reference/agent-loop-classification.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Spec-Driven Development Guide](spec-driven.md)
- [Claude Code Documentation](https://docs.claude.com/claude-code)

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_JPSPEC` | GitHub token for API requests |
| `SPECIFY_FEATURE` | Override feature detection for non-Git repos |

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review closed issues for solutions

---

*This file is automatically loaded by Claude Code for context. Keep it concise and up-to-date.*
