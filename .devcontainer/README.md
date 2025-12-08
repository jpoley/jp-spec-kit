# JP Spec Kit Devcontainer

Development container for consistent, reproducible development environments across all machines.

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
- [VS Code](https://code.visualstudio.com/) with [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- Git configured with your credentials

### First Time Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jpoley/jp-spec-kit
   cd jp-spec-kit
   ```

2. **Open in VS Code**:
   ```bash
   code .
   ```

3. **Reopen in Container**:
   - VS Code will prompt: "Reopen in Container"
   - Click "Reopen in Container"
   - Wait ~2-3 minutes for initial setup

4. **Verify Environment**:
   ```bash
   specify --version
   pytest tests/
   backlog task list
   ```

## Authentication

### Subscription-Based Tools (OAuth)

These tools use **subscription-based authentication** via browser OAuth, NOT API keys:

| Tool | Auth Method | First-Time Setup |
|------|-------------|------------------|
| **Claude Code** | Claude Pro/Max subscription | Run `claude` → Opens browser for OAuth |
| **GitHub Copilot** | Copilot Pro/Business subscription | Run `copilot` → `/login` → Opens browser |

Your OAuth tokens are persisted via volume mounts (`~/.claude`, `~/.config/github-copilot`), so you only need to authenticate once per host machine.

### API-Key Based Tools

These tools use traditional API keys (set in your host environment):

```bash
# Required for GitHub operations (backlog, gh CLI)
export GITHUB_JPSPEC="ghp_..."

# Optional: For API-based AI CLIs
export OPENAI_API_KEY="sk-..."      # For codex CLI
export GOOGLE_API_KEY="..."          # For gemini CLI
```

The devcontainer automatically forwards these to the container.

## What's Included

### Python Environment

- **Python 3.11** (from base image)
- **uv** - Fast Python package manager
- **ruff** - Linter and formatter
- **pytest** - Test framework

### AI Coding Assistants

| Tool | Command | Auth Type | Subscription Required |
|------|---------|-----------|----------------------|
| Claude Code | `claude` | OAuth (browser) | Claude Pro/Max |
| GitHub Copilot | `copilot` | OAuth (browser) | Copilot Pro/Business |
| OpenAI Codex | `codex` | API Key | OpenAI API account |
| Google Gemini | `gemini` | API Key | Google AI API |
| Cursor | `cursor` | OAuth (browser) | Cursor subscription |

### Task Management

| Tool | Command | Description |
|------|---------|-------------|
| backlog.md | `backlog` | Task management CLI |
| specify | `specify` | JP Spec Kit CLI |

### VS Code Extensions

- Python + Pylance
- Ruff (linter/formatter)
- TOML support
- YAML support
- Markdown support
- Docker support
- GitLens
- Error Lens
- Spell Checker

## Container Lifecycle

```
Start Container
│
├─→ onCreateCommand (once)
│   └─ Install uv package manager
│
├─→ postCreateCommand (once)
│   ├─ uv sync (install Python dependencies)
│   ├─ Install specify CLI
│   ├─ Install AI coding assistants (claude, copilot, codex, gemini, cursor)
│   ├─ Install backlog.md CLI
│   └─ Setup MCP server configuration
│
├─→ postStartCommand (every start)
│   └─ Git safe directory configuration
│
└─→ postAttachCommand (every attach)
    └─ Display environment info

Ready for Development!
```

## Volume Mounts

| Host Path | Container Path | Purpose | Mode |
|-----------|---------------|---------|------|
| `./backlog/` | `/workspaces/jp-spec-kit/backlog/` | Task persistence | Read-Write |
| `~/.gitconfig` | `/home/vscode/.gitconfig` | Git configuration | Read-Only |
| `~/.ssh/` | `/home/vscode/.ssh/` | SSH keys | Read-Only |
| `~/.claude/` | `/home/vscode/.claude/` | Claude config | Read-Write |

## Common Commands

```bash
# Development
pytest tests/              # Run tests
ruff check . --fix         # Lint and fix
ruff format .              # Format code
uv sync                    # Update dependencies

# Task Management
backlog task list          # List tasks
backlog task create "..."  # Create task
specify workflow validate  # Validate workflow

# AI Assistants
claude --help              # Claude Code CLI
copilot --help             # GitHub Copilot
```

## Troubleshooting

### Container Won't Start

**Symptom**: "Failed to start container"

**Solutions**:
1. Ensure Docker Desktop is running
2. Try rebuilding: Command Palette → "Dev Containers: Rebuild Container"
3. Check Docker has enough resources (4GB+ RAM recommended)

### uv Command Not Found

**Symptom**: `bash: uv: command not found`

**Solution**:
```bash
# Reload PATH
source ~/.bashrc

# Or reinstall uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### specify Command Not Found

**Symptom**: `bash: specify: command not found`

**Solution**:
```bash
# Reinstall specify CLI
uv tool install . --force

# Verify installation
which specify
specify --version
```

### AI CLI Not Working

**Symptom**: CLI installed but not responding

**Solutions**:
1. Check API key is set: `echo $ANTHROPIC_API_KEY`
2. Reinstall the CLI: `pnpm install -g @anthropic-ai/claude-code`
3. Check pnpm global bin is in PATH

### Tests Fail in Container

**Symptom**: Tests pass locally but fail in container

**Solution**:
```bash
# Check Python version
python --version  # Should be 3.11.x

# Force dependency sync
uv sync --force

# Check environment variables
env | grep -E "GITHUB_|ANTHROPIC_"
```

## Customization

### Adding VS Code Extensions

Edit `.devcontainer/devcontainer.json`:

```json
{
  "customizations": {
    "vscode": {
      "extensions": [
        "your-extension-id-here"
      ]
    }
  }
}
```

### Adding System Packages

Use devcontainer features in `.devcontainer/devcontainer.json`:

```json
{
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  }
}
```

### Local Overrides

For personal customizations that shouldn't be committed, create a `.devcontainer/devcontainer.local.json`:

```json
{
  "remoteEnv": {
    "MY_LOCAL_VAR": "value"
  }
}
```

## Multi-Machine Consistency

This devcontainer guarantees identical environments across all machines:

| Machine | Environment |
|---------|-------------|
| muckross | Identical |
| galway | Identical |
| kinsale | Identical |
| adare | Identical |

**No manual synchronization required**:

```bash
# On any machine
git pull
# VS Code: Command Palette → "Dev Containers: Rebuild Container"
# Result: Guaranteed identical to all other machines
```

This directly addresses the CLAUDE.md repeatability mandate.

## CI/CD Integration

GitHub Actions can use the same container environment:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: mcr.microsoft.com/devcontainers/python:3.11-bullseye
    steps:
      - uses: actions/checkout@v4
      - name: Setup
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          export PATH="$HOME/.cargo/bin:$PATH"
          uv sync
      - name: Test
        run: uv run pytest tests/
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VS Code + Docker                          │
│                    (Host Machine)                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Devcontainer                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Base: mcr.microsoft.com/devcontainers/python:3.11      ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Python 3.11  │  │ Node.js 20   │  │ GitHub CLI   │      │
│  │ + uv         │  │ + pnpm       │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                 AI Coding Assistants                     ││
│  │  claude  copilot  codex  gemini  cursor                 ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                 Development Tools                        ││
│  │  specify  backlog  ruff  pytest  git  gh                ││
│  └─────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                 Volume Mounts                            ││
│  │  ./backlog/  ~/.gitconfig  ~/.ssh/  ~/.claude/          ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

## References

- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Devcontainer Features](https://containers.dev/features)
- [uv Documentation](https://docs.astral.sh/uv/)
- [CLAUDE.md](../CLAUDE.md) - Development standards
