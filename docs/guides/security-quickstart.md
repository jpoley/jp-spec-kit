# Security Quickstart Guide

This guide helps you get started with security scanning in 5 minutes using `/jpspec:security` commands.

## Prerequisites

- Python 3.11+
- At least one security scanner installed (Semgrep recommended)

### Installing Semgrep

```bash
# Via pip (recommended)
pip install semgrep

# Via Homebrew (macOS/Linux)
brew install semgrep

# Verify installation
semgrep --version
```

## Quick Start (5 Minutes)

### 1. Run Your First Scan

In a Claude Code session:

```
/jpspec:security scan
```

This will:
- Detect available scanners (Semgrep, Bandit, CodeQL)
- Scan your codebase for security vulnerabilities
- Save results to `docs/security/scan-results.json`
- Display a summary of findings

**Example Output:**
```
✅ Security Scan Complete
   Scanner: Semgrep v1.50.0
   Findings: 12 total (3 critical, 5 high, 4 medium)
   Report: docs/security/scan-results.json
```

### 2. Understand Your Results

View the findings in the generated report:

```bash
cat docs/security/scan-results.json
```

Findings include:
- **Severity**: Critical, High, Medium, Low, Info
- **CWE**: Common Weakness Enumeration ID
- **OWASP**: OWASP Top 10 2021 mapping
- **Location**: File path and line number
- **Remediation**: Fix recommendations

### 3. Triage with AI (Beginner Mode)

Use AI to classify findings and get simple explanations:

```
/jpspec:security triage --persona beginner
```

**What this does:**
- Analyzes each finding to determine if it's a real vulnerability (True Positive) or false alarm (False Positive)
- Provides simple, non-technical explanations
- Shows step-by-step fix instructions
- Includes learning resources

**Example Beginner Output:**
```markdown
## Finding: SQL Injection in Login Form

### What Is This?
Someone could trick your database by entering special characters in the login form.

### Why Does It Matter?
An attacker could steal all user data or delete the database.

### How Do I Fix It?
1. Open `src/auth/login.py`
2. Find line 42
3. Change the code to use safe queries (see example below)

[Step-by-step instructions with code examples]
```

### 4. Fix Your First Vulnerability

Generate and review a security patch:

```
/jpspec:security fix
```

**Workflow:**
1. AI generates secure code patches for all True Positive findings
2. Shows you a preview of each patch (diff format)
3. Asks for confirmation before applying
4. Applies patches and creates backups

**Example Patch:**
```diff
- cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
+ cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

### 5. Generate Your First Audit Report

Create a comprehensive security report:

```
/jpspec:security report
```

**Generated Report Includes:**
- Executive summary (non-technical)
- Finding breakdown by severity
- OWASP Top 10 compliance checklist
- Detailed remediation recommendations
- Sign-off section for stakeholders

## Command Summary

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/jpspec:security scan` | Find vulnerabilities | Before every PR, commit, or release |
| `/jpspec:security triage` | Classify findings | After scanning to prioritize fixes |
| `/jpspec:security fix` | Apply security patches | When ready to fix vulnerabilities |
| `/jpspec:security report` | Generate audit report | For compliance, reviews, stakeholders |

## Configuration

Create `.jpspec/security-config.yml` in your project root:

```yaml
# Security scanning configuration
scanners:
  semgrep:
    enabled: true
    registry_rulesets:
      - p/default           # Default security rules
      - p/owasp-top-ten     # OWASP Top 10 rules
    custom_rules_dir: .security/rules

  bandit:
    enabled: true
    confidence_level: medium

# Fail threshold for CI/CD
fail_on: high  # critical, high, medium, low, none

# Path exclusions
exclusions:
  paths:
    - node_modules/
    - .venv/
    - tests/
  patterns:
    - "*_test.py"
    - "*.test.js"

# AI Triage configuration
triage:
  persona: beginner       # beginner, expert, compliance
  confidence_threshold: 0.7
  auto_dismiss_fp: false
  cluster_similar: true

# Reporting
reporting:
  format: markdown
  output_dir: docs/security/
  include_false_positives: false
```

See [docs/security/config-schema.yaml](../security/config-schema.yaml) for complete configuration options.

## CI/CD Integration

See [Security CI/CD Integration Guide](./security-cicd-integration.md) for complete examples.

### Quick GitHub Actions Example

