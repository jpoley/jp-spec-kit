# /jpspec:security Commands Reference

Complete reference for `/jpspec:security` slash commands used in Claude Code sessions.

## Command Overview

The `/jpspec:security` command suite provides AI-powered security scanning, triage, remediation, and reporting integrated into your Claude Code workflow.

### Available Commands

| Command | Purpose | Input Required | Output Generated |
|---------|---------|----------------|------------------|
| `/jpspec:security scan` | Discover vulnerabilities | None | scan-results.json |
| `/jpspec:security triage` | Classify findings with AI | scan-results.json | triage-report.md |
| `/jpspec:security fix` | Generate security patches | triage-results.json | patches/, fix-summary.md |
| `/jpspec:security report` | Generate audit report | scan & triage results | audit-report.md |

**Note**: For CI/CD pipeline integration (GitHub Actions, GitLab CI, Jenkins), use scanner CLIs directly. See [CI/CD Integration Guide](../guides/security-cicd-integration.md).

---

## `specify security scan`

Run security scanners and generate findings.

### Usage

```bash
specify security scan [PATH] [OPTIONS]
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `PATH` | Directory or file to scan | `.` (current directory) |

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--scanner` | `-s` | Specific scanner to use | All enabled |
| `--config` | `-c` | Scanner configuration | `auto` |
| `--format` | `-f` | Output format (json, sarif, markdown) | `json` |
| `--output` | `-o` | Output file path | stdout |
| `--severity` | | Minimum severity to report | `info` |
| `--fail-on` | | Fail if findings >= severity | None |
| `--incremental` | | Only scan changed files | `false` |
| `--quick` | `-q` | Fast scan with reduced rules | `false` |
| `--jobs` | `-j` | Parallel scanner jobs | Auto |
| `--timeout` | `-t` | Scan timeout in seconds | 300 |
| `--verbose` | `-v` | Verbose output | `false` |

### Examples

```bash
# Basic scan
specify security scan

# Scan specific directory with JSON output
specify security scan ./src --format json --output results.json

# Use only Semgrep
specify security scan --scanner semgrep

# Fail CI on high severity findings
specify security scan --fail-on high

# Quick scan for pre-commit
specify security scan --quick --fail-on critical

# SARIF output for GitHub
specify security scan --format sarif --output results.sarif
```

### Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success, no findings above threshold |
| 1 | Findings found above `--fail-on` threshold |
| 2 | Scanner execution error |
| 3 | Configuration error |

---

## `specify security triage`

AI-powered classification of security findings.

### Usage

```bash
specify security triage RESULTS [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `RESULTS` | Path to scan results JSON file |

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--interactive` | `-i` | Interactive confirmation mode | `false` |
| `--model` | `-m` | AI model to use | `claude-sonnet-4-20250514` |
| `--output` | `-o` | Output file for triage results | stdout |
| `--format` | `-f` | Output format (json, markdown) | `json` |
| `--auto-dismiss` | | Auto-dismiss info severity | `false` |
| `--confidence-threshold` | | Minimum AI confidence | 0.7 |
| `--explain` | `-e` | Include detailed explanations | `true` |
| `--verbose` | `-v` | Verbose output | `false` |

### Classifications

| Classification | Code | Description |
|----------------|------|-------------|
| True Positive | `TP` | Confirmed vulnerability |
| False Positive | `FP` | Not a real vulnerability |
| Needs Investigation | `NI` | Requires manual review |

### Examples

```bash
# Basic triage
specify security triage results.json

# Interactive mode with explanations
specify security triage results.json --interactive --explain

# Auto-dismiss informational findings
specify security triage results.json --auto-dismiss

# Output triage report
specify security triage results.json --format markdown --output triage.md
```

### Output Format

```json
{
  "findings": [
    {
      "id": "SEMGREP-001",
      "classification": "TP",
      "confidence": 0.95,
      "risk_score": 8.5,
      "explanation": {
        "summary": "SQL injection vulnerability",
        "impact": "Attackers can execute arbitrary SQL",
        "exploitability": "High - user input directly concatenated",
        "recommendation": "Use parameterized queries"
      }
    }
  ],
  "summary": {
    "total": 10,
    "true_positives": 6,
    "false_positives": 3,
    "needs_investigation": 1
  }
}
```

---

## `specify security fix`

Generate remediation patches for security findings.

### Usage

```bash
specify security fix RESULTS [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `RESULTS` | Path to triage results JSON file |

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--apply` | `-a` | Apply patches automatically | `false` |
| `--dry-run` | | Preview changes without applying | `true` |
| `--output` | `-o` | Output directory for patches | `./patches` |
| `--format` | `-f` | Patch format (unified, git) | `unified` |
| `--validate` | | Validate syntax after patch | `true` |
| `--test` | | Run tests after applying | `false` |
| `--backup` | | Create backup before patching | `true` |
| `--verbose` | `-v` | Verbose output | `false` |

### Examples

```bash
# Generate patches (dry-run)
specify security fix triage.json

# Preview specific fixes
specify security fix triage.json --dry-run

# Apply patches with backup
specify security fix triage.json --apply --backup

# Apply and run tests
specify security fix triage.json --apply --test

# Output patches to directory
specify security fix triage.json --output ./security-patches
```

### Patch Output

