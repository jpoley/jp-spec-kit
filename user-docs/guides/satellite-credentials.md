# Satellite Mode Credentials Guide

Securely manage API tokens for remote providers (GitHub, Jira, Notion) when using Satellite Mode to sync tasks.

## Overview

Satellite Mode connects your local backlog to remote issue trackers. Each provider requires an API token for authentication. The **SecretManager** handles credential storage and retrieval with a security-first approach.

## Credential Sources (Priority Order)

The SecretManager checks these sources in order:

1. **System Keychain** (most secure)
   - macOS: Keychain Access
   - Windows: Credential Manager
   - Linux: Secret Service (GNOME Keyring / KWallet)

2. **Environment Variables**
   - `GITHUB_TOKEN`
   - `JIRA_TOKEN`
   - `NOTION_TOKEN`

3. **gh CLI** (GitHub only)
   - Automatically uses `gh auth token` if authenticated

4. **Interactive Prompt** (fallback)
   - Securely prompts for token with option to save

## Quick Start

### Option 1: Use Environment Variables (CI/CD)

Best for automated environments:

```bash
# GitHub
export GITHUB_TOKEN="ghp_your_token_here"

# Jira
export JIRA_TOKEN="your_jira_api_token"

# Notion
export NOTION_TOKEN="secret_your_notion_token"
```

### Option 2: Use System Keychain (Local Development)

The SecretManager automatically stores tokens in your system keychain when you provide them interactively.

### Option 3: Use gh CLI (GitHub Only)

If you're already authenticated with GitHub CLI:

```bash
gh auth login
# Satellite Mode will automatically use your gh CLI token
```

## Getting API Tokens

### GitHub Personal Access Token

1. Go to **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained tokens**
2. Click **Generate new token**
3. Set permissions:
   - **Repository access**: Select repositories for sync
   - **Permissions**: `Issues` (Read and write), `Pull requests` (Read and write)
4. Copy the token (starts with `ghp_` or `github_pat_`)

### Jira API Token

1. Go to [Atlassian Account](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token**
3. Give it a label (e.g., "Backlog Satellite")
4. Copy the token

### Notion Integration Token

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Click **New integration**
3. Give it a name and select the workspace
4. Copy the **Internal Integration Token** (starts with `secret_` or `ntn_`)
5. Share your database with the integration

## Programmatic Usage

### Basic Token Retrieval

```python
from specify_cli.satellite import SecretManager, ProviderType

manager = SecretManager()

# Get token (tries all sources automatically)
token = manager.get_token(ProviderType.GITHUB)
if token:
    print("Token found!")
else:
    print("No token available")
```

### Get or Prompt

```python
# Automatically prompts if no token found
token = manager.get_or_prompt(ProviderType.GITHUB)
```

### Store Token in Keychain

```python
from specify_cli.satellite import SecretManager, ProviderType

manager = SecretManager()

# Store a new token
manager.store_token(ProviderType.GITHUB, "ghp_your_new_token")
```

### Delete Token

```python
# Remove token from keychain
manager.delete_token(ProviderType.GITHUB)
```

### Check Token Source

```python
# Find out where the token comes from
source = manager.get_token_source(ProviderType.GITHUB)
# Returns: "keychain", "env", "gh_cli", or None
```

### Validate Token Format

```python
# Check if token format is valid (doesn't verify with provider)
is_valid = manager.validate_token_format(
    ProviderType.GITHUB,
    "ghp_abc123..."
)
```

## Token Format Requirements

Each provider has specific token format requirements:

| Provider | Format | Example |
|----------|--------|---------|
| GitHub | `ghp_*` (36 chars), `gho_*`, `github_pat_*`, or 40-char hex | `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| Jira | Base64-encoded, 20+ chars | `ABCDEFGHIJKLmnop1234==` |
| Notion | `secret_*` (43 chars) or `ntn_*` (50+ chars) | `secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |

## Log Redaction

The SecretManager automatically redacts tokens from logs to prevent accidental exposure:

```python
import logging
from specify_cli.satellite import SecretManager, ProviderType

manager = SecretManager()
token = manager.get_token(ProviderType.GITHUB)

# Add the redaction filter to your logger
logger = logging.getLogger("satellite")
logger.addFilter(manager.redaction_filter)

# Tokens are automatically redacted in log output
logger.info(f"Using token {token}")
# Logs: "Using token [REDACTED:github]"
```

## Security Best Practices

### DO

- Use system keychain for local development
- Use environment variables in CI/CD (set via secrets manager)
- Use fine-grained tokens with minimal permissions
- Rotate tokens periodically
- Delete tokens when no longer needed

### DON'T

- Store tokens in plaintext files
- Commit tokens to version control
- Share tokens between users
- Use tokens with excessive permissions
- Log tokens, even in debug mode

## Troubleshooting

### "System keychain is not available"

**Linux**: Install a Secret Service provider:
```bash
# GNOME-based systems
sudo apt install gnome-keyring

# KDE-based systems
sudo apt install kwalletmanager
```

**Headless/CI**: Use environment variables instead of keychain.

### "Invalid token format"

Ensure your token matches the expected format:
- GitHub: Must start with `ghp_`, `gho_`, `github_pat_`, or be 40-char hex
- Jira: Must be 20+ characters, alphanumeric with `+/=`
- Notion: Must start with `secret_` or `ntn_`

### "gh auth token failed"

Re-authenticate with GitHub CLI:
```bash
gh auth login
gh auth status  # Verify authentication
```

### Token Works in Browser but Not in Code

1. Check token hasn't expired
2. Verify token has required scopes/permissions
3. Check if organization requires SSO authorization

## Environment Variable Reference

| Provider | Variable | Used When |
|----------|----------|-----------|
| GitHub | `GITHUB_TOKEN` | Keychain empty or unavailable |
| Jira | `JIRA_TOKEN` | Keychain empty or unavailable |
| Notion | `NOTION_TOKEN` | Keychain empty or unavailable |

## Related Documentation

- [Satellite Mode Overview](../reference/satellite-mode.md)
- [Security Architecture](../../backlog/docs/satellite-mode-security-architecture.md)
- [GitHub Provider Setup](satellite-github.md)
- [Jira Provider Setup](satellite-jira.md)
- [Notion Provider Setup](satellite-notion.md)
