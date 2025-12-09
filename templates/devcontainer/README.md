# SpecFlow Agents Devcontainer Template

This template provides a pre-configured development environment with AI coding assistants.

## Quick Start

1. Copy the `devcontainer.json` file to your project's `.devcontainer/` directory:

```bash
mkdir -p .devcontainer
cp devcontainer.json .devcontainer/
```

2. Open your project in VS Code and click "Reopen in Container" when prompted.

## What's Included

The `jpoley/specflow-agents` Docker image includes:

### AI Coding Assistants
- **Claude Code** (`claude`) - Anthropic's AI coding assistant
- **Codex** (`codex`) - [OpenAI's coding agent](https://github.com/openai/codex)
- **GitHub Copilot CLI** (`github-copilot-cli`) - GitHub's AI pair programmer
- **Google Gemini CLI** (`gemini`) - Google's AI coding assistant

### Development Tools
- **Python 3.11** with uv package manager
- **Node.js 20** with pnpm
- **GitHub CLI** (`gh`)
- **Ruff** - Python linter and formatter
- **pytest** - Python testing framework
- **backlog.md** - Task management CLI

## Environment Variables

Set these in your shell or `.env` file before opening the container:

| Variable | Purpose |
|----------|---------|
| `GITHUB_TOKEN` | GitHub API access |
| `ANTHROPIC_API_KEY` | Claude Code authentication |
| `OPENAI_API_KEY` | Codex authentication (alternative to ChatGPT login) |
| `GOOGLE_API_KEY` | Google Gemini authentication |

> **Note**: Codex supports two auth methods: (1) ChatGPT subscription login (Plus/Pro/Team/Edu/Enterprise) - recommended, or (2) `OPENAI_API_KEY` for API-based billing. Run `codex` to authenticate.

## Customization

### Adding Project-Specific Setup

Create a `postCreateCommand` to install your project's dependencies:

```json
{
  "postCreateCommand": "uv sync && npm install"
}
```

### Adding More VS Code Extensions

Add to the `extensions` array:

```json
{
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "your.extension-id"
      ]
    }
  }
}
```

### Mounting Additional Directories

Add to the `mounts` array for additional credential or config directories:

```json
{
  "mounts": [
    "source=${localEnv:HOME}/.aws,target=/home/vscode/.aws,type=bind,readonly"
  ]
}
```

## YOLO Mode Aliases

The image includes commented-out aliases for bypassing AI agent safety features. These are disabled by default. To enable them, add to your `.zshrc` inside the container:

```bash
alias claude-yolo='claude --dangerously-skip-permissions'
alias codex-yolo='codex --dangerously-bypass-approvals-and-sandbox'
alias gemini-yolo='gemini --yolo'
```

⚠️ **Warning**: Using these aliases bypasses security features designed to protect your environment. Use only in isolated, trusted environments.

## Troubleshooting

### Tools not in PATH
Open a new terminal - PATH is configured in `.zshenv` which runs for all shells.

### Permission issues with mounted directories
Ensure the source directories exist on your host machine before starting the container.

### AI CLI not working
Check that the corresponding API key environment variable is set.

## Image Tags

- `latest` - Latest stable build from main branch
- `sha-<commit>` - Specific commit build
- `main` - Latest build from main branch (same as latest)

## Support

Report issues at: https://github.com/jpoley/jp-spec-kit/issues
