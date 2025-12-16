# Command Objective: `flowspec security`

## Summary
Security scanning commands for vulnerability detection and remediation.

## Objective
Provide integrated security scanning, triage, fix generation, and audit capabilities.

## Subcommands

### `flowspec security scan`
Run security scan on target directory.

**Features:**
- Semgrep integration
- Multiple output formats (text, JSON, SARIF)
- Configurable severity threshold
- CI-friendly exit codes

**Exit Codes:**
- 0: No findings at or above threshold
- 1: Findings found at or above threshold
- 2: Error during scan

**Options:**
```bash
flowspec security scan                           # Scan current directory
flowspec security scan /path/to/code             # Scan specific path
flowspec security scan --tool semgrep            # Specify scanner
flowspec security scan --fail-on critical        # Fail only on critical
flowspec security scan --format json -o out.json # JSON output
```

### `flowspec security triage`
AI-assisted triage of security findings.

**Status: PLACEHOLDER - Future implementation**

**Options:**
```bash
flowspec security triage findings.json
flowspec security triage findings.json --min-severity high
```

### `flowspec security fix`
Generate and optionally apply security fixes.

**Status: PLACEHOLDER - Future implementation**

**Options:**
```bash
flowspec security fix SEMGREP-001 --dry-run
flowspec security fix SEMGREP-001 --apply
```

### `flowspec security audit`
Generate security audit report.

**Status: PLACEHOLDER - "Coming in Phase 2"**

**Options:**
```bash
flowspec security audit
flowspec security audit --format html --output audit.html
flowspec security audit --compliance owasp
```

## Test Results

| Test | Expected | Actual | Status |
|------|----------|--------|--------|
| `flowspec security scan` | Runs semgrep | "semgrep not available" | EXPECTED (not installed) |
| `flowspec security audit` | Audit report | "Coming in Phase 2" | PLACEHOLDER |
| `flowspec security triage` | Requires file | Placeholder message | PLACEHOLDER |
| `flowspec security fix` | Requires finding ID | Placeholder message | PLACEHOLDER |

## Acceptance Criteria
- [x] Scan command with semgrep integration
- [x] Multiple output formats
- [x] CI-friendly exit codes
- [ ] Triage command (PLACEHOLDER)
- [ ] Fix command (PLACEHOLDER)
- [ ] Audit command (PLACEHOLDER)
