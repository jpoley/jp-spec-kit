# Security Facts for AI Tools

This document contains key security facts that AI tools (Claude Code, skills, commands) should be aware of when working with the JP Spec Kit security system.

## Core Security Principles

### 1. Zero API Keys in Config System
- The security configuration system (`src/specify_cli/security/config/`) contains NO LLM SDK calls
- Configuration is pure data loading and validation
- AI logic is separated into triage and analysis modules

### 2. Scanner Architecture
- Scanners run BEFORE AI analysis
- Scanners produce structured findings (SARIF/JSON)
- AI tools consume scanner output for triage and remediation

### 3. Configuration Hierarchy
Default locations searched in order:
1. `.flowspec/security-config.yml`
2. `.flowspec/security-config.yaml`
3. `.security/config.yml`
4. `.security/config.yaml`
5. `security-config.yml`

If no config file exists, sensible defaults are used.

## Security Configuration Features

### Supported Scanners
- **Semgrep**: SAST scanner with custom rule support
- **CodeQL**: GitHub's semantic code analysis
- **Bandit**: Python security linter

### Severity Thresholds
Available severity levels (highest to lowest):
- `critical` - Must fix immediately
- `high` - Fix before production
- `medium` - Fix soon
- `low` - Fix when convenient
- `info` - Informational only

The `fail_on` setting determines when scans fail:
- `fail_on: critical` - Only fail on critical findings
- `fail_on: high` - Fail on high and critical
- `fail_on: medium` - Fail on medium, high, and critical
- `fail_on: low` - Fail on any finding except info
- `fail_on: none` - Never fail (report only)

### Path Exclusions
Three types of exclusions:
1. **Exact paths**: `node_modules/`, `.venv/`
2. **Glob patterns**: `*_test.py`, `*.generated.js`
3. **File extensions**: `.min.js`, `.map`

### AI Triage Settings
- `confidence_threshold`: 0.0-1.0 (default 0.7)
  - Findings below threshold flagged as uncertain
- `auto_dismiss_fp`: Auto-dismiss likely false positives
- `cluster_similar`: Group similar findings together

## Configuration Validation

The config system validates:
- Scanner names are valid
- Severity levels are recognized
- Confidence thresholds are 0.0-1.0
- Timeout values are non-negative
- File paths exist (for custom rules)

Validation errors include:
- Path to the invalid field
- Expected value type/range
- Actual value provided

## Security Best Practices

### For AI Tools
1. **Never log sensitive data** - No passwords, tokens, API keys
2. **Validate all inputs** - Don't trust scanner output blindly
3. **Use parameterized queries** - No string interpolation for commands
4. **Respect exclusions** - Don't scan excluded paths

### For Configuration
1. **Start with defaults** - Only override what you need
2. **Test locally first** - Don't push untested configs
3. **Use version control** - Track config changes like code
4. **Document custom rules** - Explain why rules were added

## Scanner Integration

### Semgrep
- Default rulesets: `p/default` (comprehensive security rules)
- Custom rules directory: `.security/rules/` or configured path
- Timeout: 300 seconds (5 minutes)
- Output format: SARIF or JSON

### CodeQL
- Requires database creation step
- Query suites: `security-extended` (default)
- Languages: Auto-detected or configured
- Best for: Complex dataflow analysis

### Bandit
- Python-only scanner
- Confidence levels: low, medium, high
- Skip specific tests: `["B101", "B201"]`
- Best for: Python security anti-patterns

## Error Handling

### Configuration Errors
If config is invalid:
1. Load fails with `ConfigLoadError`
2. Error includes validation messages
3. No partial config - all or nothing
4. Falls back to defaults if file missing

### Scanner Errors
If scanner fails:
1. Logged but doesn't stop other scanners
2. Reported in final output
3. Exit code reflects failure
4. CI/CD can catch and alert

## File Locations

### Configuration
- Config file: `.flowspec/security-config.yml`
- Custom rules: `.security/rules/` (configurable)
- Output reports: `docs/security/` (configurable)

### Code
- Config models: `src/specify_cli/security/config/models.py`
- Config loader: `src/specify_cli/security/config/loader.py`
- Schema validation: `src/specify_cli/security/config/schema.py`

### Tests
- Config tests: `tests/security/config/`
- Integration tests: `tests/test_security_cli.py`

## Common Patterns

### Loading Config in Code
```python
from specify_cli.security.config import load_config

# Load from default location
config = load_config()

# Load from specific path
config = load_config(Path(".flowspec/security-config.yml"))

# Disable validation (for testing)
config = load_config(validate=False)
```

### Checking Enabled Scanners
```python
enabled = config.get_enabled_scanners()
# Returns: [ScannerType.SEMGREP, ScannerType.BANDIT]
```

### Checking Severity Threshold
```python
if config.should_fail("high"):
    sys.exit(1)  # Fail on high severity
```

### Checking Exclusions
```python
if config.exclusions.matches_path(file_path):
    continue  # Skip excluded file
```

## Related Documentation

- ADR-007: Unified Security Finding Format
- ADR-008: Security MCP Server Architecture
- ADR-009: Scanner Orchestration Pattern
- `docs/guides/security-quickstart.md`: User-facing guide
- `docs/platform/flowspec-security-platform.md`: Platform design

## Version History

- v0.0.251: Initial security configuration system
- v0.0.252: Added Bandit scanner support
- v0.0.253: Added path exclusion patterns
