# JP Spec Kit - Test Suite

Comprehensive integration tests for the backlog task generation workflow.

## Quick Start

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=src/specify_cli/backlog --cov-report=term

# Run specific test file
uv run pytest tests/test_parser.py -v

# Run specific test
uv run pytest tests/test_parser.py::TestTaskParser::test_parse_simple_task_line -v
```

## Test Results

- **Total Tests:** 143
- **Coverage:** 98%
- **Execution Time:** <1 second
- **Status:** All passing ✅

## Test Structure

```
tests/
├── conftest.py                  # Shared fixtures (13 fixtures)
├── test_parser.py               # Parser unit tests (35 tests)
├── test_writer.py               # Writer unit tests (36 tests)
├── test_dependency_graph.py     # Graph tests (31 tests)
├── test_mapper.py               # Mapper integration tests (29 tests)
└── test_cli_tasks.py            # CLI command tests (23 tests)
```

## Coverage by Module

| Module | Coverage |
|--------|----------|
| `__init__.py` | 100% |
| `parser.py` | 99% |
| `writer.py` | 98% |
| `dependency_graph.py` | 97% |
| `mapper.py` | 97% |
| **Overall** | **98%** |

## What's Tested

### Parser (test_parser.py)
- Task line parsing with all markers ([P], [US#], [P#])
- Phase and user story extraction
- File path and priority parsing
- Dependency inference
- Edge cases and invalid formats

### Writer (test_writer.py)
- Backlog.md file generation
- YAML frontmatter formatting
- Filename sanitization
- Overwrite protection
- Task status management

### Dependency Graph (test_dependency_graph.py)
- Graph construction and validation
- Topological sorting (execution order)
- Parallel batch calculation
- Critical path identification
- Circular dependency detection

### Mapper (test_mapper.py)
- End-to-end task generation
- Dry run mode
- Conflict detection and resolution
- Task grouping (by phase, by story)
- Integration workflows

### CLI (test_cli_tasks.py)
- Command-line interface
- Argument parsing and validation
- Error handling
- Unicode and special character support

## Development

### Running Tests During Development

```bash
# Watch mode (requires pytest-watch)
pip install pytest-watch
ptw tests/

# With verbose output
uv run pytest tests/ -v

# Stop on first failure
uv run pytest tests/ -x

# Run only failed tests from last run
uv run pytest tests/ --lf
```

### Adding New Tests

1. Add test to appropriate file or create new test file
2. Use existing fixtures from `conftest.py`
3. Follow AAA pattern (Arrange-Act-Assert)
4. Use descriptive test names: `test_<component>_<scenario>`
5. Run tests to verify: `uv run pytest tests/`

### Test Fixtures

Available fixtures (see `conftest.py`):
- `temp_project_dir` - Temporary directory for test files
- `sample_tasks_file` - Pre-populated tasks.md
- `sample_spec_file` - Sample spec.md
- `sample_plan_file` - Sample plan.md
- `backlog_dir` - Backlog output directory
- And more...

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run tests
  run: uv run pytest tests/ --cov=src/specify_cli/backlog --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Best Practices

1. **Keep tests fast** - All tests should complete in <5 seconds
2. **Test independence** - Tests should not depend on execution order
3. **Clear assertions** - Use specific, meaningful assertions
4. **Realistic data** - Use test data that represents real-world usage
5. **Edge cases** - Always test boundary conditions and error cases

## Debugging Failed Tests

```bash
# Show full traceback
uv run pytest tests/ --tb=long

# Show local variables in traceback
uv run pytest tests/ -l

# Drop into debugger on failure
uv run pytest tests/ --pdb

# Print output (even for passing tests)
uv run pytest tests/ -s
```

## Documentation

See `/home/jpoley/ps/jp-spec-kit/docs/task-7-test-report.md` for detailed test report including:
- Coverage analysis
- Edge cases tested
- Bugs found during testing
- Self-critique assessment

## Support

For issues or questions about tests:
1. Check test documentation in each test file
2. Review fixtures in `conftest.py`
3. Consult the test report in `docs/task-7-test-report.md`
4. Run tests with `-v` flag for verbose output
