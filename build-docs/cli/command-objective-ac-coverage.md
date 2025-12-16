# Command Objective: `flowspec ac-coverage`

## Summary
Generate acceptance criteria test coverage report by scanning PRDs and matching them to test markers.

## Objective
Ensure all acceptance criteria have corresponding test coverage by scanning PRD files for ACs and checking for @pytest.mark.ac markers in test files.

## Features

### Core Features
1. **AC extraction** - Parses PRD files for acceptance criteria
2. **Test marker scanning** - Finds @pytest.mark.ac markers
3. **Coverage calculation** - Matches ACs to tests
4. **Report generation** - JSON output of coverage status
5. **CI integration** - Exit with error if not 100% coverage

### Command Options
```bash
flowspec ac-coverage                                # Default: auto-detect feature
flowspec ac-coverage --feature auth                 # Specific feature
flowspec ac-coverage --prd docs/prd/auth.md         # Custom PRD path
flowspec ac-coverage --test-dirs tests,e2e_tests    # Custom test directories
flowspec ac-coverage --output coverage.json         # Output path
flowspec ac-coverage --check                        # Exit error if not 100%
flowspec ac-coverage --allow-partial-coverage       # Allow partial coverage
```

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| `flowspec ac-coverage` | Feature detection | Error: Could not detect feature | EXPECTED |
| Feature required | Clear error message | Clear error message | PASS |

## Acceptance Criteria
- [x] Parses acceptance criteria from PRD
- [x] Scans test files for AC markers
- [x] Generates coverage report
- [x] Supports feature name specification
- [x] Supports custom PRD path
- [x] Supports custom test directories
- [x] Supports check mode for CI
- [x] Supports partial coverage allowance
