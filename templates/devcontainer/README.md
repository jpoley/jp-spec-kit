# AI Coding Agents Devcontainer Template

This template provides a pre-configured devcontainer using the published **AI Coding Agents Devcontainer** image from Docker Hub.

**Image**: `jpoley/specflow-agents:latest`

## Quick Start

1. **Copy this template to your project**:
   ```bash
   mkdir -p .devcontainer
   cp templates/devcontainer/devcontainer.json .devcontainer/
   ```

2. **Open in VS Code**:
   ```bash
   code .
   ```

3. **Reopen in Container**:
   - VS Code will prompt: "Reopen in Container"
   - Click "Reopen in Container"
   - Wait ~30 seconds for container to start (image is pre-built!)

4. **Install your project dependencies**:
   ```bash
   uv sync
   pytest tests/
   ```

## What's Included (Pre-Installed in Image)

The image includes all tools pre-installed:

### Python Environment
- Python 3.11
- uv (fast package manager)
- ruff (linter/formatter)
- pytest (test framework)

### AI Coding Assistants
- claude (Claude Code CLI)
- copilot (GitHub Copilot CLI)
- codex (OpenAI Codex CLI)
- gemini (Google Gemini CLI)

### Task Management
- backlog (backlog.md CLI)
- specify (JP Spec Kit CLI - if your project uses it)

### Development Tools
- Node.js 20 + pnpm
- GitHub CLI (gh)
- Git + zsh

## Authentication

### Subscription-Based Tools (OAuth)

| Tool | First-Time Setup |
|------|------------------|
| Claude Code | Run `claude` → Opens browser for OAuth |
| GitHub Copilot | Run `copilot` → `/login` → Opens browser |

Your tokens are persisted via volume mounts from your host machine:
- Claude: `~/.claude` → `/home/vscode/.claude`
- Copilot: `~/.config/github-copilot` → `/home/vscode/.config/github-copilot`

You only authenticate **once per host machine** (tokens survive container rebuilds).

### API-Key Based Tools

Set these in your host environment (they're automatically forwarded to the container):

```bash
# Required for GitHub operations
export GITHUB_JPSPEC="ghp_..."

# Optional: For API-based AI CLIs
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
```

## Customization

### Add VS Code Extensions

Edit `devcontainer.json`:

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

### Override Environment Variables

Edit `devcontainer.json`:

```json
{
  "remoteEnv": {
    "MY_CUSTOM_VAR": "value"
  }
}
```

### Add Additional Mounts

Edit `devcontainer.json`:

```json
{
  "mounts": [
    "source=/path/on/host,target=/path/in/container,type=bind"
  ]
}
```

### Pin to Specific Version

**Recommended for production**:

```json
{
  "image": "jpoley/specflow-agents:v1.2.3"
}
```

**Pin to immutable digest**:

```json
{
  "image": "jpoley/specflow-agents@sha256:abc123..."
}
```

## Lifecycle Hooks

The template includes these lifecycle hooks:

- **initializeCommand** (host) - Creates required directories on host
- **postCreateCommand** (once) - Runs `uv sync` to install your project dependencies
- **postStartCommand** (every start) - Copies git config from host
- **postAttachCommand** (every attach) - Displays environment info

You can customize these in `devcontainer.json`.

## Volume Mounts

| Host Path | Container Path | Purpose |
|-----------|---------------|---------|
| `./backlog/` | `${containerWorkspaceFolder}/backlog/` | Task persistence |
| `~/.gitconfig` | `/home/vscode/.gitconfig` | Git configuration |
| `~/.ssh/` | `/home/vscode/.ssh/` | SSH keys |
| `~/.claude/` | `/home/vscode/.claude/` | Claude auth tokens |
| `~/.config/github-copilot/` | `/home/vscode/.config/github-copilot/` | Copilot auth tokens |

## Benefits of Pre-Built Image

Compared to building locally:

| Aspect | Local Build | Pre-Built Image |
|--------|-------------|-----------------|
| First start | ~5 minutes | ~30 seconds |
| Consistency | May vary | Guaranteed identical |
| Security | Manual scans | Automated Trivy/Snyk scans |
| SBOM | Not generated | Embedded in image |
| Updates | Manual rebuild | `docker pull` new version |

## Multi-Machine Consistency

This template guarantees **identical environments** across all machines:

```bash
# On any machine
git pull
# VS Code: Command Palette → "Dev Containers: Rebuild Container"
# Result: Guaranteed identical to all other machines
```

No manual synchronization required!

## Troubleshooting

### Image Pull Fails

**Symptom**: "Error pulling image"

**Solution**:
```bash
# Manually pull image
docker pull jpoley/specflow-agents:latest

# Retry in VS Code
# Command Palette → "Dev Containers: Rebuild Container"
```

### CLI Not Found

**Symptom**: `bash: claude: command not found`

**Cause**: PATH not set correctly.

**Solution**:
```bash
# Open new terminal (PATH is set in .zshenv)
# Or manually source:
source ~/.zshenv
```

### Authentication Issues

**Symptom**: Claude Code or Copilot asks for auth every time

**Cause**: Token mount directory not created on host.

**Solution**:
```bash
# On host machine
mkdir -p ~/.claude ~/.config/github-copilot

# Rebuild container
# Command Palette → "Dev Containers: Rebuild Container"
```

## Example Projects

### Python Project with uv

```
my-project/
├── .devcontainer/
│   └── devcontainer.json  (this template)
├── src/
│   └── my_module/
├── tests/
├── pyproject.toml
└── uv.lock
```

**Setup**:
```bash
# Open in container (VS Code)
# Dependencies auto-install via postCreateCommand

# Verify
pytest tests/
```

### Full-Stack Project (Python + Node.js)

```
my-fullstack-project/
├── .devcontainer/
│   └── devcontainer.json  (this template)
├── backend/
│   ├── src/
│   ├── tests/
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   ├── package.json
│   └── pnpm-lock.yaml
└── backlog/
    └── backlog.md
```

**Setup**:
```bash
# Open in container (VS Code)

# Backend setup
cd backend
uv sync
pytest tests/

# Frontend setup
cd ../frontend
pnpm install
pnpm dev
```

## References

- [Image on Docker Hub](https://hub.docker.com/r/jpoley/specflow-agents)
- [Source Repository](https://github.com/jpoley/jp-spec-kit)
- [Platform Documentation](../../docs/platform/dockerhub-cicd-platform.md)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)

---

**Template Version**: 1.0.0
**Last Updated**: 2025-12-08
