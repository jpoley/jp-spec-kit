# Installation Guide

## Prerequisites

- **Linux/macOS** (or Windows; PowerShell scripts now supported without WSL)
- AI coding agent: [Claude Code](https://www.anthropic.com/claude-code), [GitHub Copilot](https://code.visualstudio.com/), [Codebuddy CLI](https://www.codebuddy.ai/cli) or [Gemini CLI](https://github.com/google-gemini/gemini-cli)
- [uv](https://docs.astral.sh/uv/) for package management
- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

## Installation

### Initialize a New Project (Layered: base + extension)

The easiest way to get started is to initialize a new project with the layered model: base spec-kit plus jp-spec-kit overlay.

```bash
uvx --from git+https://github.com/jpoley/jp-spec-kit.git specify init <PROJECT_NAME>
```

Or initialize in the current directory:

```bash
uvx --from git+https://github.com/jpoley/jp-spec-kit.git specify init .
# or use the --here flag
uvx --from git+https://github.com/jpoley/jp-spec-kit.git specify init --here
```

Alternatively, install persistently once and use everywhere:

```bash
uv tool install specify-cli --from git+https://github.com/jpoley/jp-spec-kit.git
specify init <PROJECT_NAME>
```

### Specify AI Agent

You can proactively specify your AI agent during initialization:

```bash
uvx --from git+https://github.com/jpoley/jp-spec-kit.git specify init <project_name> --ai claude
uvx --from git+https://github.com/jpoley/jp-spec-kit.git specify init <project_name> --ai gemini
uvx --from git+https://github.com/jpoley/jp-spec-kit.git specify init <project_name> --ai copilot
uvx --from git+https://github.com/jpoley/jp-spec-kit.git specify init <project_name> --ai codebuddy
```

### Specify Script Type (Shell vs PowerShell)

All automation scripts now have both Bash (`.sh`) and PowerShell (`.ps1`) variants.

Auto behavior:
- Windows default: `ps`
- Other OS default: `sh`
- Interactive mode: you'll be prompted unless you pass `--script`

Force a specific script type:
```bash
uvx --from git+https://github.com/jpoley/jp-spec-kit.git specify init <project_name> --script sh
uvx --from git+https://github.com/jpoley/jp-spec-kit.git specify init <project_name> --script ps
```

### Ignore Agent Tools Check

If you prefer to get the templates without checking for the right tools:

```bash
uvx --from git+https://github.com/jpoley/jp-spec-kit.git specify init <project_name> --ai claude --ignore-agent-tools
```

## Verification

After initialization, you should see the following commands available in your AI agent:
- `/speckit.specify` - Create specifications
- `/speckit.plan` - Generate implementation plans  
- `/speckit.tasks` - Break down into actionable tasks

The `.specify/scripts` directory will contain both `.sh` and `.ps1` scripts.

### VS Code / GitHub Copilot Setup

If you're using GitHub Copilot in VS Code, the initialization process automatically configures `.vscode/settings.json` with the required settings for prompt files. The key settings are:

```json
{
    "chat.promptFiles": true,
    "chat.promptFilesRecommendations": {
        "speckit.constitution": true,
        "speckit.specify": true,
        "speckit.plan": true,
        "speckit.tasks": true,
        "speckit.implement": true
    }
}
```

**Prompt files location:** After initialization, prompt files are created in `.github/prompts/` with the `.prompt.md` extension.

**If prompts don't appear in Copilot Chat:**
1. Ensure VS Code is version 1.96 or later (VS Code Insiders may have newer features)
2. Verify that `chat.promptFiles` is set to `true` in your workspace settings
3. Open the Command Palette (Ctrl+Shift+P / Cmd+Shift+P) and run "Developer: Reload Window"
4. Check that `.github/prompts/` directory contains files with `.prompt.md` extension

## Troubleshooting

### Private assets or API rate limits (authenticated downloads)

If the jp-spec-kit repository or its release assets are private, or you’re operating behind corporate restrictions/rate limits, provide a GitHub token so the CLI can authenticate when resolving releases and downloading assets.

Supported methods:

- Environment variable: GITHUB_JPSPEC
- CLI flag: --github-token

Examples:

- macOS/Linux (zsh/bash):

	export GITHUB_JPSPEC=ghp_your_token_here
	uvx --from git+https://github.com/jpoley/jp-spec-kit.git specify init my-project --ai claude --debug

- Windows PowerShell:

	$env:GITHUB_JPSPEC = "ghp_your_token_here"
	uvx --from git+https://github.com/jpoley/jp-spec-kit.git specify init my-project --ai claude --debug

- Pass inline:

	uvx --from git+https://github.com/jpoley/jp-spec-kit.git specify init my-project --ai claude --github-token ghp_your_token_here --debug

Notes:

- Scope: a classic Personal Access Token with repo scope (read) is sufficient to download private release assets.
- Symptom mapping: a 404 Not Found during asset download usually indicates missing auth for private assets. Provide a token or use public assets.

### Git Credential Manager on Linux

If you're having issues with Git authentication on Linux, you can install Git Credential Manager:

```bash
#!/usr/bin/env bash
set -e
echo "Downloading Git Credential Manager v2.6.1..."
wget https://github.com/git-ecosystem/git-credential-manager/releases/download/v2.6.1/gcm-linux_amd64.2.6.1.deb
echo "Installing Git Credential Manager..."
sudo dpkg -i gcm-linux_amd64.2.6.1.deb
echo "Configuring Git to use GCM..."
git config --global credential.helper manager
echo "Cleaning up..."
rm gcm-linux_amd64.2.6.1.deb
```

