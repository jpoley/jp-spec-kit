# Source Code Standards

## flowspec_cli/

The main CLI package for Flowspec.

## Code Standards

### Python Style
- **Linter/Formatter**: Ruff (run `ruff check . --fix && ruff format .`)
- **Line length**: 88 characters
- **Imports**: Sorted by ruff (stdlib, third-party, local)

### Type Hints
Required for public APIs:
```python
def process_template(template_path: Path, output_dir: Path) -> bool:
    """Process a template file."""
    ...
```

### File Paths
Use `pathlib.Path`, not `os.path`:
```python
from pathlib import Path

template_dir = Path(__file__).parent / "templates"
```

### Docstrings
Required for public functions and classes:
```python
def init_project(project_name: str, agent: str) -> None:
    """Initialize a new project with SDD templates.

    Args:
        project_name: Name of the project directory to create.
        agent: AI agent type (claude, copilot, cursor, etc).
    """
```

## Testing

```bash
# Run all tests
pytest tests/

# Specific test
pytest tests/test_cli.py::test_init_command

# With coverage
pytest tests/ --cov=src/flowspec_cli --cov-report=html

# Watch mode
ptw tests/
```

### Test Pattern (AAA)
```python
def test_feature_description():
    # Arrange
    input_data = {...}

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected
```

## Version Management

When modifying `__init__.py`:
1. Update `__version__` in `__init__.py`
2. Update version in `pyproject.toml` (must match)
3. Add entry to `CHANGELOG.md`
4. Follow semantic versioning (MAJOR.MINOR.PATCH)

## Adding New Agent Support

See `CONTRIBUTING-AGENTS.md` for:
- Adding agent to `AGENT_CONFIG`
- Updating CLI help text
- Updating README documentation
- Modifying release package scripts

## Building

```bash
uv build                      # Build package
uv tool install . --force     # Install locally
flowspec --help                # Verify installation
```
