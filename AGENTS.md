# Flowspec - Guide for AI Coding Agents

This file provides guidance for AI coding agents working on the Flowspec project. It follows the [agents.md specification](https://agents.md/) to ensure compatibility across multiple AI coding assistant platforms.

## Project Overview

Flowspec is a comprehensive toolkit for implementing **Spec-Driven Development (SDD)** - a methodology where specifications become executable, directly generating working implementations. The project includes:

- **Specify CLI** - Python-based CLI tool for bootstrapping spec-driven projects
- **Multi-agent templates** - Support for 13+ AI coding assistants (Claude, Copilot, Gemini, Cursor, Windsurf, etc.)
- **Workflow automation** - Scripts for setup, testing, and CI/CD
- **Documentation** - Comprehensive guides for inner/outer loop development

## Development Environment Setup

### Prerequisites

```bash
# Required tools
python --version        # Python 3.11+ required
git --version          # Git for version control
uv --version           # uv for package management

# Installation if missing
curl -LsSf https://astral.sh/uv/install.sh | sh  # Install uv
```

### Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd flowspec

# Install dependencies
uv sync

# Run tests to verify setup
pytest tests/

# Install CLI locally for testing
uv tool install . --force

# Verify installation
specify check
```

## Code Style Guidelines

### Python Style

- **Formatting**: Use `ruff format .` (configured in pyproject.toml)
- **Linting**: Use `ruff check .` before committing
- **Type Hints**: Add type hints to function signatures
- **Docstrings**: Include docstrings for all public functions
- **Line Length**: 88 characters maximum
- **Imports**: Organized automatically by ruff

### Code Quality Checks

```bash
# Format code
ruff format .

# Check and auto-fix linting issues
ruff check . --fix

# Run without auto-fix to see all issues
ruff check .
```

## Testing Instructions

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_cli.py

# Run specific test function
pytest tests/test_cli.py::test_init_command

# Run with coverage report
pytest tests/ --cov=src/specify_cli --cov-report=html
```

### Test Coverage

- Aim for >80% coverage on core functionality
- All new features require tests
- Bug fixes should include regression tests
- Test both success and failure paths

### Pre-Commit Checks

Before committing, always run:

```bash
# Format and lint
ruff format .
ruff check . --fix

# Run tests
pytest tests/

# Verify CLI works
uv tool install . --force
specify check
```

## Pull Request Guidelines

### Before Creating a PR

1. **Run local validation**:
   ```bash
   ruff format .
   ruff check .
   pytest tests/
   ```

2. **Update version if needed** (for `src/specify_cli/__init__.py` changes):
   - Update version in `pyproject.toml`
   - Add entry to `CHANGELOG.md`

3. **Test CLI commands**:
   ```bash
   uv tool install . --force
   flowspec init test-project --ai claude
   specify check
   ```

4. **Update documentation** if you've:
   - Added new features
   - Changed command behavior
   - Modified configuration options

### Commit Message Format

Use conventional commits:

```
<type>(<scope>): <description>

Types:
  feat     - New feature
  fix      - Bug fix
  docs     - Documentation changes
  style    - Code style changes (formatting)
  refactor - Code refactoring
  test     - Adding or updating tests
  chore    - Maintenance tasks

Examples:
  feat(cli): add support for Windsurf agent
  fix(templates): correct flowspec command paths
  docs(readme): update installation instructions
  test(cli): add tests for --force flag
```

### PR Description Template

```markdown
## Description
[Brief description of changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines (ruff)
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## Project Structure

```
flowspec/
├── src/specify_cli/        # CLI source code
│   ├── __init__.py        # Main CLI logic and AGENT_CONFIG
│   └── ...
├── tests/                  # Test suite
├── scripts/
│   ├── bash/              # Bash automation scripts
│   └── powershell/        # PowerShell equivalents
├── templates/             # Project templates
│   └── commands/flowspec/   # flowspec workflow commands
├── .claude/
│   └── commands/flowspec/   # Installed flowspec commands
├── .github/workflows/     # GitHub Actions CI/CD
├── docs/                  # Documentation
│   └── reference/         # Technical reference docs
├── CLAUDE.md             # Claude Code configuration
├── AGENTS.md             # This file
├── CONTRIBUTING-AGENTS.md # Guide for adding new agent support
└── pyproject.toml        # Project configuration
```

## Important Files

| File | Purpose | When to Modify |
|------|---------|----------------|
| `src/specify_cli/__init__.py` | CLI logic and agent config | Adding features or agent support |
| `pyproject.toml` | Dependencies and config | Adding deps or changing version |
| `CHANGELOG.md` | Version history | Every version change |
| `CLAUDE.md` | Claude Code context | Workflow or command changes |
| `AGENTS.md` | This file | Development process changes |
| `CONTRIBUTING-AGENTS.md` | Agent integration guide | When adding agent support |

## Common Development Tasks

### Adding a New Agent

See `CONTRIBUTING-AGENTS.md` for detailed instructions. Key steps:

1. Add to `AGENT_CONFIG` in `src/specify_cli/__init__.py`
2. Update CLI help text
3. Update `README.md`
4. Modify release package scripts
5. Update agent context scripts
6. Test thoroughly

### Modifying Slash Commands

Commands are in two locations:

- **Templates**: `templates/commands/flowspec/*.md` (for new projects)
- **Installed**: `.claude/commands/flow/*.md` (for this repo)

When modifying:
1. Update template in `templates/commands/flowspec/`
2. Update installed version in `.claude/commands/flow/`
3. Test with `/flow:<command>` in Claude Code

### Adding New Scripts

Scripts go in `scripts/bash/` and `scripts/powershell/`:

```bash
# Create bash script
touch scripts/bash/my-script.sh
chmod +x scripts/bash/my-script.sh

# Create PowerShell equivalent
touch scripts/powershell/my-script.ps1
```

Always provide both bash and PowerShell versions for cross-platform support.

## Debugging and Troubleshooting

### CLI Not Working

```bash
# Reinstall
uv tool uninstall flowspec-cli
uv tool install . --force

# Check installation
which specify
flowspec --help
```

### Tests Failing

```bash
# Clean and reinstall dependencies
rm -rf .venv
uv sync

# Check Python version
python --version  # Should be 3.11+

# Run tests with verbose output
pytest tests/ -v
```

### Import Errors

```bash
# Ensure you're in project root
pwd

# Sync dependencies
uv sync

# Reinstall package
uv tool install . --force
```

## Development Workflow

### Inner Loop (Local)

1. **Create feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes and test**
   ```bash
   # Make changes
   # ...

   # Format and lint
   ruff format .
   ruff check . --fix

   # Test
   pytest tests/
   ```

3. **Test CLI locally**
   ```bash
   uv tool install . --force
   flowspec init test-project --ai claude
   ```

4. **Commit**
   ```bash
   git add .
   git commit -m "feat: add my feature"
   ```

### Outer Loop (CI/CD)

After pushing, GitHub Actions will:
- Run linting checks
- Execute test suite
- Build documentation
- Create release packages (on main branch)

Monitor at: https://github.com/[username]/flowspec/actions

## Resources

- **[Spec-Driven Development Guide](spec-driven.md)** - Full methodology
- **[Contributing Guide](CONTRIBUTING.md)** - Contribution guidelines
- **[Inner Loop Reference](docs/reference/inner-loop.md)** - Local dev principles
- **[Outer Loop Reference](docs/reference/outer-loop.md)** - CI/CD principles
- **[Agent Loop Classification](docs/reference/agent-loop-classification.md)** - Agent categories

## Getting Help

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Documentation**: Check `docs/` directory
- **Examples**: Look at existing code and tests
- **Community**: Engage via GitHub discussions

## Notes for AI Agents

### When Modifying `src/specify_cli/__init__.py`

This is a critical file. Changes here require:
- Version bump in `pyproject.toml`
- Entry in `CHANGELOG.md`
- Thorough testing

### Agent-Specific Notes

- **Claude Code**: Use `/flow:*` commands for workflows
- **GitHub Copilot**: Context from `.github/prompts/` (if exists)
- **All Agents**: Follow this AGENTS.md for consistent development

### Testing Philosophy

- Write tests first when possible (TDD)
- Test both happy path and error conditions
- Use fixtures for common setups
- Keep tests focused and readable

---

*This file follows the [agents.md specification](https://agents.md/) for cross-agent compatibility.*
