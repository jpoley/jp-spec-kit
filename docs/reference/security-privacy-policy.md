# Security Scanning Privacy Policy

This document describes how `/flow:security` handles your code and data, particularly when using AI-powered features.

## Data Collection Overview

| Feature | Data Sent | Destination | Purpose |
|---------|-----------|-------------|---------|
| **Scan** | None | Local only | Scanner runs locally |
| **Triage** | Code snippets | AI API (Anthropic) | Classification |
| **Fix** | Code + context | AI API (Anthropic) | Patch generation |
| **Audit** | None | Local only | Report generation |
| **SARIF Upload** | Findings only | GitHub | Code Scanning |

## AI Feature Data Handling

### What Data is Sent to AI APIs

When using AI-powered triage or fix generation:

**Sent to AI API:**
- Code snippet from finding location (typically 10-50 lines)
- File path (relative to project root)
- Finding metadata (severity, CWE, description)
- Scanner-provided context

**NOT Sent to AI API:**
- Full source files
- Git history or commit messages
- Environment variables or secrets
- Other files in your repository
- Your API keys or credentials

### Example AI Request

```json
{
  "finding": {
    "id": "SEMGREP-001",
    "severity": "high",
    "title": "SQL Injection",
    "cwe": "CWE-89",
    "file": "src/db.py",
    "line": 42,
    "code_snippet": "query = \"SELECT * FROM users WHERE id = \" + user_id"
  },
  "context": {
    "language": "python",
    "framework_hints": ["flask"]
  }
}
```

### AI Provider Information

**Default Provider**: Anthropic (Claude)

| Aspect | Details |
|--------|---------|
| Provider | Anthropic |
| Data Retention | See [Anthropic's Privacy Policy](https://www.anthropic.com/privacy) |
| Training Use | See Anthropic's terms for API usage |
| Encryption | TLS 1.2+ in transit |
| Location | US-based servers |

**Alternative Providers**: Future versions may support additional providers. Check configuration options.

## Local-Only Operation

### Running Without AI

To run security scanning without any external API calls:

```bash
# Scan only (no AI)
specify security scan --format json --output results.json

# Manual triage (no AI)
# Review results.json directly

# Report without AI analysis
specify security audit results.json --no-ai-explanation
```

### Configuration for Air-Gapped Environments

```yaml
# .specify/security.yml
triage:
  ai_enabled: false  # Disable AI triage

fixes:
  ai_enabled: false  # Disable AI fix generation

reporting:
  include_ai_explanation: false
```

## Scanner Data Handling

### Semgrep

| Aspect | Details |
|--------|---------|
| Data Sent | None (local execution) |
| Rule Download | From Semgrep Registry (HTTPS) |
| Telemetry | Opt-out via `SEMGREP_SEND_METRICS=off` |

### CodeQL

| Aspect | Details |
|--------|---------|
| Data Sent | None (local analysis) |
| Database | Local CodeQL database |
| Telemetry | See GitHub's telemetry policy |

### Bandit

| Aspect | Details |
|--------|---------|
| Data Sent | None (fully local) |
| Telemetry | None |

## SARIF Upload to GitHub

When uploading SARIF results to GitHub Code Scanning:

**Data Included in SARIF:**
- Finding locations (file, line numbers)
- Rule IDs and descriptions
- Severity levels
- CWE identifiers

**NOT Included:**
- Source code content
- AI triage explanations
- Fix suggestions

### Controlling SARIF Content

```bash
# Minimal SARIF (findings only)
specify security audit results.json --format sarif --sarif-minimal

# Full SARIF (with descriptions)
specify security audit results.json --format sarif
```

## Data Storage

### Local Files Created

| File | Location | Contents | Sensitive? |
|------|----------|----------|------------|
| Scan results | `./security-results.json` | Finding details | Low |
| Triage results | `./triage-results.json` | AI classifications | Low |
| Patches | `./patches/*.patch` | Code fixes | Medium |
| Reports | `./security-report.md` | Aggregated findings | Low |

### Cleaning Up

```bash
# Remove all generated files
rm -f security-results.json triage-results.json
rm -rf ./patches
rm -f security-report.*
```

## Compliance Considerations

### SOC2

- AI triage sends code snippets externally
- Document in your data flow diagrams
- Consider disabling AI for SOC2-scoped code

### HIPAA

- Do not scan PHI-containing code with AI enabled
- Use local-only mode for healthcare applications
- Review Anthropic's BAA status

### GDPR

- Code snippets may contain PII
- Anthropic processes data in US
- Ensure appropriate data processing agreements

### PCI-DSS

- Cardholder data should not be in source code
- AI triage is low risk if code is properly written
- Document external data flows

## Opting Out

### Disable All External Communication

```yaml
# .specify/security.yml
privacy:
  offline_mode: true  # No external API calls
  disable_telemetry: true
  disable_rule_updates: true
```

### Environment Variables

```bash
# Disable AI features
export SPECIFY_AI_ENABLED=false

# Disable Semgrep telemetry
export SEMGREP_SEND_METRICS=off

# Disable CodeQL telemetry
export CODEQL_DISABLE_TELEMETRY=true
```

## Security of API Keys

### Anthropic API Key

**Required for**: AI triage, AI fix generation

**Storage Options:**
1. Environment variable: `ANTHROPIC_API_KEY`
2. Configuration file: `.specify/credentials.yml` (gitignored)
3. CI/CD secrets

**Best Practices:**
- Never commit API keys to version control
- Use environment variables in CI/CD
- Rotate keys periodically
- Use least-privilege API key scopes

### GitHub Token

**Required for**: SARIF upload to GitHub Code Scanning

**Storage Options:**
1. Environment variable: `GITHUB_TOKEN`
2. `gh` CLI authentication

## Data Retention

| System | Retention | User Control |
|--------|-----------|--------------|
| Local files | Until deleted | Full control |
| AI API | Per provider policy | Request deletion |
| GitHub SARIF | Per repo settings | Delete via API |

## Contact

For privacy concerns or data deletion requests:
- Open an issue on GitHub
- Contact the maintainers

## Updates

This privacy policy may be updated. Check for the latest version:
- In documentation: `docs/reference/security-privacy-policy.md`
- On GitHub releases

**Last Updated**: 2025-12-03
**Version**: 1.0

## Related Documentation

- [Threat Model](./security-threat-model.md) - Security boundaries
- [Command Reference](./flowspec-security-commands.md) - CLI options
- [Configuration](./security-configuration.md) - Privacy settings