```diff
--- a/src/db.py
+++ b/src/db.py
@@ -42,7 +42,8 @@
     # Fetch user by ID
-    query = "SELECT * FROM users WHERE id = " + user_id
-    cursor.execute(query)
+    query = "SELECT * FROM users WHERE id = ?"
+    cursor.execute(query, (user_id,))
     result = cursor.fetchone()
     return result
```

---

## `specify security audit`

Generate compliance-ready security audit reports.

### Usage

```bash
specify security audit RESULTS [OPTIONS]
```

### Arguments

| Argument | Description |
|----------|-------------|
| `RESULTS` | Path to scan or triage results |

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--format` | `-f` | Report format (markdown, html, sarif, json) | `markdown` |
| `--output` | `-o` | Output file path | stdout |
| `--compliance` | `-c` | Compliance framework (soc2, iso27001, hipaa) | None |
| `--owasp` | | Include OWASP Top 10 mapping | `true` |
| `--executive` | | Include executive summary | `true` |
| `--technical` | | Include technical details | `true` |
| `--remediation` | | Include remediation guidance | `true` |
| `--trend` | | Include historical trend | `false` |
| `--verbose` | `-v` | Verbose output | `false` |

### Examples

```bash
# Basic markdown report
specify security audit results.json

# SARIF for GitHub Code Scanning
specify security audit results.json --format sarif --output results.sarif

# SOC2 compliance report
specify security audit results.json --compliance soc2 --format html

# Executive summary only
specify security audit results.json --executive --no-technical
```

### Report Sections

1. **Executive Summary** - High-level security posture
2. **Finding Summary** - Counts by severity and category
3. **OWASP Top 10 Mapping** - Compliance view
4. **Detailed Findings** - Technical vulnerability details
5. **Remediation Plan** - Prioritized fix recommendations
6. **Appendix** - Scanner configuration and metadata

---

## `specify security status`

Display current security configuration and scan status.

### Usage

```bash
specify security status [OPTIONS]
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--check-tools` | | Verify scanner installation | `true` |
| `--config` | | Show current configuration | `true` |
| `--format` | `-f` | Output format (text, json) | `text` |

### Examples

```bash
# Check status
specify security status

# JSON output for scripting
specify security status --format json
```

### Output

```
Security Status
===============

Configuration: .specify/security.yml (found)

Scanners:
  [✓] semgrep 1.50.0 (installed)
  [✗] codeql (not installed)
  [✗] bandit (not installed)

Last Scan:
  Date: 2025-12-03 14:30:00
  Findings: 12 (3 critical, 5 high, 4 medium)
  Duration: 45s

Configuration:
  Fail on: high
  OWASP mapping: enabled
  Auto-triage: disabled
```

---

## `specify security init`

Initialize security configuration for a project.

### Usage

```bash
specify security init [OPTIONS]
```

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--template` | `-t` | Configuration template (minimal, standard, strict) | `standard` |
| `--force` | `-f` | Overwrite existing configuration | `false` |
| `--scanners` | `-s` | Scanners to configure | `semgrep` |

### Examples

```bash
# Initialize with standard template
specify security init

# Strict security configuration
specify security init --template strict

# Minimal configuration
specify security init --template minimal --scanners semgrep
```

---

## Slash Commands

### `/jpspec:security scan`

Interactive security scanning within Claude Code sessions.

```
/jpspec:security scan
```

**Behavior:**
1. Detects available scanners
2. Prompts for scan scope (all files, changed files, specific path)
3. Runs scan with progress display
4. Shows findings summary
5. Offers to proceed with triage

### `/jpspec:security triage`

AI-powered finding triage with explanations.

```
/jpspec:security triage
```

**Behavior:**
1. Loads latest scan results
2. Classifies each finding (TP/FP/NI)
3. Provides plain-English explanations
4. Calculates risk scores
5. Prioritizes remediation order

### `/jpspec:security fix`

Generate and apply security fixes.

```
/jpspec:security fix
```

**Behavior:**
1. Loads triage results
2. Generates fix patches for true positives
3. Shows diff preview
4. Prompts for confirmation
5. Applies patches with backup

### `/jpspec:security audit`

Generate security audit report.

```
/jpspec:security audit
```

**Behavior:**
1. Aggregates scan and triage results
2. Maps to OWASP Top 10
3. Calculates security posture score
4. Generates markdown report
5. Creates SARIF for GitHub integration

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SPECIFY_SECURITY_CONFIG` | Path to configuration file | `.specify/security.yml` |
| `SPECIFY_SECURITY_SCANNER` | Default scanner | `semgrep` |
| `SPECIFY_SECURITY_OUTPUT` | Default output directory | `./security-reports` |
| `SEMGREP_APP_TOKEN` | Semgrep App token | None |
| `GITHUB_TOKEN` | GitHub token for SARIF upload | None |

---

## Configuration File

See [Security Configuration Reference](./security-configuration.md) for complete `.specify/security.yml` schema.

## Related Documentation

- [Security Quickstart](../guides/security-quickstart.md) - Getting started guide
- [CI/CD Integration](../guides/security-cicd-integration.md) - Pipeline setup
- [Custom Rules](../guides/security-custom-rules.md) - Writing custom rules
- [Threat Model](./security-threat-model.md) - Security limitations
- [Privacy Policy](./security-privacy-policy.md) - AI data handling