```yaml
name: Security Scan
on: [push, pull_request]

permissions:
  contents: read
  security-events: write

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install scanners
        run: pip install semgrep

      - name: Run security scan
        run: |
          semgrep --config=auto --sarif --output=results.sarif .

      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

**Note**: For full CI/CD integration with AI triage and fix generation, see the detailed guide.

## Common Workflows

### Workflow 1: Pre-Commit Quick Check

In Claude Code, before committing:

```
/jpspec:security scan
```

Reviews critical issues only before commit.

### Workflow 2: Pull Request Security Review

```
/jpspec:security scan
/jpspec:security triage --persona expert
/jpspec:security fix --review
```

Full security check with AI triage and fix generation.

### Workflow 3: Compliance Audit

```
/jpspec:security scan --all-scanners
/jpspec:security triage --persona compliance
/jpspec:security report --format pdf --compliance soc2
```

Comprehensive audit for regulatory requirements.

## Severity Levels

| Level | Description | Example |
|-------|-------------|---------|
| **Critical** | Immediate exploitation risk | SQL injection, RCE |
| **High** | Significant security impact | XSS, path traversal |
| **Medium** | Moderate risk with mitigations | Information disclosure |
| **Low** | Minor issues or hardening | Missing security headers |
| **Info** | Best practices, no risk | Code quality suggestions |

## OWASP Top 10 Mapping

Findings are automatically mapped to OWASP Top 10 2021:

| Category | CWEs | Example |
|----------|------|---------|
| A01 Broken Access Control | CWE-22, CWE-284 | Path traversal |
| A02 Cryptographic Failures | CWE-327, CWE-328 | Weak encryption |
| A03 Injection | CWE-79, CWE-89 | SQL injection, XSS |
| A04 Insecure Design | CWE-209, CWE-256 | Design flaws |
| A05 Security Misconfiguration | CWE-16, CWE-611 | XML external entities |
| A06 Vulnerable Components | CWE-829, CWE-1035 | Known vulnerabilities |
| A07 Auth Failures | CWE-287, CWE-384 | Broken authentication |
| A08 Data Integrity Failures | CWE-502, CWE-829 | Deserialization |
| A09 Logging Failures | CWE-117, CWE-223 | Log injection |
| A10 SSRF | CWE-918 | Server-side request forgery |

## Personas Explained

The `/jpspec:security triage` command supports three personas:

### Beginner Persona
**Use when**: Training junior developers, onboarding new team members
- Simple, non-technical language
- Step-by-step fix instructions with code examples
- Learning resources and tutorials
- Explanations under 100 words

### Expert Persona
**Use when**: Security reviews, penetration testing, advanced development
- Technical depth with CWE/CVE references
- Exploitation scenarios and proof-of-concepts
- Defense-in-depth strategies
- Performance and edge case considerations

### Compliance Persona
**Use when**: Preparing for audits, regulatory compliance, stakeholder reporting
- Regulatory mapping (PCI-DSS, SOC2, HIPAA, ISO 27001)
- Audit evidence format with sign-off checklist
- Compliance status assessment
- Remediation timeframes per policy

## Troubleshooting

### "Scanner not found"

**Problem**: Semgrep or Bandit not installed

**Solution**:
```bash
pip install semgrep bandit
```

### "No scan results found"

**Problem**: Triage/fix/report commands can't find results

**Solution**: Run scan first:
```
/jpspec:security scan
```

### "AI API error"

**Problem**: AI triage failed

**Solution**:
- Check `ANTHROPIC_API_KEY` environment variable is set
- Verify you have API access and quota
- Try with lower confidence threshold: `--confidence 0.6`

### High False Positive Rate

**Solution**:
1. Use AI triage to auto-classify: `/jpspec:security triage`
2. Add exclusions to `.jpspec/security-config.yml`
3. Create custom rules to reduce noise (see Custom Rules guide)

## Next Steps

- [Command Reference](../reference/jpspec-security-commands.md) - Complete command documentation
- [CI/CD Integration](./security-cicd-integration.md) - Detailed pipeline setup
- [Custom Rules Guide](./security-custom-rules.md) - Writing custom security rules
- [Threat Model](../reference/security-threat-model.md) - Security limitations
- [AI Privacy Policy](../security/ai-privacy-policy.md) - Data handling and privacy
