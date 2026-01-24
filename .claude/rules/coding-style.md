# Coding Style Rules

Rules for consistent, maintainable code.

## Python Standards

- **Linter/Formatter**: Ruff (replaces Black, Flake8, isort)
- **Line length**: 88 characters
- **Type hints**: Required for public APIs
- **File paths**: Use `pathlib`

## Imports

All imports at **module level** (top of file), never inline:

```python
# Good
import json

def parse_response(data: str):
    return json.loads(data)

# Bad
def parse_response(data: str):
    import json  # Inline import
    return json.loads(data)
```

## Naming (Avoid Shadowing)

Never use Python built-in names:
- **Bad**: `id`, `type`, `list`, `dict`, `input`, `filter`, `map`, `hash`
- **Good**: `finding_id`, `item_type`, `items`, `data`, `user_input`

Never shadow imported modules:
- **Bad**: `html = generate_html()` when `import html` exists
- **Good**: `html_output = generate_html()`

## File I/O

Always use `encoding="utf-8"`:

```python
# Reading
with open(file_path, encoding="utf-8") as f:
    content = f.read()

# Writing with pathlib
path.write_text(content, encoding="utf-8")
```

Always clean up temp files:

```python
with tempfile.NamedTemporaryFile(delete=False) as f:
    temp_path = f.name
try:
    # use temp file
finally:
    Path(temp_path).unlink(missing_ok=True)
```

## Defensive Programming

- Clamp external inputs: `max(0.0, min(1.0, value))`
- Use explicit type conversions: `str(finding.location.file)`

## YAGNI (You Aren't Gonna Need It)

- Don't add config fields you don't use
- Remove dead code, don't comment it out
- If a feature isn't implemented, don't scaffold it

## Docstrings

Document return guarantees clearly:

```python
"""Get version from compatibility matrix.

Returns:
    Version string (e.g., "0.0.20"), guaranteed to return a value
"""
```

## Consistency

Standards apply everywhere: production, tests, docstrings, templates.